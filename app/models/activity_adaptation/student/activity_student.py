"""Models for relationships between activities and students."""
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, JSON, Enum as SQLEnum, Boolean
from sqlalchemy.orm import relationship
import enum

from app.models.core.base import BaseModel, StatusMixin
from app.models.physical_education.base.timestamped import TimestampedMixin
from app.models.physical_education.activity.models import StudentActivityPerformance

class ProgressionLevel(str, enum.Enum):
    """Enumeration of possible progression levels."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class PreferenceActivityType(str, enum.Enum):
    """Enumeration of preference activity types."""
    WARM_UP = "WARM_UP"
    SKILL_DEVELOPMENT = "SKILL_DEVELOPMENT"
    FITNESS_TRAINING = "FITNESS_TRAINING"
    GAME = "GAME"
    COOL_DOWN = "COOL_DOWN"

class StudentActivityPreference(BaseModel, TimestampedMixin):
    """Model for tracking student preferences for activities."""
    __tablename__ = "adaptation_activity_preferences"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    activity_type = Column(SQLEnum(PreferenceActivityType, name='preferenceactivitytype'), nullable=False)
    preference_score = Column(Float, nullable=False, default=0.5)

    # Relationships
    student = relationship("app.models.physical_education.student.models.Student", back_populates="adaptation_preferences")

    def __repr__(self):
        return f"<StudentActivityPreference {self.student_id} - {self.activity_type}>"

class ActivityProgression(BaseModel, TimestampedMixin):
    """Model for tracking student progression in activities."""
    __tablename__ = "student_activity_progressions"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    current_level = Column(SQLEnum(ProgressionLevel, name='progression_level_enum'), nullable=False)
    improvement_rate = Column(Float, nullable=False, default=0.0)
    last_assessment_date = Column(DateTime)

    # Relationships
    student = relationship("Student", back_populates="adaptation_progressions", overlaps="student,adaptation_progressions")
    activity = relationship("app.models.physical_education.activity.models.Activity", back_populates="progressions", overlaps="activity,progressions")

    def __repr__(self):
        return f"<ActivityProgression {self.activity_id} - {self.current_level}>"

class ActivityAdaptation(BaseModel, TimestampedMixin, StatusMixin):
    """Model for activity adaptations."""
    __tablename__ = "student_activity_adaptations"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    adaptation_type = Column(String, nullable=False)
    modifications = Column(JSON, nullable=False)
    reason = Column(String)
    effectiveness_rating = Column(Integer)  # 1-5 scale
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime)

    # Relationships
    activity = relationship("app.models.physical_education.activity.models.Activity", back_populates="student_adaptations")
    student = relationship("app.models.physical_education.student.models.Student", back_populates="student_activity_adaptations")
    history = relationship("app.models.activity_adaptation.student.activity_student.AdaptationHistory", back_populates="adaptation")

    def __repr__(self):
        return f"<ActivityAdaptation {self.activity_id} - {self.student_id}>"

class AdaptationHistory(BaseModel, TimestampedMixin):
    """Model for tracking adaptation history."""
    __tablename__ = "student_adaptation_history"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    adaptation_id = Column(Integer, ForeignKey("student_activity_adaptations.id"), nullable=False)
    change_type = Column(String, nullable=False)
    previous_data = Column(JSON)
    new_data = Column(JSON)
    reason = Column(String)
    effectiveness_score = Column(Float)

    # Relationships
    adaptation = relationship("app.models.activity_adaptation.student.activity_student.ActivityAdaptation", back_populates="history")

    def __repr__(self):
        return f"<AdaptationHistory {self.adaptation_id}>" 