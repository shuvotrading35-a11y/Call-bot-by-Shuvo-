import re
from datetime import datetime, timedelta

def is_valid_bd_phone(number: str) -> bool:
    pattern = r'^01[3-9]\d{8}$'
    return bool(re.match(pattern, number))

def format_datetime(ts: str) -> str:
    try:
        dt = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
        return dt.strftime("%d %b %Y, %I:%M %p")
    except:
        return ts

def can_claim_daily(last_claim_date: str) -> bool:
    if not last_claim_date:
        return True
    last = datetime.strptime(last_claim_date, "%Y-%m-%d")
    return (datetime.now().date() - last.date()).days >= 1

def generate_referral_link(bot_username: str, user_id: int) -> str:
    return f"https://t.me/{bot_username}?start=ref_{user_id}"
