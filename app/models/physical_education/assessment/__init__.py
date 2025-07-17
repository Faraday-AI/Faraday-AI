"""
Assessment Models Package

This package contains models related to student assessments.
"""

from app.models.physical_education.assessment.models import (
    Assessment,
    AssessmentCreate,
    AssessmentUpdate,
    AssessmentResponse,
    SkillAssessment,
    SkillAssessmentCreate,
    SkillAssessmentUpdate,
    SkillAssessmentResponse,
    FitnessAssessment,
    FitnessAssessmentCreate,
    FitnessAssessmentUpdate,
    FitnessAssessmentResponse,
    MovementAssessment,
    MovementAssessmentCreate,
    MovementAssessmentUpdate,
    MovementAssessmentResponse
)

__all__ = [
    'Assessment',
    'AssessmentCreate',
    'AssessmentUpdate',
    'AssessmentResponse',
    'SkillAssessment',
    'SkillAssessmentCreate',
    'SkillAssessmentUpdate',
    'SkillAssessmentResponse',
    'FitnessAssessment',
    'FitnessAssessmentCreate',
    'FitnessAssessmentUpdate',
    'FitnessAssessmentResponse',
    'MovementAssessment',
    'MovementAssessmentCreate',
    'MovementAssessmentUpdate',
    'MovementAssessmentResponse'
] 