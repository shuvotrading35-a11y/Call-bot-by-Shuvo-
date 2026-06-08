from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from services.stats_service import get_global_stats
from keyboards.user import user_main_menu

async def statistics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    stats = get_global_stats()
    text = (
        f"📊 Bot Statistics\n\n"
        f"👥 Total Users: {stats['total_users']}\n"
        f"📞 Total Calls Sent: {stats['total_calls']}\n"
        f"🔥 Active Users Today: {stats['active_today']}\n"
        f"👥 Total Referrals: {stats['total_referrals']}"
    )
    await update.message.reply_text(text, reply_markup=user_main_menu())

stats_handler = MessageHandler(filters.Regex("^📊 Statistics$"), statistics)
