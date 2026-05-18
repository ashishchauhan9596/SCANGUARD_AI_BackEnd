# Scan Model (PostgreSQL JSONB)
# Table: scans
# Columns:
# - id: UUID (PK)
# - user_id: UUID (FK to users)
# - barcode: TEXT (Indexed)
# - data: JSONB { "name", "brand", "exp_date", "mfg_date", "status" }
# - analysis: JSONB { "pros", "cons", "bimari_risks", "verdict", "worth_it" }
