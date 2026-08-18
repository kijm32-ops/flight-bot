import os
from datetime import datetime, timedelta, timezone

SERPAPI_KEY = os.environ.get("SERPAPI_KEY")
GMAIL_USER = os.environ.get("GMAIL_USER")
GMAIL_PASSWORD = os.environ.get("GMAIL_PASSWORD")
KAKAO_JS_KEY = os.environ.get("KAKAO_JS_KEY")

PAGE_URL = "https://kijm32-ops.github.io/flight-bot/"

# 양양(YNY) 제외 — 국제선 노선이 거의 없어 호출 대비 수확이 없음
TARGET_ORIGINS = ["ICN", "CJJ", "GMP"]
DOMESTIC_ALLOWED_ORIGINS = ["CJJ", "GMP", "ICN"]

# ── SerpApi 무료 티어 예산 관리 ──────────────────────
SERPAPI_MONTHLY_LIMIT = 250
SERPAPI_SAFE_BUDGET = 235        # 재시도/수동실행 대비 15회 예비분
API_QUOTA_WARNING_THRESHOLD = 200
# ────────────────────────────────────────────────────

# ── 특가 판정 기준 ──────────────────────────────────
MAX_VALUE_RATIO = 1.0
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

# ── 요일 판정 (GitHub Actions는 UTC로 동작하므로 KST 고정) ──
KST = timezone(timedelta(hours=9))


def _now_kst() -> datetime:
    return datetime.now(KST)


def is_deep_scan_day() -> bool:
    """
    주 1회 심층 검색 실행 여부.
    - 기본: 한국 시간 토요일(weekday() == 5)
    - FORCE_DEEP_SCAN=1 환경변수로 강제 실행 가능 (테스트/수동 트리거용)
    """
    if os.environ.get("FORCE_DEEP_SCAN") == "1":
        return True
    return _now_kst().weekday() == 5


tomorrow = _now_kst() + timedelta(days=1)


def _range(start_offset: int, end_offset: int) -> str:
    s = tomorrow + timedelta(days=start_offset)
    e = tomorrow + timedelta(days=end_offset)
    return f"{s.strftime('%Y-%m-%d')},{e.strftime('%Y-%m-%d')}"


# 프로필 정의: {이름: (outbound_date 범위, trip_length)}
PROFILES = {
    "near":  (_range(0, 60),    "2,7"),    # 근거리 임박
    "mid":   (_range(45, 150),  "3,9"),    # 중거리
    "far":   (_range(90, 240),  "7,14"),   # 장거리 (유럽/대양주)
    "deep":  (_range(240, 330), "7,16"),   # 심층: 8~11개월 후 장거리 (주 1회)
}

# 출발지별로 실제 의미 있는 프로필만 배정
ORIGIN_PROFILES = {
    "ICN": ["near", "mid", "far", "deep"],
    "CJJ": ["near", "mid"],
    "GMP": ["near"],
}

# 매일 실행되는 작업 (우선순위 순 — 예산 부족 시 뒤에서부터 잘림)
DAILY_TASK_PRIORITY = [
    ("ICN", "near"),
    ("ICN", "mid"),
    ("CJJ", "near"),
    ("ICN", "far"),
    ("CJJ", "mid"),
    ("GMP", "near"),
]

# 심층 검색일에만 추가되는 작업 (일반 작업보다 후순위)
DEEP_TASK_PRIORITY = [
    ("ICN", "deep"),
]

BASE_SEARCH_PARAMS = {
    "engine": "google_flights_deals",
    "currency": "KRW",
    "hl": "ko",
    "gl": "kr",
}
