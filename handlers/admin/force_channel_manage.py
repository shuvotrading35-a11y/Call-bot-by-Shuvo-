from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters
from handlers.common import is_admin
from database import get_connection
from keyboards.admin import admin_main_menu

ADD_CHANNEL, REMOVE_CHANNEL = range(2)

async def channel_manage_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update): return
    keyboard = [["➕ Add Channel", "➖ Remove Channel"], ["📋 List Channels", "🔙 Admin Menu"]]
    await update.message.reply_text("📢 Force Channel Management", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
    return ADD_CHANNEL

async def channel_manage_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text
    if choice == "➕ Add Channel":
        await update.message.reply_text("Send channel ID and @username separated by space:\nExample: -100123456 @channelname")
        context.user_data['ch_action'] = 'add'
        return ADD_CHANNEL
    elif choice == "➖ Remove Channel":
        await update.message.reply_text("Enter channel ID to remove:")
        context.user_data['ch_action'] = 'remove'
        return REMOVE_CHANNEL
    elif choice == "📋 List Channels":
        conn = get_connection()
        channels = conn.execute("SELECT * FROM force_channels").fetchall()
        conn.close()
        msg = "\n".join([f"{ch['channel_id']} ({ch['channel_name']})" for ch in channels]) if channels else "No channels configured."
        await update.message.reply_text(msg)
        return ConversationHandler.END
    elif choice == "🔙 Admin Menu":
        await update.message.reply_text("Admin panel", reply_markup=admin_main_menu())
        return ConversationHandler.END

async def channel_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = update.message.text.split()
    if len(data) < 2:
        await update.message.reply_text("Invalid format. Use: channel_id @username")
        return ADD_CHANNEL
    channel_id, channel_name = data[0], data[1]
    conn = get_connection()
    conn.execute("INSERT OR REPLACE INTO force_channels (channel_id, channel_name, added_by) VALUES (?,?,?)",
                 (channel_id, channel_name, update.effective_user.id))
    conn.commit()
    conn.close()
    await update.message.reply_text("Channel added.", reply_markup=admin_main_menu())
    return ConversationHandler.END

async def channel_remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    channel_id = update.message.text.strip()
    conn = get_connection()
    conn.execute("DELETE FROM force_channels WHERE channel_id=?", (channel_id,))
    conn.commit()
    conn.close()
    await update.message.reply_text("Channel removed.", reply_markup=admin_main_menu())
    return ConversationHandler.END

channel_manage_conv = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex("^📢 Force Channel$"), channel_manage_entry)],
    states={
        ADD_CHANNEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, channel_add)],
        REMOVE_CHANNEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, channel_remove)]
    },
    fallbacks=[MessageHandler(filters.Regex("^🔙 Admin Menu$"), lambda u,c: ConversationHandler.END)],
    allow_reentry=True
)
