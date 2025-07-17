"""
Equipment Models

This module defines equipment models for physical education.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Float, Text, Boolean
from sqlalchemy.orm import relationship
from pydantic import BaseModel, ConfigDict

from app.models.base import Base, BaseModel as SQLBaseModel
from app.models.mixins import TimestampedMixin
from app.models.physical_education.pe_enums.pe_types import (
    EquipmentType,
    EquipmentStatus
)

# Re-export for backward compatibility
BaseModelMixin = SQLBaseModel
TimestampMixin = TimestampedMixin

class Equipment(BaseModelMixin, TimestampMixin):
    """Model for physical education equipment."""
    
    __tablename__ = "physical_education_equipment"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    category = Column(String(50))
    quantity = Column(Integer, default=0)
    condition = Column(String(20))
    location = Column(String(100))
    equipment_metadata = Column(JSON)
    
    # Relationships
    maintenance_records = relationship("EquipmentMaintenance", back_populates="equipment")
    usage_records = relationship("EquipmentUsage", back_populates="equipment")

class EquipmentMaintenance(BaseModelMixin, TimestampMixin):
    """Model for equipment maintenance records."""
    
    __tablename__ = "physical_education_equipment_maintenance"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=False)
    maintenance_date = Column(DateTime, nullable=False)
    maintenance_type = Column(String(50), nullable=False)
    description = Column(Text)
    cost = Column(Float)
    performed_by = Column(String(100))
    maintenance_metadata = Column(JSON)
    
    # Relationships
    equipment = relationship("Equipment", back_populates="maintenance_records")

class EquipmentUsage(BaseModelMixin, TimestampMixin):
    """Model for equipment usage records."""
    
    __tablename__ = "equipment_usage"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=False)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    usage_date = Column(DateTime, nullable=False)
    quantity_used = Column(Integer)
    usage_notes = Column(Text)
    usage_metadata = Column(JSON)
    
    # Relationships
    equipment = relationship("Equipment", back_populates="usage_records")
    activity = relationship("app.models.physical_education.activity.models.Activity")

class EquipmentCreate(BaseModel):
    """Pydantic model for creating equipment."""
    
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    quantity: Optional[int] = 0
    condition: Optional[str] = None
    location: Optional[str] = None
    equipment_metadata: Optional[dict] = None

class EquipmentUpdate(BaseModel):
    """Pydantic model for updating equipment."""
    
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    quantity: Optional[int] = None
    condition: Optional[str] = None
    location: Optional[str] = None
    equipment_metadata: Optional[dict] = None

class EquipmentResponse(BaseModel):
    """Pydantic model for equipment responses."""
    
    id: int
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    quantity: Optional[int] = None
    condition: Optional[str] = None
    location: Optional[str] = None
    equipment_metadata: Optional[dict] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class EquipmentCategory(BaseModelMixin, TimestampMixin):
    """Model for equipment categories."""
    __tablename__ = 'equipment_categories'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    parent_id = Column(Integer, ForeignKey('equipment_categories.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    equipment = relationship('Equipment', back_populates='category')
    parent = relationship('EquipmentCategory', remote_side=[id], backref='children')

class EquipmentCategoryCreate(BaseModel):
    """Pydantic model for creating equipment categories."""
    
    name: str
    description: Optional[str] = None
    parent_id: Optional[int] = None

class EquipmentCategoryUpdate(BaseModel):
    """Pydantic model for updating equipment categories."""
    
    name: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[int] = None

class EquipmentCategoryResponse(BaseModel):
    """Pydantic model for equipment category responses."""
    
    id: int
    name: str
    description: Optional[str] = None
    parent_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class EquipmentCondition(BaseModelMixin, TimestampMixin):
    """Model for equipment conditions."""
    __tablename__ = 'equipment_conditions'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    severity = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    equipment = relationship('Equipment', back_populates='condition')

class EquipmentConditionCreate(BaseModel):
    """Pydantic model for creating equipment conditions."""
    
    name: str
    description: Optional[str] = None
    severity: str

class EquipmentConditionUpdate(BaseModel):
    """Pydantic model for updating equipment conditions."""
    
    name: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[str] = None

class EquipmentConditionResponse(BaseModel):
    """Pydantic model for equipment condition responses."""
    
    id: int
    name: str
    description: Optional[str] = None
    severity: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class EquipmentStatus(BaseModelMixin, TimestampMixin):
    """Model for equipment status."""
    __tablename__ = 'equipment_status'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class EquipmentStatusCreate(BaseModel):
    """Pydantic model for creating equipment status."""
    
    name: str
    description: Optional[str] = None
    is_active: bool = True

class EquipmentStatusUpdate(BaseModel):
    """Pydantic model for updating equipment status."""
    
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class EquipmentStatusResponse(BaseModel):
    """Pydantic model for equipment status responses."""
    
    id: int
    name: str
    description: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class EquipmentType(BaseModelMixin, TimestampMixin):
    """Model for equipment types."""
    __tablename__ = 'equipment_types'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class EquipmentTypeCreate(BaseModel):
    """Pydantic model for creating equipment types."""
    
    name: str
    description: Optional[str] = None

class EquipmentTypeUpdate(BaseModel):
    """Pydantic model for updating equipment types."""
    
    name: Optional[str] = None
    description: Optional[str] = None

class EquipmentTypeResponse(BaseModel):
    """Pydantic model for equipment type responses."""
    
    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class MaintenanceRecord(BaseModelMixin, TimestampMixin):
    """Model for tracking equipment maintenance records."""
    
    __tablename__ = "maintenance_records"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=False)
    maintenance_date = Column(DateTime, nullable=False)
    maintenance_type = Column(String(50), nullable=False)
    description = Column(Text)
    performed_by = Column(String(100))
    cost = Column(Float)
    record_metadata = Column(JSON)  # Renamed from metadata
    next_maintenance_date = Column(DateTime)
    
    # Relationships
    equipment = relationship("Equipment", back_populates="maintenance_records")
    maintainer = relationship("User", back_populates="performed_maintenance") 