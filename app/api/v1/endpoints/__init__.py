from .ai_analysis import router as ai_analysis_router
from .lesson_plans import router as lesson_plans_router
from .memory import router as memory_router
from .math_assistant import router as math_assistant_router
from .science_assistant import router as science_assistant_router

__all__ = [
    'ai_analysis_router',
    'lesson_plans_router',
    'memory_router',
    'math_assistant_router',
    'science_assistant_router'
] 