import logging
import sys
from config import SERPAPI_KEY, ORIGIN, DATE_OUT, DATE_RET, TARGETS
from search import fetch_flight_data
from parser import extract_best_deal
from notifier import send_email

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_system():
    if not SERPAPI_KEY:
        logging.error("❌ SERPAPI_KEY가 설정되지 않았습니다.")
        sys.exit(1)

    deals = []
    logging.info("🚀 PTIS Phase 1: 파일 분리 구조 기반 특가 수집 시작...")

    for code, (name, threshold) in TARGETS.items():
        data = fetch_flight_data(ORIGIN, code, DATE_OUT, DATE_RET, SERPAPI_KEY)
        if data:
            deal = extract_best_deal(data, name, code, threshold, DATE_OUT, DATE_RET)
            if deal:
                deals.append(deal)
                logging.info(f"✅ 특가 발견: {name} - {deal['price']}")
            else:
                logging.info(f"➖ 조건 부합 특가 없음: {name}")

    send_email(deals)

if __name__ == "__main__":
    run_system()
