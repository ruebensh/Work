"""Payments endpoints: add a payment, list payments per student."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Payment, Student
from app.schemas import PaymentCreate, PaymentOut

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("", response_model=PaymentOut, status_code=201)
def create_payment(payload: PaymentCreate, db: Session = Depends(get_db)):
    if not db.get(Student, payload.student_id):
        raise HTTPException(404, "student not found")
    payment = Payment(**payload.model_dump())
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment


@router.get("", response_model=list[PaymentOut])
def list_payments(
    student_id: int = Query(..., description="filter by student"),
    db: Session = Depends(get_db),
):
    if not db.get(Student, student_id):
        raise HTTPException(404, "student not found")
    return (
        db.query(Payment)
        .filter(Payment.student_id == student_id)
        .order_by(Payment.paid_at.desc(), Payment.id.desc())
        .all()
    )
