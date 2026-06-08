from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from handlers.common import is_admin
from database import get_connection
from keyboards.admin import admin_main_menu

async def dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update): return
    conn = get_connection()
    total_users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    total_calls = conn.execute("SELECT COUNT(*) FROM call_logs").fetchone()[0]
    active_today = conn.execute(
        "SELECT COUNT(DISTINCT user_id) FROM call_logs WHERE date(timestamp)=date('now','localtime')"
    ).fetchone()[0]
    premium_users = conn.execute("SELECT COUNT(*) FROM users WHERE is_premium=1").fetchone()[0]
    banned_users = conn.execute("SELECT COUNT(*) FROM users WHERE is_banned=1").fetchone()[0]
    open_tickets = conn.execute("SELECT COUNT(*) FROM support_tickets WHERE status='open'").fetchone()[0]
    new_users_today = conn.execute(
        "SELECT COUNT(*) FROM users WHERE date(join_date)=date('now','localtime')"
    ).fetchone()[0]
    # Revenue = sum of all active subscription prices
    revenue = conn.execute(
        "SELECT COALESCE(SUM(price), 0) FROM subscriptions"
    ).fetchone()[0]
    conn.close()

    text = (
        f"📊 Admin Dashboard\n"
        f"{'━'*25}\n"
        f"👥 Total Users: {total_users}\n"
        f"🆕 New Today: {new_users_today}\n"
        f"👑 Premium Users: {premium_users}\n"
        f"🚫 Banned Users: {banned_users}\n"
        f"{'━'*25}\n"
        f"📞 Total Calls: {total_calls}\n"
        f"🔥 Active Today: {active_today}\n"
        f"{'━'*25}\n"
        f"💰 Total Revenue: {revenue} TK\n"
        f"🎫 Open Tickets: {open_tickets}\n"
        f"{'━'*25}"
    )
    await update.message.reply_text(text, reply_markup=admin_main_menu())

dashboard_handler = MessageHandler(filters.Regex("^📊 Dashboard$"), dashboard)
