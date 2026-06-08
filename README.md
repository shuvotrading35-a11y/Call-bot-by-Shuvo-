# Call Sender Bot

A premium Telegram bot for call sending requests with subscription management, referral system, and admin panel.

## Setup
1. Clone repository.
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `.env` and fill your bot token and admin IDs.
4. Run `python bot.py`

## Features
- User panel: call requests, profile, referral, subscription, redeem, daily claim, support
- Admin panel: dashboard, user management, subscription activation, force channel, code generator, broadcast, tickets
- SQLite database, rate limiting, force join

## Project Structure
```
call_sender_bot/
├── bot.py
├── config.py
├── database.py
├── requirements.txt
├── .env
├── utils/
│   ├── helpers.py
│   ├── logger.py
│   └── rate_limiter.py
├── services/
│   ├── api_client.py
│   ├── user_service.py
│   ├── subscription_service.py
│   ├── referral_service.py
│   ├── redeem_service.py
│   ├── ticket_service.py
│   └── stats_service.py
├── keyboards/
│   ├── user.py
│   └── admin.py
└── handlers/
    ├── common.py
    ├── start.py
    ├── user/
    │   ├── force_join.py
    │   ├── send_call.py
    │   ├── profile.py
    │   ├── referral.py
    │   ├── subscription.py
    │   ├── redeem.py
    │   ├── statistics.py
    │   ├── daily_claim.py
    │   └── support.py
    └── admin/
        ├── dashboard.py
        ├── user_list.py
        ├── subscription_manage.py
        ├── force_channel_manage.py
        ├── generate_code.py
        ├── settings.py
        ├── global_stats.py
        ├── banned_users.py
        ├── unban_user.py
        ├── broadcast.py
        └── support_tickets.py
```

## Developer
👨‍💻 Shuvo  
☎️ Support: @shuvo_9882
