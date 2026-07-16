from __future__ import annotations

from enum import StrEnum
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class LlmProvider(StrEnum):
    OPENAI = "openai"
    OLLAMA = "ollama"


LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR"]


class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables and `.env`.

    Design rules:
    - Keep provider-specific config grouped.
    - Validate impossible configurations early.
    - Avoid hiding missing credentials until a request is already running.
    - Keep derived properties side-effect free.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # -------------------------------------------------------------------------
    # LLM
    # -------------------------------------------------------------------------

    llm_provider: LlmProvider = LlmProvider.OPENAI
    llm_model: str = "gpt-4o-mini"
    llm_temperature: float = Field(default=0.1, ge=0.0, le=2.0)
    llm_max_retries: int = Field(default=3, ge=0)

    # -------------------------------------------------------------------------
    # OpenAI
    # -------------------------------------------------------------------------

    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_base_url: str | None = Field(default=None, alias="OPENAI_BASE_URL")

    # -------------------------------------------------------------------------
    # Ollama
    # -------------------------------------------------------------------------

    ollama_base_url: str = Field(
        default="http://host.docker.internal:11434",
        alias="OLLAMA_BASE_URL",
    )
    ollama_model: str = Field(
        default="deepseek-v4-flash:cloud",
        alias="OLLAMA_MODEL",
    )

    # -------------------------------------------------------------------------
    # Search backends
    # -------------------------------------------------------------------------

    bing_news_api_key: str = Field(default="", alias="BING_NEWS_API_KEY")
    serpapi_api_key: str = Field(default="", alias="SERPAPI_API_KEY")
    tavily_api_key: str = Field(default="", alias="TAVILY_API_KEY")

    reddit_client_id: str = Field(default="", alias="REDDIT_CLIENT_ID")
    reddit_client_secret: str = Field(default="", alias="REDDIT_CLIENT_SECRET")
    reddit_user_agent: str = Field(
        default="research-agent/0.1",
        alias="REDDIT_USER_AGENT",
    )

    # -------------------------------------------------------------------------
    # Storage
    # -------------------------------------------------------------------------

    database_url: str = Field(
        default="sqlite+aiosqlite:///data/research.db",
        alias="DATABASE_URL",
    )

    # -------------------------------------------------------------------------
    # Runtime
    # -------------------------------------------------------------------------

    log_level: LogLevel = Field(default="INFO", alias="LOG_LEVEL")
    debug: bool = Field(default=False, alias="DEBUG")

    max_results_per_source: int = Field(default=3, ge=1, le=100)
    default_time_window_days: int = Field(default=30, ge=1, le=3650)
    max_concurrent_fetches: int = Field(default=10, ge=1, le=100)
    http_timeout_seconds: int = Field(default=30, ge=1, le=300)
    max_response_size_bytes: int = Field(default=5 * 1024 * 1024, ge=1024)

    # -------------------------------------------------------------------------
    # Paths
    # -------------------------------------------------------------------------

    data_dir: Path = Field(default=Path("data"), alias="DATA_DIR")
    intermediate_dir: Path | None = Field(default=None, alias="INTERMEDIATE_DIR")

    # -------------------------------------------------------------------------
    # Validators
    # -------------------------------------------------------------------------

    @field_validator("ollama_base_url")
    @classmethod
    def strip_trailing_slash(cls, value: str) -> str:
        return value.rstrip("/")

    @model_validator(mode="after")
    def derive_paths(self) -> Settings:
        if self.intermediate_dir is None:
            self.intermediate_dir = self.data_dir / "intermediate"

        return self

    @model_validator(mode="after")
    def validate_selected_llm_provider(self) -> Settings:
        """
        Validate only the selected provider.

        This allows local Ollama development without OPENAI_API_KEY,
        and OpenAI development without Ollama running.
        """

        if self.llm_provider == LlmProvider.OPENAI and not self.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY is required when LLM_PROVIDER=openai. "
                "Either set OPENAI_API_KEY or use LLM_PROVIDER=ollama."
            )

        if self.llm_provider == LlmProvider.OLLAMA and not self.ollama_model:
            raise ValueError("OLLAMA_MODEL is required when LLM_PROVIDER=ollama.")

        return self

    # -------------------------------------------------------------------------
    # Derived LLM helpers
    # -------------------------------------------------------------------------

    @property
    def effective_llm_model(self) -> str:
        match self.llm_provider:
            case LlmProvider.OLLAMA:
                return self.ollama_model
            case LlmProvider.OPENAI:
                return self.llm_model

    @property
    def effective_llm_base_url(self) -> str | None:
        match self.llm_provider:
            case LlmProvider.OLLAMA:
                return self.ollama_base_url
            case LlmProvider.OPENAI:
                return self.openai_base_url

    @property
    def effective_llm_api_key(self) -> str | None:
        """
        Return the API key for providers that require one.

        Ollama local API usually does not need an API key.
        If using Ollama Cloud directly, model that separately rather than
        overloading OpenAI credentials.
        """

        match self.llm_provider:
            case LlmProvider.OPENAI:
                return self.openai_api_key
            case LlmProvider.OLLAMA:
                return None

    @property
    def uses_ollama(self) -> bool:
        return self.llm_provider == LlmProvider.OLLAMA

    @property
    def uses_openai(self) -> bool:
        return self.llm_provider == LlmProvider.OPENAI

    # -------------------------------------------------------------------------
    # Search backend helpers
    # -------------------------------------------------------------------------

    @property
    def has_openai_key(self) -> bool:
        return bool(self.openai_api_key)

    @property
    def has_tavily_key(self) -> bool:
        return bool(self.tavily_api_key)

    @property
    def has_serpapi_key(self) -> bool:
        return bool(self.serpapi_api_key)

    @property
    def has_bing_news_key(self) -> bool:
        return bool(self.bing_news_api_key)

    @property
    def has_reddit_creds(self) -> bool:
        return bool(self.reddit_client_id and self.reddit_client_secret)


settings = Settings()