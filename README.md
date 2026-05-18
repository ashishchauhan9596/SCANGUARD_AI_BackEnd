# SCANGUARD AI (K-LEVEL)

A "User-Reliable" health ecosystem providing instant medical-grade research on products/medicines via Barcode or Vision-OCR.

## Core Features
- **K-Level Intelligence:** Deep Bimari-linkage research powered by Gemini 1.5 Flash.
- **Zero-Join Architecture:** High-speed flat-write ledger for medical reports.
- **Vault Security:** UUID v7 time-sortable keys with Google OIDC identity.
- **Multi-lingual:** Native support for English and Hindi (En/Hi).
- **Monetized Wallet:** Token-bucket scan logic with ₹3 refill cycles.

## Tech Stack
- **Backend:** Python 3.12, FastAPI (Async)
- **Database:** PostgreSQL (Flat-write), Redis (Cache)
- **AI:** Gemini 1.5 Flash
- **Auth:** Google OIDC (@gmail.com only)

## 🏗️ Architecture
This project follows a modular, industry-standard FastAPI architecture:
- `backend/app/api/`: API versioning and route handlers.
- `backend/app/core/`: Centralized configuration (Pydantic Settings) and security.
- `backend/app/db/`: Database connection and session management.
- `backend/app/models/`: Database table definitions.
- `backend/app/schemas/`: Pydantic models for data validation and API contracts.
- `backend/app/services/`: Business logic and external integrations (Gemini AI).
- `backend/app/utils/`: Shared helper functions (UUID v7).

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.9+
- PostgreSQL
- Gemini API Key & Google Client ID

### 2. Environment Setup
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### 3. Run the Server
```bash
# From the backend directory
export PYTHONPATH=$PYTHONPATH:.
uvicorn app.main:app --reload
```

## 🛡️ API documentation
Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- Redoc: `http://localhost:8000/redoc`
