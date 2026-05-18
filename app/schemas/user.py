from pydantic import BaseModel, EmailStr
from typing import Dict, Any

class UserBase(BaseModel):
    email: EmailStr

class UserBilling(BaseModel):
    scans_left: int = 5
    is_premium: bool = False

class User(UserBase):
    id: str
    billing: UserBilling

class GoogleAuth(BaseModel):
    id_token: str
