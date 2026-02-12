"""Application configuration loaded from environment variables."""

from functools import lru_cache
from pathlib import Path

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _project_root() -> Path:
    """Project root (directory containing pyproject.toml)."""
    for parent in Path(__file__).resolve().parents:
        if (parent / "pyproject.toml").exists():
            return parent
    return Path.cwd()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=str(_project_root() / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    debug: bool = False
    log_level: str = "INFO"

    # Database: use RECRUITING_DATABASE_URL if set (e.g. when sharing Postgres with another app), else DATABASE_URL
    database_url: str | None = Field(None, description="PostgreSQL connection string")
    recruiting_database_url: str | None = Field(
        None,
        description="Override for this app when using an existing Postgres instance",
    )

    @model_validator(mode="after")
    def resolve_database_url(self) -> "Settings":
        url = self.recruiting_database_url or self.database_url
        if not url:
            raise ValueError("Set DATABASE_URL or RECRUITING_DATABASE_URL")
        object.__setattr__(self, "database_url", url)
        return self

    # Gmail API
    gmail_client_id: str = Field(..., description="Google OAuth2 client ID")
    gmail_client_secret: SecretStr = Field(..., description="Google OAuth2 client secret")
    gmail_refresh_token: SecretStr = Field(..., description="Gmail OAuth2 refresh token")
    gmail_processed_label: str = "Processed-EmailParser"

    # OpenAI
    openai_api_key: SecretStr = Field(..., description="OpenAI API key")
    openai_model: str = "gpt-4o"

    # Processing
    polling_interval_seconds: int = 5


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
