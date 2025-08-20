"""
Schools Module

This module provides models for managing multi-school district structure.
"""

from .models import (
    School,
    SchoolFacility,
    SchoolType,
    SchoolStatus
)

from .relationships import (
    TeacherSchoolAssignment,
    StudentSchoolEnrollment,
    ClassSchoolAssignment,
    SchoolAcademicYear,
    AssignmentStatus
)

__all__ = [
    'School',
    'SchoolFacility',
    'SchoolType',
    'SchoolStatus',
    'TeacherSchoolAssignment',
    'StudentSchoolEnrollment',
    'ClassSchoolAssignment',
    'SchoolAcademicYear',
    'AssignmentStatus'
] 