from database import get_connection

def create_ticket(user_id: int, username: str, message: str):
    conn = get_connection()
    conn.execute("INSERT INTO support_tickets (user_id, username, message) VALUES (?,?,?)",
                 (user_id, username, message))
    conn.commit()
    conn.close()

def get_open_tickets():
    conn = get_connection()
    tickets = conn.execute("SELECT * FROM support_tickets WHERE status='open' ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(t) for t in tickets]

def get_ticket(ticket_id: int):
    conn = get_connection()
    ticket = conn.execute("SELECT * FROM support_tickets WHERE ticket_id=?", (ticket_id,)).fetchone()
    conn.close()
    return dict(ticket) if ticket else None

def close_ticket(ticket_id: int):
    conn = get_connection()
    conn.execute("UPDATE support_tickets SET status='closed' WHERE ticket_id=?", (ticket_id,))
    conn.commit()
    conn.close()

def reply_ticket(ticket_id: int, reply: str):
    conn = get_connection()
    conn.execute("UPDATE support_tickets SET admin_response=?, status='answered' WHERE ticket_id=?", (reply, ticket_id))
    conn.commit()
    conn.close()
