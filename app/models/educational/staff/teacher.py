"""Teacher models for physical education."""
from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy import Column, String, DateTime, JSON, ForeignKey, Boolean, Integer, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func

from app.models.core.base import BaseModel, NamedMixin, TimestampedMixin, StatusMixin, MetadataMixin

class Teacher(BaseModel, NamedMixin, TimestampedMixin, StatusMixin):
    """Model for physical education teachers."""
    __tablename__ = "educational_teachers"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    school = Column(String(255), nullable=True)
    department = Column(String(100), nullable=True)
    subjects = Column(JSONB, nullable=True)
    grade_levels = Column(JSONB, nullable=True)
    certifications = Column(JSONB, nullable=True)
    specialties = Column(JSONB, nullable=True)
    bio = Column(String, nullable=True)
    last_login = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("app.models.core.user.User", back_populates="teacher_profile", overlaps="user,teacher_profile")
    classes = relationship("app.models.educational.classroom.class_.EducationalClass", back_populates="instructor", overlaps="instructor,classes")
    lesson_plans = relationship("app.models.educational.curriculum.lesson_plan.LessonPlan", back_populates="teacher", cascade="all, delete-orphan", overlaps="teacher,lesson_plans", foreign_keys="[app.models.educational.curriculum.lesson_plan.LessonPlan.teacher_id]")
    availability = relationship("app.models.educational.staff.teacher.EducationalTeacherAvailability", back_populates="teacher", cascade="all, delete-orphan", overlaps="teacher,availability")
    certifications_list = relationship("app.models.educational.staff.teacher.TeacherCertification", back_populates="teacher", cascade="all, delete-orphan", overlaps="teacher,certifications_list")

    def __repr__(self):
        return f"<Teacher {self.first_name} {self.last_name}>"

class EducationalTeacherAvailability(BaseModel, TimestampedMixin):
    """Model for tracking teacher availability."""
    __tablename__ = "educational_teacher_availability"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("educational_teachers.id", ondelete="CASCADE"), nullable=False)
    day_of_week = Column(String, nullable=False)  # Monday, Tuesday, etc.
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    is_available = Column(Boolean, default=True)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    teacher = relationship("app.models.educational.staff.teacher.Teacher", back_populates="availability", overlaps="teacher,availability")

    def __repr__(self):
        return f"<EducationalTeacherAvailability {self.teacher_id} - {self.day_of_week}>"

class TeacherCertification(BaseModel, TimestampedMixin):
    """Model for tracking teacher certifications."""
    __tablename__ = "educational_teacher_certifications"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("educational_teachers.id", ondelete="CASCADE"), nullable=False)
    certification_name = Column(String, nullable=False)
    issuing_organization = Column(String, nullable=False)
    issue_date = Column(DateTime, nullable=False)
    expiry_date = Column(DateTime, nullable=True)
    certification_number = Column(String, nullable=True)
    verification_url = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    teacher = relationship("app.models.educational.staff.teacher.Teacher", back_populates="certifications_list", overlaps="teacher,certifications_list")

    def __repr__(self):
        return f"<TeacherCertification {self.certification_name} - {self.teacher_id}>" 