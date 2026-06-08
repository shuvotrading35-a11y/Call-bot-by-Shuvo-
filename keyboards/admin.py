from telegram import ReplyKeyboardMarkup

def admin_main_menu():
    keyboard = [
        ["📊 Dashboard", "👥 User List"],
        ["💰 Subscription Manage", "📢 Force Channel"],
        ["🎁 Generate Code", "⚙️ Settings"],
        ["📈 Global Stats", "🚫 Banned Users"],
        ["🌐 Broadcast", "🔓 Unban User"],
        ["☎️ Support Tickets"],
        ["👤 User Panel"]   # Admin user panel এ যেতে পারবে
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def back_to_admin():
    return ReplyKeyboardMarkup([["🔙 Admin Menu"]], resize_keyboard=True)
