import os
from datetime import datetime, timedelta

SERPAPI_KEY = os.environ.get("SERPAPI_KEY")
GMAIL_USER = os.environ.get("GMAIL_USER")
GMAIL_PASSWORD = os.environ.get("GMAIL_PASSWORD")
KAKAO_JS_KEY = os.environ.get("KAKAO_JS_KEY")

PAGE_URL = "https://kijm32-ops.github.io/flight-bot/"

# 양양(YNY) 제외 — 국제선 노선이 거의 없어 호출 대비 수확이 없음
TARGET_ORIGINS = ["ICN", "CJJ", "GMP"]
DOMESTIC_ALLOWED_ORIGINS = ["CJJ", "GMP", "ICN"]

# ── SerpApi 무료 티어 예산 관리 ──────────────────────
SERPAPI_MONTHLY_LIMIT = 250      # 무료 요금제 한도
SERPAPI_SAFE_BUDGET = 235        # 재시도/수동실행 대비 15회 예비분 확보
API_QUOTA_WARNING_THRESHOLD = 200
# ────────────────────────────────────────────────────

# ── 특가 판정 기준 ──────────────────────────────────
MAX_VALUE_RATIO = 1.05
ALERT_VALUE_RATIO = 0.85
MIN_DISCOUNT_PERCENTAGE = 20
DISCOUNT_BYPASS_RATIO = 0.75
ORIGIN_SWAP_THRESHOLD = 50_000
MAX_PER_DESTINATION = 2
KEEP_ALT_DATES = 4
# ────────────────────────────────────────────────────

# ── 권역별 최소/최대 체류일수 ────────────────────────
TIER_TRIP_DAYS = {
    "domestic":  (2, 7),
    "jp_near":   (2, 7),
    "jp_mid":    (3, 7),
    "cn_near":   (2, 7),
    "cn_mid":    (3, 7),
    "tw_hk":     (3, 7),
    "sea_near":  (4, 9),
    "sea_far":   (5, 10),
    "mongolia":  (4, 8),
    "guam":      (4, 8),
    "oceania":   (7, 14),
    "europe":    (7, 14),
    "namerica":  (7, 14),
    "longhaul":  (7, 14),
}
DEFAULT_TRIP_DAYS = (3, 7)
# ────────────────────────────────────────────────────

tomorrow = datetime.now() + timedelta(days=1)


def _range(start_offset: int, end_offset: int) -> str:
    s = tomorrow + timedelta(days=start_offset)
    e = tomorrow + timedelta(days=end_offset)
    return f"{s.strftime('%Y-%m-%d')},{e.strftime('%Y-%m-%d')}"


# 프로필 정의: {이름: (outbound_date 범위, trip_length)}
PROFILES = {
    "near": (_range(0, 60),   "2,7"),    # 근거리 임박
    "mid":  (_range(45, 150), "3,9"),    # 중거리
    "far":  (_range(90, 240), "7,14"),   # 장거리 (유럽/대양주)
}

# 출발지별로 실제 의미 있는 프로필만 배정 (호출 절감의 핵심)
# GMP 국제선은 하네다/간사이/베이징/타이베이 수준, CJJ는 장거리 직항 없음
ORIGIN_PROFILES = {
    "ICN": ["near", "mid", "far"],
    "CJJ": ["near", "mid"],
    "GMP": ["near"],
}

# 예산 부족 시 뒤쪽부터 잘라냄 (앞이 우선순위 높음)
TASK_PRIORITY = [
    ("ICN", "near"),
    ("ICN", "mid"),
    ("CJJ", "near"),
    ("ICN", "far"),
    ("CJJ", "mid"),
    ("GMP", "near"),
]

BASE_SEARCH_PARAMS = {
    "engine": "google_flights_deals",
    "currency": "KRW",
    "hl": "ko",
    "gl": "kr",
}
