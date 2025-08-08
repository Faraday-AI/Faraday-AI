"""Activity plan models."""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.shared_base import SharedBase
from app.models.activity import Activity
from app.models.user_management.user.user import User

class AdaptedActivityPlan(SharedBase):
    """Model for adapted activity plans."""
    __tablename__ = "adapted_activity_plans"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(String(1000))
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    is_template = Column(Boolean, default=False)
    plan_metadata = Column(JSON)  # Additional plan metadata
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    activities = relationship("app.models.activity_adaptation.activity.activity_plan.ActivityPlanActivity", back_populates="plan")
    creator = relationship("User", back_populates="created_activity_plans")

class ActivityPlanActivity(SharedBase):
    """Model for activities within a plan."""
    __tablename__ = "activity_plan_activities"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("activity_plans.id"), nullable=False)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    sequence_number = Column(Integer, nullable=False)  # Order in the plan
    duration_minutes = Column(Integer, nullable=False)
    notes = Column(String(1000))
    activity_metadata = Column(JSON)  # Additional activity metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    plan = relationship("app.models.activity_adaptation.activity.activity.ActivityPlan", back_populates="activities")
    activity = relationship("app.models.physical_education.activity.models.Activity", back_populates="activity_plans") 