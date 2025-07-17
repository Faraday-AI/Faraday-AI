from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

class Search(Base):
    """Model for searches."""
    __tablename__ = "searches"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("dashboard_users.id"), nullable=False)
    query = Column(String, nullable=False)
    filters = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("DashboardUser", back_populates="searches") 