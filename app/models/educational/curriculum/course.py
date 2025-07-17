"""
Course model for managing educational courses.

This module contains the Course model which is used to organize assignments,
message boards, and other educational content.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.physical_education.base.base_class import Base
from app.dashboard.models import DashboardUser

# Association table for course enrollments
course_enrollments = Table(
    'course_enrollments',
    Base.metadata,
    Column('course_id', Integer, ForeignKey('courses.id'), primary_key=True),
    Column('user_id', Integer, ForeignKey('dashboard_users.id'), primary_key=True),
    Column('role', String)  # student, teacher, ta
)

class Course(Base):
    """Course model for organizing educational content."""
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    code = Column(String, unique=True, index=True)
    description = Column(Text)
    created_by = Column(Integer, ForeignKey("dashboard_users.id"))
    is_active = Column(Boolean, default=True)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    creator = relationship("DashboardUser", foreign_keys=[created_by])
    participants = relationship("DashboardUser", secondary=course_enrollments, backref="enrolled_courses")
    assignments = relationship("Assignment", back_populates="course")
    message_boards = relationship("MessageBoard", back_populates="course") 