from typing import List, Dict, Tuple
from datetime import datetime
from dataclasses import replace
from models import Flight
from config import (
    MIN_DISCOUNT_PERCENTAGE,
    DOMESTIC_ALLOWED_ORIGINS,
    MAX_VALUE_RATIO,
    DISCOUNT_BYPASS_RATIO,
    MAX_PER_DESTINATION,
    KEEP_ALT_DATES,
)
from valuation import value_ratio, grade, trip_days_range


def _parse_date(date_str: str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def normalize_and_deduplicate(origin: str, raw_deals: list) -> List[Flight]:
    best_flights: Dict[Tuple[str, str, str, str], Flight] = {}

    for deal in raw_deals:
        try:
            depart_date = _parse_date(deal.get("outbound_date", ""))
            return_date = _parse_date(deal.get("return_date", ""))
            if not depart_date or not return_date:
                continue

            price = deal.get("price", 0)
            destination_id = deal.get("destination_id", "UNKNOWN")
            destination_name = deal.get("name", "알 수 없음")
            destination_country = deal.get("country", "")

            # ── 게이트 1: 권역별 체류일수 (name 기반 매칭 포함) ──
            trip_days = (return_date - depart_date).days
            min_days, max_days = trip_days_range(destination_id, destination_country, destination_name)
            if not (min_days <= trip_days <= max_days):
                continue

            # ── 게이트 2: 권역 기준가 대비 비율 ──
            ratio = value_ratio(price, destination_id, destination_country, destination_name)
            if ratio is None or ratio > MAX_VALUE_RATIO:
                continue

            # ── 게이트 3: 할인율. 단, 이미 충분히 싸면 면제 ──
            discount_percentage = deal.get("discount_percentage", 0)
            if ratio > DISCOUNT_BYPASS_RATIO and discount_percentage < MIN_DISCOUNT_PERCENTAGE:
                continue

            # 국내 목적지는 접근성 좋은 출발지에서만 허용
            if destination_country == "대한민국" and origin not in DOMESTIC_ALLOWED_ORIGINS:
                continue

            flight = Flight(
                origin=origin,
                destination=destination_id,
                destination_name=destination_name,
                destination_country=destination_country,
                depart_date=depart_date,
                return_date=return_date,
                price=price,
                average_price=deal.get("average_price", 0),
                discount_percentage=discount_percentage,
                airline=deal.get("airline", "Unknown"),
                duration=deal.get("duration", 0),
                stops=deal.get("stops", 0),
                booking_link=deal.get("flight_link", ""),
                value_ratio=ratio,
                value_grade=grade(ratio),
            )

            # dedup 키는 그대로 destination_id 포함 (동일 날짜 중복 제거용)
            dedup_key = (flight.origin, flight.destination, str(flight.depart_date), str(flight.return_date))
            if dedup_key not in best_flights or price < best_flights[dedup_key].price:
                best_flights[dedup_key] = flight

        except Exception:
            continue

    return collapse_by_destination(list(best_flights.values()))


def collapse_by_destination(
    flights: List[Flight],
    max_per_dest: int = MAX_PER_DESTINATION,
    keep_alts: int = KEEP_ALT_DATES,
) -> List[Flight]:
    """
    목적지별로 저렴한 순 max_per_dest건을 노출하고 나머지는 alt_dates로 접는다.
    destination_id가 신뢰할 수 없는 값일 수 있어 (origin, destination_name)으로 묶는다.
    """
    buckets: Dict[Tuple[str, str], List[Flight]] = {}
    for f in flights:
        buckets.setdefault((f.origin, f.destination_name), []).append(f)

    result = []
    for group in buckets.values():
        group.sort(key=lambda f: f.price)
        shown = group[:max_per_dest]
        rest = group[max_per_dest:max_per_dest + keep_alts]

        alt_dates = [
            (str(f.depart_date), str(f.return_date), f.price) for f in rest
        ]
        result.append(replace(shown[0], alt_dates=alt_dates))
        result.extend(shown[1:])

    return result
