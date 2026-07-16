import json

import pandas as pd
import plotly.express as px
import streamlit as st

from app.agent import run_agent
from app.schema_loader import load_schema

# ── Config ────────────────────────────────────────────────────────────────────

MAX_REQUESTS_PER_SESSION = 20

SAMPLE_QUESTIONS = [
    "Which region had the highest claim payouts last quarter?",
    "What is the average claim amount by insurance type?",
    "How many claims were filed per month this year?",
    "Which policy holders have more than 3 claims?",
    "What percentage of claims were denied vs approved?",
    "Show me the top 5 largest approved claims.",
    "What is the total payout by claim type?",
]

st.set_page_config(page_title="Chat with Your Warehouse", page_icon="❄️", layout="wide")


# ── Session state init ─────────────────────────────────────────────────────────

if "messages" not in st.session_state:
    st.session_state.messages = []   # [{"role": ..., "content": ..., "sql": ..., "result_json": ...}]
if "request_count" not in st.session_state:
    st.session_state.request_count = 0


# ── Helpers ────────────────────────────────────────────────────────────────────

def _try_chart(result_json: str) -> None:
    if not result_json or result_json == "[]":
        return
    try:
        df = pd.DataFrame(json.loads(result_json))
    except Exception:
        return
    if df.empty:
        return

    # Try to coerce object columns to datetime, then numeric
    for col in df.select_dtypes(include="object").columns:
        try:
            df[col] = pd.to_datetime(df[col])
        except Exception:
            try:
                df[col] = pd.to_numeric(df[col])
            except Exception:
                pass

    numeric = df.select_dtypes(include="number").columns.tolist()
    dates   = df.select_dtypes(include=["datetime", "datetimetz"]).columns.tolist()
    cats    = df.select_dtypes(include=["object", "category"]).columns.tolist()

    if not numeric:
        return

    # Single-row wide result (e.g. pct_approved + pct_denied columns) → melt to long format
    if len(df) == 1 and len(numeric) > 1 and not dates and not cats:
        melted = df[numeric].T.reset_index()
        melted.columns = ["category", "value"]
        fig = px.bar(melted, x="category", y="value")
        st.plotly_chart(fig, use_container_width=True)
        return

    # Columns whose name suggests they are IDs or dimensions, not measures
    id_cols = [c for c in numeric if c.lower().endswith("_id") or c.lower() == "id"]
    # Promote ID columns to categorical so they become x-axis candidates
    for col in id_cols:
        df[col] = df[col].astype(str)
        numeric.remove(col)
        cats.append(col)

    if not numeric:
        return

    # Exclude date-like numeric columns (e.g. Unix timestamps) from measure candidates
    _date_keywords = ("date", "time", "year", "month", "day", "quarter")
    measure_candidates = [c for c in numeric if not any(k in c.lower() for k in _date_keywords)]
    if not measure_candidates:
        measure_candidates = numeric
    # Best y = measure column with largest mean absolute value
    y = max(measure_candidates, key=lambda c: df[c].abs().mean())
    x_num = [c for c in numeric if c != y]

    if dates:
        fig = px.line(df.sort_values(dates[0]), x=dates[0], y=y, markers=True)
    elif cats:
        fig = px.bar(df, x=cats[0], y=y)
    elif x_num:
        fig = px.bar(df.sort_values(x_num[0]), x=x_num[0], y=y)
    else:
        return

    st.plotly_chart(fig, use_container_width=True)


def _render_assistant_message(msg: dict) -> None:
    st.write(msg["content"])
    _try_chart(msg.get("result_json", ""))
    if msg.get("sql"):
        with st.expander("Show SQL", expanded=False):
            st.code(msg["sql"], language="sql")


def _history_for_agent() -> list[dict]:
    """Convert session messages to plain text pairs for the agent prompt."""
    out = []
    for m in st.session_state.messages:
        out.append({"role": m["role"], "content": m["content"]})
    return out


# ── Layout ─────────────────────────────────────────────────────────────────────

st.title("Chat with Your Warehouse ❄️")
st.caption("Ask your Snowflake insurance-claims data questions in plain English.")

with st.sidebar:
    st.header("Your OpenAI API key")
    api_key = st.text_input(
        "sk-...",
        type="password",
        placeholder="Paste your OpenAI API key",
        help="Your key is used only for this session and never stored.",
    )
    st.caption("[Get a key →](https://platform.openai.com/api-keys)")

    st.divider()
    st.header("Try a question")
    for q in SAMPLE_QUESTIONS:
        if st.button(q, use_container_width=True):
            st.session_state["pending_question"] = q

    st.divider()
    used = st.session_state.request_count
    st.caption(f"Requests this session: {used} / {MAX_REQUESTS_PER_SESSION}")
    if st.button("Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.request_count = 0
        st.rerun()

# Render history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant":
            _render_assistant_message(msg)
        else:
            st.write(msg["content"])

# Collect input (typed or sidebar button)
question: str | None = st.chat_input("Ask a question about the claims data…")
if "pending_question" in st.session_state:
    question = st.session_state.pop("pending_question")

if not api_key:
    st.info("Enter your OpenAI API key in the sidebar to get started.", icon="🔑")
    st.stop()

if question:
    if st.session_state.request_count >= MAX_REQUESTS_PER_SESSION:
        st.warning("Session limit reached. Refresh the page to start a new session.")
        st.stop()

    # Show user message immediately
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.write(question)

    # Run agent
    schema = load_schema()
    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            result = run_agent(question, schema, _history_for_agent(), api_key)

        assistant_msg = {
            "role": "assistant",
            "content": result["answer"],
            "sql": result["sql"],
            "result_json": result["result_json"],
        }
        st.session_state.messages.append(assistant_msg)
        st.session_state.request_count += 1
        _render_assistant_message(assistant_msg)
