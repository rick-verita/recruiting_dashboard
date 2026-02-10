"""Application configuration loaded from environment variables."""

from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application
    debug: bool = False
    log_level: str = "INFO"

    # Database
    database_url: str = Field(
        ...,
        description="PostgreSQL connection string",
    )

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
