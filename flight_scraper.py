import os
import sys
import smtplib
import requests
import logging
from typing import List, Dict, Any, Optional, Tuple
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# 1. 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 2. API 호출 모듈 분리
def fetch_flight_data(origin: str, dest_code: str, date_out: str, date_ret: str, api_key: str) -> Optional[Dict[str, Any]]:
    """SerpApi를 호출하여 항공권 데이터를 가져옵니다."""
    url = "https://serpapi.com/search.json"
    params = {
        "engine": "google_flights",
        "departure_id": origin,
        "arrival_id": dest_code,
        "outbound_date": date_out,
        "return_date": date_ret,
        "currency": "KRW",
        "hl": "ko",
        "gl": "kr",
        "api_key": api_key
    }
    
    try:
        res = requests.get(url, params=params, timeout=30)
        res.raise_for_status() # HTTP 에러 발생 시 예외 처리
        return res.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"❌ API 호출 에러 ({dest_code}): {e}")
        return None

# 3. 데이터 파싱 모듈 분리 (버그 수정 완료)
def extract_best_deal(data: Dict[str, Any], dest_name: str, dest_code: str, threshold: int, date_out: str, date_ret: str) -> Optional[Dict[str, str]]:
    """API 응답 데이터에서 목표가 이하의 '최저가 직항' 항공권을 찾습니다."""
    flights = data.get("best_flights", []) + data.get("other_flights", [])
    
    lowest_price = float('inf')
    best_flight = None
    
    # break 없이 전체를 순회하며 최저가 탐색
    for flight in flights:
        price = flight.get("price")
        is_direct = len(flight.get("flights", [])) == 1 and "layovers" not in flight
        
        if price and is_direct:
            if price < lowest_price:
                lowest_price = price
                best_flight = flight
                
    if best_flight and lowest_price <= threshold:
        # 실제 검색 조건이 포함된 완벽한 구글 플라이트 링크 생성
        search_url = f"https://www.google.com/travel/flights?q=Flights%20to%20{dest_code}%20from%20ICN%20on%20{date_out}%20through%20{date_ret}"
        
        return {
            "destination": dest_name,
            "price": f"{lowest_price:,}원",
            "discount": f"목표가({threshold:,}원) 이하 특가!",
            "link": search_url
        }
    
    return None

# 4. 전체 제어 모듈
def get_flight_deals() -> List[Dict[str, str]]:
    """전체 타겟 공항을 순회하며 특가 항공권을 수집합니다."""
    serpapi_key = os.environ.get("SERPAPI_KEY")
    if not serpapi_key:
        logging.error("❌ SERPAPI_KEY가 설정되지 않았습니다.")
        sys.exit(1)

    # 기존 하드코딩 설정 유지 (Phase 0 원칙 엄수)
    origin = "ICN"
    date_out = "2026-05-15"
    date_ret = "2026-05-19"
    targets: Dict[str, Tuple[str, int]] = {
        "NRT": ("도쿄(나리타)", 250000),
        "KIX": ("오사카(간사이)", 220000),
        "FUK": ("후쿠오카", 160000),
        "TPE": ("타이베이", 230000),
        "DAD": ("다낭", 290000),
        "BKK": ("방콕", 350000),
        "CBU": ("세부", 260000),
    }

    deals: List[Dict[str, str]] = []
    logging.info("🚀 PTIS Phase 0: 실시간 특가 수집을 시작합니다...")

    for code, (name, threshold) in targets.items():
        data = fetch_flight_data(origin, code, date_out, date_ret, serpapi_key)
        if data:
            deal = extract_best_deal(data, name, code, threshold, date_out, date_ret)
            if deal:
                deals.append(deal)
                logging.info(f"✅ 특가 발견: {name} - {deal['price']}")
            else:
                logging.info(f"➖ 조건 부합 특가 없음: {name}")

    return deals

# 5. 알림 발송 모듈
def send_email(deals: List[Dict[str, str]]) -> None:
    """수집된 특가 정보를 이메일로 전송합니다."""
    # 이메일 주소 환경변수 처리
    sender_email = os.environ.get("GMAIL_USER")
    receiver_email = os.environ.get("GMAIL_USER") 
    sender_password = os.environ.get("GMAIL_PASSWORD")

    if not sender_email or not sender_password:
        logging.error("❌ GMAIL_USER 또는 GMAIL_PASSWORD 환경변수가 없습니다.")
        sys.exit(1)

    msg = MIMEMultipart()
    msg['Subject'] = f"✈️ [PTIS] 오늘의 실시간 특가 리포트 ({len(deals)}건)"
    msg['From'] = sender_email
    msg['To'] = receiver_email

    if not deals:
        html_content = "<h3>📢 오늘의 특가 항공권 내역</h3><p>현재 설정한 목표가 이하의 직항 특가 항공권이 없습니다.</p>"
    else:
        html_content = """
        <html><body style='font-family: Malgun Gothic, sans-serif; padding: 20px;'>
            <h2 style='color: #1a73e8;'>📊 오늘의 실시간 직항 특가</h2>
            <table border='0' style='border-collapse: collapse; width: 100%; max-width: 650px;'>
                <tr style='background-color: #1a73e8; color: white;'>
                    <th style='padding: 10px;'>목적지</th>
                    <th style='padding: 10px;'>특가 금액</th>
                    <th style='padding: 10px;'>예약</th>
                </tr>
        """
        for deal in deals:
            html_content += f"""
                <tr style='border-bottom: 1px solid #eee;'>
                    <td style='padding: 10px; font-weight: bold;'>{deal['destination']}</td>
                    <td style='padding: 10px; color: #d93025; font-weight: bold;'>{deal['price']}</td>
                    <td style='padding: 10px;'><a href='{deal['link']}' target='_blank'>확인</a></td>
                </tr>
            """
        html_content += "</table></body></html>"

    msg.attach(MIMEText(html_content, 'html'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        logging.info("📬 PTIS 리포트 메일 발송 성공!")
    except Exception as e:
        logging.error(f"❌ 메일 발송 에러: {e}")

if __name__ == "__main__":
    flight_deals = get_flight_deals()
    send_email(flight_deals)
