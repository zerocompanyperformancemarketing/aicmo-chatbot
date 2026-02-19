from langchain_openai import ChatOpenAI
from config import Config


def get_llm(temperature: float = 0.0) -> ChatOpenAI:
    """Return a ChatOpenAI instance configured for OpenAI."""
    return ChatOpenAI(
        api_key=Config.OPENAI_API_KEY,
        model=Config.OPENAI_MODEL,
        temperature=temperature,
    )
