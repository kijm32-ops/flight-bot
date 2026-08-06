import smtplib
import logging
import sys
from typing import List, Dict
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config import GMAIL_USER, GMAIL_PASSWORD

def send_email(deals: List[Dict[str, str]]) -> None:
    if not GMAIL_USER or not GMAIL_PASSWORD:
        logging.error("❌ 메일 계정 환경변수가 없습니다.")
        sys.exit(1)

    msg = MIMEMultipart()
    msg['Subject'] = f"✈️ [PTIS] 오늘의 실시간 특가 리포트 ({len(deals)}건)"
    msg['From'] = GMAIL_USER
    msg['To'] = GMAIL_USER

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
            server.login(GMAIL_USER, GMAIL_PASSWORD)
            server.sendmail(GMAIL_USER, GMAIL_USER, msg.as_string())
        logging.info("📬 PTIS 리포트 메일 발송 성공!")
    except Exception as e:
        logging.error(f"❌ 메일 발송 에러: {e}")
