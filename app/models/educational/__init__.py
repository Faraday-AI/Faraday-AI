"""
Educational models package.

This package contains models for managing educational content,
including curricula, classes, teachers, and related components.
"""

from app.models.educational.base.message import Message
from app.models.educational.base.message_board import MessageBoard, MessageBoardPost

from app.models.educational.curriculum import (
    Curriculum,
    LessonPlan,
    Course,
    SubjectCategory,
    Assignment,
    Grade,
    Rubric
)

from app.models.educational.classroom import (
    EducationalClass,
    EducationalClassStudent
)

from app.models.educational.staff.teacher import Teacher
from app.models.educational.instructor import Instructor

__all__ = [
    'Grade', 'Assignment', 'Rubric', 'Message', 'MessageBoard', 'MessageBoardPost', 
    'Curriculum', 'LessonPlan', 'Course', 'SubjectCategory',
    'EducationalClass', 'EducationalClassStudent', 'Teacher', 'Instructor'
]