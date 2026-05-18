from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt, JWTError
from app.core.config import settings
from app.db.session import db

security = HTTPBearer()

async def get_current_user(auth: HTTPAuthorizationCredentials = Security(security)) -> str:
    """
    Verifies the custom JWT issued by our POST /v1/auth/google endpoint.
    Returns the user_id (UUID v7).
    """
    token = auth.credentials
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        
        # Verify the user actually exists in identities
        user = await db.fetchrow("SELECT id FROM identities WHERE id = $1", user_id)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
            
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

