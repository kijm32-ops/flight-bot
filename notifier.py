import smtplib
import logging
import os
import json
import requests
from typing import List
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config import GMAIL_USER, GMAIL_PASSWORD, PAGE_URL
from models import Flight


def send_email(deals: List[Flight]) -> None:
    if not GMAIL_USER or not GMAIL_PASSWORD:
        logging.error("❌ 메일 계정 환경변수가 없습니다.")
        return

    msg = MIMEMultipart()
    msg['Subject'] = f"✈️ [PTIS] 오늘의 실시간 특가 리포트 ({len(deals)}건)"
    msg['From'] = GMAIL_USER
    msg['To'] = GMAIL_USER

    if not deals:
        html_content = "<h3>📢 오늘의 특가 항공권 내역</h3><p>현재 조건에 부합하는 특가 항공권이 없습니다.</p>"
    else:
        html_content = """
        <html><body style='font-family: Malgun Gothic, sans-serif; padding: 20px;'>
            <h2 style='color: #1a73e8;'>📊 오늘의 실시간 직항 특가</h2>
            <table border='0' style='border-collapse: collapse; width: 100%; max-width: 750px;'>
                <tr style='background-color: #1a73e8; color: white;'>
                    <th style='padding: 10px;'>노선</th>
                    <th style='padding: 10px;'>일정</th>
                    <th style='padding: 10px;'>특가 금액</th>
                    <th style='padding: 10px;'>예약</th>
                </tr>
        """
        for deal in deals:
            trip_nights = (deal.return_date - deal.depart_date).days
            html_content += f"""
                <tr style='border-bottom: 1px solid #eee; text-align: center;'>
                    <td style='padding: 10px; font-weight: bold;'>
                        {deal.origin} ➔ {deal.destination_name}
                        <br><span style='font-size: 12px; color: gray;'>({deal.destination_country})</span>
                    </td>
                    <td style='padding: 10px;'>
                        {deal.depart_date} ~ {deal.return_date}
                        <br><span style='font-size: 12px; color: gray;'>({trip_nights}박 {trip_nights+1}일)</span>
                    </td>
                    <td style='padding: 10px; color: #d93025; font-weight: bold;'>
                        {deal.price:,}원<br>
                        <span style='font-size: 12px; color: gray;'>(-{deal.discount_percentage}%)</span>
                    </td>
                    <td style='padding: 10px;'><a href='{deal.booking_link}' target='_blank'>확인</a></td>
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


def send_kakao_message(deals: List[Flight]) -> None:
    """카카오톡 '나에게 보내기'로 특가 요약 알림 발송 (전체 목록은 웹페이지로 연결)"""
    rest_api_key = os.environ.get("KAKAO_REST_API_KEY")
    refresh_token = os.environ.get("KAKAO_REFRESH_TOKEN")

    if not rest_api_key or not refresh_token:
        logging.warning("⚠️ 카카오 API 환경변수가 없어 카카오톡 발송을 건너뜁니다.")
        return

    if not deals:
        return

    try:
        token_res = requests.post(
            "https://kauth.kakao.com/oauth/token",
            data={
                "grant_type": "refresh_token",
                "client_id": rest_api_key,
                "refresh_token": refresh_token,
            },
        )
        token_res.raise_for_status()
        access_token = token_res.json().get("access_token")
    except Exception as e:
        logging.error(f"❌ 카카오 Access Token 갱신 실패: {e}")
        return

    top_deals = deals[:3]
    lines = [f"✈️ 오늘의 특가 항공권 {len(deals)}건 발견!\n"]
    for d in top_deals:
        nights = (d.return_date - d.depart_date).days
        lines.append(
            f"{d.origin}→{d.destination_name}({d.destination_country}) "
            f"{d.price:,}원 (-{d.discount_percentage}%) {nights}박{nights+1}일"
        )
    lines.append("\n👇 전체 목록 및 공유는 아래에서 확인하세요.")
    message_text = "\n".join(lines)

    template_object = {
        "object_type": "text",
        "text": message_text,
        "link": {
            "web_url": PAGE_URL,
            "mobile_web_url": PAGE_URL,
        },
        "button_title": "전체 특가 보기",
    }

    try:
        send_res = requests.post(
            "https://kapi.kakao.com/v2/api/talk/memo/default/send",
            headers={"Authorization": f"Bearer {access_token}"},
            data={"template_object": json.dumps(template_object)},
        )
        send_res.raise_for_status()
        logging.info("💬 카카오톡 알림 발송 성공!")
    except Exception as e:
        logging.error(f"❌ 카카오톡 발송 에러: {e}")
