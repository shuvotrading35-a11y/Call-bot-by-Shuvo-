from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CallbackQueryHandler
from handlers.common import check_force_join
from keyboards.user import user_main_menu

async def check_join_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    joined, not_joined = await check_force_join(update, context)
    if joined:
        await query.edit_message_text("✅ Channels joined! You can now use the bot.")
        await query.message.reply_text("Main menu:", reply_markup=user_main_menu())
    else:
        buttons = []
        for ch_id, ch_name in not_joined:
            url = f"https://t.me/{ch_name.replace('@', '')}"
            buttons.append([InlineKeyboardButton(f"✅ Join {ch_name}", url=url)])
        buttons.append([InlineKeyboardButton("🔄 Check Again", callback_data="check_join")])
        await query.edit_message_text(
            "⚠️ You haven't joined all channels yet.",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

force_join_handler = CallbackQueryHandler(check_join_callback, pattern="^check_join$")
