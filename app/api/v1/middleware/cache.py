from fastapi import Request, Response
from typing import Optional, Any
import json
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class CacheManager:
    def __init__(self):
        self.cache = {}
        self.default_ttl = 300  # 5 minutes default TTL

    async def get(self, key: str) -> Optional[Any]:
        """Get a value from the cache."""
        if key in self.cache:
            value, expiry = self.cache[key]
            if datetime.now() < expiry:
                return value
            del self.cache[key]
        return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set a value in the cache with optional TTL."""
        ttl = ttl or self.default_ttl
        expiry = datetime.now() + timedelta(seconds=ttl)
        self.cache[key] = (value, expiry)
        logger.debug(f"Cache set for key: {key} with TTL: {ttl}s")

    async def delete(self, key: str) -> None:
        """Delete a value from the cache."""
        if key in self.cache:
            del self.cache[key]
            logger.debug(f"Cache deleted for key: {key}")

    async def clear(self) -> None:
        """Clear all cached values."""
        self.cache.clear()
        logger.debug("Cache cleared")

# Initialize the cache manager
cache_manager = CacheManager()

async def add_caching(request: Request, call_next):
    """Middleware to handle caching."""
    # Get the cache key from the request
    cache_key = f"{request.method}:{request.url.path}:{request.query_params}"
    
    # Try to get cached response
    cached_response = await cache_manager.get(cache_key)
    if cached_response:
        logger.debug(f"Cache hit for key: {cache_key}")
        return Response(
            content=cached_response["content"],
            status_code=cached_response["status_code"],
            headers=cached_response["headers"]
        )
    
    # If not cached, process the request
    response = await call_next(request)
    
    # Cache the response if it's cacheable
    if response.status_code == 200 and request.method == "GET":
        response_body = b""
        async for chunk in response.body_iterator:
            response_body += chunk
        
        await cache_manager.set(cache_key, {
            "content": response_body,
            "status_code": response.status_code,
            "headers": dict(response.headers)
        })
        
        return Response(
            content=response_body,
            status_code=response.status_code,
            headers=response.headers
        )
    
    return response 