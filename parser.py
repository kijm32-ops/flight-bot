from typing import Dict, Any, Optional

def extract_best_deal(data: Dict[str, Any], dest_name: str, dest_code: str, threshold: int, date_out: str, date_ret: str) -> Optional[Dict[str, str]]:
    flights = data.get("best_flights", []) + data.get("other_flights", [])
    
    lowest_price = float('inf')
    best_flight = None
    
    for flight in flights:
        price = flight.get("price")
        is_direct = len(flight.get("flights", [])) == 1 and "layovers" not in flight
        
        if price and is_direct:
            if price < lowest_price:
                lowest_price = price
                best_flight = flight
                
    if best_flight and lowest_price <= threshold:
        search_url = f"https://www.google.com/travel/flights?q=Flights%20to%20{dest_code}%20from%20ICN%20on%20{date_out}%20through%20{date_ret}"
        
        return {
            "destination": dest_name,
            "price": f"{lowest_price:,}원",
            "discount": f"목표가({threshold:,}원) 이하 특가!",
            "link": search_url
        }
    
    return None
