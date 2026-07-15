import streamlit as st
from pathlib import Path


@st.cache_data
def load_schema() -> str:
    path = Path(__file__).parent.parent / "sql" / "schema_description.md"
    return path.read_text(encoding="utf-8")
