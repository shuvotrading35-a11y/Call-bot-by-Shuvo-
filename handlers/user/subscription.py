from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, MessageHandler, filters, CallbackQueryHandler
from services.user_service import get_user
from services.subscription_service import get_active_subscription
from config import PLANS
from keyboards.user import user_main_menu

async def buy_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)
    sub = get_active_subscription(user['user_id'])
    if sub:
        sub_text = f"✅  Active  ·  {sub['plan_name']}  (Expires: {sub['end_date']})"
    else:
        sub_text = "❌  No Active Subscription"

    text = (
        f"🛒  Buy Subscription\n"
        f"{'─' * 28}\n\n"
        f"💰  Balance          :  {user['credits']} credits\n"
        f"👑  Subscription   :  {sub_text}\n\n"
        f"{'─' * 28}\n"
        f"📦  Available Plans:"
    )
    keyboard = []
    for key, plan in PLANS.items():
        keyboard.append([InlineKeyboardButton(
            f"⭐  {plan['name']}  —  {plan['price']} TK", callback_data=f"sub_{key}"
        )])
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def subscription_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    plan_key = query.data.replace("sub_", "")
    if plan_key not in PLANS:
        await query.edit_message_text("❌  Invalid plan selected.")
        return
    plan = PLANS[plan_key]
    keyboard = [[
        InlineKeyboardButton("💙  bKash", callback_data=f"pay_{plan_key}_bkash"),
        InlineKeyboardButton("🧡  Nagad", callback_data=f"pay_{plan_key}_nagad")
    ]]
    await query.edit_message_text(
        f"💳  Select Payment Method\n"
        f"{'─' * 28}\n\n"
        f"📦  Plan      :  {plan['name']}\n"
        f"💵  Amount  :  {plan['price']} TK\n\n"
        f"{'─' * 28}\n"
        f"👇  Choose your payment method:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    _, plan_key, method = query.data.split("_")
    plan = PLANS[plan_key]
    user_id = update.effective_user.id
    method_icon = "💙" if method == "bkash" else "🧡"

    await query.edit_message_text(
        f"📩  Payment Instructions\n"
        f"{'─' * 28}\n\n"
        f"📦  Plan        :  {plan['name']}\n"
        f"💵  Amount    :  {plan['price']} TK\n"
        f"{method_icon}  Method    :  {method.capitalize()}\n\n"
        f"{'─' * 28}\n"
        f"✅  Send payment and forward the\n"
        f"    screenshot to the admin.\n\n"
        f"👤  Admin: @shuvo_9882\n\n"
        f"⚡  Your plan will be activated after\n"
        f"    payment is confirmed."
    )
    for admin_id in context.bot_data.get('admin_ids', []):
        await context.bot.send_message(
            admin_id,
            f"💰  New Payment Request\n"
            f"{'─' * 28}\n\n"
            f"🆔  User ID  :  {user_id}\n"
            f"📦  Plan      :  {plan['name']}\n"
            f"💵  Amount  :  {plan['price']} TK\n"
            f"{method_icon}  Method  :  {method.capitalize()}"
        )

buy_subscription_handler = MessageHandler(filters.Regex("^🛒 Buy Subscription$"), buy_subscription)
subscription_callback_handler = CallbackQueryHandler(subscription_callback, pattern="^sub_")
payment_callback_handler = CallbackQueryHandler(payment_callback, pattern="^pay_")
