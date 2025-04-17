from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from pydantic import BaseModel, Field

class RoutineActivity(Base):
    """Model for activities in a routine."""
    __tablename__ = "routine_activities"

    id = Column(Integer, primary_key=True)
    routine_id = Column(Integer, ForeignKey("routines.id"), nullable=False)
    activity_id = Column(String, ForeignKey("activities.id"), nullable=False)
    order = Column(Integer, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    activity_type = Column(String, nullable=False)  # warm_up, main, cool_down
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    routine = relationship("Routine", back_populates="activities")
    activity = relationship("Activity", back_populates="routines")

    def __repr__(self):
        return f"<RoutineActivity {self.id}>"

class RoutineActivityBase(BaseModel):
    routine_id: int
    activity_id: str
    order: int
    duration_minutes: int
    activity_type: str

class RoutineActivityCreate(RoutineActivityBase):
    pass

class RoutineActivityUpdate(BaseModel):
    order: int | None = None
    duration_minutes: int | None = None
    activity_type: str | None = None

class RoutineActivityResponse(RoutineActivityBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 