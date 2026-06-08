from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CommandHandler
from services.user_service import get_or_create_user
from services.referral_service import process_referral
from keyboards.user import user_main_menu
from keyboards.admin import admin_main_menu
from handlers.common import check_force_join, check_banned, check_maintenance
from config import ADMIN_IDS

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    get_or_create_user(user.id, user.username, user.first_name, user.last_name)

    if await check_banned(update): return
    if await check_maintenance(update): return

    # Check force join
    joined, not_joined = await check_force_join(update, context)
    if not joined:
        buttons = []
        for ch_id, ch_name in not_joined:
            url = f"https://t.me/{ch_name.replace('@', '')}"
            buttons.append([InlineKeyboardButton(f"✅ Join {ch_name}", url=url)])
        buttons.append([InlineKeyboardButton("🔄 Check Again", callback_data="check_join")])
        await update.message.reply_text(
            "⚠️ Please join all required channels to use the bot.",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return

    # Process referral
    if context.args and context.args[0].startswith("ref_"):
        try:
            ref_id = int(context.args[0].split("_")[1])
            if ref_id != user.id:
                process_referral(ref_id, user.id)
        except:
            pass

    # Send appropriate menu
    if user.id in ADMIN_IDS:
        await update.message.reply_text(
            f"👑 Welcome Admin {user.first_name}!\n\nDeveloped by 👨‍💻 Shuvo\nSupport: @shuvo_9882",
            reply_markup=admin_main_menu()
        )
    else:
        await update.message.reply_text(
            f"Welcome to Call Sender Bot, {user.first_name}!\n\nDeveloped by 👨‍💻 Shuvo\nSupport: @shuvo_9882",
            reply_markup=user_main_menu()
        )

start_handler = CommandHandler("start", start)
