from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters
from handlers.common import is_admin
from services.ticket_service import get_open_tickets, get_ticket, reply_ticket, close_ticket
from keyboards.admin import back_to_admin, admin_main_menu

TICKET_SELECT, TICKET_ACTION, REPLY_TEXT = range(3)

async def tickets_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update): return
    tickets = get_open_tickets()
    if not tickets:
        await update.message.reply_text("No open tickets.", reply_markup=admin_main_menu())
        return ConversationHandler.END
    msg = "📨 Open Tickets:\n" + "\n".join([f"#{t['ticket_id']} @{t['username']}: {t['message'][:30]}" for t in tickets])
    await update.message.reply_text(msg + "\n\nEnter ticket ID to manage:", reply_markup=back_to_admin())
    return TICKET_SELECT

async def ticket_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tid = int(update.message.text)
    ticket = get_ticket(tid)
    if not ticket:
        await update.message.reply_text("Ticket not found.")
        return TICKET_SELECT
    context.user_data['ticket_id'] = tid
    text = f"Ticket #{tid}\nFrom: @{ticket['username']} ({ticket['user_id']})\nMessage: {ticket['message']}\nStatus: {ticket['status']}"
    keyboard = [["💬 Reply", "✅ Close"], ["🔙 Admin Menu"]]
    await update.message.reply_text(text, reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
    return TICKET_ACTION

async def ticket_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    action = update.message.text
    tid = context.user_data.get('ticket_id')
    if action == "💬 Reply":
        await update.message.reply_text("Type your reply:")
        return REPLY_TEXT
    elif action == "✅ Close":
        close_ticket(tid)
        await update.message.reply_text("Ticket closed.", reply_markup=admin_main_menu())
        return ConversationHandler.END
    elif action == "🔙 Admin Menu":
        await update.message.reply_text("Admin panel", reply_markup=admin_main_menu())
        return ConversationHandler.END

async def reply_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply = update.message.text
    tid = context.user_data['ticket_id']
    reply_ticket(tid, reply)
    ticket = get_ticket(tid)
    try:
        await context.bot.send_message(ticket['user_id'], f"📨 Admin reply to your ticket:\n\n{reply}")
    except:
        pass
    await update.message.reply_text("Reply sent.", reply_markup=admin_main_menu())
    return ConversationHandler.END

support_ticket_conv = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex("^☎️ Support Tickets$"), tickets_list)],
    states={
        TICKET_SELECT: [MessageHandler(filters.TEXT & ~filters.COMMAND, ticket_select)],
        TICKET_ACTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, ticket_action)],
        REPLY_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, reply_text_handler)]
    },
    fallbacks=[MessageHandler(filters.Regex("^🔙 Admin Menu$"), lambda u,c: ConversationHandler.END)],
    allow_reentry=True
)
