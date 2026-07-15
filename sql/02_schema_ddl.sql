-- Insurance claims schema — run as ACCOUNTADMIN or SYSADMIN
-- Designed to support the 5 sample questions in the brief

USE DATABASE INSURANCE_DB;
USE SCHEMA   CLAIMS;

-- ── DIMENSION TABLES ──────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS DIM_POLICY_HOLDER (
    policy_holder_id  NUMBER        NOT NULL PRIMARY KEY,
    full_name         VARCHAR(200)  NOT NULL,
    gender            VARCHAR(10),
    date_of_birth     DATE,
    region            VARCHAR(100)  NOT NULL,   -- e.g. 'North', 'South', 'East', 'West'
    state             VARCHAR(50),
    city              VARCHAR(100),
    agent_id          NUMBER                     -- FK to DIM_AGENT (optional)
);

CREATE TABLE IF NOT EXISTS DIM_POLICY (
    policy_id         NUMBER        NOT NULL PRIMARY KEY,
    policy_holder_id  NUMBER        NOT NULL REFERENCES DIM_POLICY_HOLDER(policy_holder_id),
    insurance_type    VARCHAR(50)   NOT NULL,   -- 'Auto', 'Health', 'Home', 'Life'
    plan_name         VARCHAR(100),
    premium_amount    NUMBER(12,2)  NOT NULL,
    coverage_amount   NUMBER(14,2)  NOT NULL,
    start_date        DATE          NOT NULL,
    end_date          DATE,
    policy_status     VARCHAR(20)   NOT NULL    -- 'Active', 'Lapsed', 'Cancelled'
);

-- ── FACT TABLE ────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS FACT_CLAIMS (
    claim_id           NUMBER        NOT NULL PRIMARY KEY,
    policy_id          NUMBER        NOT NULL REFERENCES DIM_POLICY(policy_id),
    policy_holder_id   NUMBER        NOT NULL REFERENCES DIM_POLICY_HOLDER(policy_holder_id),
    claim_date         DATE          NOT NULL,
    incident_date      DATE          NOT NULL,
    claim_amount       NUMBER(14,2)  NOT NULL,
    approved_amount    NUMBER(14,2),             -- NULL until adjudicated
    claim_status       VARCHAR(20)   NOT NULL,   -- 'Pending','Approved','Denied','Settled'
    denial_reason      VARCHAR(200),             -- populated when status = 'Denied'
    settlement_date    DATE,
    claim_type         VARCHAR(50)               -- 'Accident','Theft','Medical','Fire', etc.
);

-- ── SUPPORTING VIEWS (schema description cache will use these) ────────────────

CREATE OR REPLACE VIEW V_CLAIMS_SUMMARY AS
SELECT
    f.claim_id,
    f.claim_date,
    f.claim_status,
    f.claim_amount,
    f.approved_amount,
    f.claim_type,
    p.insurance_type,
    p.plan_name,
    h.region,
    h.state,
    h.full_name AS policy_holder_name
FROM FACT_CLAIMS      f
JOIN DIM_POLICY       p ON p.policy_id       = f.policy_id
JOIN DIM_POLICY_HOLDER h ON h.policy_holder_id = f.policy_holder_id;
