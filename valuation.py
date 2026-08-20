# valuation.py
# NOTE: All Korean text is written as unicode escape sequences (\uXXXX)
# to prevent corruption from editors/IMEs during copy-paste.

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
    "CJU": "domestic", "PUS": "domestic", "USN": "domestic", "RSU": "domestic",
    "KWJ": "domestic", "TAE": "domestic", "FUK": "jp_near", "KIX": "jp_near",
    "KKJ": "jp_near", "HSG": "jp_near", "YGJ": "jp_near", "TAK": "jp_near",
    "OIT": "jp_near", "KMJ": "jp_near", "KOJ": "jp_near", "HIJ": "jp_near",
    "UBJ": "jp_near", "IZO": "jp_near", "NRT": "jp_mid", "HND": "jp_mid",
    "NGO": "jp_mid", "CTS": "jp_mid", "KMQ": "jp_mid", "MYJ": "jp_mid",
    "KMI": "jp_mid", "NGS": "jp_mid", "OKA": "jp_mid", "SDJ": "jp_mid",
    "TOY": "jp_mid", "AOJ": "jp_mid", "DLC": "cn_near", "TAO": "cn_near",
    "YNJ": "cn_near", "SHE": "cn_near", "PVG": "cn_mid", "PEK": "cn_mid",
    "PKX": "cn_mid", "CAN": "cn_mid", "XIY": "cn_mid", "CTU": "cn_mid",
    "TPE": "tw_hk", "RMQ": "tw_hk", "KHH": "tw_hk", "HKG": "tw_hk",
    "MFM": "tw_hk", "DAD": "sea_near", "CXR": "sea_near", "HAN": "sea_near",
    "SGN": "sea_near", "PQC": "sea_near", "BKK": "sea_near", "DMK": "sea_near",
    "CRK": "sea_near", "CEB": "sea_near", "MNL": "sea_near", "KLO": "sea_near",
    "CNX": "sea_near", "DPS": "sea_far", "SIN": "sea_far", "BKI": "sea_far",
    "KUL": "sea_far", "BWN": "sea_far", "HKT": "sea_far", "PEN": "sea_far",
    "ULN": "mongolia", "GUM": "guam", "SPN": "guam", "BNE": "oceania",
    "SYD": "oceania", "MEL": "oceania", "AKL": "oceania", "WAW": "europe",
    "WRO": "europe", "KRK": "europe", "GDN": "europe", "FCO": "europe",
    "MXP": "europe", "VCE": "europe", "NAP": "europe", "CDG": "europe",
    "ORY": "europe", "LHR": "europe", "LGW": "europe", "FRA": "europe",
    "MUC": "europe", "BER": "europe", "AMS": "europe", "BCN": "europe",
    "MAD": "europe", "LIS": "europe", "OPO": "europe", "VIE": "europe",
    "PRG": "europe", "BUD": "europe", "ZRH": "europe", "IST": "europe",
    "ATH": "europe", "CPH": "europe", "ARN": "europe", "HEL": "europe",
    "OSL": "europe", "DUB": "europe", "BRU": "europe", "LAX": "namerica",
    "SFO": "namerica", "SEA": "namerica", "JFK": "namerica", "EWR": "namerica",
    "ORD": "namerica", "IAD": "namerica", "BOS": "namerica", "YVR": "namerica",
    "YYZ": "namerica", "HNL": "namerica", "LAS": "namerica",
}

CITY_NAME_TIER = {
    "\uD6C4\uCFE0\uC624\uCE74\uC2DC": "jp_near", "\uC624\uC0AC\uCE74\uC2DC": "jp_near",
    "\uAE30\uD0C0\uD050\uC288\uC2DC": "jp_near", "\uC0AC\uAC00\uC2DC": "jp_near",
    "\uC694\uB098\uACE0\uC2DC": "jp_near", "\uB2E4\uCE74\uB9C8\uC4F0\uC2DC": "jp_near",
    "\uD788\uB85C\uC2DC\uB9C8\uC2DC": "jp_near", "\uB9C8\uC4F0\uC57C\uB9C8\uC2DC": "jp_near",
    "\uC624\uC774\uD0C0\uC2DC": "jp_near", "\uAD6C\uB9C8\uBAA8\uD1A0\uC2DC": "jp_near",
    "\uAC00\uACE0\uC2DC\uB9C8\uC2DC": "jp_near", "\uC6B0\uBCA0\uC2DC": "jp_near",
    "\uC774\uC988\uBAA8\uC2DC": "jp_near", "\uB3C4\uCFC4\uB3C4": "jp_mid",
    "\uB098\uACE0\uC57C\uC2DC": "jp_mid", "\uC0BF\uD3EC\uB85C\uC2DC": "jp_mid",
    "\uC624\uD0A4\uB098\uC640\uC2DC": "jp_mid", "\uC2DC\uC988\uC624\uCE74\uC2DC": "jp_mid",
    "\uBBF8\uC57C\uC790\uD0A4\uC2DC": "jp_mid", "\uB098\uAC00\uC0AC\uD0A4\uC2DC": "jp_mid",
    "\uACE0\uB9C8\uC4F0\uC2DC": "jp_mid", "\uC13C\uB2E4\uC774\uC2DC": "jp_mid",
    "\uB3C4\uC57C\uB9C8\uC2DC": "jp_mid", "\uC544\uC624\uBAA8\uB9AC\uC2DC": "jp_mid",
    "\uB2E4\uB844\uC2DC": "cn_near", "\uCE6D\uB2E4\uC624\uC2DC": "cn_near",
    "\uC60C\uC9C0\uC2DC": "cn_near", "\uC120\uC591\uC2DC": "cn_near",
    "\uC0C1\uD558\uC774": "cn_mid", "\uBCA0\uC774\uC9D5\uC2DC": "cn_mid",
    "\uC120\uC804\uC2DC": "cn_mid", "\uAD11\uC800\uC6B0\uC2DC": "cn_mid",
    "\uC2DC\uC548\uC2DC": "cn_mid", "\uCCAD\uB450\uC2DC": "cn_mid",
    "\uD0C0\uC774\uBCA0\uC774": "tw_hk", "\uAC00\uC624\uC29D\uC2DC": "tw_hk",
    "\uD0C0\uC774\uC911\uC2DC": "tw_hk", "\uD64D\uCF69": "tw_hk",
    "\uB9C8\uCE74\uC624": "tw_hk", "\uB2E4\uB0AD": "sea_near",
    "\uD558\uB178\uC774": "sea_near", "\uD638\uCE58\uBBFC\uC2DC": "sea_near",
    "\uD478\uAFB8\uC625": "sea_near", "\uB098\uD2B8\uB791": "sea_near",
    "\uBC29\uCF55": "sea_near", "\uCE58\uC559\uB9C8\uC774": "sea_near",
    "\uC138\uBD80\uC2DC": "sea_near", "\uB9C8\uB2D0\uB77C": "sea_near",
    "\uD074\uB77D": "sea_near", "\uCF54\uD0C0\uD0A4\uB098\uBC1C\uB8E8": "sea_far",
    "\uBC1C\uB9AC": "sea_far", "\uB374\uD30C\uC0AC\uB974": "sea_far",
    "\uC2F1\uAC00\uD3EC\uB974": "sea_far", "\uCFE0\uC54C\uB77C\uB8F8\uD478\uB974": "sea_far",
    "\uD478\uCF13": "sea_far", "\uBC18\uB2E4\uB974\uC138\uB9AC\uBCA0\uAC00\uC644": "sea_far",
    "\uD398\uB0AD": "sea_far", "\uC6B8\uB780\uBC14\uD1A0\uB974": "mongolia",
    "\uAD0C": "guam", "\uC0AC\uC774\uD310": "guam",
    "\uBE0C\uB9AC\uC988\uBC88": "oceania", "\uC2DC\uB4DC\uB2C8": "oceania",
    "\uBA5C\uBC84\uB978": "oceania", "\uC624\uD074\uB79C\uB4DC": "oceania",
    "\uBC14\uB974\uC0E4\uBC14": "europe", "\uBE0C\uB85C\uCE20\uC640\uD504": "europe",
    "\uD06C\uB77C\uCFE0\uD504": "europe", "\uB85C\uB9C8": "europe",
    "\uBC00\uB77C\uB178": "europe", "\uBCA0\uB124\uCE58\uC544": "europe",
    "\uD30C\uB9AC": "europe", "\uB7F0\uB358": "europe",
    "\uD504\uB791\uD06C\uD478\uB974\uD2B8": "europe", "\uBB8C\uD5E8": "europe",
    "\uBCA0\uB97C\uB9B0": "europe", "\uC554\uC2A4\uD14C\uB974\uB2F4": "europe",
    "\uBC14\uB974\uC140\uB85C\uB098": "europe", "\uB9C8\uB4DC\uB9AC\uB4DC": "europe",
    "\uB9AC\uC2A4\uBCF8": "europe", "\uBE44\uC5D4\uB098": "europe",
    "\uD504\uB77C\uD558": "europe", "\uBD80\uB2E4\uD398\uC2A4\uD2B8": "europe",
    "\uCDE8\uB9AC\uD788": "europe", "\uC774\uC2A4\uD0C4\uBD88": "europe",
    "\uC544\uD14C\uB124": "europe", "\uCF54\uD39C\uD558\uAC90": "europe",
    "\uC2A4\uD1A1\uD640\uB984": "europe", "\uD5EC\uC2F1\uD0A4": "europe",
    "\uC624\uC2AC\uB85C": "europe", "\uB354\uBE14\uB9B0": "europe",
    "\uBE0C\uB93C\uC140": "europe",
}

COUNTRY_TIER = {
    "\uB300\uD55C\uBBFC\uAD6D": "domestic", "\uC77C\uBCF8": "jp_mid",
    "\uC911\uAD6D": "cn_mid", "\uB300\uB9CC": "tw_hk",
    "\uD64D\uCF69": "tw_hk", "\uB9C8\uCE74\uC624": "tw_hk",
    "\uBCA0\uD2B8\uB0A8": "sea_near", "\uD0DC\uAD6D": "sea_near",
    "\uD544\uB9AC\uD540": "sea_near", "\uCE84\uBCF4\uB514\uC544": "sea_near",
    "\uB77C\uC624\uC2A4": "sea_near", "\uB9D0\uB808\uC774\uC2DC\uC544": "sea_far",
    "\uC2F1\uAC00\uD3EC\uB974": "sea_far", "\uC778\uB3C4\uB124\uC2DC\uC544": "sea_far",
    "\uBE0C\uB8E8\uB098\uC774": "sea_far", "\uBABD\uACE8": "mongolia",
    "\uC624\uC2A4\uD2B8\uB808\uC77C\uB9AC\uC544": "oceania", "\uB274\uC9C8\uB79C\uB4DC": "oceania",
    "\uD3F4\uB780\uB4DC": "europe", "\uC774\uD0C8\uB9AC\uC544": "europe",
    "\uD504\uB791\uC2A4": "europe", "\uB3C5\uC77C": "europe",
    "\uC601\uAD6D": "europe", "\uC2A4\uD398\uC778": "europe",
    "\uD3EC\uB974\uD22C\uAC08": "europe", "\uB124\uB35C\uB780\uB4DC": "europe",
    "\uCCB4\uCF54": "europe", "\uC624\uC2A4\uD2B8\uB9AC\uC544": "europe",
    "\uD5DD\uAC00\uB9AC": "europe", "\uC2A4\uC704\uC2A4": "europe",
    "\uD280\uB974\uD0A4\uC608": "europe", "\uD130\uD0A4": "europe",
    "\uADF8\uB9AC\uC2A4": "europe", "\uB374\uB9C8\uD06C": "europe",
    "\uC2A4\uC6E8\uB374": "europe", "\uB178\uB974\uC6E8\uC774": "europe",
    "\uD540\uB780\uB4DC": "europe", "\uC544\uC77C\uB79C\uB4DC": "europe",
    "\uBCA8\uAE30\uC5D0": "europe", "\uBBF8\uAD6D": "namerica",
    "\uCE90\uB098\uB2E4": "namerica",
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
