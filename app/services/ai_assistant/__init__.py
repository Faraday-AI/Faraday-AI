"""
AI Assistant System

This module provides AI-powered assistance for content generation,
optimization, and analysis in the physical education system.
"""

from .ai_assistant_service import AIAssistantService
from .content_generator import ContentGenerator
from .content_optimizer import ContentOptimizer
from .lesson_planner import LessonPlanner

__all__ = [
    "AIAssistantService",
    "ContentGenerator", 
    "ContentOptimizer",
    "LessonPlanner"
] 