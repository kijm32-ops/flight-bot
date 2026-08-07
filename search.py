import requests
import logging
from typing import Dict, Any, List
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

class APIFetchError(Exception):
    pass

# 최대 3회 재시도 (대기 시간: 2초 -> 4초 -> 8초)
@retry(
    wait=wait_exponential(multiplier=1, min=2, max=10),
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type(APIFetchError)
)
def fetch_raw_flight_deals(api_key: str, base_params: Dict[str, Any], origin: str) -> List[Dict[str, Any]]:
    url = "https://serpapi.com/search.json"
    request_params = {**base_params, "api_key": api_key, "departure_id": origin}
    
    try:
        logging.info(f"[{origin}] 구글 플라이트 특가 데이터 검색 중...")
        res = requests.get(url, params=request_params, timeout=30)
        res.raise_for_status()
        data = res.json()
        
        return data.get("deals", [])
    except requests.exceptions.RequestException as e:
        logging.error(f"[{origin}] ❌ API 호출 에러: {e}")
        raise APIFetchError(f"API Fetch Failed for {origin}: {e}")

res = requests.get(url, params=request_params, timeout=30)
res.raise_for_status()
data = res.json()
logging.info(f"[{origin}] 응답 키 목록: {list(data.keys())}")  # 임시 디버그 로그
return data.get("deals", [])
