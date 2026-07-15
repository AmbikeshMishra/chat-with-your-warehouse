import streamlit as st
import snowflake.connector
import pandas as pd


@st.cache_resource
def get_connection():
    cfg = st.secrets["snowflake"]
    account = cfg["account"].replace(".snowflakecomputing.com", "")
    return snowflake.connector.connect(
        account=account,
        user=cfg["user"],
        password=cfg["password"],
        warehouse=cfg["warehouse"],
        database=cfg["database"],
        schema=cfg["schema"],
        role=cfg["role"],
    )


def run_query(sql: str) -> pd.DataFrame:
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(sql)
        return cur.fetch_pandas_all()
