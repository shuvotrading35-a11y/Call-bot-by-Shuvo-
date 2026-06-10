from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from database import get_connection, get_setting
from utils.helpers import can_claim_daily
from keyboards.user import user_main_menu
from handlers.common import check_banned, check_maintenance
import random

async def daily_claim(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_banned(update): return
    if await check_maintenance(update): return
    user_id = update.effective_user.id
    conn = get_connection()
    last = conn.execute(
        "SELECT claim_date FROM daily_rewards WHERE user_id=? ORDER BY claim_date DESC LIMIT 1",
        (user_id,)
    ).fetchone()
    if last and not can_claim_daily(last['claim_date']):
        conn.close()
        await update.message.reply_text(
            f"⏳  Already Claimed!\n"
            f"{'─' * 28}\n\n"
            f"You've already collected today's bonus.\n\n"
            f"🔄  Come back in 24 hours for your\n"
            f"    next reward!",
            reply_markup=user_main_menu()
        )
        return

    reward_min = int(get_setting('daily_reward_min', '1'))
    reward_max = int(get_setting('daily_reward_max', '10'))
    reward = random.randint(reward_min, reward_max)
    conn.execute(
        "INSERT INTO daily_rewards (user_id, claim_date, reward) VALUES (?, date('now','localtime'), ?)",
        (user_id, reward)
    )
    conn.execute("UPDATE users SET credits = credits + ? WHERE user_id=?", (reward, user_id))
    conn.commit()
    updated = conn.execute("SELECT credits FROM users WHERE user_id=?", (user_id,)).fetchone()
    conn.close()

    await update.message.reply_text(
        f"🎉  Daily Bonus Claimed!\n"
        f"{'─' * 28}\n\n"
        f"🎁  Today's Reward  :  +{reward} credits\n"
        f"💰  Total Credits    :  {updated['credits']}\n\n"
        f"{'─' * 28}\n"
        f"⏰  Next claim available in 24 hours",
        reply_markup=user_main_menu()
    )

daily_handler = MessageHandler(filters.Regex("^🎯 Daily Claim$"), daily_claim)