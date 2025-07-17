"""
Resource Sharing Cache Service

This module provides caching functionality for resource sharing operations
in the Faraday AI Dashboard, improving performance and reducing database load.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
from redis import Redis
from fastapi import HTTPException

class ResourceSharingCacheService:
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        """Initialize the cache service with Redis connection."""
        try:
            self.redis = Redis.from_url(
                url=redis_url,
                decode_responses=True,
                socket_timeout=5
            )
            self.default_ttl = 3600  # 1 hour in seconds
            self._initialize_cache_settings()
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to initialize cache service: {str(e)}"
            )

    def _initialize_cache_settings(self):
        """Initialize cache settings with performance optimizations."""
        self.cache_settings = {
            "shared_resources": {
                "ttl": 3600,  # 1 hour
                "max_size": 10000,  # Maximum number of cached resources
                "compression": True
            },
            "metrics": {
                "ttl": 300,  # 5 minutes
                "max_size": 1000,
                "compression": True
            },
            "user_preferences": {
                "ttl": 7200,  # 2 hours
                "max_size": 5000,
                "compression": False
            }
        }

    async def get_shared_resources(
        self,
        org_id: str,
        status: Optional[str] = None
    ) -> Optional[List[Dict[str, Any]]]:
        """Get cached shared resources for an organization."""
        cache_key = f"shared_resources:{org_id}"
        if status:
            cache_key += f":{status}"

        try:
            cached_data = self.redis.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
            return None
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Cache retrieval error: {str(e)}"
            )

    async def set_shared_resources(
        self,
        org_id: str,
        resources: List[Dict[str, Any]],
        status: Optional[str] = None,
        ttl: Optional[int] = None
    ):
        """Cache shared resources for an organization."""
        cache_key = f"shared_resources:{org_id}"
        if status:
            cache_key += f":{status}"

        try:
            ttl = ttl or self.cache_settings["shared_resources"]["ttl"]
            self.redis.setex(
                cache_key,
                ttl,
                json.dumps(resources)
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Cache storage error: {str(e)}"
            )

    async def get_sharing_metrics(
        self,
        org_id: str,
        time_range: str = "24h"
    ) -> Optional[Dict[str, Any]]:
        """Get cached sharing metrics for an organization."""
        cache_key = f"sharing_metrics:{org_id}:{time_range}"

        try:
            cached_data = self.redis.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
            return None
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Cache retrieval error: {str(e)}"
            )

    async def set_sharing_metrics(
        self,
        org_id: str,
        metrics: Dict[str, Any],
        time_range: str = "24h",
        ttl: Optional[int] = None
    ):
        """Cache sharing metrics for an organization."""
        cache_key = f"sharing_metrics:{org_id}:{time_range}"

        try:
            ttl = ttl or self.cache_settings["metrics"]["ttl"]
            self.redis.setex(
                cache_key,
                ttl,
                json.dumps(metrics)
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Cache storage error: {str(e)}"
            )

    async def invalidate_org_cache(self, org_id: str):
        """Invalidate all cached data for an organization."""
        try:
            pattern = f"*:{org_id}:*"
            keys = self.redis.keys(pattern)
            if keys:
                self.redis.delete(*keys)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Cache invalidation error: {str(e)}"
            )

    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics and performance metrics."""
        try:
            info = self.redis.info()
            return {
                "hits": info.get("keyspace_hits", 0),
                "misses": info.get("keyspace_misses", 0),
                "memory_used": info.get("used_memory_human", "0B"),
                "total_keys": sum(
                    len(self.redis.keys(f"*:{key_type}:*"))
                    for key_type in self.cache_settings.keys()
                ),
                "uptime": info.get("uptime_in_seconds", 0)
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error getting cache stats: {str(e)}"
            ) 