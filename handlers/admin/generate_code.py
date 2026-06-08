from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters
from handlers.common import is_admin
from database import get_connection
from keyboards.admin import back_to_admin, admin_main_menu

CODE_VALUE, EXPIRY, USAGE = range(3)

async def gen_code_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update): return
    await update.message.reply_text("Enter code value (credits):", reply_markup=back_to_admin())
    return CODE_VALUE

async def code_value(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['code_val'] = int(update.message.text)
    await update.message.reply_text("Expiry date (YYYY-MM-DD) or 'none':")
    return EXPIRY

async def code_expiry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['code_exp'] = update.message.text if update.message.text.lower() != 'none' else None
    await update.message.reply_text("Maximum uses:")
    return USAGE

async def code_usage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    max_uses = int(update.message.text)
    code = f"CS{update.effective_user.id}{max_uses}{context.user_data['code_val']}"
    conn = get_connection()
    conn.execute("INSERT INTO redeem_codes (code, value, max_uses, expiry_date, created_by) VALUES (?,?,?,?,?)",
                 (code, context.user_data['code_val'], max_uses, context.user_data['code_exp'], update.effective_user.id))
    conn.commit()
    conn.close()
    await update.message.reply_text(
        f"🎁 Code generated: `{code}`\nValue: {context.user_data['code_val']}\nExpiry: {context.user_data['code_exp']}\nUses: {max_uses}",
        reply_markup=admin_main_menu(), parse_mode="Markdown"
    )
    return ConversationHandler.END

generate_code_conv = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex("^🎁 Generate Code$"), gen_code_entry)],
    states={
        CODE_VALUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, code_value)],
        EXPIRY: [MessageHandler(filters.TEXT & ~filters.COMMAND, code_expiry)],
        USAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, code_usage)]
    },
    fallbacks=[MessageHandler(filters.Regex("^🔙 Admin Menu$"), lambda u,c: ConversationHandler.END)],
    allow_reentry=True
)
