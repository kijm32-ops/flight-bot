import os

SERPAPI_KEY = os.environ.get("SERPAPI_KEY")

# [STEP 2 안전 모드 테스트] 
# 날짜, 다중 출발지를 모두 빼고 가장 기본인 LAX(로스앤젤레스) 단일 출발만 테스트합니다.
SEARCH_PARAMS = {
    "engine": "google_flights_deals",
    "departure_id": "LAX",
    "currency": "KRW",
    "hl": "ko",
    "gl": "kr"
}
