import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from playwright.sync_api import sync_playwright

def fetch_flight_deals(target_url):
    deals = []
    with sync_playwright() as p:
        # 봇 차단 우회를 위한 User-Agent 설정
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        # 페이지 로딩 및 대기
        page.goto(target_url)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(5000) # 결과가 렌더링될 때까지 5초간 추가 대기

        # 화면에 나타난 텍스트 중 필요한 정보 추출
        # 구글 플라이트 특가 정보 카드의 텍스트 패턴을 분석하여 가져옵니다.
        page_text = page.locator("body").inner_text()
        lines = page_text.split("\n")
        
        # '평소 가격 대비' 단어가 포함된 라인을 찾아 목적지와 가격을 역추적
        for i, line in enumerate(lines):
            if "평소 가격 대비" in line:
                try:
                    # 주변 텍스트 구조를 활용해 목적지 및 가격 파싱
                    destination = lines[i-2] if i-2 >= 0 else "알 수 없는 목적지"
                    price = lines[i-1] if i-1 >= 0 else "가격 정보 없음"
                    discount = line
                    
                    # URL은 메인 주소로 연결하되, 정보를 추가함
                    deals.append({
                        "destination": destination,
                        "price": price,
                        "discount": discount,
                        "link": target_url
                    })
                except:
                    continue
        
        browser.close()
    return deals[:15] # 상위 15개 추출

def send_email(deals):
    # 깃허브 Secrets와 코드에서 메일 설정값 가져오기
    sender_email = "본인의_구글_메일_주소@gmail.com"  # 👈 내 메일 주소로 수정!
    receiver_email = "본인의_구글_메일_주소@gmail.com" # 👈 내 메일 주소로 수정!
    sender_password = os.environ.get("GMAIL_PASSWORD") # 4단계 금고에서 자동으로 가져옴

    if not sender_password:
        print("에러: GMAIL_PASSWORD를 찾을 수 없습니다.")
        return

    msg = MIMEMultipart('alternative')
    msg['Subject'] = "✈️ 오늘의 구글 플라이트 AI 특가 항공편 리포트"
    msg['From'] = sender_email
    msg['To'] = receiver_email

    if not deals:
        html_content = "<html><body><h3>오늘 발견된 새로운 특가 항공편이 없거나 데이터를 불러오지 못했습니다.</h3></body></html>"
    else:
        html_content = """
        <html>
        <body style='font-family: Arial, sans-serif; padding: 20px;'>
            <h2 style='color: #1a73e8;'>📊 오늘의 AI 추천 직항 특가 내역 (3박 이상)</h2>
            <p>구글 플라이트 AI 가 찾아낸 실시간 특가 정보입니다.</p>
            <table border='1' style='border-collapse: collapse; width: 100%; text-align: left; border-color: #ddd;'>
                <tr style='background-color: #f8f9fa;'>
                    <th style='padding: 12px;'>목적지</th>
                    <th style='padding: 12px;'>가격</th>
                    <th style='padding: 12px;'>할인 정보</th>
                    <th style='padding: 12px;'>이동 링크</th>
                </tr>
        """
        for deal in deals:
            html_content += f"""
                <tr>
                    <td style='padding: 12px; font-weight: bold;'>{deal['destination']}</td>
                    <td style='padding: 12px; color: #d93025; font-weight: bold;'>{deal['price']}</td>
                    <td style='padding: 12px; color: #188038;'>{deal['discount']}</td>
                    <td style='padding: 12px;'><a href='{deal['link']}' target='_blank' style='background-color: #1a73e8; color: white; padding: 6px 12px; text-decoration: none; border-radius: 4px; font-size: 13px;'>항공편 확인</a></td>
                </tr>
            """
        html_content += "</table></body></html>"
    
    msg.attach(MIMEText(html_content, 'html'))

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(kijm32@gmail.com, sender_password)
        server.sendmail(kijm32@gmail.com, kijm32@gmail.com, msg.as_string())
    print("메일 발송 완료!")

if __name__ == "__main__":
    # 👈 2단계에서 복사한 주소를 아래 따옴표 안에 붙여넣으세요!
    FLIGHT_URL = "https://www.google.com/travel/flights/deals?tfs=CBwQBhrRAxIKMjAyNi0wNy0yOCgAagwIAxIIL20vMGhzcWZyDAgDEggvbS8wN2Rma3IMCAMSCC9tLzBkcXl3cgwIAxIIL20vMGdxa2RyDQgDEgkvbS8wZ3A1bDZyDQgDEgkvbS8wMzV4eXpyDQgDEgkvbS8wZ3A2XzByDQgDEgkvbS8wZ3A2cm5yDAgDEggvbS8wZnRreHIMCAMSCC9tLzA0Ym54cgwIAxIIL20vMDNoNjRyDAgDEggvbS8wNHRocHIMCAMSCC9tLzBmbjJncg0IAxIJL20vMDFqYjdncg0IAxIJL20vMDFocjU4cg0IAxIJL20vMDI2eXFmcg0IAxIJL20vMDQ0Y2p2cgwIAxIIL20vMGZuZmZyDAgDEggvbS8waG40aHINCAMSCS9tLzAxcF9seXINCAMSCS9tLzAxOTVwZHINCAMSCS9tLzAxeXF3Z3IMCAMSCC9tLzA2dDJ0cgwIAxIIL20vMDQ5ZDFyDQgDEgkvbS8wMV9nN2ZyDwgDEgsvZy8xMjFoeGgxanIMCAMSCC9tLzAzNHRscg0IAxIJL20vMDFjZm01cgwIAxIIL20vMGhxa2dyDAgDEggvbS8wZnRwOHINCAMSCS9tLzBnZ2RsehrRAxIKMjAyNi0wOC0wMSgAagwIAxIIL20vMDdkZmtqDAgDEggvbS8wZHF5d2oMCAMSCC9tLzBncWtkag0IAxIJL20vMGdwNWw2ag0IAxIJL20vMDM1eHl6ag0IAxIJL20vMGdwNl8wag0IAxIJL20vMGdwNnJuagwIAxIIL20vMGZ0a3hqDAgDEggvbS8wNGJueGoMCAMSCC9tLzAzaDY0agwIAxIIL20vMDR0aHBqDAgDEggvbS8wZm4yZ2oNCAMSCS9tLzAxamI3Z2oNCAMSCS9tLzAxaHI1OGoNCAMSCS9tLzAyNnlxZmoNCAMSCS9tLzA0NGNqdmoMCAMSCC9tLzBmbmZmagwIAxIIL20vMGhuNGhqDQgDEgkvbS8wMXBfbHlqDQgDEgkvbS8wMTk1cGRqDQgDEgkvbS8wMXlxd2dqDAgDEggvbS8wNnQydGoMCAMSCC9tLzA0OWQxag0IAxIJL20vMDFfZzdmag8IAxILL2cvMTIxaHhoMWpqDAgDEggvbS8wMzR0bGoNCAMSCS9tLzAxY2ZtNWoMCAMSCC9tLzBocWtnagwIAxIIL20vMGZ0cDhqDQgDEgkvbS8wZ2dkbHpyDAgDEggvbS8waHNxZkABSAFwAYIBCwj___________8BmAEB2gEiCiASGAoKMjAyNi0wNy0xNBIKMjAyNy0wNS0yMyoECAMQDQ&q=%EC%98%A4%EB%8A%98%EB%B6%80%ED%84%B0%20%ED%96%A5%ED%9B%84%201%EB%85%84%20%EA%B9%8C%EC%A7%80%20%EB%8C%80%ED%95%9C%EB%AF%BC%EA%B5%AD%EC%97%90%EC%84%9C%20%EC%B6%9C%EB%B0%9C%ED%95%98%EB%8A%94%203%EB%B0%95%20%EC%9D%B4%EC%83%81%EC%9D%98%20%ED%95%AD%EA%B3%B5%ED%8E%B8%20%EC%A7%81%ED%95%AD%2C%20%ED%8A%B9%EA%B0%80%20%EC%95%8C%EC%95%84%EB%B4%90%20%EC%A4%84%EB%9E%98&ved=0CAMQusIPahcKEwjQrZyOhM2VAxUAAAAAHQAAAAAQfQ&uact=3" 
    
    flight_data = fetch_flight_deals(FLIGHT_URL)
    send_email(flight_data)
