import jwt
from datetime import datetime, timedelta
from typing import Any, Union
from app.core.config import settings

def create_access_token(subject: Union[str, Any]) -> str:
    expire = datetime.utcnow() + timedelta(days=settings.ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode = {"exp": expire, "user_id": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
