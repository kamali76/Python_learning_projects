"""
Configuration Management using Pydantic Settings.

This module handles all application configuration from environment variables.
Pydantic automatically validates types and provides defaults.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    Why Pydantic Settings:
    - Type validation (DATABASE_URL must be a string)
    - Default values
    - Automatic .env file loading
    - IDE autocomplete support
    """

    # Database
    DATABASE_URL: str

    # JWT Settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Application
    DEBUG: bool = False
    APP_NAME: str = "Auth Service API"
    APP_VERSION: str = "1.0.0"

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8080"

    @property
    def cors_origins_list(self) -> List[str]:
        """Convert comma-separated CORS origins to list"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


# Create global settings instance
settings = Settings()