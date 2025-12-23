from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from backend.models.models import User, UserRole
from backend.schemas.schemas import UserCreate, UserLogin
from backend.core.security import get_password_hash, verify_password, create_access_token

class AuthService:
    def register_user(self, db: Session, user: UserCreate):
        # Check if user exists
        db_user = db.query(User).filter(User.username == user.username).first()
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        hashed_password = get_password_hash(user.password)
        new_user = User(
            username=user.username,
            hashed_password=hashed_password,
            role=user.role,
            credit_score=650, # Default
            balance=5000.0   # Default
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user

    def authenticate_user(self, db: Session, user: UserLogin):
        db_user = db.query(User).filter(User.username == user.username).first()
        if not db_user:
            return None
        if not verify_password(user.password, db_user.hashed_password):
            return None
        return db_user

    def create_token_for_user(self, user: User):
        access_token = create_access_token(
            data={"sub": user.username, "role": user.role, "id": user.id}
        )
        return access_token
    
    def get_or_create_user(self, db: Session, username: str, role: str = "farmer"):
        db_user = db.query(User).filter(User.username == username).first()
        if db_user:
            return db_user
        new_user = User(
            username=username,
            hashed_password=get_password_hash("oauth"),
            role=role,
            credit_score=650,
            balance=5000.0
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user

auth_service = AuthService()
