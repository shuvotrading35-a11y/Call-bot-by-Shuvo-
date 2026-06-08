from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from handlers.common import is_admin
from database import get_connection
from keyboards.admin import admin_main_menu

async def banned_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update): return
    conn = get_connection()
    users = conn.execute("SELECT * FROM banned_users").fetchall()
    conn.close()
    if users:
        msg = "\n".join([f"🆔 {u['user_id']} @{u['username']} - {u['reason']} ({u['ban_date']})" for u in users])
    else:
        msg = "No banned users."
    await update.message.reply_text(msg, reply_markup=admin_main_menu())

banned_users_handler = MessageHandler(filters.Regex("^🚫 Banned Users$"), banned_users)
