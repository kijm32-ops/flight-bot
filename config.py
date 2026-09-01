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
# MAX_VALUE_RATIO 는 이제 느슨한 안전망일 뿐이다.
# 실질적인 가격 컷은 selection.TIER_HARD_CAP 이,
# 순위는 회차 내 상대평가가 담당한다.
# 1.0 으로 두면 기준가보다 1원만 비싸도 후보에서 사라져
# 유럽/미주가 리포트에 아예 도달하지 못한다.
MAX_VALUE_RATIO = 1.20

ALERT_VALUE_RATIO = 0.85
MIN_DISCOUNT_PERCENTAGE = 20
DISCOUNT_BYPASS_RATIO = 0.75
ORIGIN_SWAP_THRESHOLD = 50_000

# selection.strict_collapse() 가 목적지당 1건을 최종 보장하므로
# 여기서는 1로 두고 나머지는 alt_dates 로 접는다.
MAX_PER_DESTINATION = 1
KEEP_ALT_DATES = 4

# 체류일수 상한에 허용할 여유일. far/deep 프로필은 trip_length 7~16 으로
# 검색하기 때문에 상한을 엄격히 적용하면 근거리 결과가 거의 전멸한다.
# (예: sea_near 상한 9일 → far 프로필의 10~14박 결과 전량 폐기)
TRIP_DAYS_MAX_SLACK = 5
# ────────────────────────────────────────────────────

# ── 권역별 체류일수는 valuation.TIER_TRIP_DAYS 가 단일 출처 ──
# 이전 버전은 여기에 같은 이름의 사본을 두었으나 아무도 참조하지 않는
# 죽은 코드였고, valuation.py 쪽과 값이 어긋나 있었다
# (sea_far 10 vs 12, sea_mid 는 여기 아예 없었음).
# 수정할 일이 있으면 valuation.py 만 고칠 것.
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
    "sea":   (_range(30, 120),  "4,11"),   # 동남아/몽골 전용 체류일수
    "far":   (_range(90, 240),  "7,14"),   # 장거리 (유럽/대양주)
    "deep":  (_range(240, 330), "7,16"),   # 심층: 8~11개월 후 장거리 (주 1회)
}

# 출발지별로 실제 의미 있는 프로필만 배정
ORIGIN_PROFILES = {
    "ICN": ["near", "mid", "sea", "far", "deep"],
    "CJJ": ["near", "mid"],
    "GMP": ["near"],
}

# 매일 실행되는 작업 (우선순위 순 — 예산 부족 시 뒤에서부터 잘림)
# 7작업 x 30일 = 210, + 심층 약 4.3회 = 약 215회/월 (안전 예산 235)
DAILY_TASK_PRIORITY = [
    ("ICN", "near"),
    ("ICN", "mid"),
    ("ICN", "sea"),
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
