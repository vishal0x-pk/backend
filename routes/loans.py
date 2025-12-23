from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.core.database import get_db
from backend.services.loan_service import loan_service
from backend.schemas.schemas import LoanCreate, LoanResponse
from backend.models.models import User
from backend.routes.deps import get_current_active_farmer

router = APIRouter(prefix="/loans", tags=["Loans"])

@router.post("/", response_model=LoanResponse)
def apply_for_loan(
    loan: LoanCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_active_farmer)
):
    return loan_service.create_loan(db, loan, current_user.id)

@router.get("/my-loans", response_model=List[LoanResponse])
def get_my_loans(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_active_farmer)
):
    return loan_service.get_loans_by_farmer(db, current_user.id)
