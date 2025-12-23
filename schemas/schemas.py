from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# --- Token Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None

class GoogleLoginRequest(BaseModel):
    id_token: str

class PhoneRequest(BaseModel):
    phone: str

class OtpVerifyRequest(BaseModel):
    phone: str
    otp: str

# --- User Schemas ---
class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str
    role: str = "farmer" # Default to farmer for registration

class UserLogin(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    role: str
    credit_score: int
    balance: float

    class Config:
        from_attributes = True

# --- Loan Schemas ---
class LoanBase(BaseModel):
    amount: float
    purpose: str
    land_size: float
    crop_type: str
    annual_income: float
    location: str
    repayment_frequency: str = "monthly"

class LoanCreate(LoanBase):
    pass

class LoanResponse(LoanBase):
    id: int
    farmer_id: int
    status: str
    decision_reason: Optional[str] = None
    confidence_score: Optional[float] = None
    created_at: datetime
    remarks: Optional[str] = None
    emi_amount: Optional[float] = None
    next_due_date: Optional[datetime] = None
    
    # We might want to return farmer details too, or just the ID
    # farmer: Optional[UserResponse] = None

    class Config:
        from_attributes = True

class LoanUpdate(BaseModel):
    status: str
    remarks: Optional[str] = None
