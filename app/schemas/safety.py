from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel

from app.models.physical_education.pe_enums.pe_types import (
    RiskLevel,
    IncidentSeverity,
    IncidentType,
    AlertType,
    CheckType
)

# Risk Assessment Schemas
class RiskAssessmentBase(BaseModel):
    activity_id: int
    risk_level: RiskLevel
    factors: List[str]
    mitigation_measures: List[str]
    environmental_conditions: Optional[Dict[str, Any]] = None
    equipment_status: Optional[Dict[str, Any]] = None
    student_health_considerations: Optional[Dict[str, Any]] = None
    weather_conditions: Optional[Dict[str, Any]] = None
    assessed_by: Optional[int] = None

class RiskAssessmentCreate(RiskAssessmentBase):
    pass

class RiskAssessmentResponse(RiskAssessmentBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Safety Incident Schemas
class SafetyIncidentBase(BaseModel):
    activity_id: int
    student_id: Optional[int] = None
    incident_type: IncidentType
    severity: IncidentSeverity
    description: str
    response_taken: str
    reported_by: int
    location: Optional[str] = None
    equipment_involved: Optional[Dict[str, Any]] = None
    witnesses: Optional[List[str]] = None
    follow_up_required: Optional[bool] = None

class SafetyIncidentCreate(SafetyIncidentBase):
    pass

class SafetyIncidentResponse(SafetyIncidentBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Safety Alert Schemas
class SafetyAlertBase(BaseModel):
    alert_type: AlertType
    severity: IncidentSeverity
    message: str
    recipients: List[int]
    activity_id: Optional[int] = None
    equipment_id: Optional[int] = None
    created_by: Optional[int] = None

class SafetyAlertCreate(SafetyAlertBase):
    pass

class SafetyAlertResponse(SafetyAlertBase):
    id: int
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Safety Protocol Schemas
class SafetyProtocolBase(BaseModel):
    name: str
    description: str
    protocol_type: str
    steps: List[str]
    activity_type: str
    required_equipment: Optional[List[str]] = None
    emergency_contacts: Optional[List[Dict[str, str]]] = None
    created_by: int

class SafetyProtocolCreate(SafetyProtocolBase):
    pass

class SafetyProtocolResponse(SafetyProtocolBase):
    id: int
    created_at: datetime
    updated_at: datetime
    last_reviewed_at: Optional[datetime] = None
    next_review_due: Optional[datetime] = None

    class Config:
        from_attributes = True 