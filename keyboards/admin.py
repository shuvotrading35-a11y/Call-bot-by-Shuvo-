# keyboards.py - Primary/Success/Danger স্টাইল সংবলিত JSON রিটার্ন করে
# টেলিগ্রাম বটের জন্য ReplyKeyboardMarkup প্রয়োজন হলে আলাদা ফাংশন ব্যবহার করুন।

def admin_main_menu():
    """Admin মেনুর বাটনগুলো primary/success/danger স্টাইলসহ JSON আকারে রিটার্ন করে"""
    return [
        [{"text": "📊 Dashboard", "style": "primary"}, {"text": "👥 User List", "style": "primary"}],
        [{"text": "💰 Subscription Manage", "style": "success"}, {"text": "📢 Force Channel", "style": "success"}],
        [{"text": "🎁 Generate Code", "style": "success"}, {"text": "⚙️ Settings", "style": "primary"}],
        [{"text": "📈 Global Stats", "style": "primary"}, {"text": "🚫 Banned Users", "style": "danger"}],
        [{"text": "🌐 Broadcast", "style": "success"}, {"text": "🔓 Unban User", "style": "success"}],
        [{"text": "☎️ Support Tickets", "style": "primary"}],
        [{"text": "👤 User Panel", "style": "primary"}]
    ]

def back_to_admin():
    """Back বাটনের স্টাইল সংবলিত JSON"""
    return [{"text": "🔙 Admin Menu", "style": "primary"}]

# -----------------------------------------------------------------
# টেলিগ্রাম বটের জন্য ReplyKeyboardMarkup তৈরি করতে চাইলে নিচের ফাংশন ব্যবহার করুন
# -----------------------------------------------------------------
from telegram import ReplyKeyboardMarkup

def admin_main_menu_telegram():
    """শুধু টেক্সট নিয়ে টেলিগ্রাম কিবোর্ড তৈরি করে (স্টাইল ইগনোর করা হয়)"""
    json_data = admin_main_menu()
    keyboard = [[btn["text"] for btn in row] for row in json_data]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def back_to_admin_telegram():
    json_data = back_to_admin()
    keyboard = [[json_data[0]["text"]]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)