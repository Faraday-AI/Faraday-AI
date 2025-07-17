from app.services.physical_education.config.model_paths import get_model_path, ensure_model_directories 

"""Activity planning manager for physical education."""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import numpy as np
from sqlalchemy.orm import Session
from app.core.database import get_db

# Import models
from app.models.physical_education.activity import Activity
from app.models.activity import (
    ActivityCategoryAssociation
)
from app.models.student import Student
from app.models.planning import (
    ActivityPlan,
    PlanningMetrics,
    PlanningHistory
)
from app.models.physical_education.pe_enums.pe_types import (
    ActivityType,
    DifficultyLevel,
    EquipmentRequirement,
    PlanningType,
    PlanningLevel,
    PlanningStatus,
    PlanningTrigger
)
from app.models.physical_education.activity.models import (
    StudentActivityPerformance,
    StudentActivityPreference
)

class ActivityPlanningManager:
    """Service for planning physical education activities."""
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ActivityPlanningManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.logger = logging.getLogger("activity_planning_manager")
        self.db = None
        
        # Planning settings
        self.settings = {
            "planning_enabled": True,
            "auto_plan": True,
            "min_data_points": 5,
            "planning_window": 30,  # days
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
        
        # Planning components
        self.planning_history = []
        self.planning_metrics = {}
        self.performance_cache = {}
        self.planning_cache = {}
    
    async def initialize(self):
        """Initialize the planning manager."""
        try:
            # Get database session using context manager
            db_gen = get_db()
            self.db = await anext(db_gen)
            
            # Initialize planning metrics
            self.initialize_planning_metrics()
            
            self.logger.info("Activity Planning Manager initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing Activity Planning Manager: {str(e)}")
            raise
    
    async def cleanup(self):
        """Cleanup the planning manager."""
        try:
            # Clear all data
            self.planning_history.clear()
            self.planning_metrics.clear()
            self.performance_cache.clear()
            self.planning_cache.clear()
            
            # Reset service references
            self.db = None
            
            self.logger.info("Activity Planning Manager cleaned up successfully")
        except Exception as e:
            self.logger.error(f"Error cleaning up Activity Planning Manager: {str(e)}")
            raise

    def initialize_planning_metrics(self):
        """Initialize planning metrics."""
        try:
            self.planning_metrics = {
                "activity": {
                    "duration": {
                        "description": "Planned activity duration",
                        "unit": "minutes",
                        "aggregation": "sum"
                    },
                    "intensity": {
                        "description": "Planned activity intensity",
                        "unit": "score",
                        "aggregation": "mean"
                    },
                    "frequency": {
                        "description": "Planned activity frequency",
                        "unit": "count",
                        "aggregation": "count"
                    }
                },
                "performance": {
                    "target_score": {
                        "description": "Target performance score",
                        "unit": "score",
                        "aggregation": "mean"
                    },
                    "improvement_goal": {
                        "description": "Target improvement rate",
                        "unit": "rate",
                        "aggregation": "diff"
                    },
                    "consistency_goal": {
                        "description": "Target consistency",
                        "unit": "score",
                        "aggregation": "std"
                    }
                }
            }
            
            self.logger.info("Planning metrics initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing planning metrics: {str(e)}")
            raise

    async def create_activity_plan(
        self,
        student_id: str,
        plan_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create an activity plan for a student."""
        try:
            if not self.settings["planning_enabled"]:
                raise ValueError("Activity planning is disabled")
            
            # Validate plan data
            self._validate_plan_data(plan_data)
            
            # Calculate planning metrics
            metrics = self._calculate_planning_metrics(plan_data)
            
            # Create plan record
            plan = {
                "student_id": student_id,
                "data": plan_data,
                "metrics": metrics,
                "status": "draft",
                "timestamp": datetime.now().isoformat()
            }
            
            # Update planning history
            self._update_planning_history(plan)
            
            # Update performance cache
            self._update_performance_cache(
                student_id,
                metrics
            )
            
            return plan
            
        except Exception as e:
            self.logger.error(f"Error creating activity plan: {str(e)}")
            raise

    async def get_planning_history(
        self,
        student_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get planning history for a student."""
        try:
            history = self.planning_history
            
            if student_id:
                history = [h for h in history if h["student_id"] == student_id]
            
            return history
            
        except Exception as e:
            self.logger.error(f"Error getting planning history: {str(e)}")
            raise

    def _validate_plan_data(
        self,
        plan_data: Dict[str, Any]
    ) -> None:
        """Validate plan data."""
        try:
            required_fields = [
                "activities",
                "duration",
                "intensity",
                "target_score"
            ]
            
            for field in required_fields:
                if field not in plan_data:
                    raise ValueError(f"Missing required field: {field}")
                
            # Validate activities
            if not isinstance(plan_data["activities"], list):
                raise ValueError("Activities must be a list")
            
            if not plan_data["activities"]:
                raise ValueError("Activities list cannot be empty")
            
            # Validate data types and ranges
            if not isinstance(plan_data["duration"], (int, float)):
                raise ValueError("Duration must be a number")
            
            if not isinstance(plan_data["intensity"], (int, float)):
                raise ValueError("Intensity must be a number")
            
            if not isinstance(plan_data["target_score"], (int, float)):
                raise ValueError("Target score must be a number")
            
            if plan_data["duration"] < 0:
                raise ValueError("Duration cannot be negative")
            
            if not 0 <= plan_data["intensity"] <= 10:
                raise ValueError("Intensity must be between 0 and 10")
            
            if not 0 <= plan_data["target_score"] <= 100:
                raise ValueError("Target score must be between 0 and 100")
            
        except Exception as e:
            self.logger.error(f"Error validating plan data: {str(e)}")
            raise

    def _calculate_planning_metrics(
        self,
        plan_data: Dict[str, Any]
    ) -> Dict[str, float]:
        """Calculate planning metrics from plan data."""
        try:
            metrics = {}
            
            # Calculate activity metrics
            metrics["planned_duration"] = plan_data["duration"]
            metrics["planned_intensity"] = plan_data["intensity"]
            metrics["target_score"] = plan_data["target_score"]
            
            # Calculate derived metrics
            metrics["planned_volume"] = (
                plan_data["duration"] *
                plan_data["intensity"]
            )
            
            metrics["efficiency_target"] = (
                plan_data["target_score"] /
                (plan_data["duration"] * plan_data["intensity"])
            ) * 100
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error calculating planning metrics: {str(e)}")
            raise

    def _update_planning_history(
        self,
        plan: Dict[str, Any]
    ) -> None:
        """Update planning history."""
        try:
            self.planning_history.append(plan)
            
            # Trim history if needed
            if len(self.planning_history) > 1000:  # Keep last 1000 records
                self.planning_history = self.planning_history[-1000:]
            
        except Exception as e:
            self.logger.error(f"Error updating planning history: {str(e)}")
            raise

    def _update_performance_cache(
        self,
        student_id: str,
        metrics: Dict[str, float]
    ) -> None:
        """Update performance cache."""
        try:
            if student_id not in self.performance_cache:
                self.performance_cache[student_id] = []
            
            self.performance_cache[student_id].append({
                "timestamp": datetime.now().isoformat(),
                "metrics": metrics
            })
            
            # Trim cache if needed
            if len(self.performance_cache[student_id]) > 100:  # Keep last 100 records
                self.performance_cache[student_id] = self.performance_cache[student_id][-100:]
            
        except Exception as e:
            self.logger.error(f"Error updating performance cache: {str(e)}")
            raise 