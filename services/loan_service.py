from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from backend.models.models import Loan, User, LoanStatus
from backend.schemas.schemas import LoanCreate, LoanUpdate
from backend.services.decision_engine import decision_engine
from datetime import datetime
from backend.core.config import settings
from datetime import timedelta

class LoanService:
    def create_loan(self, db: Session, loan_data: LoanCreate, farmer_id: int):
        # Fetch farmer data for ML
        farmer = db.query(User).filter(User.id == farmer_id).first()
        farmer_data = {
            "credit_score": farmer.credit_score,
            "balance": farmer.balance
        } if farmer else {}

        # 1. Run Automated Decision Engine
        data_dict = loan_data.dict()
        status_result, reason, confidence = decision_engine.decide_loan(data_dict, farmer_data)
        
        rate = settings.GOV_INTEREST_RATE
        n = 12 if loan_data.repayment_frequency == "monthly" else 4 if loan_data.repayment_frequency == "quarterly" else 2
        r = rate / n
        emi = (loan_data.amount * r) if r == 0 else (loan_data.amount * r) / (1 - (1 + r) ** (-n))
        next_due = datetime.utcnow() + (timedelta(days=30) if loan_data.repayment_frequency == "monthly" else timedelta(days=90) if loan_data.repayment_frequency == "quarterly" else timedelta(days=180))
        
        # 2. Save to DB
        new_loan = Loan(
            farmer_id=farmer_id,
            amount=loan_data.amount,
            purpose=loan_data.purpose,
            land_size=loan_data.land_size,
            crop_type=loan_data.crop_type,
            annual_income=loan_data.annual_income,
            location=loan_data.location,
            repayment_frequency=loan_data.repayment_frequency,
            emi_amount=emi,
            next_due_date=next_due,
            status=status_result,
            decision_reason=reason,
            confidence_score=confidence,
            created_at=datetime.utcnow()
        )
        db.add(new_loan)
        db.commit()
        db.refresh(new_loan)
        return new_loan

    def get_loans_by_farmer(self, db: Session, farmer_id: int):
        return db.query(Loan).filter(Loan.farmer_id == farmer_id).all()

    def get_all_loans(self, db: Session):
        return db.query(Loan).all()

    def update_loan_status(self, db: Session, loan_id: int, update_data: LoanUpdate):
        loan = db.query(Loan).filter(Loan.id == loan_id).first()
        if not loan:
            raise HTTPException(status_code=404, detail="Loan not found")
        
        loan.status = update_data.status
        loan.remarks = update_data.remarks
        # Append to remarks if needed, but for now simple overwrite/update
        
        db.commit()
        db.refresh(loan)
        return loan

loan_service = LoanService()
