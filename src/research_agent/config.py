from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import Field, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # LLM
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    llm_model: str = "gpt-4o-mini"
    llm_provider: str = "openai"
    llm_temperature: float = 0.1
    llm_max_retries: int = 3

    # Search backends
    bing_news_api_key: str = ""
    serpapi_api_key: str = ""
    tavily_api_key: str = ""
    reddit_client_id: str = ""
    reddit_client_secret: str = ""
    reddit_user_agent: str = "research-agent/0.1"

    # Storage
    database_url: str = "sqlite+aiosqlite:///data/research.db"

    # Runtime
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    debug: bool = False
    max_results_per_source: int = 10
    default_time_window_days: int = 30
    max_concurrent_fetches: int = 10
    http_timeout_seconds: int = 30
    max_response_size_bytes: int = 5 * 1024 * 1024  # 5 MB

    # Paths
    data_dir: Path = Path("data")
    intermediate_dir: Path = Field(default=Path("data/intermediate"))

    def effective_api_key(self) -> str:
        if not self.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY is not set. "
                "Create a .env file from .env.example and add your key."
            )
        return self.api_key  # type: ignore[attr-defined]

    @property
    def has_openai_key(self) -> bool:
        return bool(self.openai_api_key)

    @property
    def has_reddit_creds(self) -> bool:
        return bool(self.reddit_client_id and self.reddit_client_secret)


settings = Settings()
