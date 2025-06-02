import os
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, Field, field_validator
from pydantic_settings import BaseSettings


class LogLevel(str, Enum):
    """Valid logging levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Environment(str, Enum):
    """Application environment types."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class Settings(BaseSettings):
    """
    Application settings with type validation using Pydantic.
    
    Loads values from environment variables and provides defaults.
    Uses nested classes to organize settings by category.
    """

    # General settings
    APP_NAME: str = "SentimentFlow API"
    ENVIRONMENT: Environment = Environment.DEVELOPMENT
    DEBUG: bool = Field(True, description="Enable debug mode")
    LOG_LEVEL: LogLevel = LogLevel.INFO
    LOG_FILE: Optional[str] = Field(None, description="Path to log file (if None, logs to stdout only)")

    # API settings
    API_V1_PREFIX: str = "/api/v1"
    API_TITLE: str = "SentimentFlow API"
    API_DESCRIPTION: str = "A microservices-based sentiment analysis API with cloud integration"
    API_VERSION: str = "0.1.0"
    DOCS_URL: str = "/docs"
    REDOC_URL: str = "/redoc"
    OPENAPI_URL: str = "/openapi.json"
    
    # CORS settings
    CORS_ORIGINS: List[str] = Field(
        ["*"],
        description="CORS allowed origins. Use ['*'] for allowing all or specific domains"
    )
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]

    # Database settings
    MONGODB_URL: Optional[str] = Field(
        None, 
        description="MongoDB connection string. Required in production."
    )
    MONGODB_DB_NAME: str = "sentimentflow"
    MONGODB_CONNECT_TIMEOUT_MS: int = 5000
    MONGODB_SOCKET_TIMEOUT_MS: int = 10000
    
    # Redis settings
    REDIS_URL: Optional[str] = Field(
        None,
        description="Redis connection string. If provided, enables caching."
    )
    REDIS_CACHE_EXPIRATION: int = Field(
        3600, 
        description="Default cache expiration time in seconds"
    )
    
    # Security settings (will be expanded in future phases)
    API_KEY_HEADER: str = "X-API-Key"
    SECRET_KEY: str = Field(
        "development_secret_key",
        description="Secret key for signing tokens. Must be changed in production."
    )
    
    # ML model settings
    MODEL_PATH: str = Field(
        "./data/models",
        description="Path to directory containing ML models"
    )
    DEFAULT_MODEL: str = "distilbert-base-uncased-finetuned-sst-2-english"
    TEXT_MAX_LENGTH: int = 512
    BATCH_SIZE: int = 16
    MAX_BATCH_SIZE: int = Field(
        100,
        description="Maximum number of texts allowed in batch requests"
    )
    
    # Rate limiting
    RATE_LIMIT_ENABLED: bool = Field(
        False,
        description="Enable rate limiting. Recommended for production."
    )
    RATE_LIMIT_DEFAULT: str = "100/minute"
    
    # Performance settings
    WORKERS_COUNT: int = Field(
        1, 
        description="Number of worker processes. Set to 0 to use CPU count."
    )
    
    # Cloud settings (for future phases)
    CLOUD_PROVIDER: Optional[str] = Field(
        None,
        description="Cloud provider (aws, azure, or None for local)"
    )
    
    @field_validator("ENVIRONMENT", mode="before")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate and normalize environment value."""
        if isinstance(v, str):
            return v.lower()
        return v
    
    @field_validator("MONGODB_URL")
    @classmethod
    def validate_mongodb_url(cls, v: Optional[str], info: Any) -> Optional[str]:
        """Validate MongoDB URL based on environment."""
        values = info.data
        if values.get("ENVIRONMENT") == Environment.PRODUCTION and not v:
            raise ValueError("MONGODB_URL is required in production environment")
        return v
    
    @field_validator("WORKERS_COUNT")
    @classmethod
    def validate_workers_count(cls, v: int) -> int:
        """Validate and adjust workers count."""
        if v < 0:
            raise ValueError("WORKERS_COUNT must be a non-negative integer")
        if v == 0:
            import multiprocessing
            return multiprocessing.cpu_count()
        return v
    
    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str, info: Any) -> str:
        """Warn about default secret key in production."""
        values = info.data
        if values.get("ENVIRONMENT") == Environment.PRODUCTION and v == "development_secret_key":
            import logging
            logging.warning(
                "WARNING: Using default SECRET_KEY in production environment. "
                "This is insecure and should be changed."
            )
        return v

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "arbitrary_types_allowed": True,
        "extra": "ignore"
    }


# Create a singleton instance to be imported by other modules
settings = Settings()
