"""
Organization Role Model

This model represents roles within an organization.
"""

from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base


class OrganizationRole(Base):
    """Model for organization roles."""
    __tablename__ = "organization_roles"

    id = Column(Integer, primary_key=True, index=True)
    role_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    role_type = Column(String(50), nullable=False)  # Administrative, Academic, Support, Leadership, Staff
    permissions = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    members = relationship("OrganizationMember", back_populates="role")

    def __repr__(self):
        return f"<OrganizationRole(id={self.id}, name={self.role_name}, type={self.role_type})>"