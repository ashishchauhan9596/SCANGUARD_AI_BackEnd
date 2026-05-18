import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "SCANGUARD AI"
    API_V1_STR: str = "/api/v1"
    
    # Database (PostgreSQL)
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/scanguard"
    
    # Custom Auth (Google OIDC)
    SECRET_KEY: str = "7297e6b7-a363-4416-8c46-77e810cb9907-super-secret-key" # fallback default
    GOOGLE_CLIENT_ID: Optional[str] = None
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_DAYS: int = 30
    
    # AI (Gemini 1.5 Flash)
    GEMINI_API_KEY: Optional[str] = None

    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "allow"
    }

settings = Settings()
