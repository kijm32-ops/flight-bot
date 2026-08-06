import os

SERPAPI_KEY = os.environ.get("SERPAPI_KEY")

# [STEP 3 테스트] 
# 날짜와 기간 조건은 비워두고, 오직 ICN(인천) 출발 데이터가 존재하는지만 확인합니다.
SEARCH_PARAMS = {
    "engine": "google_flights_deals",
    "departure_id": "ICN",
    "currency": "KRW",
    "hl": "ko",
    "gl": "kr"
}
