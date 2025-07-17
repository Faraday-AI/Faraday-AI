"""Rate limiting functionality for API endpoints."""
from typing import Optional, Dict, Any, Callable
from datetime import datetime, timedelta
import asyncio
from fastapi import HTTPException, status
from functools import wraps
import logging

logger = logging.getLogger(__name__)

# In-memory store for rate limiting
rate_limit_store: Dict[str, Dict[str, Any]] = {}

def rate_limit(requests: int, period: int):
    """
    Rate limiting decorator for FastAPI endpoints.
    
    Args:
        requests: Maximum number of requests allowed in the period
        period: Time period in seconds
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get client identifier (could be IP, user ID, etc.)
            client_id = kwargs.get('current_user', {}).get('id', 'anonymous')
            endpoint = func.__name__
            key = f"{client_id}:{endpoint}"
            
            # Get current time
            now = datetime.now()
            
            # Initialize or get rate limit data
            if key not in rate_limit_store:
                rate_limit_store[key] = {
                    'requests': 0,
                    'window_start': now,
                    'last_reset': now
                }
            
            # Check if we need to reset the window
            data = rate_limit_store[key]
            window_duration = timedelta(seconds=period)
            if now - data['window_start'] > window_duration:
                data['requests'] = 0
                data['window_start'] = now
                data['last_reset'] = now
            
            # Check rate limit
            if data['requests'] >= requests:
                wait_time = (data['window_start'] + window_duration - now).total_seconds()
                logger.warning(f"Rate limit exceeded for {key}. Wait time: {wait_time}s")
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "error": "Rate limit exceeded",
                        "wait_time": wait_time,
                        "retry_after": data['window_start'] + window_duration
                    }
                )
            
            # Increment request count
            data['requests'] += 1
            
            # Execute the endpoint function
            return await func(*args, **kwargs)
            
        return wrapper
    return decorator

def cleanup_rate_limits():
    """Clean up expired rate limit data."""
    now = datetime.now()
    expired = []
    
    for key, data in rate_limit_store.items():
        if now - data['last_reset'] > timedelta(hours=1):
            expired.append(key)
    
    for key in expired:
        del rate_limit_store[key]
        logger.debug(f"Cleaned up rate limit data for {key}")

# Run cleanup periodically
async def periodic_cleanup():
    """Run cleanup periodically."""
    while True:
        try:
            cleanup_rate_limits()
            await asyncio.sleep(3600)  # Run every hour
        except Exception as e:
            logger.error(f"Error in rate limit cleanup: {str(e)}")
            await asyncio.sleep(60)  # Retry after a minute on error 