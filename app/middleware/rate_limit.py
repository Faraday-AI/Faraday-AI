from fastapi import Request, HTTPException
from fastapi.middleware.base import BaseHTTPMiddleware
from redis import Redis
import time
from typing import Dict, Optional
from app.core.config import settings

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        redis_client: Redis,
        rate_limit: int = 100,  # requests per minute
        rate_limit_window: int = 60,  # window in seconds
        rate_limit_by: str = "ip",  # or "user" for authenticated users
    ):
        super().__init__(app)
        self.redis_client = redis_client
        self.rate_limit = rate_limit
        self.rate_limit_window = rate_limit_window
        self.rate_limit_by = rate_limit_by

    async def dispatch(self, request: Request, call_next):
        # Get the identifier for rate limiting
        if self.rate_limit_by == "ip":
            identifier = request.client.host
        else:
            # For authenticated users, use their user ID
            identifier = request.user.id if hasattr(request, "user") else request.client.host

        # Create the Redis key
        key = f"rate_limit:{identifier}:{int(time.time() / self.rate_limit_window)}"

        # Get the current count
        current = self.redis_client.get(key)
        if current is None:
            # Set initial count with expiration
            self.redis_client.setex(key, self.rate_limit_window, 1)
        else:
            # Increment count
            count = int(current) + 1
            if count > self.rate_limit:
                raise HTTPException(
                    status_code=429,
                    detail="Too many requests. Please try again later.",
                    headers={"Retry-After": str(self.rate_limit_window)},
                )
            self.redis_client.incr(key)

        # Process the request
        response = await call_next(request)
        return response 