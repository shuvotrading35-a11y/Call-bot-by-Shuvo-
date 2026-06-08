from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, MessageHandler, filters, CallbackQueryHandler
from services.user_service import get_user
from services.subscription_service import get_active_subscription, activate_plan
from config import PLANS
from keyboards.user import user_main_menu

async def buy_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)
    sub = get_active_subscription(user['user_id'])
    status = "🟢 Active" if sub else "🔴 Inactive"
    text = (
        f"💰 Your Wallet\n💳 Balance: {user['credits']} credits\n"
        f"👑 Subscription Status: {status}\n\n"
        "🛒 Subscription Plans:"
    )
    keyboard = []
    for key, plan in PLANS.items():
        keyboard.append([InlineKeyboardButton(f"{plan['name']} - {plan['price']} TK", callback_data=f"sub_{key}")])
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def subscription_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    plan_key = query.data.replace("sub_", "")
    if plan_key not in PLANS:
        await query.edit_message_text("Invalid plan.")
        return
    plan = PLANS[plan_key]
    keyboard = [
        [InlineKeyboardButton("bKash", callback_data=f"pay_{plan_key}_bkash"),
         InlineKeyboardButton("Nagad", callback_data=f"pay_{plan_key}_nagad")]
    ]
    await query.edit_message_text(
        f"Selected: {plan['name']}\nPrice: {plan['price']} TK\n\nSelect payment method:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    _, plan_key, method = query.data.split("_")
    plan = PLANS[plan_key]
    user_id = update.effective_user.id
    await query.edit_message_text(
        f"📩 Please contact admin to complete payment of {plan['price']} TK via {method}.\n\n"
        "Admin: @shuvo_9882\n\nAfter payment, admin will activate your plan."
    )
    for admin_id in context.bot_data.get('admin_ids', []):
        await context.bot.send_message(admin_id, f"User {user_id} wants to buy {plan['name']} via {method}.")

buy_subscription_handler = MessageHandler(filters.Regex("^🛒 Buy Subscription$"), buy_subscription)
subscription_callback_handler = CallbackQueryHandler(subscription_callback, pattern="^sub_")
payment_callback_handler = CallbackQueryHandler(payment_callback, pattern="^pay_")
