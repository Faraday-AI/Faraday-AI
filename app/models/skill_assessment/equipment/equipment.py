"""Equipment-related models for physical education."""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Enum as SQLEnum, Boolean, Float, Text
from sqlalchemy.orm import relationship
from app.models.shared_base import SharedBase
from app.models.physical_education.pe_enums.pe_types import EquipmentType
from app.models.physical_education.safety import SafetyAlert
from app.models.core.core_models import EquipmentStatus
import enum

class Equipment(SharedBase):
    """Model for physical education equipment."""
    __tablename__ = "skill_assessment_equipment"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    equipment_type = Column(SQLEnum(EquipmentType, name='equipment_type_enum'), nullable=False)
    description = Column(Text, nullable=True)
    quantity = Column(Integer, nullable=False)
    condition = Column(String(50), nullable=False)  # good, fair, poor
    status = Column(SQLEnum(EquipmentStatus, name='equipment_status_enum'), nullable=False, default=EquipmentStatus.AVAILABLE)
    purchase_date = Column(DateTime, nullable=True)
    last_maintenance = Column(DateTime, nullable=True)
    next_maintenance = Column(DateTime, nullable=True)
    location = Column(String(255), nullable=False)
    notes = Column(Text, nullable=True)
    equipment_metadata = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    checks = relationship("EquipmentCheck", back_populates="equipment", cascade="all, delete-orphan")
    safety_alerts = relationship("SafetyAlert", back_populates="equipment", cascade="all, delete-orphan")
    # safety_reports = relationship("SafetyReport", back_populates="equipment", cascade="all, delete-orphan")
    maintenance_records = relationship("EquipmentMaintenance", back_populates="equipment", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Equipment {self.name} - {self.equipment_type}>"

class EquipmentMaintenance(SharedBase):
    """Model for tracking equipment maintenance records."""
    __tablename__ = "skill_assessment_equipment_maintenance"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=False)
    maintenance_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    maintenance_type = Column(String, nullable=False)
    performed_by = Column(String, nullable=False)
    cost = Column(Float)
    notes = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    equipment = relationship("Equipment", back_populates="maintenance_records")

    def __repr__(self):
        return f"<EquipmentMaintenance {self.equipment_id} - {self.maintenance_date}>"

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional
from datetime import datetime

class EquipmentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    status: EquipmentStatus
    purchase_date: Optional[datetime] = None
    last_maintenance: Optional[datetime] = None
    next_maintenance: Optional[datetime] = None
    condition: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty or whitespace')
        return v.strip()

class EquipmentCreate(EquipmentBase):
    pass

class EquipmentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    status: Optional[EquipmentStatus] = None
    purchase_date: Optional[datetime] = None
    last_maintenance: Optional[datetime] = None
    next_maintenance: Optional[datetime] = None
    condition: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Name cannot be empty or whitespace')
        return v.strip() if v else v

class EquipmentResponse(EquipmentBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True) 