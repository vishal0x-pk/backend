from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from backend.core.database import get_db
from backend.core.config import settings
from backend.models.models import User
from backend.core.security import oauth2_scheme

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_farmer(current_user: User = Depends(get_current_user)):
    if current_user.role != "farmer":
        raise HTTPException(status_code=400, detail="Not a farmer user")
    return current_user

async def get_current_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    return current_user

async def get_current_approver(current_user: User = Depends(get_current_user)):
    if current_user.role != "approver":
        raise HTTPException(status_code=403, detail="Not authorized")
    return current_user

async def get_current_treasury(current_user: User = Depends(get_current_user)):
    if current_user.role != "treasury":
        raise HTTPException(status_code=403, detail="Not authorized")
    return current_user
