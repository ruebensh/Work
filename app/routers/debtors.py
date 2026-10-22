"""GET /debtors?month=YYYY-MM endpoint."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas import DebtorOut
from app.auth import require_auth
from app.services.debtors import get_debtors

router = APIRouter(tags=["debtors"], dependencies=[Depends(require_auth)])


@router.get("/debtors", response_model=list[DebtorOut])
def list_debtors(
    month: str = Query(..., pattern=r"^\d{4}-\d{2}$", description="YYYY-MM"),
    db: Session = Depends(get_db),
):
    try:
        return get_debtors(db, month)
    except ValueError as exc:
        raise HTTPException(400, str(exc))
