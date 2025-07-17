from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

class Notification(Base):
    """Model for notifications."""
    __tablename__ = "dashboard_notifications"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    message = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("dashboard_users.id"), nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("DashboardUser", back_populates="notifications") 