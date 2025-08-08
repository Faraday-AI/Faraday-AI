"""Activity rate limit manager for physical education."""

import logging
import redis
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import numpy as np
from sqlalchemy.orm import Session
from app.core.database import get_db

# Import models
from app.models.activity import (
    Activity,
    ActivityCategoryAssociation
)
from app.models.student import Student
from app.models.physical_education.activity.models import (
    StudentActivityPerformance,
    StudentActivityPreference
)
from app.models.physical_education.pe_enums.pe_types import (
    ActivityType,
    DifficultyLevel,
    EquipmentRequirement,
    RateLimitType,
    RateLimitLevel,
    RateLimitStatus,
    RateLimitTrigger,
    ActivityCategoryType
)

class ActivityRateLimitManager:
    """Service for managing physical education activity rate limiting."""
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ActivityRateLimitManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, db: Session = None):
        self.logger = logging.getLogger("activity_rate_limit_manager")
        self.db = db
        
        # Initialize Redis connection
        try:
            from app.core.config import get_settings
            settings = get_settings()
            self.redis_client = redis.Redis.from_url(
                settings.REDIS_URL,
                decode_responses=True
            )
            self.redis_client.ping()  # Test connection
        except Exception as e:
            self.logger.warning(f"Redis connection failed: {str(e)}")
            self.redis_client = None
        
        # Rate limit settings
        self.settings = {
            "rate_limit_enabled": True,
            "auto_limit": True,
            "window_size": 3600,  # seconds
            "thresholds": {
                "low_usage": 0.2,
                "high_usage": 0.8,
                "burst_threshold": 0.9
            },
            "limits": {
                "requests_per_window": 1000,
                "burst_size": 100,
                "concurrent_requests": 10
            },
            "default_limits": {
                "create_activity": {"max_requests": 10, "time_window": 3600},
                "participate_activity": {"max_requests": 100, "time_window": 3600},
                "update_progress": {"max_requests": 50, "time_window": 3600}
            },
            "block_duration": 3600  # 1 hour
        }
        
        # Rate limit components
        self.rate_limits = {}
        self.rate_metrics = {}
        self.request_history = []
        self.violation_history = []
        
        # Initialize assessment criteria
        self.initialize_rate_limit_components()
    
    async def initialize(self):
        """Initialize the rate limit manager."""
        try:
            # Initialize assessment criteria
            self.initialize_rate_limit_components()
            
            self.logger.info("Activity Rate Limit Manager initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing Activity Rate Limit Manager: {str(e)}")
            raise
    
    async def cleanup(self):
        """Cleanup the rate limit manager."""
        try:
            # Clear all data
            self.rate_limits.clear()
            self.rate_metrics.clear()
            self.request_history.clear()
            self.violation_history.clear()
            
            # Reset service references
            self.db = None
            
            self.logger.info("Activity Rate Limit Manager cleaned up successfully")
        except Exception as e:
            self.logger.error(f"Error cleaning up Activity Rate Limit Manager: {str(e)}")
            raise

    def initialize_rate_limit_components(self):
        """Initialize rate limit components."""
        try:
            # Initialize rate metrics
            self.rate_metrics = {
                "requests": {
                    "count": 0,
                    "rate": 0.0,
                    "window_start": datetime.now().isoformat()
                },
                "violations": {
                    "count": 0,
                    "rate": 0.0,
                    "window_start": datetime.now().isoformat()
                },
                "concurrent": {
                    "current": 0,
                    "max": self.settings["limits"]["concurrent_requests"]
                }
            }
            
            self.logger.info("Rate limit components initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing rate limit components: {str(e)}")
            raise

    async def check_rate_limit(
        self,
        user_id: str,
        action: str
    ) -> bool:
        """Check if request is within rate limits."""
        try:
            if not self.settings["rate_limit_enabled"]:
                return True
            
            if not self.redis_client:
                # Fallback to in-memory if Redis is not available
                return True
            
            # Get rate limit configuration
            config = self.settings["default_limits"].get(action)
            if not config:
                return True
            
            # Create Redis key
            redis_key = f"rate_limit:{user_id}:{action}"
            
            # Get current count and timestamp from Redis
            current_data = self.redis_client.get(redis_key)
            
            if current_data is None:
                # First request
                current_count = 0
                current_time = datetime.now().timestamp()
            else:
                # Parse existing data
                try:
                    count_str, timestamp_str = current_data.split(":")
                    current_count = int(count_str)
                    current_time = float(timestamp_str)
                except (ValueError, AttributeError):
                    current_count = 0
                    current_time = datetime.now().timestamp()
            
            # Check if window has expired
            now = datetime.now().timestamp()
            window_duration = config["time_window"]
            
            if now - current_time > window_duration:
                # Window expired, reset count
                current_count = 0
                current_time = now
            
            # Check if limit exceeded (before incrementing)
            if current_count >= config["max_requests"]:
                return False
            
            # Increment count for current request
            current_count += 1
            
            # Store updated data in Redis
            new_data = f"{current_count}:{current_time}"
            self.redis_client.setex(
                redis_key,
                window_duration,
                new_data
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking rate limit: {str(e)}")
            return True  # Allow request on error

    async def get_rate_metrics(self) -> Dict[str, Any]:
        """Get rate limit metrics."""
        try:
            # Calculate rates
            window_start = datetime.fromisoformat(
                self.rate_metrics["requests"]["window_start"]
            )
            now = datetime.now()
            window_duration = (now - window_start).total_seconds()
            
            if window_duration > 0:
                self.rate_metrics["requests"]["rate"] = (
                    self.rate_metrics["requests"]["count"] /
                    window_duration
                )
                
                self.rate_metrics["violations"]["rate"] = (
                    self.rate_metrics["violations"]["count"] /
                    window_duration
                )
            
            return self.rate_metrics
            
        except Exception as e:
            self.logger.error(f"Error getting rate metrics: {str(e)}")
            raise

    def _check_concurrent_limit(self) -> bool:
        """Check concurrent request limit."""
        try:
            return (
                self.rate_metrics["concurrent"]["current"] <
                self.rate_metrics["concurrent"]["max"]
            )
            
        except Exception as e:
            self.logger.error(f"Error checking concurrent limit: {str(e)}")
            return False

    def _check_request_rate(
        self,
        limit_key: str
    ) -> bool:
        """Check request rate limit."""
        try:
            if limit_key not in self.rate_limits:
                self.rate_limits[limit_key] = {
                    "count": 0,
                    "window_start": datetime.now().isoformat()
                }
            
            limit = self.rate_limits[limit_key]
            window_start = datetime.fromisoformat(limit["window_start"])
            now = datetime.now()
            
            # Check if window has expired
            if (now - window_start).total_seconds() > self.settings["window_size"]:
                # Reset window
                limit["count"] = 0
                limit["window_start"] = now.isoformat()
                return True
            
            # Check if limit exceeded
            return limit["count"] < self.settings["limits"]["requests_per_window"]
            
        except Exception as e:
            self.logger.error(f"Error checking request rate: {str(e)}")
            return False

    def _check_burst_limit(
        self,
        limit_key: str
    ) -> bool:
        """Check burst limit."""
        try:
            if limit_key not in self.rate_limits:
                return True
            
            limit = self.rate_limits[limit_key]
            
            # Get recent requests
            recent_requests = [
                r for r in self.request_history
                if r["limit_key"] == limit_key
            ][-self.settings["limits"]["burst_size"]:]
            
            if not recent_requests:
                return True
            
            # Calculate burst rate
            first_request = datetime.fromisoformat(recent_requests[0]["timestamp"])
            last_request = datetime.fromisoformat(recent_requests[-1]["timestamp"])
            duration = (last_request - first_request).total_seconds()
            
            if duration == 0:
                return False
            
            burst_rate = len(recent_requests) / duration
            
            return burst_rate <= (
                self.settings["limits"]["requests_per_window"] /
                self.settings["window_size"]
            )
            
        except Exception as e:
            self.logger.error(f"Error checking burst limit: {str(e)}")
            return False

    def _update_rate_metrics(
        self,
        metric_type: str
    ) -> None:
        """Update rate limit metrics."""
        try:
            if metric_type == "requests":
                self.rate_metrics["requests"]["count"] += 1
            elif metric_type == "violations":
                self.rate_metrics["violations"]["count"] += 1
            elif metric_type == "concurrent":
                self.rate_metrics["concurrent"]["current"] += 1
            
        except Exception as e:
            self.logger.error(f"Error updating rate metrics: {str(e)}")
            raise
    
    async def block_user(self, user_id: str, reason: str) -> bool:
        """Block a user from making requests."""
        try:
            if not self.redis_client:
                # Fallback to in-memory if Redis is not available
                blocked_users = getattr(self, '_blocked_users', {})
                blocked_users[user_id] = {
                    "reason": reason,
                    "blocked_at": datetime.now().isoformat()
                }
                self._blocked_users = blocked_users
                return True
            
            # Store block in Redis
            redis_key = f"blocked:{user_id}"
            self.redis_client.setex(
                redis_key,
                self.settings["block_duration"],
                reason
            )
            return True
        except Exception as e:
            self.logger.error(f"Error blocking user: {str(e)}")
            return False
    
    async def is_user_blocked(self, user_id: str) -> str:
        """Check if a user is blocked. Returns reason if blocked, None if not."""
        try:
            if not self.redis_client:
                # Fallback to in-memory if Redis is not available
                blocked_users = getattr(self, '_blocked_users', {})
                return blocked_users.get(user_id, {}).get("reason") if user_id in blocked_users else None
            
            # Check Redis for block
            redis_key = f"blocked:{user_id}"
            reason = self.redis_client.get(redis_key)
            return reason
        except Exception as e:
            self.logger.error(f"Error checking if user is blocked: {str(e)}")
            return None
    
    async def unblock_user(self, user_id: str) -> bool:
        """Unblock a user."""
        try:
            if not self.redis_client:
                # Fallback to in-memory if Redis is not available
                blocked_users = getattr(self, '_blocked_users', {})
                if user_id in blocked_users:
                    del blocked_users[user_id]
                    self._blocked_users = blocked_users
                    return True
                return False
            
            # Remove block from Redis
            redis_key = f"blocked:{user_id}"
            result = self.redis_client.delete(redis_key)
            return result > 0
        except Exception as e:
            self.logger.error(f"Error unblocking user: {str(e)}")
            return False
    
    async def get_rate_limit_stats(self, user_id: str) -> Dict[str, Any]:
        """Get rate limit statistics for a user."""
        try:
            if not self.redis_client:
                # Fallback to in-memory if Redis is not available
                return {}
            
            stats = {}
            for action in self.settings["default_limits"]:
                redis_key = f"rate_limit:{user_id}:{action}"
                current_data = self.redis_client.get(redis_key)
                
                if current_data:
                    try:
                        count_str, timestamp_str = current_data.split(":")
                        current_count = int(count_str)
                        window_start = float(timestamp_str)
                    except (ValueError, AttributeError):
                        current_count = 0
                        window_start = datetime.now().timestamp()
                else:
                    current_count = 0
                    window_start = datetime.now().timestamp()
                
                config = self.settings["default_limits"][action]
                stats[action] = {
                    "current_count": current_count,
                    "max_allowed": config["max_requests"],
                    "window_start": window_start,
                    "time_window": config["time_window"]
                }
            
            return stats
        except Exception as e:
            self.logger.error(f"Error getting rate limit stats: {str(e)}")
            return {} 