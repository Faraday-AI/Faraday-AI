from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base

class ActivityPlanActivity(Base):
    """Model for activities within an activity plan."""
    __tablename__ = "activity_plan_activities"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    plan_id = Column(Integer, ForeignKey("activity_plans.id"), nullable=False)
    activity_id = Column(String, ForeignKey("activities.id"), nullable=False)
    order = Column(Integer, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    activity_type = Column(String, nullable=False)  # warm_up, main, cool_down
    is_completed = Column(Boolean, default=False)
    notes = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    plan = relationship("ActivityPlan", back_populates="activities")
    activity = relationship("Activity")

    def __repr__(self):
        return f"<ActivityPlanActivity {self.id}>" 