from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.core.database import get_db
from backend.models.models import TransactionLog, Loan, LoanStatus

router = APIRouter(prefix="/public", tags=["Transparency"])

@router.get("/summary")
def summary(db: Session = Depends(get_db)):
    total_transfers = db.query(func.count(TransactionLog.id)).scalar() or 0
    total_amount = db.query(func.sum(TransactionLog.amount)).scalar() or 0
    approved_loans = db.query(Loan).filter(Loan.status == LoanStatus.APPROVED).count()
    return {
        "transfers": total_transfers,
        "total_amount": total_amount,
        "approved_loans": approved_loans
    }

@router.get("/transactions")
def transactions(db: Session = Depends(get_db), limit: int = 50):
    txns = db.query(TransactionLog).order_by(TransactionLog.id.desc()).limit(limit).all()
    return [
        {
            "reference_id": t.reference_id,
            "amount": t.amount,
            "to_account": t.to_account,
            "timestamp": t.timestamp.isoformat(),
            "hash": t.hash,
            "prev_hash": t.prev_hash
        } for t in txns
    ]
