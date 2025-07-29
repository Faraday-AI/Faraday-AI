"""Core endpoints package."""

from .memory import router as memory_router
from .lesson_plans import router as lesson_plans_router
from .collaboration import router as collaboration_router
from .visualization import router as visualization_router

__all__ = [
    'memory_router',
    'lesson_plans_router', 
    'collaboration_router',
    'visualization_router'
] 