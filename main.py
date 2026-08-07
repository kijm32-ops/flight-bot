import logging
import sys
import concurrent.futures
from typing import List

from config import SERPAPI_KEY, BASE_SEARCH_PARAMS, TARGET_ORIGINS
from search import fetch_raw_flight_deals
from normalizer import normalize_and_deduplicate
from notifier import send_email
from models import Flight

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def process_origin(origin: str) -> List[Flight]:
    """개별 스레드에서 실행되는 파이프라인 워커"""
    try:
        raw_deals = fetch_raw_flight_deals(SERPAPI_KEY, BASE_SEARCH_PARAMS, origin)
        if not raw_deals:
            return []
            
        flights = normalize_and_deduplicate(origin, raw_deals)
        logging.info(f"✅ [{origin}] {len(flights)}개의 최저가 항공권 정규화 완료.")
        return flights
    except Exception as e:
        logging.error(f"🚨 [{origin}] 작업 최종 실패: {e}")
        return []

def run_system():
    if not SERPAPI_KEY:
        logging.error("❌ SERPAPI_KEY가 없습니다.")
        sys.exit(1)

    logging.info("🚀 PTIS Phase 3: 다중 출발지 멀티스레딩 검색 시작...")
    all_final_flights: List[Flight] = []

    # 병렬 처리 (max_workers는 타겟 출발지의 개수와 동일하게 설정)
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(TARGET_ORIGINS)) as executor:
        future_to_origin = {
            executor.submit(process_origin, origin): origin 
            for origin in TARGET_ORIGINS
        }
        
        for future in concurrent.futures.as_completed(future_to_origin):
            origin = future_to_origin[future]
            try:
                result_flights = future.result()
                all_final_flights.extend(result_flights)
            except Exception as exc:
                logging.error(f"[{origin}] 스레드 예외 발생: {exc}")

    # 최종 결과 가격 오름차순(저렴한 순)으로 정렬
    all_final_flights.sort(key=lambda x: x.price)
    
    logging.info(f"🎉 스크래핑 종료! 총 {len(all_final_flights)}개의 최적화된 항공권 수집 완료.")
    
    # 정규화된 Flight 객체 리스트를 알림 모듈로 전달
    if all_final_flights:
        send_email(all_final_flights)
    else:
        logging.warning("발송할 특가 항공권이 없습니다.")

if __name__ == "__main__":
    run_system()
