from dataclasses import dataclass
from datetime import date

@dataclass(frozen=True)
class Flight:
    origin: str                  # 출발 공항 코드 (예: ICN)
    destination: str             # 도착 공항 코드
    depart_date: date            # 출발일
    return_date: date            # 귀국일
    price: int                   # 현재 특가 가격
    average_price: int           # 평소 평균 가격
    discount_percentage: int     # 할인율 (예: 76)
    airline: str                 # 항공사 코드
    duration: int                # 비행 시간 (분 단위)
    stops: int                   # 경유 횟수 (직항은 0)
    booking_link: str            # 예약 링크
