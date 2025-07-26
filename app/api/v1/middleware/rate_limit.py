from fastapi import Request, HTTPException, status
from datetime import timedelta
from functools import wraps
from typing import Callable, Any
import asyncio
import redis.asyncio as redis
import os
from app.core.config import settings

# Initialize Redis client
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    password=settings.REDIS_PASSWORD,
    decode_responses=True
)

# Rate limiting configuration
RATE_LIMIT_WINDOW = 60  # 1 minute window
RATE_LIMIT_REQUESTS = 100  # Maximum requests per window

def get_test_mode():
    """Check if we're in test mode."""
    return os.getenv("TESTING", "false").lower() == "true" or os.getenv("TEST_MODE", "false").lower() == "true"

def rate_limiter(limit: int, window: int):
    """Rate limiter decorator."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            request = kwargs.get('request')
            if not request:
                return await func(*args, **kwargs)
                
            client_ip = request.client.host
            key = f"rate_limit:{client_ip}"
            
            # Get current request count
            current = await redis_client.get(key)
            if current is None:
                await redis_client.setex(key, window, 1)
            else:
                current = int(current)
                if current >= limit:
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail="Too many requests"
                    )
                await redis_client.incr(key)
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

async def add_rate_limiting(request: Request, call_next):
    """Middleware for rate limiting."""
    # Skip rate limiting in test mode to prevent event loop issues
    if get_test_mode():
        response = await call_next(request)
        return response
    
    client_ip = request.client.host
    key = f"rate_limit:{client_ip}"
    
    # Get current request count
    current = await redis_client.get(key)
    if current is None:
        await redis_client.setex(key, RATE_LIMIT_WINDOW, 1)
    else:
        current = int(current)
        if current >= RATE_LIMIT_REQUESTS:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests"
            )
        await redis_client.incr(key)
    
    response = await call_next(request)
    return response 