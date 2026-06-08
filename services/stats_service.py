from database import get_connection

def get_global_stats():
    conn = get_connection()
    total_users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    total_calls = conn.execute("SELECT COUNT(*) FROM call_logs").fetchone()[0]
    active_today = conn.execute("SELECT COUNT(DISTINCT user_id) FROM call_logs WHERE date(timestamp)=date('now','localtime')").fetchone()[0]
    total_referrals = conn.execute("SELECT COUNT(*) FROM referrals").fetchone()[0]
    conn.close()
    return {
        "total_users": total_users,
        "total_calls": total_calls,
        "active_today": active_today,
        "total_referrals": total_referrals
    }
