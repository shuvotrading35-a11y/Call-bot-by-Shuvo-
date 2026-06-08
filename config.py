import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(",")))
API_KEY = os.getenv("API_KEY")
API_URL = os.getenv("API_URL", "https://rakabro.top/api.php")
DB_PATH = os.getenv("DB_PATH", "data/database.db")

PLANS = {
    "7days": {"name": "📞 7 Days Unlimited", "price": 60, "duration_days": 7},
    "15days": {"name": "📞 15 Days Unlimited", "price": 80, "duration_days": 15},
    "1month": {"name": "📞 1 Month Unlimited", "price": 110, "duration_days": 30},
    "api1month": {"name": "📞 1 Month API", "price": 1000, "duration_days": 30, "api_access": True}
}

DEFAULT_CREDITS = 5
REFERRAL_BONUS = 10
DAILY_REWARD_MIN = 1
DAILY_REWARD_MAX = 10
CALL_LIMITS = list(range(1, 11))
FREE_CALL_LIMIT = 5
