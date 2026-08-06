import os
from datetime import datetime, timedelta

SERPAPI_KEY = os.environ.get("SERPAPI_KEY")
GMAIL_USER = os.environ.get("GMAIL_USER")
GMAIL_PASSWORD = os.environ.get("GMAIL_PASSWORD")

# [수정 1] 출발지 최적화: 서울(SEL - 인천/김포 자동 포함)과 청주(CJJ)만 타겟팅
ORIGINS = "SEL,CJJ" 

# [수정 2] 날짜 최적화: 시차 꼬임을 방지하기 위해 무조건 '내일'부터 30일간 검색
tomorrow = datetime.now() + timedelta(days=1)
future_30d = tomorrow + timedelta(days=30)
DATE_RANGE = f"{tomorrow.strftime('%Y-%m-%d')},{future_30d.strftime('%Y-%m-%d')}"

SEARCH_PARAMS = {
    "engine": "google_flights_deals",
    "departure_id": ORIGINS,
    "outbound_date": DATE_RANGE,
    "trip_length": "3,14", # 3박 ~ 14박 사이
    "currency": "KRW",
    "hl": "ko",
    "gl": "kr"
}
