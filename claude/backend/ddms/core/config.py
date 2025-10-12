"""Application configuration using pydantic-settings."""

from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Environment
    environment: Literal["development", "production", "test"] = Field(
        default="development",
        description="Runtime environment",
    )

    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://ddms:password@localhost:5433/ddms",
        description="PostgreSQL database URL",
    )

    # Security
    secret_key: str = Field(
        default="dev-secret-key-change-in-production",
        description="Secret key for JWT signing",
    )

    # Application
    debug: bool = Field(
        default=True,
        description="Enable debug mode",
    )

    api_version: str = Field(
        default="0.1.0",
        description="API version",
    )

    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Logging level",
    )

    log_format: Literal["json", "text"] = Field(
        default="json",
        description="Log output format",
    )


# Global settings instance
settings = Settings()
