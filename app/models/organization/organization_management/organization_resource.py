"""
Organization Resource Model

This model represents resources within organizations.
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Text, Float, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base


class OrganizationResource(Base):
    """Model for organization resources."""
    __tablename__ = "organization_resources"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    resource_name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    resource_type = Column(String(100), nullable=False)  # Equipment, Software, Facilities, Materials, Personnel
    quantity = Column(Integer, nullable=False)
    unit_cost = Column(Float, nullable=True)
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organization = relationship("Organization", back_populates="resources")

    def __repr__(self):
        return f"<OrganizationResource(id={self.id}, name={self.resource_name}, type={self.resource_type})>"