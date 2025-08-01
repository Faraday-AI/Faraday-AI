"""
Activity Cache Manager Service

This module provides caching functionality for physical education activities.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.core.database import get_db

logger = logging.getLogger(__name__)

class ActivityCacheManager:
    """Service for managing activity caching in the physical education system."""
    
    def __init__(self, db: Session = None):
        self.logger = logging.getLogger("activity_cache_manager")
        self.db = db
        self._cache = {}
        self._cache_ttl = timedelta(hours=1)  # 1 hour TTL
        
    async def get_cached_activity(
        self,
        activity_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get activity from cache."""
        try:
            if activity_id in self._cache:
                cache_entry = self._cache[activity_id]
                if datetime.utcnow() < cache_entry["expires_at"]:
                    return cache_entry["data"]
                else:
                    # Cache expired, remove it
                    del self._cache[activity_id]
            return None
        except Exception as e:
            self.logger.error(f"Error getting cached activity: {str(e)}")
            return None
    
    async def cache_activity(
        self,
        activity_id: str,
        activity_data: Dict[str, Any],
        ttl: Optional[timedelta] = None
    ) -> bool:
        """Cache activity data."""
        try:
            expires_at = datetime.utcnow() + (ttl or self._cache_ttl)
            self._cache[activity_id] = {
                "data": activity_data,
                "expires_at": expires_at,
                "cached_at": datetime.utcnow()
            }
            return True
        except Exception as e:
            self.logger.error(f"Error caching activity: {str(e)}")
            return False
    
    async def invalidate_activity_cache(
        self,
        activity_id: str
    ) -> bool:
        """Invalidate cached activity."""
        try:
            if activity_id in self._cache:
                del self._cache[activity_id]
            return True
        except Exception as e:
            self.logger.error(f"Error invalidating activity cache: {str(e)}")
            return False
    
    async def clear_all_cache(self) -> bool:
        """Clear all cached activities."""
        try:
            self._cache.clear()
            return True
        except Exception as e:
            self.logger.error(f"Error clearing cache: {str(e)}")
            return False
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        try:
            now = datetime.utcnow()
            active_entries = sum(
                1 for entry in self._cache.values()
                if now < entry["expires_at"]
            )
            expired_entries = len(self._cache) - active_entries
            
            return {
                "total_entries": len(self._cache),
                "active_entries": active_entries,
                "expired_entries": expired_entries,
                "cache_size_mb": len(str(self._cache)) / (1024 * 1024),  # Rough estimate
                "ttl_hours": self._cache_ttl.total_seconds() / 3600
            }
        except Exception as e:
            self.logger.error(f"Error getting cache stats: {str(e)}")
            return {}
    
    async def cleanup_expired_cache(self) -> int:
        """Clean up expired cache entries."""
        try:
            now = datetime.utcnow()
            expired_keys = [
                key for key, entry in self._cache.items()
                if now >= entry["expires_at"]
            ]
            
            for key in expired_keys:
                del self._cache[key]
            
            return len(expired_keys)
        except Exception as e:
            self.logger.error(f"Error cleaning up expired cache: {str(e)}")
            return 0 