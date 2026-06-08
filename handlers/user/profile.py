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

    # Subscription status
    if sub:
        sub_status = f"🟢 Active — {sub['plan_name']}\n   ⏳ Expires: {sub['end_date']}"
    else:
        sub_status = "🔴 Inactive"

    # Call history (last 5)
    conn = get_connection()
    call_logs = conn.execute(
        "SELECT target_number, call_limit, timestamp, status FROM call_logs WHERE user_id=? ORDER BY timestamp DESC LIMIT 5",
        (user_id,)
    ).fetchall()
    total_calls = conn.execute("SELECT COUNT(*) FROM call_logs WHERE user_id=?", (user_id,)).fetchone()[0]
    conn.close()

    text = (
        f"👤 My Profile\n"
        f"{'━'*25}\n"
        f"🆔 User ID: {user['user_id']}\n"
        f"👤 Username: @{user['username'] or 'N/A'}\n"
        f"📅 Join Date: {user['join_date']}\n"
        f"{'━'*25}\n"
        f"💰 Credits: {user['credits']}\n"
        f"📞 Total Calls: {total_calls}\n"
        f"👥 Referrals: {ref_stats['total']}\n"
        f"🎁 Referral Earnings: {ref_stats['earned']} credits\n"
        f"{'━'*25}\n"
        f"👑 Subscription: {sub_status}\n"
    )

    if call_logs:
        text += f"\n📋 Recent Calls:\n"
        for log in call_logs:
            text += f"  📞 {log['target_number']} | Limit:{log['call_limit']} | {log['status']}\n"

    await update.message.reply_text(text, reply_markup=user_main_menu())

profile_handler = MessageHandler(filters.Regex("^👤 My Profile$"), my_profile)
