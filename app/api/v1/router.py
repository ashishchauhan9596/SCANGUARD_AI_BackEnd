from fastapi import APIRouter
from app.api.v1.endpoints import auth, analyze, wallet, users

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(analyze.router, prefix="/analyze", tags=["analyze"])
api_router.include_router(wallet.router, prefix="/wallet", tags=["wallet"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
