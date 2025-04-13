import asyncio
import time
from typing import Any, Callable, Dict, Optional, TypeVar
from functools import wraps
import logging
from datetime import datetime, timedelta
from collections import deque

T = TypeVar('T')

class RateLimiter:
    """Rate limiter implementation using token bucket algorithm."""
    
    def __init__(
        self,
        rate: int,
        burst: int,
        window: int = 1,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize the rate limiter.
        
        Args:
            rate: Number of requests allowed per window
            burst: Maximum number of requests allowed in a burst
            window: Time window in seconds
            logger: Optional logger instance
        """
        self.rate = rate
        self.burst = burst
        self.window = window
        self.logger = logger or logging.getLogger(__name__)
        
        self.tokens = burst
        self.last_update = time.time()
        self._lock = asyncio.Lock()
        self.request_times: Dict[str, deque] = {}
        self._cleanup_task = None

    async def __call__(self, func: Callable[..., Any]) -> Any:
        """Decorator for rate limiting."""
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            client_id = kwargs.get('client_id', 'default')
            
            async with self._lock:
                if not self._cleanup_task:
                    self._cleanup_task = asyncio.create_task(self._cleanup_old_requests())
                
                if client_id not in self.request_times:
                    self.request_times[client_id] = deque(maxlen=self.burst)
                
                current_time = time.time()
                self._update_tokens(current_time)
                
                if self.tokens <= 0:
                    self.logger.warning(f"Rate limit exceeded for client {client_id}")
                    raise RateLimitExceededError("Rate limit exceeded")
                
                self.tokens -= 1
                self.request_times[client_id].append(current_time)
            
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                self.logger.error(f"Error in rate-limited function: {str(e)}")
                raise

        return wrapper

    def _update_tokens(self, current_time: float) -> None:
        """Update the token count based on elapsed time."""
        time_passed = current_time - self.last_update
        new_tokens = time_passed * (self.rate / self.window)
        self.tokens = min(self.burst, self.tokens + new_tokens)
        self.last_update = current_time

    async def _cleanup_old_requests(self) -> None:
        """Clean up old request records."""
        while True:
            try:
                current_time = time.time()
                for client_id, times in list(self.request_times.items()):
                    while times and current_time - times[0] > self.window:
                        times.popleft()
                    if not times:
                        del self.request_times[client_id]
                await asyncio.sleep(self.window)
            except Exception as e:
                self.logger.error(f"Error in cleanup task: {str(e)}")
                await asyncio.sleep(1)

    def get_usage(self, client_id: str = 'default') -> Dict[str, Any]:
        """Get usage statistics for a client."""
        if client_id not in self.request_times:
            return {
                "requests": 0,
                "remaining_tokens": self.tokens,
                "rate_limit": self.rate,
                "burst_limit": self.burst
            }
        
        current_time = time.time()
        recent_requests = [t for t in self.request_times[client_id] 
                         if current_time - t <= self.window]
        
        return {
            "requests": len(recent_requests),
            "remaining_tokens": self.tokens,
            "rate_limit": self.rate,
            "burst_limit": self.burst,
            "window": self.window
        }

    async def cleanup(self) -> None:
        """Clean up resources."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

class RateLimitExceededError(Exception):
    """Exception raised when rate limit is exceeded."""
    pass

def rate_limit(
    rate: int,
    burst: int,
    window: int = 1,
    logger: Optional[logging.Logger] = None
) -> Callable[[Callable[..., Any]], Any]:
    """
    Decorator factory for rate limiting.
    
    Args:
        rate: Number of requests allowed per window
        burst: Maximum number of requests allowed in a burst
        window: Time window in seconds
        logger: Optional logger instance
    
    Returns:
        Decorator function
    """
    limiter = RateLimiter(rate, burst, window, logger)
    
    def decorator(func: Callable[..., Any]) -> Any:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            return await limiter(func)(*args, **kwargs)
        return wrapper
    
    return decorator 