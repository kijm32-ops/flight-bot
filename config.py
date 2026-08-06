import os
from datetime import datetime, timedelta

SERPAPI_KEY = os.environ.get("SERPAPI_KEY")

# [STEP 4 & 5 테스트] 
# 출발지는 안전이 확보된 ICN(인천) 단독으로 유지합니다.
# 유동적 날짜(내일부터 30일)와 여행 기간(3~14일) 파라미터를 추가하여 범인을 색출합니다.
tomorrow = datetime.now() + timedelta(days=1)
future_30d = tomorrow + timedelta(days=30)
DATE_RANGE = f"{tomorrow.strftime('%Y-%m-%d')},{future_30d.strftime('%Y-%m-%d')}"

SEARCH_PARAMS = {
    "engine": "google_flights_deals",
    "departure_id": "ICN",
    "outbound_date": DATE_RANGE,
    "trip_length": "3,14",
    "currency": "KRW",
    "hl": "ko",
    "gl": "kr"
}
