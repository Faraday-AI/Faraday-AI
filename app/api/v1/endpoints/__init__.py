from .memory import router as memory_router
from .pe_health import router as pe_health_router
from .math_assistant import router as math_assistant_router
from .science_assistant import router as science_assistant_router

__all__ = [
    'memory_router',
    'pe_health_router',
    'math_assistant_router',
    'science_assistant_router'
] 