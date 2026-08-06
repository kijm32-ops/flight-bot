import logging
import sys
import json
import requests
from config import SERPAPI_KEY, SEARCH_PARAMS

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def run_investigation():
    if not SERPAPI_KEY:
        sys.exit(1)

    url = "https://serpapi.com/search.json"
    request_params = {**SEARCH_PARAMS, "api_key": SERPAPI_KEY}
    
    logging.info("🕵️‍♂️ SerpApi 증거 수집 및 심층 분석 시작...")
    
    try:
        res = requests.get(url, params=request_params, timeout=30)
        
        print("\n========== [EVIDENCE 1: Request URL] ==========")
        # API 키는 가리고 출력
        safe_url = res.url.replace(SERPAPI_KEY, "HIDDEN_KEY")
        print(safe_url)
        
        print("\n========== [EVIDENCE 2: Response Headers] ==========")
        for key, value in res.headers.items():
            print(f"{key}: {value}")
            
        print("\n========== [EVIDENCE 3: Raw JSON Data] ==========")
        raw_data = res.json()
        print(json.dumps(raw_data, ensure_ascii=False, indent=2))
        
    except Exception as e:
        logging.error(f"❌ 네트워크 예외 발생: {e}")

if __name__ == "__main__":
    run_investigation()
