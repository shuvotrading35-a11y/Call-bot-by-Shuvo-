from telegram import ReplyKeyboardMarkup

def user_main_menu(is_admin: bool = False):
    keyboard = [
        [{"text": "🚀 Send Call", "style": "danger"},       {"text": "👤 My Profile",      "style": "primary"}],
        [{"text": "👥 Referral", "style": "primary"},        {"text": "🛒 Buy Subscription", "style": "success"}],
        [{"text": "🎁 Redeem Code", "style": "success"},  	 {"text": "🎯 Daily Claim",      "style": "success"}],
        [{"text": "📊 Statistics", "style": "primary"},      {"text": "☎️ Support", "style": "danger"}],
       
    ]
    if is_admin:
        keyboard.append([{"text": "👑 Admin Panel", "style": "danger"}])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, is_persistent=True)

def cancel_keyboard():
    return ReplyKeyboardMarkup(
        [[{"text": "🔙 Cancel", "style": "danger"}]],
        resize_keyboard=True
    )

def back_to_user_menu():
    return ReplyKeyboardMarkup(
        [[{"text": "🔙 Main Menu", "style": "success"}]],
        resize_keyboard=True
    )
