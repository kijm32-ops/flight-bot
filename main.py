import logging
import sys
import json
from config import SERPAPI_KEY, SEARCH_PARAMS
from search import fetch_raw_flight_data

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_system():
    if not SERPAPI_KEY:
        logging.error("❌ SERPAPI_KEY가 설정되지 않았습니다.")
        sys.exit(1)

    logging.info("🚀 PTIS Phase 2: 다중 출발지 & 유동 날짜 검색 엔진 테스트 시작...")

    # 단 한 번의 API 호출로 4개 공항 + 30일치 전 세계 특가를 싹 쓸어옵니다.
    raw_data = fetch_raw_flight_data(SERPAPI_KEY, SEARCH_PARAMS)
    
    if raw_data and "top_deals" in raw_data:
        deals_count = len(raw_data["top_deals"])
        logging.info(f"✅ 성공! 한 번의 호출로 {deals_count}개의 글로벌 특가 데이터를 긁어왔습니다.")
        
        # 데이터가 어떻게 생겼는지 첫 번째 결과물 1개만 화면에 찍어봅니다.
        first_deal = raw_data["top_deals"][0]
        logging.info(f"🔍 특가 데이터 샘플 확인:\n{json.dumps(first_deal, ensure_ascii=False, indent=2)}")
    else:
        logging.error("❌ 데이터를 가져오지 못했거나 특가 내역(top_deals)이 없습니다.")

if __name__ == "__main__":
    run_system()
