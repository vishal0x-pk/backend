from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.core.database import get_db
from backend.models.models import User
from backend.routes.deps import get_current_active_farmer
from backend.schemas.schemas import PhoneRequest
from fastapi import UploadFile, File
import os
from backend.models.models import Invoice, Loan
from sqlalchemy.orm import Session

router = APIRouter(prefix="/onboarding", tags=["Onboarding"])

@router.post("/kyc")
def submit_kyc(aadhaar: str, phone: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_farmer)):
    if len(aadhaar) != 12 or not aadhaar.isdigit():
        raise HTTPException(status_code=400, detail="Invalid Aadhaar")
    current_user.aadhaar = aadhaar
    current_user.phone = phone
    current_user.kyc_verified = 1
    db.commit()
    return {"message": "KYC verified"}

@router.post("/link-bank")
def link_bank(bank_account: str, ifsc: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_farmer)):
    if len(bank_account) < 9:
        raise HTTPException(status_code=400, detail="Invalid account")
    if len(ifsc) != 11:
        raise HTTPException(status_code=400, detail="Invalid IFSC")
    current_user.bank_account = bank_account
    current_user.ifsc = ifsc
    db.commit()
    return {"message": "Bank linked"}

@router.post("/upload-land-doc")
def upload_land_doc(file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_active_farmer)):
    os.makedirs("uploads", exist_ok=True)
    path = os.path.join("uploads", f"land_{current_user.id}_{file.filename}")
    with open(path, "wb") as f:
        f.write(file.file.read())
    return {"message": "Document uploaded", "path": path}

@router.post("/insurance-link")
def insurance_link(provider: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_farmer)):
    current_user.insurance_provider = provider
    db.commit()
    return {"message": "Insurance linked"}

@router.post("/upload-invoice")
def upload_invoice(loan_id: int, amount: float, file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_active_farmer)):
    loan = db.query(Loan).filter(Loan.id == loan_id, Loan.farmer_id == current_user.id).first()
    if not loan:
        return {"error": "Loan not found"}
    os.makedirs("uploads", exist_ok=True)
    path = os.path.join("uploads", f"invoice_{loan_id}_{file.filename}")
    with open(path, "wb") as f:
        f.write(file.file.read())
    inv = Invoice(loan_id=loan_id, file_path=path, amount=amount)
    db.add(inv)
    db.commit()
    db.refresh(inv)
    return {"id": inv.id, "message": "Invoice uploaded"}
