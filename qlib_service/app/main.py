"""
Main FastAPI application for Qlib Advisor & Predictor Service.

This service provides:
1. REST API endpoints for stock forecasting, portfolio analysis, and recommendations
2. RabbitMQ consumer for processing AI extraction results
3. RabbitMQ publisher for sending prediction results
4. Qlib initialization and model management
"""
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.config.settings import settings
from app.api.endpoints import router
from app.services.qlib_manager import QlibManager
from app.messaging.consumer import consumer
from app.messaging.publisher import publisher


# Service startup time tracking
import time
service_start_time = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # ========== STARTUP ==========
    logger.info("=" * 60)
    logger.info(f"Starting {settings.service_name}")
    logger.info("=" * 60)

    # 1. Initialize Qlib
    logger.info("Step 1/4: Initializing Qlib...")
    qlib_manager = QlibManager()
    qlib_initialized = await qlib_manager.initialize()

    if qlib_initialized:
        logger.info("✓ Qlib initialized successfully")
    else:
        logger.warning("⚠ Qlib initialization failed - service will run with limited functionality")

    # Store in app state
    app.state.qlib_manager = qlib_manager
    app.state.start_time = service_start_time

    # 2. Connect to RabbitMQ Publisher
    logger.info("Step 2/4: Connecting to RabbitMQ Publisher...")
    publisher_connected = await publisher.connect()

    if publisher_connected:
        logger.info("✓ RabbitMQ Publisher connected successfully")
    else:
        logger.error("✗ Failed to connect RabbitMQ Publisher")

    # 3. Connect to RabbitMQ Consumer
    logger.info("Step 3/4: Connecting to RabbitMQ Consumer...")
    consumer_connected = await consumer.connect()

    if consumer_connected:
        logger.info("✓ RabbitMQ Consumer connected successfully")
    else:
        logger.error("✗ Failed to connect RabbitMQ Consumer")

    # 4. Start consuming messages
    if consumer_connected:
        logger.info("Step 4/4: Starting message consumption...")
        # Start consumer in background
        asyncio.create_task(consumer.start_consuming())
        logger.info("✓ Message consumer started")
    else:
        logger.warning("⚠ Consumer not started - RabbitMQ connection failed")

    # Startup complete
    logger.info("=" * 60)
    logger.info(f"{settings.service_name} started successfully")
    logger.info(f"Service URL: http://{settings.service_host}:{settings.service_port}")
    logger.info(f"Health Check: http://{settings.service_host}:{settings.service_port}/health")
    logger.info(f"API Docs: http://{settings.service_host}:{settings.service_port}/docs")
    logger.info("=" * 60)

    # Service is now running
    yield

    # ========== SHUTDOWN ==========
    logger.info("=" * 60)
    logger.info(f"Shutting down {settings.service_name}")
    logger.info("=" * 60)

    # Stop consumer
    logger.info("Stopping RabbitMQ consumer...")
    await consumer.disconnect()
    logger.info("✓ Consumer stopped")

    # Disconnect publisher
    logger.info("Disconnecting RabbitMQ publisher...")
    await publisher.disconnect()
    logger.info("✓ Publisher disconnected")

    # Cleanup Qlib (if needed)
    logger.info("Cleaning up Qlib resources...")
    # Add any Qlib cleanup if needed
    logger.info("✓ Cleanup complete")

    logger.info("=" * 60)
    logger.info(f"{settings.service_name} shutdown complete")
    logger.info("=" * 60)


# Create FastAPI application
app = FastAPI(
    title="Qlib Advisor & Predictor Service",
    description="Quantitative investment analysis service using Microsoft Qlib",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(router, tags=["qlib"])


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return {
        "error": "Internal server error",
        "detail": str(exc) if settings.debug else "An unexpected error occurred"
    }


# Application entry point
if __name__ == "__main__":
    import uvicorn

    logger.info(f"Starting Uvicorn server on {settings.service_host}:{settings.service_port}")

    uvicorn.run(
        "app.main:app",
        host=settings.service_host,
        port=settings.service_port,
        reload=settings.reload,
        log_level=settings.log_level.lower(),
    )
