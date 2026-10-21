"""Debtors report: who paid less than their monthly fee for a given month."""
import calendar
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Payment, Student


def month_bounds(month: str) -> tuple[date, date]:
    """'YYYY-MM' -> (first_day, last_day) of that month."""
    year_str, month_str = month.split("-")
    year, m = int(year_str), int(month_str)
    if not 1 <= m <= 12:
        raise ValueError("month must be 1..12")
    return date(year, m, 1), date(year, m, calendar.monthrange(year, m)[1])


def get_debtors(db: Session, month: str) -> list[dict]:
    """Students whose payments within `month` are less than their monthly fee.

    A student who paid nothing at all in the month is a debtor for the full
    monthly amount. Overpayers are excluded.
    """
    start, end = month_bounds(month)

    paid = (
        select(
            Payment.student_id,
            func.coalesce(func.sum(Payment.amount), 0).label("paid_in_month"),
        )
        .where(Payment.paid_at >= start, Payment.paid_at <= end)
        .group_by(Payment.student_id)
        .subquery()
    )

    rows = db.execute(
        select(
            Student.id,
            Student.name,
            Student.phone,
            Student.group_name,
            Student.monthly_amount,
            func.coalesce(paid.c.paid_in_month, 0).label("paid_in_month"),
        )
        .outerjoin(paid, paid.c.student_id == Student.id)
        .order_by(Student.id)
    ).all()

    debtors = []
    for r in rows:
        debt = r.monthly_amount - r.paid_in_month
        if debt > 0:
            debtors.append(
                {
                    "student_id": r.id,
                    "name": r.name,
                    "phone": r.phone,
                    "group_name": r.group_name,
                    "monthly_amount": r.monthly_amount,
                    "paid_in_month": r.paid_in_month,
                    "debt": debt,
                }
            )
    return debtors
