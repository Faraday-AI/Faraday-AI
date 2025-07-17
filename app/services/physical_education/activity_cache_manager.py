"""Activity cache manager for physical education."""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import numpy as np
from sqlalchemy.orm import Session
from app.core.database import get_db

# Import models
from app.models.activity import (
    Activity,
    ActivityCategoryAssociation
)
from app.models.student import Student
from app.models.cache import (
    CachePolicy,
    CacheEntry,
    CacheMetrics
)
from app.models.physical_education.pe_enums.pe_types import (
    ActivityType,
    DifficultyLevel,
    EquipmentRequirement,
    CacheType,
    CacheLevel,
    CacheStatus,
    CacheTrigger
)

class ActivityCacheManager:
    """Service for managing physical education activity caching."""
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ActivityCacheManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.logger = logging.getLogger("activity_cache_manager")
        self.db = None
        
        # Cache settings
        self.settings = {
            "cache_enabled": True,
            "auto_cache": True,
            "max_cache_size": 1000,  # entries
            "cache_ttl": 3600,  # seconds
            "thresholds": {
                "low_usage": 0.2,
                "high_usage": 0.8,
                "eviction_threshold": 0.9
            },
            "weights": {
                "frequency": 0.4,
                "recency": 0.3,
                "size": 0.3
            }
        }
        
        # Cache components
        self.cache_entries = {}
        self.cache_metrics = {}
        self.eviction_history = []
        self.access_history = []
    
    async def initialize(self):
        """Initialize the cache manager."""
        try:
            self.db = next(get_db())
            
            # Initialize cache components
            self.initialize_cache_components()
            
            self.logger.info("Activity Cache Manager initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing Activity Cache Manager: {str(e)}")
            raise
    
    async def cleanup(self):
        """Cleanup the cache manager."""
        try:
            # Clear all data
            self.cache_entries.clear()
            self.cache_metrics.clear()
            self.eviction_history.clear()
            self.access_history.clear()
            
            # Reset service references
            self.db = None
            
            self.logger.info("Activity Cache Manager cleaned up successfully")
        except Exception as e:
            self.logger.error(f"Error cleaning up Activity Cache Manager: {str(e)}")
            raise

    def initialize_cache_components(self):
        """Initialize cache components."""
        try:
            # Initialize cache metrics
            self.cache_metrics = {
                "size": {
                    "current": 0,
                    "max": self.settings["max_cache_size"],
                    "unit": "entries"
                },
                "hits": {
                    "count": 0,
                    "rate": 0.0
                },
                "misses": {
                    "count": 0,
                    "rate": 0.0
                },
                "evictions": {
                    "count": 0,
                    "rate": 0.0
                }
            }
            
            self.logger.info("Cache components initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing cache components: {str(e)}")
            raise

    async def get_cached_activity(
        self,
        activity_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get cached activity data."""
        try:
            if not self.settings["cache_enabled"]:
                return None
            
            if activity_id not in self.cache_entries:
                self._update_cache_metrics("misses")
                return None
            
            entry = self.cache_entries[activity_id]
            
            # Check if entry is expired
            if self._is_entry_expired(entry):
                self._evict_entry(activity_id)
                self._update_cache_metrics("misses")
                return None
            
            # Update access history
            self._update_access_history(activity_id)
            
            # Update cache metrics
            self._update_cache_metrics("hits")
            
            return entry["data"]
            
        except Exception as e:
            self.logger.error(f"Error getting cached activity: {str(e)}")
            raise

    async def cache_activity(
        self,
        activity_id: str,
        activity_data: Dict[str, Any]
    ) -> None:
        """Cache activity data."""
        try:
            if not self.settings["cache_enabled"]:
                return
            
            # Check cache size and evict if necessary
            if len(self.cache_entries) >= self.settings["max_cache_size"]:
                self._evict_entries()
            
            # Create cache entry
            entry = {
                "id": activity_id,
                "data": activity_data,
                "created_at": datetime.now().isoformat(),
                "accessed_at": datetime.now().isoformat(),
                "access_count": 0
            }
            
            # Add to cache
            self.cache_entries[activity_id] = entry
            
            # Update cache metrics
            self._update_cache_metrics("size")
            
        except Exception as e:
            self.logger.error(f"Error caching activity: {str(e)}")
            raise

    async def invalidate_cache(
        self,
        activity_id: Optional[str] = None
    ) -> None:
        """Invalidate cache entries."""
        try:
            if activity_id:
                if activity_id in self.cache_entries:
                    self._evict_entry(activity_id)
            else:
                self.cache_entries.clear()
                self._update_cache_metrics("size")
            
        except Exception as e:
            self.logger.error(f"Error invalidating cache: {str(e)}")
            raise

    async def get_cache_metrics(self) -> Dict[str, Any]:
        """Get cache metrics."""
        try:
            total_requests = (
                self.cache_metrics["hits"]["count"] +
                self.cache_metrics["misses"]["count"]
            )
            
            if total_requests > 0:
                self.cache_metrics["hits"]["rate"] = (
                    self.cache_metrics["hits"]["count"] /
                    total_requests
                )
                self.cache_metrics["misses"]["rate"] = (
                    self.cache_metrics["misses"]["count"] /
                    total_requests
                )
            
            return self.cache_metrics
            
        except Exception as e:
            self.logger.error(f"Error getting cache metrics: {str(e)}")
            raise

    def _is_entry_expired(
        self,
        entry: Dict[str, Any]
    ) -> bool:
        """Check if cache entry is expired."""
        try:
            created_at = datetime.fromisoformat(entry["created_at"])
            now = datetime.now()
            age = (now - created_at).total_seconds()
            
            return age > self.settings["cache_ttl"]
            
        except Exception as e:
            self.logger.error(f"Error checking entry expiration: {str(e)}")
            return True

    def _evict_entries(self) -> None:
        """Evict cache entries based on policy."""
        try:
            # Calculate entry scores
            scores = {}
            for entry_id, entry in self.cache_entries.items():
                scores[entry_id] = self._calculate_entry_score(entry)
            
            # Sort entries by score
            sorted_entries = sorted(
                scores.items(),
                key=lambda x: x[1]
            )
            
            # Evict entries until below threshold
            target_size = int(
                self.settings["max_cache_size"] *
                (1 - self.settings["thresholds"]["eviction_threshold"])
            )
            
            while len(self.cache_entries) > target_size:
                entry_id = sorted_entries.pop(0)[0]
                self._evict_entry(entry_id)
            
        except Exception as e:
            self.logger.error(f"Error evicting entries: {str(e)}")
            raise

    def _evict_entry(
        self,
        entry_id: str
    ) -> None:
        """Evict a cache entry."""
        try:
            if entry_id in self.cache_entries:
                entry = self.cache_entries.pop(entry_id)
                
                # Update eviction history
                self.eviction_history.append({
                    "entry_id": entry_id,
                    "reason": "manual" if entry_id else "policy",
                    "timestamp": datetime.now().isoformat()
                })
                
                # Update cache metrics
                self._update_cache_metrics("evictions")
                self._update_cache_metrics("size")
            
        except Exception as e:
            self.logger.error(f"Error evicting entry: {str(e)}")
            raise

    def _calculate_entry_score(
        self,
        entry: Dict[str, Any]
    ) -> float:
        """Calculate cache entry score for eviction."""
        try:
            # Calculate frequency score
            max_count = max(
                e["access_count"]
                for e in self.cache_entries.values()
            )
            frequency_score = (
                entry["access_count"] / max_count
                if max_count > 0 else 0
            )
            
            # Calculate recency score
            now = datetime.now()
            accessed_at = datetime.fromisoformat(entry["accessed_at"])
            age = (now - accessed_at).total_seconds()
            max_age = self.settings["cache_ttl"]
            recency_score = 1 - (age / max_age)
            
            # Calculate size score
            size_score = 1.0  # Placeholder for size-based scoring
            
            # Calculate weighted score
            score = (
                frequency_score * self.settings["weights"]["frequency"] +
                recency_score * self.settings["weights"]["recency"] +
                size_score * self.settings["weights"]["size"]
            )
            
            return score
            
        except Exception as e:
            self.logger.error(f"Error calculating entry score: {str(e)}")
            return 0.0

    def _update_access_history(
        self,
        entry_id: str
    ) -> None:
        """Update cache access history."""
        try:
            # Update entry access time and count
            entry = self.cache_entries[entry_id]
            entry["accessed_at"] = datetime.now().isoformat()
            entry["access_count"] += 1
            
            # Add to access history
            self.access_history.append({
                "entry_id": entry_id,
                "timestamp": datetime.now().isoformat()
            })
            
            # Trim access history if needed
            if len(self.access_history) > 1000:  # Keep last 1000 records
                self.access_history = self.access_history[-1000:]
            
        except Exception as e:
            self.logger.error(f"Error updating access history: {str(e)}")
            raise

    def _update_cache_metrics(
        self,
        metric_type: str
    ) -> None:
        """Update cache metrics."""
        try:
            if metric_type == "hits":
                self.cache_metrics["hits"]["count"] += 1
            elif metric_type == "misses":
                self.cache_metrics["misses"]["count"] += 1
            elif metric_type == "evictions":
                self.cache_metrics["evictions"]["count"] += 1
            elif metric_type == "size":
                self.cache_metrics["size"]["current"] = len(self.cache_entries)
            
        except Exception as e:
            self.logger.error(f"Error updating cache metrics: {str(e)}")
            raise 