"""
Database configuration and session management
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import redis.asyncio as aioredis
from redis.asyncio import Redis

from app.core.config import settings

# PostgreSQL Database Engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_pre_ping=True,
    echo=settings.DEBUG
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Redis connection pool
redis_pool = None


async def get_redis() -> Redis:
    """Get Redis connection"""
    global redis_pool
    if redis_pool is None:
        redis_pool = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            max_connections=settings.REDIS_MAX_CONNECTIONS
        )
    return redis_pool


async def close_redis():
    """Close Redis connection"""
    global redis_pool
    if redis_pool:
        await redis_pool.close()


def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency
    Usage: db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)


def drop_db():
    """Drop all database tables (use with caution!)"""
    Base.metadata.drop_all(bind=engine)

# Made with Bob
