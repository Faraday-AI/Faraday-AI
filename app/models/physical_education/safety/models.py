"""
Safety Models

This module defines safety-related models for physical education.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text, Boolean, Float, JSON, Table
from sqlalchemy.orm import relationship
from pydantic import BaseModel, ConfigDict

from app.models.shared_base import SharedBase

from app.models.physical_education.pe_enums.pe_types import (
    IncidentType,
    IncidentSeverity,
    EquipmentStatus
)

class SafetyIncident(SharedBase):
    """Model for safety incidents."""
    __tablename__ = "safety_incidents"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    protocol_id = Column(Integer, ForeignKey("safety_protocols.id"), nullable=True)
    incident_date = Column(DateTime, nullable=False)
    incident_type = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False)
    incident_metadata = Column(JSON)  # Renamed from metadata
    
    # Relationships
    student = relationship("Student", back_populates="safety_incidents")
    activity = relationship("app.models.physical_education.activity.models.Activity", back_populates="safety_incidents")
    protocol = relationship("SafetyProtocol", back_populates="incidents")
    measures = relationship("SafetyMeasure", back_populates="incident")
    risk_assessments = relationship("app.models.physical_education.safety.models.RiskAssessment", back_populates="incident", lazy="joined")

class SafetyMeasure(SharedBase):
    """Model for safety measures."""
    __tablename__ = "safety_measures"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("safety_incidents.id"), nullable=False)
    measure_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    implementation_date = Column(DateTime, nullable=False)
    measure_metadata = Column(JSON)  # Renamed from metadata
    
    # Relationships
    incident = relationship("SafetyIncident", back_populates="measures")

class SafetyChecklist(SharedBase):
    """Model for safety checklists."""
    __tablename__ = "safety_checklists"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    checklist_date = Column(DateTime, nullable=False)
    checklist_type = Column(String(50), nullable=False)
    checklist_metadata = Column(JSON)  # Renamed from metadata
    
    # Relationships
    activity = relationship("app.models.physical_education.activity.models.Activity", back_populates="safety_checklists")
    items = relationship("SafetyChecklistItem", back_populates="checklist")

class SafetyChecklistItem(SharedBase):
    """Model for safety checklist items."""
    __tablename__ = "safety_checklist_items"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    checklist_id = Column(Integer, ForeignKey("safety_checklists.id"), nullable=False)
    item_name = Column(String(100), nullable=False)
    is_checked = Column(Boolean, default=False)
    notes = Column(Text)
    item_metadata = Column(JSON)  # Renamed from metadata
    
    # Relationships
    checklist = relationship("SafetyChecklist", back_populates="items")

class SafetyIncidentBase(SharedBase):
    """Base class for safety incident models."""
    __tablename__ = 'safety_incident_base'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    type = Column(Enum(IncidentType, name='incident_type_enum'), nullable=False)
    severity = Column(Enum(IncidentSeverity, name='incident_severity_enum'), nullable=False)
    description = Column(Text, nullable=False)
    location = Column(String(100), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"))
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    equipment_id = Column(Integer, ForeignKey('equipment.id'))
    action_taken = Column(Text, nullable=False)
    follow_up_required = Column(Boolean, default=False)
    follow_up_notes = Column(Text)
    
    # Relationships
    student = relationship("Student", back_populates="safety_incident_bases")
    teacher = relationship("User", back_populates="reported_incidents")
    equipment = relationship("Equipment", back_populates="safety_incidents")

class SafetyIncidentCreate(BaseModel):
    """Pydantic model for creating safety incidents."""
    __allow_unmapped__ = True
    
    type: IncidentType
    severity: IncidentSeverity
    description: str
    location: str
    student_id: Optional[int] = None
    teacher_id: int
    equipment_id: Optional[int] = None
    action_taken: str
    follow_up_required: bool = False
    follow_up_notes: Optional[str] = None

class SafetyIncidentUpdate(BaseModel):
    """Pydantic model for updating safety incidents."""
    __allow_unmapped__ = True
    
    type: Optional[IncidentType] = None
    severity: Optional[IncidentSeverity] = None
    description: Optional[str] = None
    location: Optional[str] = None
    student_id: Optional[int] = None
    teacher_id: Optional[int] = None
    equipment_id: Optional[int] = None
    action_taken: Optional[str] = None
    follow_up_required: Optional[bool] = None
    follow_up_notes: Optional[str] = None

class SafetyIncidentResponse(BaseModel):
    """Pydantic model for safety incident responses."""
    __allow_unmapped__ = True
    
    id: int
    type: IncidentType
    severity: IncidentSeverity
    description: str
    location: str
    student_id: Optional[int] = None
    teacher_id: int
    equipment_id: Optional[int] = None
    action_taken: str
    follow_up_required: bool
    follow_up_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class EquipmentBase(SharedBase):
    """Base class for equipment models."""
    __tablename__ = 'equipment_base'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False)
    status = Column(Enum(EquipmentStatus, name='equipment_status_enum'), default=EquipmentStatus.AVAILABLE)
    last_maintenance = Column(DateTime)
    next_maintenance = Column(DateTime)
    maintenance_notes = Column(Text)
    
    __mapper_args__ = {
        'polymorphic_identity': 'equipment_base',
        'polymorphic_on': 'type'
    }

class Equipment(EquipmentBase):
    """Model for physical education equipment."""
    __tablename__ = 'equipment'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, ForeignKey('equipment_base.id'), primary_key=True)
    
    # Relationships
    safety_incidents = relationship("SafetyIncidentBase", back_populates="equipment", lazy="joined")
    safety_checks = relationship("SafetyCheck", back_populates="equipment", lazy="joined")
    safety_alerts = relationship("SafetyAlert", back_populates="equipment", lazy="joined")
    maintenance_records = relationship("EquipmentMaintenance", back_populates="equipment", lazy="joined")
    
    __mapper_args__ = {
        'polymorphic_identity': 'equipment',
        'inherit_condition': EquipmentBase.id == id
    }
    
    def __repr__(self):
        return f"<Equipment {self.name} - {self.type}>"

class EquipmentCreate(BaseModel):
    """Pydantic model for creating equipment."""
    __allow_unmapped__ = True
    
    name: str
    description: Optional[str] = None
    status: EquipmentStatus
    quantity: int
    location: str
    last_maintenance_date: Optional[datetime] = None
    next_maintenance_date: Optional[datetime] = None
    notes: Optional[str] = None

class EquipmentUpdate(BaseModel):
    """Pydantic model for updating equipment."""
    __allow_unmapped__ = True
    
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[EquipmentStatus] = None
    quantity: Optional[int] = None
    location: Optional[str] = None
    last_maintenance_date: Optional[datetime] = None
    next_maintenance_date: Optional[datetime] = None
    notes: Optional[str] = None

class EquipmentResponse(BaseModel):
    """Pydantic model for equipment responses."""
    __allow_unmapped__ = True
    
    id: int
    name: str
    description: Optional[str] = None
    status: EquipmentStatus
    quantity: int
    location: str
    last_maintenance_date: Optional[datetime] = None
    next_maintenance_date: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class EquipmentMaintenance(SharedBase):
    """Model for tracking equipment maintenance records."""
    __tablename__ = 'equipment_maintenance'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(Integer, ForeignKey('equipment.id'), nullable=False)
    maintenance_type = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    performed_by = Column(String(100), nullable=False)
    cost = Column(Float)
    notes = Column(Text)

    # Relationships
    equipment = relationship('Equipment', back_populates='maintenance_records')

class RiskAssessment(SharedBase):
    """Model for tracking risk assessments."""
    __tablename__ = "risk_assessments"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("safety_incidents.id"), nullable=False)
    risk_level = Column(String(20), default="LOW")
    assessment_date = Column(DateTime, nullable=False)
    assessed_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    mitigation_plan = Column(Text)
    follow_up_date = Column(DateTime)
    
    # Relationships
    incident = relationship("SafetyIncident", back_populates="risk_assessments")
    assessor = relationship("User", back_populates="conducted_risk_assessments")

class RiskAssessmentCreate(BaseModel):
    """Pydantic model for creating risk assessments."""
    __allow_unmapped__ = True
    
    activity_id: int
    risk_level: str
    factors: str
    mitigation_measures: str
    environmental_conditions: Optional[str] = None
    equipment_status: Optional[str] = None
    student_health_considerations: Optional[str] = None
    weather_conditions: Optional[str] = None

class RiskAssessmentUpdate(BaseModel):
    """Pydantic model for updating risk assessments."""
    __allow_unmapped__ = True
    
    activity_id: Optional[int] = None
    risk_level: Optional[str] = None
    factors: Optional[str] = None
    mitigation_measures: Optional[str] = None
    environmental_conditions: Optional[str] = None
    equipment_status: Optional[str] = None
    student_health_considerations: Optional[str] = None
    weather_conditions: Optional[str] = None

class RiskAssessmentResponse(BaseModel):
    """Pydantic model for risk assessment responses."""
    __allow_unmapped__ = True
    
    id: int
    activity_id: int
    risk_level: str
    factors: str
    mitigation_measures: str
    environmental_conditions: Optional[str] = None
    equipment_status: Optional[str] = None
    student_health_considerations: Optional[str] = None
    weather_conditions: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class SafetyCheck(SharedBase):
    """Model for tracking safety checks."""
    __tablename__ = "safety_checks"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=False)
    check_date = Column(DateTime, nullable=False)
    checked_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    performed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(String(20), default="PASS")
    notes = Column(Text)
    
    # Relationships
    equipment = relationship("Equipment", back_populates="safety_checks")
    checker = relationship("User", back_populates="conducted_checks", foreign_keys="[SafetyCheck.checked_by]")
    performer = relationship("User", back_populates="performed_checks", foreign_keys="[SafetyCheck.performed_by]")

class SafetyCheckCreate(BaseModel):
    """Pydantic model for creating safety checks."""
    __allow_unmapped__ = True
    
    equipment_id: str
    check_date: datetime
    checked_by: str
    status: str = "PASS"
    notes: Optional[str] = None

class SafetyCheckUpdate(BaseModel):
    """Pydantic model for updating safety checks."""
    __allow_unmapped__ = True
    
    equipment_id: Optional[str] = None
    check_date: Optional[datetime] = None
    checked_by: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None

class SafetyCheckResponse(BaseModel):
    """Pydantic model for safety check responses."""
    __allow_unmapped__ = True
    
    id: str
    equipment_id: str
    check_date: datetime
    checked_by: str
    status: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class EnvironmentalCheck(SharedBase):
    """Model for tracking environmental safety checks."""
    __tablename__ = "physical_education_environmental_checks"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("physical_education_classes.id"), nullable=False)
    check_date = Column(DateTime, nullable=False)
    checked_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    temperature = Column(Float)
    humidity = Column(Float)
    air_quality = Column(String(20))
    lighting_conditions = Column(String(20))
    surface_condition = Column(String(20))
    weather_conditions = Column(String(20))
    status = Column(String(20), default="PASS")
    notes = Column(Text)
    
    # Relationships
    class_ = relationship("PhysicalEducationClass", back_populates="environmental_checks")
    checker = relationship("User", back_populates="conducted_environmental_checks")

class EnvironmentalCheckCreate(BaseModel):
    """Pydantic model for creating environmental checks."""
    __allow_unmapped__ = True
    
    class_id: str
    check_date: datetime
    checked_by: str
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    air_quality: Optional[str] = None
    lighting_conditions: Optional[str] = None
    surface_condition: Optional[str] = None
    weather_conditions: Optional[str] = None
    status: str = "PASS"
    notes: Optional[str] = None

class EnvironmentalCheckUpdate(BaseModel):
    """Pydantic model for updating environmental checks."""
    __allow_unmapped__ = True
    
    class_id: Optional[str] = None
    check_date: Optional[datetime] = None
    checked_by: Optional[str] = None
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    air_quality: Optional[str] = None
    lighting_conditions: Optional[str] = None
    surface_condition: Optional[str] = None
    weather_conditions: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None

class EnvironmentalCheckResponse(BaseModel):
    """Pydantic model for environmental check responses."""
    __allow_unmapped__ = True
    
    id: str
    class_id: str
    check_date: datetime
    checked_by: str
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    air_quality: Optional[str] = None
    lighting_conditions: Optional[str] = None
    surface_condition: Optional[str] = None
    weather_conditions: Optional[str] = None
    status: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class SafetyProtocol(SharedBase):
    """Model for safety protocols and procedures."""
    __tablename__ = "safety_protocols"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)
    requirements = Column(Text, nullable=False)
    procedures = Column(Text, nullable=False)
    emergency_contacts = Column(Text)
    is_active = Column(Boolean, default=True)
    last_reviewed = Column(DateTime)
    reviewed_by = Column(Integer, ForeignKey("users.id"))
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    reviewer = relationship("User", back_populates="reviewed_protocols", foreign_keys="[SafetyProtocol.reviewed_by]")
    creator = relationship("User", back_populates="created_protocols", foreign_keys="[SafetyProtocol.created_by]")
    incidents = relationship("SafetyIncident", back_populates="protocol")

class SafetyAlert(SharedBase):
    """Model for safety alerts."""
    __tablename__ = "physical_education_safety_alerts"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    alert_type = Column(String(50), nullable=False)
    severity = Column(String(20), default="LOW")
    message = Column(Text, nullable=False)
    recipients = Column(Text, nullable=False)  # JSON string of recipient IDs
    activity_id = Column(Integer, ForeignKey('activities.id'))
    equipment_id = Column(Integer, ForeignKey('equipment.id'))
    created_by = Column(Integer, ForeignKey("users.id"))
    resolved_at = Column(DateTime)
    resolution_notes = Column(Text)
    
    # Relationships
    activity = relationship("app.models.physical_education.activity.models.Activity", back_populates="safety_alerts")
    equipment = relationship("Equipment", back_populates="safety_alerts")
    creator = relationship("User", back_populates="created_alerts")

class SafetyAlertCreate(BaseModel):
    """Pydantic model for creating safety alerts."""
    __allow_unmapped__ = True
    
    alert_type: str
    severity: str
    message: str
    recipients: List[int]
    activity_id: Optional[int] = None
    equipment_id: Optional[int] = None
    created_by: Optional[int] = None

class SafetyAlertUpdate(BaseModel):
    """Pydantic model for updating safety alerts."""
    __allow_unmapped__ = True
    
    alert_type: Optional[str] = None
    severity: Optional[str] = None
    message: Optional[str] = None
    recipients: Optional[List[int]] = None
    activity_id: Optional[int] = None
    equipment_id: Optional[int] = None
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None

class SafetyAlertResponse(BaseModel):
    """Pydantic model for safety alert responses."""
    __allow_unmapped__ = True
    
    id: int
    alert_type: str
    severity: str
    message: str
    recipients: List[int]
    activity_id: Optional[int] = None
    equipment_id: Optional[int] = None
    created_by: Optional[int] = None
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True) 