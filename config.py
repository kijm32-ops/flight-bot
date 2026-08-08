import os
from datetime import datetime, timedelta

SERPAPI_KEY = os.environ.get("SERPAPI_KEY")
GMAIL_USER = os.environ.get("GMAIL_USER")
GMAIL_PASSWORD = os.environ.get("GMAIL_PASSWORD")

# Phase 3: 다중 출발지 배열 확장
TARGET_ORIGINS = ["ICN", "CJJ", "GMP", "YNY"]

# 검색 범위: 내일부터 약 210일 후(다음 해 2월 말경)까지
tomorrow = datetime.now() + timedelta(days=1)
future_horizon = tomorrow + timedelta(days=210)
DATE_RANGE = f"{tomorrow.strftime('%Y-%m-%d')},{future_horizon.strftime('%Y-%m-%d')}"

# 최소 할인율 기준 (이 값 미만인 특가는 제외)
MIN_DISCOUNT_PERCENTAGE = 20

# 출발지(departure_id)는 스레드별로 동적 할당되므로 공통 파라미터에서 제외합니다.
BASE_SEARCH_PARAMS = {
    "engine": "google_flights_deals",
    "outbound_date": DATE_RANGE,
    "trip_length": "2,7",   # 2박~7박(짧은 휴가)로 범위 유지
    "currency": "KRW",
    "hl": "ko",
    "gl": "kr"
}
