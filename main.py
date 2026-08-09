import logging
import sys
import concurrent.futures
from typing import List
from config import SERPAPI_KEY, BASE_SEARCH_PARAMS, TARGET_ORIGINS, DATE_RANGES, KAKAO_JS_KEY
from search import fetch_raw_flight_deals
from normalizer import normalize_and_deduplicate
from notifier import send_email, send_kakao_message, send_warning_email
from report_generator import generate_report_html
from state import load_state, save_state, update_route_history, record_api_calls, record_kakao_result
from models import Flight

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# 무료 요금제 한도(월 250회) 대비 경고 발동 기준
API_QUOTA_WARNING_THRESHOLD = 230


def process_origin_range(origin: str, date_range: str) -> List[Flight]:
    """개별 스레드에서 실행되는 파이프라인 워커 (출발지 + 날짜구간 조합)"""
    try:
        search_params = {**BASE_SEARCH_PARAMS, "outbound_date": date_range}
        raw_deals = fetch_raw_flight_deals(SERPAPI_KEY, search_params, origin)
        if not raw_deals:
            return []

        flights = normalize_and_deduplicate(origin, raw_deals)
        logging.info(f"✅ [{origin} / {date_range}] {len(flights)}개의 최저가 항공권 정규화 완료.")
        return flights
    except Exception as e:
        logging.error(f"🚨 [{origin} / {date_range}] 작업 최종 실패: {e}")
        return []


def run_system():
    if not SERPAPI_KEY:
        logging.error("❌ SERPAPI_KEY가 없습니다.")
        sys.exit(1)

    state = load_state()

    logging.info("🚀 PTIS Phase 3: 다중 출발지 x 근거리/원거리 검색 시작...")
    all_final_flights: List[Flight] = []

    tasks = [(origin, date_range) for origin in TARGET_ORIGINS for date_range in DATE_RANGES]

    with concurrent.futures.ThreadPoolExecutor(max_workers=len(tasks)) as executor:
        future_to_task = {
            executor.submit(process_origin_range, origin, date_range): (origin, date_range)
            for origin, date_range in tasks
        }

        for future in concurrent.futures.as_completed(future_to_task):
            origin, date_range = future_to_task[future]
            try:
                result_flights = future.result()
                all_final_flights.extend(result_flights)
            except Exception as exc:
                logging.error(f"[{origin} / {date_range}] 스레드 예외 발생: {exc}")

    all_final_flights.sort(key=lambda x: x.price)

    logging.info(f"🎉 스크래핑 종료! 총 {len(all_final_flights)}개의 최적화된 항공권 수집 완료.")

    # 1. 30일 최저가 판별 (동시에 가격 이력 갱신)
    low_price_keys = update_route_history(state, all_final_flights)
    if low_price_keys:
        logging.info(f"🔥 30일 최저가 갱신 항공권: {len(low_price_keys)}건")

    # 2. SerpApi 무료 한도(월 250회) 사용량 추적 및 경고
    total_calls = record_api_calls(state, len(tasks))
    logging.info(f"📈 이번 달 SerpApi 누적 호출: {total_calls}회")
    if total_calls >= API_QUOTA_WARNING_THRESHOLD:
        send_warning_email(
            "⚠️ [PTIS] SerpApi 무료 한도 임박",
            f"이번 달 SerpApi 호출이 {total_calls}회를 기록했습니다 (무료 한도 250회). "
            f"한도 초과 전에 요금제 업그레이드나 검색 범위 조정을 검토해주세요."
        )

    # 3. 리포트 페이지는 결과 유무와 상관없이 항상 최신화
    generate_report_html(all_final_flights, KAKAO_JS_KEY, low_price_keys)

    if all_final_flights:
        send_email(all_final_flights, low_price_keys)

        # 4. 카카오톡 발송 및 연속 실패 감지
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
