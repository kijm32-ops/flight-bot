import os
import smtplib
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from playwright.sync_api import sync_playwright

def fetch_flight_deals():
    deals = []
    screenshot_path = "google_flight_view.png"
    
    # 1. 쿼리가 없는 아주 깨끗한 기본 특가 URL (한국어/원화 강제 세팅)
    base_url = "https://www.google.com/travel/flights/deals?hl=ko&gl=KR&curr=KRW"
    
    try:
        with sync_playwright() as p:
            print("1. 가상 브라우저를 실행합니다...")
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                viewport={"width": 1440, "height": 1200},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            
            print("2. 구글 플라이트 기본 페이지로 이동 중...")
            page.goto(base_url, timeout=60000, wait_until="networkidle")
            page.wait_for_timeout(5000) 

            # 3. AI 팝업창이 있다면 제거
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

            # 4. 사람처럼 검색창에 직접 자연어 입력!
            print("4. 로봇이 직접 AI 검색어 타이핑을 시작합니다...")
            search_query = "오늘부터 향후 1년까지 대한민국에서 출발하는 3박 이상의 항공편 직항 특가 알아봐 줄래"
            
            try:
                # 화면의 첫 번째 입력창(AI 검색창)을 클릭하고 사람의 속도로 타이핑합니다.
                page.locator('input').first.click(timeout=5000)
                page.keyboard.type(search_query, delay=100)
                page.keyboard.press("Enter")
            except Exception as e:
                print("검색창을 찾지 못했습니다. 스크린샷을 확인하세요.", e)

            # 5. 검색 결과가 완전히 나올 때까지 15초간 느긋하게 대기
            print("5. 검색 버튼을 눌렀습니다! 결과 로딩을 15초간 대기합니다...")
            page.wait_for_timeout(15000)

            # 검색이 완료된 후의 최종 URL을 가져옵니다.
            final_url = page.url

            print("📸 로봇의 시야를 캡처합니다...")
            page.screenshot(path=screenshot_path, full_page=False)

            print("6. 엄격한 특가 정보 파싱 시작...")
            page_text = page.locator("body").inner_text()
            lines = [l.strip() for l in page_text.split("\n") if l.strip()]
            
            for i, line in enumerate(lines):
                # '보다 저렴' 같은 모호한 단어를 빼고 오직 '평소 가격 대비'만 엄격하게 추적합니다.
                if "평소 가격 대비" in line:
                    try:
                        destination = lines[i-2] if i-2 >= 0 else "특가 지역"
                        price = lines[i-1] if i-1 >= 0 else "가격 정보"
                        
                        # 엉뚱한 텍스트를 막기 위해 가격란에 '원'이나 '₩' 기호가 있는지 2차 검증
                        if "원" in price or "₩" in price:
                            if destination and not any(d['destination'] == destination for d in deals):
                                deals.append({
                                    "destination": destination,
                                    "price": price,
                                    "discount": line,
                                    "link": final_url # 검색이 완료된 URL로 연결
                                })
                    except:
                        continue

            browser.close()
            print(f"7. 크롤링 완료! 총 {len(deals)}개의 진짜 특가 정보를 추출했습니다.")
    except Exception as e:
        print(f"❌ 크롤링 중 에러 발생: {e}")
        
    return deals[:15], screenshot_path, final_url if 'final_url' in locals() else base_url

def send_email(deals, screenshot_path, final_url):
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
            <p>로봇이 타이핑까지 완료했으나 조건에 맞는 특가 표를 찾지 못했습니다. 아래 사진을 확인해 주세요.</p>
            <p><a href='{final_url}' target='_blank' style='background-color: #1a73e8; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;'>현재 페이지 확인하기</a></p>
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
            <p style='color: #666; margin-bottom: 20px;'>로봇이 직접 검색창에 조건을 입력하여 찾아낸 진짜 결과입니다.</p>
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
        html_content += """
            </table>
            <br><br>
            <h4>⬇️ 로봇 시야 스크린샷 (제대로 검색했는지 인증용)</h4>
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
        print("📬 직접 타이핑 버전 메일 발송 성공!")
    except Exception as e:
        print(f"❌ 메일 발송 중 에러 발생: {e}")

if __name__ == "__main__":
    flight_data, img_path, final_url = fetch_flight_deals()
    send_email(flight_data, img_path, final_url)
