from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy import Column, String, DateTime, JSON, ForeignKey, Boolean, Float, Integer
from sqlalchemy.orm import relationship
from app.core.database import Base

class Student(Base):
    """Model for students."""
    __tablename__ = "students"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    grade = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    medical_conditions = Column(JSON, default=list)
    fitness_level = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    safety_incidents = relationship("SafetyIncident", back_populates="student", cascade="all, delete-orphan")
    activity_performances = relationship("StudentActivityPerformance", back_populates="student", cascade="all, delete-orphan")
    activity_preferences = relationship("StudentActivityPreference", back_populates="student", cascade="all, delete-orphan")
    activity_progressions = relationship("ActivityProgression", back_populates="student", cascade="all, delete-orphan")
    activity_plans = relationship("ActivityPlan", back_populates="student", cascade="all, delete-orphan")
    classes = relationship("ClassStudent", back_populates="student", cascade="all, delete-orphan")
    movement_analyses = relationship("MovementAnalysis", back_populates="student", cascade="all, delete-orphan")
    skill_assessments = relationship("SkillAssessment", back_populates="student", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Student {self.name} - {self.grade}>" 