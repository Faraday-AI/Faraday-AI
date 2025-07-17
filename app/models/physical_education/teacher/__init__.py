"""
Teacher Models

This module exports teacher-related models.
"""

from app.models.physical_education.teacher.models import (
    PhysicalEducationTeacher,
    PhysicalEducationTeacherCreate,
    PhysicalEducationTeacherUpdate,
    PhysicalEducationTeacherResponse,
    TeacherCertificationBase,
    TeacherCertification,
    TeacherCertificationCreate,
    TeacherCertificationUpdate,
    TeacherCertificationResponse
)

__all__ = [
    'PhysicalEducationTeacher',
    'PhysicalEducationTeacherCreate',
    'PhysicalEducationTeacherUpdate',
    'PhysicalEducationTeacherResponse',
    'TeacherCertificationBase',
    'TeacherCertification',
    'TeacherCertificationCreate',
    'TeacherCertificationUpdate',
    'TeacherCertificationResponse'
] 