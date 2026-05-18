import json
from fastapi import APIRouter, Depends, HTTPException
from app.api.v1.deps import get_current_user
from app.db.session import db
from app.schemas.scan import AnalyzeRequest, ScanResult, ScanFeedback
from app.services.ai_service import ai_service
from app.utils.uuid_v7 import generate_uuid_v7

router = APIRouter()

@router.post("/")
async def analyze_product(request: AnalyzeRequest, user_id: str = Depends(get_current_user)):
    # 1. Fetch User Data (Wallet + Profile)
    user = await db.fetchrow("SELECT wallet, profile FROM identities WHERE id = $1", user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    wallet = json.loads(user['wallet']) if isinstance(user['wallet'], str) else user['wallet']
    profile = json.loads(user['profile']) if isinstance(user['profile'], str) else (user['profile'] or {})
    
    if wallet.get("scans_left", 0) <= 0 and not wallet.get("is_premium", False):
        raise HTTPException(status_code=402, detail="Payment Required: Refill your wallet")
    
    # 2. AI Generation: Deep personalized research
    input_text = request.text_input or request.barcode or "Unknown Product"
    report = await ai_service.analyze_product(input_text, user_profile=profile, lang=request.lang)
    
    # 3. Check for AI Failure (Fallback Data or Extreme Low Confidence)
    identity = report.get("identity", {})
    if identity.get("name") == "Analysis Failed" or identity.get("confidence", 100) < 15:
        report["scan_id"] = f"err_{generate_uuid_v7()}"
        return report
        
    # 4. Create Scan Record
    scan_id = generate_uuid_v7()
    report["scan_id"] = str(scan_id)
    
    # 5. Storage Logic: Store in new JSONB 'scan_data' column
    category = identity.get("category", "unknown")
    await db.execute(
        """INSERT INTO master_scans (id, user_id, barcode, category, scan_data) 
           VALUES ($1, $2, $3, $4, $5)""",
        scan_id, user_id, request.barcode, category, json.dumps(report)
    )
    
    # 6. Wallet Update
    wallet["scans_left"] = max(0, wallet.get("scans_left", 0) - 1)
    wallet["total_spent"] = wallet.get("total_spent", 0) + 1
    await db.execute("UPDATE identities SET wallet = $1 WHERE id = $2", json.dumps(wallet), user_id)
    
    return report

@router.post("/feedback")
async def scan_feedback(feedback: ScanFeedback, user_id: str = Depends(get_current_user)):
    """
    Stores user feedback for a specific scan to improve AI accuracy.
    """
    await db.execute(
        "INSERT INTO scan_feedback (id, scan_id, is_helpful, comment) VALUES ($1, $2, $3, $4)",
        str(generate_uuid_v7()), feedback.scan_id, feedback.is_helpful, feedback.comment
    )
    return {"status": "success"}

@router.get("/history")
async def get_scan_history(user_id: str = Depends(get_current_user)):
    scans = await db.fetch(
        "SELECT id as scan_id, scan_data, created_at FROM master_scans WHERE user_id = $1 ORDER BY created_at DESC",
        user_id
    )
    
    results = []
    for scan in scans:
        raw_data = scan['scan_data']
        
        if raw_data is None:
            raw_data = scan.get('health_report') or scan.get('product_identity')
            
        if raw_data is None:
            continue
            
        data = json.loads(raw_data) if isinstance(raw_data, str) else raw_data
        if not data or not isinstance(data, dict):
            continue
            
        if "error" in data:
            data["scan_id"] = str(scan['scan_id'])
            data["created_at"] = scan['created_at'].isoformat()
            results.append(data)
            continue
            
        # DATA TRANSLATION LAYER -> EXPERT BRAIN SCHEMA
        if "identity" not in data:
            # Transform legacy data into the new schema
            legacy_name = data.get("product_name", "Unknown Product")
            legacy_verdict = data.get("verdict", "CAUTION")
            
            # Map Traffic Light
            tl = "YELLOW"
            if legacy_verdict == "SAFE": tl = "GREEN"
            elif legacy_verdict == "AVOID": tl = "RED"
            
            new_data = {
                "identity": {
                    "name": legacy_name,
                    "brand": data.get("brand_name", "Unknown"),
                    "category": data.get("category", "unknown"),
                    "confidence": data.get("confidence_score", 80)
                },
                "extracted_facts": {
                    "batch": "Unknown",
                    "expiry": data.get("expiry_info", {}).get("exp_date", "Unknown"),
                    "mrp": "Unknown"
                },
                "expert_analysis": {
                    "compositions": [{"name": i.get("name", i) if isinstance(i, dict) else i, "effect": i.get("purpose", "Unknown") if isinstance(i, dict) else "Unknown"} for i in data.get("ingredients", [])],
                    "body_response_30mins": data.get("advice", "Unknown"),
                    "long_term_impact": "Unknown",
                    "traffic_light_status": tl,
                    "pros": [],
                    "cons": data.get("health_risk_reasons", [])
                },
                "lifestyle_warnings": {
                    "diabetes": "Unknown",
                    "blood_pressure": "Unknown",
                    "kids_safe": "Unknown"
                },
                "disclaimer": data.get("disclaimer", "Health information only, not medical advice.")
            }
            data = new_data

        data["scan_id"] = str(scan['scan_id'])
        data["created_at"] = scan['created_at'].isoformat()
        results.append(data)
    
    return results
