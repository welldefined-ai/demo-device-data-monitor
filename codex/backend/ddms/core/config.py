from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    env: str = Field("development", description="Application environment")
    database_url: str = Field(
        default="postgresql+psycopg://postgres:postgres@localhost:5432/ddms",
        description="SQLAlchemy database URL",
    )
    secret_key: str = Field("change-me", description="JWT signing secret")
    jwt_algorithm: str = Field("HS256", description="JWT algorithm")

    model_config = SettingsConfigDict(env_file=".env", env_prefix="DDMS_", case_sensitive=False)

