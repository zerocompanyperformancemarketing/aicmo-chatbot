from langchain_openai import ChatOpenAI
from config import Config


def get_llm(temperature: float = 0.0) -> ChatOpenAI:
    """Return a ChatOpenAI instance configured for OpenRouter."""
    return ChatOpenAI(
        base_url=Config.OPENROUTER_BASE_URL,
        api_key=Config.OPENROUTER_API_KEY,
        model=Config.OPENROUTER_MODEL,
        temperature=temperature,
    )
