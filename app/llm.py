"""Single LLM interface — swap provider/model here only."""
import streamlit as st
from langchain_openai import ChatOpenAI


def get_llm(temperature: float = 0.0) -> ChatOpenAI:
    return ChatOpenAI(
        model="gpt-4o-mini",
        temperature=temperature,
        api_key=st.secrets["openai"]["api_key"],
    )
