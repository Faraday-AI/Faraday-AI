"""
Movement Analysis Module

This module provides models for analyzing and tracking movement patterns in physical education.
"""

from .models import (
    MovementAnalysis,
    MovementAnalysisCreate,
    MovementAnalysisUpdate,
    MovementAnalysisResponse,
    MovementPattern,
    MovementPatternCreate,
    MovementPatternUpdate,
    MovementPatternResponse,
    MovementFeedback,
    MovementFeedbackCreate,
    MovementFeedbackUpdate,
    MovementFeedbackResponse
)

# Import movement_models to ensure all classes are registered with SQLAlchemy
from . import movement_models
from .movement_models import MovementAnalysisRecord, MovementPattern as MovementPatternRecord

__all__ = [
    'MovementAnalysis',
    'MovementAnalysisCreate',
    'MovementAnalysisUpdate',
    'MovementAnalysisResponse',
    'MovementPattern',
    'MovementPatternCreate',
    'MovementPatternUpdate',
    'MovementPatternResponse',
    'MovementFeedback',
    'MovementFeedbackCreate',
    'MovementFeedbackUpdate',
    'MovementFeedbackResponse',
    'MovementAnalysisRecord',
    'MovementPatternRecord'
] 