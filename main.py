import logging
import sys
import concurrent.futures
from typing import List
from config import SERPAPI_KEY, BASE_SEARCH_PARAMS, TARGET_ORIGINS, DATE_RANGES
from search import fetch_raw_flight_deals
from normalizer import normalize_and_deduplicate
from notifier import send_email, send_kakao_message
from models import Flight

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')


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

    if all_final_flights:
        send_email(all_final_flights)
        send_kakao_message(all_final_flights)
    else:
        logging.warning("발송할 특가 항공권이 없습니다.")


if __name__ == "__main__":
    run_system()
