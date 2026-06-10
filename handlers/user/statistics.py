from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from services.stats_service import get_global_stats
from keyboards.user import user_main_menu

async def statistics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    stats = get_global_stats()
    await update.message.reply_text(
        f"📊  Bot Statistics\n"
        f"{'─' * 28}\n\n"
        f"👥  Total Users          :  {stats['total_users']}\n"
        f"📞  Total Calls Sent    :  {stats['total_calls']}\n"
        f"🔥  Active Today         :  {stats['active_today']}\n"
        f"🤝  Total Referrals     :  {stats['total_referrals']}\n\n"
        f"{'─' * 28}\n"
        f"🛠  Dev: @shuvo_9882",
        reply_markup=user_main_menu()
    )

stats_handler = MessageHandler(filters.Regex("^📊 Statistics$"), statistics)
