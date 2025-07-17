"""Assessment system for physical education."""


import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from app.core.monitoring import track_metrics
from app.services.physical_education import service_integration
from collections import deque
import asyncio
from dataclasses import dataclass
from enum import Enum
from sqlalchemy.orm import Session
from app.core.database import get_db

# Import models
from app.models.assessment import (
    SkillAssessment,
    AssessmentCriteria,
    AssessmentResult,
    AssessmentHistory,
    SkillProgress
)
from app.models.activity import Activity
from app.models.student import Student
from app.models.physical_education.pe_enums.pe_types import (
    AssessmentType,
    AssessmentStatus,
    SkillLevel,
    ProgressionLevel
)

class AssessmentState(Enum):
    INITIALIZING = "initializing"
    READY = "ready"
    ASSESSING = "assessing"
    COMPLETED = "completed"
    ERROR = "error"

@dataclass
class RealTimeMetrics:
    current_score: float
    trend: str
    confidence: float
    recommendations: List[str]
    warnings: List[str]
    last_update: datetime

class AssessmentSystem:
    """Service for managing skill assessments and progress tracking."""
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(AssessmentSystem, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.logger = logging.getLogger("assessment_system")
        self.db = None
        self.movement_analyzer = None
        self.activity_manager = None
        
        # Enhanced assessment settings
        self.settings = {
            "skill_levels": ["beginner", "intermediate", "advanced"],
            "assessment_categories": [
                "technique",
                "performance",
                "safety",
                "consistency",
                "improvement",
                "adaptability",
                "endurance",
                "coordination"
            ],
            "feedback_templates": {
                "positive": [
                    "Great job on {skill}! Your {aspect} is excellent.",
                    "Excellent {skill} technique! Keep focusing on {aspect}.",
                    "Impressive improvement in {skill}! Your {aspect} has improved significantly."
                ],
                "constructive": [
                    "Try to focus on {aspect} during {skill}. Here's how: {recommendation}",
                    "Consider working on {aspect} for better {skill}. Try this: {exercise}",
                    "To improve {skill}, pay attention to {aspect}. Practice this: {drill}"
                ],
                "safety": [
                    "Remember to maintain proper form during {skill}. Watch your {aspect}.",
                    "Be mindful of {safety_concern} when performing {skill}. Try this adjustment: {modification}",
                    "Safety first! Watch out for {safety_concern}. Here's a safer alternative: {alternative}"
                ],
                "progression": [
                    "You're ready to move to the next level in {skill}! Try this: {next_step}",
                    "Great progress! Let's challenge you with: {challenge}",
                    "You've mastered the basics of {skill}. Time to try: {advanced_variation}"
                ]
            },
            "age_groups": {
                "elementary": (5, 10),
                "middle": (11, 14),
                "high": (15, 18)
            },
            "scoring_weights": {
                "technique": 0.3,
                "performance": 0.25,
                "safety": 0.2,
                "consistency": 0.1,
                "improvement": 0.1,
                "adaptability": 0.05
            }
        }
        
        # Enhanced student data structure
        self.student_data = {
            "profiles": {},
            "assessments": {},
            "progress": {},
            "goals": {},
            "milestones": {},
            "achievements": {},
            "peer_comparisons": {}
        }
        
        # Enhanced performance benchmarks
        self.benchmarks = {
            "elementary": {
                "technique": {
                    "beginner": 0.5,
                    "intermediate": 0.65,
                    "advanced": 0.8
                },
                "performance": {
                    "beginner": 0.4,
                    "intermediate": 0.6,
                    "advanced": 0.75
                },
                "safety": {
                    "beginner": 0.6,
                    "intermediate": 0.75,
                    "advanced": 0.9
                }
            },
            "middle": {
                "technique": {
                    "beginner": 0.6,
                    "intermediate": 0.75,
                    "advanced": 0.9
                },
                "performance": {
                    "beginner": 0.5,
                    "intermediate": 0.7,
                    "advanced": 0.85
                },
                "safety": {
                    "beginner": 0.7,
                    "intermediate": 0.85,
                    "advanced": 0.95
                }
            },
            "high": {
                "technique": {
                    "beginner": 0.7,
                    "intermediate": 0.85,
                    "advanced": 0.95
                },
                "performance": {
                    "beginner": 0.6,
                    "intermediate": 0.8,
                    "advanced": 0.9
                },
                "safety": {
                    "beginner": 0.8,
                    "intermediate": 0.9,
                    "advanced": 0.98
                }
            }
        }
        
        # Enhanced assessment history
        self.assessment_history = {
            "recent_assessments": [],
            "trends": {},
            "statistics": {},
            "milestones": {},
            "achievements": {},
            "peer_comparisons": {}
        }

        # Real-time assessment settings
        self.real_time_settings = {
            "update_interval": 0.5,  # seconds
            "buffer_size": 30,  # frames
            "confidence_threshold": 0.7,
            "trend_window": 10,  # frames
            "warning_thresholds": {
                "safety": 0.6,
                "performance": 0.5,
                "technique": 0.5
            }
        }
        
        # Real-time assessment state
        self.assessment_state = AssessmentState.INITIALIZING
        self.real_time_metrics = {}
        self.assessment_buffer = {}
        self.trend_analysis = {}
        
        # Enhanced analytics settings
        self.analytics_settings = {
            "prediction_window": 7,  # days
            "trend_analysis_window": 30,  # days
            "performance_thresholds": {
                "improvement": 0.1,
                "decline": -0.1,
                "plateau": 0.02
            },
            "correlation_threshold": 0.7
        }
        
        # Analytics data structures
        self.performance_trends = {}
        self.skill_correlations = {}
        self.prediction_models = {}

        # Assessment components
        self.assessment_history = []
        self.skill_benchmarks = {}
        self.progress_tracking = {}
        self.feedback_history = {}
        
        # Assessment metrics
        self.performance_metrics = {}
        self.skill_metrics = {}
        self.progress_metrics = {}
        self.adaptation_metrics = {}
        
        # Caching and optimization
        self.assessment_cache = {}
        self.batch_cache = {}

    async def initialize(self):
        """Initialize the assessment system."""
        try:
            self.db = next(get_db())
            self.movement_analyzer = service_integration.get_service('movement_analyzer')
            self.activity_manager = service_integration.get_service('activity_manager')
            
            # Load assessment templates
            self.load_assessment_templates()
            
            # Initialize student data storage
            self.initialize_student_data()
            
            # Initialize real-time assessment
            self.initialize_real_time_assessment()
            
            # Initialize analytics
            self.initialize_analytics()
            
            # Load skill benchmarks
            await self.load_skill_benchmarks()
            
            self.assessment_state = AssessmentState.READY
            self.logger.info("Assessment system initialized successfully")
        except Exception as e:
            self.assessment_state = AssessmentState.ERROR
            self.logger.error(f"Error initializing assessment system: {str(e)}")
            raise

    async def cleanup(self):
        """Cleanup assessment system resources."""
        try:
            self.db = None
            self.movement_analyzer = None
            self.activity_manager = None
            
            # Save student data
            self.save_student_data()
            
            # Clear all data
            self.assessment_history.clear()
            self.skill_benchmarks.clear()
            self.progress_tracking.clear()
            self.feedback_history.clear()
            self.performance_metrics.clear()
            self.skill_metrics.clear()
            self.progress_metrics.clear()
            self.adaptation_metrics.clear()
            self.assessment_cache.clear()
            self.batch_cache.clear()
            
            self.logger.info("Assessment system cleaned up successfully")
        except Exception as e:
            self.logger.error(f"Error cleaning up assessment system: {str(e)}")
            raise

    def load_assessment_templates(self):
        """Load assessment templates and criteria."""
        try:
            # Load skill-specific assessment criteria
            self.assessment_criteria = {
                "running": {
                    "technique": ["posture", "stride", "arm movement"],
                    "performance": ["speed", "endurance", "efficiency"],
                    "safety": ["form", "surface", "pace"]
                },
                "jumping": {
                    "technique": ["takeoff", "flight", "landing"],
                    "performance": ["height", "distance", "control"],
                    "safety": ["landing", "surface", "warmup"]
                },
                "throwing": {
                    "technique": ["grip", "stance", "follow-through"],
                    "performance": ["accuracy", "distance", "power"],
                    "safety": ["form", "environment", "equipment"]
                }
            }
            
            self.logger.info("Assessment templates loaded successfully")
        except Exception as e:
            self.logger.error(f"Error loading assessment templates: {str(e)}")
            raise

    def initialize_student_data(self):
        """Initialize student data storage."""
        try:
            # Create data structure for each student
            self.student_data = {
                "profiles": {},
                "assessments": {},
                "progress": {},
                "goals": {},
                "milestones": {},
                "achievements": {},
                "peer_comparisons": {}
            }
            
            self.logger.info("Student data storage initialized")
        except Exception as e:
            self.logger.error(f"Error initializing student data: {str(e)}")
            raise

    def initialize_real_time_assessment(self):
        """Initialize real-time assessment components."""
        try:
            # Initialize assessment buffers
            for skill in self.assessment_criteria.keys():
                self.assessment_buffer[skill] = deque(maxlen=self.real_time_settings["buffer_size"])
                self.trend_analysis[skill] = {
                    "scores": deque(maxlen=self.real_time_settings["trend_window"]),
                    "trend": "stable",
                    "confidence": 0.0
                }
            
            self.logger.info("Real-time assessment initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing real-time assessment: {str(e)}")
            raise

    def initialize_analytics(self):
        """Initialize analytics components."""
        try:
            # Initialize performance trends
            for skill in self.assessment_criteria.keys():
                self.performance_trends[skill] = {
                    "daily_scores": [],
                    "weekly_averages": [],
                    "monthly_trends": [],
                    "predictions": []
                }
            
            # Initialize skill correlations
            self.skill_correlations = {
                skill: {other_skill: 0.0 for other_skill in self.assessment_criteria.keys()}
                for skill in self.assessment_criteria.keys()
            }
            
            self.logger.info("Analytics system initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing analytics: {str(e)}")
            raise

    @track_metrics
    async def start_real_time_assessment(
        self,
        student_id: str,
        skill: str,
        video_stream: Any
    ) -> Dict[str, Any]:
        """Start real-time assessment of a student's performance."""
        try:
            if self.assessment_state != AssessmentState.READY:
                raise RuntimeError("Assessment system not ready")
            
            self.assessment_state = AssessmentState.ASSESSING
            self.real_time_metrics[student_id] = {
                skill: RealTimeMetrics(
                    current_score=0.0,
                    trend="stable",
                    confidence=0.0,
                    recommendations=[],
                    warnings=[],
                    last_update=datetime.now()
                )
            }
            
            # Start assessment loop
            asyncio.create_task(self._assessment_loop(student_id, skill, video_stream))
            
            return {
                "status": "started",
                "student_id": student_id,
                "skill": skill,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            self.assessment_state = AssessmentState.ERROR
            self.logger.error(f"Error starting real-time assessment: {str(e)}")
            raise

    async def _assessment_loop(
        self,
        student_id: str,
        skill: str,
        video_stream: Any
    ):
        """Main assessment loop for real-time processing."""
        try:
            while self.assessment_state == AssessmentState.ASSESSING:
                # Process frame
                frame = await self._get_next_frame(video_stream)
                if frame is None:
                    break
                
                # Analyze movement
                analysis_results = await self.movement_analyzer.analyze_movement(frame)
                
                # Update buffer
                self.assessment_buffer[skill].append(analysis_results)
                
                # Calculate real-time metrics
                metrics = await self._calculate_real_time_metrics(student_id, skill)
                
                # Update real-time metrics
                self.real_time_metrics[student_id][skill] = metrics
                
                # Generate recommendations and warnings
                await self._update_recommendations(student_id, skill)
                
                # Update analytics
                await self._update_analytics(student_id, skill, metrics)
                
                await asyncio.sleep(self.real_time_settings["update_interval"])
        except Exception as e:
            self.assessment_state = AssessmentState.ERROR
            self.logger.error(f"Error in assessment loop: {str(e)}")
            raise

    async def _calculate_real_time_metrics(
        self,
        student_id: str,
        skill: str
    ) -> RealTimeMetrics:
        """Calculate real-time metrics from buffered data."""
        try:
            buffer_data = list(self.assessment_buffer[skill])
            if not buffer_data:
                return RealTimeMetrics(0.0, "stable", 0.0, [], [], datetime.now())
            
            # Calculate current score
            current_score = np.mean([data["score"] for data in buffer_data])
            
            # Calculate trend
            trend = self._calculate_trend(skill)
            
            # Calculate confidence
            confidence = self._calculate_confidence(buffer_data)
            
            return RealTimeMetrics(
                current_score=current_score,
                trend=trend,
                confidence=confidence,
                recommendations=[],
                warnings=[],
                last_update=datetime.now()
            )
        except Exception as e:
            self.logger.error(f"Error calculating real-time metrics: {str(e)}")
            raise

    def _calculate_trend(self, skill: str) -> str:
        """Calculate performance trend from recent data."""
        try:
            scores = list(self.trend_analysis[skill]["scores"])
            if len(scores) < 2:
                return "stable"
            
            # Calculate trend
            recent_scores = scores[-self.real_time_settings["trend_window"]:]
            if len(recent_scores) < 2:
                return "stable"
            
            # Calculate slope
            x = np.arange(len(recent_scores))
            slope = np.polyfit(x, recent_scores, 1)[0]
            
            if slope > 0.1:
                return "improving"
            elif slope < -0.1:
                return "declining"
            else:
                return "stable"
        except Exception as e:
            self.logger.error(f"Error calculating trend: {str(e)}")
            return "stable"

    def _calculate_confidence(self, buffer_data: List[Dict[str, Any]]) -> float:
        """Calculate confidence in the assessment."""
        try:
            if not buffer_data:
                return 0.0
            
            # Calculate variance in scores
            scores = [data["score"] for data in buffer_data]
            variance = np.var(scores)
            
            # Calculate confidence based on variance
            confidence = 1.0 - min(variance, 1.0)
            
            return max(0.0, min(1.0, confidence))
        except Exception as e:
            self.logger.error(f"Error calculating confidence: {str(e)}")
            return 0.0

    async def _update_recommendations(
        self,
        student_id: str,
        skill: str
    ):
        """Update recommendations and warnings based on current performance."""
        try:
            metrics = self.real_time_metrics[student_id][skill]
            
            # Clear previous recommendations and warnings
            metrics.recommendations = []
            metrics.warnings = []
            
            # Check for safety concerns
            if metrics.current_score < self.real_time_settings["warning_thresholds"]["safety"]:
                metrics.warnings.append("Safety concern detected. Please review form.")
            
            # Check for performance issues
            if metrics.current_score < self.real_time_settings["warning_thresholds"]["performance"]:
                metrics.warnings.append("Performance below expected level. Consider adjustments.")
            
            # Generate recommendations based on trend
            if metrics.trend == "declining":
                metrics.recommendations.append("Performance is declining. Consider taking a break.")
            elif metrics.trend == "improving":
                metrics.recommendations.append("Good progress! Keep up the good work.")
            
            # Update last update time
            metrics.last_update = datetime.now()
        except Exception as e:
            self.logger.error(f"Error updating recommendations: {str(e)}")
            raise

    async def _update_analytics(
        self,
        student_id: str,
        skill: str,
        metrics: RealTimeMetrics
    ):
        """Update analytics data with new metrics."""
        try:
            # Update performance trends
            self.performance_trends[skill]["daily_scores"].append({
                "timestamp": datetime.now(),
                "score": metrics.current_score,
                "confidence": metrics.confidence
            })
            
            # Update weekly averages
            if len(self.performance_trends[skill]["daily_scores"]) >= 7:
                weekly_scores = self.performance_trends[skill]["daily_scores"][-7:]
                weekly_avg = np.mean([score["score"] for score in weekly_scores])
                self.performance_trends[skill]["weekly_averages"].append({
                    "timestamp": datetime.now(),
                    "score": weekly_avg
                })
            
            # Update skill correlations
            for other_skill in self.assessment_criteria.keys():
                if other_skill != skill:
                    correlation = self._calculate_skill_correlation(skill, other_skill)
                    self.skill_correlations[skill][other_skill] = correlation
            
            # Update predictions
            self._update_predictions(skill)
        except Exception as e:
            self.logger.error(f"Error updating analytics: {str(e)}")
            raise

    def _calculate_skill_correlation(self, skill1: str, skill2: str) -> float:
        """Calculate correlation between two skills."""
        try:
            scores1 = [score["score"] for score in self.performance_trends[skill1]["daily_scores"]]
            scores2 = [score["score"] for score in self.performance_trends[skill2]["daily_scores"]]
            
            if len(scores1) < 2 or len(scores2) < 2:
                return 0.0
            
            # Calculate correlation
            correlation = np.corrcoef(scores1, scores2)[0, 1]
            
            return max(-1.0, min(1.0, correlation))
        except Exception as e:
            self.logger.error(f"Error calculating skill correlation: {str(e)}")
            return 0.0

    def _update_predictions(self, skill: str):
        """Update performance predictions for a skill."""
        try:
            scores = [score["score"] for score in self.performance_trends[skill]["daily_scores"]]
            if len(scores) < 7:
                return
            
            # Calculate moving average
            window = min(7, len(scores))
            moving_avg = np.convolve(scores, np.ones(window)/window, mode='valid')
            
            # Calculate trend
            x = np.arange(len(moving_avg))
            slope, intercept = np.polyfit(x, moving_avg, 1)
            
            # Generate predictions
            predictions = []
            for i in range(1, self.analytics_settings["prediction_window"] + 1):
                prediction = slope * (len(moving_avg) + i) + intercept
                predictions.append({
                    "days_ahead": i,
                    "predicted_score": max(0.0, min(1.0, prediction))
                })
            
            self.performance_trends[skill]["predictions"] = predictions
        except Exception as e:
            self.logger.error(f"Error updating predictions: {str(e)}")
            raise

    async def stop_real_time_assessment(
        self,
        student_id: str,
        skill: str
    ) -> Dict[str, Any]:
        """Stop real-time assessment and generate final report."""
        try:
            if self.assessment_state != AssessmentState.ASSESSING:
                raise RuntimeError("No active assessment")
            
            # Generate final report
            final_report = await self._generate_final_report(student_id, skill)
            
            # Reset assessment state
            self.assessment_state = AssessmentState.READY
            self.assessment_buffer[skill].clear()
            
            return final_report
        except Exception as e:
            self.assessment_state = AssessmentState.ERROR
            self.logger.error(f"Error stopping real-time assessment: {str(e)}")
            raise

    async def _generate_final_report(
        self,
        student_id: str,
        skill: str
    ) -> Dict[str, Any]:
        """Generate final assessment report."""
        try:
            metrics = self.real_time_metrics[student_id][skill]
            
            # Calculate overall performance
            buffer_data = list(self.assessment_buffer[skill])
            overall_score = np.mean([data["score"] for data in buffer_data])
            
            # Generate recommendations
            recommendations = self._generate_comprehensive_recommendations(
                skill,
                metrics,
                buffer_data
            )
            
            # Generate analytics summary
            analytics_summary = self._generate_analytics_summary(skill)
            
            return {
                "student_id": student_id,
                "skill": skill,
                "overall_score": overall_score,
                "performance_trend": metrics.trend,
                "confidence": metrics.confidence,
                "recommendations": recommendations,
                "analytics_summary": analytics_summary,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error generating final report: {str(e)}")
            raise

    def _generate_comprehensive_recommendations(
        self,
        skill: str,
        metrics: RealTimeMetrics,
        buffer_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate comprehensive recommendations based on assessment data."""
        try:
            recommendations = []
            
            # Add real-time recommendations
            recommendations.extend([
                {"type": "real_time", "text": rec}
                for rec in metrics.recommendations
            ])
            
            # Add warnings
            recommendations.extend([
                {"type": "warning", "text": warn}
                for warn in metrics.warnings
            ])
            
            # Add trend-based recommendations
            if metrics.trend == "declining":
                recommendations.append({
                    "type": "trend",
                    "text": "Consider reviewing technique and taking appropriate rest periods."
                })
            elif metrics.trend == "improving":
                recommendations.append({
                    "type": "trend",
                    "text": "Continue current training regimen with gradual progression."
                })
            
            # Add analytics-based recommendations
            analytics_recs = self._generate_analytics_recommendations(skill)
            recommendations.extend(analytics_recs)
            
            return recommendations
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {str(e)}")
            return []

    def _generate_analytics_recommendations(self, skill: str) -> List[Dict[str, Any]]:
        """Generate recommendations based on analytics data."""
        try:
            recommendations = []
            
            # Check skill correlations
            for other_skill, correlation in self.skill_correlations[skill].items():
                if correlation > self.analytics_settings["correlation_threshold"]:
                    recommendations.append({
                        "type": "correlation",
                        "text": f"Consider cross-training with {other_skill} to improve {skill}."
                    })
            
            # Check predictions
            predictions = self.performance_trends[skill]["predictions"]
            if predictions:
                last_prediction = predictions[-1]
                if last_prediction["predicted_score"] < 0.6:
                    recommendations.append({
                        "type": "prediction",
                        "text": "Consider additional training to meet performance goals."
                    })
            
            return recommendations
        except Exception as e:
            self.logger.error(f"Error generating analytics recommendations: {str(e)}")
            return []

    def _generate_analytics_summary(self, skill: str) -> Dict[str, Any]:
        """Generate summary of analytics data."""
        try:
            return {
                "performance_trend": self.performance_trends[skill],
                "skill_correlations": self.skill_correlations[skill],
                "predictions": self.performance_trends[skill]["predictions"]
            }
        except Exception as e:
            self.logger.error(f"Error generating analytics summary: {str(e)}")
            return {}

    @track_metrics
    async def assess_student(
        self,
        student_id: str,
        skill: str,
        video_data: Dict[str, Any],
        age_group: Optional[str] = None
    ) -> Dict[str, Any]:
        """Assess a student's performance in a specific skill with enhanced analysis."""
        try:
            # Validate student
            if student_id not in self.student_data["profiles"]:
                raise ValueError(f"Student {student_id} not found")
            
            # Determine age group if not provided
            if not age_group:
                age_group = self.determine_age_group(student_id)
            
            # Analyze movement with enhanced metrics
            analysis_results = await self.movement_analyzer.analyze(video_data)
            
            # Calculate enhanced scores
            scores = self.calculate_enhanced_scores(analysis_results, skill, age_group)
            
            # Generate comprehensive feedback
            feedback = self.generate_comprehensive_feedback(scores, skill, age_group)
            
            # Update student data with enhanced tracking
            self.update_enhanced_student_data(student_id, skill, scores, feedback, age_group)
            
            # Update assessment history with trends
            self.update_assessment_history(student_id, skill, scores)
            
            # Check for milestones and achievements
            milestones = self.check_milestones(student_id, skill, scores)
            achievements = self.check_achievements(student_id, skill, scores)
            
            # Generate peer comparison
            peer_comparison = self.generate_peer_comparison(student_id, skill, scores, age_group)
            
            return {
                "student_id": student_id,
                "skill": skill,
                "age_group": age_group,
                "scores": scores,
                "feedback": feedback,
                "milestones": milestones,
                "achievements": achievements,
                "peer_comparison": peer_comparison,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error assessing student {student_id}: {str(e)}")
            raise

    def calculate_enhanced_scores(
        self,
        analysis_results: Dict[str, Any],
        skill: str,
        age_group: str
    ) -> Dict[str, float]:
        """Calculate enhanced assessment scores with weighted metrics."""
        try:
            scores = {}
            
            # Calculate weighted scores for each category
            for category, weight in self.settings["scoring_weights"].items():
                if category == "technique":
                    scores[category] = self.calculate_technique_score(analysis_results, skill) * weight
                elif category == "performance":
                    scores[category] = self.calculate_performance_score(analysis_results, skill) * weight
                elif category == "safety":
                    scores[category] = self.calculate_safety_score(analysis_results, skill) * weight
                elif category == "consistency":
                    scores[category] = self.calculate_consistency_score(analysis_results, skill) * weight
                elif category == "improvement":
                    scores[category] = self.calculate_improvement_score(analysis_results, skill) * weight
                elif category == "adaptability":
                    scores[category] = self.calculate_adaptability_score(analysis_results, skill) * weight
            
            # Calculate overall score
            scores["overall"] = sum(scores.values())
            
            # Adjust scores based on age group benchmarks
            self.adjust_scores_by_age_group(scores, age_group)
            
            return scores
            
        except Exception as e:
            self.logger.error(f"Error calculating enhanced scores: {str(e)}")
            raise

    def calculate_technique_score(self, analysis_results: Dict[str, Any], skill: str) -> float:
        """Calculate technique score based on movement analysis."""
        try:
            # Get technique criteria for the skill
            criteria = self.assessment_criteria[skill]["technique"]
            
            # Calculate score for each criterion
            scores = []
            for criterion in criteria:
                if criterion in analysis_results["technique_analysis"]:
                    scores.append(analysis_results["technique_analysis"][criterion])
            
            # Return average score
            return np.mean(scores) if scores else 0.0
            
        except Exception as e:
            self.logger.error(f"Error calculating technique score: {str(e)}")
            return 0.0

    def calculate_performance_score(self, analysis_results: Dict[str, Any], skill: str) -> float:
        """Calculate performance score based on movement analysis."""
        try:
            # Get performance criteria for the skill
            criteria = self.assessment_criteria[skill]["performance"]
            
            # Calculate score for each criterion
            scores = []
            for criterion in criteria:
                if criterion in analysis_results["performance_metrics"]:
                    scores.append(analysis_results["performance_metrics"][criterion])
            
            # Return average score
            return np.mean(scores) if scores else 0.0
            
        except Exception as e:
            self.logger.error(f"Error calculating performance score: {str(e)}")
            return 0.0

    def calculate_safety_score(self, analysis_results: Dict[str, Any], skill: str) -> float:
        """Calculate safety score based on movement analysis."""
        try:
            # Get safety criteria for the skill
            criteria = self.assessment_criteria[skill]["safety"]
            
            # Calculate score for each criterion
            scores = []
            for criterion in criteria:
                if criterion in analysis_results["safety_analysis"]:
                    scores.append(analysis_results["safety_analysis"][criterion])
            
            # Return average score
            return np.mean(scores) if scores else 0.0
            
        except Exception as e:
            self.logger.error(f"Error calculating safety score: {str(e)}")
            return 0.0

    def calculate_consistency_score(self, analysis_results: Dict[str, Any], skill: str) -> float:
        """Calculate consistency score based on movement analysis."""
        try:
            # Get consistency metrics
            consistency_metrics = analysis_results.get("consistency_metrics", {})
            
            # Calculate score based on consistency metrics
            if consistency_metrics:
                return np.mean(list(consistency_metrics.values()))
            
            return 0.0
            
        except Exception as e:
            self.logger.error(f"Error calculating consistency score: {str(e)}")
            return 0.0

    def calculate_improvement_score(self, analysis_results: Dict[str, Any], skill: str) -> float:
        """Calculate improvement score based on movement analysis."""
        try:
            # Get improvement metrics
            improvement_metrics = analysis_results.get("improvement_metrics", {})
            
            # Calculate score based on improvement metrics
            if improvement_metrics:
                return np.mean(list(improvement_metrics.values()))
            
            return 0.0
            
        except Exception as e:
            self.logger.error(f"Error calculating improvement score: {str(e)}")
            return 0.0

    def calculate_adaptability_score(self, analysis_results: Dict[str, Any], skill: str) -> float:
        """Calculate adaptability score based on movement analysis."""
        try:
            # Get adaptability criteria
            criteria = self.assessment_criteria[skill].get("adaptability", [])
            
            if not criteria:
                return 0.0
            
            # Calculate score for each criterion
            scores = []
            for criterion in criteria:
                if criterion in analysis_results["adaptability_metrics"]:
                    scores.append(analysis_results["adaptability_metrics"][criterion])
            
            return np.mean(scores) if scores else 0.0
            
        except Exception as e:
            self.logger.error(f"Error calculating adaptability score: {str(e)}")
            return 0.0

    def adjust_scores_by_age_group(self, scores: Dict[str, float], age_group: str) -> None:
        """Adjust scores based on age group benchmarks."""
        try:
            benchmarks = self.benchmarks[age_group]
            
            for category in scores:
                if category in benchmarks:
                    level = self.determine_skill_level(scores[category])
                    benchmark = benchmarks[category][level]
                    scores[category] = min(scores[category] / benchmark, 1.0)
            
        except Exception as e:
            self.logger.error(f"Error adjusting scores by age group: {str(e)}")
            raise

    def generate_comprehensive_feedback(
        self,
        scores: Dict[str, float],
        skill: str,
        age_group: str
    ) -> Dict[str, str]:
        """Generate comprehensive feedback with specific recommendations."""
        try:
            feedback = {}
            
            # Generate feedback for each category
            for category, score in scores.items():
                if category == "overall":
                    continue
                    
                level = self.determine_skill_level(score)
                template_type = "positive" if score >= 0.8 else "constructive"
                
                # Get specific aspects to focus on
                aspects = self.get_focus_aspects(category, skill, score)
                
                # Generate recommendations
                recommendations = self.generate_recommendations(category, skill, score, age_group)
                
                # Generate feedback text
                feedback[category] = self.settings["feedback_templates"][template_type][0].format(
                    skill=skill,
                    aspect=aspects[0],
                    recommendation=recommendations[0] if recommendations else ""
                )
            
            # Add progression feedback if applicable
            if scores["overall"] >= 0.9:
                next_steps = self.get_next_steps(skill, age_group)
                feedback["progression"] = self.settings["feedback_templates"]["progression"][0].format(
                    skill=skill,
                    next_step=next_steps[0] if next_steps else ""
                )
            
            return feedback
            
        except Exception as e:
            self.logger.error(f"Error generating comprehensive feedback: {str(e)}")
            raise

    def get_focus_aspects(self, category: str, skill: str, score: float) -> List[str]:
        """Get specific aspects to focus on for improvement."""
        try:
            criteria = self.assessment_criteria[skill][category]
            return [criterion for criterion in criteria if score < 0.8]
            
        except Exception as e:
            self.logger.error(f"Error getting focus aspects: {str(e)}")
            return []

    def generate_recommendations(
        self,
        category: str,
        skill: str,
        score: float,
        age_group: str
    ) -> List[str]:
        """Generate specific recommendations for improvement."""
        try:
            recommendations = []
            
            # Get appropriate exercises based on category and skill level
            exercises = self.activity_manager.get_exercises_for_skill(
                skill=skill,
                category=category,
                difficulty=self.determine_skill_level(score),
                age_group=age_group
            )
            
            for exercise in exercises:
                recommendations.append(f"Practice {exercise['name']}: {exercise['description']}")
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {str(e)}")
            return []

    def get_next_steps(self, skill: str, age_group: str) -> List[str]:
        """Get next steps for skill progression."""
        try:
            next_steps = []
            
            # Get advanced variations of the skill
            variations = self.activity_manager.get_skill_variations(
                skill=skill,
                difficulty="advanced",
                age_group=age_group
            )
            
            for variation in variations:
                next_steps.append(f"Try {variation['name']}: {variation['description']}")
            
            return next_steps
            
        except Exception as e:
            self.logger.error(f"Error getting next steps: {str(e)}")
            return []

    def check_milestones(self, student_id: str, skill: str, scores: Dict[str, float]) -> List[Dict[str, Any]]:
        """Check for achieved milestones."""
        try:
            milestones = []
            
            # Check overall score milestone
            if scores["overall"] >= 0.9:
                milestones.append({
                    "type": "skill_mastery",
                    "skill": skill,
                    "score": scores["overall"],
                    "timestamp": datetime.now().isoformat()
                })
            
            # Check category milestones
            for category, score in scores.items():
                if category != "overall" and score >= 0.9:
                    milestones.append({
                        "type": f"{category}_mastery",
                        "skill": skill,
                        "category": category,
                        "score": score,
                        "timestamp": datetime.now().isoformat()
                    })
            
            return milestones
            
        except Exception as e:
            self.logger.error(f"Error checking milestones: {str(e)}")
            return []

    def check_achievements(self, student_id: str, skill: str, scores: Dict[str, float]) -> List[Dict[str, Any]]:
        """Check for achieved achievements."""
        try:
            achievements = []
            
            # Check for perfect scores
            if all(score >= 0.95 for score in scores.values() if score != "overall"):
                achievements.append({
                    "type": "perfect_performance",
                    "skill": skill,
                    "timestamp": datetime.now().isoformat()
                })
            
            # Check for rapid improvement
            if self.check_rapid_improvement(student_id, skill, scores):
                achievements.append({
                    "type": "rapid_improvement",
                    "skill": skill,
                    "timestamp": datetime.now().isoformat()
                })
            
            return achievements
            
        except Exception as e:
            self.logger.error(f"Error checking achievements: {str(e)}")
            return []

    def check_rapid_improvement(self, student_id: str, skill: str, current_scores: Dict[str, float]) -> bool:
        """Check if student has shown rapid improvement."""
        try:
            if student_id not in self.student_data["assessments"]:
                return False
            
            previous_assessments = [
                assessment for assessment in self.student_data["assessments"][student_id]
                if assessment["skill"] == skill
            ]
            
            if len(previous_assessments) < 2:
                return False
            
            # Get scores from last two assessments
            last_scores = previous_assessments[-1]["scores"]
            previous_scores = previous_assessments[-2]["scores"]
            
            # Calculate improvement
            improvement = {
                category: current_scores[category] - last_scores[category]
                for category in current_scores
                if category in last_scores
            }
            
            # Check if improvement is significant
            return all(imp >= 0.2 for imp in improvement.values())
            
        except Exception as e:
            self.logger.error(f"Error checking rapid improvement: {str(e)}")
            return False

    def generate_peer_comparison(
        self,
        student_id: str,
        skill: str,
        scores: Dict[str, float],
        age_group: str
    ) -> Dict[str, Any]:
        """Generate peer comparison metrics."""
        try:
            # Get all students in the same age group
            peers = [
                student for student in self.student_data["profiles"].values()
                if student.get("age_group") == age_group
            ]
            
            if not peers:
                return {}
            
            # Calculate peer statistics
            peer_scores = []
            for peer in peers:
                if peer["id"] in self.student_data["assessments"]:
                    peer_assessments = [
                        assessment for assessment in self.student_data["assessments"][peer["id"]]
                        if assessment["skill"] == skill
                    ]
                    if peer_assessments:
                        peer_scores.append(peer_assessments[-1]["scores"]["overall"])
            
            if not peer_scores:
                return {}
            
            # Calculate comparison metrics
            percentile = np.percentile(peer_scores, scores["overall"] * 100)
            
            return {
                "percentile": percentile,
                "average_peer_score": np.mean(peer_scores),
                "top_peer_score": max(peer_scores),
                "peer_count": len(peer_scores)
            }
            
        except Exception as e:
            self.logger.error(f"Error generating peer comparison: {str(e)}")
            return {}

    def update_student_data(self, student_id: str, skill: str, scores: Dict[str, float], feedback: Dict[str, str]):
        """Update student data with new assessment results."""
        try:
            # Update assessments
            if student_id not in self.student_data["assessments"]:
                self.student_data["assessments"][student_id] = {}
            
            self.student_data["assessments"][student_id][skill] = {
                "scores": scores,
                "feedback": feedback,
                "timestamp": datetime.now().isoformat()
            }
            
            # Update progress
            if student_id not in self.student_data["progress"]:
                self.student_data["progress"][student_id] = {}
            
            self.student_data["progress"][student_id][skill] = {
                "current_level": self.determine_skill_level(scores),
                "improvement": self.calculate_improvement(student_id, skill, scores),
                "last_assessment": datetime.now().isoformat()
            }
            
            self.logger.info(f"Student data updated for {student_id}")
        except Exception as e:
            self.logger.error(f"Error updating student data: {str(e)}")
            raise

    def determine_skill_level(self, scores: Dict[str, float]) -> str:
        """Determine skill level based on assessment scores."""
        try:
            # Calculate average score
            avg_score = np.mean(list(scores.values()))
            
            # Determine level
            if avg_score >= self.benchmarks["technique"]["advanced"]:
                return "advanced"
            elif avg_score >= self.benchmarks["technique"]["intermediate"]:
                return "intermediate"
            else:
                return "beginner"
                
        except Exception as e:
            self.logger.error(f"Error determining skill level: {str(e)}")
            return "beginner"

    def calculate_improvement(self, student_id: str, skill: str, current_scores: Dict[str, float]) -> Dict[str, float]:
        """Calculate improvement from previous assessment."""
        try:
            # Get previous assessment
            if student_id in self.student_data["assessments"] and skill in self.student_data["assessments"][student_id]:
                previous_scores = self.student_data["assessments"][student_id][skill]["scores"]
                
                # Calculate improvement for each category
                improvement = {}
                for category, current_score in current_scores.items():
                    if category in previous_scores:
                        improvement[category] = current_score - previous_scores[category]
                    else:
                        improvement[category] = 0.0
                
                return improvement
            
            return {category: 0.0 for category in current_scores.keys()}
            
        except Exception as e:
            self.logger.error(f"Error calculating improvement: {str(e)}")
            return {category: 0.0 for category in current_scores.keys()}

    def update_assessment_history(self, student_id: str, skill: str, scores: Dict[str, float]):
        """Update assessment history with new results."""
        try:
            # Add to recent assessments
            self.assessment_history["recent_assessments"].append({
                "student_id": student_id,
                "skill": skill,
                "scores": scores,
                "timestamp": datetime.now().isoformat()
            })
            
            # Keep only last 100 assessments
            if len(self.assessment_history["recent_assessments"]) > 100:
                self.assessment_history["recent_assessments"] = self.assessment_history["recent_assessments"][-100:]
            
            # Update trends
            if student_id not in self.assessment_history["trends"]:
                self.assessment_history["trends"][student_id] = {}
            
            if skill not in self.assessment_history["trends"][student_id]:
                self.assessment_history["trends"][student_id][skill] = []
            
            self.assessment_history["trends"][student_id][skill].append({
                "scores": scores,
                "timestamp": datetime.now().isoformat()
            })
            
            # Update statistics
            self.update_statistics(student_id, skill, scores)
            
        except Exception as e:
            self.logger.error(f"Error updating assessment history: {str(e)}")
            raise

    def update_statistics(self, student_id: str, skill: str, scores: Dict[str, float]):
        """Update assessment statistics."""
        try:
            if student_id not in self.assessment_history["statistics"]:
                self.assessment_history["statistics"][student_id] = {}
            
            if skill not in self.assessment_history["statistics"][student_id]:
                self.assessment_history["statistics"][student_id][skill] = {
                    "total_assessments": 0,
                    "average_scores": {},
                    "best_scores": {},
                    "improvement_rates": {}
                }
            
            stats = self.assessment_history["statistics"][student_id][skill]
            stats["total_assessments"] += 1
            
            # Update average scores
            for category, score in scores.items():
                if category not in stats["average_scores"]:
                    stats["average_scores"][category] = score
                else:
                    stats["average_scores"][category] = (
                        (stats["average_scores"][category] * (stats["total_assessments"] - 1) + score) /
                        stats["total_assessments"]
                    )
                
                # Update best scores
                if category not in stats["best_scores"] or score > stats["best_scores"][category]:
                    stats["best_scores"][category] = score
            
            # Calculate improvement rates
            if stats["total_assessments"] > 1:
                for category in scores.keys():
                    if category in stats["average_scores"]:
                        improvement = (scores[category] - stats["average_scores"][category]) / stats["total_assessments"]
                        stats["improvement_rates"][category] = improvement
            
        except Exception as e:
            self.logger.error(f"Error updating statistics: {str(e)}")
            raise

    def save_student_data(self):
        """Save student data to persistent storage."""
        try:
            # TODO: Implement data persistence
            self.logger.info("Student data saved successfully")
        except Exception as e:
            self.logger.error(f"Error saving student data: {str(e)}")
            raise

    async def load_skill_benchmarks(self):
        """Load skill benchmarks from persistent storage."""
        try:
            # TODO: Implement data loading
            self.logger.info("Skill benchmarks loaded successfully")
        except Exception as e:
            self.logger.error(f"Error loading skill benchmarks: {str(e)}")
            raise

    def determine_age_group(self, student_id: str) -> str:
        """Determine age group based on student data."""
        try:
            # TODO: Implement age group determination logic
            return "middle"  # Placeholder return
        except Exception as e:
            self.logger.error(f"Error determining age group: {str(e)}")
            return "middle"

    def update_enhanced_student_data(self, student_id: str, skill: str, scores: Dict[str, float], feedback: Dict[str, str], age_group: str):
        """Update student data with enhanced tracking."""
        try:
            # TODO: Implement enhanced student data update logic
            self.logger.info(f"Student data updated for {student_id}")
        except Exception as e:
            self.logger.error(f"Error updating enhanced student data: {str(e)}")
            raise

    def calculate_technique_score(self, analysis_results: Dict[str, Any], skill: str) -> float:
        """Calculate technique score based on movement analysis."""
        try:
            # Get technique criteria for the skill
            criteria = self.assessment_criteria[skill]["technique"]
            
            # Calculate score for each criterion
            scores = []
            for criterion in criteria:
                if criterion in analysis_results["technique_analysis"]:
                    scores.append(analysis_results["technique_analysis"][criterion])
            
            # Return average score
            return np.mean(scores) if scores else 0.0
            
        except Exception as e:
            self.logger.error(f"Error calculating technique score: {str(e)}")
            return 0.0

    def calculate_performance_score(self, analysis_results: Dict[str, Any], skill: str) -> float:
        """Calculate performance score based on movement analysis."""
        try:
            # Get performance criteria for the skill
            criteria = self.assessment_criteria[skill]["performance"]
            
            # Calculate score for each criterion
            scores = []
            for criterion in criteria:
                if criterion in analysis_results["performance_metrics"]:
                    scores.append(analysis_results["performance_metrics"][criterion])
            
            # Return average score
            return np.mean(scores) if scores else 0.0
            
        except Exception as e:
            self.logger.error(f"Error calculating performance score: {str(e)}")
            return 0.0

    def calculate_safety_score(self, analysis_results: Dict[str, Any], skill: str) -> float:
        """Calculate safety score based on movement analysis."""
        try:
            # Get safety criteria for the skill
            criteria = self.assessment_criteria[skill]["safety"]
            
            # Calculate score for each criterion
            scores = []
            for criterion in criteria:
                if criterion in analysis_results["safety_analysis"]:
                    scores.append(analysis_results["safety_analysis"][criterion])
            
            # Return average score
            return np.mean(scores) if scores else 0.0
            
        except Exception as e:
            self.logger.error(f"Error calculating safety score: {str(e)}")
            return 0.0

    def calculate_consistency_score(self, analysis_results: Dict[str, Any], skill: str) -> float:
        """Calculate consistency score based on movement analysis."""
        try:
            # Get consistency metrics
            consistency_metrics = analysis_results.get("consistency_metrics", {})
            
            # Calculate score based on consistency metrics
            if consistency_metrics:
                return np.mean(list(consistency_metrics.values()))
            
            return 0.0
            
        except Exception as e:
            self.logger.error(f"Error calculating consistency score: {str(e)}")
            return 0.0

    def calculate_improvement_score(self, analysis_results: Dict[str, Any], skill: str) -> float:
        """Calculate improvement score based on movement analysis."""
        try:
            # Get improvement metrics
            improvement_metrics = analysis_results.get("improvement_metrics", {})
            
            # Calculate score based on improvement metrics
            if improvement_metrics:
                return np.mean(list(improvement_metrics.values()))
            
            return 0.0
            
        except Exception as e:
            self.logger.error(f"Error calculating improvement score: {str(e)}")
            return 0.0

    def calculate_adaptability_score(self, analysis_results: Dict[str, Any], skill: str) -> float:
        """Calculate adaptability score based on movement analysis."""
        try:
            # Get adaptability criteria
            criteria = self.assessment_criteria[skill].get("adaptability", [])
            
            if not criteria:
                return 0.0
            
            # Calculate score for each criterion
            scores = []
            for criterion in criteria:
                if criterion in analysis_results["adaptability_metrics"]:
                    scores.append(analysis_results["adaptability_metrics"][criterion])
            
            return np.mean(scores) if scores else 0.0
            
        except Exception as e:
            self.logger.error(f"Error calculating adaptability score: {str(e)}")
            return 0.0

    def generate_comprehensive_feedback(self, scores: Dict[str, float], skill: str, age_group: str) -> Dict[str, str]:
        """Generate comprehensive feedback with specific recommendations."""
        try:
            feedback = {}
            
            # Generate feedback for each category
            for category, score in scores.items():
                if category == "overall":
                    continue
                    
                level = self.determine_skill_level(score)
                template_type = "positive" if score >= 0.8 else "constructive"
                
                # Get specific aspects to focus on
                aspects = self.get_focus_aspects(category, skill, score)
                
                # Generate recommendations
                recommendations = self.generate_recommendations(category, skill, score, age_group)
                
                # Generate feedback text
                feedback[category] = self.settings["feedback_templates"][template_type][0].format(
                    skill=skill,
                    aspect=aspects[0],
                    recommendation=recommendations[0] if recommendations else ""
                )
            
            # Add progression feedback if applicable
            if scores["overall"] >= 0.9:
                next_steps = self.get_next_steps(skill, age_group)
                feedback["progression"] = self.settings["feedback_templates"]["progression"][0].format(
                    skill=skill,
                    next_step=next_steps[0] if next_steps else ""
                )
            
            return feedback
            
        except Exception as e:
            self.logger.error(f"Error generating comprehensive feedback: {str(e)}")
            raise

    def get_focus_aspects(self, category: str, skill: str, score: float) -> List[str]:
        """Get specific aspects to focus on for improvement."""
        try:
            criteria = self.assessment_criteria[skill][category]
            return [criterion for criterion in criteria if score < 0.8]
            
        except Exception as e:
            self.logger.error(f"Error getting focus aspects: {str(e)}")
            return []

    def generate_recommendations(self, category: str, skill: str, score: float, age_group: str) -> List[str]:
        """Generate specific recommendations for improvement."""
        try:
            recommendations = []
            
            # Get appropriate exercises based on category and skill level
            exercises = self.activity_manager.get_exercises_for_skill(
                skill=skill,
                category=category,
                difficulty=self.determine_skill_level(score),
                age_group=age_group
            )
            
            for exercise in exercises:
                recommendations.append(f"Practice {exercise['name']}: {exercise['description']}")
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {str(e)}")
            return []

    def get_next_steps(self, skill: str, age_group: str) -> List[str]:
        """Get next steps for skill progression."""
        try:
            next_steps = []
            
            # Get advanced variations of the skill
            variations = self.activity_manager.get_skill_variations(
                skill=skill,
                difficulty="advanced",
                age_group=age_group
            )
            
            for variation in variations:
                next_steps.append(f"Try {variation['name']}: {variation['description']}")
            
            return next_steps
            
        except Exception as e:
            self.logger.error(f"Error getting next steps: {str(e)}")
            return []

    def check_milestones(self, student_id: str, skill: str, scores: Dict[str, float]) -> List[Dict[str, Any]]:
        """Check for achieved milestones."""
        try:
            milestones = []
            
            # Check overall score milestone
            if scores["overall"] >= 0.9:
                milestones.append({
                    "type": "skill_mastery",
                    "skill": skill,
                    "score": scores["overall"],
                    "timestamp": datetime.now().isoformat()
                })
            
            # Check category milestones
            for category, score in scores.items():
                if category != "overall" and score >= 0.9:
                    milestones.append({
                        "type": f"{category}_mastery",
                        "skill": skill,
                        "category": category,
                        "score": score,
                        "timestamp": datetime.now().isoformat()
                    })
            
            return milestones
            
        except Exception as e:
            self.logger.error(f"Error checking milestones: {str(e)}")
            return []

    def check_achievements(self, student_id: str, skill: str, scores: Dict[str, float]) -> List[Dict[str, Any]]:
        """Check for achieved achievements."""
        try:
            achievements = []
            
            # Check for perfect scores
            if all(score >= 0.95 for score in scores.values() if score != "overall"):
                achievements.append({
                    "type": "perfect_performance",
                    "skill": skill,
                    "timestamp": datetime.now().isoformat()
                })
            
            # Check for rapid improvement
            if self.check_rapid_improvement(student_id, skill, scores):
                achievements.append({
                    "type": "rapid_improvement",
                    "skill": skill,
                    "timestamp": datetime.now().isoformat()
                })
            
            return achievements
            
        except Exception as e:
            self.logger.error(f"Error checking achievements: {str(e)}")
            return []

    def check_rapid_improvement(self, student_id: str, skill: str, current_scores: Dict[str, float]) -> bool:
        """Check if student has shown rapid improvement."""
        try:
            if student_id not in self.student_data["assessments"]:
                return False
            
            previous_assessments = [
                assessment for assessment in self.student_data["assessments"][student_id]
                if assessment["skill"] == skill
            ]
            
            if len(previous_assessments) < 2:
                return False
            
            # Get scores from last two assessments
            last_scores = previous_assessments[-1]["scores"]
            previous_scores = previous_assessments[-2]["scores"]
            
            # Calculate improvement
            improvement = {
                category: current_scores[category] - last_scores[category]
                for category in current_scores
                if category in last_scores
            }
            
            # Check if improvement is significant
            return all(imp >= 0.2 for imp in improvement.values())
            
        except Exception as e:
            self.logger.error(f"Error checking rapid improvement: {str(e)}")
            return False

    def generate_peer_comparison(self, student_id: str, skill: str, scores: Dict[str, float], age_group: str) -> Dict[str, Any]:
        """Generate peer comparison metrics."""
        try:
            # Get all students in the same age group
            peers = [
                student for student in self.student_data["profiles"].values()
                if student.get("age_group") == age_group
            ]
            
            if not peers:
                return {}
            
            # Calculate peer statistics
            peer_scores = []
            for peer in peers:
                if peer["id"] in self.student_data["assessments"]:
                    peer_assessments = [
                        assessment for assessment in self.student_data["assessments"][peer["id"]]
                        if assessment["skill"] == skill
                    ]
                    if peer_assessments:
                        peer_scores.append(peer_assessments[-1]["scores"]["overall"])
            
            if not peer_scores:
                return {}
            
            # Calculate comparison metrics
            percentile = np.percentile(peer_scores, scores["overall"] * 100)
            
            return {
                "percentile": percentile,
                "average_peer_score": np.mean(peer_scores),
                "top_peer_score": max(peer_scores),
                "peer_count": len(peer_scores)
            }
            
        except Exception as e:
            self.logger.error(f"Error generating peer comparison: {str(e)}")
            return {}

    def update_enhanced_student_data(self, student_id: str, skill: str, scores: Dict[str, float], feedback: Dict[str, str], age_group: str):
        """Update student data with enhanced tracking."""
        try:
            # TODO: Implement enhanced student data update logic
            self.logger.info(f"Student data updated for {student_id}")
        except Exception as e:
            self.logger.error(f"Error updating enhanced student data: {str(e)}")
            raise

    def update_assessment_history(self, student_id: str, skill: str, scores: Dict[str, float]):
        """Update assessment history with new results."""
        try:
            # Add to recent assessments
            self.assessment_history["recent_assessments"].append({
                "student_id": student_id,
                "skill": skill,
                "scores": scores,
                "timestamp": datetime.now().isoformat()
            })
            
            # Keep only last 100 assessments
            if len(self.assessment_history["recent_assessments"]) > 100:
                self.assessment_history["recent_assessments"] = self.assessment_history["recent_assessments"][-100:]
            
            # Update trends
            if student_id not in self.assessment_history["trends"]:
                self.assessment_history["trends"][student_id] = {}
            
            if skill not in self.assessment_history["trends"][student_id]:
                self.assessment_history["trends"][student_id][skill] = []
            
            self.assessment_history["trends"][student_id][skill].append({
                "scores": scores,
                "timestamp": datetime.now().isoformat()
            })
            
            # Update statistics
            self.update_statistics(student_id, skill, scores)
            
        except Exception as e:
            self.logger.error(f"Error updating assessment history: {str(e)}")
            raise

    def update_statistics(self, student_id: str, skill: str, scores: Dict[str, float]):
        """Update assessment statistics."""
        try:
            if student_id not in self.assessment_history["statistics"]:
                self.assessment_history["statistics"][student_id] = {}
            
            if skill not in self.assessment_history["statistics"][student_id]:
                self.assessment_history["statistics"][student_id][skill] = {
                    "total_assessments": 0,
                    "average_scores": {},
                    "best_scores": {},
                    "improvement_rates": {}
                }
            
            stats = self.assessment_history["statistics"][student_id][skill]
            stats["total_assessments"] += 1
            
            # Update average scores
            for category, score in scores.items():
                if category not in stats["average_scores"]:
                    stats["average_scores"][category] = score
                else:
                    stats["average_scores"][category] = (
                        (stats["average_scores"][category] * (stats["total_assessments"] - 1) + score) /
                        stats["total_assessments"]
                    )
                
                # Update best scores
                if category not in stats["best_scores"] or score > stats["best_scores"][category]:
                    stats["best_scores"][category] = score
            
            # Calculate improvement rates
            if stats["total_assessments"] > 1:
                for category in scores.keys():
                    if category in stats["average_scores"]:
                        improvement = (scores[category] - stats["average_scores"][category]) / stats["total_assessments"]
                        stats["improvement_rates"][category] = improvement
            
        except Exception as e:
            self.logger.error(f"Error updating statistics: {str(e)}")
            raise

    def save_student_data(self):
        """Save student data to persistent storage."""
        try:
            # TODO: Implement data persistence
            self.logger.info("Student data saved successfully")
        except Exception as e:
            self.logger.error(f"Error saving student data: {str(e)}")
            raise 