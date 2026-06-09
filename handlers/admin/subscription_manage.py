from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters
from handlers.common import is_admin
from services.subscription_service import activate_plan, deactivate_subscription
from config import PLANS
from keyboards.admin import admin_main_menu

CHOICE, GET_USER_ID, GET_PLAN = range(3)

async def sub_manage_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update): return
    keyboard = [
        [{"text": "➕ Activate Subscription", "style": "success"}, {"text": "➖ Remove Subscription", "style": "danger"}],
        [{"text": "📋 View History", "style": "primary"}, {"text": "🔙 Admin Menu", "style": "success"}],
    ]
    await update.message.reply_text("💰 Subscription Management", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
    return CHOICE

async def sub_manage_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text
    if choice == "➕ Activate Subscription":
        context.user_data['sub_action'] = 'activate'
        await update.message.reply_text("Enter user ID:")
        return GET_USER_ID
    elif choice == "➖ Remove Subscription":
        context.user_data['sub_action'] = 'remove'
        await update.message.reply_text("Enter user ID:")
        return GET_USER_ID
    elif choice == "📋 View History":
        from database import get_connection
        conn = get_connection()
        subs = conn.execute("SELECT * FROM subscriptions ORDER BY start_date DESC LIMIT 10").fetchall()
        conn.close()
        if not subs:
            await update.message.reply_text("No subscriptions yet.")
        else:
            msg = "\n".join([f"User {s['user_id']}: {s['plan_name']} (until {s['end_date']})" for s in subs])
            await update.message.reply_text(msg)
        return ConversationHandler.END
    elif choice == "🔙 Admin Menu":
        await update.message.reply_text("Admin panel", reply_markup=admin_main_menu())
        return ConversationHandler.END
    return CHOICE

async def get_user_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = int(update.message.text)
    except:
        await update.message.reply_text("Invalid ID. Enter a number:")
        return GET_USER_ID
    context.user_data['sub_user'] = user_id
    action = context.user_data.get('sub_action')
    if action == 'activate':
        plans_text = "\n".join([f"{k} — {PLANS[k]['name']} ({PLANS[k]['price']} TK)" for k in PLANS])
        await update.message.reply_text(f"Select plan key:\n\n{plans_text}")
        return GET_PLAN
    elif action == 'remove':
        deactivate_subscription(user_id)
        await update.message.reply_text("✅ Subscription removed.", reply_markup=admin_main_menu())
        return ConversationHandler.END

async def get_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    plan_key = update.message.text.strip()
    user_id = context.user_data.get('sub_user')
    if plan_key not in PLANS:
        await update.message.reply_text(f"Invalid key. Choose from: {', '.join(PLANS.keys())}")
        return GET_PLAN
    activate_plan(user_id, plan_key)
    await update.message.reply_text(f"✅ {PLANS[plan_key]['name']} activated for user {user_id}.", reply_markup=admin_main_menu())
    return ConversationHandler.END

sub_manage_conv = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex("^💰 Subscription Manage$"), sub_manage_entry)],
    states={
        CHOICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, sub_manage_choice)],
        GET_USER_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_user_id)],
        GET_PLAN: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_plan)],
    },
    fallbacks=[MessageHandler(filters.Regex("^🔙 Admin Menu$"), lambda u, c: ConversationHandler.END)],
    allow_reentry=True
)
