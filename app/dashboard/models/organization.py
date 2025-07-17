from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.shared_base import SharedBase

class Organization(SharedBase):
    """Model for organizations."""
    __tablename__ = "dashboard_organizations"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    parent_id = Column(Integer, ForeignKey("dashboard_organizations.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    parent = relationship("Organization", remote_side=[id], backref="children")
    users = relationship("DashboardUser", back_populates="organization")
    departments = relationship("Department", back_populates="organization")
    teams = relationship("Team", back_populates="organization")
    projects = relationship("DashboardProject", back_populates="organization") 