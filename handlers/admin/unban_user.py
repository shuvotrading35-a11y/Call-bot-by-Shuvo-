from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters
from handlers.common import is_admin
from services.user_service import unban_user, get_user
from database import get_connection
from keyboards.admin import back_to_admin, admin_main_menu

CHOOSE_METHOD, GET_INPUT = range(2)

async def unban_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update): return
    keyboard = [["🆔 Unban by User ID", "👤 Unban by Username"], ["📋 View Banned Users", "🔙 Admin Menu"]]
    await update.message.reply_text("🔓 Unban User", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
    return CHOOSE_METHOD

async def choose_method(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text
    if choice == "🆔 Unban by User ID":
        context.user_data['unban_method'] = 'id'
        await update.message.reply_text("Enter user ID:", reply_markup=back_to_admin())
        return GET_INPUT
    elif choice == "👤 Unban by Username":
        context.user_data['unban_method'] = 'username'
        await update.message.reply_text("Enter username (without @):", reply_markup=back_to_admin())
        return GET_INPUT
    elif choice == "📋 View Banned Users":
        conn = get_connection()
        users = conn.execute("SELECT * FROM banned_users ORDER BY ban_date DESC").fetchall()
        conn.close()
        if not users:
            await update.message.reply_text("No banned users.", reply_markup=admin_main_menu())
        else:
            msg = "🚫 Banned Users:\n" + "━"*20 + "\n"
            for u in users:
                msg += f"🆔 {u['user_id']} @{u['username']}\n📋 {u['reason']}\n📅 {u['ban_date']}\n\n"
            await update.message.reply_text(msg, reply_markup=admin_main_menu())
        return ConversationHandler.END
    elif choice == "🔙 Admin Menu":
        await update.message.reply_text("Admin panel", reply_markup=admin_main_menu())
        return ConversationHandler.END
    return CHOOSE_METHOD

async def process_unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text == "🔙 Admin Menu":
        await update.message.reply_text("Admin panel", reply_markup=admin_main_menu())
        return ConversationHandler.END

    method = context.user_data.get('unban_method')
    user_id = None

    if method == 'id':
        try:
            user_id = int(text)
        except:
            await update.message.reply_text("Invalid ID. Enter a number:")
            return GET_INPUT
    elif method == 'username':
        username = text.replace('@', '')
        conn = get_connection()
        row = conn.execute("SELECT user_id FROM users WHERE username=?", (username,)).fetchone()
        conn.close()
        if not row:
            await update.message.reply_text(f"User @{username} not found.")
            return GET_INPUT
        user_id = row['user_id']

    user = get_user(user_id)
    if not user:
        await update.message.reply_text("User not found in database.")
        return GET_INPUT

    if not user['is_banned']:
        await update.message.reply_text(f"User {user_id} is not banned.")
        return ConversationHandler.END

    unban_user(user_id)
    await update.message.reply_text(
        f"✅ User has been successfully unbanned and can now use the bot again.\n\n"
        f"🆔 ID: {user_id}\n"
        f"👤 Username: @{user['username'] or 'N/A'}",
        reply_markup=admin_main_menu()
    )
    # Notify user
    try:
        await context.bot.send_message(user_id, "✅ You have been unbanned! You can now use the bot again.")
    except:
        pass
    return ConversationHandler.END

unban_conv = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex("^🔓 Unban User$"), unban_entry)],
    states={
        CHOOSE_METHOD: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_method)],
        GET_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_unban)],
    },
    fallbacks=[MessageHandler(filters.Regex("^🔙 Admin Menu$"), lambda u, c: ConversationHandler.END)],
    allow_reentry=True
)
