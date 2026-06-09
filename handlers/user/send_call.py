from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters
from handlers.common import check_force_join, check_banned, check_maintenance
from services.api_client import send_call_api
from services.user_service import get_user
from database import get_connection, get_setting
from utils.helpers import is_valid_bd_phone
from utils.rate_limiter import RateLimiter
from keyboards.user import cancel_keyboard, user_main_menu
from config import CALL_LIMITS

TARGET_NUMBER, CALL_LIMIT = range(2)

free_limiter = RateLimiter(3, 60)
premium_limiter = RateLimiter(20, 60)

async def send_call_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_banned(update): return ConversationHandler.END
    if await check_maintenance(update): return ConversationHandler.END
    joined, _ = await check_force_join(update, context)
    if not joined:
        await update.message.reply_text("⚠️ Please join required channels first.")
        return ConversationHandler.END
    await update.message.reply_text("📱 Enter Target Number\nExample: 017XXXXXXXX", reply_markup=cancel_keyboard())
    return TARGET_NUMBER

async def receive_target(update: Update, context: ContextTypes.DEFAULT_TYPE):
    number = update.message.text.strip()
    if number == "🔙 Cancel":
        await update.message.reply_text("Cancelled.", reply_markup=user_main_menu())
        return ConversationHandler.END
    if not is_valid_bd_phone(number):
        await update.message.reply_text("❌ Invalid number. Try again:\nExample: 017XXXXXXXX")
        return TARGET_NUMBER
    context.user_data['target'] = number
    styles = ["primary", "danger", "success"]
    keyboard = [[{"text": str(limit), "style": styles[(limit - 1) % 3]}] for limit in CALL_LIMITS]
    keyboard.append([{"text": "🔙 Cancel", "style": "danger"}])
    await update.message.reply_text("⚡ Select Call Limit:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
    return CALL_LIMIT

async def receive_limit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "🔙 Cancel":
        await update.message.reply_text("Cancelled.", reply_markup=user_main_menu())
        return ConversationHandler.END

    try:
        limit = int(text)
        if limit not in CALL_LIMITS:
            raise ValueError
    except ValueError:
        await update.message.reply_text("Please select a valid number from the buttons.")
        return CALL_LIMIT

    user_id = update.effective_user.id
    user = get_user(user_id)
    free_call_limit = int(get_setting('free_call_limit', '5'))
    credits_per_call = int(get_setting('free_credits_per_call', '1'))

    if not user['is_premium']:
        if limit > free_call_limit:
            await update.message.reply_text(
                f"🔒 Free users can select max {free_call_limit} calls.\n\n"
                "🛒 Buy a subscription for unlimited calls!"
            )
            return CALL_LIMIT
        if user['credits'] < credits_per_call:
            await update.message.reply_text(
                f"💰 Insufficient credits!\n"
                f"You need {credits_per_call} credit(s) to send a call.\n\n"
                "Use 🎯 Daily Claim or 🎁 Redeem Code to get credits."
            )
            return ConversationHandler.END

    limiter = premium_limiter if user['is_premium'] else free_limiter
    if not await limiter.is_allowed(user_id):
        await update.message.reply_text("⏳ Too many requests. Please wait a moment.")
        return ConversationHandler.END

    target = context.user_data['target']
    await update.message.reply_text("⏳ Sending request...")

    result = await send_call_api(target, limit)
    status = "failed" if result.get("error") else "submitted"

    conn = get_connection()
    conn.execute(
        "INSERT INTO call_logs (user_id, target_number, call_limit, status) VALUES (?,?,?,?)",
        (user_id, target, limit, status)
    )
    if not user['is_premium'] and status == "submitted":
        conn.execute("UPDATE users SET credits = credits - ? WHERE user_id=?", (credits_per_call, user_id))
    conn.commit()
    conn.close()

    if status == "failed":
        await update.message.reply_text(f"❌ Request failed: {result['error']}")
    else:
        remaining = ""
        if not user['is_premium']:
            updated = get_user(user_id)
            remaining = f"\n💰 Remaining Credits: {updated['credits']}"
        await update.message.reply_text(
            f"✅ Request Submitted!\n\n"
            f"📞 Target: {target}\n"
            f"📊 Limit: {limit}\n"
            f"🕒 Time: {update.message.date.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"📌 Status: Submitted{remaining}"
        )
    await update.message.reply_text("Main menu:", reply_markup=user_main_menu())
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Cancelled.", reply_markup=user_main_menu())
    return ConversationHandler.END

send_call_conv = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex("^🚀 Send Call$"), send_call_entry)],
    states={
        TARGET_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_target)],
        CALL_LIMIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_limit)],
    },
    fallbacks=[MessageHandler(filters.Regex("^🔙 Cancel$"), cancel)],
    allow_reentry=True
)