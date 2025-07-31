"""
Seed Data Module

This module provides functions to seed the database with initial data.
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
import random
from typing import List, Dict, Any

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from app.models.physical_education.activity.models import Activity
from app.models.physical_education.exercise.models import Exercise
from app.models.physical_education.routine.models import Routine
from app.models.physical_education.student.models import Student
from app.models.physical_education.class_.models import PhysicalEducationClass
from app.models.physical_education.safety.models import (
    SafetyIncident,
    RiskAssessment,
    SafetyCheck,
    EnvironmentalCheck,
    SafetyProtocol,
    SafetyAlert
)
from app.models.physical_education.pe_enums.pe_types import (
    RiskLevel,
    IncidentSeverity,
    IncidentType,
    AlertType,
    CheckType
)
from app.models.organization.base.organization_management import Department, Organization
from app.core.database import SessionLocal

from app.core.config import settings
from app.models.physical_education.movement_analysis.movement_models import (
    MovementAnalysisRecord, MovementPattern
)
from app.models.physical_education.skill_assessment.skill_assessment_models import (
    SkillAssessment
)
# from app.models.physical_education.progress.routine_performance_models import (
#     RoutinePerformance, PerformanceMetrics
# )  # Remove incorrect import

# Import seed functions
from .seed_activities import seed_activities
from .seed_students import seed_students
from .seed_classes import seed_classes
from .seed_class_students import seed_class_students
from .seed_exercises import seed_exercises
from .seed_routines import seed_routines
from .seed_routine_activities import seed_routine_activities
from .seed_movement_analysis import seed_movement_analysis
from .seed_movement_patterns import seed_movement_patterns
from .seed_activity_adaptations import seed_activity_adaptations
from .seed_adaptation_history import seed_adaptation_history
from .seed_skill_assessments import seed_skill_assessments
from .seed_skill_progress import seed_skill_progress
from .seed_routine_performance import seed_routine_performance
from .seed_performance_metrics import seed_performance_metrics
from .seed_safety_incidents import seed_safety_incidents
from .seed_risk_assessments import seed_risk_assessments
from .seed_activity_plans import seed_activity_plans

from .seed_database import seed_database

__all__ = [
    "seed_activities",
    "seed_students",
    "seed_classes",
    "seed_safety_incidents",
    "seed_activity_plans"
] 