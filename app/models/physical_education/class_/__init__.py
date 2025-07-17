"""
Class Models

This module exports class-related models.
"""

from app.models.physical_education.class_.models import (
    ClassStudent,
    PhysicalEducationClass,
    ClassRoutine,
    ClassCreate,
    ClassUpdate,
    ClassResponse
)

# Ensure models are registered in the correct order
__all__ = [
    'ClassStudent',
    'PhysicalEducationClass',
    'ClassRoutine',
    'ClassCreate',
    'ClassUpdate',
    'ClassResponse'
] 