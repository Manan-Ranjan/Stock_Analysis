"""
Main FastAPI Application for Real-Time Stock Analysis Platform
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import sys
from datetime import datetime

from app.core.config import settings

# Configure logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

# Optional imports - gracefully handle missing dependencies
DATABASE_AVAILABLE = False
STREAMING_AVAILABLE = False

try:
    from app.core.database import init_db, close_redis
    DATABASE_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Database module not available - running without Redis/PostgreSQL: {e}")

try:
    from app.services.streaming import streamer
    STREAMING_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Streaming module not available: {e}")

# Use simple websocket without Redis dependency
from app.api.v1.endpoints import websocket_simple as websocket


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    # Startup
    logger.info("Starting Real-Time Stock Analysis Platform...")
    
    # Initialize database (if available)
    if DATABASE_AVAILABLE:
        try:
            init_db()
            logger.info("Database initialized")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
    else:
        logger.info("Running without database - using in-memory storage")
    
    # Start real-time streaming (if available)
    if STREAMING_AVAILABLE and settings.ENABLE_REAL_TIME_STREAMING:
        try:
            await streamer.start_streaming()
            logger.info("Real-time streaming started")
        except Exception as e:
            logger.error(f"Failed to start streaming: {e}")
    
    logger.info(f"Application started successfully on {settings.API_HOST}:{settings.API_PORT}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    
    # Stop streaming (if available)
    if STREAMING_AVAILABLE and settings.ENABLE_REAL_TIME_STREAMING:
        try:
            await streamer.stop_streaming()
            logger.info("Streaming stopped")
        except Exception as e:
            logger.error(f"Error stopping streaming: {e}")
    
    # Close Redis connection (if available)
    if DATABASE_AVAILABLE:
        try:
            await close_redis()
            logger.info("Redis connection closed")
        except Exception as e:
            logger.error(f"Error closing Redis: {e}")
    
    logger.info("Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Real-time stock analysis platform with live data streaming, predictive analytics, and intelligent trading features",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc) if settings.DEBUG else "An error occurred",
            "timestamp": datetime.now().isoformat()
        }
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.now().isoformat()
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Real-Time Stock Analysis Platform API",
        "version": settings.APP_VERSION,
        "docs": "/docs" if settings.DEBUG else "Documentation disabled in production",
        "websocket": "/api/v1/ws",
        "timestamp": datetime.now().isoformat()
    }


# Include routers
app.include_router(
    websocket.router,
    prefix="/api/v1",
    tags=["WebSocket"]
)


# Startup message
@app.on_event("startup")
async def startup_message():
    """Print startup message"""
    logger.info("="*70)
    logger.info(f"  {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info("="*70)
    logger.info(f"  Environment: {settings.ENVIRONMENT}")
    logger.info(f"  Debug Mode: {settings.DEBUG}")
    logger.info(f"  API Docs: http://{settings.API_HOST}:{settings.API_PORT}/docs")
    logger.info(f"  WebSocket: ws://{settings.API_HOST}:{settings.API_PORT}/api/v1/ws")
    logger.info("="*70)


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        workers=1 if settings.DEBUG else settings.API_WORKERS,
        log_level=settings.LOG_LEVEL.lower()
    )

# Made with Bob
