import sqlite3
import os
from config import DB_PATH

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.executescript('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        last_name TEXT,
        join_date TEXT DEFAULT (datetime('now','localtime')),
        credits INTEGER DEFAULT 5,
        is_premium INTEGER DEFAULT 0,
        is_banned INTEGER DEFAULT 0,
        ban_reason TEXT
    );

    CREATE TABLE IF NOT EXISTS subscriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        plan_name TEXT,
        plan_key TEXT,
        price INTEGER DEFAULT 0,
        start_date TEXT DEFAULT (datetime('now','localtime')),
        end_date TEXT,
        active INTEGER DEFAULT 1,
        FOREIGN KEY(user_id) REFERENCES users(user_id)
    );

    CREATE TABLE IF NOT EXISTS referrals (
        inviter_id INTEGER,
        invited_id INTEGER,
        reward_claimed INTEGER DEFAULT 0,
        date TEXT DEFAULT (datetime('now','localtime')),
        PRIMARY KEY (inviter_id, invited_id),
        FOREIGN KEY(inviter_id) REFERENCES users(user_id),
        FOREIGN KEY(invited_id) REFERENCES users(user_id)
    );

    CREATE TABLE IF NOT EXISTS redeem_codes (
        code TEXT PRIMARY KEY,
        value INTEGER,
        max_uses INTEGER,
        used_count INTEGER DEFAULT 0,
        expiry_date TEXT,
        created_by INTEGER
    );

    CREATE TABLE IF NOT EXISTS daily_rewards (
        user_id INTEGER,
        claim_date TEXT,
        reward INTEGER,
        PRIMARY KEY (user_id, claim_date),
        FOREIGN KEY(user_id) REFERENCES users(user_id)
    );

    CREATE TABLE IF NOT EXISTS force_channels (
        channel_id TEXT PRIMARY KEY,
        channel_name TEXT,
        added_by INTEGER,
        added_date TEXT DEFAULT (datetime('now','localtime'))
    );

    CREATE TABLE IF NOT EXISTS support_tickets (
        ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        username TEXT,
        message TEXT,
        status TEXT DEFAULT 'open',
        created_at TEXT DEFAULT (datetime('now','localtime')),
        admin_response TEXT,
        FOREIGN KEY(user_id) REFERENCES users(user_id)
    );

    CREATE TABLE IF NOT EXISTS broadcast_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        admin_id INTEGER,
        message_text TEXT,
        target_type TEXT,
        sent_at TEXT DEFAULT (datetime('now','localtime'))
    );

    CREATE TABLE IF NOT EXISTS banned_users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        banned_by INTEGER,
        ban_date TEXT DEFAULT (datetime('now','localtime')),
        reason TEXT,
        FOREIGN KEY(user_id) REFERENCES users(user_id)
    );

    CREATE TABLE IF NOT EXISTS call_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        target_number TEXT,
        call_limit INTEGER,
        timestamp TEXT DEFAULT (datetime('now','localtime')),
        status TEXT DEFAULT 'submitted',
        FOREIGN KEY(user_id) REFERENCES users(user_id)
    );

    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    );
    ''')

    # Default settings
    defaults = [
        ('referral_bonus', '10'),
        ('daily_reward_min', '1'),
        ('daily_reward_max', '10'),
        ('free_call_limit', '5'),
        ('free_rate_limit', '3'),
        ('premium_rate_limit', '20'),
        ('maintenance_mode', '0'),
        ('api_key', 'Extremeuser'),
        ('api_url', 'https://rakabro.top/api.php'),
        ('free_credits_per_call', '1'),
    ]
    for key, value in defaults:
        cur.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?,?)", (key, value))

    conn.commit()
    conn.close()

def get_setting(key: str, default: str = '') -> str:
    conn = get_connection()
    row = conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    conn.close()
    return row[0] if row else default

def set_setting(key: str, value: str):
    conn = get_connection()
    conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?,?)", (key, value))
    conn.commit()
    conn.close()
