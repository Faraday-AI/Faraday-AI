"""
Progress Models

This module exports progress-related models.
"""

from app.models.physical_education.progress.models import (
    Progress,
    ProgressBase,
    ProgressCreate,
    ProgressUpdate,
    ProgressResponse,
    ProgressGoal,
    ProgressGoalCreate,
    ProgressGoalUpdate,
    ProgressGoalResponse,
    PhysicalEducationProgressNote,
    ProgressNoteBase,
    ProgressNoteCreate,
    ProgressNoteUpdate,
    ProgressNoteResponse,
    ProgressMilestone,
    ProgressAssessment
)

# Create alias for backward compatibility
ProgressNote = PhysicalEducationProgressNote

__all__ = [
    'Progress',
    'ProgressBase',
    'ProgressCreate',
    'ProgressUpdate',
    'ProgressResponse',
    'ProgressGoal',
    'ProgressGoalCreate',
    'ProgressGoalUpdate',
    'ProgressGoalResponse',
    'PhysicalEducationProgressNote',
    'ProgressNoteBase',
    'ProgressNoteCreate',
    'ProgressNoteUpdate',
    'ProgressNoteResponse',
    'ProgressMilestone',
    'ProgressAssessment',
    'ProgressNote'  # Alias for PhysicalEducationProgressNote
] 