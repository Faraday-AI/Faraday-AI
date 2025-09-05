"""
Organization Setting Model

This model represents settings for organizations.
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Text, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base


class OrganizationSetting(Base):
    """Model for organization settings."""
    __tablename__ = "organization_settings"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    setting_key = Column(String(100), nullable=False)
    setting_value = Column(Text, nullable=False)
    setting_type = Column(String(50), nullable=False)  # General, Security, Notification, Integration, Custom
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organization = relationship("Organization", back_populates="settings")

    def __repr__(self):
        return f"<OrganizationSetting(id={self.id}, key={self.setting_key}, type={self.setting_type})>"