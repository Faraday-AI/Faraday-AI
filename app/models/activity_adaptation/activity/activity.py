"""Activity models for physical education."""
from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, JSON, Enum as SQLEnum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ENUM, JSONB

from app.models.shared_base import SharedBase
from app.models.mixins import StatusMixin, MetadataMixin, TimestampedMixin, NamedMixin
from app.models.physical_education.pe_enums.pe_types import (
    ActivityType as PEActivityType,
    DifficultyLevel as PEActivityDifficultyLevel,
    EquipmentRequirement as PEActivityEquipmentRequirement,
    ActivityCategoryType as PEActivityCategoryType
)
from app.models.core.activity import CoreActivity
from app.models.activity_adaptation.categories.associations import ActivityCategoryAssociation

# Re-export the models
__all__ = [
    'CoreActivity',
    'AdaptedActivity',
    'AdaptedActivityCategory',
    'ActivityPlan',
    'ActivityPlanActivity'
]

class AdaptedActivityCategory(SharedBase, NamedMixin, MetadataMixin):
    """Model for adapted activity categories."""
    __tablename__ = "adapted_activity_categories"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    category_type = Column(SQLEnum(PEActivityCategoryType, name='activity_category_type_enum'), nullable=False)

    def __repr__(self):
        return f"<AdaptedActivityCategory {self.name}>"

class ActivityPlan(SharedBase, NamedMixin, TimestampedMixin, StatusMixin, MetadataMixin):
    """Model for activity plans."""
    __tablename__ = "adapted_activity_plans"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime)
    goals = Column(JSON)
    progress_metrics = Column(JSON)
    notes = Column(String)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=True)  # Optional for template plans

    # Relationships
    student = relationship("Student", back_populates="adapted_activity_plans")
    activities = relationship("app.models.activity_adaptation.activity.activity.ActivityPlanActivity", back_populates="plan")

    def __repr__(self):
        return f"<ActivityPlan {self.name}>"

class ActivityPlanActivity(SharedBase, TimestampedMixin):
    """Model for activities within an activity plan."""
    __tablename__ = "adapted_activity_plan_activities"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("adapted_activity_plans.id"), nullable=False)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    order = Column(Integer, nullable=False)
    duration_minutes = Column(Integer)
    intensity_level = Column(String)
    adaptations = Column(JSON)
    notes = Column(String)

    # Relationships
    plan = relationship("app.models.activity_adaptation.activity.activity.ActivityPlan", back_populates="activities")
    activity = relationship("app.models.physical_education.activity.models.Activity", back_populates="activity_plans")

    def __repr__(self):
        return f"<ActivityPlanActivity {self.plan_id} - {self.activity_id}>"

class AdaptedActivity(SharedBase, NamedMixin, TimestampedMixin, StatusMixin, MetadataMixin):
    """Model for adapted activities."""
    __tablename__ = "adapted_activities"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=True)  # Link to base activity
    type = Column(SQLEnum(PEActivityType, name='activity_type_enum'), nullable=False)
    difficulty_level = Column(SQLEnum(PEActivityDifficultyLevel, name='activity_difficulty_level_enum'), nullable=False)
    equipment_requirements = Column(SQLEnum(PEActivityEquipmentRequirement, name='activity_equipment_requirement_enum'), nullable=False)
    duration_minutes = Column(Integer)
    instructions = Column(JSON)
    adaptations = Column(JSON)
    activity_metadata = Column(JSON)  # Renamed from metadata to avoid SQLAlchemy reserved name

    # Relationships

    def __repr__(self):
        return f"<AdaptedActivity {self.name}>" 