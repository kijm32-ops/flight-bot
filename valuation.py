# valuation.py
from typing import Optional

# 권역별 "이 정도면 싸다" 기준가 (1인 왕복, KRW)
TIER_BASELINE = {
    "domestic":   60_000,
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
    "longhaul":  900_000,
}

AIRPORT_TIER = {
    # 국내
    "CJU": "domestic", "PUS": "domestic", "USN": "domestic",
    "RSU": "domestic", "KWJ": "domestic", "TAE": "domestic",
    # 일본 근거리
    "FUK": "jp_near", "KIX": "jp_near", "KKJ": "jp_near", "HSG": "jp_near",
    "YGJ": "jp_near", "TAK": "jp_near", "OIT": "jp_near", "KMJ": "jp_near",
    "KOJ": "jp_near", "HIJ": "jp_near", "UBJ": "jp_near", "IZO": "jp_near",
    # 일본 중거리
    "NRT": "jp_mid", "HND": "jp_mid", "NGO": "jp_mid", "CTS": "jp_mid",
    "KMQ": "jp_mid", "MYJ": "jp_mid", "KMI": "jp_mid", "NGS": "jp_mid",
    "OKA": "jp_mid", "SDJ": "jp_mid", "TOY": "jp_mid", "AOJ": "jp_mid",
    # 중국
    "DLC": "cn_near", "TAO": "cn_near", "YNJ": "cn_near", "SHE": "cn_near",
    "PVG": "cn_mid", "PEK": "cn_mid", "PKX": "cn_mid", "CAN": "cn_mid",
    "XIY": "cn_mid", "CTU": "cn_mid",
    # 대만/홍콩/마카오
    "TPE": "tw_hk", "RMQ": "tw_hk", "KHH": "tw_hk", "HKG": "tw_hk", "MFM": "tw_hk",
    # 동남아 근거리
    "DAD": "sea_near", "CXR": "sea_near", "HAN": "sea_near", "SGN": "sea_near",
    "PQC": "sea_near", "BKK": "sea_near", "DMK": "sea_near", "CRK": "sea_near",
    "CEB": "sea_near", "MNL": "sea_near", "KLO": "sea_near",
    # 동남아 원거리
    "DPS": "sea_far", "SIN": "sea_far", "BKI": "sea_far", "KUL": "sea_far",
    "BWN": "sea_far", "HKT": "sea_far", "PEN": "sea_far",
    # 기타
    "ULN": "mongolia", "GUM": "guam", "SPN": "guam",
    "BNE": "oceania", "SYD": "oceania", "MEL": "oceania", "AKL": "oceania",
}

COUNTRY_TIER = {
    "대한민국": "domestic", "일본": "jp_mid", "중국": "cn_mid",
    "대만": "tw_hk", "홍콩": "tw_hk", "베트남": "sea_near",
    "태국": "sea_near", "필리핀": "sea_near", "말레이시아": "sea_far",
    "싱가포르": "sea_far", "인도네시아": "sea_far", "브루나이": "sea_far",
    "몽골": "mongolia", "오스트레일리아": "oceania", "뉴질랜드": "oceania",
}

def resolve_tier(destination_id: str, country: str) -> str:
    return (AIRPORT_TIER.get(destination_id)
            or COUNTRY_TIER.get(country)
            or "longhaul")

def value_ratio(price: int, destination_id: str, country: str) -> Optional[float]:
    """1.0 = 권역 기준가와 동일. 낮을수록 특가."""
    if not price:
        return None
    baseline = TIER_BASELINE[resolve_tier(destination_id, country)]
    return round(price / baseline, 3)

def grade(ratio: Optional[float]) -> str:
    if ratio is None:      return "unknown"
    if ratio <= 0.70:      return "🔥 초특가"
    if ratio <= 0.85:      return "✨ 특가"
    if ratio <= 1.00:      return "👍 괜찮음"
    return "보통"
