from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters
from services.redeem_service import redeem_code
from keyboards.user import cancel_keyboard, user_main_menu

REDEEM_CODE = 1

async def redeem_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎁 Enter your redeem code:", reply_markup=cancel_keyboard())
    return REDEEM_CODE

async def redeem_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    code = update.message.text.strip()
    if code == "🔙 Cancel":
        await update.message.reply_text("Cancelled.", reply_markup=user_main_menu())
        return ConversationHandler.END
    result = redeem_code(update.effective_user.id, code)
    await update.message.reply_text(result['message'], reply_markup=user_main_menu())
    return ConversationHandler.END

redeem_conv = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex("^🎁 Redeem Code$"), redeem_entry)],
    states={
        REDEEM_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, redeem_check)]
    },
    fallbacks=[MessageHandler(filters.Regex("^🔙 Cancel$"), redeem_check)],
    allow_reentry=True
)
