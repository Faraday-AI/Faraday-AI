import logging
from typing import Dict, Any, Optional, List
from fastapi import Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.physical_education.services.activity_manager import ActivityManager
import redis.asyncio as redis
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class ActivityCacheManager:
    """Service for managing activity caching."""
    
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
        self.logger = logging.getLogger(__name__)
        self.activity_manager = ActivityManager(db)
        self.redis_client = redis.Redis(
            host='localhost',
            port=6379,
            db=0,
            decode_responses=True
        )
        
        # Cache settings
        self.settings = {
            'default_ttl': 3600,  # 1 hour
            'max_cache_size': 1000,
            'cleanup_interval': 300  # 5 minutes
        }
        
    async def get_cached_activity(self, activity_id: str) -> Optional[Dict[str, Any]]:
        """Get activity from cache."""
        try:
            cache_key = f"activity:{activity_id}"
            cached_data = await self.redis_client.get(cache_key)
            if cached_data:
                return eval(cached_data)  # Convert string back to dict
            return None
        except Exception as e:
            self.logger.error(f"Error getting cached activity: {str(e)}")
            return None
            
    async def cache_activity(self, activity_id: str, activity_data: Dict[str, Any]) -> bool:
        """Cache activity data."""
        try:
            cache_key = f"activity:{activity_id}"
            await self.redis_client.setex(
                cache_key,
                self.settings['default_ttl'],
                str(activity_data)  # Convert dict to string for storage
            )
            return True
        except Exception as e:
            self.logger.error(f"Error caching activity: {str(e)}")
            return False
            
    async def invalidate_activity_cache(self, activity_id: str) -> bool:
        """Invalidate activity cache."""
        try:
            cache_key = f"activity:{activity_id}"
            await self.redis_client.delete(cache_key)
            return True
        except Exception as e:
            self.logger.error(f"Error invalidating activity cache: {str(e)}")
            return False
            
    async def get_cached_student_activities(self, student_id: str) -> Optional[List[Dict[str, Any]]]:
        """Get cached student activities."""
        try:
            cache_key = f"student_activities:{student_id}"
            cached_data = await self.redis_client.get(cache_key)
            if cached_data:
                return eval(cached_data)  # Convert string back to list
            return None
        except Exception as e:
            self.logger.error(f"Error getting cached student activities: {str(e)}")
            return None
            
    async def cache_student_activities(self, student_id: str, activities: List[Dict[str, Any]]) -> bool:
        """Cache student activities."""
        try:
            cache_key = f"student_activities:{student_id}"
            await self.redis_client.setex(
                cache_key,
                self.settings['default_ttl'],
                str(activities)  # Convert list to string for storage
            )
            return True
        except Exception as e:
            self.logger.error(f"Error caching student activities: {str(e)}")
            return False
            
    async def cleanup_cache(self) -> bool:
        """Cleanup expired cache entries."""
        try:
            # Get all cache keys
            keys = await self.redis_client.keys("*")
            
            # Check each key's TTL
            for key in keys:
                ttl = await self.redis_client.ttl(key)
                if ttl <= 0:
                    await self.redis_client.delete(key)
                    
            return True
        except Exception as e:
            self.logger.error(f"Error cleaning up cache: {str(e)}")
            return False
            
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        try:
            keys = await self.redis_client.keys("*")
            return {
                'total_entries': len(keys),
                'memory_usage': await self.redis_client.info('memory'),
                'last_cleanup': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error getting cache stats: {str(e)}")
            return {} 