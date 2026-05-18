from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from google.oauth2 import id_token
from google.auth.transport import requests
from jose import jwt
from datetime import datetime, timedelta
from app.db.session import db
from app.utils.uuid_v7 import generate_uuid_v7
from app.core.config import settings
import json

router = APIRouter()

class GoogleAuthRequest(BaseModel):
    id_token: str

@router.post("/google")
async def google_auth(request: GoogleAuthRequest):
    """
    Custom Google OIDC Auth: Verifies Google token, enforces @gmail.com, and issues a custom JWT.
    """
    try:
        # Verify the Google token
        idinfo = id_token.verify_oauth2_token(
            request.id_token, 
            requests.Request(), 
            settings.GOOGLE_CLIENT_ID
        )
        
        email = idinfo.get("email", "")
        google_sub = idinfo.get("sub")
        name = idinfo.get("name", "")
        picture = idinfo.get("picture", "")
        
        # CRITICAL GATEKEEPER: Strictly @gmail.com
        if not email.endswith("@gmail.com"):
            raise HTTPException(status_code=403, detail="Forbidden: Only @gmail.com addresses are allowed.")
            
        # UPSERT LOGIC
        user = await db.fetchrow("SELECT id FROM identities WHERE google_sub = $1", google_sub)
        
        if user:
            # Update metadata
            user_id = str(user['id'])
            meta = json.dumps({"name": name, "avatar": picture, "lang": "en"})
            await db.execute("UPDATE identities SET meta = $1 WHERE id = $2", meta, user_id)
        else:
            # New user
            user_id = str(generate_uuid_v7())
            wallet = json.dumps({"scans_left": 3, "is_premium": False, "total_spent": 0})
            meta = json.dumps({"name": name, "avatar": picture, "lang": "en"})
            
            await db.execute(
                """INSERT INTO identities (id, google_sub, email, wallet, meta) 
                   VALUES ($1, $2, $3, $4, $5)""",
                user_id, google_sub, email, wallet, meta
            )
            
        # Create Custom JWT
        expire = datetime.utcnow() + timedelta(days=settings.ACCESS_TOKEN_EXPIRE_DAYS)
        jwt_payload = {"sub": user_id, "exp": expire}
        access_token = jwt.encode(jwt_payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        
        return {"access_token": access_token, "token_type": "bearer"}
        
    except ValueError as e:
        raise HTTPException(status_code=401, detail=f"Invalid Google token: {str(e)}")
