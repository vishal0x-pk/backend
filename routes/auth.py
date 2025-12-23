from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from backend.core.database import get_db
from backend.services.auth_service import auth_service
from backend.schemas.schemas import UserCreate, UserResponse, Token, GoogleLoginRequest, PhoneRequest, OtpVerifyRequest
import requests
import random
import time

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    return auth_service.register_user(db, user)

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Create UserLogin object for service
    from backend.schemas.schemas import UserLogin
    user_login = UserLogin(username=form_data.username, password=form_data.password)
    
    user = auth_service.authenticate_user(db, user_login)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = auth_service.create_token_for_user(user)
    return {"access_token": access_token, "token_type": "bearer"}

OTP_STORE = {}

@router.post("/google", response_model=Token)
def google_login(data: GoogleLoginRequest, db: Session = Depends(get_db)):
    try:
        resp = requests.get("https://oauth2.googleapis.com/tokeninfo", params={"id_token": data.id_token}, timeout=5)
        if resp.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid Google token")
        info = resp.json()
        email = info.get("email")
        if not email:
            raise HTTPException(status_code=400, detail="Google token missing email")
        user = auth_service.get_or_create_user(db, username=email, role="farmer")
        token = auth_service.create_token_for_user(user)
        return {"access_token": token, "token_type": "bearer"}
    except requests.RequestException:
        raise HTTPException(status_code=503, detail="Google verification service unavailable")

@router.post("/send-otp")
def send_otp(req: PhoneRequest):
    otp = f"{random.randint(100000, 999999)}"
    OTP_STORE[req.phone] = {"otp": otp, "exp": time.time() + 300}
    print(f"OTP for {req.phone}: {otp}")
    return {"message": "OTP sent"}

@router.post("/verify-otp", response_model=Token)
def verify_otp(req: OtpVerifyRequest, db: Session = Depends(get_db)):
    entry = OTP_STORE.get(req.phone)
    if not entry or entry["exp"] < time.time() or entry["otp"] != req.otp:
        raise HTTPException(status_code=401, detail="Invalid or expired OTP")
    username = f"phone:{req.phone}"
    user = auth_service.get_or_create_user(db, username=username, role="farmer")
    token = auth_service.create_token_for_user(user)
    return {"access_token": token, "token_type": "bearer"}
