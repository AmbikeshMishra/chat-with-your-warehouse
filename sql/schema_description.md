
# INSURANCE_DB.CLAIMS — Schema Reference

Used by the LangGraph agent as a cached schema prompt (loaded once per session, not resent every turn).

## IMPORTANT — how to reference tables and views
ALWAYS use the fully qualified three-part name: DATABASE.SCHEMA.OBJECT
  CORRECT:   SELECT ... FROM INSURANCE_DB.CLAIMS.V_CLAIMS_SUMMARY
  CORRECT:   SELECT ... FROM INSURANCE_DB.CLAIMS.FACT_CLAIMS
  CORRECT:   SELECT ... FROM INSURANCE_DB.CLAIMS.DIM_POLICY_HOLDER
  CORRECT:   SELECT ... FROM INSURANCE_DB.CLAIMS.DIM_POLICY
  WRONG:     SELECT ... FROM V_CLAIMS_SUMMARY          ← missing database and schema
  WRONG:     SELECT ... FROM INSURANCE_DB.V_CLAIMS_SUMMARY  ← missing schema

## Tables

### FACT_CLAIMS
Primary fact table — one row per insurance claim.

| Column | Type | Description |
|---|---|---|
| claim_id | NUMBER PK | Unique claim identifier |
| policy_id | NUMBER FK | Links to DIM_POLICY |
| policy_holder_id | NUMBER FK | Links to DIM_POLICY_HOLDER |
| claim_date | DATE | Date claim was filed |
| incident_date | DATE | Date the incident occurred |
| claim_amount | NUMBER(14,2) | Amount requested |
| approved_amount | NUMBER(14,2) | Amount approved (NULL if pending/denied) |
| claim_status | VARCHAR(20) | 'Pending' | 'Approved' | 'Denied' | 'Settled' |
| denial_reason | VARCHAR(200) | Populated when status = 'Denied' |
| settlement_date | DATE | Date settlement was paid |
| claim_type | VARCHAR(50) | 'Accident' | 'Theft' | 'Medical' | 'Fire' |

### DIM_POLICY_HOLDER
One row per insured customer.

| Column | Type | Description |
|---|---|---|
| policy_holder_id | NUMBER PK | |
| full_name | VARCHAR(200) | |
| gender | VARCHAR(10) | |
| date_of_birth | DATE | |
| region | VARCHAR(100) | 'North' | 'South' | 'East' | 'West' |
| state | VARCHAR(50) | US state |
| city | VARCHAR(100) | |

### DIM_POLICY
One row per policy (a holder can have multiple).

| Column | Type | Description |
|---|---|---|
| policy_id | NUMBER PK | |
| policy_holder_id | NUMBER FK | |
| insurance_type | VARCHAR(50) | 'Auto' | 'Health' | 'Home' | 'Life' |
| plan_name | VARCHAR(100) | |
| premium_amount | NUMBER(12,2) | Monthly premium |
| coverage_amount | NUMBER(14,2) | Maximum covered amount |
| start_date | DATE | |
| end_date | DATE | NULL = still active |
| policy_status | VARCHAR(20) | 'Active' | 'Lapsed' | 'Cancelled' |

### V_CLAIMS_SUMMARY (view)
Pre-joined convenience view combining FACT_CLAIMS + DIM_POLICY + DIM_POLICY_HOLDER.
Prefer this view for single-table-style questions about claims.

## Key relationships
- FACT_CLAIMS.policy_id → DIM_POLICY.policy_id
- FACT_CLAIMS.policy_holder_id → DIM_POLICY_HOLDER.policy_holder_id
- DIM_POLICY.policy_holder_id → DIM_POLICY_HOLDER.policy_holder_id

## Data coverage
- claim_date ranges from 2025-01-01 to 2026-07-15
- Today's date in Snowflake: CURRENT_DATE() → 2026-07-16
- Current quarter: Q3 2026 (Jul–Sep 2026)
- Last quarter: Q2 2026 (Apr–Jun 2026)

## Snowflake date patterns — use these exactly
- **Last quarter date range:**
  claim_date >= DATE_TRUNC('quarter', DATEADD(quarter, -1, CURRENT_DATE()))
  AND claim_date < DATE_TRUNC('quarter', CURRENT_DATE())
- **This year:** YEAR(claim_date) = YEAR(CURRENT_DATE())
- **Last year:** YEAR(claim_date) = YEAR(CURRENT_DATE()) - 1
- **By month:** TO_CHAR(DATE_TRUNC('month', claim_date), 'YYYY-MM') AS month  ← always use this format, never MONTH() alone
- **By quarter:** QUARTER(claim_date) AS quarter, YEAR(claim_date) AS year

## Common query patterns
- **Claims by region:** GROUP BY region, SUM(approved_amount)
- **Payout = approved_amount** (not claim_amount). For total payouts include Approved AND Settled status. approved_amount is NULL for Pending, 0.00 for Denied.
- **Percentage/comparison queries:** ALWAYS use long format (one row per category), never wide format (one column per metric).
  CORRECT: SELECT claim_status, ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1) AS percentage FROM INSURANCE_DB.CLAIMS.FACT_CLAIMS GROUP BY claim_status ORDER BY percentage DESC
  WRONG:   SELECT COUNT(CASE WHEN claim_status='Approved'...) AS pct_approved, COUNT(CASE WHEN claim_status='Denied'...) AS pct_denied ← never do this
- **Total payouts by quarter:** SUM(approved_amount) GROUP BY YEAR(claim_date), QUARTER(claim_date)
- **Holders with multiple claims:** Always show policy_holder_name (never policy_holder_id) as the label. Example:
  SELECT h.full_name AS policy_holder_name, COUNT(f.claim_id) AS claim_count
  FROM INSURANCE_DB.CLAIMS.FACT_CLAIMS f
  JOIN INSURANCE_DB.CLAIMS.DIM_POLICY_HOLDER h ON h.policy_holder_id = f.policy_holder_id
  GROUP BY h.full_name HAVING COUNT(f.claim_id) > 3 ORDER BY claim_count DESC
- **General rule:** Never SELECT numeric ID columns (policy_holder_id, policy_id, claim_id) as the only label — always JOIN to get the human-readable name.
