"""Generates sql/04_load_full_data.sql with 30 holders, 50 policies, 120 claims."""
import random
from datetime import date, timedelta

random.seed(42)

# ── Reference data ─────────────────────────────────────────────────────────────

HOLDERS = [
    (1,  'Alice Sharma',       'Female', '1980-04-12', 'North', 'New York',       'Albany'),
    (2,  'Bob Tremblay',       'Male',   '1975-09-30', 'East',  'Massachusetts',  'Boston'),
    (3,  'Carol Diaz',         'Female', '1990-01-22', 'South', 'Texas',          'Houston'),
    (4,  'David Okafor',       'Male',   '1968-11-05', 'West',  'California',     'Los Angeles'),
    (5,  'Eva Chen',           'Female', '1995-07-18', 'West',  'Washington',     'Seattle'),
    (6,  'Frank Johnson',      'Male',   '1972-03-15', 'North', 'New York',       'New York City'),
    (7,  'Grace Kim',          'Female', '1988-08-24', 'West',  'California',     'San Francisco'),
    (8,  'Henry Williams',     'Male',   '1965-12-01', 'South', 'Florida',        'Miami'),
    (9,  'Isabel Rodriguez',   'Female', '1983-06-30', 'South', 'Georgia',        'Atlanta'),
    (10, 'James Lee',          'Male',   '1992-02-14', 'West',  'Oregon',         'Portland'),
    (11, 'Karen Patel',        'Female', '1978-09-07', 'North', 'New Jersey',     'Newark'),
    (12, 'Liam Brown',         'Male',   '1985-04-19', 'East',  'Maryland',       'Baltimore'),
    (13, 'Maria Gonzalez',     'Female', '1991-11-28', 'South', 'North Carolina', 'Charlotte'),
    (14, 'Nathan Davis',       'Male',   '1970-07-03', 'North', 'Pennsylvania',   'Philadelphia'),
    (15, 'Olivia Wilson',      'Female', '1987-01-16', 'West',  'Colorado',       'Denver'),
    (16, 'Peter Martinez',     'Male',   '1963-05-22', 'South', 'Virginia',       'Richmond'),
    (17, 'Quinn Thompson',     'Female', '1994-10-09', 'East',  'Rhode Island',   'Providence'),
    (18, 'Robert Anderson',    'Male',   '1958-03-17', 'North', 'Connecticut',    'Hartford'),
    (19, 'Sarah Jackson',      'Female', '1986-08-12', 'South', 'Texas',          'Dallas'),
    (20, 'Thomas White',       'Male',   '1979-12-25', 'West',  'Arizona',        'Phoenix'),
    (21, 'Uma Harris',         'Female', '1993-04-05', 'North', 'New York',       'Buffalo'),
    (22, 'Victor Clark',       'Male',   '1967-07-31', 'East',  'Maine',          'Portland'),
    (23, 'Wendy Lewis',        'Female', '1982-09-14', 'South', 'Florida',        'Orlando'),
    (24, 'Xavier Robinson',    'Male',   '1989-02-08', 'West',  'California',     'San Diego'),
    (25, 'Yvonne Walker',      'Female', '1976-06-20', 'North', 'New Jersey',     'Jersey City'),
    (26, 'Zachary Hall',       'Male',   '1984-11-03', 'East',  'Vermont',        'Burlington'),
    (27, 'Amanda Young',       'Female', '1997-01-27', 'South', 'Georgia',        'Savannah'),
    (28, 'Brian Allen',        'Male',   '1971-08-16', 'West',  'Washington',     'Tacoma'),
    (29, 'Catherine Scott',    'Female', '1980-03-11', 'North', 'Pennsylvania',   'Pittsburgh'),
    (30, 'Daniel Green',       'Male',   '1969-10-29', 'South', 'North Carolina', 'Raleigh'),
]

# (policy_id, holder_id, insurance_type, plan_name, premium, coverage, start, end, status)
POLICIES = [
    (101, 1,  'Health', 'Gold Plan',       1200, 500000,  '2020-01-01', 'NULL', 'Active'),
    (102, 2,  'Auto',   'Comprehensive',    800, 200000,  '2019-03-15', 'NULL', 'Active'),
    (103, 3,  'Home',   'Standard',         600, 300000,  '2019-06-01', 'NULL', 'Active'),
    (104, 4,  'Life',   'Term 20yr',       1500,1000000,  '2019-01-01', "'2039-01-01'", 'Active'),
    (105, 5,  'Health', 'Silver Plan',      900, 250000,  '2021-01-01', 'NULL', 'Active'),
    (106, 1,  'Auto',   'Liability',        400, 100000,  '2020-01-01', 'NULL', 'Active'),
    (107, 3,  'Health', 'Bronze Plan',      600, 150000,  '2021-02-01', 'NULL', 'Active'),
    (108, 6,  'Home',   'Premium',          750, 400000,  '2018-05-01', 'NULL', 'Active'),
    (109, 7,  'Auto',   'Full Coverage',    950, 250000,  '2020-08-01', 'NULL', 'Active'),
    (110, 8,  'Health', 'Gold Plan',       1200, 500000,  '2019-04-01', 'NULL', 'Active'),
    (111, 9,  'Life',   'Term 30yr',       2000, 750000,  '2018-09-01', "'2048-09-01'", 'Active'),
    (112, 10, 'Auto',   'Comprehensive',    700, 180000,  '2020-11-01', 'NULL', 'Active'),
    (113, 11, 'Health', 'Platinum Plan',   1800,1000000,  '2019-07-01', 'NULL', 'Active'),
    (114, 12, 'Home',   'Standard',         550, 280000,  '2020-02-01', 'NULL', 'Active'),
    (115, 13, 'Auto',   'Liability',        350,  80000,  '2021-04-01', 'NULL', 'Active'),
    (116, 14, 'Life',   'Whole Life',      3000,2000000,  '2017-01-01', 'NULL', 'Active'),
    (117, 15, 'Health', 'Silver Plan',      900, 250000,  '2020-06-01', 'NULL', 'Active'),
    (118, 16, 'Home',   'Premium',          800, 450000,  '2019-03-01', 'NULL', 'Active'),
    (119, 17, 'Auto',   'Full Coverage',   1000, 260000,  '2021-07-01', 'NULL', 'Active'),
    (120, 18, 'Health', 'Bronze Plan',      600, 150000,  '2020-09-01', 'NULL', 'Active'),
    (121, 19, 'Auto',   'Comprehensive',    750, 200000,  '2019-12-01', 'NULL', 'Active'),
    (122, 20, 'Life',   'Term 20yr',       1400, 800000,  '2018-07-01', "'2038-07-01'", 'Active'),
    (123, 21, 'Health', 'Gold Plan',       1200, 500000,  '2020-04-01', 'NULL', 'Active'),
    (124, 22, 'Home',   'Standard',         580, 290000,  '2021-01-01', 'NULL', 'Active'),
    (125, 23, 'Auto',   'Liability',        380,  90000,  '2020-10-01', 'NULL', 'Active'),
    (126, 24, 'Health', 'Silver Plan',      850, 230000,  '2019-08-01', 'NULL', 'Active'),
    (127, 25, 'Life',   'Term 30yr',       1800, 700000,  '2018-11-01', "'2048-11-01'", 'Active'),
    (128, 26, 'Auto',   'Comprehensive',    720, 190000,  '2020-05-01', 'NULL', 'Active'),
    (129, 27, 'Health', 'Bronze Plan',      580, 140000,  '2021-03-01', 'NULL', 'Active'),
    (130, 28, 'Home',   'Premium',          900, 500000,  '2019-06-01', 'NULL', 'Active'),
    (131, 29, 'Auto',   'Full Coverage',    980, 255000,  '2020-12-01', 'NULL', 'Active'),
    (132, 30, 'Health', 'Gold Plan',       1100, 480000,  '2019-10-01', 'NULL', 'Active'),
    (133, 6,  'Auto',   'Liability',        380,  85000,  '2019-02-01', 'NULL', 'Active'),
    (134, 8,  'Auto',   'Comprehensive',    780, 195000,  '2020-07-01', 'NULL', 'Active'),
    (135, 10, 'Home',   'Standard',         560, 270000,  '2021-05-01', 'NULL', 'Active'),
    (136, 12, 'Health', 'Silver Plan',      880, 240000,  '2020-03-01', 'NULL', 'Active'),
    (137, 14, 'Auto',   'Comprehensive',    760, 185000,  '2019-09-01', 'NULL', 'Active'),
    (138, 16, 'Life',   'Term 20yr',       1350, 750000,  '2018-04-01', "'2038-04-01'", 'Active'),
    (139, 18, 'Auto',   'Liability',        360,  82000,  '2021-06-01', 'NULL', 'Active'),
    (140, 20, 'Health', 'Bronze Plan',      570, 145000,  '2020-08-01', 'NULL', 'Active'),
    (141, 22, 'Auto',   'Comprehensive',    730, 192000,  '2019-11-01', 'NULL', 'Active'),
    (142, 24, 'Life',   'Term 30yr',       1750, 680000,  '2018-08-01', "'2048-08-01'", 'Active'),
    (143, 26, 'Health', 'Silver Plan',      870, 235000,  '2020-01-01', 'NULL', 'Active'),
    (144, 28, 'Auto',   'Liability',        370,  87000,  '2021-04-01', 'NULL', 'Active'),
    (145, 4,  'Auto',   'Comprehensive',    850, 220000,  '2020-06-01', 'NULL', 'Active'),
    (146, 7,  'Health', 'Gold Plan',       1150, 490000,  '2019-05-01', 'NULL', 'Active'),
    (147, 11, 'Auto',   'Liability',        390,  88000,  '2020-11-01', 'NULL', 'Active'),
    (148, 15, 'Home',   'Basic',            450, 200000,  '2021-02-01', 'NULL', 'Active'),
    (149, 19, 'Health', 'Platinum Plan',   1850,1050000,  '2020-01-01', 'NULL', 'Active'),
    (150, 23, 'Life',   'Term 20yr',       1300, 700000,  '2019-04-01', "'2039-04-01'", 'Active'),
]

# Map policy_id -> (holder_id, insurance_type)
POLICY_MAP = {p[0]: (p[1], p[2]) for p in POLICIES}

# Claim type by insurance type
CLAIM_TYPES = {
    'Auto':   ['Accident', 'Theft', 'Liability'],
    'Health': ['Medical'],
    'Home':   ['Fire', 'Theft', 'Natural Disaster'],
    'Life':   ['Medical'],
}

DENIAL_REASONS = [
    'Pre-existing condition',
    'Policy lapsed',
    'Claim exceeds coverage limit',
    'Fraudulent documentation',
    'Incident not covered under policy',
    'Late filing',
]

# Amount ranges by insurance type
AMOUNT_RANGES = {
    'Auto':   (1500,  25000),
    'Health': (800,   60000),
    'Home':   (5000, 120000),
    'Life':   (20000,300000),
}

def rand_date(start: date, end: date) -> date:
    return start + timedelta(days=random.randint(0, (end - start).days))

def build_claims():
    """120 claims: 2023-01-01 to 2024-12-31, weighted toward North region."""
    START = date(2025, 1, 1)
    END   = date(2026, 7, 15)

    # Force high-claim holders so sample question "holders with 3+ claims" works
    forced = [
        # (policy_id, count)  — these holders get multiple claims
        (101, 5), (106, 4),   # Alice (North) — 9 claims
        (104, 4), (145, 3),   # David (West)  — 7 claims
        (110, 4), (134, 3),   # Henry (South) — 7 claims
        (116, 3), (137, 3),   # Nathan (North)— 6 claims
        (103, 3), (107, 3),   # Carol (South) — 6 claims
    ]
    pool = []
    for pid, cnt in forced:
        pool.extend([pid] * cnt)

    # Fill to 120 with remaining policies (excluding already-used ones)
    remaining_policies = [p[0] for p in POLICIES]
    while len(pool) < 120:
        pid = random.choice(remaining_policies)
        pool.append(pid)

    random.shuffle(pool)
    pool = pool[:120]

    claims = []
    statuses = (['Approved'] * 48 + ['Settled'] * 36 +
                ['Denied'] * 24 + ['Pending'] * 12)
    random.shuffle(statuses)

    for i, (pid, status) in enumerate(zip(pool, statuses)):
        cid = 1001 + i
        holder_id, ins_type = POLICY_MAP[pid]
        lo, hi = AMOUNT_RANGES[ins_type]
        claim_amount = round(random.uniform(lo, hi), 2)

        claim_date    = rand_date(START, END)
        incident_date = claim_date - timedelta(days=random.randint(1, 5))

        if status == 'Approved':
            approved_amount = round(claim_amount * random.uniform(0.85, 1.0), 2)
            denial_reason   = 'NULL'
            settlement_date = 'NULL'
        elif status == 'Settled':
            approved_amount = round(claim_amount * random.uniform(0.80, 0.98), 2)
            denial_reason   = 'NULL'
            settlement_date = f"'{claim_date + timedelta(days=random.randint(15, 45))}'"
        elif status == 'Denied':
            approved_amount = 0.00
            denial_reason   = f"'{random.choice(DENIAL_REASONS)}'"
            settlement_date = 'NULL'
        else:  # Pending
            approved_amount = 'NULL'
            denial_reason   = 'NULL'
            settlement_date = 'NULL'

        claim_type = random.choice(CLAIM_TYPES[ins_type])
        claims.append((
            cid, pid, holder_id,
            f"'{claim_date}'", f"'{incident_date}'",
            claim_amount, approved_amount,
            status, denial_reason, settlement_date,
            claim_type,
        ))

    return claims


def main():
    claims = build_claims()

    lines = []
    lines.append("-- Full seed data: 30 holders, 50 policies, 120 claims")
    lines.append("-- Run in a Snowflake worksheet as ACCOUNTADMIN or SYSADMIN")
    lines.append("")
    lines.append("USE DATABASE INSURANCE_DB;")
    lines.append("USE SCHEMA CLAIMS;")
    lines.append("")
    lines.append("-- Clear existing data (FK-safe order)")
    lines.append("DELETE FROM FACT_CLAIMS;")
    lines.append("DELETE FROM DIM_POLICY;")
    lines.append("DELETE FROM DIM_POLICY_HOLDER;")
    lines.append("")

    # Holders
    lines.append("INSERT INTO DIM_POLICY_HOLDER")
    lines.append("  (policy_holder_id,full_name,gender,date_of_birth,region,state,city,agent_id)")
    lines.append("VALUES")
    rows = []
    for h in HOLDERS:
        hid, name, gender, dob, region, state, city = h
        rows.append(f"  ({hid},'{name}','{gender}','{dob}','{region}','{state}','{city}',NULL)")
    lines.append(",\n".join(rows) + ";")
    lines.append("")

    # Policies
    lines.append("INSERT INTO DIM_POLICY")
    lines.append("  (policy_id,policy_holder_id,insurance_type,plan_name,premium_amount,")
    lines.append("   coverage_amount,start_date,end_date,policy_status)")
    lines.append("VALUES")
    rows = []
    for p in POLICIES:
        pid, hid, ins, plan, prem, cov, start, end, status = p
        rows.append(
            f"  ({pid},{hid},'{ins}','{plan}',{prem},{cov},'{start}',{end},'{status}')"
        )
    lines.append(",\n".join(rows) + ";")
    lines.append("")

    # Claims
    lines.append("INSERT INTO FACT_CLAIMS")
    lines.append("  (claim_id,policy_id,policy_holder_id,claim_date,incident_date,")
    lines.append("   claim_amount,approved_amount,claim_status,denial_reason,")
    lines.append("   settlement_date,claim_type)")
    lines.append("VALUES")
    rows = []
    for c in claims:
        cid, pid, hid, cd, ind, ca, aa, st, dr, sd, ct = c
        rows.append(
            f"  ({cid},{pid},{hid},{cd},{ind},{ca},{aa},'{st}',{dr},{sd},'{ct}')"
        )
    lines.append(",\n".join(rows) + ";")
    lines.append("")
    lines.append("-- Verify")
    lines.append("SELECT 'holders' AS tbl, COUNT(*) AS n FROM DIM_POLICY_HOLDER")
    lines.append("UNION ALL SELECT 'policies', COUNT(*) FROM DIM_POLICY")
    lines.append("UNION ALL SELECT 'claims',   COUNT(*) FROM FACT_CLAIMS;")

    output = "\n".join(lines)
    out_path = "sql/04_load_full_data.sql"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(output)
    print(f"Written {len(claims)} claims to {out_path}")


if __name__ == "__main__":
    main()
