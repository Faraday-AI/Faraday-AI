"""
Organization Models

This module defines organization-related models.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, JSON, Boolean, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
from pydantic import BaseModel

from app.models.core.base import CoreBase
from app.db.mixins import MetadataMixin

class Organization(CoreBase, MetadataMixin):
    """Model for organizations."""
    __tablename__ = "core_organizations"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    organization_type = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    organization_metadata = Column(JSON, nullable=True)

    # Relationships
    departments = relationship("Department", back_populates="organization")
    users = relationship("User", back_populates="organization")

class Department(CoreBase, MetadataMixin):
    """Model for departments."""
    __tablename__ = "departments"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("core_organizations.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    department_metadata = Column(JSON, nullable=True)

    # Relationships
    organization = relationship("Organization", back_populates="departments")
    users = relationship("User", back_populates="department") 