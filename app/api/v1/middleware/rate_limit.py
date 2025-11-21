from fastapi import Request, HTTPException, status
from datetime import timedelta
from functools import wraps
from typing import Callable, Any, Optional
import asyncio
import redis.asyncio as redis
import os
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

# Initialize Redis client - supports both REDIS_URL and REDIS_HOST/REDIS_PORT
redis_client: Optional[redis.Redis] = None
redis_available = False

try:
    # Prefer REDIS_URL if available (for Render/production)
    # Check if REDIS_URL is set and not the default Docker value
    redis_url_env = os.getenv("REDIS_URL")
    if redis_url_env and redis_url_env.strip():
        redis_client = redis.Redis.from_url(
            redis_url_env,
            encoding="utf-8",
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True
        )
        redis_available = True
        # Mask password in log for security
        masked_url = redis_url_env.split('@')[-1] if '@' in redis_url_env else redis_url_env.split('://')[-1]
        logger.info(f"Redis client initialized for rate limiting using REDIS_URL (host: {masked_url})")
    # Fall back to REDIS_HOST/REDIS_PORT (for Docker/local)
    elif settings.REDIS_HOST:
        redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD if settings.REDIS_PASSWORD else None,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True
        )
        redis_available = True
        logger.info(f"Redis client initialized for rate limiting using REDIS_HOST/REDIS_PORT ({settings.REDIS_HOST}:{settings.REDIS_PORT})")
    else:
        logger.warning("Neither REDIS_URL nor REDIS_HOST configured, rate limiting will be disabled")
except Exception as e:
    logger.warning(f"Failed to initialize Redis client for rate limiting: {e}. Rate limiting will be disabled.")
    redis_client = None
    redis_available = False

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
                
            # Skip rate limiting if Redis is not available
            if not redis_available or not redis_client:
                return await func(*args, **kwargs)
                
            try:
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
            except (redis.ConnectionError, redis.TimeoutError, Exception) as e:
                # If Redis fails, allow the request through (graceful degradation)
                logger.warning(f"Rate limiting Redis error: {e}. Allowing request.")
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# Known security scanner IPs - block immediately
BLOCKED_IPS = {
    "104.199.121.87",  # Security scanner from logs
}

# Suspicious path patterns that indicate scanning
SUSPICIOUS_PATHS = [
    "/blog", "/wordpress", "/wp", "/backup", "/old", "/new",
    "/admin", "/phpmyadmin", "/.env", "/config", "/.git"
]

async def add_rate_limiting(request: Request, call_next):
    """Middleware for rate limiting and security."""
    # Skip rate limiting in test mode to prevent event loop issues
    if get_test_mode():
        response = await call_next(request)
        return response
    
    client_ip = request.client.host
    
    # Block known security scanner IPs
    if client_ip in BLOCKED_IPS:
        logger.warning(f"Blocked request from known security scanner IP: {client_ip}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Check for suspicious path patterns
    path = request.url.path.lower()
    if any(suspicious in path for suspicious in SUSPICIOUS_PATHS):
        logger.warning(f"Suspicious path access attempt from {client_ip}: {path}")
        # Log but don't block - might be legitimate in some cases
        # Could add IP to watchlist here
    
    # Skip rate limiting if Redis is not available
    if not redis_available or not redis_client:
        response = await call_next(request)
        return response
    
    try:
        key = f"rate_limit:{client_ip}"
        
        # Get current request count
        current = await redis_client.get(key)
        if current is None:
            await redis_client.setex(key, RATE_LIMIT_WINDOW, 1)
        else:
            current = int(current)
            if current >= RATE_LIMIT_REQUESTS:
                logger.warning(f"Rate limit exceeded for IP: {client_ip}")
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many requests"
                )
            await redis_client.incr(key)
    except (redis.ConnectionError, redis.TimeoutError, Exception) as e:
        # If Redis fails, allow the request through (graceful degradation)
        logger.warning(f"Rate limiting Redis error: {e}. Allowing request.")
    
    response = await call_next(request)
    return response 