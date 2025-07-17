"""
Educational Models

This module exports all educational models.
"""

from app.models.educational.base import (
    Grade,
    Assignment,
    Rubric,
    Message,
    MessageBoard,
    MessageBoardPost
)

from app.models.educational.curriculum import (
    Curriculum,
    LessonPlan,
    Subject,
    Course,
    SubjectCategory
)

from app.models.educational.classroom import (
    EducationalClass,
    EducationalClassStudent
)

from app.models.educational.staff import (
    Teacher
)

from .instructor import Instructor, InstructorStatus

__all__ = [
    # Base models
    'Grade',
    'Assignment',
    'Rubric',
    'Message',
    'MessageBoard',
    'MessageBoardPost',
    
    # Curriculum models
    'Curriculum',
    'LessonPlan',
    'Subject',
    'Course',
    'SubjectCategory',
    
    # Classroom models
    'EducationalClass',
    'EducationalClassStudent',
    
    # Staff models
    'Teacher'
] 