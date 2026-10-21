"""Telegram bot command handlers (Part 2-A).

Talks to the DB directly through the same SQLAlchemy models/services as the
API — one source of truth for both interfaces.
"""
from datetime import date

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from app.db import SessionLocal
from app.models import Payment, Student
from app.services.debtors import get_debtors
from bot.formatting import (
    current_month,
    format_debtors,
    format_payment_ok,
    format_students,
    parse_pay_args,
)

HELP_TEXT = (
    " <b>Uch markazi hisobi</b>\n\n"
    "/debt — joriy oy dolzniklari\n"
    "/pay &lt;student_id&gt; &lt;summa&gt; — to'lov qo'shish, masalan: /pay 3 200000\n"
    "/students — o'quvchilar ro'yxati (id'lar bilan)\n"
    "/help — yordam"
)


def _authorized(update: Update) -> bool:
    """Optional allow-list: TELEGRAM_ALLOWED_CHAT_IDS='123,456' (empty = open)."""
    from app.config import TELEGRAM_ALLOWED_CHAT_IDS

    if not TELEGRAM_ALLOWED_CHAT_IDS:
        return True
    allowed = {int(x) for x in TELEGRAM_ALLOWED_CHAT_IDS.split(",") if x.strip()}
    chat = update.effective_chat
    return bool(chat and chat.id in allowed)


async def _reply(update: Update, text: str) -> None:
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _authorized(update):
        return
    await _reply(update, HELP_TEXT)


async def cmd_debt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Joriy oy dolzniklari: oylik summasidan kam to'laganlar + qarzi."""
    if not _authorized(update):
        return
    month = current_month()
    db = SessionLocal()
    try:
        debtors = get_debtors(db, month)
    finally:
        db.close()
    await _reply(update, format_debtors(month, debtors))


async def cmd_pay(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/pay &lt;student_id&gt; &lt;summa&gt; — bugungi sana bilan to'lov qo'shish."""
    if not _authorized(update):
        return
    parsed = parse_pay_args(update.message.text or "")
    if isinstance(parsed, str):  # error message
        await _reply(update, f"⚠️ {parsed}")
        return
    student_id, amount = parsed
    db = SessionLocal()
    try:
        student = db.get(Student, student_id)
        if not student:
            await _reply(update, f"⚠️ id={student_id} bilan o'quvchi topilmadi. /students ni ko'ring.")
            return
        paid_on = date.today()
        db.add(Payment(student_id=student.id, amount=amount, paid_at=paid_on))
        db.commit()
        await _reply(update, format_payment_ok(student.name, amount, paid_on))
    finally:
        db.close()


async def cmd_students(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _authorized(update):
        return
    db = SessionLocal()
    try:
        students = db.query(Student).order_by(Student.id).all()
    finally:
        db.close()
    await _reply(update, format_students(students))


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _authorized(update):
        return
    await _reply(update, HELP_TEXT)


async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.logger.exception("Handler raised an exception", exc_info=context.error)
