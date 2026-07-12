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
            print("1. 브라우저를 실행합니다...")
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            
            print("2. 구글 플라이트 특가 페이지 주소로 이동 중...")
            page.goto(target_url, timeout=60000) # 타임아웃 60초 설정
            
            print("3. 데이터가 안정적으로 로드될 때까지 10초간 대기합니다...")
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(10000) 

            print("4. 화면의 특가 정보 분석 중...")
            page_text = page.locator("body").inner_text()
            lines = page_text.split("\n")
            
            for i, line in enumerate(lines):
                if "평소 가격 대비" in line:
                    try:
                        destination = lines[i-2] if i-2 >= 0 else "특가 목적지"
                        price = lines[i-1] if i-1 >= 0 else "가격 정보"
                        discount = line
                        
                        deals.append({
                            "destination": destination,
                            "price": price,
                            "discount": discount,
                            "link": target_url
                        })
                    except:
                        continue
            
            browser.close()
            print(f"5. 크롤링 완료! 총 {len(deals)}개의 특가 정보를 추출했습니다.")
    except Exception as e:
        print(f"❌ 크롤링 중 치명적 에러 발생: {e}")
        sys.exit(1)
        
    return deals[:15]

def send_email(deals):
    sender_email = "kijm32@gmail.com"
    receiver_email = "kijm32@gmail.com"
    sender_password = os.environ.get("GMAIL_PASSWORD")

    if not sender_password:
        print("❌ 에러: GMAIL_PASSWORD 비밀 금고에서 비밀번호를 가져오지 못했습니다. GitHub Secrets 설정을 확인해 주세요.")
        sys.exit(1)

    msg = MIMEMultipart('alternative')
    msg['Subject'] = "✈️ 오늘의 구글 플라이트 AI 특가 항공편 리포트"
    msg['From'] = sender_email
    msg['To'] = receiver_email

    if not deals:
        print("⚠️ 오늘 발견된 특가 항공편이 없어 안내 메일을 발송합니다.")
        html_content = """
        <html>
        <body style='font-family: Arial, sans-serif; padding: 20px;'>
            <h3 style='color: #d93025;'>오늘 구글 플라이트 AI 검색 결과에서 파싱된 특가 정보가 없습니다.</h3>
            <p>실시간 조건에 따라 일시적으로 특가 항공편이 없을 수 있습니다. 아래 링크에서 직접 확인해 보실 수 있습니다.</p>
            <p><a href='{0}' target='_blank' style='background-color: #1a73e8; color: white; padding: 8px 16px; text-decoration: none; border-radius: 4px;'>구글 플라이트에서 직접 보기</a></p>
        </body>
        </html>
        """.format(FLIGHT_URL)
    else:
        html_content = """
        <html>
        <body style='font-family: Arial, sans-serif; padding: 20px;'>
            <h2 style='color: #1a73e8;'>📊 오늘의 AI 추천 직항 특가 내역 (3박 이상)</h2>
            <p>구글 플라이트 AI가 실시간으로 찾아낸 대한민국 출발 특가 정보입니다. 각 항공편의 '확인' 버튼을 누르면 상세 페이지로 이동합니다.</p>
            <table border='1' style='border-collapse: collapse; width: 100%; text-align: left; border-color: #ddd;'>
                <tr style='background-color: #f8f9fa;'>
                    <th style='padding: 12px; border: 1px solid #ddd;'>목적지</th>
                    <th style='padding: 12px; border: 1px solid #ddd;'>가격</th>
                    <th style='padding: 12px; border: 1px solid #ddd;'>할인 정보</th>
                    <th style='padding: 12px; border: 1px solid #ddd;'>이동 링크</th>
                </tr>
        """
        for deal in deals:
            html_content += f"""
                <tr>
                    <td style='padding: 12px; border: 1px solid #ddd; font-weight: bold;'>{deal['destination']}</td>
                    <td style='padding: 12px; border: 1px solid #ddd; color: #d93025; font-weight: bold;'>{deal['price']}</td>
                    <td style='padding: 12px; border: 1px solid #ddd; color: #188038;'>{deal['discount']}</td>
                    <td style='padding: 12px; border: 1px solid #ddd;'><a href='{deal['link']}' target='_blank' style='background-color: #1a73e8; color: white; padding: 6px 12px; text-decoration: none; border-radius: 4px; font-size: 13px;'>항공편 확인</a></td>
                </tr>
            """
        html_content += "</table></body></html>"
    
    msg.attach(MIMEText(html_content, 'html'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        print("📬 메일 발송 성공!")
    except Exception as e:
        print(f"❌ 메일 발송 중 에러 발생: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # 요청하신 구글 플라이트 고정 검색 URL 주소 반영
    FLIGHT_URL = "https://www.google.com/travel/flights/deals?tfs=CBwQBhrRAxIKMjAyNi0wNy0yOCgAagwIAxIIL20vMGhzcWZyDAgDEggvbS8wN2Rma3IMCAMSCC9tLzBkcXl3cgwIAxIIL20vMGdxa2RyDQgDEgkvbS8wZ3A1bDZyDQgDEgkvbS8wMzV4eXpyDQgDEgkvbS8wZ3A2XzByDQgDEgkvbS8wZ3A2cm5yDAgDEggvbS8wZnRreHIMCAMSCC9tLzA0Ym54cgwIAxIIL20vMDNoNjRyDAgDEggvbS8wNHRocHIMCAMSCC9tLzBmbjJncg0IAxIJL20vMDFqYjdncg0IAxIJL20vMDFocjU4cg0IAxIJL20vMDI2eXFmcg0IAxIJL20vMDQ0Y2p2cgwIAxIIL20vMGZuZmZyDAgDEggvbS8waG40aHINCAMSCS9tLzAxcF9seXINCAMSCS9tLzAxOTVwZHINCAMSCS9tLzAxeXF3Z3IMCAMSCC9tLzA2dDJ0cgwIAxIIL20vMD45ZDFyDQgDEgkvbS8wMV9nN2ZyDwgDEgsvZy8xMjFoeGgxanIMCAMSCC9tLzAzNHRscg0IAxIJL20vMDFjZm01cgwIAxIIL20vMGhxa2dyDAgDEggvbS8wZnRwOHINCAMSCS9tLzBnZ2RsehrRAxIKMjAyNi0wOC0wMSgAagwIAxIIL20vMDdkZmtqDAgDEggvbS8wZHF5d2oMCAMSCC9tLzBncWtkag0IAxIJL20vMGdwNWw2ag0IAxIJL20vMDM1eHl6ag0IAxIJL20vMGdwNl8wag0IAxIJL20vMGdwNnJuagwIAxIIL20vMGZ0a3hqDAgDEggvbS8wNGJueGoMCAMSCC9tLzAzaDY0agwIAxIIL20vMDR0aHBqDAgDEggvbS8wZm4yZ2oNCAMSCS9tLzAxaEoxN2dKag0IAxIJL20vMDFocjU4ag0IAxIJL20vMDI2eXFmaA0IAxIJL20vMDQ0Y2p2agwIAxIIL20vMGZuZmZqDAgDEggvbS8waG40aGkNCAMSCS9tLzAxcF9seWoNCAMSCS9tLzAxOTVwZGoNCAMSCS9tLzAxeXF3Z2oMCAMSCC9tLzA2dDJ0agwIAxIIL20vMDQ5ZDFqDQgDEgkvbS8wMV9nN2ZqDwgDEgsvZy8xMjFoeGgxamowDAgDEggvbS8wMzR0bGoNCAMSCS9tLzAxY2ZtNWowDAgDEggvbS8waHFrZ2oMCAMSCC9tLzBmdHA4ag0IAxIJL20vMGdnZGx6cgwIAxIIL20vaHNxZkABSAFwAYIBCwj___________8BmAEB2gEiCiASGAoKMjAyNi0wNy0xNBIKMjAyNy0wNS0yMyoECAMQDQ&q=%EC%98%A4%EB%8A%98%EB%B6%80%ED%84%B0%20%ED%96%A5%ED%9B%84%201%EB%85%84%20%EA%B9%8C%EC%A7%80%20%EB%8C%80%ED%95%9C%EB%AF%BC%EA%B5%AD%EC%97%90%EC%84%9C%20%EC%B6%9C%EB%B0%9C%ED%95%98%EB%8A%94%203%EB%B0%95%20%EC%9D%B4%EC%83%81%EC%9D%98%20%ED%95%AD%EA%B3%B5%ED%8E%B8%20%EC%A7%81%ED%95%AD%2C%20%ED%8A%B9%EA%B0%80%20%EC%95%8C%EC%95%84%EB%B4%90%20%EC%A4%84%EB%9E%98&ved=0CAMQusIPahcKEwjQrZyOhM2VAxUAAAAAHQAAAAAQfQ&uact=3"
    
    flight_data = fetch_flight_deals(FLIGHT_URL)
    send_email(flight_data)
