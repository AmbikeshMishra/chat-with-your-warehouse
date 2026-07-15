-- Option A: Load from a public S3 CSV (Kaggle insurance dataset mirror)
-- Option B: Use the INSERT statements below for a small hand-crafted seed

-- ── OPTION A: Stage + COPY (preferred if you have an S3 URI) ─────────────────
-- CREATE STAGE IF NOT EXISTS CLAIMS_STAGE URL='s3://your-bucket/insurance/' FILE_FORMAT=(TYPE=CSV SKIP_HEADER=1);
-- COPY INTO DIM_POLICY_HOLDER FROM @CLAIMS_STAGE/policy_holders.csv;
-- COPY INTO DIM_POLICY        FROM @CLAIMS_STAGE/policies.csv;
-- COPY INTO FACT_CLAIMS        FROM @CLAIMS_STAGE/claims.csv;


-- ── OPTION B: Seed data (100-row CSV inlined; enough to validate the schema) ──

INSERT INTO DIM_POLICY_HOLDER VALUES
  (1,'Alice Sharma','Female','1980-04-12','North','New York','Albany',NULL),
  (2,'Bob Tremblay','Male','1975-09-30','East','Massachusetts','Boston',NULL),
  (3,'Carol Diaz','Female','1990-01-22','South','Texas','Houston',NULL),
  (4,'David Okafor','Male','1968-11-05','West','California','Los Angeles',NULL),
  (5,'Eva Chen','Female','1995-07-18','West','Washington','Seattle',NULL);

INSERT INTO DIM_POLICY VALUES
  (101,1,'Health','Gold Plan',1200.00,500000.00,'2023-01-01',NULL,'Active'),
  (102,2,'Auto','Comprehensive',800.00,200000.00,'2023-03-15',NULL,'Active'),
  (103,3,'Home','Standard',600.00,300000.00,'2022-06-01',NULL,'Active'),
  (104,4,'Life','Term 20yr',1500.00,1000000.00,'2021-01-01','2041-01-01','Active'),
  (105,5,'Health','Silver Plan',900.00,250000.00,'2024-01-01',NULL,'Active'),
  (106,1,'Auto','Liability',400.00,100000.00,'2023-01-01',NULL,'Active'),
  (107,3,'Health','Bronze Plan',600.00,150000.00,'2024-02-01',NULL,'Active');

INSERT INTO FACT_CLAIMS VALUES
  (1001,101,1,'2024-01-10','2024-01-08',5000.00,4800.00,'Approved',NULL,'2024-01-20','Medical'),
  (1002,102,2,'2024-01-15','2024-01-14',12000.00,NULL,'Pending',NULL,NULL,'Accident'),
  (1003,103,3,'2024-02-01','2024-01-30',8000.00,0.00,'Denied','Pre-existing damage',NULL,'Fire'),
  (1004,104,4,'2024-02-20','2024-02-18',50000.00,50000.00,'Approved',NULL,'2024-03-01','Medical'),
  (1005,105,5,'2024-03-05','2024-03-03',2000.00,1800.00,'Settled',NULL,'2024-03-15','Medical'),
  (1006,101,1,'2024-03-20','2024-03-19',3000.00,2700.00,'Approved',NULL,'2024-03-28','Medical'),
  (1007,106,1,'2024-04-01','2024-03-31',7500.00,NULL,'Pending',NULL,NULL,'Accident'),
  (1008,102,2,'2024-04-10','2024-04-09',500.00,0.00,'Denied','Policy lapsed',NULL,'Theft'),
  (1009,103,3,'2024-05-01','2024-04-28',15000.00,14000.00,'Settled',NULL,'2024-05-20','Fire'),
  (1010,107,3,'2024-06-15','2024-06-14',1200.00,1200.00,'Approved',NULL,'2024-06-22','Medical');
