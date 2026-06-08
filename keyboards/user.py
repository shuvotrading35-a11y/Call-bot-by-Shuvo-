from telegram import ReplyKeyboardMarkup

def user_main_menu():
    keyboard = [
        ["🚀 Send Call", "👤 My Profile"],
        ["👥 Referral", "🛒 Buy Subscription"],
        ["🎁 Redeem Code"],
        ["📊 Statistics", "🎯 Daily Claim"],
        ["☎️ Support"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def cancel_keyboard():
    return ReplyKeyboardMarkup([["🔙 Cancel"]], resize_keyboard=True)

def back_to_user_menu():
    return ReplyKeyboardMarkup([["🔙 Main Menu"]], resize_keyboard=True)
