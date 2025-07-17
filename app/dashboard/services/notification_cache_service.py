"""
Notification Cache Service

This module provides caching functionality for notifications with compression,
predictive caching, and performance optimization.
"""

from typing import Dict, Any, Optional, List
import asyncio
from redis.asyncio import Redis
import zlib
import json
import time
from datetime import datetime, timedelta
from collections import defaultdict
import msgpack
from app.core.config import get_settings


class NotificationCacheService:
    """Service for caching notifications with smart optimization."""
    
    def __init__(self):
        self.settings = get_settings()
        self.redis = None
        self.local_cache = {}
        self.access_patterns = defaultdict(lambda: {'count': 0, 'times': []})
        self.compression_threshold = 1024  # bytes
        self.cache_prediction_window = 300  # 5 minutes
        self.max_local_cache_size = 10000
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'compression_savings': 0
        }

    async def initialize(self):
        """Initialize Redis connection pool for caching."""
        if not self.redis:
            self.redis = Redis.from_url(
                self.settings.REDIS_URL,
                encoding='utf-8',
                decode_responses=True,
                max_connections=20
            )

    async def close(self):
        """Close Redis connections."""
        if self.redis:
            await self.redis.close()

    async def get_notification(self, notification_id: str) -> Optional[Dict[str, Any]]:
        """Get notification from cache with smart fallback."""
        # Try local cache first
        if notification_id in self.local_cache:
            self.cache_stats['hits'] += 1
            self._update_access_pattern(notification_id)
            return self.local_cache[notification_id]

        # Try Redis cache
        await self.initialize()
        cached_data = await self.redis.get(f"notification_cache:{notification_id}")
        
        if cached_data:
            self.cache_stats['hits'] += 1
            # Check if data is compressed
            try:
                if isinstance(cached_data, bytes) and cached_data.startswith(b'\x78\x9c'):  # zlib header
                    cached_data = zlib.decompress(cached_data)
                data = msgpack.unpackb(cached_data)
                self._update_local_cache(notification_id, data)
                return data
            except Exception as e:
                print(f"Error decompressing cached data: {str(e)}")
                return None
        
        self.cache_stats['misses'] += 1
        return None

    async def cache_notification(self, notification_id: str, data: Dict[str, Any], ttl: int = 3600):
        """Cache notification with compression if beneficial."""
        await self.initialize()
        
        # Serialize data
        serialized = msgpack.packb(data)
        
        # Compress if beneficial
        if len(serialized) > self.compression_threshold:
            compressed = zlib.compress(serialized)
            if len(compressed) < len(serialized):
                serialized = compressed
                self.cache_stats['compression_savings'] += len(serialized) - len(compressed)
        
        # Store in Redis with TTL
        await self.redis.set(
            f"notification_cache:{notification_id}",
            serialized,
            ex=ttl
        )
        
        # Update local cache
        self._update_local_cache(notification_id, data)
        
        # Predict and cache related notifications
        await self._predictive_caching(notification_id, data)

    def _update_local_cache(self, notification_id: str, data: Dict[str, Any]):
        """Update local cache with LRU eviction."""
        if len(self.local_cache) >= self.max_local_cache_size:
            # Evict least recently used items
            sorted_items = sorted(
                self.access_patterns.items(),
                key=lambda x: x[1]['times'][-1] if x[1]['times'] else 0
            )
            for old_id, _ in sorted_items[:100]:  # Remove oldest 100 items
                self.local_cache.pop(old_id, None)
                self.access_patterns.pop(old_id, None)
        
        self.local_cache[notification_id] = data
        self._update_access_pattern(notification_id)

    def _update_access_pattern(self, notification_id: str):
        """Update access patterns for predictive caching."""
        now = time.time()
        patterns = self.access_patterns[notification_id]
        patterns['count'] += 1
        patterns['times'].append(now)
        
        # Keep only recent access times
        cutoff = now - self.cache_prediction_window
        patterns['times'] = [t for t in patterns['times'] if t > cutoff]

    async def _predictive_caching(self, notification_id: str, data: Dict[str, Any]):
        """Predict and cache related notifications."""
        # Analyze notification content for related items
        related_ids = self._find_related_notifications(data)
        
        # Cache frequently accessed related notifications
        for related_id in related_ids:
            if self._should_cache_predictively(related_id):
                related_data = await self._fetch_notification(related_id)
                if related_data:
                    await self.cache_notification(related_id, related_data)

    def _find_related_notifications(self, data: Dict[str, Any]) -> List[str]:
        """Find potentially related notification IDs."""
        related_ids = []
        
        # Check for relationships in notification data
        if 'related_items' in data:
            related_ids.extend(data['related_items'])
        
        if 'thread_id' in data:
            related_ids.append(f"thread:{data['thread_id']}")
        
        if 'user_id' in data:
            # Recent notifications for same user
            user_notifications = [
                nid for nid, ndata in self.local_cache.items()
                if ndata.get('user_id') == data['user_id']
            ]
            related_ids.extend(user_notifications[:5])  # Last 5 notifications
        
        return list(set(related_ids))  # Remove duplicates

    def _should_cache_predictively(self, notification_id: str) -> bool:
        """Determine if a notification should be cached predictively."""
        patterns = self.access_patterns[notification_id]
        
        if not patterns['times']:
            return False
        
        # Calculate access frequency
        recent_accesses = len(patterns['times'])
        time_window = time.time() - patterns['times'][0]
        frequency = recent_accesses / time_window if time_window > 0 else 0
        
        # Cache if frequently accessed
        return frequency > 0.1  # More than 1 access per 10 seconds

    async def _fetch_notification(self, notification_id: str) -> Optional[Dict[str, Any]]:
        """Fetch notification data from database."""
        # Implement actual database fetch logic here
        return None  # Placeholder

    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics."""
        total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
        hit_rate = self.cache_stats['hits'] / total_requests if total_requests > 0 else 0
        
        return {
            'hit_rate': hit_rate,
            'compression_savings_kb': self.cache_stats['compression_savings'] / 1024,
            'local_cache_size': len(self.local_cache),
            'access_patterns_tracked': len(self.access_patterns),
            'cache_stats': self.cache_stats
        }

    async def optimize_cache(self):
        """Optimize cache based on usage patterns."""
        # Analyze access patterns
        hot_items = []
        cold_items = []
        
        for notification_id, patterns in self.access_patterns.items():
            if self._should_cache_predictively(notification_id):
                hot_items.append(notification_id)
            else:
                cold_items.append(notification_id)
        
        # Remove cold items from local cache
        for notification_id in cold_items:
            self.local_cache.pop(notification_id, None)
        
        # Ensure hot items are cached
        for notification_id in hot_items:
            if notification_id not in self.local_cache:
                data = await self._fetch_notification(notification_id)
                if data:
                    self._update_local_cache(notification_id, data) 