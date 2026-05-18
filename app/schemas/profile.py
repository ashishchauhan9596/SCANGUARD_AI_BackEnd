from pydantic import BaseModel
from typing import List, Optional

class LifestyleProfile(BaseModel):
    smoking: str = "none" # none/occasional/regular
    alcohol: str = "none" # none/occasional/regular
    physical_activity: str = "low" # low/medium/high
    sleep_quality: str = "fair" # poor/fair/good

class UserProfileBase(BaseModel):
    age: int
    gender: str # male/female/other
    weight: Optional[float] = None
    height: Optional[float] = None
    conditions: List[str] = []
    allergies: List[str] = []
    lifestyle: LifestyleProfile = LifestyleProfile()
    diet_preferences: List[str] = []
    risk_profile: str = "normal" # cautious/normal/risk_tolerant

class UserProfileCreate(UserProfileBase):
    pass

class UserProfileResponse(UserProfileBase):
    user_id: str
