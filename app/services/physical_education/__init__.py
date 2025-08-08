"""
Physical Education Services module.

This module provides all service classes for physical education functionality.
"""

import logging
from typing import Dict, Any, Optional
from app.core.database import get_db
from app.models.core.core_models import (
    Region,
    ServiceStatus,
    DeploymentStatus,
    FeatureFlagType,
    FeatureFlagStatus,
    ABTestType,
    ABTestStatus,
    AlertSeverity,
    AlertStatus,
    CircuitBreakerState
)
from sqlalchemy.orm import Session

# First, import base models
from app.models.physical_education.activity import Activity
from app.models.physical_education.exercise import Exercise
from app.models.physical_education.safety import (
    RiskAssessment,
    SafetyIncident,
    EquipmentCheck,
    EnvironmentalCheck,
    SafetyCheck,
    IncidentSeverity,
    IncidentType
)
from app.models.physical_education.class_ import PhysicalEducationClass
from app.models.physical_education.student import Student

# Import service integration
from .service_integration import service_integration

# Then import core services that don't depend on other services
from .pe_service import PEService
from .security_service import SecurityService
from .equipment_manager import EquipmentManager
from .student_manager import StudentManager
from .ai_assistant import AIAssistant

# Import activity-related managers
from .activity_manager import ActivityManager
from .activity_analysis_manager import ActivityAnalysisManager
from .activity_visualization_manager import ActivityVisualizationManager
from .activity_export_manager import ActivityExportManager
from .activity_collaboration_manager import ActivityCollaborationManager
from .activity_adaptation_manager import ActivityAdaptationManager
from .activity_assessment_manager import ActivityAssessmentManager
from .activity_security_manager import ActivitySecurityManager
from .activity_cache_manager import ActivityCacheManager
from .activity_rate_limit_manager import ActivityRateLimitManager
from .activity_circuit_breaker_manager import ActivityCircuitBreakerManager
from .activity_scheduling_manager import ActivitySchedulingManager
from .activity_validation_manager import ActivityValidationManager
from .activity_engagement_manager import ActivityEngagementManager
from .activity_analytics_manager import ActivityAnalyticsManager
from .activity_tracking_manager import ActivityTrackingManager
from .activity_planning_manager import ActivityPlanningManager
from .activity_recommendation_service import ActivityRecommendationService
from .recommendation_engine import RecommendationEngine
from .activity_service import ActivityService
from .safety_service import SafetyService
from .student_service import StudentService
from .class_service import ClassService
from .rate_limiter import RateLimiter
from .circuit_breaker import CircuitBreaker
from .cache_monitor import CacheMonitor
from .workout_planner import WorkoutPlanner
from .nutrition_planner import NutritionPlanner
from .fitness_goal_manager import FitnessGoalManager
from .health_fitness_service import HealthFitnessService
from .routine_service import RoutineService

# Import safety-related managers
from .safety_incident_manager import SafetyIncidentManager
from .safety_manager import SafetyManager
from .safety_report_generator import SafetyReportGenerator
from .risk_assessment_manager import RiskAssessmentManager

# Import planning and analysis services
from .lesson_planner import LessonPlanner
from .assessment_system import AssessmentSystem
from .notification_service import NotificationService
from .progress_service import ProgressService

# Import video and movement analysis last since they depend on other modules
from .video_processor import VideoProcessor
from .movement_analyzer import MovementAnalyzer

# Export all services for easy access
__all__ = [
    'service_integration',
    'PEService',
    'SecurityService',
    'EquipmentManager',
    'StudentManager',
    'AIAssistant',
    'ActivityManager',
    'ActivityAnalysisManager',
    'ActivityVisualizationManager',
    'ActivityExportManager',
    'ActivityCollaborationManager',
    'ActivityAdaptationManager',
    'ActivityAssessmentManager',
    'ActivitySecurityManager',
    'ActivityCacheManager',
    'ActivityRateLimitManager',
    'ActivityCircuitBreakerManager',
    'ActivitySchedulingManager',
    'ActivityValidationManager',
    'ActivityEngagementManager',
    'ActivityAnalyticsManager',
    'ActivityTrackingManager',
    'ActivityPlanningManager',
    'ActivityRecommendationService',
    'RecommendationEngine',
    'ActivityService',
    'SafetyService',
    'StudentService',
    'ClassService',
    'RateLimiter',
    'CircuitBreaker',
    'CacheMonitor',
    'WorkoutPlanner',
    'NutritionPlanner',
    'FitnessGoalManager',
    'HealthFitnessService',
    'RoutineService',
    'SafetyIncidentManager',
    'SafetyManager',
    'SafetyReportGenerator',
    'RiskAssessmentManager',
    'LessonPlanner',
    'AssessmentSystem',
    'NotificationService',
    'ProgressService',
    'VideoProcessor',
    'MovementAnalyzer'
] 