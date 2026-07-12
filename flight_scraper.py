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
            
            print("2. 구글 플라이트로 이동 중...")
            page.goto(base_url, timeout=60000, wait_until="networkidle")
            
            # 🛑 [핵심 수정] 팝업창이 스멀스멀 나타날 때까지 최대 10초까지 진득하게 기다립니다.
            print("3. 눈치 없는 AI 팝업창이 뜰 때까지 잠복 대기 중...")
            page.wait_for_timeout(8000) 

            # 파란색 '확인' 버튼을 찾아 무조건 격파합니다.
            print("4. 팝업창 폭파 작전 시작...")
            popups = ["text='확인'", "button:has-text('확인')", "text='Got it'"]
            for selector in popups:
                try:
                    if page.locator(selector).is_visible():
                        print(f"-> 팝업 발견! [{selector}] 버튼을 눌러 부숩니다.")
                        page.locator(selector).click(force=True) # force=True로 강제 클릭
                        page.wait_for_timeout(2000)
                        break
                except Exception as e:
                    pass

            print("5. AI 검색창을 찾아 정밀 타격합니다...")
            try:
                # 가짜 껍데기 버튼을 찾아 누릅니다.
                fake_box = page.locator("text='언제, 어디로, 어떻게 여행하고 싶으신가요?'").first
                if fake_box.is_visible():
                    fake_box.click(force=True)
                    page.wait_for_timeout(1000)
                else:
                    page.locator("input").first.click(force=True)

                # 한 땀 한 땀 타자를 칩니다.
                search_query = "인천에서 출발하는 3박 이상 직항 특가 1년치 알아봐 줘"
                print(f"-> 검색어 입력 중: {search_query}")
                page.keyboard.type(search_query, delay=150)
                page.wait_for_timeout(1000)
                
                # 확실하게 엔터키를 때려 넣습니다.
                print("-> 쾅! 엔터키를 눌렀습니다. 15초 대기합니다.")
                page.keyboard.press("Enter")
                page.wait_for_timeout(500)
                page.keyboard.press("Enter")
                page.wait_for_timeout(15000)
            except Exception as e:
                print("-> 검색창 타격 실패:", e)

            final_url = page.url

            print("6. 화면 캡처 중...")
            page.screenshot(path=screenshot_path, full_page=False)
            page.wait_for_timeout(3000) 

            print("7. 텍스트 파싱 시작...")
            page_text = page.locator("body").inner_text()
            lines = [l.strip() for l in page_text.split("\n") if l.strip()]
            
            for i, line in enumerate(lines):
                if ("원" in line or "₩" in line) and any(char.isdigit() for char in line):
                    try:
                        price = line
                        destination = lines[i-3] if i-3 >= 0 and len(lines[i-3]) < 15 else lines[i-2]
                        
                        if "로그인" in destination or "변경" in destination or "알아보기" in destination:
                            continue
                            
                        discount = "할인 정보 없음"
                        if i+1 < len(lines) and ("대비" in lines[i+1] or "저렴" in lines[i+1]):
                            discount = lines[i+1]
                        elif i-1 >= 0 and ("대비" in lines[i-1] or "저렴" in lines[i-1]):
                            discount = lines[i-1]

                        if destination and not any(d['destination'] == destination for d in deals):
                            deals.append({
                                "destination": destination,
                                "price": price,
                                "discount": discount,
                                "link": final_url
                            })
                    except:
                        continue

            browser.close()
            print(f"8. 크롤링 완료! 총 {len(deals)}개의 특가 수집.")
    except Exception as e:
        print(f"❌ 크롤링 에러: {e}")
        
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
            <p>팝업창을 부수고 진입했으나 조건에 맞는 특가가 안 떴습니다. 봇이 임무를 완수했는지 사진을 확인해 주세요!</p>
            <p><a href='{final_url}' target='_blank' style='background-color: #1a73e8; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;'>현재 결과 페이지 열기</a></p>
            <br>
            <h4>⬇ 로봇이 찍어온 현장 사진</h4>
            <img src="cid:robot_view" style="max-width:100%; border:1px solid #ccc;"/>
        </body>
        </html>
        """
    else:
        html_content = f"""
        <html>
        <body style='font-family: Malgun Gothic, sans-serif; padding: 20px;'>
            <h2 style='color: #1a73e8; margin-bottom: 5px;'>📊 오늘의 AI 추천 직항 특가 내역</h2>
            <p style='color: #666; margin-bottom: 20px;'>방해물을 모두 뚫고 로봇이 캐온 실시간 1년치 직항 특가 리스트입니다.</p>
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

    if os.path.exists(screenshot_path) and os.path.getsize(screenshot_path) > 0:
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
    flight_data, img_path, final_url = fetch_flight_deals()
    send_email(flight_data, img_path, final_url)
