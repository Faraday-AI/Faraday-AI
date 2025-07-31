"""
Equipment Models

This module defines equipment models for physical education.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Float, Text, Boolean
from sqlalchemy.orm import relationship
from pydantic import BaseModel, ConfigDict

from app.models.core.base import CoreBase
from app.models.mixins import TimestampedMixin
from app.models.physical_education.pe_enums.pe_types import (
    EquipmentType,
    EquipmentStatus
)



# Import Activity model to ensure it's registered with SQLAlchemy
from app.models.physical_education.activity.models import Activity
# Import User model to ensure it's registered with SQLAlchemy
from app.models.core.user import User

# Re-export for backward compatibility
BaseModelMixin = CoreBase
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
    condition = Column(String(20))  # Keep for backward compatibility
    condition_id = Column(Integer, ForeignKey('equipment_conditions.id'))  # New foreign key
    location = Column(String(100))
    equipment_metadata = Column(JSON)
    category_id = Column(Integer, ForeignKey('equipment_categories.id'))
    
    # Relationships
    maintenance_records = relationship("app.models.physical_education.equipment.models.EquipmentMaintenance", back_populates="equipment")
    maintenance_records_alt = relationship("app.models.physical_education.equipment.models.MaintenanceRecord", back_populates="equipment")
    usage_records = relationship("app.models.physical_education.equipment.models.EquipmentUsage", back_populates="equipment")
    category = relationship("EquipmentCategory", back_populates="equipment")
    condition_relation = relationship("EquipmentCondition", back_populates="equipment")
    safety_alerts = relationship("app.models.skill_assessment.safety.safety.SafetyAlert", back_populates="equipment", overlaps="equipment,safety_alerts")
    safety_checks = relationship("app.models.skill_assessment.safety.safety.EquipmentCheck", back_populates="equipment", overlaps="equipment,safety_checks")
    safety_reports = relationship("app.models.skill_assessment.safety.safety.SafetyReport", back_populates="equipment", overlaps="equipment,safety_reports")

class EquipmentMaintenance(BaseModelMixin, TimestampMixin):
    """Model for equipment maintenance records."""
    
    __tablename__ = "physical_education_equipment_maintenance"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(Integer, ForeignKey("physical_education_equipment.id"), nullable=False)
    maintenance_date = Column(DateTime, nullable=False)
    maintenance_type = Column(String(50), nullable=False)
    description = Column(Text)
    cost = Column(Float)
    performed_by = Column(String(100))
    maintenance_metadata = Column(JSON)
    
    # Relationships
    equipment = relationship("app.models.physical_education.equipment.models.Equipment", back_populates="maintenance_records")

class EquipmentUsage(BaseModelMixin, TimestampMixin):
    """Model for equipment usage records."""
    
    __tablename__ = "equipment_usage"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(Integer, ForeignKey("physical_education_equipment.id"), nullable=False)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    usage_date = Column(DateTime, nullable=False)
    quantity_used = Column(Integer)
    usage_notes = Column(Text)
    usage_metadata = Column(JSON)
    
    # Relationships
    equipment = relationship("app.models.physical_education.equipment.models.Equipment", back_populates="usage_records")
    
    # Activity relationship temporarily disabled to fix mapper initialization
    # activity = relationship(
    #     "Activity",
    #     foreign_keys=[activity_id],
    #     lazy="dynamic",
    #     viewonly=True
    # )
    
    # Bridge relationship to avoid circular imports
    def get_activity(self):
        """Get the associated activity through a lazy relationship."""
        from app.models.physical_education.activity.models import Activity
        return Activity.query.get(self.activity_id)

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
    equipment = relationship('app.models.physical_education.equipment.models.Equipment', back_populates='category')
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
    equipment = relationship('app.models.physical_education.equipment.models.Equipment', back_populates='condition_relation')

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
    equipment_id = Column(Integer, ForeignKey("physical_education_equipment.id"), nullable=False)
    maintenance_date = Column(DateTime, nullable=False)
    maintenance_type = Column(String(50), nullable=False)
    description = Column(Text)
    performed_by = Column(String(100))  # Keep for backward compatibility
    maintainer_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Foreign key to users table
    cost = Column(Float)
    record_metadata = Column(JSON)  # Renamed from metadata
    next_maintenance_date = Column(DateTime)
    
    # Relationships
    equipment = relationship("app.models.physical_education.equipment.models.Equipment", back_populates="maintenance_records_alt")
    maintainer = relationship(User, back_populates="performed_maintenance") 