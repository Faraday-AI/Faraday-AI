"""
Progress Models

This module defines progress models for physical education.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Text, JSON, Boolean
from sqlalchemy.orm import relationship
from pydantic import BaseModel, ConfigDict

from app.models.base import Base, BaseModel as SQLBaseModel
from app.models.mixins import TimestampedMixin
from app.models.physical_education.pe_enums.pe_types import (
    ProgressStatus,
    ProgressType,
    ProgressLevel,
    ProgressTrigger,
    ChangeType,
    PerformanceLevel
)
from app.models.physical_education.base.sqlalchemy_base import BaseModelMixin
from app.db.mixins import TimestampMixin
from app.models.physical_education.base.base_class import PEBase
from app.models.physical_education.relationships import setup_progress_relationships

# Import Activity model to ensure it's available for relationships
from app.models.physical_education.activity.models import Activity

# Note: Student model is imported via string-based relationships to avoid circular imports

# Note: Using string-based relationships to avoid circular imports

# Re-export for backward compatibility
BaseModelMixin = SQLBaseModel
TimestampMixin = TimestampedMixin

# Base classes first
class ProgressBase(BaseModelMixin, TimestampMixin):
    """Base class for progress models."""
    __tablename__ = 'progress_base'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    type = Column(Enum(ProgressType, name='progress_type_enum'), nullable=False)
    status = Column(Enum(ProgressStatus, name='progress_status_enum'), nullable=False)
    description = Column(Text)
    student_id = Column(Integer, ForeignKey('students.id', ondelete="CASCADE"), nullable=False)
    teacher_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    class_id = Column(Integer, ForeignKey('physical_education_classes.id', ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

class ProgressNoteBase(BaseModelMixin, TimestampMixin):
    """Base class for progress note models."""
    __tablename__ = 'progress_note_base'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    progress_id = Column(Integer, ForeignKey('progress_base.id', ondelete="CASCADE"), nullable=False)
    teacher_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    type = Column(String(50))  # Polymorphic discriminator
    
    __mapper_args__ = {
        'polymorphic_identity': 'progress_note_base',
        'polymorphic_on': 'type'
    }

class PhysicalEducationProgressNote(ProgressNoteBase):
    """Model for progress notes."""
    __tablename__ = 'progress_notes'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, ForeignKey('progress_note_base.id'), primary_key=True)
    # Removed duplicate created_at and updated_at columns - they're inherited from base class
    
    __mapper_args__ = {
        'polymorphic_identity': 'progress_note',
        'inherit_condition': ProgressNoteBase.id == id
    }
    
    # Relationships will be set up by setup_progress_relationships
    pass

    def __repr__(self):
        return f"<PhysicalEducationProgressNote {self.id} - {self.content[:30]}>"

class ProgressGoalBase(BaseModelMixin, TimestampMixin):
    """Base class for progress goal models."""
    __tablename__ = 'progress_goals_base'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    goal_type = Column(String(50), nullable=False)
    target_value = Column(Float)
    start_date = Column(DateTime, nullable=False)
    target_date = Column(DateTime, nullable=False)
    status = Column(String(20), default="PENDING")
    goal_notes = Column(Text)
    type = Column(String(50))  # Polymorphic discriminator
    
    # Progress relationships temporarily disabled to fix seeding issues
    # student = relationship("Student", back_populates="progress_goals")
    # activity = relationship("Activity", back_populates="progress_goals")
    
    __mapper_args__ = {
        'polymorphic_identity': 'progress_goal_base',
        'polymorphic_on': 'type'
    }

class ProgressGoal(ProgressGoalBase):
    """Model for tracking student progress goals."""
    __tablename__ = 'progress_goals'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, ForeignKey('progress_goals_base.id'), primary_key=True)
    
    __mapper_args__ = {
        'polymorphic_identity': 'progress_goal',
        'inherit_condition': ProgressGoalBase.id == id
    }
    
    # Additional fields specific to ProgressGoal can be added here
    pass

    def __repr__(self):
        return f"<ProgressGoal {self.id} - {self.goal_type}>"

class ProgressMilestone(BaseModelMixin, TimestampMixin):
    """Model for tracking progress milestones."""
    __tablename__ = "progress_milestones"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    progress_id = Column(Integer, ForeignKey("progress_base.id", ondelete="CASCADE"), nullable=False)
    milestone_name = Column(String(100), nullable=False)
    target_date = Column(DateTime, nullable=False)
    achieved_date = Column(DateTime)
    status = Column(String(20), default="PENDING")
    notes = Column(Text)
    
    # Relationships will be set up by setup_progress_relationships
    pass

    def __repr__(self):
        return f"<ProgressMilestone {self.milestone_name} - {self.status}>"

# Define ProgressAssessment
class ProgressAssessment(BaseModelMixin, TimestampMixin):
    """Model for tracking progress assessments."""
    __tablename__ = "progress_assessments"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    progress_id = Column(Integer, ForeignKey("progress_base.id", ondelete="CASCADE"), nullable=False)
    assessment_type = Column(String(50), nullable=False)
    assessment_date = Column(DateTime, nullable=False)
    assessor_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    score = Column(Float)
    feedback = Column(Text)
    recommendations = Column(Text)
    
    # Relationships will be set up by setup_progress_relationships
    pass

    def __repr__(self):
        return f"<ProgressAssessment {self.assessment_type} - {self.assessment_date}>"

# Finally define Progress after all its related models are defined
class Progress(Base, TimestampMixin):
    """Model for student progress."""
    __tablename__ = "progress"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    progress_date = Column(DateTime, nullable=False)
    progress_type = Column(String(50), nullable=False)
    score = Column(Float)
    progress_notes = Column(Text)
    progress_metadata = Column(JSON)
    
    # Progress relationships temporarily disabled to fix seeding issues
    # student = relationship("Student", back_populates="progress")
    # activity = relationship("Activity")
    metrics = relationship("ProgressMetric", back_populates="progress")

    def __repr__(self):
        return f"<Progress {self.student_id} - {self.activity_id}>"

# Pydantic models for API
class ProgressCreate(BaseModel):
    """Pydantic model for creating progress records."""
    __allow_unmapped__ = True
    
    student_id: int
    activity_id: int
    progress_date: datetime
    progress_type: str
    score: Optional[float] = None
    progress_notes: Optional[str] = None
    progress_metadata: Optional[dict] = None

class ProgressUpdate(BaseModel):
    """Pydantic model for updating progress records."""
    __allow_unmapped__ = True
    
    progress_date: Optional[datetime] = None
    progress_type: Optional[str] = None
    score: Optional[float] = None
    progress_notes: Optional[str] = None
    progress_metadata: Optional[dict] = None

class ProgressResponse(BaseModel):
    """Pydantic model for progress responses."""
    __allow_unmapped__ = True
    
    id: int
    student_id: int
    activity_id: int
    progress_date: datetime
    progress_type: str
    score: Optional[float] = None
    progress_notes: Optional[str] = None
    progress_metadata: Optional[dict] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ProgressGoalCreate(BaseModel):
    """Pydantic model for creating progress goals."""
    __allow_unmapped__ = True
    
    title: str
    description: Optional[str] = None
    target_date: datetime
    status: ProgressStatus
    progress_id: int

class ProgressGoalUpdate(BaseModel):
    """Pydantic model for updating progress goals."""
    __allow_unmapped__ = True
    
    title: Optional[str] = None
    description: Optional[str] = None
    target_date: Optional[datetime] = None
    status: Optional[ProgressStatus] = None

class ProgressGoalResponse(BaseModel):
    """Pydantic model for progress goal responses."""
    __allow_unmapped__ = True
    
    id: int
    title: str
    description: Optional[str] = None
    target_date: datetime
    status: ProgressStatus
    progress_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ProgressNoteCreate(BaseModel):
    """Pydantic model for creating progress notes."""
    __allow_unmapped__ = True
    
    content: str
    progress_id: int
    teacher_id: int

class ProgressNoteUpdate(BaseModel):
    """Pydantic model for updating progress notes."""
    __allow_unmapped__ = True
    
    content: Optional[str] = None

class ProgressNoteResponse(BaseModel):
    """Pydantic model for progress note responses."""
    __allow_unmapped__ = True
    
    id: int
    content: str
    progress_id: int
    teacher_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ProgressMetric(BaseModelMixin, TimestampMixin):
    """Model for progress metrics."""
    __tablename__ = "progress_metrics"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    progress_id = Column(Integer, ForeignKey("progress.id"), nullable=False)
    metric_type = Column(String(50), nullable=False)
    value = Column(Float)
    unit = Column(String(20))
    metric_notes = Column(Text)
    metric_metadata = Column(JSON)
    
    # Relationships
    progress = relationship("Progress") 