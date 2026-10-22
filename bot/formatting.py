"""Pure text formatting/parsing helpers for bot replies (unit-testable)."""
from datetime import date


import html

def _escape(text: str) -> str:
    return html.escape(text)
def format_amount(value: int) -> str:
    """400000 -> '400 000' (thin-space style grouping, so'm added by callers)."""
    return f"{value:,}".replace(",", " ")


def current_month(today: date | None = None) -> str:
    today = today or date.today()
    return f"{today.year:04d}-{today.month:02d}"


def format_debtors(month: str, debtors: list[dict]) -> str:
    """Generate HTML text for debtors list.
    All user‑provided values are escaped to avoid Telegram HTML parse errors.
    """
    if not debtors:
        return f"✅ {month}: qarzdorlar yo'q — hamma to'lagan!"
    total = sum(d["debt"] for d in debtors)
    lines = [f"📊 <b>Dolzniklar — {month}</b> ({len(debtors)} ta):", ""]
    for i, d in enumerate(debtors, 1):
        lines.append(
            f"{i}. <b>{_escape(d['name'])}</b> (id={d['student_id']}, {_escape(d['group_name'])})\n"
            f"   To'lagan: {format_amount(d['paid_in_month'])} / {format_amount(d['monthly_amount'])} so'm"
            f" — qarz: <b>{format_amount(d['debt'])} so'm</b>"
        )
    lines.append("")
    lines.append(f"Jami qarz: <b>{format_amount(total)} so'm</b>")
    return "\n".join(lines)
    """/debt javob matni."""
    if not debtors:
        return f"✅ {month}: qarzdorlar yo'q — hamma to'lagan!"
    total = sum(d["debt"] for d in debtors)
    lines = [f"📊 <b>Dolzniklar — {month}</b> ({len(debtors)} ta):", ""]
    for i, d in enumerate(debtors, 1):
        lines.append(
            f"{i}. <b>{d['name']}</b> (id={d['student_id']}, {d['group_name']})\n"
            f"   To'lagan: {format_amount(d['paid_in_month'])} / {format_amount(d['monthly_amount'])} so'm"
            f" — qarz: <b>{format_amount(d['debt'])} so'm</b>"
        )
    lines.append("")
    lines.append(f"Jami qarz: <b>{format_amount(total)} so'm</b>")
    return "\n".join(lines)


def parse_pay_args(text: str) -> tuple[int, int] | str:
    """/pay <student_id> <amount> -> (id, amount). Returns error text on failure."""
    parts = text.split()
    if len(parts) != 3:
        return "Ishlatish: /pay <student_id> <summa>. Masalan: /pay 3 200000"
    try:
        student_id = int(parts[1])
        amount = int(parts[2])
    except ValueError:
        return "student_id va summa butun son bo'lishi kerak."
    if amount <= 0:
        return "Summa musbat son bo'lishi kerak."
    return (student_id, amount)


def format_payment_ok(student_name: str, amount: int, paid_on: date) -> str:
    """Return HTML‑escaped success message for a payment."""
    return (
        f"✅ <b>{_escape(student_name)}</b> ga {format_amount(amount)} so'm to'lov qo'shildi "
        f"(sana: {paid_on.isoformat()})."
    )
    return (
        f"✅ <b>{student_name}</b> ga {format_amount(amount)} so'm to'lov qo'shildi "
        f"(sana: {paid_on.isoformat()})."
    )


def format_students(students: list) -> str:
    """Return HTML‑escaped list of students.
    Each student's name and group are escaped to avoid Telegram HTML errors.
    """
    if not students:
        return "O'quvchilar yo'q."
    lines = ["👥 <b>O'quvchilar:</b>", ""]
    for s in students:
        lines.append(
            f"id={s.id} — <b>{_escape(s.name)}</b> ({_escape(s.group_name)}), "
            f"{format_amount(s.monthly_amount)} so'm oyiga"
        )
    return "\n".join(lines)
    """/students javobi — id, name, group, monthly."""
    if not students:
        return "O'quvchilar yo'q."
    lines = ["👥 <b>O'quvchilar:</b>", ""]
    for s in students:
        lines.append(
            f"id={s.id} — <b>{s.name}</b> ({s.group_name}), "
            f"{format_amount(s.monthly_amount)} so'm oyiga"
        )
    return "\n".join(lines)
