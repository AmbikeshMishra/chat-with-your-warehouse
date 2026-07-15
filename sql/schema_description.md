# INSURANCE_DB.CLAIMS — Schema Reference

Used by the LangGraph agent as a cached schema prompt (loaded once per session, not resent every turn).

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

## Common query patterns
- **Claims by region:** JOIN FACT_CLAIMS + DIM_POLICY_HOLDER, GROUP BY region
- **Claim approval rate:** COUNT(*) FILTER (WHERE claim_status='Approved') / COUNT(*)
- **Total payouts by quarter:** SUM(approved_amount) GROUP BY QUARTER(claim_date)
- **Holders with multiple claims:** COUNT(claim_id) > 1 GROUP BY policy_holder_id
