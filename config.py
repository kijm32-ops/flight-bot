import os
from datetime import datetime, timedelta

SERPAPI_KEY = os.environ.get("SERPAPI_KEY")
GMAIL_USER = os.environ.get("GMAIL_USER")
GMAIL_PASSWORD = os.environ.get("GMAIL_PASSWORD")

# Phase 3: 다중 출발지 배열 확장
TARGET_ORIGINS = ["ICN", "CJJ", "GMP", "YNY"]

# 최소 할인율 기준 (이 값 미만인 특가는 제외)
MIN_DISCOUNT_PERCENTAGE = 25

# 근거리/원거리 2단계 날짜 구간 (무료 요금제 250회/월 한도 안에서 운영)
tomorrow = datetime.now() + timedelta(days=1)

near_start = tomorrow
near_end = tomorrow + timedelta(days=60)
NEAR_DATE_RANGE = f"{near_start.strftime('%Y-%m-%d')},{near_end.strftime('%Y-%m-%d')}"

far_start = tomorrow + timedelta(days=90)
far_end = tomorrow + timedelta(days=210)
FAR_DATE_RANGE = f"{far_start.strftime('%Y-%m-%d')},{far_end.strftime('%Y-%m-%d')}"

DATE_RANGES = [NEAR_DATE_RANGE, FAR_DATE_RANGE]

# 공통 파라미터 (outbound_date는 실행 시 구간별로 채워짐)
BASE_SEARCH_PARAMS = {
    "engine": "google_flights_deals",
    "trip_length": "2,7",
    "currency": "KRW",
    "hl": "ko",
    "gl": "kr"
}
