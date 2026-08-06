import os
import smtplib
import sys
import requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def fetch_flight_deals():
    serpapi_key = os.environ.get("SERPAPI_KEY")
    if not serpapi_key:
        print("❌ SERPAPI_KEY가 설정되지 않았습니다.")
        sys.exit(1)

    # 주요 노선 및 목표 특가 설정 (원)
    targets = {
        "NRT": ("도쿄(나리타)", 250000),
        "KIX": ("오사카(간사이)", 220000),
        "FUK": ("후쿠오카", 160000),
        "TPE": ("타이베이", 230000),
        "DAD": ("다낭", 290000),
        "BKK": ("방콕", 350000),
        "CBU": ("세부", 260000),
    }

    deals = []
    print("🚀 SerpApi를 통해 구글 플라이트 실시간 특가 수집을 시작합니다...")

    for code, (name, threshold) in targets.items():
        try:
            url = "https://serpapi.com/search.json"
            params = {
                "engine": "google_flights",
                "departure_id": "ICN",  # 인천 출발
                "arrival_id": code,
                "outbound_date": "2026-05-15", # 임의의 출발일 (예시)
                "return_date": "2026-05-19",   # 3박 4일 일정
                "currency": "KRW",
                "hl": "ko",
                "gl": "kr",
                "api_key": serpapi_key
            }

            res = requests.get(url, params=params, timeout=30)
            data = res.json()

            # 최저가 추천 항공권 파싱
            flights = data.get("best_flights", []) + data.get("other_flights", [])
            for flight in flights:
                price = flight.get("price")
                # 직항 여부 확인 (경류 레이오버가 없는 경우)
                is_direct = len(flight.get("flights", [])) == 1 and "layovers" not in flight
                
                if price and is_direct:
                    if price <= threshold:
                        deals.append({
                            "destination": name,
                            "price": f"{price:,}원",
                            "discount": f"목표가({threshold:,}원) 이하 특가!",
                            "link": f"https://www.google.com/travel/flights?q=Flights%20to%20{code}"
                        })
                    break  # 해당 도시 최저가 1건 확인 후 종료
        except Exception as e:
            print(f"❌ {name} 데이터 수집 중 에러: {e}")

    return deals

def send_email(deals):
    sender_email = "kijm32@gmail.com"
    receiver_email = "kijm32@gmail.com"
    sender_password = os.environ.get("GMAIL_PASSWORD")

    if not sender_password:
        print("❌ GMAIL_PASSWORD 비밀번호가 없습니다.")
        sys.exit(1)

    msg = MIMEMultipart()
    msg['Subject'] = f"✈️ [SerpApi] 오늘의 구글 플라이트 실시간 특가 리포트 ({len(deals)}건)"
    msg['From'] = sender_email
    msg['To'] = receiver_email

    if not deals:
        html_content = """
        <html>
        <body style='font-family: Malgun Gothic, sans-serif; padding: 20px;'>
            <h3>📢 오늘의 특가 항공권 내역</h3>
            <p>현재 설정한 목표가 이하의 직항 특가 항공권이 없습니다.</p>
        </body>
        </html>
        """
    else:
        html_content = """
        <html>
        <body style='font-family: Malgun Gothic, sans-serif; padding: 20px;'>
            <h2 style='color: #1a73e8;'>📊 오늘의 구글 플라이트 실시간 직항 특가</h2>
            <table border='0' style='border-collapse: collapse; width: 100%; max-width: 650px;'>
                <tr style='background-color: #1a73e8; color: white;'>
                    <th style='padding: 10px;'>목적지</th>
                    <th style='padding: 10px;'>특가 금액</th>
                    <th style='padding: 10px;'>상태</th>
                    <th style='padding: 10px;'>예약</th>
                </tr>
        """
        for deal in deals:
            html_content += f"""
                <tr style='border-bottom: 1px solid #eee;'>
                    <td style='padding: 10px; font-weight: bold;'>{deal['destination']}</td>
                    <td style='padding: 10px; color: #d93025; font-weight: bold;'>{deal['price']}</td>
                    <td style='padding: 10px; color: #188038;'>{deal['discount']}</td>
                    <td style='padding: 10px;'><a href='{deal['link']}' target='_blank'>확인</a></td>
                </tr>
            """
        html_content += "</table></body></html>"

    msg.attach(MIMEText(html_content, 'html'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        print("📬 SerpApi 기반 특가 리포트 발송 성공!")
    except Exception as e:
        print(f"❌ 메일 발송 에러: {e}")

if __name__ == "__main__":
    flight_deals = fetch_flight_deals()
    send_email(flight_deals)
