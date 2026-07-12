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
            page.wait_for_timeout(5000) 

            # 안내 팝업 닫기
            for selector in ["text=Got it", "text=확인", "button:has-text('Got it')"]:
                try:
                    if page.locator(selector).is_visible():
                        page.locator(selector).click()
                        page.wait_for_timeout(1000)
                        break
                except:
                    continue

            # 🎯 [핵심] 꽁꽁 숨겨진 AI 검색창 정확히 조준해서 열기
            print("3. AI 검색창을 찾아 클릭합니다...")
            try:
                # 1단계: "언제, 어디로..." 라고 적힌 가짜 버튼을 눌러서 진짜 입력창을 엽니다.
                fake_box = page.locator("text='언제, 어디로, 어떻게 여행하고 싶으신가요?'").first
                if fake_box.is_visible():
                    fake_box.click()
                    page.wait_for_timeout(1000)
                else:
                    page.locator("input").first.click()

                # 2단계: 키보드로 꾹꾹 눌러쓰기
                search_query = "인천에서 출발하는 3박 이상 직항 특가 1년치 알아봐 줘"
                page.keyboard.type(search_query, delay=150)
                page.wait_for_timeout(1000)
                
                # 3단계: 엔터키 2번 연속 타격 (확인 사살)
                page.keyboard.press("Enter")
                page.wait_for_timeout(500)
                page.keyboard.press("Enter")
                
                print("-> 검색 명령 하달 완료! 데이터가 뜰 때까지 15초 대기합니다...")
                page.wait_for_timeout(15000)
            except Exception as e:
                print("-> 검색창 타격 실패:", e)

            final_url = page.url

            # 📸 사진이 완전히 저장될 때까지 기다려줍니다.
            print("4. 화면 캡처 중...")
            page.screenshot(path=screenshot_path, full_page=False)
            page.wait_for_timeout(3000) # 사진 파일이 구워질 시간 3초 부여!

            print("5. 텍스트 파싱 (유연한 룰 적용) 시작...")
            page_text = page.locator("body").inner_text()
            lines = [l.strip() for l in page_text.split("\n") if l.strip()]
            
            for i, line in enumerate(lines):
                # '평소 가격 대비'라는 멘트가 없어도 '₩'나 '원'이 포함된 가격 데이터면 무조건 수집!
                if ("원" in line or "₩" in line) and any(char.isdigit() for char in line):
                    try:
                        price = line
                        # 가격 바로 위나 위위 줄에 도시 이름이 위치함
                        destination = lines[i-3] if i-3 >= 0 and len(lines[i-3]) < 15 else lines[i-2]
                        
                        # 이상한 버튼 텍스트 걸러내기
                        if "로그인" in destination or "변경" in destination or "알아보기" in destination:
                            continue
                            
                        # 할인 정보 찾기
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
            print(f"6. 크롤링 완료! 총 {len(deals)}개의 특가 수집.")
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
            <h3 style='color: #d93025;'>📢 구글 플라이트 특가 내역 수집 재시도</h3>
            <p>특가 텍스트를 찾지 못했습니다. 이번엔 스크린샷이 깨지지 않았을 테니 봇이 뭘 보고 있었는지 확인해 보세요!</p>
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
            <p style='color: #666; margin-bottom: 20px;'>인천 출발 조건으로 로봇이 열심히 타자 쳐서 가져온 결과입니다.</p>
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
