import os
from datetime import datetime, timedelta

SERPAPI_KEY = os.environ.get("SERPAPI_KEY")
GMAIL_USER = os.environ.get("GMAIL_USER")
GMAIL_PASSWORD = os.environ.get("GMAIL_PASSWORD")
KAKAO_JS_KEY = os.environ.get("KAKAO_JS_KEY")

# 특가 리포트 웹페이지 주소 (GitHub Pages)
PAGE_URL = "https://kijm32-ops.github.io/flight-bot/"

# Phase 3: 다중 출발지 배열 확장
TARGET_ORIGINS = ["ICN", "CJJ", "GMP", "YNY"]

# 최소 할인율 기준 (이 값 미만인 특가는 제외)
MIN_DISCOUNT_PERCENTAGE = 25

# 국내 목적지는 이 출발지에서 뜬 것만 허용 (청주/김포/인천 접근성 기준, 양양 제외)
DOMESTIC_ALLOWED_ORIGINS = ["CJJ", "GMP", "ICN"]

# 근거리/원거리 2단계 날짜 구간 (무료 요금제 250회/월 한도 안에서 운영)
tomorrow = datetime.now() + timedelta(days=1)

near_start = tomorrow
near_end = tomorrow + timedelta(days=60)
NEAR_DATE_RANGE = f"{near_start.strftime('%Y-%m-%d')},{near_end.strftime('%Y-%m-%d')}"

far_start = tomorrow + timedelta(days=90)
far_end = tomorrow + timedelta(days=210)
FAR_DATE_RANGE = f"{far_start.strftime('%Y-%m-%d')},{far_end.strftime('%Y-%m-%d')}"

DATE_RANGES = [NEAR_DATE_RANGE, FAR_DATE_RANGE]

BASE_SEARCH_PARAMS = {
    "engine": "google_flights_deals",
    "trip_length": "3,7",
    "currency": "KRW",
    "hl": "ko",
    "gl": "kr"
}
