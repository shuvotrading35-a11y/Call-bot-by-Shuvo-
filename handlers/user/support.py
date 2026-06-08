from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters
from services.ticket_service import create_ticket
from keyboards.user import cancel_keyboard, user_main_menu

SUPPORT_MESSAGE = 1

async def support_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("☎️ Describe your issue (type your message):", reply_markup=cancel_keyboard())
    return SUPPORT_MESSAGE

async def support_receive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text
    if message == "🔙 Cancel":
        await update.message.reply_text("Cancelled.", reply_markup=user_main_menu())
        return ConversationHandler.END
    user = update.effective_user
    create_ticket(user.id, user.username, message)
    await update.message.reply_text("✅ Support ticket created. Admin will reply soon.", reply_markup=user_main_menu())
    for admin_id in context.bot_data.get('admin_ids', []):
        await context.bot.send_message(admin_id, f"📨 New ticket from @{user.username} ({user.id})\nMessage: {message}")
    return ConversationHandler.END

support_conv = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex("^☎️ Support$"), support_entry)],
    states={
        SUPPORT_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, support_receive)]
    },
    fallbacks=[MessageHandler(filters.Regex("^🔙 Cancel$"), support_receive)],
    allow_reentry=True
)
