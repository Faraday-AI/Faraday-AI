"""
Activity Rate Limit Manager Service

This module provides rate limiting functionality for physical education activities.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.core.database import get_db

logger = logging.getLogger(__name__)

class RateLimitConfig:
    """Configuration for rate limiting."""
    
    def __init__(
        self,
        max_requests: int,
        window_seconds: int,
        burst_limit: Optional[int] = None
    ):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.burst_limit = burst_limit or max_requests

class ActivityRateLimitManager:
    """Service for managing rate limits for physical education activities."""
    
    def __init__(self, db: Session = None):
        self.logger = logging.getLogger("activity_rate_limit_manager")
        self.db = db
        self._rate_limits = {}
        self._request_history = {}
        
        # Default rate limit configurations
        self._default_configs = {
            "activity_creation": RateLimitConfig(max_requests=10, window_seconds=3600),  # 10 per hour
            "activity_participation": RateLimitConfig(max_requests=100, window_seconds=3600),  # 100 per hour
            "progress_update": RateLimitConfig(max_requests=50, window_seconds=3600),  # 50 per hour
            "assessment_submission": RateLimitConfig(max_requests=20, window_seconds=3600),  # 20 per hour
        }
        
    async def check_rate_limit(
        self,
        user_id: str,
        activity_type: str,
        custom_config: Optional[RateLimitConfig] = None
    ) -> Dict[str, Any]:
        """Check if a request is within rate limits."""
        try:
            config = custom_config or self._default_configs.get(activity_type)
            if not config:
                return {"allowed": True, "remaining": -1, "reset_time": None}
            
            key = f"{user_id}:{activity_type}"
            now = datetime.utcnow()
            window_start = now - timedelta(seconds=config.window_seconds)
            
            # Get request history for this user and activity type
            if key not in self._request_history:
                self._request_history[key] = []
            
            # Remove old requests outside the window
            self._request_history[key] = [
                req_time for req_time in self._request_history[key]
                if req_time > window_start
            ]
            
            # Check if request is allowed
            current_requests = len(self._request_history[key])
            allowed = current_requests < config.max_requests
            
            if allowed:
                # Add current request to history
                self._request_history[key].append(now)
            
            # Calculate remaining requests and reset time
            remaining = max(0, config.max_requests - current_requests - (1 if allowed else 0))
            reset_time = window_start + timedelta(seconds=config.window_seconds)
            
            return {
                "allowed": allowed,
                "remaining": remaining,
                "reset_time": reset_time.isoformat(),
                "current_requests": current_requests,
                "max_requests": config.max_requests,
                "window_seconds": config.window_seconds
            }
            
        except Exception as e:
            self.logger.error(f"Error checking rate limit: {str(e)}")
            return {"allowed": True, "remaining": -1, "reset_time": None}
    
    async def get_rate_limit_status(
        self,
        user_id: str,
        activity_type: str
    ) -> Dict[str, Any]:
        """Get current rate limit status for a user and activity type."""
        try:
            config = self._default_configs.get(activity_type)
            if not config:
                return {"error": "Unknown activity type"}
            
            key = f"{user_id}:{activity_type}"
            now = datetime.utcnow()
            window_start = now - timedelta(seconds=config.window_seconds)
            
            if key not in self._request_history:
                return {
                    "current_requests": 0,
                    "max_requests": config.max_requests,
                    "remaining": config.max_requests,
                    "window_seconds": config.window_seconds,
                    "reset_time": (window_start + timedelta(seconds=config.window_seconds)).isoformat()
                }
            
            # Remove old requests outside the window
            self._request_history[key] = [
                req_time for req_time in self._request_history[key]
                if req_time > window_start
            ]
            
            current_requests = len(self._request_history[key])
            remaining = max(0, config.max_requests - current_requests)
            reset_time = window_start + timedelta(seconds=config.window_seconds)
            
            return {
                "current_requests": current_requests,
                "max_requests": config.max_requests,
                "remaining": remaining,
                "window_seconds": config.window_seconds,
                "reset_time": reset_time.isoformat(),
                "is_limited": current_requests >= config.max_requests
            }
            
        except Exception as e:
            self.logger.error(f"Error getting rate limit status: {str(e)}")
            return {"error": str(e)}
    
    async def reset_rate_limit(
        self,
        user_id: str,
        activity_type: str
    ) -> bool:
        """Reset rate limit for a user and activity type."""
        try:
            key = f"{user_id}:{activity_type}"
            if key in self._request_history:
                del self._request_history[key]
            return True
        except Exception as e:
            self.logger.error(f"Error resetting rate limit: {str(e)}")
            return False
    
    async def set_custom_rate_limit(
        self,
        activity_type: str,
        max_requests: int,
        window_seconds: int,
        burst_limit: Optional[int] = None
    ) -> bool:
        """Set a custom rate limit configuration for an activity type."""
        try:
            self._default_configs[activity_type] = RateLimitConfig(
                max_requests=max_requests,
                window_seconds=window_seconds,
                burst_limit=burst_limit
            )
            return True
        except Exception as e:
            self.logger.error(f"Error setting custom rate limit: {str(e)}")
            return False
    
    async def get_all_rate_limits(self) -> Dict[str, Any]:
        """Get all current rate limit configurations."""
        try:
            return {
                activity_type: {
                    "max_requests": config.max_requests,
                    "window_seconds": config.window_seconds,
                    "burst_limit": config.burst_limit
                }
                for activity_type, config in self._default_configs.items()
            }
        except Exception as e:
            self.logger.error(f"Error getting all rate limits: {str(e)}")
            return {}
    
    async def cleanup_old_requests(self) -> int:
        """Clean up old request history entries."""
        try:
            now = datetime.utcnow()
            cleaned_count = 0
            
            for key, requests in list(self._request_history.items()):
                # Keep only requests from the last 24 hours
                cutoff_time = now - timedelta(hours=24)
                original_count = len(requests)
                self._request_history[key] = [
                    req_time for req_time in requests
                    if req_time > cutoff_time
                ]
                cleaned_count += original_count - len(self._request_history[key])
                
                # Remove empty entries
                if not self._request_history[key]:
                    del self._request_history[key]
            
            return cleaned_count
        except Exception as e:
            self.logger.error(f"Error cleaning up old requests: {str(e)}")
            return 0 