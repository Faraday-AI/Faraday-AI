from typing import Dict, Any, Optional
import logging
import time
from datetime import datetime
import redis.asyncio as redis
from prometheus_client import Counter, Histogram, Gauge

# Prometheus metrics
CACHE_HITS = Counter('cache_hits_total', 'Total number of cache hits', ['service', 'method'])
CACHE_MISSES = Counter('cache_misses_total', 'Total number of cache misses', ['service', 'method'])
CACHE_LATENCY = Histogram('cache_latency_seconds', 'Cache operation latency in seconds', ['service', 'operation'])
CACHE_SIZE = Gauge('cache_size_bytes', 'Current size of cache in bytes', ['service'])
CACHE_ERRORS = Counter('cache_errors_total', 'Total number of cache errors', ['service', 'error_type'])

class CacheMonitor:
    """Service for monitoring Redis cache performance and reliability."""
    
    def __init__(self, redis_client: redis.Redis, service_name: str):
        self.redis = redis_client
        self.service_name = service_name
        self.logger = logging.getLogger(f"cache_monitor.{service_name}")

    async def track_cache_operation(
        self,
        operation: str,
        method: str,
        start_time: Optional[float] = None
    ) -> None:
        """Track a cache operation with timing and success/failure metrics."""
        try:
            if start_time is not None:
                latency = time.time() - start_time
                CACHE_LATENCY.labels(
                    service=self.service_name,
                    operation=operation
                ).observe(latency)

            # Track cache size
            cache_size = await self.redis.dbsize()
            CACHE_SIZE.labels(service=self.service_name).set(cache_size)

        except Exception as e:
            self.logger.error(f"Error tracking cache operation: {str(e)}")
            CACHE_ERRORS.labels(
                service=self.service_name,
                error_type="monitoring_error"
            ).inc()

    async def track_cache_hit(self, method: str) -> None:
        """Track a successful cache hit."""
        CACHE_HITS.labels(
            service=self.service_name,
            method=method
        ).inc()
        await self.track_cache_operation("hit", method)

    async def track_cache_miss(self, method: str) -> None:
        """Track a cache miss."""
        CACHE_MISSES.labels(
            service=self.service_name,
            method=method
        ).inc()
        await self.track_cache_operation("miss", method)

    async def track_cache_error(self, error_type: str) -> None:
        """Track a cache error."""
        CACHE_ERRORS.labels(
            service=self.service_name,
            error_type=error_type
        ).inc()
        self.logger.error(f"Cache error occurred: {error_type}")

    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get current cache statistics."""
        try:
            stats = {
                "service": self.service_name,
                "timestamp": datetime.utcnow().isoformat(),
                "cache_size": await self.redis.dbsize(),
                "hits": CACHE_HITS.labels(service=self.service_name, method="*")._value.get(),
                "misses": CACHE_MISSES.labels(service=self.service_name, method="*")._value.get(),
                "errors": CACHE_ERRORS.labels(service=self.service_name, error_type="*")._value.get()
            }
            
            # Get latency percentiles
            latency_histogram = CACHE_LATENCY.labels(service=self.service_name, operation="*")
            stats["latency"] = {
                "p50": latency_histogram._buckets[0.5],
                "p95": latency_histogram._buckets[0.95],
                "p99": latency_histogram._buckets[0.99]
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting cache stats: {str(e)}")
            return {
                "service": self.service_name,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def check_cache_health(self) -> Dict[str, Any]:
        """Check the health of the cache system."""
        try:
            # Test basic cache operations
            test_key = f"health_check:{datetime.utcnow().timestamp()}"
            test_value = "health_check"
            
            # Test set operation
            start_time = time.time()
            await self.redis.set(test_key, test_value, ex=1)
            await self.track_cache_operation("set", "health_check", start_time)
            
            # Test get operation
            start_time = time.time()
            value = await self.redis.get(test_key)
            await self.track_cache_operation("get", "health_check", start_time)
            
            # Test delete operation
            start_time = time.time()
            await self.redis.delete(test_key)
            await self.track_cache_operation("delete", "health_check", start_time)
            
            return {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "service": self.service_name,
                "operations": ["set", "get", "delete"],
                "success": True
            }
            
        except Exception as e:
            self.logger.error(f"Cache health check failed: {str(e)}")
            await self.track_cache_error("health_check_failed")
            return {
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "service": self.service_name,
                "error": str(e),
                "success": False
            } 