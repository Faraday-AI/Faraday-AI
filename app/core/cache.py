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
        
    def initialize(self):
        """Initialize Redis clients for all regions."""
        try:
            for region in Region:
                # Get region-specific Redis URL
                redis_url = self._get_region_redis_url(region)
                
                # Create Redis client
                self.clients[region.value] = redis.Redis.from_url(
                    redis_url,
                    decode_responses=True,
                    socket_timeout=5,
                    socket_connect_timeout=5,
                    retry_on_timeout=True
                )
                
                # Test connection
                self.clients[region.value].ping()
                logger.info(f"Redis client initialized for region {region.value}")
                
        except Exception as e:
            logger.error(f"Failed to initialize Redis cluster: {e}")
            raise
            
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
        
    def get_client(self, region: Optional[Region] = None) -> redis.Redis:
        """Get Redis client for a specific region."""
        if region is None:
            region = self._current_region
        return self.clients[region.value]
        
    async def replicate(self, key: str, value: Any, ttl: Optional[int] = None):
        """Replicate data to all regions."""
        if not self.replication_enabled:
            return
            
        tasks = []
        for region in Region:
            if region != self.primary_region:
                client = self.clients[region.value]
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
        """Set value in cache with TTL and optional replication."""
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
            return False
    
    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        try:
            with cache_operation_duration.time():
                success = bool(self.redis.delete(key))
                
                if success and self.replicate:
                    asyncio.run(redis_cluster.replicate(key, None))
                    
                return success
        except redis.RedisError as e:
            self.logger.error(f"Cache delete error: {str(e)}")
            return False
    
    def clear(self) -> bool:
        """Clear all cache entries."""
        try:
            with cache_operation_duration.time():
                success = self.redis.flushdb()
                
                if success and self.replicate:
                    # Clear all regions
                    for region in Region:
                        if region != redis_cluster.primary_region:
                            client = redis_cluster.get_client(region)
                            client.flushdb()
                    
                return success
        except redis.RedisError as e:
            self.logger.error(f"Cache clear error: {str(e)}")
            return False

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