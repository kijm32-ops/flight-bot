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

    logging.info("🚀 PTIS Phase 2: 다중 출발지 & 유동 날짜 검색 엔진 디버깅 시작...")

    raw_data = fetch_raw_flight_data(SERPAPI_KEY, SEARCH_PARAMS)
    
    if raw_data:
        # 1. SerpApi 자체가 에러를 반환했을 경우
        if "error" in raw_data:
            logging.error(f"🚨 SerpApi 반환 에러: {raw_data['error']}")
        
        # 2. 정상적으로 특가 데이터를 가져왔을 경우
        elif "top_deals" in raw_data:
            deals_count = len(raw_data["top_deals"])
            logging.info(f"✅ 성공! {deals_count}개의 글로벌 특가 데이터를 긁어왔습니다.")
        
        # 3. 에러는 아닌데 우리가 찾는 형태의 데이터가 아닐 경우 (전체 구조 출력)
        else:
            logging.error("❌ top_deals 키가 없습니다. API가 반환한 실제 데이터 구조는 다음과 같습니다:")
            print(json.dumps(raw_data, ensure_ascii=False, indent=2))
    else:
        logging.error("❌ API 통신 자체가 실패했습니다.")

if __name__ == "__main__":
    run_system()
