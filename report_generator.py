import os
import logging
from typing import List
from models import Flight

OUTPUT_DIR = "public"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "index.html")


def generate_report_html(deals: List[Flight], js_key: str) -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    if not deals:
        rows_html = "<tr><td colspan='4' style='padding:20px;text-align:center;'>오늘은 조건에 맞는 특가가 없습니다.</td></tr>"
    else:
        rows_html = ""
        for deal in deals:
            trip_nights = (deal.return_date - deal.depart_date).days
            rows_html += f"""
            <tr>
                <td>
                    {deal.origin} ➔ {deal.destination_name}
                    <br><span class='sub'>({deal.destination_country})</span>
                </td>
                <td>
                    {deal.depart_date} ~ {deal.return_date}
                    <br><span class='sub'>({trip_nights}박 {trip_nights+1}일)</span>
                </td>
                <td class='price'>
                    {deal.price:,}원<br>
                    <span class='sub'>(-{deal.discount_percentage}%)</span>
                </td>
                <td><a href="{deal.booking_link}" target="_blank" rel="noopener">확인</a></td>
            </tr>
            """

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>PTIS 오늘의 실시간 특가</title>
<script src="https://t1.kakaocdn.net/kakao_js_sdk/2.7.2/kakao.min.js"></script>
<style>
  body {{ font-family: 'Malgun Gothic', sans-serif; padding: 20px; max-width: 800px; margin: 0 auto; background:#f7f8fa; }}
  h2 {{ color: #1a73e8; }}
  table {{ border-collapse: collapse; width: 100%; background:white; }}
  th {{ background-color: #1a73e8; color: white; padding: 10px; }}
  td {{ padding: 10px; text-align: center; border-bottom: 1px solid #eee; }}
  .sub {{ font-size: 12px; color: gray; }}
  .price {{ color: #d93025; font-weight: bold; }}
  #shareBtn {{
    display: inline-block; margin-bottom: 16px; padding: 10px 16px;
    background-color: #FEE500; color: #191919; border: none; border-radius: 6px;
    font-weight: bold; cursor: pointer; font-size: 15px;
  }}
</style>
</head>
<body>
  <h2>📊 오늘의 실시간 직항 특가 ({len(deals)}건)</h2>
  <button id="shareBtn">💬 카카오톡으로 공유하기</button>
  <table>
    <tr>
      <th>노선</th><th>일정</th><th>특가 금액</th><th>예약</th>
    </tr>
    {rows_html}
  </table>

  <script>
    Kakao.init('{js_key}');
    document.getElementById('shareBtn').addEventListener('click', function() {{
      Kakao.Share.sendDefault({{
        objectType: 'feed',
        content: {{
          title: '✈️ 오늘의 실시간 특가 항공권 ({len(deals)}건)',
          description: '지금 확인해보세요! 실시간 특가 리포트',
          imageUrl: 'https://developers.kakao.com/assets/img/about/logos/kakaolink/kakaolink_btn_medium.png',
          link: {{
            mobileWebUrl: window.location.href,
            webUrl: window.location.href
          }}
        }},
        buttons: [
          {{
            title: '전체 특가 보기',
            link: {{
              mobileWebUrl: window.location.href,
              webUrl: window.location.href
            }}
          }}
        ]
      }});
    }});
  </script>
</body>
</html>
"""

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    logging.info(f"🌐 리포트 페이지 생성 완료: {OUTPUT_FILE}")
