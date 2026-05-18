from fastapi import APIRouter, Depends, HTTPException
from app.api.v1.deps import get_current_user
from app.db.session import db
import json
from app.schemas.profile import UserProfileCreate, UserProfileResponse

router = APIRouter()

@router.get("/me")
async def get_user_profile(user_id: str = Depends(get_current_user)):
    user = await db.fetchrow("SELECT id, email, wallet, profile, meta FROM identities WHERE id = $1", user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": str(user['id']),
        "email": user['email'],
        "wallet": json.loads(user['wallet']) if isinstance(user['wallet'], str) else user['wallet'],
        "profile": json.loads(user['profile']) if isinstance(user['profile'], str) else (user['profile'] or {}),
        "meta": json.loads(user['meta']) if isinstance(user['meta'], str) else user['meta']
    }

@router.post("/profile", response_model=UserProfileResponse)
async def update_profile(profile_data: UserProfileCreate, user_id: str = Depends(get_current_user)):
    """
    Updates the user's medical and lifestyle profile in the database.
    """
    await db.execute(
        "UPDATE identities SET profile = $1 WHERE id = $2",
        json.dumps(profile_data.dict()), user_id
    )
    return {**profile_data.dict(), "user_id": user_id}
