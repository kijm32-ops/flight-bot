import os
from datetime import datetime, timedelta

SERPAPI_KEY = os.environ.get("SERPAPI_KEY")
GMAIL_USER = os.environ.get("GMAIL_USER")
GMAIL_PASSWORD = os.environ.get("GMAIL_PASSWORD")

# [Issue 1 & 3 해결] 접근성 좋은 공항 다중 선택 및 유동적 날짜 계산
ORIGINS = "ICN,CJJ,GMP,YNY"  # 인천, 청주, 김포, 양양을 한 번에 스캔

# 오늘 기준 향후 30일 이내의 기간 자동 설정
today = datetime.now()
future_30d = today + timedelta(days=30)
DATE_RANGE = f"{today.strftime('%Y-%m-%d')},{future_30d.strftime('%Y-%m-%d')}"

# SerpApi google_flights_deals 전용 파라미터 세팅
SEARCH_PARAMS = {
    "engine": "google_flights_deals",
    "departure_id": ORIGINS,
    "outbound_date": DATE_RANGE,
    "trip_length": "3,14", # 3박 ~ 14박 사이의 모든 일정 탐색
    "currency": "KRW",
    "hl": "ko",
    "gl": "kr"
}
