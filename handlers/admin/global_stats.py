from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from handlers.common import is_admin
from database import get_connection
from keyboards.admin import admin_main_menu

async def global_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update): return
    conn = get_connection()

    today_calls = conn.execute("SELECT COUNT(*) FROM call_logs WHERE date(timestamp)=date('now','localtime')").fetchone()[0]
    yesterday_calls = conn.execute("SELECT COUNT(*) FROM call_logs WHERE date(timestamp)=date('now','localtime','-1 day')").fetchone()[0]
    week_calls = conn.execute("SELECT COUNT(*) FROM call_logs WHERE timestamp >= datetime('now','-7 days')").fetchone()[0]
    month_calls = conn.execute("SELECT COUNT(*) FROM call_logs WHERE timestamp >= datetime('now','-30 days')").fetchone()[0]

    active_today = conn.execute("SELECT COUNT(DISTINCT user_id) FROM call_logs WHERE date(timestamp)=date('now','localtime')").fetchone()[0]
    active_week = conn.execute("SELECT COUNT(DISTINCT user_id) FROM call_logs WHERE timestamp >= datetime('now','-7 days')").fetchone()[0]

    new_today = conn.execute("SELECT COUNT(*) FROM users WHERE date(join_date)=date('now','localtime')").fetchone()[0]
    new_week = conn.execute("SELECT COUNT(*) FROM users WHERE join_date >= datetime('now','-7 days')").fetchone()[0]
    new_month = conn.execute("SELECT COUNT(*) FROM users WHERE join_date >= datetime('now','-30 days')").fetchone()[0]

    total_referrals = conn.execute("SELECT COUNT(*) FROM referrals").fetchone()[0]
    total_premium = conn.execute("SELECT COUNT(*) FROM users WHERE is_premium=1").fetchone()[0]
    total_revenue = conn.execute("SELECT COALESCE(SUM(price),0) FROM subscriptions").fetchone()[0]

    # Top callers today
    top_callers = conn.execute("""
        SELECT u.username, u.first_name, COUNT(*) as cnt 
        FROM call_logs cl JOIN users u ON cl.user_id=u.user_id
        WHERE date(cl.timestamp)=date('now','localtime')
        GROUP BY cl.user_id ORDER BY cnt DESC LIMIT 3
    """).fetchall()

    conn.close()

    growth = ""
    if yesterday_calls > 0:
        pct = ((today_calls - yesterday_calls) / yesterday_calls) * 100
        arrow = "📈" if pct >= 0 else "📉"
        growth = f"{arrow} vs Yesterday: {pct:+.1f}%"
    else:
        growth = "📊 First day of data"

    top_text = ""
    for i, row in enumerate(top_callers, 1):
        name = row['username'] or row['first_name'] or "Unknown"
        top_text += f"  {i}. @{name} — {row['cnt']} calls\n"

    text = (
        f"📈 Global Statistics\n"
        f"{'━'*25}\n"
        f"📞 Daily Activity\n"
        f"  Today: {today_calls} calls\n"
        f"  Yesterday: {yesterday_calls} calls\n"
        f"  {growth}\n"
        f"{'━'*25}\n"
        f"📅 Total Requests\n"
        f"  This Week: {week_calls}\n"
        f"  This Month: {month_calls}\n"
        f"{'━'*25}\n"
        f"👥 Growth Analytics\n"
        f"  New Today: {new_today}\n"
        f"  New This Week: {new_week}\n"
        f"  New This Month: {new_month}\n"
        f"{'━'*25}\n"
        f"🔥 Active Users\n"
        f"  Today: {active_today}\n"
        f"  This Week: {active_week}\n"
        f"{'━'*25}\n"
        f"💰 Revenue: {total_revenue} TK\n"
        f"👑 Premium Users: {total_premium}\n"
        f"👥 Total Referrals: {total_referrals}\n"
    )

    if top_text:
        text += f"{'━'*25}\n🏆 Top Callers Today:\n{top_text}"

    await update.message.reply_text(text, reply_markup=admin_main_menu())

global_stats_handler = MessageHandler(filters.Regex("^📈 Global Stats$"), global_stats)
