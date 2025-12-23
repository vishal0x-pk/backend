from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from backend.core.database import get_db
from backend.services.loan_service import loan_service
from backend.services.transfer_service import transfer_service
from backend.schemas.schemas import LoanResponse, LoanUpdate
from backend.routes.deps import get_current_admin, get_current_approver, get_current_treasury
from backend.models.models import User
from fastapi.responses import StreamingResponse
import csv
from io import StringIO

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/loans", response_model=List[LoanResponse])
def get_all_loans(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_admin)
):
    return loan_service.get_all_loans(db)

@router.put("/loans/{loan_id}", response_model=LoanResponse)
def update_loan_status(
    loan_id: int, 
    update_data: LoanUpdate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_admin)
):
    # In a real system, we might check permissions or log who did it
    return loan_service.update_loan_status(db, loan_id, update_data)

@router.get("/analytics")
def get_analytics(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_admin)
):
    # This could be moved to a service, but for now:
    from backend.models.models import Loan, LoanStatus
    from sqlalchemy import func
    
    total_loans = db.query(Loan).count()
    approved = db.query(Loan).filter(Loan.status == LoanStatus.APPROVED).count()
    rejected = db.query(Loan).filter(Loan.status == LoanStatus.REJECTED).count()
    pending = db.query(Loan).filter(Loan.status == LoanStatus.PENDING).count()
    
    total_amount = db.query(func.sum(Loan.amount)).scalar() or 0
    
    return {
        "total": total_loans,
        "approved": approved,
        "rejected": rejected,
        "pending": pending,
        "total_amount": total_amount
    }

@router.post("/approve/{loan_id}", response_model=LoanResponse)
def approve_loan(
    loan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_approver)
):
    return loan_service.update_loan_status(db, loan_id, LoanUpdate(status="APPROVED", remarks="Approved by approver"))

@router.post("/release/{loan_id}")
def release_funds(
    loan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_treasury)
):
    result = transfer_service.release_funds(db, loan_id, current_user.id)
    return result

@router.get("/export-audit")
def export_audit(db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    from backend.models.models import TransactionLog, Loan
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["reference_id", "loan_id", "amount", "to_account", "timestamp", "hash", "prev_hash", "status"])
    txns = db.query(TransactionLog).all()
    for t in txns:
        loan = db.query(Loan).filter(Loan.id == t.loan_id).first()
        writer.writerow([t.reference_id, t.loan_id, t.amount, t.to_account, t.timestamp.isoformat(), t.hash, t.prev_hash, loan.status if loan else ""])
    output.seek(0)
    return StreamingResponse(iter([output.getvalue()]), media_type="text/csv")
