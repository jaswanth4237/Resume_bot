import os
from typing import Dict
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    APP_ENV: str = "development"
    PORT: int = 8000
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgrespassword@localhost:5432/resumematch"
    REDIS_URL: str = "redis://localhost:6379/0"

    TELEGRAM_BOT_TOKEN: str = Field(default="", description="Telegram Bot Token")
    LLM_API_KEY: str = Field(default="", description="LLM Provider API Key")
    LLM_MODEL: str = "gpt-4o-mini"
    EMBEDDING_MODEL: str = "text-embedding-3-small"

    MAX_FILE_SIZE_MB: int = 10
    ANALYSIS_RATE_LIMIT_SECONDS: int = 60
    MATCH_THRESHOLD: float = 75.0
    SUITABLE_THRESHOLD: float = 75.0
    BORDERLINE_THRESHOLD: float = 60.0
    REJECT_THRESHOLD: float = 60.0

    LOG_LEVEL: str = "INFO"

    WEIGHTS: Dict[str, float] = {
        "skills": 0.50,
        "experience": 0.20,
        "responsibilities": 0.15,
        "education": 0.05,
        "preferred": 0.10,
    }


settings = Settings()
