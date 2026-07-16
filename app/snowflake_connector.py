import decimal
import datetime
import streamlit as st
import snowflake.connector
import pandas as pd


@st.cache_resource
def get_connection():
    cfg = st.secrets["snowflake"]
    account = cfg["account"].replace(".snowflakecomputing.com", "")
    conn = snowflake.connector.connect(
        account=account,
        user=cfg["user"],
        password=cfg["password"],
        warehouse=cfg["warehouse"],
        database=cfg["database"],
        schema=cfg["schema"],
        role=cfg["role"],
    )
    with conn.cursor() as cur:
        cur.execute(f"USE DATABASE {cfg['database']}")
        cur.execute(f"USE SCHEMA {cfg['database']}.{cfg['schema']}")
        cur.execute(f"USE WAREHOUSE {cfg['warehouse']}")
    return conn


def _clean(val):
    """Normalise Snowflake types for pandas compatibility."""
    if isinstance(val, decimal.Decimal):
        return float(val)
    if isinstance(val, (datetime.date, datetime.datetime)):
        return val.isoformat()   # keeps as string → never treated as numeric
    return val


def run_query(sql: str) -> pd.DataFrame:
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(sql)
        rows = cur.fetchall()
        cols = [desc[0] for desc in cur.description] if cur.description else []
        cleaned = [tuple(_clean(v) for v in row) for row in rows]
        return pd.DataFrame(cleaned, columns=cols)
