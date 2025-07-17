"""Activity rate limit manager for physical education."""

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
    
    def __init__(self):
        self.logger = logging.getLogger("activity_rate_limit_manager")
        self.db = None
        
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
            }
        }
        
        # Rate limit components
        self.rate_limits = {}
        self.rate_metrics = {}
        self.request_history = []
        self.violation_history = []
    
    async def initialize(self):
        """Initialize the rate limit manager."""
        try:
            self.db = next(get_db())
            
            # Initialize rate limit components
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
                    "rate": 0.0
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
        activity_id: str,
        student_id: str
    ) -> Dict[str, Any]:
        """Check if request is within rate limits."""
        try:
            if not self.settings["rate_limit_enabled"]:
                return {"allowed": True}
            
            # Get rate limit key
            limit_key = f"{student_id}_{activity_id}"
            
            # Check concurrent requests
            if not self._check_concurrent_limit():
                return {
                    "allowed": False,
                    "reason": "Too many concurrent requests"
                }
            
            # Check request rate
            if not self._check_request_rate(limit_key):
                return {
                    "allowed": False,
                    "reason": "Request rate exceeded"
                }
            
            # Check burst limit
            if not self._check_burst_limit(limit_key):
                return {
                    "allowed": False,
                    "reason": "Burst limit exceeded"
                }
            
            # Update metrics
            self._update_rate_metrics("requests")
            
            return {"allowed": True}
            
        except Exception as e:
            self.logger.error(f"Error checking rate limit: {str(e)}")
            raise

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