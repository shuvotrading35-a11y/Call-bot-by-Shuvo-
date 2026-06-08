from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CallbackQueryHandler
from handlers.common import check_force_join
from keyboards.user import user_main_menu
from keyboards.admin import admin_main_menu
from config import ADMIN_IDS

def build_join_buttons(not_joined: list) -> InlineKeyboardMarkup:
    buttons = []
    for ch_id, ch_name, invite_link in not_joined:
        url = invite_link or f"https://t.me/{ch_name.replace('@', '')}"
        buttons.append([InlineKeyboardButton(f"✅ Join {ch_name}", url=url)])
    buttons.append([InlineKeyboardButton("🔄 Check Again", callback_data="check_join")])
    return InlineKeyboardMarkup(buttons)

async def check_join_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    joined, not_joined = await check_force_join(update, context)
    if joined:
        await query.edit_message_text("✅ সব channel join করা হয়েছে! Bot ব্যবহার করতে পারবেন।")
        user_id = update.effective_user.id
        menu = admin_main_menu() if user_id in ADMIN_IDS else user_main_menu()
        await query.message.reply_text("Main menu:", reply_markup=menu)
    else:
        await query.edit_message_text(
            f"⚠️ এখনো {len(not_joined)}টি channel join করেননি।",
            reply_markup=build_join_buttons(not_joined)
        )

force_join_handler = CallbackQueryHandler(check_join_callback, pattern="^check_join$")
