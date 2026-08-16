import logging
import sys
import concurrent.futures
from typing import List, Tuple
from config import (
    SERPAPI_KEY, BASE_SEARCH_PARAMS, KAKAO_JS_KEY,
    PROFILES, ORIGIN_PROFILES,
    DAILY_TASK_PRIORITY, DEEP_TASK_PRIORITY, is_deep_scan_day,
    SERPAPI_SAFE_BUDGET, SERPAPI_MONTHLY_LIMIT, API_QUOTA_WARNING_THRESHOLD,
)
from search import fetch_raw_flight_deals
from normalizer import normalize_and_deduplicate
from notifier import send_email, send_kakao_message, send_warning_email
from report_generator import generate_report_html
from state import (
    load_state, save_state, update_route_history,
    peek_api_usage, record_api_calls, record_kakao_result,
)
from models import Flight
from origin_compare import annotate_origin_alternatives

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')


def build_tasks(remaining_budget: int, deep_scan: bool) -> List[Tuple[str, str]]:
    """
    우선순위 순으로 작업을 구성하되, 남은 예산만큼만 잘라서 반환한다.
    심층 검색일에는 deep 작업이 일반 작업 뒤에 추가된다
    (예산이 빠듯하면 deep이 가장 먼저 희생됨).
    """
    candidates = list(DAILY_TASK_PRIORITY)
    if deep_scan:
        candidates += DEEP_TASK_PRIORITY

    valid = [
        (origin, profile)
        for origin, profile in candidates
        if profile in ORIGIN_PROFILES.get(origin, [])
    ]

    if remaining_budget >= len(valid):
        return valid

    trimmed = valid[:max(0, remaining_budget)]
    dropped = valid[len(trimmed):]
    if dropped:
        logging.warning(
            f"⚠️ 예산 부족으로 {len(dropped)}개 작업 생략: "
            + ", ".join(f"{o}/{p}" for o, p in dropped)
        )
    return trimmed


def process_profile(origin: str, profile_name: str) -> List[Flight]:
    """개별 스레드 워커 (출발지 + 검색 프로필 조합)"""
    try:
        date_range, trip_length = PROFILES[profile_name]
        search_params = {
            **BASE_SEARCH_PARAMS,
            "outbound_date": date_range,
            "trip_length": trip_length,
        }
        raw_deals = fetch_raw_flight_deals(SERPAPI_KEY, search_params, origin)
        if not raw_deals:
            return []

        flights = normalize_and_deduplicate(origin, raw_deals)
        logging.info(f"✅ [{origin} / {profile_name}] {len(flights)}건 정규화 완료.")
        return flights
    except Exception as e:
        logging.error(f"🚨 [{origin} / {profile_name}] 작업 최종 실패: {e}")
        return []


def run_system():
    if not SERPAPI_KEY:
        logging.error("❌ SERPAPI_KEY가 없습니다.")
        sys.exit(1)

    state = load_state()

    deep_scan = is_deep_scan_day()
    if deep_scan:
        logging.info("🔭 오늘은 심층 검색일입니다 (8~11개월 후 장거리 포함).")

    # ── 실행 전 예산 확인 ──
    used = peek_api_usage(state)
    remaining = SERPAPI_SAFE_BUDGET - used
    logging.info(
        f"💰 이번 달 사용량 {used}/{SERPAPI_MONTHLY_LIMIT}회 "
        f"(안전 예산 {SERPAPI_SAFE_BUDGET}회 기준 잔여 {remaining}회)"
    )

    tasks = build_tasks(remaining, deep_scan)

    if not tasks:
        logging.error("🛑 안전 예산을 모두 소진하여 이번 실행은 API 호출을 건너뜁니다.")
        send_warning_email(
            "🛑 [PTIS] SerpApi 예산 소진 — 검색 중단",
            f"이번 달 SerpApi 호출이 {used}회에 도달하여 검색을 중단했습니다. "
            f"(무료 한도 {SERPAPI_MONTHLY_LIMIT}회 / 안전 예산 {SERPAPI_SAFE_BUDGET}회) "
            f"다음 달 1일에 자동으로 재개됩니다."
        )
        generate_report_html([], KAKAO_JS_KEY, set())
        save_state(state)
        return

    logging.info(f"🚀 PTIS: {len(tasks)}개 작업 시작 — " + ", ".join(f"{o}/{p}" for o, p in tasks))
    all_final_flights: List[Flight] = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=len(tasks)) as executor:
        future_to_task = {
            executor.submit(process_profile, origin, profile): (origin, profile)
            for origin, profile in tasks
        }

        for future in concurrent.futures.as_completed(future_to_task):
            origin, profile = future_to_task[future]
            try:
                all_final_flights.extend(future.result())
            except Exception as exc:
                logging.error(f"[{origin} / {profile}] 스레드 예외 발생: {exc}")

    # 프로필 간 날짜창 중복 제거 (near 0~60일 / mid 45~150일 구간이 겹침)
    seen = {}
    for f in all_final_flights:
        key = (f.origin, f.destination, str(f.depart_date), str(f.return_date))
        if key not in seen or f.price < seen[key].price:
            seen[key] = f
    all_final_flights = list(seen.values())

    all_final_flights = annotate_origin_alternatives(all_final_flights)
    all_final_flights.sort(key=lambda x: (x.value_ratio, x.price))

    logging.info(f"🎉 스크래핑 종료! 총 {len(all_final_flights)}건 수집 완료.")

    low_price_keys = update_route_history(state, all_final_flights)
    if low_price_keys:
        logging.info(f"🔥 30일 최저가 갱신 항공권: {len(low_price_keys)}건")

    total_calls = record_api_calls(state, len(tasks))
    logging.info(f"📈 이번 달 SerpApi 누적 호출: {total_calls}회")
    if total_calls >= API_QUOTA_WARNING_THRESHOLD:
        send_warning_email(
            "⚠️ [PTIS] SerpApi 한도 임박",
            f"이번 달 SerpApi 호출이 {total_calls}회를 기록했습니다 "
            f"(무료 한도 {SERPAPI_MONTHLY_LIMIT}회 / 안전 예산 {SERPAPI_SAFE_BUDGET}회). "
            f"안전 예산 도달 시 자동으로 검색이 중단됩니다."
        )

    generate_report_html(all_final_flights, KAKAO_JS_KEY, low_price_keys)

    if all_final_flights:
        send_email(all_final_flights, low_price_keys)

        kakao_success = send_kakao_message(all_final_flights)
        need_warning = record_kakao_result(state, kakao_success)
        if need_warning:
            send_warning_email(
                "⚠️ [PTIS] 카카오톡 발송 3회 연속 실패",
                "카카오톡 알림이 3회 연속 발송에 실패했습니다. "
                "KAKAO_REFRESH_TOKEN이 만료되었을 가능성이 있으니 재발급을 확인해주세요."
            )
    else:
        logging.warning("발송할 특가 항공권이 없습니다.")

    save_state(state)


if __name__ == "__main__":
    run_system()
