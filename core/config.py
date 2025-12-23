import os

class Settings:
    PROJECT_NAME: str = "Farm Loan System"
    PROJECT_VERSION: str = "1.0.0"
    
    SQLALCHEMY_DATABASE_URL: str = "sqlite:///./farm_loans.db"
    
    SECRET_KEY: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7" # Change in production
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    GOV_INTEREST_RATE: float = 0.06
    
settings = Settings()
