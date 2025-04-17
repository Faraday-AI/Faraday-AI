from functools import wraps
import time
from fastapi import HTTPException, status
from typing import Callable, Any
import asyncio

class RateLimiter:
    def __init__(self, limit: int, window: int):
        self.limit = limit
        self.window = window
        self.requests = []
    
    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            now = time.time()
            # Remove requests older than window
            self.requests = [req for req in self.requests if now - req < self.window]
            
            if len(self.requests) >= self.limit:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded"
                )
            
            self.requests.append(now)
            return await func(*args, **kwargs)
        return wrapper

def rate_limiter(limit: int, window: int) -> Callable:
    """Rate limiter decorator for FastAPI endpoints.
    
    Args:
        limit: Maximum number of requests allowed
        window: Time window in seconds
        
    Returns:
        Decorator function
    """
    limiter = RateLimiter(limit, window)
    return limiter 