from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.core.database import get_db
from backend.models.models import Complaint, User
from backend.routes.deps import get_current_active_farmer
from datetime import datetime

router = APIRouter(prefix="/complaints", tags=["Complaints"])

@router.post("/")
def submit_complaint(text: str, anonymous: bool = False, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_farmer)):
    comp = Complaint(
        farmer_id=None if anonymous else current_user.id,
        text=text,
        anonymous=1 if anonymous else 0,
        created_at=datetime.utcnow()
    )
    db.add(comp)
    db.commit()
    db.refresh(comp)
    return {"id": comp.id, "message": "Complaint submitted"}
