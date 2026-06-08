from database import get_connection, get_setting

def process_referral(inviter_id: int, invited_id: int):
    conn = get_connection()
    if inviter_id == invited_id:
        conn.close()
        return False
    exists = conn.execute(
        "SELECT 1 FROM referrals WHERE inviter_id=? AND invited_id=?",
        (inviter_id, invited_id)
    ).fetchone()
    if exists:
        conn.close()
        return False
    bonus = int(get_setting('referral_bonus', '10'))
    conn.execute("INSERT INTO referrals (inviter_id, invited_id) VALUES (?,?)", (inviter_id, invited_id))
    conn.execute("UPDATE users SET credits = credits + ? WHERE user_id=?", (bonus, inviter_id))
    conn.commit()
    conn.close()
    return True

def get_referral_stats(user_id: int) -> dict:
    conn = get_connection()
    bonus = int(get_setting('referral_bonus', '10'))
    total = conn.execute("SELECT COUNT(*) FROM referrals WHERE inviter_id=?", (user_id,)).fetchone()[0]
    conn.close()
    return {"total": total, "earned": total * bonus}
