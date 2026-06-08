from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from services.referral_service import get_referral_stats
from utils.helpers import generate_referral_link
from keyboards.user import user_main_menu

async def referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    bot_username = context.bot.username
    ref_link = generate_referral_link(bot_username, user_id)
    stats = get_referral_stats(user_id)
    text = (
        f"👥 Total Referrals: {stats['total']}\n"
        f"🎁 Earned Credits: {stats['earned']}\n\n"
        f"🔗 Your referral link:\n{ref_link}"
    )
    await update.message.reply_text(text, reply_markup=user_main_menu())

referral_handler = MessageHandler(filters.Regex("^👥 Referral$"), referral)
