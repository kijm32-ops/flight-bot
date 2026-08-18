# valuation.py
from typing import Optional, Tuple
from config import TIER_TRIP_DAYS, DEFAULT_TRIP_DAYS

TIER_BASELINE = {
    "domestic":   45_000,   # 60,000 → 45,000 (제주 5만원대는 평범한 가격)
    "jp_near":   150_000,
    "jp_mid":    200_000,
    "cn_near":   150_000,
    "cn_mid":    220_000,
    "tw_hk":     200_000,
    "sea_near":  250_000,
    "sea_far":   400_000,
    "mongolia":  350_000,
    "guam":      350_000,
    "oceania":   800_000,
    "europe":    900_000,
    "namerica": 1_000_000,
    "longhaul": 1_000_000,
}

# 1순위: 공항 IATA 코드 (destination_id가 코드 형태일 때만 맞음)
AIRPORT_TIER = {
    "CJU": "domestic", "PUS": "domestic", "USN": "domestic",
    "RSU": "domestic", "KWJ": "domestic", "TAE": "domestic",
    "FUK": "jp_near", "KIX": "jp_near", "KKJ": "jp_near", "HSG": "jp_near",
    "YGJ": "jp_near", "TAK": "jp_near", "OIT": "jp_near", "KMJ": "jp_near",
    "KOJ": "jp_near", "HIJ": "jp_near", "UBJ": "jp_near", "IZO": "jp_near",
    "NRT": "jp_mid", "HND": "jp_mid", "NGO": "jp_mid", "CTS": "jp_mid",
    "KMQ": "jp_mid", "MYJ": "jp_mid", "KMI": "jp_mid", "NGS": "jp_mid",
    "OKA": "jp_mid", "SDJ": "jp_mid", "TOY": "jp_mid", "AOJ": "jp_mid",
    "DLC": "cn_near", "TAO": "cn_near", "YNJ": "cn_near", "SHE": "cn_near",
    "PVG": "cn_mid", "PEK": "cn_mid", "PKX": "cn_mid", "CAN": "cn_mid",
    "XIY": "cn_mid", "CTU": "cn_mid",
    "TPE": "tw_hk", "RMQ": "tw_hk", "KHH": "tw_hk", "HKG": "tw_hk", "MFM": "tw_hk",
    "DAD": "sea_near", "CXR": "sea_near", "HAN": "sea_near", "SGN": "sea_near",
    "PQC": "sea_near", "BKK": "sea_near", "DMK": "sea_near", "CRK": "sea_near",
    "CEB": "sea_near", "MNL": "sea_near", "KLO": "sea_near", "CNX": "sea_near",
    "DPS": "sea_far", "SIN": "sea_far", "BKI": "sea_far", "KUL": "sea_far",
    "BWN": "sea_far", "HKT": "sea_far", "PEN": "sea_far",
    "ULN": "mongolia", "GUM": "guam", "SPN": "guam",
    "BNE": "oceania", "SYD": "oceania", "MEL": "oceania", "AKL": "oceania",
    "WAW": "europe", "WRO": "europe", "KRK": "europe", "GDN": "europe",
    "FCO": "europe", "MXP": "europe", "VCE": "europe", "NAP": "europe",
    "CDG": "europe", "ORY": "europe", "LHR": "europe", "LGW": "europe",
    "FRA": "europe", "MUC": "europe", "BER": "europe", "AMS": "europe",
    "BCN": "europe", "MAD": "europe", "LIS": "europe", "OPO": "europe",
    "VIE": "europe", "PRG": "europe", "BUD": "europe", "ZRH": "europe",
    "IST": "europe", "ATH": "europe", "CPH": "europe", "ARN": "europe",
    "HEL": "europe", "OSL": "europe", "DUB": "europe", "BRU": "europe",
    "LAX": "namerica", "SFO": "namerica", "SEA": "namerica", "JFK": "namerica",
    "EWR": "namerica", "ORD": "namerica", "IAD": "namerica", "BOS": "namerica",
    "YVR": "namerica", "YYZ": "namerica", "HNL": "namerica", "LAS": "namerica",
}

# 2순위: 리포트에 실제로 찍히는 한글 도시명. destination_id 형식이 무엇이든
# 이 매핑이 화면과 100% 일치하므로 가장 신뢰도가 높다.
CITY_NAME_TIER = {
    # 일본 근거리
    "후쿠오카시": "jp_near", "오사카시": "jp_near", "기타큐슈시": "jp_near",
    "사가시": "jp_near", "요나고시": "jp_near", "다카마쓰시": "jp_near",
    "히로시마시": "jp_near", "마쓰야마시": "jp_near", "오이타시": "jp_near",
    "구마모토시": "jp_near", "가고시마시": "jp_near", "우베시": "jp_near",
    "이즈모시": "jp_near",
    # 일본 중거리
    "도쿄도": "jp_mid", "나고야시": "jp_mid", "삿포로시": "jp_mid",
    "오키나와시": "jp_mid", "시즈오카시": "jp_mid", "미야자키시": "jp_mid",
    "나가사키시": "jp_mid", "고마쓰시": "jp_mid", "센다이시": "jp_mid",
    "마쓰야마시": "jp_mid", "도야마시": "jp_mid", "아오모리시": "jp_mid",
    # 중국
    "다롄
