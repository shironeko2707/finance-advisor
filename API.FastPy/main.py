from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
from contextlib import asynccontextmanager

from config.database import engine, Base
from module.user_mgmt.user_controller import router as user_router
from module.user_auth.auth_controller import router as auth_router
from module.file_upload import router as file_upload_router
from module.report.generatedreport_controller import router as generated_report_router
from module.template.template_controller import router as template_router
from module.prediction.prediction_controller import router as prediction_router
from module.prediction import start_prediction_consumer_background, get_prediction_consumer

# for running directly with `python main.py`, using python-dotenv to load .env.local to GLOBAL VARIABLE
# from dotenv import load_dotenv
# load_dotenv('.env.local')

# Import prediction models to register them with SQLAlchemy
from module.prediction.PredictionModel import (
    PredictionRequest,
    StockPrediction,
    PortfolioAnalysis,
    Recommendation,
    MarketRegime
)

# Create all tables - CODE FIRST APPROACH
Base.metadata.create_all(bind=engine)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("=" * 60)
    logger.info("Starting up KhengLeong Smart Report Generator API...")
    logger.info("=" * 60)

    # Start Qlib prediction consumer
    try:
        start_prediction_consumer_background()
        logger.info("✓ Qlib prediction consumer started successfully")
    except Exception as e:
        logger.error(f"✗ Failed to start prediction consumer: {e}")
        logger.warning("⚠ Application will continue without prediction consumer")

    logger.info("=" * 60)
    logger.info("Application started successfully")
    logger.info("=" * 60)

    yield

    # Shutdown
    logger.info("=" * 60)
    logger.info("Shutting down KhengLeong Smart Report Generator API...")
    logger.info("=" * 60)

    # Stop prediction consumer
    try:
        consumer = get_prediction_consumer()
        consumer.stop_consuming()
        logger.info("✓ Prediction consumer stopped")
    except Exception as e:
        logger.error(f"Error stopping prediction consumer: {e}")

    logger.info("=" * 60)
    logger.info("Application shutdown complete")
    logger.info("=" * 60)

# Initialize FastAPI app
APP_MODE = os.getenv('APP_MODE', 'production')
SWAGGER_ENABLED = APP_MODE == 'development'
SWAGGER_URL = os.getenv('SWAGGER_URL', '/docs')

doc_url = None if not SWAGGER_ENABLED else SWAGGER_URL + "/api"
redoc_url = None if not SWAGGER_ENABLED else SWAGGER_URL

app = FastAPI(
    title="KhengLeong Smart Report Generator API",
    description="""
    A comprehensive API for managing users, templates, file uploads, and AI-generated content.
    For support, contact the development team dev@khengleong.sg.

    ## Features
    - **User Management**: Complete CRUD operations for users
    - **Authentication**: JWT-based authentication with role-based access
    - **Template Management**: Create and manage report templates
    - **File Upload**: Handle various file formats for processing
    - **AI Integration**: Generate reports and content using AI
    - **Qlib Predictions**: Stock forecasting, portfolio analysis, and investment recommendations
    - **Storage Management**: Organized file storage with persistence

    ## Authentication

    ### Getting Started:
    1. Use the `/auth/login` endpoint to authenticate with username and password
    2. Include the returned JWT token in the Authorization header: `Bearer <token>`
    3. Tokens expire after 8 hours

    ### Token Format
    ```
    Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    ```

    ## Admin Access Required
    - All `/users/*` endpoints require admin role
    - All `/templates/base*` endpoints require admin role
    """,
    version="1.0.0",
    contact={
        "name": "KhengLeong Development Team",
        "email": "dev@khengleong.sg",
    },
    license_info={
        "name": "MIT",
    },
    docs_url=doc_url,
    redoc_url=redoc_url,
    openapi_url="/openapi.json" if SWAGGER_ENABLED else None,
    lifespan=lifespan,
)

# CORS Configuration, default values = false
ALLOW_CORS_LOCAL = os.getenv("ALLOW_CORS_LOCAL", "false").lower() == "true"

def _parse_env_list(var_name: str, default: str = "*") -> list[str]:
    """Parse a comma-separated env var into a list; treat '*' as a wildcard list.

    Returns ['*'] when the env var is exactly '*', otherwise returns a stripped list.
    """
    val = os.getenv(var_name, default)
    if isinstance(val, str) and val.strip() == "*":
        return ["*"]
    return [v.strip() for v in val.split(",") if v.strip()]

CORS_ORIGINS = _parse_env_list("CORS_ORIGINS", "*")
CORS_METHODS = _parse_env_list("CORS_METHODS", "*")
CORS_HEADERS = _parse_env_list("CORS_HEADERS", "*")

if ALLOW_CORS_LOCAL:
    # When '*' is used for origins/methods/headers the lists will contain ['*']
    # which tells the middleware to allow all. Keep allow_credentials=False
    # to avoid wildcard+credentials conflicts.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_methods=CORS_METHODS,
        allow_headers=CORS_HEADERS,
    )

# Include routers
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(file_upload_router)
app.include_router(generated_report_router)
app.include_router(template_router)
app.include_router(prediction_router)

# Root endpoint
@app.get("/", tags=["Health Check"])
async def root():
    """
    Root endpoint that returns a simple status message.

    Returns:
        dict: Simple status message
    """
    return {"message": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
