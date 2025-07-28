"""
Physical Education API endpoints.

This module exports all physical education-related routers.
"""

from .physical_education import router as pe_router
from .health_fitness import router as health_fitness_router
from .activity import router as activity_router
from .activity_recommendations import router as activity_recommendations_router
from .student import router as student_router
from .safety import router as safety_router
from .security import router as security_router

__all__ = [
    'pe_router',
    'health_fitness_router', 
    'activity_router',
    'activity_recommendations_router',
    'student_router',
    'safety_router',
    'security_router'
] 