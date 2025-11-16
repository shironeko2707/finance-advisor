"""
Logging configuration using Loguru.
"""
import sys
from loguru import logger
from app.config.settings import settings


def setup_logger():
    """Configure loguru logger for the application."""
    # Remove default logger
    logger.remove()

    # Add console logger with formatting
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.log_level,
        colorize=True
    )

    # Add file logger (if not in debug mode)
    if not settings.debug:
        logger.add(
            "logs/qlib_service_{time:YYYY-MM-DD}.log",
            rotation="00:00",  # Rotate daily at midnight
            retention="30 days",  # Keep logs for 30 days
            level="INFO",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            compression="zip"  # Compress old logs
        )

    logger.info(f"Logger initialized with level: {settings.log_level}")
    return logger


# Initialize logger
setup_logger()
