from typing import Any, Optional, Dict
import json
import redis
from functools import wraps
import logging
import asyncio
from prometheus_client import Counter, Histogram
from app.core.config import get_settings
from app.core.regional_failover import Region, RegionalFailoverManager

# Initialize settings and failover manager
settings = get_settings()
failover_manager = RegionalFailoverManager()

# Prometheus metrics
try:
    cache_hits = Counter('cache_hits_total', 'Number of cache hits')
    cache_misses = Counter('cache_misses_total', 'Number of cache misses')
    cache_operation_duration = Histogram('cache_operation_duration_seconds', 'Time spent in cache operations')
    replication_latency = Histogram('cache_replication_latency_seconds', 'Time spent in cache replication')
except ValueError:
    # Metrics already registered, import them from registry
    from prometheus_client import REGISTRY
    # Get existing metrics from registry
    for collector in list(REGISTRY._collector_to_names.keys()):
        if hasattr(collector, '_name'):
            if collector._name == 'cache_hits_total':
                cache_hits = collector
            elif collector._name == 'cache_misses_total':
                cache_misses = collector
            elif collector._name == 'cache_operation_duration_seconds':
                cache_operation_duration = collector
            elif collector._name == 'cache_replication_latency_seconds':
                replication_latency = collector

logger = logging.getLogger(__name__)

class RedisCluster:
    """Manages Redis connections for multiple regions."""
    
    def __init__(self):
        self.clients: Dict[str, redis.Redis] = {}
        self.primary_region = Region.NORTH_AMERICA
        self.replication_enabled = True
        self.replication_timeout = 1.0  # seconds
        self._current_region = self.primary_region  # Default to primary region
        self.is_available = False  # Track if Redis is available
        
    def initialize(self):
        """Initialize Redis clients for all regions. Gracefully handles Redis unavailability."""
        # Always try to initialize - if it fails, we'll gracefully degrade
        
        try:
            initialized_regions = 0
            for region in Region:
                try:
                    # Get region-specific Redis URL
                    redis_url = self._get_region_redis_url(region)
                    
                    # Create Redis client
                    client = redis.Redis.from_url(
                        redis_url,
                        decode_responses=True,
                        socket_timeout=5,
                        socket_connect_timeout=5,
                        retry_on_timeout=True
                    )
                    
                    # Test connection with short timeout
                    client.ping()
                    self.clients[region.value] = client
                    logger.info(f"Redis client initialized for region {region.value}")
                    initialized_regions += 1
                except Exception as e:
                    logger.warning(f"Failed to initialize Redis for region {region.value}: {e}")
                    # Continue with other regions
                    continue
            
            if initialized_regions > 0:
                self.is_available = True
                logger.info(f"Redis cluster initialized with {initialized_regions} region(s)")
            else:
                self.is_available = False
                logger.warning("No Redis regions could be initialized. Cache will operate in degraded mode.")
                
        except Exception as e:
            logger.warning(f"Failed to initialize Redis cluster: {e}. Cache will operate in degraded mode.")
            self.is_available = False
            # Don't raise - allow app to start without Redis
            
    def _get_region_redis_url(self, region: Region) -> str:
        """Get Redis URL for a specific region."""
        base_url = settings.REDIS_URL
        # For local development or Docker environment, use the base URL as is
        if "localhost" in base_url or "redis:" in base_url:
            return base_url
        # For production/staging environments
        if "redis://" in base_url:
            # Replace host with region-specific host while preserving the scheme
            return base_url.replace("redis://", f"redis://redis-{region.value}-")
        return base_url
        
    def get_client(self, region: Optional[Region] = None) -> Optional[redis.Redis]:
        """Get Redis client for a specific region. Returns None if Redis is not available."""
        if not self.is_available:
            return None
        if region is None:
            region = self._current_region
        return self.clients.get(region.value)
        
    async def replicate(self, key: str, value: Any, ttl: Optional[int] = None):
        """Replicate data to all regions."""
        if not self.replication_enabled or not self.is_available:
            return
            
        tasks = []
        for region in Region:
            if region != self.primary_region:
                client = self.clients.get(region.value)
                if client:
                    tasks.append(
                        self._replicate_to_region(client, key, value, ttl)
                    )
                
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
            
    async def _replicate_to_region(
        self,
        client: redis.Redis,
        key: str,
        value: Any,
        ttl: Optional[int]
    ):
        """Replicate data to a specific region."""
        try:
            with replication_latency.time():
                if ttl is not None:
                    await asyncio.to_thread(
                        client.setex,
                        key,
                        ttl,
                        json.dumps(value)
                    )
                else:
                    await asyncio.to_thread(
                        client.set,
                        key,
                        json.dumps(value)
                    )
        except Exception as e:
            logger.error(f"Replication failed: {e}")

# Initialize Redis cluster
redis_cluster = RedisCluster()
redis_cluster.initialize()

# Initialize default Redis client (for backward compatibility)
# This may be None if Redis is not available
redis_client = redis_cluster.get_client(redis_cluster.primary_region)

def get_cache_key(prefix: str, *args, **kwargs) -> str:
    """Generate a cache key from prefix and arguments."""
    key_parts = [prefix]
    key_parts.extend(str(arg) for arg in args)
    key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
    return ":".join(key_parts)

class Cache:
    """Cache manager class for handling Redis operations with regional support."""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None, replicate: bool = True):
        self.redis = redis_client or redis_cluster.get_client()
        self.replicate = replicate
        self.logger = logging.getLogger(__name__)
        self._in_memory_cache: Dict[str, Any] = {}  # Fallback in-memory cache
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        # If Redis is not available, use in-memory cache
        if self.redis is None:
            return self._in_memory_cache.get(key)
            
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
            # Fallback to in-memory cache
            return self._in_memory_cache.get(key)
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache with TTL and optional replication."""
        # If Redis is not available, use in-memory cache
        if self.redis is None:
            self._in_memory_cache[key] = value
            return True
            
        try:
            with cache_operation_duration.time():
                success = self.redis.setex(
                    key,
                    ttl,
                    json.dumps(value)
                )
                
                if success and self.replicate:
                    asyncio.run(redis_cluster.replicate(key, value, ttl))
                    
                return success
        except redis.RedisError as e:
            self.logger.error(f"Cache set error: {str(e)}")
            # Fallback to in-memory cache
            self._in_memory_cache[key] = value
            return True
    
    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        # If Redis is not available, use in-memory cache
        if self.redis is None:
            if key in self._in_memory_cache:
                del self._in_memory_cache[key]
                return True
            return False
            
        try:
            with cache_operation_duration.time():
                success = bool(self.redis.delete(key))
                
                if success and self.replicate:
                    asyncio.run(redis_cluster.replicate(key, None))
                
                # Also remove from in-memory cache
                self._in_memory_cache.pop(key, None)
                    
                return success
        except redis.RedisError as e:
            self.logger.error(f"Cache delete error: {str(e)}")
            # Fallback to in-memory cache
            if key in self._in_memory_cache:
                del self._in_memory_cache[key]
                return True
            return False
    
    def clear(self) -> bool:
        """Clear all cache entries."""
        # If Redis is not available, clear in-memory cache
        if self.redis is None:
            self._in_memory_cache.clear()
            return True
            
        try:
            with cache_operation_duration.time():
                success = self.redis.flushdb()
                
                if success and self.replicate:
                    # Clear all regions
                    for region in Region:
                        if region != redis_cluster.primary_region:
                            client = redis_cluster.get_client(region)
                            if client:
                                client.flushdb()
                
                # Also clear in-memory cache
                self._in_memory_cache.clear()
                    
                return success
        except redis.RedisError as e:
            self.logger.error(f"Cache clear error: {str(e)}")
            # Fallback to in-memory cache
            self._in_memory_cache.clear()
            return True

# Singleton instance of Cache
_cache_instance = None

def get_cache() -> Cache:
    """
    Get or create a singleton instance of the Cache class.
    
    Returns:
        Cache: A singleton instance of the Cache class
    """
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = Cache(redis_client=redis_client)
    return _cache_instance

def cached(prefix: str, ttl: int = 3600, replicate: bool = True):
    """
    Decorator for caching function results with optional replication.
    
    Args:
        prefix: Prefix for cache key
        ttl: Time to live in seconds (default: 1 hour)
        replicate: Whether to replicate to other regions (default: True)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = get_cache_key(prefix, *args, **kwargs)
            
            # If Redis is not available, just execute the function
            if redis_client is None:
                return func(*args, **kwargs)
            
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
                    
                    # Replicate if enabled
                    if replicate:
                        asyncio.run(redis_cluster.replicate(cache_key, result, ttl))
                    
                    return result
                    
            except redis.RedisError as e:
                logger.error(f"Cache error: {str(e)}")
                # If cache fails, execute function without caching
                return func(*args, **kwargs)
                
        return wrapper
    return decorator

# Initialize cache manager instance
cache_manager = Cache() 