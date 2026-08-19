# valuation.py
from typing import Optional, Tuple

TIER_TRIP_DAYS = {
    "domestic": (2, 7), "jp_near": (2, 7), "jp_mid": (3, 7),
    "cn_near": (2, 7), "cn_mid": (3, 7), "tw_hk": (3, 7),
    "sea_near": (4, 9), "sea_far": (5, 10), "mongolia": (4, 8),
    "guam": (4, 8), "oceania": (7, 14), "europe": (7, 14),
    "namerica": (7, 14), "longhaul": (7, 14),
}
DEFAULT_TRIP_DAYS = (3, 7)

TIER_BASELINE = {
    "domestic": 45000, "jp_near": 150000, "jp_mid": 200000,
    "cn_near": 150000, "cn_mid": 220000, "tw_hk": 200000,
    "sea_near": 250000, "sea_far": 400000, "mongolia": 350000,
    "guam": 350000, "oceania": 800000, "europe": 900000,
    "namerica": 1000000, "longhaul": 1000000,
}

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

CITY_NAME_TIER = {
    "후쿠오카시": "jp_near", "오사카시": "jp_near", "기타큐슈시": "jp_near",
    "사가시": "jp_near", "요나고시": "jp_near", "다카마쓰시": "jp_near",
    "히로시마시": "jp_near", "마쓰야마시": "jp_near", "오이타시": "jp_near",
    "구마모토시": "jp_near", "가고시마시": "jp_near", "우베시": "jp_near",
    "이즈모시": "jp_near",
    "도쿄도": "jp_mid", "나고야시": "jp_mid", "삿포로시": "jp_mid",
    "오키나와시": "jp_mid", "시즈오카시": "jp_mid", "미야자키시": "jp_mid",
    "나가사키시": "jp_mid", "고마쓰시": "jp_mid", "센다이시": "jp_mid",
    "도야마시": "jp_mid", "아오모리시": "jp_mid",
    "다롄시": "cn_near", "칭다오시": "cn_near",
    "옌지시": "cn_near", "선양시": "cn_near",
    "상하이": "cn_mid", "베이징시": "cn_mid", "선전시": "cn_mid",
    "광저우시": "cn_mid", "시안시": "cn_mid", "청두시": "cn_mid",
    "타이베이": "tw_hk", "가오슝시": "tw_hk", "타이중시": "tw_hk",
    "홍콩": "tw_hk", "마카오": "tw_hk",
    "다낭": "sea_near", "하노이": "sea_near", "호치민시": "sea_near",
    "푸꾸옥": "sea_near", "나트랑": "sea_near", "방콕": "sea_near",
    "치앙마이": "sea_near", "세부시": "sea_near", "마닐라": "sea_near",
    "클락": "sea_near",
    "코타키나발루": "sea_far", "발리": "sea_far", "덴파사르": "sea_far",
    "싱가포르": "sea_far", "쿠알라룸푸르": "sea_far", "푸켓": "sea_far",
    "반다르세리베가완": "sea_far", "페낭": "sea_far",
    "울란바토르": "mongolia",
    "괌": "guam", "사이판": "guam",
    "브리즈번": "oceania", "시드니": "oceania", "멜버른": "oceania",
    "오클랜드": "oceania",
    "바르샤바": "europe", "브로츠와프": "europe", "크라쿠프": "europe",
    "로마": "europe", "밀라노": "europe", "베네치아": "europe",
    "파리": "europe", "런던": "europe", "프랑크푸르트": "europe",
    "뮌헨": "europe", "베를린": "europe", "암스테르담": "europe",
    "바르셀로나": "europe", "마드리드": "europe", "리스본": "europe",
    "비엔나": "europe", "프라하": "europe", "부다페스트": "europe",
    "취리히": "europe", "이스탄불": "europe", "아테네": "europe",
    "코펜하겐": "europe", "스톡홀름": "europe", "헬싱키": "europe",
    "오슬로": "europe", "더블린": "europe", "브뤼셀": "europe",
}

COUNTRY_TIER = {
    "대한민국": "domestic", "일본": "jp_mid", "중국": "cn_mid",
    "대만": "tw_hk", "홍콩": "tw_hk", "마카오": "tw_hk",
    "베트남": "sea_near", "태국": "sea_near", "필리핀": "sea_near",
    "캄보디아": "sea_near", "라오스": "sea_near",
    "말레이시아": "sea_far", "싱가포르": "sea_far",
    "인도네시아": "sea_far", "브루나이": "sea_far",
    "몽골": "mongolia",
    "오스트레일리아": "oceania", "뉴질랜드": "oceania",
    "폴란드": "europe", "이탈리아": "europe", "프랑스": "europe",
    "독일": "europe", "영국": "europe", "스페인": "europe",
    "포르투갈": "europe", "네덜란드": "europe", "체코": "europe",
    "오스트리아": "europe", "헝가리": "europe", "스위스": "europe",
    "튀르키예": "europe", "터키": "europe", "그리스": "europe",
    "덴마크": "europe", "스웨덴": "europe", "노르웨이": "europe",
    "핀란드": "europe", "아일랜드": "europe", "벨기에": "europe",
    "미국": "namerica", "캐나다": "namerica",
}


def resolve_tier(destination_id, country, name=""):
    return (AIRPORT_TIER.get(destination_id)
            or CITY_NAME_TIER.get(name.strip())
            or COUNTRY_TIER.get(country)
            or "longhaul")


def trip_days_range(destination_id, country, name=""):
    tier = resolve_tier(destination_id, country, name)
    return TIER_TRIP_DAYS.get(tier, DEFAULT_TRIP_DAYS)


def value_ratio(price, destination_id, country, name=""):
    if not price:
        return None
    baseline = TIER_BASELINE[resolve_tier(destination_id, country, name)]
    return round(price / baseline, 3)


def grade(ratio):
    if ratio is None:
        return "unknown"
    if ratio <= 0.70:
        return "\U0001F525 \uCD08\uD2B9\uAC00"
    if ratio <= 0.85:
        return "\u2728 \uD2B9\uAC00"
    if ratio <= 1.00:
        return "\U0001F44D \uAD1C\uCC2E\uC74C"
    return "\uBCF4\uD1B5"
