from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.shared_base import SharedBase

class Analytics(SharedBase):
    """Model for analytics."""
    __tablename__ = "analytics"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("dashboard_users.id"), nullable=False)
    event_type = Column(String, nullable=False)
    event_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("DashboardUser", back_populates="analytics") 