"""
Core Configuration for Real-Time Stock Analysis Platform
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = "Real-Time Stock Analysis Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    
    # API Server
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_WORKERS: int = 4
    
    # Database
    DATABASE_URL: str = "postgresql://stockuser:stockpass@localhost:5432/stockanalysis"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL: int = 300
    REDIS_MAX_CONNECTIONS: int = 50
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8501",
        "http://localhost:8000"
    ]
    
    # External APIs
    YAHOO_FINANCE_ENABLED: bool = True
    FINNHUB_API_KEY: Optional[str] = None
    FINNHUB_ENABLED: bool = False
    NEWS_API_KEY: Optional[str] = None
    NEWS_API_ENABLED: bool = False
    
    # Notifications
    SENDGRID_API_KEY: Optional[str] = None
    EMAIL_FROM: str = "noreply@stockanalysis.com"
    EMAIL_ENABLED: bool = False
    
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_PHONE_NUMBER: Optional[str] = None
    SMS_ENABLED: bool = False
    
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_ENABLED: bool = False
    
    # WebSocket
    WS_HEARTBEAT_INTERVAL: int = 30
    WS_MAX_CONNECTIONS: int = 1000
    WS_MESSAGE_QUEUE_SIZE: int = 100
    
    # Real-Time Data
    PRICE_UPDATE_INTERVAL: int = 5
    MARKET_DATA_CACHE_TTL: int = 60
    ENABLE_REAL_TIME_STREAMING: bool = True
    
    # Machine Learning
    ML_MODEL_PATH: str = "./ml_models/saved_models"
    ML_PREDICTION_CACHE_TTL: int = 300
    ENABLE_PREDICTIONS: bool = True
    
    # Backtesting
    BACKTEST_INITIAL_CAPITAL: float = 100000
    BACKTEST_POSITION_SIZE: float = 0.1
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    SENTRY_ENABLED: bool = False
    PROMETHEUS_ENABLED: bool = True
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    LOG_FILE: str = "./logs/app.log"
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    CELERY_TASK_ALWAYS_EAGER: bool = False
    
    # Feature Flags
    ENABLE_PAPER_TRADING: bool = True
    ENABLE_SOCIAL_FEATURES: bool = False
    ENABLE_ADVANCED_ANALYTICS: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Global settings instance
settings = get_settings()

# Made with Bob
