"""Activity adaptation manager for physical education."""

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
from app.models.physical_education.pe_enums.pe_types import (
    DifficultyLevel,
    EquipmentRequirement,
    AdaptationType,
    AdaptationLevel,
    AdaptationStatus,
    AdaptationTrigger
)
from app.models.physical_education.activity.models import (
    StudentActivityPerformance,
    StudentActivityPreference
)

class ActivityAdaptationManager:
    """Service for adapting physical education activities based on student performance."""
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ActivityAdaptationManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.logger = logging.getLogger("activity_adaptation_manager")
        self.db = None
        
        # Adaptation settings
        self.settings = {
            "adaptation_enabled": True,
            "auto_adapt": True,
            "min_data_points": 5,
            "performance_window": 30,  # days
            "thresholds": {
                "low_performance": 0.4,
                "high_performance": 0.8,
                "significant_change": 0.2
            },
            "weights": {
                "recent_performance": 0.6,
                "historical_performance": 0.2,
                "student_preference": 0.2
            }
        }
        
        # Adaptation components
        self.adaptation_history = []
        self.adaptation_rules = {}
        self.performance_cache = {}
        self.adaptation_cache = {}
    
    async def initialize(self):
        """Initialize the adaptation manager."""
        try:
            # Get database session using context manager
            db_gen = get_db()
            self.db = await anext(db_gen)
            
            # Initialize adaptation rules
            self.initialize_adaptation_rules()
            
            self.logger.info("Activity Adaptation Manager initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing Activity Adaptation Manager: {str(e)}")
            raise
    
    async def cleanup(self):
        """Cleanup the adaptation manager."""
        try:
            # Clear all data
            self.adaptation_history.clear()
            self.adaptation_rules.clear()
            self.performance_cache.clear()
            self.adaptation_cache.clear()
            
            # Reset service references
            self.db = None
            
            self.logger.info("Activity Adaptation Manager cleaned up successfully")
        except Exception as e:
            self.logger.error(f"Error cleaning up Activity Adaptation Manager: {str(e)}")
            raise

    def initialize_adaptation_rules(self):
        """Initialize adaptation rules."""
        try:
            self.adaptation_rules = {
                "difficulty": {
                    "increase": {
                        "condition": lambda performance: performance > self.settings["thresholds"]["high_performance"],
                        "action": self._increase_difficulty
                    },
                    "decrease": {
                        "condition": lambda performance: performance < self.settings["thresholds"]["low_performance"],
                        "action": self._decrease_difficulty
                    }
                },
                "equipment": {
                    "add": {
                        "condition": lambda performance: performance > self.settings["thresholds"]["high_performance"],
                        "action": self._add_equipment
                    },
                    "remove": {
                        "condition": lambda performance: performance < self.settings["thresholds"]["low_performance"],
                        "action": self._remove_equipment
                    }
                },
                "duration": {
                    "increase": {
                        "condition": lambda performance: performance > self.settings["thresholds"]["high_performance"],
                        "action": self._increase_duration
                    },
                    "decrease": {
                        "condition": lambda performance: performance < self.settings["thresholds"]["low_performance"],
                        "action": self._decrease_duration
                    }
                }
            }
            
            self.logger.info("Adaptation rules initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing adaptation rules: {str(e)}")
            raise

    async def adapt_activity(
        self,
        activity_id: str,
        student_id: str,
        force_adapt: bool = False
    ) -> Dict[str, Any]:
        """Adapt an activity based on student performance."""
        try:
            if not self.settings["adaptation_enabled"]:
                raise ValueError("Activity adaptation is disabled")
            
            # Get performance data
            performance_data = await self._get_performance_data(
                activity_id, student_id
            )
            
            if (len(performance_data) < self.settings["min_data_points"] and
                not force_adapt):
                return None
            
            # Calculate performance metrics
            performance_metrics = self._calculate_performance_metrics(
                performance_data
            )
            
            # Determine needed adaptations
            adaptations = self._determine_adaptations(
                performance_metrics
            )
            
            if not adaptations and not force_adapt:
                return None
            
            # Apply adaptations
            adapted_activity = await self._apply_adaptations(
                activity_id,
                adaptations
            )
            
            # Update adaptation history
            self._update_adaptation_history(
                activity_id,
                student_id,
                adaptations,
                performance_metrics
            )
            
            return adapted_activity
            
        except Exception as e:
            self.logger.error(f"Error adapting activity: {str(e)}")
            raise

    async def get_adaptation_history(
        self,
        activity_id: Optional[str] = None,
        student_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get adaptation history for an activity or student."""
        try:
            history = self.adaptation_history
            
            if activity_id:
                history = [h for h in history if h["activity_id"] == activity_id]
            
            if student_id:
                history = [h for h in history if h["student_id"] == student_id]
            
            return history
            
        except Exception as e:
            self.logger.error(f"Error getting adaptation history: {str(e)}")
            raise

    def _calculate_performance_metrics(
        self,
        performance_data: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Calculate performance metrics from performance data."""
        try:
            recent_data = sorted(
                performance_data,
                key=lambda x: x["timestamp"],
                reverse=True
            )[:self.settings["min_data_points"]]
            
            recent_scores = [d["score"] for d in recent_data]
            all_scores = [d["score"] for d in performance_data]
            
            metrics = {
                "recent_average": np.mean(recent_scores),
                "historical_average": np.mean(all_scores),
                "trend": self._calculate_trend(performance_data),
                "volatility": np.std(all_scores),
                "improvement_rate": self._calculate_improvement_rate(performance_data)
            }
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error calculating performance metrics: {str(e)}")
            raise

    def _calculate_trend(
        self,
        performance_data: List[Dict[str, Any]]
    ) -> float:
        """Calculate performance trend."""
        try:
            if len(performance_data) < 2:
                return 0.0
            
            sorted_data = sorted(
                performance_data,
                key=lambda x: x["timestamp"]
            )
            
            scores = [d["score"] for d in sorted_data]
            x = np.arange(len(scores))
            
            # Calculate linear regression
            z = np.polyfit(x, scores, 1)
            slope = z[0]
            
            return slope
            
        except Exception as e:
            self.logger.error(f"Error calculating trend: {str(e)}")
            raise

    def _calculate_improvement_rate(
        self,
        performance_data: List[Dict[str, Any]]
    ) -> float:
        """Calculate improvement rate."""
        try:
            if len(performance_data) < 2:
                return 0.0
            
            sorted_data = sorted(
                performance_data,
                key=lambda x: x["timestamp"]
            )
            
            first_score = sorted_data[0]["score"]
            last_score = sorted_data[-1]["score"]
            time_diff = (
                datetime.fromisoformat(sorted_data[-1]["timestamp"]) -
                datetime.fromisoformat(sorted_data[0]["timestamp"])
            ).days
            
            if time_diff == 0:
                return 0.0
            
            return (last_score - first_score) / time_diff
            
        except Exception as e:
            self.logger.error(f"Error calculating improvement rate: {str(e)}")
            raise

    def _determine_adaptations(
        self,
        performance_metrics: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """Determine needed adaptations based on performance metrics."""
        try:
            adaptations = []
            
            # Check each adaptation rule
            for adaptation_type, rules in self.adaptation_rules.items():
                for action, rule in rules.items():
                    if rule["condition"](performance_metrics["recent_average"]):
                        adaptations.append({
                            "type": adaptation_type,
                            "action": action,
                            "reason": f"Performance threshold triggered: {performance_metrics['recent_average']:.2f}"
                        })
            
            return adaptations
            
        except Exception as e:
            self.logger.error(f"Error determining adaptations: {str(e)}")
            raise

    async def _apply_adaptations(
        self,
        activity_id: str,
        adaptations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Apply adaptations to an activity."""
        try:
            activity = await self._get_activity(activity_id)
            
            for adaptation in adaptations:
                action = self.adaptation_rules[adaptation["type"]][adaptation["action"]]["action"]
                activity = await action(activity)
            
            # Save adapted activity
            updated_activity = await self._save_activity(activity)
            
            return updated_activity
            
        except Exception as e:
            self.logger.error(f"Error applying adaptations: {str(e)}")
            raise

    def _update_adaptation_history(
        self,
        activity_id: str,
        student_id: str,
        adaptations: List[Dict[str, Any]],
        performance_metrics: Dict[str, float]
    ) -> None:
        """Update adaptation history."""
        try:
            self.adaptation_history.append({
                "activity_id": activity_id,
                "student_id": student_id,
                "adaptations": adaptations,
                "performance_metrics": performance_metrics,
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            self.logger.error(f"Error updating adaptation history: {str(e)}")
            raise

    # Adaptation actions
    async def _increase_difficulty(self, activity: Dict[str, Any]) -> Dict[str, Any]:
        """Increase activity difficulty."""
        try:
            current_level = DifficultyLevel[activity["difficulty"]]
            levels = list(DifficultyLevel)
            current_index = levels.index(current_level)
            
            if current_index < len(levels) - 1:
                activity["difficulty"] = levels[current_index + 1].value
            
            return activity
            
        except Exception as e:
            self.logger.error(f"Error increasing difficulty: {str(e)}")
            raise

    async def _decrease_difficulty(self, activity: Dict[str, Any]) -> Dict[str, Any]:
        """Decrease activity difficulty."""
        try:
            current_level = DifficultyLevel[activity["difficulty"]]
            levels = list(DifficultyLevel)
            current_index = levels.index(current_level)
            
            if current_index > 0:
                activity["difficulty"] = levels[current_index - 1].value
            
            return activity
            
        except Exception as e:
            self.logger.error(f"Error decreasing difficulty: {str(e)}")
            raise

    async def _add_equipment(self, activity: Dict[str, Any]) -> Dict[str, Any]:
        """Add equipment to activity."""
        try:
            # Implementation depends on equipment rules
            return activity
            
        except Exception as e:
            self.logger.error(f"Error adding equipment: {str(e)}")
            raise

    async def _remove_equipment(self, activity: Dict[str, Any]) -> Dict[str, Any]:
        """Remove equipment from activity."""
        try:
            # Implementation depends on equipment rules
            return activity
            
        except Exception as e:
            self.logger.error(f"Error removing equipment: {str(e)}")
            raise

    async def _increase_duration(self, activity: Dict[str, Any]) -> Dict[str, Any]:
        """Increase activity duration."""
        try:
            activity["duration"] = int(activity["duration"] * 1.2)  # 20% increase
            return activity
            
        except Exception as e:
            self.logger.error(f"Error increasing duration: {str(e)}")
            raise

    async def _decrease_duration(self, activity: Dict[str, Any]) -> Dict[str, Any]:
        """Decrease activity duration."""
        try:
            activity["duration"] = int(activity["duration"] * 0.8)  # 20% decrease
            return activity
            
        except Exception as e:
            self.logger.error(f"Error decreasing duration: {str(e)}")
            raise 