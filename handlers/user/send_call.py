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
        await update.message.reply_text(
            f"⚠️  Please join the required channels first."
        )
        return ConversationHandler.END
    await update.message.reply_text(
        f"🚀  Send Call\n"
        f"{'─' * 28}\n\n"
        f"📱  Enter the target phone number\n\n"
        f"📌  Format: 017XXXXXXXX\n"
        f"🌏  Bangladesh numbers only",
        reply_markup=cancel_keyboard()
    )
    return TARGET_NUMBER

async def receive_target(update: Update, context: ContextTypes.DEFAULT_TYPE):
    number = update.message.text.strip()
    if number == "🔙 Cancel":
        await update.message.reply_text("❌  Cancelled.", reply_markup=user_main_menu())
        return ConversationHandler.END
    if not is_valid_bd_phone(number):
        await update.message.reply_text(
            f"❌  Invalid Number\n"
            f"{'─' * 28}\n\n"
            f"⚠️  Please enter a valid BD number\n"
            f"📌  Example: 017XXXXXXXX\n\n"
            f"Try again:"
        )
        return TARGET_NUMBER
    context.user_data['target'] = number
    styles = ["primary", "danger", "success"]
    keyboard = [[{"text": str(limit), "style": styles[(limit - 1) % 3]}] for limit in CALL_LIMITS]
    keyboard.append([{"text": "🔙 Cancel", "style": "danger"}])
    await update.message.reply_text(
        f"⚡  Select Call Limit\n"
        f"{'─' * 28}\n\n"
        f"📞  Target  :  {number}\n\n"
        f"👇  How many calls to send?",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )
    return CALL_LIMIT

async def receive_limit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "🔙 Cancel":
        await update.message.reply_text("❌  Cancelled.", reply_markup=user_main_menu())
        return ConversationHandler.END

    try:
        limit = int(text)
        if limit not in CALL_LIMITS:
            raise ValueError
    except ValueError:
        await update.message.reply_text("⚠️  Please select a number from the buttons.")
        return CALL_LIMIT

    user_id = update.effective_user.id
    user = get_user(user_id)
    free_call_limit = int(get_setting('free_call_limit', '5'))
    credits_per_call = int(get_setting('free_credits_per_call', '1'))

    if not user['is_premium']:
        if limit > free_call_limit:
            await update.message.reply_text(
                f"🔒  Limit Exceeded\n"
                f"{'─' * 28}\n\n"
                f"⚠️  Free users can send max {free_call_limit} calls\n"
                f"    per request.\n\n"
                f"{'─' * 28}\n"
                f"💡  Upgrade for unlimited calls:\n"
                f"    👑  Tap 🛒 Buy Subscription"
            )
            return CALL_LIMIT
        if user['credits'] < credits_per_call:
            await update.message.reply_text(
                f"💰  Insufficient Credits\n"
                f"{'─' * 28}\n\n"
                f"⚠️  You need {credits_per_call} credit(s) to send a call.\n"
                f"    Current balance: {user['credits']}\n\n"
                f"{'─' * 28}\n"
                f"💡  Get more credits:\n"
                f"  🎯  Daily Claim\n"
                f"  🎁  Redeem a code\n"
                f"  👥  Refer a friend",
                reply_markup=user_main_menu()
            )
            return ConversationHandler.END

    limiter = premium_limiter if user['is_premium'] else free_limiter
    if not await limiter.is_allowed(user_id):
        await update.message.reply_text(
            f"⏳  Too many requests!\n"
            f"Please wait a moment and try again."
        )
        return ConversationHandler.END

    target = context.user_data['target']
    await update.message.reply_text("⏳  Sending request, please wait...")

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
        await update.message.reply_text(
            f"❌  Request Failed\n"
            f"{'─' * 28}\n\n"
            f"⚠️  Error: {result['error']}\n\n"
            f"Please try again or contact support.",
            reply_markup=user_main_menu()
        )
    else:
        remaining = ""
        if not user['is_premium']:
            updated = get_user(user_id)
            remaining = f"\n💰  Remaining Credits  :  {updated['credits']}"
        await update.message.reply_text(
            f"✅  Request Submitted!\n"
            f"{'─' * 28}\n\n"
            f"📞  Target    :  {target}\n"
            f"📊  Calls      :  {limit}\n"
            f"🕒  Time       :  {update.message.date.strftime('%Y-%m-%d %H:%M')}\n"
            f"📌  Status    :  ✅ Submitted"
            f"{remaining}",
            reply_markup=user_main_menu()
        )
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌  Cancelled.", reply_markup=user_main_menu())
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
