import os
import logging
from typing import List, Set, Tuple
from models import Flight

OUTPUT_DIR = "public"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "index.html")

# value_grade 문자열 → CSS 클래스 매핑
GRADE_CLASS = {
    "🔥 초특가": "grade-super",
    "✨ 특가": "grade-good",
    "👍 괜찮음": "grade-ok",
}


def _grade_badge(deal: Flight) -> str:
    """권역 기준가 대비 등급 배지 HTML"""
    if not deal.value_grade or deal.value_grade == "unknown":
        return ""
    cls = GRADE_CLASS.get(deal.value_grade, "grade-ok")
    ratio_text = f"기준가 대비 {int(deal.value_ratio * 100)}%"
    return f"<span class='grade {cls}' title='{ratio_text}'>{deal.value_grade}</span>"


def _alt_dates_html(deal: Flight) -> str:
    """같은 목적지의 다른 저렴한 날짜 조합"""
    if not deal.alt_dates:
        return ""
    items = ""
    for depart, ret, price in deal.alt_dates:
        items += f"<li>{depart} ~ {ret} · {price:,}원</li>"
    return f"""
        <details class='alt'>
            <summary>다른 날짜 {len(deal.alt_dates)}건</summary>
            <ul>{items}</ul>
        </details>
    """


def generate_report_html(deals: List[Flight], js_key: str, low_price_keys: Set[Tuple[str, str, str, str]] = None) -> None:
    low_price_keys = low_price_keys or set()
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    if not deals:
        rows_html = "<tr><td colspan='4' style='padding:20px;text-align:center;'>오늘은 조건에 맞는 특가가 없습니다.</td></tr>"
    else:
        rows_html = ""
        for deal in deals:
            trip_nights = (deal.return_date - deal.depart_date).days
            dedup_key = (deal.origin, deal.destination, str(deal.depart_date), str(deal.return_date))
            badge = "<br><span class='badge'>🔥 30일 최저가</span>" if dedup_key in low_price_keys else ""
            grade_badge = _grade_badge(deal)
            alt_html = _alt_dates_html(deal)

            rows_html += f"""
            <tr>
                <td>
                    {deal.origin} ➔ {deal.destination_name}
                    <br><span class='sub'>({deal.destination_country})</span>
                    {f"<br>{grade_badge}" if grade_badge else ""}
                </td>
                <td>
                    {deal.depart_date} ~ {deal.return_date}
                    <br><span class='sub'>({trip_nights}박 {trip_nights+1}일)</span>
                    {alt_html}
                </td>
                <td class='price'>
                    {deal.price:,}원<br>
                    <span class='sub'>(-{deal.discount_percentage}%)</span>
                    {badge}
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
  .badge {{
    display:inline-block; font-size: 11px; color:#d93025; background:#ffe4e1;
    padding: 2px 6px; border-radius: 4px; margin-top: 4px;
  }}
  .grade {{
    display:inline-block; font-size: 11px; font-weight: bold;
    padding: 2px 7px; border-radius: 10px; margin-top: 5px;
  }}
  .grade-super {{ color:#b3261e; background:#fce8e6; }}
  .grade-good  {{ color:#b06000; background:#fef7e0; }}
  .grade-ok    {{ color:#1e6b3a; background:#e6f4ea; }}
  .alt {{ margin-top: 6px; font-size: 12px; }}
  .alt summary {{
    cursor: pointer; color: #1a73e8; list-style: none;
    display: inline-block; padding: 2px 6px;
    border: 1px solid #d2e3fc; border-radius: 4px; background: #f0f6ff;
  }}
  .alt summary::-webkit-details-marker {{ display: none; }}
  .alt ul {{
    list-style: none; padding: 6px 0 0 0; margin: 0;
    color: #5f6368; text-align: center;
  }}
  .alt li {{ padding: 2px 0; }}
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
