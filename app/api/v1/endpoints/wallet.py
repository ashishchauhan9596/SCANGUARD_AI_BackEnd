import json
from fastapi import APIRouter, Depends, HTTPException
from app.api.v1.deps import get_current_user
from app.db.session import db
from pydantic import BaseModel

router = APIRouter()

class RefillRequest(BaseModel):
    amount: int  # Example: 3 for ₹3

@router.post("/refill")
async def refill_wallet(request: RefillRequest, user_id: str = Depends(get_current_user)):
    """
    Process wallet refill. 
    In a real scenario, this would validate a UPI/Gateway callback.
    """
    user = await db.fetchrow("SELECT wallet FROM vault_users WHERE id = $1", user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    wallet = json.loads(user['wallet']) if isinstance(user['wallet'], str) else user['wallet']
    
    # Logic: Increment scans_left based on amount
    # PRD: Increment scans_left by 1 for ₹3
    scans_to_add = request.amount // 3
    if scans_to_add <= 0:
        raise HTTPException(status_code=400, detail="Minimum refill amount is ₹3")
        
    wallet["scans_left"] += scans_to_add
    wallet["total_spent"] = wallet.get("total_spent", 0) + request.amount
    
    await db.execute("UPDATE vault_users SET wallet = $1 WHERE id = $2", json.dumps(wallet), user_id)
    
    return {"status": "success", "scans_left": wallet["scans_left"]}
