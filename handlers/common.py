from telegram import Update
from telegram.ext import ContextTypes
from config import ADMIN_IDS
from database import get_connection, get_setting

async def is_admin(update: Update) -> bool:
    return update.effective_user.id in ADMIN_IDS

async def check_banned(update: Update) -> bool:
    """Returns True if user is banned."""
    user_id = update.effective_user.id
    conn = get_connection()
    row = conn.execute("SELECT is_banned FROM users WHERE user_id=?", (user_id,)).fetchone()
    conn.close()
    if row and row['is_banned']:
        conn2 = get_connection()
        reason = conn2.execute("SELECT reason FROM banned_users WHERE user_id=?", (user_id,)).fetchone()
        conn2.close()
        reason_text = reason['reason'] if reason else "No reason given"
        await update.message.reply_text(
            f"🚫 You have been banned from using this bot.\n📋 Reason: {reason_text}\n\n"
            "Contact admin: @shuvo_9882"
        )
        return True
    return False

async def check_maintenance(update: Update) -> bool:
    """Returns True if maintenance mode is on (and user is not admin)."""
    if update.effective_user.id in ADMIN_IDS:
        return False
    if get_setting('maintenance_mode', '0') == '1':
        await update.message.reply_text(
            "🔧 Bot is currently under maintenance.\n"
            "Please try again later.\n\n"
            "Contact admin: @shuvo_9882"
        )
        return True
    return False

async def check_force_join(update: Update, context: ContextTypes.DEFAULT_TYPE) -> tuple:
    """Returns (joined: bool, not_joined_channels: list)."""
    user_id = update.effective_user.id
    conn = get_connection()
    channels = conn.execute("SELECT channel_id, channel_name FROM force_channels").fetchall()
    conn.close()
    not_joined = []
    for row in channels:
        ch_id, ch_name = row['channel_id'], row['channel_name']
        try:
            member = await context.bot.get_chat_member(chat_id=ch_id, user_id=user_id)
            if member.status in ['left', 'kicked', 'banned']:
                not_joined.append((ch_id, ch_name))
        except Exception:
            not_joined.append((ch_id, ch_name))
    return len(not_joined) == 0, not_joined
