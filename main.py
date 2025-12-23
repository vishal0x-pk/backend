from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.core.database import engine, Base, SessionLocal
from backend.routes import auth, loans, onboarding, public, complaints
from backend.models.models import User, UserRole
from backend.core.security import get_password_hash

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Farm Loan System", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router)
app.include_router(loans.router)
app.include_router(onboarding.router)
app.include_router(public.router)
app.include_router(complaints.router)

@app.on_event("startup")
def startup_init():
    db = SessionLocal()
    db.close()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Farm Loan Management System API"}
