"""Single LLM interface — swap provider/model here only."""
from langchain_openai import ChatOpenAI


def get_llm(api_key: str, temperature: float = 0.0) -> ChatOpenAI:
    return ChatOpenAI(
        model="gpt-4o-mini",
        temperature=temperature,
        api_key=api_key,
    )
