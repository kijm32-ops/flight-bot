import requests
import logging
from typing import Dict, Any, Optional

def fetch_flight_data(origin: str, dest_code: str, date_out: str, date_ret: str, api_key: str) -> Optional[Dict[str, Any]]:
    url = "https://serpapi.com/search.json"
    params = {
        "engine": "google_flights",
        "departure_id": origin,
        "arrival_id": dest_code,
        "outbound_date": date_out,
        "return_date": date_ret,
        "currency": "KRW",
        "hl": "ko",
        "gl": "kr",
        "api_key": api_key
    }
    
    try:
        res = requests.get(url, params=params, timeout=30)
        res.raise_for_status()
        return res.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"❌ API 호출 에러 ({dest_code}): {e}")
        return None
