from .activity import router as activity_router
from .management.ai_analysis import router as ai_analysis_router
from .core.lesson_plans import router as lesson_plans_router
from .physical_education.physical_education import router as pe_router

__all__ = [
    'activity_router',
    'ai_analysis_router',
    'lesson_plans_router',
    'pe_router'
] 