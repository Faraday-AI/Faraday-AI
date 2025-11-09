"""
Beta Safety Service
Provides safety management for beta teachers (lesson plan safety, resource safety, etc.)
Independent from district-level safety management.
"""

from typing import Dict, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from fastapi import HTTPException, status

from app.dashboard.services.safety_service import SafetyService
from app.models.physical_education.safety.models import (
    SafetyProtocol,
    EmergencyProcedure,
    RiskAssessment,
    SafetyIncident
)
from app.models.teacher_registration import TeacherRegistration
from app.models.lesson_plan.models import LessonPlan
from app.models.core.user import User


class BetaSafetyService(SafetyService):
    """Safety service for beta teachers - filters to teacher's context."""
    
    def __init__(self, db: Session, teacher_id):
        """
        Initialize beta safety service.
        
        Args:
            db: Database session
            teacher_id: TeacherRegistration UUID or User ID (integer)
        """
        super().__init__(db)
        self.teacher_id = teacher_id
        # Map beta teacher UUID to User ID if needed
        # SafetyProtocol.created_by expects Integer (users.id), not UUID
        self.user_id = self._get_user_id(teacher_id)
    
    def _get_user_id(self, teacher_id) -> int:
        """
        Get User ID for beta teacher.
        If teacher_id is UUID, find User by email matching TeacherRegistration.
        If teacher_id is already an integer, return it.
        """
        from uuid import UUID as UUIDType
        
        # If already an integer, return it
        if isinstance(teacher_id, int):
            return teacher_id
        
        # If UUID, find TeacherRegistration and then User by email
        try:
            if isinstance(teacher_id, (str, UUIDType)):
                teacher_reg = self.db.query(TeacherRegistration).filter(
                    TeacherRegistration.id == teacher_id
                ).first()
                if teacher_reg:
                    # Find User with matching email
                    user = self.db.query(User).filter(
                        User.email == teacher_reg.email
                    ).first()
                    if user:
                        return user.id
                    # If no User exists, create one
                    user = User(
                        email=teacher_reg.email,
                        hashed_password=teacher_reg.password_hash,
                        full_name=f"{teacher_reg.first_name} {teacher_reg.last_name}",
                        is_active=teacher_reg.is_active
                    )
                    self.db.add(user)
                    self.db.flush()
                    return user.id
        except Exception:
            pass
        
        # Fallback: return as-is (will cause error if used as created_by)
        return teacher_id
    
    async def get_safety_protocols(self) -> List[Dict]:
        """Get safety protocols for this beta teacher's context."""
        try:
            # Use user_id (Integer) for created_by, not teacher_id (UUID)
            protocols = self.db.query(SafetyProtocol).filter(
                SafetyProtocol.is_active == True,
                SafetyProtocol.created_by == self.user_id
            ).all()
            return [self._protocol_to_dict(p) for p in protocols]
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving safety protocols: {str(e)}"
            )
    
    async def get_emergency_procedures(self) -> List[Dict]:
        """Get emergency procedures for this beta teacher's context."""
        try:
            # Use user_id (Integer) for created_by
            procedures = self.db.query(EmergencyProcedure).filter(
                EmergencyProcedure.is_active == True,
                EmergencyProcedure.created_by == self.user_id
            ).all()
            return [self._procedure_to_dict(p) for p in procedures]
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving emergency procedures: {str(e)}"
            )
    
    async def get_risk_assessments(self) -> List[Dict]:
        """Get risk assessments for this beta teacher's context."""
        try:
            # Use user_id (Integer) for assessed_by
            assessments = self.db.query(RiskAssessment).filter(
                RiskAssessment.assessed_by == self.user_id
            ).all()
            return [self._risk_assessment_to_dict(a) for a in assessments]
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving risk assessments: {str(e)}"
            )
    
    async def get_incident_reports(self) -> List[Dict]:
        """Get incident reports for this beta teacher's context."""
        try:
            # Use user_id (Integer) for teacher_id, not teacher_id (UUID)
            incidents = self.db.query(SafetyIncident).filter(
                SafetyIncident.teacher_id == self.user_id
            ).all()
            return [self._incident_to_dict(i) for i in incidents]
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving incident reports: {str(e)}"
            )
    
    async def create_safety_protocol(self, protocol: Dict) -> Dict:
        """Create a new safety protocol for beta teacher."""
        # Ensure created_by is set to user_id (Integer), not teacher_id (UUID)
        protocol['created_by'] = self.user_id
        return await super().create_safety_protocol(protocol)
    
    async def create_emergency_procedure(self, procedure: Dict) -> Dict:
        """Create a new emergency procedure for beta teacher."""
        # Ensure created_by is set to user_id (Integer)
        procedure['created_by'] = self.user_id
        return await super().create_emergency_procedure(procedure)
    
    async def create_risk_assessment(self, assessment: Dict) -> Dict:
        """Create a new risk assessment for beta teacher."""
        # Use user_id (Integer) for assessed_by
        assessment['assessed_by'] = self.user_id
        return await super().create_risk_assessment(assessment)
    
    async def create_incident_report(self, incident: Dict) -> Dict:
        """Create a new incident report for beta teacher."""
        # SafetyIncident.teacher_id is Integer (users.id), not UUID
        incident['teacher_id'] = self.user_id
        return await super().create_incident_report(incident)

