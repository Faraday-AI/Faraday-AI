"""
Load Balancer Cache Manager

This module provides specialized caching for load balancer data, including:
- Configuration caching
- Metrics caching
- Health check results caching
- Circuit breaker state caching
"""

from typing import Dict, Any, Optional, List
import json
from datetime import datetime, timedelta
import logging
from prometheus_client import Counter, Histogram

from app.core.cache import Cache, redis_cluster, get_cache_key
from app.core.regional_failover import Region
from app.models.load_balancer import (
    LoadBalancerConfig,
    RegionConfig,
    MetricsHistory,
    AlertConfig
)

# Prometheus metrics for load balancer cache
LB_CACHE_HITS = Counter('load_balancer_cache_hits_total', 'Load balancer cache hits', ['cache_type'])
LB_CACHE_MISSES = Counter('load_balancer_cache_misses_total', 'Load balancer cache misses', ['cache_type'])
LB_CACHE_LATENCY = Histogram('load_balancer_cache_latency_seconds', 'Load balancer cache operation latency', ['operation'])

logger = logging.getLogger(__name__)

class LoadBalancerCache:
    """Specialized cache manager for load balancer data."""
    
    def __init__(self):
        self.cache = Cache(replicate=True)
        self.config_ttl = 300  # 5 minutes
        self.metrics_ttl = 60   # 1 minute
        self.health_ttl = 30    # 30 seconds
        
    def _get_config_key(self, config_id: int) -> str:
        """Generate cache key for load balancer config."""
        return get_cache_key("lb:config", config_id)
        
    def _get_region_key(self, region: Region) -> str:
        """Generate cache key for region config."""
        return get_cache_key("lb:region", region.value)
        
    def _get_metrics_key(self, region: Region) -> str:
        """Generate cache key for region metrics."""
        return get_cache_key("lb:metrics", region.value)
        
    def _get_health_key(self, region: Region) -> str:
        """Generate cache key for health check results."""
        return get_cache_key("lb:health", region.value)
        
    def get_config(self, config_id: int) -> Optional[Dict[str, Any]]:
        """Get load balancer configuration from cache."""
        key = self._get_config_key(config_id)
        with LB_CACHE_LATENCY.labels(operation="get_config").time():
            data = self.cache.get(key)
            if data:
                LB_CACHE_HITS.labels(cache_type="config").inc()
                return data
            LB_CACHE_MISSES.labels(cache_type="config").inc()
            return None
            
    def set_config(self, config: LoadBalancerConfig) -> None:
        """Cache load balancer configuration."""
        key = self._get_config_key(config.id)
        with LB_CACHE_LATENCY.labels(operation="set_config").time():
            self.cache.set(key, config.dict(), self.config_ttl)
            
    def get_region_config(self, region: Region) -> Optional[Dict[str, Any]]:
        """Get region configuration from cache."""
        key = self._get_region_key(region)
        with LB_CACHE_LATENCY.labels(operation="get_region").time():
            data = self.cache.get(key)
            if data:
                LB_CACHE_HITS.labels(cache_type="region").inc()
                return data
            LB_CACHE_MISSES.labels(cache_type="region").inc()
            return None
            
    def set_region_config(self, config: RegionConfig) -> None:
        """Cache region configuration."""
        key = self._get_region_key(config.region)
        with LB_CACHE_LATENCY.labels(operation="set_region").time():
            self.cache.set(key, config.dict(), self.config_ttl)
            
    def get_recent_metrics(self, region: Region) -> Optional[List[Dict[str, Any]]]:
        """Get recent metrics from cache."""
        key = self._get_metrics_key(region)
        with LB_CACHE_LATENCY.labels(operation="get_metrics").time():
            data = self.cache.get(key)
            if data:
                LB_CACHE_HITS.labels(cache_type="metrics").inc()
                return data
            LB_CACHE_MISSES.labels(cache_type="metrics").inc()
            return None
            
    def add_metrics(self, region: Region, metrics: MetricsHistory) -> None:
        """Add new metrics to cache."""
        key = self._get_metrics_key(region)
        with LB_CACHE_LATENCY.labels(operation="set_metrics").time():
            # Get existing metrics
            current = self.get_recent_metrics(region) or []
            
            # Add new metrics and keep only last hour
            current.append(metrics.dict())
            cutoff = datetime.utcnow() - timedelta(hours=1)
            current = [
                m for m in current
                if datetime.fromisoformat(m['timestamp']) > cutoff
            ]
            
            # Update cache
            self.cache.set(key, current, self.metrics_ttl)
            
    def get_health_status(self, region: Region) -> Optional[Dict[str, Any]]:
        """Get health check results from cache."""
        key = self._get_health_key(region)
        with LB_CACHE_LATENCY.labels(operation="get_health").time():
            data = self.cache.get(key)
            if data:
                LB_CACHE_HITS.labels(cache_type="health").inc()
                return data
            LB_CACHE_MISSES.labels(cache_type="health").inc()
            return None
            
    def set_health_status(self, region: Region, status: Dict[str, Any]) -> None:
        """Cache health check results."""
        key = self._get_health_key(region)
        with LB_CACHE_LATENCY.labels(operation="set_health").time():
            self.cache.set(key, status, self.health_ttl)
            
    def invalidate_config(self, config_id: int) -> None:
        """Invalidate load balancer configuration cache."""
        key = self._get_config_key(config_id)
        self.cache.delete(key)
        
    def invalidate_region(self, region: Region) -> None:
        """Invalidate region configuration cache."""
        key = self._get_region_key(region)
        self.cache.delete(key)
        
    def invalidate_metrics(self, region: Region) -> None:
        """Invalidate metrics cache."""
        key = self._get_metrics_key(region)
        self.cache.delete(key)
        
    def invalidate_health(self, region: Region) -> None:
        """Invalidate health check cache."""
        key = self._get_health_key(region)
        self.cache.delete(key)
        
    def clear_all(self) -> None:
        """Clear all load balancer related caches."""
        pattern = "lb:*"
        for client in redis_cluster.clients.values():
            for key in client.scan_iter(pattern):
                client.delete(key)

# Initialize global cache instance
load_balancer_cache = LoadBalancerCache() 