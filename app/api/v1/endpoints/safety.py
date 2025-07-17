from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.physical_education.pe_enums.pe_types import (
    SafetyType,
    SafetyLevel,
    SafetyStatus,
    SafetyTrigger,
    IncidentType,
    IncidentLevel,
    IncidentStatus,
    IncidentTrigger,
    RiskType,
    RiskLevel,
    RiskStatus,
    RiskTrigger,
    AlertType
)
from app.services.physical_education.safety_manager import SafetyManager
from app.schemas.safety import (
    RiskAssessmentCreate,
    RiskAssessmentResponse,
    SafetyIncidentCreate,
    SafetyIncidentResponse,
    SafetyAlertCreate,
    SafetyAlertResponse,
    SafetyProtocolCreate,
    SafetyProtocolResponse
)

router = APIRouter()

@router.post("/risk-assessments", response_model=RiskAssessmentResponse)
async def create_risk_assessment(
    assessment: RiskAssessmentCreate,
    db: Session = Depends(get_db)
):
    """Create a new risk assessment."""
    safety_manager = SafetyManager(db)
    return await safety_manager.create_risk_assessment(
        activity_id=assessment.activity_id,
        risk_level=assessment.risk_level,
        factors=assessment.factors,
        mitigation_measures=assessment.mitigation_measures,
        environmental_conditions=assessment.environmental_conditions,
        equipment_status=assessment.equipment_status,
        student_health_considerations=assessment.student_health_considerations,
        weather_conditions=assessment.weather_conditions,
        assessed_by=assessment.assessed_by
    )

@router.get("/risk-assessments/{activity_id}", response_model=Optional[RiskAssessmentResponse])
async def get_risk_assessment(
    activity_id: int,
    db: Session = Depends(get_db)
):
    """Get the latest risk assessment for an activity."""
    safety_manager = SafetyManager(db)
    return await safety_manager.get_risk_assessment(activity_id)

@router.post("/incidents", response_model=SafetyIncidentResponse)
async def report_incident(
    incident: SafetyIncidentCreate,
    db: Session = Depends(get_db)
):
    """Report a new safety incident."""
    safety_manager = SafetyManager(db)
    return await safety_manager.report_incident(
        activity_id=incident.activity_id,
        incident_type=incident.incident_type,
        severity=incident.severity,
        description=incident.description,
        response_taken=incident.response_taken,
        reported_by=incident.reported_by,
        student_id=incident.student_id,
        location=incident.location,
        equipment_involved=incident.equipment_involved,
        witnesses=incident.witnesses,
        follow_up_required=incident.follow_up_required
    )

@router.get("/incidents/{incident_id}", response_model=Optional[SafetyIncidentResponse])
async def get_incident(
    incident_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific safety incident."""
    safety_manager = SafetyManager(db)
    return await safety_manager.get_incident(incident_id)

@router.get("/activities/{activity_id}/incidents", response_model=List[SafetyIncidentResponse])
async def get_activity_incidents(
    activity_id: int,
    db: Session = Depends(get_db)
):
    """Get all incidents for an activity."""
    safety_manager = SafetyManager(db)
    return await safety_manager.get_activity_incidents(activity_id)

@router.post("/alerts", response_model=SafetyAlertResponse)
async def create_alert(
    alert: SafetyAlertCreate,
    db: Session = Depends(get_db)
):
    """Create a new safety alert."""
    safety_manager = SafetyManager(db)
    return await safety_manager.create_alert(
        alert_type=alert.alert_type,
        severity=alert.severity,
        message=alert.message,
        recipients=alert.recipients,
        activity_id=alert.activity_id,
        equipment_id=alert.equipment_id,
        created_by=alert.created_by
    )

@router.put("/alerts/{alert_id}/resolve", response_model=SafetyAlertResponse)
async def resolve_alert(
    alert_id: int,
    resolution_notes: str,
    db: Session = Depends(get_db)
):
    """Resolve a safety alert."""
    safety_manager = SafetyManager(db)
    return await safety_manager.resolve_alert(alert_id, resolution_notes)

@router.get("/alerts/active", response_model=List[SafetyAlertResponse])
async def get_active_alerts(
    db: Session = Depends(get_db)
):
    """Get all unresolved safety alerts."""
    safety_manager = SafetyManager(db)
    return await safety_manager.get_active_alerts()

@router.post("/protocols", response_model=SafetyProtocolResponse)
async def create_safety_protocol(
    protocol: SafetyProtocolCreate,
    db: Session = Depends(get_db)
):
    """Create a new safety protocol."""
    safety_manager = SafetyManager(db)
    return await safety_manager.create_safety_protocol(
        name=protocol.name,
        description=protocol.description,
        protocol_type=protocol.protocol_type,
        steps=protocol.steps,
        activity_type=protocol.activity_type,
        required_equipment=protocol.required_equipment,
        emergency_contacts=protocol.emergency_contacts,
        created_by=protocol.created_by
    )

@router.get("/protocols/{protocol_id}", response_model=Optional[SafetyProtocolResponse])
async def get_protocol(
    protocol_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific safety protocol."""
    safety_manager = SafetyManager(db)
    return await safety_manager.get_protocol(protocol_id)

@router.get("/protocols/activity/{activity_type}", response_model=List[SafetyProtocolResponse])
async def get_activity_protocols(
    activity_type: str,
    db: Session = Depends(get_db)
):
    """Get all protocols for an activity type."""
    safety_manager = SafetyManager(db)
    return await safety_manager.get_activity_protocols(activity_type)

@router.put("/protocols/{protocol_id}/review", response_model=SafetyProtocolResponse)
async def update_protocol_review(
    protocol_id: int,
    db: Session = Depends(get_db)
):
    """Update the review dates for a protocol."""
    safety_manager = SafetyManager(db)
    return await safety_manager.update_protocol_review(protocol_id) 