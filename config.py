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

# 국내 목적지는 이 출발지에서 뜬 것만 허용 (청주/김포/인천 접근성 기준, 양양 제외)
DOMESTIC_ALLOWED_ORIGINS = ["CJJ", "GMP", "ICN"]

# ── 특가 판정 기준 (신규) ──────────────────────────────
# 권역 기준가 대비 이 비율을 넘으면 "특가 아님"으로 완전 탈락
MAX_VALUE_RATIO = 1.0

# 리포트/알림에 실제로 노출할 상한 (참고용, 현재 코드에서는 미사용 — 필요시 normalizer에서 활용)
ALERT_VALUE_RATIO = 0.85

# 할인율은 보조 지표로 강등: 기본 최소 할인율
MIN_DISCOUNT_PERCENTAGE = 20

# value_ratio가 이 값 이하로 충분히 싸면 할인율 조건을 면제
DISCOUNT_BYPASS_RATIO = 0.75

# 같은 목적지에 대해 ICN이 이 금액 이상 싸면 지방 출발편에 경고 표시
ORIGIN_SWAP_THRESHOLD = 50_000
# ────────────────────────────────────────────────────

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
