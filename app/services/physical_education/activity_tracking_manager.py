from app.services.physical_education.config.model_paths import get_model_path, ensure_model_directories 

"""Activity tracking manager for physical education."""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import numpy as np
from sqlalchemy.orm import Session
from app.core.database import get_db

# Import models
from app.models.activity import (
    Activity,
    ActivityType,
    ActivityCategoryAssociation
)
from app.models.student import Student
from app.models.tracking import (
    ActivityTracking,
    TrackingMetrics,
    TrackingHistory,
    TrackingStatus
)
from app.models.physical_education.pe_enums.pe_types import (
    TrackingType,
    TrackingLevel,
    TrackingStatus,
    TrackingTrigger,
    DifficultyLevel,
    EquipmentRequirement
)
from app.models.physical_education.activity.models import (
    StudentActivityPerformance,
    StudentActivityPreference
)

class ActivityTrackingManager:
    """Service for tracking physical education activities."""
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ActivityTrackingManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.logger = logging.getLogger("activity_tracking_manager")
        self.db = None
        
        # Tracking settings
        self.settings = {
            "tracking_enabled": True,
            "auto_track": True,
            "min_data_points": 5,
            "tracking_window": 30,  # days
            "thresholds": {
                "low_activity": 0.4,
                "high_activity": 0.8,
                "significant_change": 0.2
            },
            "weights": {
                "recent_activity": 0.6,
                "historical_activity": 0.2,
                "student_preference": 0.2
            }
        }
        
        # Tracking components
        self.tracking_history = []
        self.tracking_metrics = {}
        self.performance_cache = {}
        self.tracking_cache = {}
    
    async def initialize(self):
        """Initialize the tracking manager."""
        try:
            # Get database session using context manager
            db_gen = get_db()
            self.db = await anext(db_gen)
            
            # Initialize tracking metrics
            self.initialize_tracking_metrics()
            
            self.logger.info("Activity Tracking Manager initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing Activity Tracking Manager: {str(e)}")
            raise
    
    async def cleanup(self):
        """Cleanup the tracking manager."""
        try:
            # Clear all data
            self.tracking_history.clear()
            self.tracking_metrics.clear()
            self.performance_cache.clear()
            self.tracking_cache.clear()
            
            # Reset service references
            self.db = None
            
            self.logger.info("Activity Tracking Manager cleaned up successfully")
        except Exception as e:
            self.logger.error(f"Error cleaning up Activity Tracking Manager: {str(e)}")
            raise

    def initialize_tracking_metrics(self):
        """Initialize tracking metrics."""
        try:
            self.tracking_metrics = {
                "activity": {
                    "duration": {
                        "description": "Total activity duration",
                        "unit": "minutes",
                        "aggregation": "sum"
                    },
                    "intensity": {
                        "description": "Average activity intensity",
                        "unit": "score",
                        "aggregation": "mean"
                    },
                    "frequency": {
                        "description": "Activity frequency",
                        "unit": "count",
                        "aggregation": "count"
                    }
                },
                "performance": {
                    "score": {
                        "description": "Average performance score",
                        "unit": "score",
                        "aggregation": "mean"
                    },
                    "improvement": {
                        "description": "Performance improvement rate",
                        "unit": "rate",
                        "aggregation": "diff"
                    },
                    "consistency": {
                        "description": "Performance consistency",
                        "unit": "score",
                        "aggregation": "std"
                    }
                }
            }
            
            self.logger.info("Tracking metrics initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing tracking metrics: {str(e)}")
            raise

    async def track_activity(
        self,
        activity_id: str,
        student_id: str,
        tracking_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Track student activity and performance."""
        try:
            if not self.settings["tracking_enabled"]:
                raise ValueError("Activity tracking is disabled")
            
            # Validate tracking data
            self._validate_tracking_data(tracking_data)
            
            # Calculate tracking metrics
            metrics = self._calculate_tracking_metrics(tracking_data)
            
            # Create tracking record
            tracking = {
                "activity_id": activity_id,
                "student_id": student_id,
                "data": tracking_data,
                "metrics": metrics,
                "timestamp": datetime.now().isoformat()
            }
            
            # Update tracking history
            self._update_tracking_history(tracking)
            
            # Update performance cache
            self._update_performance_cache(
                student_id,
                activity_id,
                metrics
            )
            
            return tracking
            
        except Exception as e:
            self.logger.error(f"Error tracking activity: {str(e)}")
            raise

    async def get_tracking_history(
        self,
        activity_id: Optional[str] = None,
        student_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get tracking history for an activity or student."""
        try:
            history = self.tracking_history
            
            if activity_id:
                history = [h for h in history if h["activity_id"] == activity_id]
            
            if student_id:
                history = [h for h in history if h["student_id"] == student_id]
            
            return history
            
        except Exception as e:
            self.logger.error(f"Error getting tracking history: {str(e)}")
            raise

    def _validate_tracking_data(
        self,
        tracking_data: Dict[str, Any]
    ) -> None:
        """Validate tracking data."""
        try:
            required_fields = [
                "duration",
                "intensity",
                "performance_score"
            ]
            
            for field in required_fields:
                if field not in tracking_data:
                    raise ValueError(f"Missing required field: {field}")
                
            # Validate data types and ranges
            if not isinstance(tracking_data["duration"], (int, float)):
                raise ValueError("Duration must be a number")
            
            if not isinstance(tracking_data["intensity"], (int, float)):
                raise ValueError("Intensity must be a number")
            
            if not isinstance(tracking_data["performance_score"], (int, float)):
                raise ValueError("Performance score must be a number")
            
            if tracking_data["duration"] < 0:
                raise ValueError("Duration cannot be negative")
            
            if not 0 <= tracking_data["intensity"] <= 10:
                raise ValueError("Intensity must be between 0 and 10")
            
            if not 0 <= tracking_data["performance_score"] <= 100:
                raise ValueError("Performance score must be between 0 and 100")
            
        except Exception as e:
            self.logger.error(f"Error validating tracking data: {str(e)}")
            raise

    def _calculate_tracking_metrics(
        self,
        tracking_data: Dict[str, Any]
    ) -> Dict[str, float]:
        """Calculate tracking metrics from tracking data."""
        try:
            metrics = {}
            
            # Calculate activity metrics
            metrics["activity_duration"] = tracking_data["duration"]
            metrics["activity_intensity"] = tracking_data["intensity"]
            metrics["activity_score"] = tracking_data["performance_score"]
            
            # Calculate derived metrics
            metrics["activity_volume"] = (
                tracking_data["duration"] *
                tracking_data["intensity"]
            )
            
            metrics["efficiency_score"] = (
                tracking_data["performance_score"] /
                (tracking_data["duration"] * tracking_data["intensity"])
            ) * 100
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error calculating tracking metrics: {str(e)}")
            raise

    def _update_tracking_history(
        self,
        tracking: Dict[str, Any]
    ) -> None:
        """Update tracking history."""
        try:
            self.tracking_history.append(tracking)
            
            # Trim history if needed
            if len(self.tracking_history) > 1000:  # Keep last 1000 records
                self.tracking_history = self.tracking_history[-1000:]
            
        except Exception as e:
            self.logger.error(f"Error updating tracking history: {str(e)}")
            raise

    def _update_performance_cache(
        self,
        student_id: str,
        activity_id: str,
        metrics: Dict[str, float]
    ) -> None:
        """Update performance cache."""
        try:
            cache_key = f"{student_id}_{activity_id}"
            
            if cache_key not in self.performance_cache:
                self.performance_cache[cache_key] = []
            
            self.performance_cache[cache_key].append({
                "timestamp": datetime.now().isoformat(),
                "metrics": metrics
            })
            
            # Trim cache if needed
            if len(self.performance_cache[cache_key]) > 100:  # Keep last 100 records
                self.performance_cache[cache_key] = self.performance_cache[cache_key][-100:]
            
        except Exception as e:
            self.logger.error(f"Error updating performance cache: {str(e)}")
            raise 