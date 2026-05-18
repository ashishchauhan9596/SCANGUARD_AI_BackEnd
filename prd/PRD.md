# TECHNICAL BLUEPRINT: SCANGUARD AI (K-LEVEL)

## 1. PROJECT CORE
**Goal**: Scan product barcodes/labels to return Expiry Dates + Personalized "Bimari" (Disease) risks.
**Stack**: FastAPI (Async), PostgreSQL, Gemini 1.5 Flash.
**Identity**: UUID v7 (Time-ordered/Sortable PKs).
**Architecture**: Denormalized Flat-Write (Zero-Joins). Use JSONB for data blobs.

## 2. GOOGLE-ONLY AUTH (CUSTOM)
**Logic**: Frontend sends Google id_token. Backend verifies via google-auth library.
**Restriction**: REJECT any email not ending in @gmail.com.
**Session**: Issue a custom JWT containing the user_id (UUID v7).

## 3. DATABASE SCHEMA (POSTGRESQL)
### Table: users
- **id**: UUID v7 (PK)
- **email**: String (Unique, @gmail.com only)
- **billing**: JSONB `{ "scans_left": 5, "is_premium": false }`

### Table: scans
- **id**: UUID v7 (PK)
- **user_id**: UUID v7
- **barcode**: String (Indexed)
- **data**: JSONB `{ "name", "brand", "exp_date", "mfg_date", "status" }`
- **analysis**: JSONB `{ "pros", "cons", "bimari_risks", "verdict", "worth_it" }`

## 4. API SPECIFICATION: POST /analyze
**Auth**: Verify JWT.
**Gatekeeper**: If `users.billing.scans_left <= 0`, return `402 Payment Required`.
**Process**: Extract Barcode/Text -> Check Cache -> Run Gemini AI (if new).
**AI Researcher Prompt**: "Identify ingredients. List 3 Pros, 3 Cons. Link ingredients to specific Diseases (Bimari) like Diabetes, Hypertension, or Gut issues. Give a Thumbs Up/Down and 'Is it worth it' verdict."
**Write**: Upsert product data to scans. Decrement `scans_left` in users.
**Response**: Return the full JSON report.

## 5. SCALABILITY RULES
- **No Joins**: Fetch all data for a scan from a single row in the scans table.
- **Performance**: Use `asyncpg` for DB ops. Use `lru_cache` for barcode lookups.
- **Sortability**: Rely on UUID v7 for sequential disk writes.
