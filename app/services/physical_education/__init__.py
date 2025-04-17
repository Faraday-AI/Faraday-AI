"""
Physical Education Services module.

This module provides all service classes for physical education functionality.
"""

# First, import base models
from .models import (
    Activity,
    Exercise,
    RiskAssessment,
    SafetyIncident,
    SafetyCheck,
    EquipmentCheck,
    EnvironmentalCheck,
    Class,
    Student
)

# Then import core services that don't depend on other services
from .pe_service import PEService
from .security_service import SecurityService
from .equipment_manager import EquipmentManager
from .student_manager import StudentManager

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

# Import safety-related managers
from .safety_incident_manager import SafetyIncidentManager
from .safety_manager import SafetyManager
from .safety_report_generator import SafetyReportGenerator
from .risk_assessment_manager import RiskAssessmentManager

# Import planning and analysis services
from .lesson_planner import LessonPlanner

# Import video and movement analysis last since they depend on other modules
from .video_processor import VideoProcessor
from .movement_analyzer import MovementAnalyzer

__all__ = [
    'Activity',
    'Exercise',
    'RiskAssessment',
    'SafetyIncident',
    'SafetyCheck',
    'EquipmentCheck',
    'EnvironmentalCheck',
    'Class',
    'Student',
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
    'SafetyIncidentManager',
    'SafetyManager',
    'SafetyReportGenerator',
    'SecurityService',
    'StudentManager',
    'VideoProcessor',
    'LessonPlanner',
    'MovementAnalyzer',
    'PEService',
    'RiskAssessmentManager',
    'EquipmentManager'
] 