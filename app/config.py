from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()

class Settings(BaseSettings):
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    openai_model: str | None = Field(default="gpt-4o-mini", alias="OPENAI_MODEL")

    tavily_api_key: str | None = Field(default=None, alias="TAVILY_API_KEY")

    google_credentials_file: str = Field(
        default="credentials.json",
        alias="GOOGLE_CREDENTIALS_FILE"
    )

    google_token_file: str = Field(
        default="token.json",
        alias="GOOGLE_TOKEN_FILE"
    )

    calendar_days_ahead: int = Field(
        default=7,
        alias="CALENDAR_DAYS_AHEAD"
    )

    model_config = SettingsConfigDict(
        extra="ignore",
        populate_by_name=True
    )

    google_calendar_id: str = Field(
        default="primary",
        alias="GOOGLE_CALENDAR_ID"
    )
    
@lru_cache
def get_settings() -> Settings:
    return Settings()