"""
Qlib Advisor & Predictor Service - Main Application Entry Point

This service provides AI-powered stock predictions, portfolio analysis,
and investment recommendations using Microsoft Qlib.
"""
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.config.settings import settings
import app.utils.logger  # Initialize logger setup
from app.services.qlib_manager import QlibManager
from app.api.routes import router as api_router
from app.messaging.consumer import QlibConsumer
from app.models.database import engine, Base

# Global instances
qlib_manager = QlibManager()
consumer = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    logger.info("Starting Qlib Advisor & Predictor Service...")
    logger.info(f"Service: {settings.service_name}")
    logger.info(f"Host: {settings.service_host}:{settings.service_port}")
    logger.info(f"Database: {settings.database_url}")

    # Create database tables
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)

    # Initialize Qlib
    logger.info("Initializing Qlib...")
    success = await qlib_manager.initialize()
    if success:
        logger.info("✓ Qlib initialized successfully")
    else:
        logger.warning("⚠ Qlib initialization failed - using fallback mode")

    # Start RabbitMQ consumer
    global consumer
    consumer = QlibConsumer(qlib_manager)
    logger.info("Starting RabbitMQ consumer...")
    asyncio.create_task(consumer.start())
    logger.info("✓ RabbitMQ consumer started")

    logger.info("=" * 60)
    logger.info("Qlib Service is ready!")
    logger.info(f"API Documentation: http://{settings.service_host}:{settings.service_port}/docs")
    logger.info("=" * 60)

    yield

    # Shutdown
    logger.info("Shutting down Qlib Service...")

    # Stop consumer
    if consumer:
        logger.info("Stopping RabbitMQ consumer...")
        await consumer.stop()
        logger.info("✓ RabbitMQ consumer stopped")

    logger.info("Qlib Service shutdown complete")


# Initialize FastAPI app
app = FastAPI(
    title="Qlib Advisor & Predictor Service",
    description="""
    AI-powered financial forecasting and investment advisory service using Microsoft Qlib.

    ## Features
    - **Stock Price Forecasting**: Multi-horizon predictions with confidence intervals
    - **Portfolio Analysis**: Risk metrics, performance forecasts, diversification scoring
    - **Investment Recommendations**: Buy/Sell/Hold signals with confidence ratings
    - **Market Regime Detection**: Trend and volatility analysis

    ## Message Queue Integration
    This service consumes messages from AI extraction service and publishes predictions
    to the report generation module via RabbitMQ.

    ## Usage
    - For direct API access, use the endpoints below
    - For message queue integration, publish to queue: `{queue_name}`

    ## Health Check
    Use `/health` endpoint to verify service status
    """.format(queue_name=settings.queue_ai_extraction_complete),
    version="1.0.0",
    contact={
        "name": "KhengLeong Development Team",
        "email": "dev@khengleong.sg",
    },
    lifespan=lifespan,
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_router)

# Root endpoint
@app.get("/", tags=["Health Check"])
async def root():
    """
    Root endpoint - service status.

    Returns:
        dict: Basic service information
    """
    return {
        "service": settings.service_name,
        "status": "running",
        "version": "1.0.0",
        "qlib_initialized": qlib_manager.initialized,
        "documentation": f"http://{settings.service_host}:{settings.service_port}/docs"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.service_host,
        port=settings.service_port,
        reload=settings.reload,
        log_level=settings.log_level.lower()
    )
