import os
import smtplib
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from playwright.sync_api import sync_playwright

def fetch_flight_deals(target_url):
    deals = []
    screenshot_path = "google_flight_view.png"
    
    try:
        with sync_playwright() as p:
            print("1. 가상 브라우저를 실행합니다 (한국인 패치 완료)...")
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                viewport={"width": 1440, "height": 1200},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                locale="ko-KR",          
                timezone_id="Asia/Seoul" 
            )
            page = context.new_page()
            
            print("2. 특가 URL로 다이렉트 접속합니다...")
            page.goto(target_url, timeout=90000, wait_until="networkidle")
            page.wait_for_timeout(10000) 

            print("3. 안내 팝업창 제거 시도...")
            popups = ["text=Got it", "text=확인", "button:has-text('Got it')", "button:has-text('확인')"]
            for selector in popups:
                try:
                    if page.locator(selector).is_visible():
                        page.locator(selector).click()
                        page.wait_for_timeout(2000)
                        break
                except:
                    continue

            # 🎯 [핵심] 구글 웹페이지 속이기 (텍스트 변경 이벤트 발생)
            print("4. 검색창을 흔들어 깨우고 강제로 어그로를 끕니다!")
            try:
                # 검색창 클릭
                search_input = page.locator('input').first
                search_input.click(timeout=5000)
                
                # 1) 키보드 커서를 텍스트 맨 끝으로 보냄
                page.keyboard.press("End")
                # 2) 로봇이 진짜 사람처럼 한 글자씩 타자를 쳐서 텍스트를 바꿈 (이게 핵심!)
                page.keyboard.type(" 제발 부탁이야", delay=150)
                page.wait_for_timeout(1000)
                
                # 3) 구글이 텍스트 변경을 인지했을 때 엔터키 쾅!
                page.keyboard.press("Enter")
                
                print("-> 검색 강제 실행 완료! 15초간 느긋하게 기다립니다...")
                page.wait_for_timeout(15000)
            except Exception as e:
                print("-> 검색창 타격 실패:", e)

            print("📸 로봇의 시야를 캡처합니다...")
            page.screenshot(path=screenshot_path, full_page=False)

            print("5. 특가 정보 파싱 시작...")
            page_text = page.locator("body").inner_text()
            lines = [l.strip() for l in page_text.split("\n") if l.strip()]
            
            for i, line in enumerate(lines):
                if "평소 가격 대비" in line:
                    try:
                        destination = lines[i-2] if i-2 >= 0 else "특가 지역"
                        price = lines[i-1] if i-1 >= 0 else "가격 정보"
                        
                        if "원" in price or "₩" in price:
                            if destination and not any(d['destination'] == destination for d in deals):
                                deals.append({
                                    "destination": destination,
                                    "price": price,
                                    "discount": line,
                                    "link": target_url
                                })
                    except:
                        continue

            browser.close()
            print(f"6. 크롤링 완료! 총 {len(deals)}개의 진짜 특가 정보를 추출했습니다.")
    except Exception as e:
        print(f"❌ 크롤링 중 에러 발생: {e}")
        
    return deals[:15], screenshot_path

def send_email(deals, screenshot_path, target_url):
    sender_email = "kijm32@gmail.com"
    receiver_email = "kijm32@gmail.com"
    sender_password = os.environ.get("GMAIL_PASSWORD")

    if not sender_password:
        print("❌ 에러: GMAIL_PASSWORD가 없습니다.")
        sys.exit(1)

    msg = MIMEMultipart('related')
    msg['Subject'] = "✈️ 오늘의 구글 플라이트 AI 특가 항공편 리포트"
    msg['From'] = sender_email
    msg['To'] = receiver_email

    if not deals:
        html_content = f"""
        <html>
        <body style='font-family: Malgun Gothic, sans-serif; padding: 20px; line-height: 1.6;'>
            <h3 style='color: #d93025;'>📢 구글 플라이트 특가 내역 없음</h3>
            <p>검색 로직을 사람과 동일하게 변경하여 검색을 시도했습니다. 아래 사진을 통해 검색이 정상적으로 넘어갔는지 확인해 주세요.</p>
            <p><a href='{target_url}' target='_blank' style='background-color: #1a73e8; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;'>현재 페이지 직접 확인하기</a></p>
            <br>
            <h4>⬇️ 로봇이 바라본 현재 화면</h4>
            <img src="cid:robot_view" style="max-width:100%; border:1px solid #ccc;"/>
        </body>
        </html>
        """
    else:
        html_content = f"""
        <html>
        <body style='font-family: Malgun Gothic, sans-serif; padding: 20px;'>
            <h2 style='color: #1a73e8; margin-bottom: 5px;'>📊 오늘의 AI 추천 직항 특가 내역</h2>
            <p style='color: #666; margin-bottom: 20px;'>요청하신 조건에 맞게 수집된 완벽한 결과입니다.</p>
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
                    <td style='padding: 14px 16px; text-align: center;'><a href='{target_url}' target='_blank' style='background-color: #f1f3f4; color: #1a73e8; padding: 6px 12px; text-decoration: none; border-radius: 4px; font-size: 13px; font-weight: bold;'>전체 확인</a></td>
                </tr>
            """
        html_content += """
            </table>
            <br><br>
            <h4>⬇️ 로봇 시야 스크린샷 (검색 성공 인증)</h4>
            <img src="cid:robot_view" style="max-width:100%; border:1px solid #ccc;"/>
        </body>
        </html>
        """
    
    msg_html = MIMEText(html_content, 'html')
    msg.attach(msg_html)

    if os.path.exists(screenshot_path):
        with open(screenshot_path, 'rb') as fp:
            msg_img = MIMEImage(fp.read())
            msg_img.add_header('Content-ID', '<robot_view>')
            msg_img.add_header('Content-Disposition', 'inline', filename=screenshot_path)
            msg.attach(msg_img)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        print("📬 최종 완성 버전 메일 발송 성공!")
    except Exception as e:
        print(f"❌ 메일 발송 중 에러 발생: {e}")

if __name__ == "__main__":
    # 처음 주셨던 완벽한 검색 조건이 담긴 오리지널 URL
    FLIGHT_URL = "https://www.google.com/travel/flights/deals?tfs=CBwQBhrRAxIKMjAyNi0wNy0yOCgAagwIAxIIL20vMGhzcWZyDAgDEggvbS8wN2Rma3IMCAMSCC9tLzBkcXl3cgwIAxIIL20vMGdxa2RyDQgDEgkvbS8wZ3A1bDZyDQgDEgkvbS8wMzV4eXpyDQgDEgkvbS8wZ3A2XzByDQgDEgkvbS8wZ3A2cm5yDAgDEggvbS8wZnRreHIMCAMSCC9tLzA0Ym54cgwIAxIIL20vMDNoNjRyDAgDEggvbS8wNHRocHIMCAMSCC9tLzBmbjJncg0IAxIJL20vMDFqYjdncg0IAxIJL20vMDFocjU4cg0IAxIJL20vMDI2eXFmcg0IAxIJL20vMDQ0Y2p2cgwIAxIIL20vMGZuZmZyDAgDEggvbS8waG40aHINCAMSCS9tLzAxcF9seXINCAMSCS9tLzAxOTVwZHINCAMSCS9tLzAxeXF3Z3IMCAMSCC9tLzA2dDJ0cgwIAxIIL20vMDQ5ZDFyDQgDEgkvbS8wMV9nN2ZyDwgDEgsvZy8xMjFoeGgxanIMCAMSCC9tLzAzNHRscg0IAxIJL20vMDFjZm01cgwIAxIIL20vMGhxa2dyDAgDEggvbS8wZnRwOHINCAMSCS9tLzBnZ2RsehrRAxIKMjAyNi0wOC0wMSgAagwIAxIIL20vMDdkZmtqDAgDEggvbS8wZHF5d2oMCAMSCC9tLzBncWtkag0IAxIJL20vMGdwNWw2ag0IAxIJL20vMDM1eHl6ag0IAxIJL20vMGdwNl8wag0IAxIJL20vMGdwNnJuagwIAxIIL20vMGZ0a3hqDAgDEggvbS8wNGJueGoMCAMSCC9tLzAzaDY0agwIAxIIL20vMDR0aHBqDAgDEggvbS8wZm4yZ2oNCAMSCS9tLzAxaEoxN2dKag0IAxIJL20vMDFocjU4ag0IAxIJL20vMDI2eXFmaA0IAxIJL20vMDQ0Y2p2agwIAxIIL20vMGZuZmZqDAgDEggvbS8waG40aGkNCAMSCS9tLzAxcF9seWoNCAMSCS9tLzAxOTVwZGoNCAMSCS9tLzAxeXF3Z2oMCAMSCC9tLzA2dDJ0agwIAxIIL20vMDQ5ZDFqDQgDEgkvbS8wMV9nN2ZqDwgDEgsvZy8xMjFoeGgxanowDAgDEggvbS8wMzR0bGoNCAMSCS9tLzAxY2ZtNWowDAgDEggvbS8waHFrZ2oMCAMSCC9tLzBmdHA4ag0IAxIJL20vMGdnZGx6cgwIAxIIL20vaHNxZkABSAFwAYIBCwj___________8BmAEB2gEiCiASGAoKMjAyNi0wNy0xNBIKMjAyNy0wNS0yMyoECAMQDQ&q=%EC%98%A4%EB%8A%98%EB%B6%80%ED%84%B0%20%ED%96%A5%ED%9B%84%201%EB%85%84%20%EA%B9%8C%EC%A7%80%20%EB%8C%80%ED%95%9C%EB%AF%BC%EA%B5%AD%EC%97%90%EC%84%9C%20%EC%B6%9C%EB%B0%9C%ED%95%98%EB%8A%94%203%EB%B0%95%20%EC%9D%B4%EC%83%81%EC%9D%98%20%ED%95%AD%EA%B3%B5%ED%8E%B8%20%EC%A7%81%ED%95%AD%2C%20%ED%8A%B9%EA%B0%80%20%EC%95%8C%EC%95%84%EB%B4%90%20%EC%A4%84%EB%9E%98&ved=0CAMQusIPahcKEwjQrZyOhM2VAxUAAAAAHQAAAAAQfQ&uact=3"
    
    flight_data, img_path = fetch_flight_deals(FLIGHT_URL)
    send_email(flight_data, img_path, FLIGHT_URL)
