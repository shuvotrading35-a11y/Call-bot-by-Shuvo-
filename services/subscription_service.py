from typing import Optional
from database import get_connection
from config import PLANS
from datetime import datetime, timedelta

def get_active_subscription(user_id: int) -> Optional[dict]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM subscriptions 
        WHERE user_id=? AND active=1 AND end_date > datetime('now','localtime')
        ORDER BY end_date DESC LIMIT 1
    """, (user_id,))
    sub = cur.fetchone()
    conn.close()
    return dict(sub) if sub else None

def activate_plan(user_id: int, plan_key: str):
    plan = PLANS[plan_key]
    start = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    end = (datetime.now() + timedelta(days=plan['duration_days'])).strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO subscriptions (user_id, plan_name, plan_key, price, start_date, end_date) VALUES (?,?,?,?,?,?)",
        (user_id, plan['name'], plan_key, plan['price'], start, end)
    )
    cur.execute("UPDATE users SET is_premium=1 WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()

def deactivate_subscription(user_id: int):
    conn = get_connection()
    conn.execute("UPDATE subscriptions SET active=0 WHERE user_id=?", (user_id,))
    conn.execute("UPDATE users SET is_premium=0 WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()
