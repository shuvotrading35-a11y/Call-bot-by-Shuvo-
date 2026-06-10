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

    joined, not_joined = await check_force_join(update, context)
    if not joined:
        await update.message.reply_text(
            f"🚫  Access Restricted\n"
            f"{'─' * 28}\n\n"
            f"You must join {len(not_joined)} required channel(s)\n"
            f"before using this bot.\n\n"
            f"👇  Join below, then tap ✅ Check Again",
            reply_markup=build_join_buttons(not_joined)
        )
        return

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
            f"👑  Admin Panel\n"
            f"{'─' * 28}\n\n"
            f"Welcome back, {user.first_name}!\n\n"
            f"🔐  Name  :  {user.first_name}\n"
            f"🆔  ID      :  {user.id}\n"
            f"🛡️  Role   :  Administrator\n\n"
            f"{'─' * 28}\n"
            f"🛠  Dev: @shuvo_9882",
            reply_markup=admin_main_menu()
        )
    else:
        await update.message.reply_text(
            f"🚀  Welcome to Call Sender Bot!\n"
            f"{'─' * 28}\n\n"
            f"Hey {user.first_name}, glad you're here! 👋\n\n"
            f"⚡  What you can do:\n"
            f"  📞  Send calls to any BD number\n"
            f"  🎯  Claim daily bonus credits\n"
            f"  👥  Earn credits by referring friends\n"
            f"  🎁  Redeem codes for free credits\n\n"
            f"{'─' * 28}\n"
            f"🛠  Dev: @shuvo_9882",
            reply_markup=user_main_menu()
        )

async def switch_to_user_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id not in ADMIN_IDS: return
    await update.message.reply_text(
        f"👤  User Panel\n"
        f"{'─' * 28}\n\n"
        f"✅  You are now in User Mode\n"
        f"🔐  Tap 👑 Admin Panel to switch back",
        reply_markup=user_main_menu(is_admin=True)
    )

async def switch_to_admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS: return
    await update.message.reply_text(
        f"👑  Admin Panel\n"
        f"{'─' * 28}\n\n"
        f"✅  Switched back to Admin Mode",
        reply_markup=admin_main_menu()
    )

start_handler = CommandHandler("start", start)
user_panel_handler = MessageHandler(filters.Regex("^👤 User Panel$"), switch_to_user_panel)
admin_panel_handler = MessageHandler(filters.Regex("^👑 Admin Panel$"), switch_to_admin_panel)