from typing import List, Dict, Tuple
from datetime import datetime
from models import Flight

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
            depart_date = _parse_date(deal.get("departure_date", ""))
            return_date = _parse_date(deal.get("return_date", ""))
            
            if not depart_date or not return_date:
                continue

            price = deal.get("price", 0)
            
            flight = Flight(
                origin=origin,
                destination=deal.get("destination_id", "UNKNOWN"),
                depart_date=depart_date,
                return_date=return_date,
                price=price,
                average_price=deal.get("average_price", 0),
                discount_percentage=deal.get("discount_percentage", 0),
                airline=deal.get("airline", "Unknown"),
                duration=deal.get("duration", 0),
                stops=deal.get("stops", 0),
                booking_link=deal.get("link", "")
            )

            dedup_key = (flight.origin, flight.destination, str(flight.depart_date), str(flight.return_date))

            # 키가 없거나 기존 가격보다 더 싸면 덮어쓰기
            if dedup_key not in best_flights or price < best_flights[dedup_key].price:
                best_flights[dedup_key] = flight

        except Exception:
            continue # 손상된 개별 데이터는 무시하고 계속 진행

    return list(best_flights.values())
