"""
Curriculum Models

This module exports all curriculum-related models.

- Use the Subject Enum (in app.models.core.types) for standard, built-in subjects (e.g., Physical Education, Math).
- Use the SubjectCategory model (below) for user/admin-defined custom subjects.
"""

from app.models.educational.curriculum.curriculum import Curriculum
from app.models.educational.curriculum.lesson_plan import LessonPlan
from app.models.educational.curriculum.course import Course
from app.models.educational.curriculum.subject import SubjectCategory
from app.models.educational.base.assignment import Assignment
from app.models.educational.base.message_board import MessageBoard
from app.models.core.types import Subject

__all__ = [
    'Curriculum',
    'LessonPlan',
    'Course',
    'SubjectCategory',
    'Assignment',
    'MessageBoard',
    'Subject'
] 