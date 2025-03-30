from typing import Any, Optional
import json
import redis
from functools import wraps
import logging
from prometheus_client import Counter, Histogram

# Initialize Redis client
redis_client = redis.Redis(
    host='redis',
    port=6379,
    db=0,
    decode_responses=True
)

# Prometheus metrics
cache_hits = Counter('cache_hits_total', 'Number of cache hits')
cache_misses = Counter('cache_misses_total', 'Number of cache misses')
cache_operation_duration = Histogram('cache_operation_duration_seconds', 'Time spent in cache operations')

logger = logging.getLogger(__name__)

def get_cache_key(prefix: str, *args, **kwargs) -> str:
    """Generate a cache key from prefix and arguments."""
    key_parts = [prefix]
    key_parts.extend(str(arg) for arg in args)
    key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
    return ":".join(key_parts)

def cached(prefix: str, ttl: int = 3600):
    """
    Decorator for caching function results.
    
    Args:
        prefix: Prefix for cache key
        ttl: Time to live in seconds (default: 1 hour)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = get_cache_key(prefix, *args, **kwargs)
            
            try:
                with cache_operation_duration.time():
                    # Try to get from cache
                    cached_value = redis_client.get(cache_key)
                    
                    if cached_value:
                        cache_hits.inc()
                        return json.loads(cached_value)
                    
                    cache_misses.inc()
                    # If not in cache, execute function
                    result = func(*args, **kwargs)
                    
                    # Store in cache
                    redis_client.setex(
                        cache_key,
                        ttl,
                        json.dumps(result)
                    )
                    
                    return result
                    
            except redis.RedisError as e:
                logger.error(f"Cache error: {str(e)}")
                # If cache fails, execute function without caching
                return func(*args, **kwargs)
                
        return wrapper
    return decorator

class Cache:
    """Cache manager class for handling Redis operations."""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis = redis_client or redis_client
        self.logger = logging.getLogger(__name__)
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        try:
            with cache_operation_duration.time():
                value = self.redis.get(key)
                if value:
                    cache_hits.inc()
                    return json.loads(value)
                cache_misses.inc()
                return None
        except redis.RedisError as e:
            self.logger.error(f"Cache get error: {str(e)}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache with TTL."""
        try:
            with cache_operation_duration.time():
                return self.redis.setex(
                    key,
                    ttl,
                    json.dumps(value)
                )
        except redis.RedisError as e:
            self.logger.error(f"Cache set error: {str(e)}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        try:
            with cache_operation_duration.time():
                return bool(self.redis.delete(key))
        except redis.RedisError as e:
            self.logger.error(f"Cache delete error: {str(e)}")
            return False
    
    def clear(self) -> bool:
        """Clear all cache entries."""
        try:
            with cache_operation_duration.time():
                return self.redis.flushdb()
        except redis.RedisError as e:
            self.logger.error(f"Cache clear error: {str(e)}")
            return False

# Initialize global cache instance
cache = Cache() 