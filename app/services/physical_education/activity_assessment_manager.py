"""Activity assessment manager for physical education."""

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
from app.models.assessment import (
    GeneralAssessment,
    AssessmentCriteria,
    AssessmentResult,
    AssessmentHistory
)
from app.models.physical_education.pe_enums.pe_types import (
    ActivityType,
    DifficultyLevel,
    EquipmentRequirement,
    AssessmentType,
    AssessmentStatus,
    AssessmentLevel,
    AssessmentTrigger
)
from app.models.physical_education.activity.models import (
    StudentActivityPerformance,
    StudentActivityPreference
)

class ActivityAssessmentManager:
    """Service for managing physical education activity assessments."""
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ActivityAssessmentManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.logger = logging.getLogger("activity_assessment_manager")
        self.db = None
        
        # Assessment settings
        self.settings = {
            "assessment_enabled": True,
            "auto_assess": True,
            "min_data_points": 5,
            "assessment_window": 30,  # days
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
        
        # Assessment components
        self.assessment_history = []
        self.assessment_criteria = {}
        self.performance_cache = {}
        self.assessment_cache = {}
    
    async def initialize(self):
        """Initialize the assessment manager."""
        try:
            # Get database session using context manager
            db_gen = get_db()
            self.db = await anext(db_gen)
            
            # Initialize assessment criteria
            self.initialize_assessment_criteria()
            
            self.logger.info("Activity Assessment Manager initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing Activity Assessment Manager: {str(e)}")
            raise
    
    async def cleanup(self):
        """Cleanup the assessment manager."""
        try:
            # Clear all data
            self.assessment_history.clear()
            self.assessment_criteria.clear()
            self.performance_cache.clear()
            self.assessment_cache.clear()
            
            # Reset service references
            self.db = None
            
            self.logger.info("Activity Assessment Manager cleaned up successfully")
        except Exception as e:
            self.logger.error(f"Error cleaning up Activity Assessment Manager: {str(e)}")
            raise

    def initialize_assessment_criteria(self):
        """Initialize assessment criteria."""
        try:
            self.assessment_criteria = {
                "performance": {
                    "excellent": {
                        "threshold": 0.9,
                        "description": "Consistently exceeds expectations"
                    },
                    "good": {
                        "threshold": 0.7,
                        "description": "Meets expectations with good performance"
                    },
                    "average": {
                        "threshold": 0.5,
                        "description": "Meets basic expectations"
                    },
                    "needs_improvement": {
                        "threshold": 0.3,
                        "description": "Below expectations, needs improvement"
                    },
                    "poor": {
                        "threshold": 0.0,
                        "description": "Significantly below expectations"
                    }
                },
                "progress": {
                    "rapid": {
                        "threshold": 0.2,
                        "description": "Shows rapid improvement"
                    },
                    "steady": {
                        "threshold": 0.1,
                        "description": "Shows steady improvement"
                    },
                    "slow": {
                        "threshold": 0.05,
                        "description": "Shows slow improvement"
                    },
                    "no_progress": {
                        "threshold": 0.0,
                        "description": "Shows no significant improvement"
                    },
                    "declining": {
                        "threshold": -0.1,
                        "description": "Shows declining performance"
                    }
                }
            }
            
            self.logger.info("Assessment criteria initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing assessment criteria: {str(e)}")
            raise

    async def assess_activity(
        self,
        activity_id: str,
        student_id: str,
        force_assess: bool = False
    ) -> Dict[str, Any]:
        """Assess student performance in an activity."""
        try:
            if not self.settings["assessment_enabled"]:
                raise ValueError("Activity assessment is disabled")
            
            # Get performance data
            performance_data = await self._get_performance_data(
                activity_id, student_id
            )
            
            if (len(performance_data) < self.settings["min_data_points"] and
                not force_assess):
                return None
            
            # Calculate performance metrics
            performance_metrics = self._calculate_performance_metrics(
                performance_data
            )
            
            # Evaluate performance
            assessment = self._evaluate_performance(
                performance_metrics
            )
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                assessment, performance_metrics
            )
            
            # Create assessment result
            result = {
                "activity_id": activity_id,
                "student_id": student_id,
                "assessment": assessment,
                "metrics": performance_metrics,
                "recommendations": recommendations,
                "timestamp": datetime.now().isoformat()
            }
            
            # Update assessment history
            self._update_assessment_history(result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error assessing activity: {str(e)}")
            raise

    async def get_assessment_history(
        self,
        activity_id: Optional[str] = None,
        student_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get assessment history for an activity or student."""
        try:
            history = self.assessment_history
            
            if activity_id:
                history = [h for h in history if h["activity_id"] == activity_id]
            
            if student_id:
                history = [h for h in history if h["student_id"] == student_id]
            
            return history
            
        except Exception as e:
            self.logger.error(f"Error getting assessment history: {str(e)}")
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

    def _evaluate_performance(
        self,
        metrics: Dict[str, float]
    ) -> Dict[str, Any]:
        """Evaluate performance based on metrics."""
        try:
            # Evaluate performance level
            performance_level = None
            for level, criteria in self.assessment_criteria["performance"].items():
                if metrics["recent_average"] >= criteria["threshold"]:
                    performance_level = level
                    break
            
            # Evaluate progress
            progress_level = None
            for level, criteria in self.assessment_criteria["progress"].items():
                if metrics["improvement_rate"] >= criteria["threshold"]:
                    progress_level = level
                    break
            
            return {
                "performance_level": performance_level,
                "progress_level": progress_level,
                "performance_description": self.assessment_criteria["performance"][performance_level]["description"],
                "progress_description": self.assessment_criteria["progress"][progress_level]["description"]
            }
            
        except Exception as e:
            self.logger.error(f"Error evaluating performance: {str(e)}")
            raise

    def _generate_recommendations(
        self,
        assessment: Dict[str, Any],
        metrics: Dict[str, float]
    ) -> List[str]:
        """Generate recommendations based on assessment."""
        try:
            recommendations = []
            
            # Performance-based recommendations
            if assessment["performance_level"] in ["poor", "needs_improvement"]:
                recommendations.append("Consider reducing activity difficulty")
                recommendations.append("Focus on fundamental skills")
            elif assessment["performance_level"] in ["excellent", "good"]:
                recommendations.append("Consider increasing activity difficulty")
                recommendations.append("Introduce advanced techniques")
            
            # Progress-based recommendations
            if assessment["progress_level"] in ["declining", "no_progress"]:
                recommendations.append("Review current approach and identify barriers")
                recommendations.append("Consider alternative teaching methods")
            elif assessment["progress_level"] in ["rapid", "steady"]:
                recommendations.append("Maintain current approach")
                recommendations.append("Set new challenging goals")
            
            # Volatility-based recommendations
            if metrics["volatility"] > 0.2:
                recommendations.append("Focus on consistency in performance")
                recommendations.append("Identify factors affecting performance variation")
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {str(e)}")
            raise

    def _update_assessment_history(
        self,
        assessment_result: Dict[str, Any]
    ) -> None:
        """Update assessment history."""
        try:
            self.assessment_history.append(assessment_result)
            
        except Exception as e:
            self.logger.error(f"Error updating assessment history: {str(e)}")
            raise 