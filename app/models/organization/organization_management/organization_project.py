"""
Organization Project Model

This model represents projects within organizations.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base


class OrganizationProject(Base):
    """Model for organization projects."""
    __tablename__ = "organization_projects"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    project_name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    project_type = Column(String(100), nullable=False)  # Research, Development, Implementation, Training, Assessment
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    status = Column(String(50), nullable=False)  # Planning, Active, On Hold, Completed, Cancelled
    budget = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organization = relationship("Organization", back_populates="projects")

    def __repr__(self):
        return f"<OrganizationProject(id={self.id}, name={self.project_name}, status={self.status})>"