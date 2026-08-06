import requests
import logging
from typing import Dict, Any, Optional

def fetch_raw_flight_data(api_key: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    [Phase 2 원칙] 비즈니스 로직 절대 금지. 필터링 금지.
    오직 주어진 파라미터로 SerpApi를 호출하여 순수 JSON 데이터만 반환합니다.
    """
    url = "https://serpapi.com/search.json"
    
    # 설정된 파라미터에 api_key만 덧붙여서 API 요청
    request_params = {**params, "api_key": api_key}
    
    try:
        res = requests.get(url, params=request_params, timeout=30)
        res.raise_for_status()
        return res.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"❌ API 호출 에러: {e}")
        return None
