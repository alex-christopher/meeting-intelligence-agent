from langchain_openai import ChatOpenAI

from app.config import Settings

settings = Settings()

def get_chat_model(temperature: float = 0) -> ChatOpenAI:
    if not settings.openai_api_key:
        raise ValueError("OPENAI API KEY MISSING")
    
    return ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        temperature=temperature
    )