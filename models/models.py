from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from backend.core.database import Base

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    FARMER = "farmer"
    APPROVER = "approver"
    TREASURY = "treasury"

class LoanStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String)
    
    # AI fields (keeping these as they seem useful for the AI part)
    credit_score = Column(Integer, default=650)
    balance = Column(Float, default=5000.0)
    
    # KYC and Banking
    aadhaar = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    kyc_verified = Column(Integer, default=0) # 0/1
    bank_account = Column(String, nullable=True)
    ifsc = Column(String, nullable=True)

    loans = relationship("Loan", back_populates="farmer")

class Loan(Base):
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Float)
    purpose = Column(String)
    
    # Required fields
    land_size = Column(Float, default=0.0) # in acres
    crop_type = Column(String, default="Unknown")
    annual_income = Column(Float, default=0.0)
    location = Column(String, default="Unknown") # Added location as per requirements
    merchant_restricted = Column(Integer, default=0)
    merchant_category = Column(String, nullable=True)
    insured = Column(Integer, default=0)
    insurance_provider = Column(String, nullable=True)
    
    status = Column(String, default=LoanStatus.PENDING)
    decision_reason = Column(String, nullable=True) # Renamed/Added for clarity
    confidence_score = Column(Float, nullable=True) # Added for ML confidence
    
    # Repayment
    repayment_frequency = Column(String, default="monthly") # monthly/quarterly/post-harvest
    emi_amount = Column(Float, nullable=True)
    next_due_date = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    remarks = Column(String, nullable=True) # For admin overrides/remarks

    farmer = relationship("User", back_populates="loans")
    history = relationship("LoanHistory", back_populates="loan")

class LoanHistory(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    loan_id = Column(Integer, ForeignKey("loans.id"))
    reference_id = Column(String, unique=True, index=True)
    amount = Column(Float)
    to_account = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    prev_hash = Column(String, nullable=True)
    hash = Column(String)
    
    remarks = Column(String, nullable=True)

class Complaint(Base):
    __tablename__ = "complaints"
    
    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("users.id"))
    text = Column(String)
    anonymous = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class LoanHistory(Base):
    __tablename__ = "loan_history"

    id = Column(Integer, primary_key=True, index=True)
    loan_id = Column(Integer, ForeignKey("loans.id"))
    action = Column(String)
    performed_by = Column(Integer, ForeignKey("users.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    remarks = Column(String, nullable=True)

    loan = relationship("Loan", back_populates="history")

class Invoice(Base):
    __tablename__ = "invoices"
    id = Column(Integer, primary_key=True, index=True)
    loan_id = Column(Integer, ForeignKey("loans.id"))
    file_path = Column(String)
    amount = Column(Float, default=0)
    timestamp = Column(DateTime, default=datetime.utcnow)

class MerchantVoucher(Base):
    __tablename__ = "merchant_vouchers"
    id = Column(Integer, primary_key=True, index=True)
    loan_id = Column(Integer, ForeignKey("loans.id"))
    voucher_code = Column(String, unique=True, index=True)
    merchant_category = Column(String)
    amount = Column(Float)
    redeemed = Column(Integer, default=0)
