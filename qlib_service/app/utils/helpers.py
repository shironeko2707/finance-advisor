"""
Helper utility functions.
"""
import time
from datetime import datetime, timedelta
from typing import Any, Dict
from functools import wraps
from loguru import logger


def timeit(func):
    """Decorator to measure function execution time."""
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            elapsed = time.time() - start_time
            logger.debug(f"{func.__name__} took {elapsed:.3f}s")
            return result
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"{func.__name__} failed after {elapsed:.3f}s: {e}")
            raise

    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            elapsed = time.time() - start_time
            logger.debug(f"{func.__name__} took {elapsed:.3f}s")
            return result
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"{func.__name__} failed after {elapsed:.3f}s: {e}")
            raise

    # Return appropriate wrapper based on function type
    import inspect
    if inspect.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper


def retry_on_exception(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """
    Decorator to retry function on exception with exponential backoff.

    Args:
        max_retries: Maximum number of retries
        delay: Initial delay in seconds
        backoff: Backoff multiplier
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            current_delay = delay
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries:
                        logger.error(f"{func.__name__} failed after {max_retries} retries: {e}")
                        raise
                    logger.warning(f"{func.__name__} attempt {attempt + 1} failed: {e}. Retrying in {current_delay}s...")
                    import asyncio
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            current_delay = delay
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries:
                        logger.error(f"{func.__name__} failed after {max_retries} retries: {e}")
                        raise
                    logger.warning(f"{func.__name__} attempt {attempt + 1} failed: {e}. Retrying in {current_delay}s...")
                    time.sleep(current_delay)
                    current_delay *= backoff

        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def generate_request_id() -> str:
    """Generate a unique request ID."""
    import uuid
    return f"req_{uuid.uuid4().hex[:16]}"


def calculate_uptime(start_time: datetime) -> Dict[str, Any]:
    """
    Calculate service uptime.

    Args:
        start_time: Service start time

    Returns:
        Dictionary with uptime information
    """
    now = datetime.utcnow()
    uptime = now - start_time

    return {
        "start_time": start_time.isoformat(),
        "current_time": now.isoformat(),
        "uptime_seconds": int(uptime.total_seconds()),
        "uptime_formatted": str(uptime)
    }


def format_number(value: float, decimal_places: int = 2) -> str:
    """Format number with specified decimal places."""
    return f"{value:.{decimal_places}f}"


def format_percentage(value: float, decimal_places: int = 2) -> str:
    """Format value as percentage."""
    return f"{value * 100:.{decimal_places}f}%"


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers, returning default if denominator is zero."""
    try:
        if denominator == 0:
            return default
        return numerator / denominator
    except (TypeError, ValueError):
        return default


def clamp(value: float, min_value: float, max_value: float) -> float:
    """Clamp value between min and max."""
    return max(min_value, min(value, max_value))
