from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
from services.user_service import get_or_create_user
from services.referral_service import process_referral
from keyboards.user import user_main_menu
from keyboards.admin import admin_main_menu
from handlers.common import check_force_join, check_banned, check_maintenance
from handlers.user.force_join import build_join_buttons
from config import ADMIN_IDS

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    get_or_create_user(user.id, user.username, user.first_name, user.last_name)

    if await check_banned(update): return
    if await check_maintenance(update): return

    # Force join check (admin bypass করবে automatically)
    joined, not_joined = await check_force_join(update, context)
    if not joined:
        await update.message.reply_text(
            f"⚠️ Bot ব্যবহার করতে নিচের {len(not_joined)}টি channel join করুন:",
            reply_markup=build_join_buttons(not_joined)
        )
        return

    # Referral process
    if context.args and context.args[0].startswith("ref_"):
        try:
            ref_id = int(context.args[0].split("_")[1])
            if ref_id != user.id:
                process_referral(ref_id, user.id)
        except:
            pass

    is_admin = user.id in ADMIN_IDS
    if is_admin:
        await update.message.reply_text(
            f"👑 Welcome Admin {user.first_name}!\n\n"
            f"Developed by 👨‍💻 Shuvo\nSupport: @shuvo_9882",
            reply_markup=admin_main_menu()
        )
    else:
        await update.message.reply_text(
            f"Welcome to Call Sender Bot, {user.first_name}!\n\n"
            f"Developed by 👨‍💻 Shuvo\nSupport: @shuvo_9882",
            reply_markup=user_main_menu()
        )

# Admin → User Panel switch
async def switch_to_user_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        return
    await update.message.reply_text(
        "👤 User Panel এ স্বাগতম!\n"
        "আপনি এখন user হিসেবে bot ব্যবহার করতে পারবেন।",
        reply_markup=user_main_menu(is_admin=True)
    )

# User Panel → Admin Panel switch
async def switch_to_admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        return
    await update.message.reply_text(
        "👑 Admin Panel এ ফিরে এসেছেন।",
        reply_markup=admin_main_menu()
    )

start_handler = CommandHandler("start", start)
user_panel_handler = MessageHandler(filters.Regex("^👤 User Panel$"), switch_to_user_panel)
admin_panel_handler = MessageHandler(filters.Regex("^👑 Admin Panel$"), switch_to_admin_panel)
