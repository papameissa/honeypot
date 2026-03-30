"""
Configuration Management for HoneyTrap
Supports: development, testing, production
"""
import os
from typing import Type
from datetime import timedelta


class BaseConfig:
    """Base configuration shared by all environments."""
    
    # Flask Core
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-change-me-in-production")
    DEBUG: bool = False
    TESTING: bool = False
    
    # Database
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    SQLALCHEMY_ECHO: bool = False
    
    # Security
    SESSION_COOKIE_SECURE: bool = True
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SAMESITE: str = "Lax"
    PERMANENT_SESSION_LIFETIME: timedelta = timedelta(hours=24)
    
    # Rate Limiting
    RATELIMIT_STORAGE_URI: str = os.getenv("REDIS_URL", "memory://")
    RATELIMIT_STRATEGY: str = "fixed-window"
    
    # CORS
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:5000"]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # "json" or "text"
    
    # API Configuration
    JSON_SORT_KEYS: bool = False
    JSONIFY_PRETTYPRINT_REGULAR: bool = False
    MAX_CONTENT_LENGTH: int = 16 * 1024 * 1024  # 16MB


class DevelopmentConfig(BaseConfig):
    """Development environment configuration."""
    
    DEBUG: bool = True
    TESTING: bool = False
    SESSION_COOKIE_SECURE: bool = False
    LOG_LEVEL: str = "DEBUG"
    SQLALCHEMY_ECHO: bool = True
    
    SQLALCHEMY_DATABASE_URI: str = os.getenv(
        "DATABASE_URL",
        "postgresql://honeytrap:strongpassword123@localhost:5432/honeytrap"
    )
    
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:5000",
        "http://127.0.0.1:5000",
    ]


class ProductionConfig(BaseConfig):
    """Production environment configuration."""
    
    DEBUG: bool = False
    TESTING: bool = False
    
    # In production, these MUST be set
    SQLALCHEMY_DATABASE_URI: str = os.getenv("DATABASE_URL")
    if not SQLALCHEMY_DATABASE_URI:
        raise ValueError("DATABASE_URL environment variable is required in production")
    
    # Security hardening
    SESSION_COOKIE_SECURE: bool = True
    SESSION_COOKIE_HTTPONLY: bool = True
    PREFERRED_URL_SCHEME: str = "https"
    
    # CORS must be explicitly configured
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "").split(",") if os.getenv("CORS_ORIGINS") else []
    
    LOG_LEVEL: str = "WARNING"
    LOG_FORMAT: str = "json"


class TestingConfig(BaseConfig):
    """Testing environment configuration."""
    
    DEBUG: bool = False
    TESTING: bool = True
    SESSION_COOKIE_SECURE: bool = False
    
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///:memory:"
    RATELIMIT_STORAGE_URI: str = "memory://"
    
    CORS_ORIGINS: list = ["*"]  # Allow all in tests
    
    LOG_LEVEL: str = "DEBUG"


# Configuration mapping
config_map: dict[str, Type[BaseConfig]] = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}


def get_config(config_name: str | None = None) -> BaseConfig:
    """Get configuration object by name."""
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")
    
    if config_name not in config_map:
        raise ValueError(f"Unknown config: {config_name}")
    
    return config_map[config_name]
