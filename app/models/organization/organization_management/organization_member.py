"""
Organization Member Model

This model represents members of organizations.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base


class OrganizationMember(Base):
    """Model for organization members."""
    __tablename__ = "organization_members"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role_id = Column(Integer, ForeignKey("organization_roles.id"), nullable=False)
    member_status = Column(String(50), nullable=False)  # Active, Inactive, Pending, Suspended
    join_date = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organization = relationship("Organization", back_populates="members")
    user = relationship("User", back_populates="organization_memberships")
    role = relationship("OrganizationRole", back_populates="members")

    def __repr__(self):
        return f"<OrganizationMember(id={self.id}, organization_id={self.organization_id}, user_id={self.user_id})>"