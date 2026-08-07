import os
from datetime import datetime, timedelta

SERPAPI_KEY = os.environ.get("SERPAPI_KEY")
GMAIL_USER = os.environ.get("GMAIL_USER")
GMAIL_PASSWORD = os.environ.get("GMAIL_PASSWORD")

# Phase 3: 다중 출발지 배열 확장
TARGET_ORIGINS = ["ICN", "CJJ", "GMP", "YNY"]

tomorrow = datetime.now() + timedelta(days=1)
future_30d = tomorrow + timedelta(days=30)
DATE_RANGE = f"{tomorrow.strftime('%Y-%m-%d')},{future_30d.strftime('%Y-%m-%d')}"

# 출발지(departure_id)는 스레드별로 동적 할당되므로 공통 파라미터에서 제외합니다.
BASE_SEARCH_PARAMS = {
    "engine": "google_flights_deals",
    "outbound_date": DATE_RANGE,
    "trip_length": "1,7",   # 당일치기 ~ 짧은 휴가(7일)로 범위 축소
    "currency": "KRW",
    "hl": "ko",
    "gl": "kr"
}
