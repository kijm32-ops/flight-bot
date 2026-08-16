from typing import List, Dict, Tuple
from datetime import datetime
from dataclasses import replace
from models import Flight
from config import (
    MIN_DISCOUNT_PERCENTAGE,
    DOMESTIC_ALLOWED_ORIGINS,
    MAX_VALUE_RATIO,
    DISCOUNT_BYPASS_RATIO,
)
from valuation import value_ratio, grade


def _parse_date(date_str: str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def normalize_and_deduplicate(origin: str, raw_deals: list) -> List[Flight]:
    # Deduplication Key: (origin, destination, depart_date, return_date)
    best_flights: Dict[Tuple[str, str, str, str], Flight] = {}

    for deal in raw_deals:
        try:
            depart_date = _parse_date(deal.get("outbound_date", ""))
            return_date = _parse_date(deal.get("return_date", ""))
            if not depart_date or not return_date:
                continue

            # 체류 기간 필터: 3~7일(3박 이상 ~ 짧은 휴가)만 허용
            trip_days = (return_date - depart_date).days
            if not (3 <= trip_days <= 7):
                continue

            price = deal.get("price", 0)
            destination_id = deal.get("destination_id", "UNKNOWN")
            destination_country = deal.get("country", "")

            # ── 게이트 1: 권역 기준가 대비 비율 (절대 통과 불가 라인) ──
            ratio = value_ratio(price, destination_id, destination_country)
            if ratio is None or ratio > MAX_VALUE_RATIO:
                continue

            # ── 게이트 2: 할인율. 단, 이미 충분히 싸면(ratio가 낮으면) 면제 ──
            discount_percentage = deal.get("discount_percentage", 0)
            if ratio > DISCOUNT_BYPASS_RATIO and discount_percentage < MIN_DISCOUNT_PERCENTAGE:
                continue

            # 국내 목적지는 원주 접근성 좋은 출발지(청주/김포/인천)에서만 허용
            if destination_country == "대한민국" and origin not in DOMESTIC_ALLOWED_ORIGINS:
                continue

            flight = Flight(
                origin=origin,
                destination=destination_id,
                destination_name=deal.get("name", "알 수 없음"),
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

            dedup_key = (flight.origin, flight.destination, str(flight.depart_date), str(flight.return_date))
            if dedup_key not in best_flights or price < best_flights[dedup_key].price:
                best_flights[dedup_key] = flight

        except Exception:
            continue

    all_flights = list(best_flights.values())
    return collapse_by_destination(all_flights)


def collapse_by_destination(flights: List[Flight], keep_alts: int = 3) -> List[Flight]:
    """
    목적지별로 최저가 1건만 대표로 남기고,
    나머지 날짜 조합은 alt_dates에 (출발일, 귀국일, 가격)로 첨부한다.
    Flight가 frozen dataclass이므로 dataclasses.replace()로 새 객체를 만든다.
    """
    buckets: Dict[Tuple[str, str], List[Flight]] = {}
    for f in flights:
        buckets.setdefault((f.origin, f.destination), []).append(f)

    result = []
    for group in buckets.values():
        group.sort(key=lambda f: f.price)
        best = group[0]
        rest = group[1:keep_alts + 1]
        alt_dates = [
            (str(f.depart_date), str(f.return_date), f.price) for f in rest
        ]
        # frozen dataclass라 mutation 대신 replace로 새 인스턴스 생성
        best_with_alts = replace(best, alt_dates=alt_dates)
        result.append(best_with_alts)
    return result
