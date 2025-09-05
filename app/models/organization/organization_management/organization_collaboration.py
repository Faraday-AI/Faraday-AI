"""
Organization Collaboration Model

This model represents collaborations between organizations.
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base


class OrganizationCollaboration(Base):
    """Model for organization collaborations."""
    __tablename__ = "organization_collaborations"

    id = Column(Integer, primary_key=True, index=True)
    organization_id_1 = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    organization_id_2 = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    collaboration_type = Column(String(100), nullable=False)  # Partnership, Joint Project, Resource Sharing, Training
    description = Column(Text, nullable=True)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    status = Column(String(50), nullable=False)  # Active, Completed, Planned, On Hold
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organization_1 = relationship("Organization", foreign_keys=[organization_id_1])
    organization_2 = relationship("Organization", foreign_keys=[organization_id_2])

    def __repr__(self):
        return f"<OrganizationCollaboration(id={self.id}, org1={self.organization_id_1}, org2={self.organization_id_2})>"