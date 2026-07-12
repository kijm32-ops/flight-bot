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
    # 깨끗한 기본 특가 페이지로 접속
    base_url = "https://www.google.com/travel/flights/deals?hl=ko&gl=KR&curr=KRW"
    
    try:
        with sync_playwright() as p:
            print("1. 가상 브라우저를 실행합니다...")
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                viewport={"width": 1440, "height": 1200},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                locale="ko-KR",          
                timezone_id="Asia/Seoul" 
            )
            page = context.new_page()
            
            print("2. 구글 플라이트 페이지로 이동 중...")
            page.goto(base_url, timeout=60000, wait_until="networkidle")
            page.wait_for_timeout(6000) 

            # 3. 안내 팝업창 제거
            popups = ["text=Got it", "text=확인", "button:has-text('Got it')", "button:has-text('확인')"]
            for selector in popups:
                try:
                    if page.locator(selector).is_visible():
                        page.locator(selector).click()
                        page.wait_for_timeout(2000)
                        break
                except:
                    continue

            # 4. 출발지 꼬임을 막기 위해 '인천 출발'을 명확히 적어 타이핑합니다.
            print("4. 검색창에 정밀 조건을 입력합니다...")
            search_input = page.locator('input').first
            search_input.click(timeout=5000)
            
            # 기존 텍스트를 싹 지우고 새로 입력
            search_input.fill("")
            search_query = "오늘부터 향후 1년까지 인천에서 출발하는 3박 이상의 항공편 직항 특가 알아봐 줘"
            search_input.type(search_query, delay=100)
            page.wait_for_timeout(2000)

            # 5. 🎯 [정밀 타격] 파란색 돋보기 버튼을 직접 클릭합니다!
            print("5. 파란색 돋보기 검색 버튼을 직접 클릭합니다!")
            try:
                # 파란색 검색 버튼의 요소(aria-label="검색" 또는 부모 button)를 찾아 클릭
                search_button = page.locator("button[aria-label*='검색'], button:has(svg)").first
                if search_button.is_visible():
                    search_button.click()
                else:
                    # 마땅한 태그가 안 잡힐 경우 엔터키로 백업
                    page.keyboard.press("Enter")
                
                print("-> 검색 반영 대기 (15초)...")
                page.wait_for_timeout(15000)
            except Exception as e:
                print("-> 버튼 클릭 실패, 엔터키로 대체합니다:", e)
                page.keyboard.press("Enter")
                page.wait_for_timeout(15000)

            # 최종 검색 결과 URL 확보
            final_url = page.url

            print("📸 로봇의 시야를 캡처합니다...")
            page.screenshot(path=screenshot_path, full_page=False)

            print("6. 특가 정보 파싱 시작...")
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
                                    "link": final_url
                                })
                    except:
                        continue

            browser.close()
            print(f"7. 크롤링 완료! 총 {len(deals)}개의 특가 정보를 추출했습니다.")
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
            <h3 style='color: #d93025;'>📢 구글 플라이트 특가 내역 수집 재시도</h3>
            <p>파란색 돋보기 버튼을 클릭해 검색을 시도했습니다. 아래 스크린샷에서 검색 결과 격자가 정상적으로 떴는지 확인해 주세요.</p>
            <p><a href='{final_url}' target='_blank' style='background-color: #1a73e8; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;'>현재 결과 페이지 열기</a></p>
            <br>
            <h4>⬇ Preserved View</h4>
            <img src="cid:robot_view" style="max-width:100%; border:1px solid #ccc;"/>
        </body>
        </html>
        """
    else:
        html_content = f"""
        <html>
        <body style='font-family: Malgun Gothic, sans-serif; padding: 20px;'>
            <h2 style='color: #1a73e8; margin-bottom: 5px;'>📊 오늘의 AI 추천 직항 특가 내역</h2>
            <p style='color: #666; margin-bottom: 20px;'>돋보기 버튼을 직접 돌파하여 찾아낸 실시간 특가 리스트입니다.</p>
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
                    <td style='padding: 14px 16px; text-align: center;'><a href='{final_url}' target='_blank' style='background-color: #f1f3f4; color: #1a73e8; padding: 6px 12px; text-decoration: none; border-radius: 4px; font-size: 13px; font-weight: bold;'>전체 확인</a></td>
                </tr>
            """
        html_content += """
            </table>
            <br><br>
            <h4>⬇ 로봇 시야 스크린샷</h4>
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
        print("📬 물리적 클릭 버전 메일 발송 성공!")
    except Exception as e:
        print(f"❌ 메일 발송 중 에러 발생: {e}")

if __name__ == "__main__":
    flight_data, img_path, final_url = fetch_flight_deals()
    send_email(flight_data, img_path, final_url)
