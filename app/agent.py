"""LangGraph pipeline: interpret → generate SQL → execute → recover → answer."""
import json
from typing import TypedDict

from langgraph.graph import END, StateGraph

from app.llm import get_llm
from app.snowflake_connector import run_query
from app.sql_guard import is_safe_sql

MAX_RETRIES = 2
MAX_PREVIEW_ROWS = 20


class AgentState(TypedDict):
    question: str
    schema: str
    history: list[dict]   # [{"role": "user"|"assistant", "content": str}]
    api_key: str
    sql: str
    result_json: str
    answer: str
    error: str
    retries: int


# ── Nodes ─────────────────────────────────────────────────────────────────────

def generate_sql(state: AgentState) -> dict:
    history_lines = ""
    for msg in state["history"][-6:]:
        role = "User" if msg["role"] == "user" else "Assistant"
        history_lines += f"{role}: {msg['content']}\n"

    prompt = f"""You are a SQL expert for a Snowflake insurance claims data warehouse.

SCHEMA:
{state['schema']}

CONVERSATION HISTORY (for context on follow-up questions):
{history_lines or "(none)"}

Current question: {state['question']}

Rules:
- Write a valid Snowflake SQL SELECT query.
- Never use INSERT, UPDATE, DELETE, DROP, CREATE, ALTER, TRUNCATE, or any DML/DDL.
- ALWAYS use fully qualified three-part names: INSURANCE_DB.CLAIMS.tablename
  Write: FROM INSURANCE_DB.CLAIMS.V_CLAIMS_SUMMARY
  Write: FROM INSURANCE_DB.CLAIMS.FACT_CLAIMS
  NEVER write: FROM V_CLAIMS_SUMMARY or FROM INSURANCE_DB.V_CLAIMS_SUMMARY
- Use V_CLAIMS_SUMMARY for simple single-topic questions; JOIN tables when needed.
- Add LIMIT 50 for detail/row-level queries. For aggregation/GROUP BY queries do NOT add LIMIT — return all groups so charts show all categories.
- If the question is too ambiguous to answer, respond with exactly:
  CLARIFY: <one specific question to ask the user>
- Return ONLY raw SQL or the CLARIFY line. No markdown fences, no explanation.
"""
    response = get_llm(state["api_key"]).invoke(prompt)
    sql = response.content.strip().removeprefix("```sql").removesuffix("```").strip()
    return {"sql": sql, "error": "", "retries": 0}


def execute_sql(state: AgentState) -> dict:
    sql = state["sql"]

    if sql.upper().startswith("CLARIFY:"):
        clarification = sql[8:].strip()
        return {"answer": clarification, "error": "CLARIFY", "result_json": ""}

    if not is_safe_sql(sql):
        return {
            "error": "BLOCKED",
            "result_json": "",
            "answer": "I can only run SELECT queries on this data. Please ask a read-only question.",
        }

    try:
        df = run_query(sql)
        return {"result_json": df.to_json(orient="records"), "error": ""}
    except Exception as exc:
        return {"result_json": "", "error": str(exc)}


def fix_sql(state: AgentState) -> dict:
    prompt = f"""You are a SQL expert. Fix the Snowflake SQL query below that failed.

SCHEMA:
{state['schema']}

Original question: {state['question']}

Failed SQL:
{state['sql']}

Error message:
{state['error']}

Always use fully qualified names: INSURANCE_DB.CLAIMS.tablename
Return ONLY the corrected SQL. No markdown, no explanation.
"""
    response = get_llm(state["api_key"]).invoke(prompt)
    sql = response.content.strip().removeprefix("```sql").removesuffix("```").strip()
    return {"sql": sql, "retries": state["retries"] + 1}


def format_answer(state: AgentState) -> dict:
    # Terminal states already have an answer set
    if state.get("error") in ("CLARIFY", "BLOCKED"):
        return {}

    result_json = state.get("result_json", "")
    if not result_json or result_json == "[]":
        return {"answer": "No data matched that query. Try rephrasing or ask about a different time period."}

    if state.get("error"):
        return {
            "answer": (
                f"I couldn't answer that after {state['retries']} attempt(s). "
                f"Last error: {state['error']}"
            )
        }

    records = json.loads(result_json)
    preview = json.dumps(records[:MAX_PREVIEW_ROWS], indent=2)

    prompt = f"""You are a data analyst. Answer the business question below using the query results.

Question: {state['question']}

Results (up to {MAX_PREVIEW_ROWS} of {len(records)} rows shown):
{preview}

Write a concise, specific answer in 2-3 sentences. Include key numbers. Do not mention SQL.
"""
    response = get_llm(state["api_key"]).invoke(prompt)
    return {"answer": response.content.strip()}


# ── Routing ───────────────────────────────────────────────────────────────────

def route_after_execute(state: AgentState) -> str:
    error = state.get("error", "")
    if error and error not in ("CLARIFY", "BLOCKED"):
        return "fix"
    return "done"


def route_after_fix(state: AgentState) -> str:
    return "retry" if state["retries"] < MAX_RETRIES else "give_up"


# ── Graph ─────────────────────────────────────────────────────────────────────

def _build_graph() -> StateGraph:
    g = StateGraph(AgentState)
    g.add_node("generate_sql", generate_sql)
    g.add_node("execute_sql", execute_sql)
    g.add_node("fix_sql", fix_sql)
    g.add_node("format_answer", format_answer)

    g.set_entry_point("generate_sql")
    g.add_edge("generate_sql", "execute_sql")
    g.add_conditional_edges(
        "execute_sql",
        route_after_execute,
        {"fix": "fix_sql", "done": "format_answer"},
    )
    g.add_conditional_edges(
        "fix_sql",
        route_after_fix,
        {"retry": "execute_sql", "give_up": "format_answer"},
    )
    g.add_edge("format_answer", END)
    return g


graph = _build_graph().compile()


def run_agent(question: str, schema: str, history: list[dict], api_key: str) -> dict:
    """Returns dict with keys: answer, sql, result_json, retries."""
    initial: AgentState = {
        "question": question,
        "schema": schema,
        "history": history,
        "api_key": api_key,
        "sql": "",
        "result_json": "",
        "answer": "",
        "error": "",
        "retries": 0,
    }
    final = graph.invoke(initial)
    return {
        "answer": final.get("answer", ""),
        "sql": final.get("sql", ""),
        "result_json": final.get("result_json", ""),
        "retries": final.get("retries", 0),
    }
