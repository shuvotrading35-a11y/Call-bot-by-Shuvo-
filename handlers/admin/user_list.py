from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters
from handlers.common import is_admin
from services.user_service import get_user, ban_user, unban_user, update_user
from keyboards.admin import back_to_admin, admin_main_menu

SEARCH, SHOW_USER, EDIT_CREDITS = range(3)

async def user_list_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update): return
    await update.message.reply_text("Enter user ID to search:", reply_markup=back_to_admin())
    return SEARCH

async def search_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "🔙 Admin Menu":
        await update.message.reply_text("Admin panel", reply_markup=admin_main_menu())
        return ConversationHandler.END
    try:
        user_id = int(text)
    except:
        await update.message.reply_text("Invalid ID. Enter a number:")
        return SEARCH
    user = get_user(user_id)
    if not user:
        await update.message.reply_text("User not found.")
        return SEARCH
    context.user_data['edit_user'] = user_id
    info = (
        f"👤 User: {user['username'] or user['first_name']}\n"
        f"🆔 ID: {user['user_id']}\n"
        f"💰 Credits: {user['credits']}\n"
        f"🔒 Banned: {'Yes' if user['is_banned'] else 'No'}"
    )
    keyboard = [
        [{"text": "✏️ Edit Credits", "style": "success"}, {"text": "🚫 Ban User", "style": "danger"}],
        [{"text": "🔓 Unban", "style": "primary"}, {"text": "🔙 Admin Menu", "style": "success"}],
    ]
    await update.message.reply_text(info, reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
    return SHOW_USER

async def show_user_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    option = update.message.text
    user_id = context.user_data.get('edit_user')
    if option == "✏️ Edit Credits":
        await update.message.reply_text("Enter new credit amount:")
        return EDIT_CREDITS
    elif option == "🚫 Ban User":
        ban_user(user_id, "Admin ban")
        await update.message.reply_text("✅ User banned.", reply_markup=admin_main_menu())
        return ConversationHandler.END
    elif option == "🔓 Unban":
        unban_user(user_id)
        await update.message.reply_text("✅ User unbanned.", reply_markup=admin_main_menu())
        return ConversationHandler.END
    elif option == "🔙 Admin Menu":
        await update.message.reply_text("Admin panel", reply_markup=admin_main_menu())
        return ConversationHandler.END
    return SHOW_USER

async def edit_credits(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = context.user_data.get('edit_user')
    try:
        new_credits = int(update.message.text)
    except:
        await update.message.reply_text("Invalid number. Enter credits:")
        return EDIT_CREDITS
    update_user(user_id, credits=new_credits)
    await update.message.reply_text(f"✅ Credits updated to {new_credits}.", reply_markup=admin_main_menu())
    return ConversationHandler.END

user_list_conv = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex("^👥 User List$"), user_list_entry)],
    states={
        SEARCH: [MessageHandler(filters.TEXT & ~filters.COMMAND, search_user)],
        SHOW_USER: [MessageHandler(filters.TEXT & ~filters.COMMAND, show_user_action)],
        EDIT_CREDITS: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_credits)],
    },
    fallbacks=[MessageHandler(filters.Regex("^🔙 Admin Menu$"), lambda u, c: ConversationHandler.END)],
    allow_reentry=True
)
