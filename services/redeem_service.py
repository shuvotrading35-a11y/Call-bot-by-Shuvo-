from database import get_connection
from datetime import datetime

def redeem_code(user_id: int, code: str) -> dict:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM redeem_codes WHERE code=?", (code,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return {"success": False, "message": "❌ Invalid code."}
    row = dict(row)
    if row['expiry_date']:
        expiry = datetime.strptime(row['expiry_date'], "%Y-%m-%d")
        if datetime.now() > expiry:
            conn.close()
            return {"success": False, "message": "❌ Code expired."}
    if row['used_count'] >= row['max_uses']:
        conn.close()
        return {"success": False, "message": "❌ Code usage limit reached."}
    cur.execute("UPDATE redeem_codes SET used_count = used_count + 1 WHERE code=?", (code,))
    cur.execute("UPDATE users SET credits = credits + ? WHERE user_id=?", (row['value'], user_id))
    conn.commit()
    conn.close()
    return {"success": True, "message": f"✅ Code redeemed! {row['value']} credits added."}
