from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters
from handlers.common import is_admin
from database import get_setting, set_setting
from keyboards.admin import admin_main_menu, back_to_admin

SETTINGS_MENU, EDIT_VALUE = range(2)

SETTINGS_MAP = {
    "1": ("referral_bonus", "Referral Bonus (credits)"),
    "2": ("daily_reward_min", "Daily Reward Min"),
    "3": ("daily_reward_max", "Daily Reward Max"),
    "4": ("free_call_limit", "Free Call Limit (max calls per request)"),
    "5": ("free_rate_limit", "Free Rate Limit (requests/min)"),
    "6": ("premium_rate_limit", "Premium Rate Limit (requests/min)"),
    "7": ("maintenance_mode", "Maintenance Mode (0=off, 1=on)"),
    "8": ("api_key", "API Key"),
    "9": ("api_url", "API URL"),
    "10": ("free_credits_per_call", "Credits deducted per call (free users)"),
}

async def settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update): return
    lines = "⚙️ Bot Settings\n" + "━"*25 + "\n"
    for num, (key, label) in SETTINGS_MAP.items():
        val = get_setting(key, 'N/A')
        lines += f"{num}. {label}: {val}\n"
    lines += "\n📝 Enter number to edit (e.g. 1):"
    keyboard = [[{"text": "🔙 Admin Menu", "style": "success"}]]
    await update.message.reply_text(lines, reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
    return SETTINGS_MENU

async def select_setting(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text == "🔙 Admin Menu":
        await update.message.reply_text("Admin panel", reply_markup=admin_main_menu())
        return ConversationHandler.END
    if text not in SETTINGS_MAP:
        await update.message.reply_text("Invalid. Enter a number from the list:")
        return SETTINGS_MENU
    key, label = SETTINGS_MAP[text]
    current = get_setting(key, 'N/A')
    context.user_data['edit_setting_key'] = key
    context.user_data['edit_setting_label'] = label
    await update.message.reply_text(
        f"✏️ Editing: {label}\nCurrent Value: {current}\n\nEnter new value:",
        reply_markup=back_to_admin()
    )
    return EDIT_VALUE

async def save_setting(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text == "🔙 Admin Menu":
        await update.message.reply_text("Admin panel", reply_markup=admin_main_menu())
        return ConversationHandler.END
    key = context.user_data.get('edit_setting_key')
    label = context.user_data.get('edit_setting_label')
    set_setting(key, text)
    await update.message.reply_text(f"✅ {label} updated to: {text}", reply_markup=admin_main_menu())
    return ConversationHandler.END

settings_conv = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex("^⚙️ Settings$"), settings_menu)],
    states={
        SETTINGS_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_setting)],
        EDIT_VALUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_setting)],
    },
    fallbacks=[MessageHandler(filters.Regex("^🔙 Admin Menu$"), lambda u, c: ConversationHandler.END)],
    allow_reentry=True
)
