from telegram import ReplyKeyboardMarkup

def admin_main_menu():
    keyboard = [
        [{"text": "📊 Dashboard",           "style": "primary"}, {"text": "👥 User List",       "style": "primary"}],
        [{"text": "💰 Subscription Manage", "style": "success"}, {"text": "📢 Force Channel",   "style": "success"}],
        [{"text": "🎁 Generate Code",       "style": "success"}, {"text": "⚙️ Settings",        "style": "primary"}],
        [{"text": "📈 Global Stats",        "style": "primary"}, {"text": "🚫 Banned Users",    "style": "danger"} ],
        [{"text": "🌐 Broadcast",           "style": "success"}, {"text": "🔓 Unban User",      "style": "danger"} ],
        [{"text": "☎️ Support Tickets", "style": "primary"},
    {"text": "👤 User Panel", "style": "primary"}],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, is_persistent=True)

def back_to_admin():
    return ReplyKeyboardMarkup(
        [[{"text": "🔙 Admin Menu", "style": "success"}]],
        resize_keyboard=True
    )
