"""
Activity Cache Manager Service

This module provides caching functionality for physical education activities using Redis.
"""

import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import redis.asyncio as redis

from app.core.database import get_db
from app.core.config import get_settings

logger = logging.getLogger(__name__)

class ActivityCacheManager:
    """Service for managing activity caching in the physical education system using Redis."""
    
    def __init__(self, db: Session = None):
        self.logger = logging.getLogger("activity_cache_manager")
        self.db = db
        self.app_settings = get_settings()
        
        # Initialize Redis connection
        try:
            self.redis = redis.Redis.from_url(
                self.app_settings.REDIS_URL,
                decode_responses=True
            )
            self.logger.info("Redis connection established for ActivityCacheManager")
        except Exception as e:
            self.logger.error(f"Failed to connect to Redis: {str(e)}")
            self.redis = None
        
        # Cache settings
        self.cache_settings = {
            'default_ttl': 3600,  # 1 hour in seconds
            'student_activities_ttl': 1800,  # 30 minutes in seconds
            'cleanup_interval': 300  # 5 minutes in seconds
        }
        
    async def get_cached_activity(
        self,
        activity_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get activity from Redis cache."""
        try:
            if not self.redis:
                self.logger.warning("Redis not available, returning None")
                return None
                
            cache_key = f'activity:{activity_id}'
            cached_data = await self.redis.get(cache_key)
            
            if cached_data:
                return json.loads(cached_data)
            return None
        except Exception as e:
            self.logger.error(f"Error getting cached activity: {str(e)}")
            return None
    
    async def cache_activity(
        self,
        activity_id: str,
        activity_data: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> bool:
        """Cache activity data in Redis."""
        try:
            if not self.redis:
                self.logger.warning("Redis not available, cache operation failed")
                return False
                
            cache_key = f'activity:{activity_id}'
            cache_ttl = ttl or self.cache_settings['default_ttl']
            
            await self.redis.setex(
                cache_key,
                cache_ttl,
                json.dumps(activity_data)
            )
            return True
        except Exception as e:
            self.logger.error(f"Error caching activity: {str(e)}")
            return False
    
    async def invalidate_activity_cache(
        self,
        activity_id: str
    ) -> bool:
        """Invalidate cached activity in Redis."""
        try:
            if not self.redis:
                self.logger.warning("Redis not available, invalidation failed")
                return False
                
            cache_key = f'activity:{activity_id}'
            await self.redis.delete(cache_key)
            return True
        except Exception as e:
            self.logger.error(f"Error invalidating activity cache: {str(e)}")
            return False
    
    async def clear_all_cache(self) -> bool:
        """Clear all cached activities from Redis."""
        try:
            if not self.redis:
                self.logger.warning("Redis not available, clear operation failed")
                return False
                
            # Get all activity keys and delete them
            activity_keys = await self.redis.keys('activity:*')
            student_keys = await self.redis.keys('student_activities:*')
            
            if activity_keys or student_keys:
                await self.redis.delete(*(activity_keys + student_keys))
            
            return True
        except Exception as e:
            self.logger.error(f"Error clearing cache: {str(e)}")
            return False
    
    async def get_cached_student_activities(
        self,
        student_id: str
    ) -> Optional[List[Dict[str, Any]]]:
        """Get cached student activities from Redis."""
        try:
            if not self.redis:
                self.logger.warning("Redis not available, returning None")
                return None
                
            cache_key = f'student_activities:{student_id}'
            cached_data = await self.redis.get(cache_key)
            
            if cached_data:
                return json.loads(cached_data)
            return None
        except Exception as e:
            self.logger.error(f"Error getting cached student activities: {str(e)}")
            return None
    
    async def cache_student_activities(
        self,
        student_id: str,
        activities: List[Dict[str, Any]],
        ttl: Optional[int] = None
    ) -> bool:
        """Cache student activities in Redis."""
        try:
            if not self.redis:
                self.logger.warning("Redis not available, cache operation failed")
                return False
                
            cache_key = f'student_activities:{student_id}'
            cache_ttl = ttl or self.cache_settings['student_activities_ttl']
            
            await self.redis.setex(
                cache_key,
                cache_ttl,
                json.dumps(activities)
            )
            return True
        except Exception as e:
            self.logger.error(f"Error caching student activities: {str(e)}")
            return False
    
    async def cleanup_cache(self) -> bool:
        """Clean up expired cache entries in Redis."""
        try:
            if not self.redis:
                self.logger.warning("Redis not available, cleanup failed")
                return False
                
            # Get all keys
            all_keys = await self.redis.keys('*')
            deleted_count = 0
            
            for key in all_keys:
                # Check if key has expired (TTL <= 0)
                ttl = await self.redis.ttl(key)
                if ttl <= 0:
                    await self.redis.delete(key)
                    deleted_count += 1
            
            self.logger.info(f"Cleaned up {deleted_count} expired cache entries")
            return True
        except Exception as e:
            self.logger.error(f"Error cleaning up cache: {str(e)}")
            return False
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics from Redis."""
        try:
            if not self.redis:
                self.logger.warning("Redis not available, returning empty stats")
                return {}
                
            # Get all keys
            all_keys = await self.redis.keys('*')
            activity_keys = await self.redis.keys('activity:*')
            student_keys = await self.redis.keys('student_activities:*')
            
            # Get memory usage
            memory_info = await self.redis.info('memory')
            
            return {
                'total_entries': len(all_keys),
                'activity_entries': len(activity_keys),
                'student_activity_entries': len(student_keys),
                'memory_usage': memory_info,
                'last_cleanup': datetime.utcnow().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error getting cache stats: {str(e)}")
            return {}
    
    async def cleanup_expired_cache(self) -> int:
        """Clean up expired cache entries and return count of deleted entries."""
        try:
            if not self.redis:
                self.logger.warning("Redis not available, cleanup failed")
                return 0
                
            # Get all keys
            all_keys = await self.redis.keys('*')
            deleted_count = 0
            
            for key in all_keys:
                # Check if key has expired (TTL <= 0)
                ttl = await self.redis.ttl(key)
                if ttl <= 0:
                    await self.redis.delete(key)
                    deleted_count += 1
            
            self.logger.info(f"Cleaned up {deleted_count} expired cache entries")
            return deleted_count
        except Exception as e:
            self.logger.error(f"Error cleaning up expired cache: {str(e)}")
            return 0 