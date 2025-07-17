from typing import List, Optional
from fastapi import Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.physical_education.safety import (
    SafetyIncident,
    RiskAssessment,
    SafetyCheck
)
from app.services.physical_education.safety_manager import SafetyManager
from app.services.physical_education.safety_incident_manager import SafetyIncidentManager
from app.services.physical_education.equipment_manager import EquipmentManager

class SafetyService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
        self.safety_manager = SafetyManager(db)
        self.safety_incident_manager = SafetyIncidentManager(db)
        self.equipment_manager = EquipmentManager(db)

    async def create_risk_assessment(
        self,
        class_id: str,
        activity_type: str,
        environment: str,
        risk_level: str,
        environmental_risks: List[dict],
        student_risks: List[dict],
        activity_risks: List[dict],
        mitigation_strategies: List[dict],
        assessment_metadata: Optional[dict] = None
    ) -> RiskAssessment:
        """Create a new risk assessment."""
        return await self.safety_manager.create_risk_assessment(
            class_id=class_id,
            activity_type=activity_type,
            environment=environment,
            risk_level=risk_level,
            environmental_risks=environmental_risks,
            student_risks=student_risks,
            activity_risks=activity_risks,
            mitigation_strategies=mitigation_strategies,
            assessment_metadata=assessment_metadata
        )

    async def get_risk_assessment(self, assessment_id: str) -> Optional[RiskAssessment]:
        """Get a risk assessment by ID."""
        return await self.safety_manager.get_risk_assessment(assessment_id)

    async def update_risk_assessment(
        self,
        assessment_id: str,
        **kwargs
    ) -> Optional[RiskAssessment]:
        """Update a risk assessment."""
        return await self.safety_manager.update_risk_assessment(assessment_id, **kwargs)

    async def delete_risk_assessment(self, assessment_id: str) -> bool:
        """Delete a risk assessment."""
        return await self.safety_manager.delete_risk_assessment(assessment_id)

    async def create_safety_incident(
        self,
        student_id: str,
        activity_id: str,
        incident_type: str,
        severity: str,
        description: str,
        action_taken: str,
        incident_metadata: Optional[dict] = None
    ) -> SafetyIncident:
        """Create a new safety incident."""
        return await self.safety_incident_manager.create_safety_incident(
            student_id=student_id,
            activity_id=activity_id,
            incident_type=incident_type,
            severity=severity,
            description=description,
            action_taken=action_taken,
            incident_metadata=incident_metadata
        )

    async def get_safety_incident(self, incident_id: str) -> Optional[SafetyIncident]:
        """Get a safety incident by ID."""
        return await self.safety_incident_manager.get_safety_incident(incident_id)

    async def update_safety_incident(
        self,
        incident_id: str,
        **kwargs
    ) -> Optional[SafetyIncident]:
        """Update a safety incident."""
        return await self.safety_incident_manager.update_safety_incident(incident_id, **kwargs)

    async def delete_safety_incident(self, incident_id: str) -> bool:
        """Delete a safety incident."""
        return await self.safety_incident_manager.delete_safety_incident(incident_id)

    async def create_equipment_check(
        self,
        class_id: str,
        equipment_id: str,
        maintenance_status: bool,
        damage_status: bool,
        age_status: bool,
        last_maintenance: Optional[str] = None,
        purchase_date: Optional[str] = None,
        max_age_years: Optional[float] = None,
        equipment_metadata: Optional[dict] = None
    ) -> SafetyCheck:
        """Create a new equipment check."""
        return await self.equipment_manager.create_equipment_check(
            class_id=class_id,
            equipment_id=equipment_id,
            maintenance_status=maintenance_status,
            damage_status=damage_status,
            age_status=age_status,
            last_maintenance=last_maintenance,
            purchase_date=purchase_date,
            max_age_years=max_age_years,
            equipment_metadata=equipment_metadata
        )

    async def get_equipment_check(self, check_id: str) -> Optional[SafetyCheck]:
        """Get an equipment check by ID."""
        return await self.equipment_manager.get_equipment_check(check_id)

    async def update_equipment_check(
        self,
        check_id: str,
        **kwargs
    ) -> Optional[SafetyCheck]:
        """Update an equipment check."""
        return await self.equipment_manager.update_equipment_check(check_id, **kwargs)

    async def delete_equipment_check(self, check_id: str) -> bool:
        """Delete an equipment check."""
        return await self.equipment_manager.delete_equipment_check(check_id)

def get_safety_service(db: Session = Depends(get_db)) -> SafetyService:
    """Dependency injection for SafetyService."""
    return SafetyService(db) 