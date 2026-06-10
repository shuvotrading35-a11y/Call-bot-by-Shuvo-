from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from services.user_service import get_user
from services.subscription_service import get_active_subscription
from services.referral_service import get_referral_stats
from database import get_connection
from keyboards.user import user_main_menu
from handlers.common import check_banned

async def my_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_banned(update): return
    user_id = update.effective_user.id
    user = get_user(user_id)
    sub = get_active_subscription(user_id)
    ref_stats = get_referral_stats(user_id)

    conn = get_connection()
    call_logs = conn.execute(
        "SELECT target_number, call_limit, timestamp, status FROM call_logs WHERE user_id=? ORDER BY timestamp DESC LIMIT 5",
        (user_id,)
    ).fetchall()
    total_calls = conn.execute("SELECT COUNT(*) FROM call_logs WHERE user_id=?", (user_id,)).fetchone()[0]
    conn.close()

    if sub:
        sub_text = f"✅  Active  ·  {sub['plan_name']}\n        ⏳  Expires: {sub['end_date']}"
        sub_icon = "💎"
    else:
        sub_text = "❌  No Active Subscription"
        sub_icon = "🔴"

    # Role badge
    role = "👑  Admin" if user.get('is_admin') else ("⭐  Premium" if user.get('is_premium') else "👤  Free User")

    text = (
        f"👑  My Account Information\n"
        f"{'─' * 30}\n\n"
        f"🌟  Name         :  {user.get('first_name') or update.effective_user.first_name}\n"
        f"🆔  Telegram ID  :  {user['user_id']}\n"
        f"📛  Username     :  @{user['username'] or 'N/A'}\n"
        f"🎭  Role            :  {role}\n"
        f"📅  Joined          :  {user['join_date']}\n\n"
        f"{'─' * 30}\n"
        f"💎  Credits           :  {user['credits']}\n"
        f"📞  Total Calls      :  {total_calls}\n"
        f"👥  Referrals         :  {ref_stats['total']}\n"
        f"🏆  Ref Earned      :  {ref_stats['earned']} credits\n\n"
        f"{'─' * 30}\n"
        f"{sub_icon}  Subscription:\n    {sub_text}\n\n"
        f"{'─' * 30}\n"
    )

    if call_logs:
        text += f"📋  Recent Calls:\n"
        for log in call_logs:
            icon = "✅" if log['status'] == "submitted" else "❌"
            text += f"  {icon}  {log['target_number']}  ·  {log['call_limit']}x  ·  {str(log['timestamp'])[:10]}\n"
        text += f"{'─' * 30}\n"

    text += f"🔥  Powered By @shuvo_9882"

    await update.message.reply_text(text, reply_markup=user_main_menu())

profile_handler = MessageHandler(filters.Regex("^👤 My Profile$"), my_profile)