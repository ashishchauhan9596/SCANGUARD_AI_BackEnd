import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_router
from app.core.config import settings
from app.db.session import db

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    await db.connect()
    
    # 1. Identities (Expanded with Full Profile Support)
    await db.execute("""
        CREATE TABLE IF NOT EXISTS identities (
            id UUID PRIMARY KEY,
            google_sub TEXT UNIQUE,
            email TEXT UNIQUE NOT NULL,
            profile JSONB DEFAULT '{}'::jsonb,
            wallet JSONB DEFAULT '{"scans_left": 3, "is_premium": false, "total_spent": 0}'::jsonb,
            meta JSONB DEFAULT '{"name": "", "avatar": "", "lang": "en"}'::jsonb,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 2. Master Scans (Updated for Deep Research results)
    await db.execute("""
        CREATE TABLE IF NOT EXISTS master_scans (
            id UUID PRIMARY KEY,
            user_id UUID NOT NULL REFERENCES identities(id),
            barcode TEXT,
            category TEXT,
            scan_data JSONB, -- Stores the full ScanResult structure
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 3. Scan Feedback (New table for A/B testing and AI improvement)
    await db.execute("""
        CREATE TABLE IF NOT EXISTS scan_feedback (
            id UUID PRIMARY KEY,
            scan_id UUID NOT NULL REFERENCES master_scans(id),
            is_helpful BOOLEAN,
            comment TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    await db.execute("CREATE INDEX IF NOT EXISTS idx_scans_user ON master_scans(user_id)")
    await db.execute("CREATE INDEX IF NOT EXISTS idx_feedback_scan ON scan_feedback(scan_id)")
@app.on_event("shutdown")
async def shutdown_event():
    await db.disconnect()

app.include_router(api_router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
