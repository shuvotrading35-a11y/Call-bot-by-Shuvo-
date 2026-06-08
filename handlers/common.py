from telegram import Update
from telegram.ext import ContextTypes
from config import ADMIN_IDS
from database import get_connection, get_setting

async def is_admin(update: Update) -> bool:
    return update.effective_user.id in ADMIN_IDS

async def check_banned(update: Update) -> bool:
    user_id = update.effective_user.id
    if user_id in ADMIN_IDS:
        return False  # Admin কখনো banned না
    conn = get_connection()
    row = conn.execute("SELECT is_banned, ban_reason FROM users WHERE user_id=?", (user_id,)).fetchone()
    conn.close()
    if row and row['is_banned']:
        reason = row['ban_reason'] or "No reason given"
        await update.message.reply_text(
            f"🚫 You are banned from this bot.\n"
            f"📋 Reason: {reason}\n\n"
            f"Contact: @shuvo_9882"
        )
        return True
    return False

async def check_maintenance(update: Update) -> bool:
    if update.effective_user.id in ADMIN_IDS:
        return False  # Admin এর জন্য maintenance নেই
    if get_setting('maintenance_mode', '0') == '1':
        await update.message.reply_text(
            "🔧 Bot is under maintenance.\n"
            "Please try again later.\n\n"
            "Contact: @shuvo_9882"
        )
        return True
    return False

async def check_force_join(update: Update, context: ContextTypes.DEFAULT_TYPE) -> tuple:
    """Returns (joined: bool, not_joined_channels: list)."""
    user_id = update.effective_user.id

    # Admin সবসময় bypass করবে
    if user_id in ADMIN_IDS:
        return True, []

    conn = get_connection()
    channels = conn.execute("SELECT channel_id, channel_name, invite_link FROM force_channels").fetchall()
    conn.close()

    if not channels:
        return True, []

    not_joined = []
    for row in channels:
        ch_id = row['channel_id']
        ch_name = row['channel_name']
        invite_link = row['invite_link'] if row['invite_link'] else None

        try:
            member = await context.bot.get_chat_member(chat_id=ch_id, user_id=user_id)
            if member.status in ['left', 'kicked', 'banned']:
                not_joined.append((ch_id, ch_name, invite_link))
        except Exception:
            not_joined.append((ch_id, ch_name, invite_link))

    return len(not_joined) == 0, not_joined