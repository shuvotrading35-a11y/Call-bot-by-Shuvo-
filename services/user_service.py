from typing import Optional
from database import get_connection
from config import DEFAULT_CREDITS

def get_or_create_user(user_id: int, username: str, first_name: str, last_name: str) -> Optional[dict]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = cur.fetchone()
    if not user:
        cur.execute(
            "INSERT INTO users (user_id, username, first_name, last_name, credits) VALUES (?,?,?,?,?)",
            (user_id, username, first_name, last_name, DEFAULT_CREDITS)
        )
        conn.commit()
        user = cur.execute("SELECT * FROM users WHERE user_id=?", (user_id,)).fetchone()
    conn.close()
    return dict(user) if user else None

def get_user(user_id: int) -> Optional[dict]:
    conn = get_connection()
    row = conn.execute("SELECT * FROM users WHERE user_id=?", (user_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def update_user(user_id: int, **kwargs):
    conn = get_connection()
    cur = conn.cursor()
    fields = ', '.join(f"{k}=?" for k in kwargs)
    values = list(kwargs.values()) + [user_id]
    cur.execute(f"UPDATE users SET {fields} WHERE user_id=?", values)
    conn.commit()
    conn.close()

def add_credits(user_id: int, amount: int):
    conn = get_connection()
    conn.execute("UPDATE users SET credits = credits + ? WHERE user_id=?", (amount, user_id))
    conn.commit()
    conn.close()

def ban_user(user_id: int, reason: str = ""):
    conn = get_connection()
    user = get_user(user_id)
    username = user['username'] if user else "unknown"
    conn.execute("UPDATE users SET is_banned=1, ban_reason=? WHERE user_id=?", (reason, user_id))
    conn.execute("INSERT OR REPLACE INTO banned_users (user_id, username, banned_by, reason) VALUES (?,?,?,?)",
                 (user_id, username, "admin", reason))
    conn.commit()
    conn.close()

def unban_user(user_id: int):
    conn = get_connection()
    conn.execute("UPDATE users SET is_banned=0, ban_reason=NULL WHERE user_id=?", (user_id,))
    conn.execute("DELETE FROM banned_users WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()
