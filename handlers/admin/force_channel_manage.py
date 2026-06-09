from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters
from handlers.common import is_admin
from database import get_connection
from keyboards.admin import admin_main_menu

MENU, WAITING_ADD, WAITING_REMOVE = range(3)

async def channel_manage_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update): return
    keyboard = [
        [{"text": "➕ Add Channel", "style": "success"}, {"text": "➖ Remove Channel", "style": "danger"}],
        [{"text": "📋 List Channels", "style": "primary"}, {"text": "🔙 Admin Menu", "style": "success"}],
    ]
    await update.message.reply_text(
        "📢 Force Channel Management",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )
    return MENU

async def channel_menu_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text

    if choice == "➕ Add Channel":
        await update.message.reply_text(
            "📌 Channel যোগ করার নিয়ম:\n\n"
            "Public Channel হলে:\n"
            "  শুধু @username লিখো\n"
            "  Example: @mychannel\n\n"
            "Private Channel হলে:\n"
            "  channel_id আর invite_link দুটো দাও\n"
            "  Example: -1001234567890 https://t.me/+xxxxx\n\n"
            "⚠️ Bot কে channel এ admin করতে হবে।"
        )
        return WAITING_ADD

    elif choice == "➖ Remove Channel":
        conn = get_connection()
        channels = conn.execute("SELECT channel_id, channel_name FROM force_channels").fetchall()
        conn.close()
        if not channels:
            await update.message.reply_text("No force channels added yet.", reply_markup=admin_main_menu())
            return ConversationHandler.END
        msg = "📋 Current Channels:\n\n"
        for ch in channels:
            msg += f"• {ch['channel_name']} (ID: {ch['channel_id']})\n"
        msg += "\nChannel ID লিখো remove করতে:"
        await update.message.reply_text(msg)
        return WAITING_REMOVE

    elif choice == "📋 List Channels":
        conn = get_connection()
        channels = conn.execute("SELECT * FROM force_channels").fetchall()
        conn.close()
        if not channels:
            await update.message.reply_text("⚠️ No force channels configured.", reply_markup=admin_main_menu())
        else:
            msg = "📢 Force Channels:\n" + "━"*25 + "\n"
            for i, ch in enumerate(channels, 1):
                msg += (
                    f"{i}. {ch['channel_name']}\n"
                    f"   🆔 ID: {ch['channel_id']}\n"
                    f"   🔗 Link: {ch['invite_link'] or 'Public'}\n\n"
                )
            await update.message.reply_text(msg, reply_markup=admin_main_menu())
        return ConversationHandler.END

    elif choice == "🔙 Admin Menu":
        await update.message.reply_text("Admin panel", reply_markup=admin_main_menu())
        return ConversationHandler.END

    return MENU

async def channel_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text == "🔙 Admin Menu":
        await update.message.reply_text("Admin panel", reply_markup=admin_main_menu())
        return ConversationHandler.END

    parts = text.split()

    if len(parts) == 1 and parts[0].startswith("@"):
        username = parts[0]
        invite_link = f"https://t.me/{username.replace('@', '')}"
        channel_id = username
        channel_name = username
        try:
            chat = await context.bot.get_chat(chat_id=username)
            channel_id = str(chat.id)
            channel_name = f"@{chat.username}" if chat.username else chat.title
        except Exception as e:
            await update.message.reply_text(
                f"❌ Channel খুঁজে পাওয়া যায়নি: {e}\n\n"
                "নিশ্চিত করো:\n• Bot টি channel এ admin আছে\n• Username সঠিক"
            )
            return WAITING_ADD

    elif len(parts) == 2:
        channel_id = parts[0]
        invite_link = parts[1]
        try:
            chat = await context.bot.get_chat(chat_id=channel_id)
            channel_name = chat.title or channel_id
        except Exception as e:
            await update.message.reply_text(
                f"❌ Channel verify করা যায়নি: {e}\n\nBot কি channel এ admin আছে?"
            )
            return WAITING_ADD
    else:
        await update.message.reply_text(
            "❌ Format ভুল!\n\nPublic: @channelname\nPrivate: -1001234567890 https://t.me/+xxxxx"
        )
        return WAITING_ADD

    conn = get_connection()
    conn.execute(
        "INSERT OR REPLACE INTO force_channels (channel_id, channel_name, invite_link, added_by) VALUES (?,?,?,?)",
        (channel_id, channel_name, invite_link, update.effective_user.id)
    )
    conn.commit()
    conn.close()

    await update.message.reply_text(
        f"✅ Channel যোগ হয়েছে!\n\n"
        f"📛 Name: {channel_name}\n🆔 ID: {channel_id}\n🔗 Link: {invite_link}",
        reply_markup=admin_main_menu()
    )
    return ConversationHandler.END

async def channel_remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text == "🔙 Admin Menu":
        await update.message.reply_text("Admin panel", reply_markup=admin_main_menu())
        return ConversationHandler.END

    conn = get_connection()
    row = conn.execute("SELECT channel_name FROM force_channels WHERE channel_id=?", (text,)).fetchone()
    if not row:
        row = conn.execute("SELECT channel_id, channel_name FROM force_channels WHERE channel_name=?", (text,)).fetchone()
        if row:
            text = row['channel_id']

    if not row:
        await update.message.reply_text("❌ Channel পাওয়া যায়নি। সঠিক ID দাও।")
        conn.close()
        return WAITING_REMOVE

    conn.execute("DELETE FROM force_channels WHERE channel_id=?", (text,))
    conn.commit()
    conn.close()
    await update.message.reply_text("✅ Channel remove হয়েছে।", reply_markup=admin_main_menu())
    return ConversationHandler.END

channel_manage_conv = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex("^📢 Force Channel$"), channel_manage_entry)],
    states={
        MENU:          [MessageHandler(filters.TEXT & ~filters.COMMAND, channel_menu_choice)],
        WAITING_ADD:   [MessageHandler(filters.TEXT & ~filters.COMMAND, channel_add)],
        WAITING_REMOVE:[MessageHandler(filters.TEXT & ~filters.COMMAND, channel_remove)],
    },
    fallbacks=[MessageHandler(filters.Regex("^🔙 Admin Menu$"), lambda u, c: ConversationHandler.END)],
    allow_reentry=True
)
