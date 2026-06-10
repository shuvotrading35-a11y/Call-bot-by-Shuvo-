from telegram import Update, MessageEntity
from telegram.ext import ContextTypes, MessageHandler, filters
from services.user_service import get_user
from services.subscription_service import get_active_subscription
from services.referral_service import get_referral_stats
from database import get_connection
from keyboards.user import user_main_menu
from handlers.common import check_banned

# Telegram built-in animated emoji IDs (from official packs)
EMOJI_IDS = {
    "crown":   "5361491001621921650",   # 👑
    "diamond": "5368324170671202286",   # 💎
    "fire":    "5364337949912710950",   # 🔥
    "star":    "5361630896928207714",   # ⭐
    "check":   "5361541047592292442",   # ✅
    "cross":   "5361711688755582803",   # ❌
    "zap":     "5362015040248141965",   # ⚡
    "trophy":  "5362056062895539312",   # 🏆
    "chart":   "5364101687067598928",   # 📊
    "phone":   "5258337316715373336",   # 📞
    "people":  "5364426929728887445",   # 👥
}

def make_entity(emoji_id: str, offset: int, length: int = 2) -> MessageEntity:
    return MessageEntity(
        type=MessageEntity.CUSTOM_EMOJI,
        offset=offset,
        length=length,
        custom_emoji_id=emoji_id
    )

async def my_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_banned(update): return
    user_id = update.effective_user.id
    user = get_user(user_id)
    sub = get_active_subscription(user_id)
    ref_stats = get_referral_stats(user_id)

    conn = get_connection()
    call_logs = conn.execute(
        "SELECT target_number, call_limit, timestamp, status FROM call_logs "
        "WHERE user_id=? ORDER BY timestamp DESC LIMIT 5",
        (user_id,)
    ).fetchall()
    total_calls = conn.execute(
        "SELECT COUNT(*) FROM call_logs WHERE user_id=?", (user_id,)
    ).fetchone()[0]
    conn.close()

    if sub:
        sub_line = f"✅  Active  ·  {sub['plan_name']}  (Expires: {sub['end_date']})"
    else:
        sub_line = "❌  No Active Subscription"

    name = user.get('first_name') or update.effective_user.first_name or "N/A"
    username = f"@{user['username']}" if user['username'] else "N/A"
    role = "Admin" if user.get('is_admin') else ("Premium" if user.get('is_premium') else "Free User")

    text = (
        f"👑  My Account Information\n"
        f"{'─' * 30}\n\n"
        f"⭐  Name           :  {name}\n"
        f"🆔  Telegram ID  :  {user['user_id']}\n"
        f"📛  Username      :  {username}\n"
        f"🎭  Role              :  {role}\n"
        f"📅  Joined            :  {user['join_date']}\n\n"
        f"{'─' * 30}\n"
        f"💎  Credits           :  {user['credits']}\n"
        f"📞  Total Calls      :  {total_calls}\n"
        f"👥  Referrals         :  {ref_stats['total']}\n"
        f"🏆  Ref Earned      :  {ref_stats['earned']} credits\n\n"
        f"{'─' * 30}\n"
        f"⚡  Subscription:\n    {sub_line}\n\n"
        f"{'─' * 30}\n"
        f"🔥  Powered By @shuvo_9882"
    )

    # Build entities for each animated emoji position
    entities = []
    lines = text.split("\n")
    offset = 0
    for line in lines:
        for emoji_char, emoji_id in [
            ("👑", EMOJI_IDS["crown"]),
            ("⭐", EMOJI_IDS["star"]),
            ("💎", EMOJI_IDS["diamond"]),
            ("📞", EMOJI_IDS["phone"]),
            ("👥", EMOJI_IDS["people"]),
            ("🏆", EMOJI_IDS["trophy"]),
            ("⚡", EMOJI_IDS["zap"]),
            ("🔥", EMOJI_IDS["fire"]),
            ("✅", EMOJI_IDS["check"]),
            ("❌", EMOJI_IDS["cross"]),
        ]:
            pos = line.find(emoji_char)
            if pos != -1:
                entities.append(make_entity(emoji_id, offset + pos, len(emoji_char.encode('utf-16-le')) // 2))
        offset += len(line.encode('utf-16-le')) // 2 + 1  # +1 for newline

    # Add recent calls if any
    if call_logs:
        calls_text = f"\n{'─' * 30}\n📋  Recent Calls:\n"
        for log in call_logs:
            icon = "✅" if log['status'] == "submitted" else "❌"
            calls_text += f"  {icon}  {log['target_number']}  ·  {log['call_limit']}x  ·  {str(log['timestamp'])[:10]}\n"
        text += calls_text

    try:
        await update.message.reply_text(text, entities=entities, reply_markup=user_main_menu())
    except Exception:
        # Fallback without custom emoji if IDs don't work
        await update.message.reply_text(text, reply_markup=user_main_menu())

profile_handler = MessageHandler(filters.Regex("^👤 My Profile$"), my_profile)