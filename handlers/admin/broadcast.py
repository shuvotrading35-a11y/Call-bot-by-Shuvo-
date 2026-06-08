from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters
from handlers.common import is_admin
from database import get_connection
from keyboards.admin import back_to_admin, admin_main_menu

TARGET_SELECT, BROADCAST_MSG = range(2)

async def broadcast_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update): return
    keyboard = [["All Users", "Premium Users"], ["🔙 Admin Menu"]]
    await update.message.reply_text("Select target:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
    return TARGET_SELECT

async def broadcast_target(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text
    if choice == "🔙 Admin Menu":
        await update.message.reply_text("Admin panel", reply_markup=admin_main_menu())
        return ConversationHandler.END
    if choice not in ["All Users", "Premium Users"]:
        await update.message.reply_text("Please select a valid option.")
        return TARGET_SELECT
    context.user_data['broadcast_target'] = choice
    await update.message.reply_text("Now send the message (text, photo, video, document).", reply_markup=back_to_admin())
    return BROADCAST_MSG

async def broadcast_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = context.user_data.get('broadcast_target')
    conn = get_connection()
    if target == "All Users":
        users = conn.execute("SELECT user_id FROM users WHERE is_banned=0").fetchall()
    elif target == "Premium Users":
        users = conn.execute("SELECT user_id FROM users WHERE is_premium=1 AND is_banned=0").fetchall()
    else:
        conn.close()
        return ConversationHandler.END
    conn.close()

    success = 0
    failed = 0
    for row in users:
        try:
            await update.message.copy(chat_id=row[0])
            success += 1
        except Exception:
            failed += 1

    await update.message.reply_text(
        f"📢 Broadcast done!\n✅ Sent: {success}\n❌ Failed: {failed}",
        reply_markup=admin_main_menu()
    )
    conn = get_connection()
    conn.execute("INSERT INTO broadcast_logs (admin_id, message_text, target_type) VALUES (?,?,?)",
                 (update.effective_user.id, update.message.text or update.message.caption or "[media]", target))
    conn.commit()
    conn.close()
    return ConversationHandler.END

broadcast_conv = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex("^🌐 Broadcast$"), broadcast_entry)],
    states={
        TARGET_SELECT: [MessageHandler(filters.TEXT & ~filters.COMMAND, broadcast_target)],
        BROADCAST_MSG: [MessageHandler(filters.ALL & ~filters.COMMAND, broadcast_send)]
    },
    fallbacks=[MessageHandler(filters.Regex("^🔙 Admin Menu$"), lambda u, c: ConversationHandler.END)],
    allow_reentry=True
)
