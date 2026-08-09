import json
import os
from datetime import datetime, timedelta

STATE_FILE = "data/state.json"


def load_state() -> dict:
    """저장된 상태 파일을 불러온다. 없으면 빈 상태로 시작."""
    if not os.path.exists(STATE_FILE):
        return {"route_history": {}, "kakao_consecutive_failures": 0, "api_usage": {}}
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"route_history": {}, "kakao_consecutive_failures": 0, "api_usage": {}}


def save_state(state: dict) -> None:
    """상태를 파일로 저장한다 (워크플로우에서 커밋되어 다음 실행에 이어짐)."""
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def update_route_history(state: dict, flights: list) -> set:
    """
    노선별(출발지->목적지) 최근 30일 가격 이력을 갱신하고,
    이번에 새로 '30일 최저가'를 기록한 항공권의 dedup key 집합을 반환한다.
    """
    today = datetime.now().strftime("%Y-%m-%d")
    cutoff = datetime.now() - timedelta(days=30)
    history = state.setdefault("route_history", {})
    low_price_keys = set()

    # 오늘 검색되지 않은 노선을 포함해 전체 이력에서 30일 지난 데이터 정리
    routes_to_delete = []
    for route_key, entries in history.items():
        pruned = [
            e for e in entries
            if datetime.strptime(e["date"], "%Y-%m-%d") >= cutoff
        ]
        if pruned:
            history[route_key] = pruned
        else:
            routes_to_delete.append(route_key)

    for route_key in routes_to_delete:
        del history[route_key]

    # 이번에 검색된 항공권 반영
    for flight in flights:
        route_key = f"{flight.origin}->{flight.destination_name}"
        entries = history.get(route_key, [])

        previous_min = min((e["price"] for e in entries), default=None)

        if previous_min is not None and flight.price <= previous_min:
            dedup_key = (
                flight.origin, flight.destination,
                str(flight.depart_date), str(flight.return_date)
            )
            low_price_keys.add(dedup_key)

        entries.append({"date": today, "price": flight.price})
        history[route_key] = entries

    return low_price_keys


def record_api_calls(state: dict, count: int) -> int:
    """이번 달 API 호출 누적 횟수를 기록하고 반환한다. 월이 바뀌면 리셋."""
    month = datetime.now().strftime("%Y-%m")
    usage = state.setdefault("api_usage", {"month": month, "count": 0})

    if usage.get("month") != month:
        usage["month"] = month
        usage["count"] = 0

    usage["count"] += count
    return usage["count"]


def record_kakao_result(state: dict, success: bool) -> bool:
    """
    카카오 발송 성공/실패를 기록한다.
    3회 연속 실패 시 True(경고 필요)를 반환.
    """
    if success:
        state["kakao_consecutive_failures"] = 0
        return False

    state["kakao_consecutive_failures"] = state.get("kakao_consecutive_failures", 0) + 1
    return state["kakao_consecutive_failures"] >= 3
