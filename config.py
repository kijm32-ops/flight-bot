import os

SERPAPI_KEY = os.environ.get("SERPAPI_KEY")
GMAIL_USER = os.environ.get("GMAIL_USER")
GMAIL_PASSWORD = os.environ.get("GMAIL_PASSWORD")

ORIGIN = "ICN"
DATE_OUT = "2026-05-15"
DATE_RET = "2026-05-19"

TARGETS = {
    "NRT": ("도쿄(나리타)", 250000),
    "KIX": ("오사카(간사이)", 220000),
    "FUK": ("후쿠오카", 160000),
    "TPE": ("타이베이", 230000),
    "DAD": ("다낭", 290000),
    "BKK": ("방콕", 350000),
    "CBU": ("세부", 260000),
}
