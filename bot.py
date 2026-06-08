from telegram.ext import Application
from config import BOT_TOKEN, ADMIN_IDS
from database import init_db
from utils.logger import setup_logger

from handlers.start import start_handler, user_panel_handler, admin_panel_handler
from handlers.user.force_join import force_join_handler
from handlers.user.send_call import send_call_conv
from handlers.user.profile import profile_handler
from handlers.user.referral import referral_handler
from handlers.user.subscription import (
    buy_subscription_handler,
    subscription_callback_handler,
    payment_callback_handler
)
from handlers.user.redeem import redeem_conv
from handlers.user.statistics import stats_handler
from handlers.user.daily_claim import daily_handler
from handlers.user.support import support_conv

from handlers.admin.dashboard import dashboard_handler
from handlers.admin.user_list import user_list_conv
from handlers.admin.subscription_manage import sub_manage_conv
from handlers.admin.force_channel_manage import channel_manage_conv
from handlers.admin.generate_code import generate_code_conv
from handlers.admin.settings import settings_conv
from handlers.admin.global_stats import global_stats_handler
from handlers.admin.banned_users import banned_users_handler
from handlers.admin.unban_user import unban_conv
from handlers.admin.broadcast import broadcast_conv
from handlers.admin.support_tickets import support_ticket_conv

logger = setup_logger()

def main():
    init_db()
    app = Application.builder().token(BOT_TOKEN).build()
    app.bot_data['admin_ids'] = ADMIN_IDS

    # Panel switch (আগে add করতে হবে যাতে conflict না হয়)
    app.add_handler(user_panel_handler)
    app.add_handler(admin_panel_handler)

    # Start
    app.add_handler(start_handler)
    app.add_handler(force_join_handler)

    # User handlers
    app.add_handler(send_call_conv)
    app.add_handler(profile_handler)
    app.add_handler(referral_handler)
    app.add_handler(buy_subscription_handler)
    app.add_handler(subscription_callback_handler)
    app.add_handler(payment_callback_handler)
    app.add_handler(redeem_conv)
    app.add_handler(stats_handler)
    app.add_handler(daily_handler)
    app.add_handler(support_conv)

    # Admin handlers
    app.add_handler(dashboard_handler)
    app.add_handler(user_list_conv)
    app.add_handler(sub_manage_conv)
    app.add_handler(channel_manage_conv)
    app.add_handler(generate_code_conv)
    app.add_handler(settings_conv)
    app.add_handler(global_stats_handler)
    app.add_handler(banned_users_handler)
    app.add_handler(unban_conv)
    app.add_handler(broadcast_conv)
    app.add_handler(support_ticket_conv)

    async def error_handler(update, context):
        logger.error(f"Update {update} caused error {context.error}")

    app.add_error_handler(error_handler)
    logger.info("Bot started...")
    app.run_polling()

if __name__ == "__main__":
    main()
