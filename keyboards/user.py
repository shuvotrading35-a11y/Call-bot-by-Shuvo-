from telegram import ReplyKeyboardMarkup

def user_main_menu(is_admin: bool = False):
    keyboard = [
        ["🚀 Send Call", "👤 My Profile"],
        ["👥 Referral", "🛒 Buy Subscription"],
        ["🎁 Redeem Code", "🎯 Daily Claim"],   # একই row তে
        ["📊 Statistics", "☎️ Support"]         # পাশাপাশি
    ]
    if is_admin:
        keyboard.append(["👑 Admin Panel"])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def cancel_keyboard():
    return ReplyKeyboardMarkup([["🔙 Cancel"]], resize_keyboard=True)

def back_to_user_menu():
    return ReplyKeyboardMarkup([["🔙 Main Menu"]], resize_keyboard=True)