import os
import smtplib
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from playwright.sync_api import sync_playwright

def fetch_flight_deals(target_url):
    deals = []
    try:
        with sync_playwright() as p:
            print("1. 가상 브라우저를 실행합니다...")
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                viewport={"width": 1280, "height": 1000},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            
            print("2. 구글 플라이트 특가 페이지 주소로 이동 중...")
            page.goto(target_url, timeout=90000, wait_until="networkidle")
            
            print("3. 구글 특가 카드가 화면에 완전히 로드될 때까지 집중 대기합니다...")
            # 구글 플라이트의 특가 격자 영역(Grid) 레이아웃이 나타날 때까지 대기합니다.
            page.wait_for_selector("[role='grid']", timeout=30000)
            page.wait_for_timeout(7000) # 렌더링 안정화를 위해 7초 추가 대기

            print("4. 특가 리스트 카드 추출 시작...")
            # 각 도시별 특가 카드가 배치되는 개별 요소를 타겟팅합니다.
            cards = page.locator("[role='griditem'], .wI3Zbe, .I7099b").all()
            print(f"-> 발견된 카드 후보군 수: {len(cards)}개")

            for card in cards:
                try:
                    text = card.inner_text()
                    if not text or "평소 가격 대비" not in text:
                        continue
                    
                    lines = [line.strip() for line in text.split("\n") if line.strip()]
                    
                    # 텍스트 라인에서 가격 기호(₩ 또는 원)와 '평소 가격 대비' 위치 기반으로 정밀 파싱
                    destination = lines[0]
                    price = "정보 없음"
                    discount = "평소 가격 수준"
                    
                    for line in lines:
                        if "₩" in line or "원" in line:
                            price = line
                        elif "평소 가격 대비" in line:
                            discount = line

                    # 중복된 목적지는 제외하면서 수집
                    if destination and not any(d['destination'] == destination for d in deals):
                        deals.append({
                            "destination": destination,
                            "price": price,
                            "discount": discount,
                            "link": target_url
                        })
                except Exception as e:
                    continue
            
            # 만약 역할 기반 태그 추출에 실패했을 경우를 대비한 2차 백업 파싱 룰
            if not deals:
                print("⚠️ 1차 타겟팅 실패로 인한 2차 백업 파싱을 시도합니다...")
                page_text = page.locator("body").inner_text()
                lines = [l.strip() for l in page_text.split("\n") if l.strip()]
                for i, line in enumerate(lines):
                    if "평소 가격 대비" in line:
                        try:
                            destination = lines[i-2] if i-2 >= 0 else "특가 지역"
                            price = lines[i-1] if i-1 >= 0 else "가격 정보"
                            if "₩" in price or "원" in price or "평소 가격" in destination:
                                if "평소 가격" in destination: 
                                    destination = lines[i-3]
                                    price = lines[i-2]
                                deals.append({
                                    "destination": destination,
                                    "price": price,
                                    "discount": line,
                                    "link": target_url
                                })
                        except:
                            continue

            browser.close()
            print(f"5. 추출 완료! 총 {len(deals)}개의 특가 정보를 정상적으로 가져왔습니다.")
    except Exception as e:
        print(f"❌ 크롤링 중 에러 발생: {e}")
        
    return deals[:15] # 상위 15개 가공

def send_email(deals):
    sender_email = "kijm32@gmail.com"
    receiver_email = "kijm32@gmail.com"
    sender_password = os.environ.get("GMAIL_PASSWORD")

    if not sender_password:
        print("❌ 에러: GMAIL_PASSWORD를 가져오지 못했습니다.")
        sys.exit(1)

    msg = MIMEMultipart('alternative')
    msg['Subject'] = "✈️ 오늘의 구글 플라이트 AI 특가 항공편 리포트"
    msg['From'] = sender_email
    msg['To'] = receiver_email

    if not deals:
        print("⚠️ 파싱된 항공 데이터가 여전히 없어 점검 안내 메일을 보냅니다.")
        html_content = f"""
        <html>
        <body style='font-family: Malgun Gothic, sans-serif; padding: 20px; line-height: 1.6;'>
            <h3 style='color: #d93025;'>📢 구글 플라이트 화면 로딩 지연 안내</h3>
            <p>구글 서버의 일시적인 로딩 지연으로 인해 메일 본문에 표를 그치 못했습니다. 아래의 버튼을 누르시면 AI가 찾아둔 실시간 특가 페이지로 즉시 연결되어 확인하실 수 있습니다.</p>
            <p style='margin-top: 20px;'><a href='{FLIGHT_URL}' target='_blank' style='background-color: #1a73e8; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; font-weight: bold;'>구글 플라이트에서 특가 바로 확인하기</a></p>
        </body>
        </html>
        """
    else:
        html_content = """
        <html>
        <body style='font-family: Malgun Gothic, sans-serif; padding: 20px;'>
            <h2 style='color: #1a73e8; margin-bottom: 5px;'>📊 오늘의 AI 추천 직항 특가 내역 (3박 이상)</h2>
            <p style='color: #666; margin-bottom: 20px;'>구글 플라이트에서 수집한 실시간 항공권 특가 리스트입니다. (PC를 켜지 않아도 매일 업데이트됩니다)</p>
            <table border='0' style='border-collapse: collapse; width: 100%; max-width: 700px; text-align: left; box-shadow: 0 1px 3px rgba(0,0,0,0.1); border-radius: 8px; overflow: hidden;'>
                <tr style='background-color: #1a73e8; color: white;'>
                    <th style='padding: 14px 16px;'>🗺️ 여행 목적지</th>
                    <th style='padding: 14px 16px;'>💵 특가 금액</th>
                    <th style='padding: 14px 16px;'>📉 할인 혜택</th>
                    <th style='padding: 14px 16px; text-align: center;'>예약 링크</th>
                </tr>
        """
        for deal in deals:
            html_content += f"""
                <tr style='border-bottom: 1px solid #eee;'>
                    <td style='padding: 14px 16px; font-weight: bold; color: #333;'>{deal['destination']}</td>
                    <td style='padding: 14px 16px; color: #d93025; font-weight: bold;'>{deal['price']}</td>
                    <td style='padding: 14px 16px; color: #188038; font-size: 14px;'>{deal['discount']}</td>
                    <td style='padding: 14px 16px; text-align: center;'><a href='{deal['link']}' target='_blank' style='background-color: #f1f3f4; color: #1a73e8; padding: 6px 12px; text-decoration: none; border-radius: 4px; font-size: 13px; font-weight: bold;'>확인</a></td>
                </tr>
            """
        html_content += "</table></body></html>"
    
    msg.attach(MIMEText(html_content, 'html'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        print("📬 깔끔한 양식으로 메일 발송 완료!")
    except Exception as e:
        print(f"❌ 메일 발송 중 에러 발생: {e}")

if __name__ == "__main__":
    FLIGHT_URL = "https://www.google.com/travel/flights/deals?tfs=CBwQBhrRAxIKMjAyNi0wNy0yOCgAagwIAxIIL20vMGhzcWZyDAgDEggvbS8wN2Rma3IMCAMSCC9tLzBkcXl3cgwIAxIIL20vMGdxa2RyDQgDEgkvbS8wZ3A1bDZyDQgDEgkvbS8wMzV4eXpyDQgDEgkvbS8wZ3A2XzByDQgDEgkvbS8wZ3A2cm5yDAgDEggvbS8wZnRreHIMCAMSCC9tLzA0Ym54cgwIAxIIL20vMDNoNjRyDAgDEggvbS8wNHRocHIMCAMSCC9tLzBmbjJncg0IAxIJL20vMDFqYjdncg0IAxIJL20vMDFocjU4cg0IAxIJL20vMDI2eXFmcg0IAxIJL20vMDQ0Y2p2cgwIAxIIL20vMGZuZmZyDAgDEggvbS8waG40aHINCAMSCS9tLzAxcF9seXINCAMSCS9tLzAxOTVwZHINCAMSCS9tLzAxeXF3Z3IMCAMSCC9tLzA6dDJ0cgwIAxIIL20vMDk5ZDFyDQgDEgkvbS8wMV9nN2ZyDwgDEgsvZy8xMjFoeGgxanIMCAMSCC9tLzAzNHRscg0IAxIJL20vMDFjZm01cgwIAxIIL20vMGhxa2dyDAgDEggvbS8wZnRwOHINCAMSCS9tLzBnZ2RsehrRAxIKMjAyNi0wOC0wMSgAagwIAxIIL20vMDdkZmtqDAgDEggvbS8wZHF5d2oMCAMSCC9tLzBncWtkag0IAxIJL20vMGdwNWw2ag0IAxIJL20vMDM1eHl6ag0IAxIJL20vMGdwNl8wag0IAxIJL20vMGdwNnJuagwIAxIIL20vMGZ0a3hqDAgDEggvbS8wNGJueGoMCAMSCC9tLzAzaDY0agwIAxIIL20vMDR0aHBqDAgDEggvbS8wZm4yZ2oNCAMSCS9tLzAxaEoxN2dKag0IAxIJL20vMDFocjU4ag0IAxIJL20vMDI2eXFmaA0IAxIJL20vMDQ0Y2p2agwIAxIIL20vMGZuZmZqDAgDEggvbS8waG40aGkNCAMSCS9tLzAxcF9seWoNCAMSCS9tLzAxOTVwZGoNCAMSCS9tLzAxeXF3Z2oMCAMSCC9tLzA2dDJ0agwIAxIIL20vMDQ5ZDFqDQgDEgkvbS8wMV9nN2ZqDwgDEgsvZy8xMjFoeGgxamowDAgDEggvbS8wMzR0bGoNCAMSCS9tLzAxY2ZtNWowDAgDEggvbS8waHFrZ2oMCAMSCC9tLzBmdHA4ag0IAxIJL20vMGdnZGx6cgwIAxIIL20vaHNxZkABSAFwAYIBCwj___________8BmAEB2gEiCiASGAoKMjAyNi0wNy0xNBIKMjAyNy0wNS0yMyoECAMQDQ&q=%EC%98%A4%EB%8A%98%EB%B6%80%ED%84%B0%20%ED%96%A5%ED%9B%84%201%EB%85%84%20%EA%B9%8C%EC%A7%80%20%EB%8C%80%ED%95%9C%EB%AF%BC%EA%B5%AD%EC%97%90%EC%84%9C%20%EC%B6%9C%EB%B0%9C%ED%95%98%EB%8A%94%203%EB%B0%95%20%EC%9D%B4%EC%83%81%EC%9D%98%20%ED%95%AD%EA%B3%B5%ED%8E%B8%20%EC%A7%81%ED%95%AD%2C%20%ED%8A%B9%EA%B0%80%20%EC%95%8C%EC%95%84%EB%B4%90%20%EC%A4%84%EB%9E%98&ved=0CAMQusIPahcKEwjQrZyOhM2VAxUAAAAAHQAAAAAQfQ&uact=3"
    
    flight_data = fetch_flight_deals(FLIGHT_URL)
    send_email(flight_data)
