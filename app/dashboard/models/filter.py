from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.shared_base import SharedBase as Base

class Filter(Base):
    """Model for filters."""
    __tablename__ = "filters"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("dashboard_users.id"), nullable=False)
    name = Column(String, nullable=False)
    filter_type = Column(String, nullable=False)
    filter_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("DashboardUser", back_populates="filters") 