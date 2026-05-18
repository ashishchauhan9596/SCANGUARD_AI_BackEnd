from pydantic import BaseModel
from typing import Optional, List

class AnalyzeRequest(BaseModel):
    barcode: Optional[str] = None
    text_input: Optional[str] = None
    lang: str = "en"

class Identity(BaseModel):
    name: str
    brand: str
    category: str
    confidence: int

class ExtractedFacts(BaseModel):
    batch: str
    expiry: str
    mrp: str

class Composition(BaseModel):
    name: str
    effect: str

class ExpertAnalysis(BaseModel):
    compositions: List[Composition]
    body_response_30mins: str
    long_term_impact: str
    traffic_light_status: str
    pros: List[str]
    cons: List[str]

class LifestyleWarnings(BaseModel):
    diabetes: str
    blood_pressure: str
    kids_safe: str

class ScanResult(BaseModel):
    scan_id: str
    identity: Identity
    extracted_facts: ExtractedFacts
    expert_analysis: ExpertAnalysis
    lifestyle_warnings: LifestyleWarnings
    disclaimer: str = "Health information only, not medical advice."

class ScanFeedback(BaseModel):
    scan_id: str
    is_helpful: bool
    comment: Optional[str] = None
