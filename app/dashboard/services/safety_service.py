"""
Safety Service

This module provides the service layer for the Safety Panel in the Physical Education Dashboard,
handling safety protocols, emergency procedures, risk assessments, and incident reports.
"""

from typing import Dict, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from fastapi import HTTPException, status

from app.models.physical_education.safety.models import (
    SafetyProtocol,
    EmergencyProcedure,
    RiskAssessment,
    SafetyIncident
)
from app.models.skill_assessment.safety.safety import (
    SafetyProtocol as SkillAssessmentSafetyProtocol,
    SkillAssessmentSafetyIncident,
    RiskAssessment as SkillAssessmentRiskAssessment
)

class SafetyService:
    def __init__(self, db: Session):
        self.db = db
        # Set query timeout to prevent hanging queries (30 seconds)
        try:
            self.db.execute(text("SET statement_timeout = '30s'"))
        except:
            pass  # Ignore if not supported
    
    def _safe_commit(self, max_retries=3):
        """Commit with timeout and deadlock protection.
        
        Retries on deadlock errors with exponential backoff.
        Uses flush() if commit fails (e.g., in SAVEPOINT transactions).
        """
        import time
        from sqlalchemy.exc import OperationalError
        
        for attempt in range(max_retries):
            try:
                self.db.commit()
                return  # Success
            except OperationalError as op_error:
                error_str = str(op_error).lower()
                # Check for deadlock
                if "deadlock" in error_str or "deadlock_detected" in error_str:
                    if attempt < max_retries - 1:
                        # Exponential backoff: 0.1s, 0.2s, 0.4s
                        time.sleep(0.1 * (2 ** attempt))
                        # Rollback and retry
                        try:
                            self.db.rollback()
                        except:
                            pass
                        continue
                    else:
                        # Final attempt failed - use flush() as fallback for SAVEPOINT transactions
                        try:
                            self.db.flush()
                            return
                        except Exception as flush_error:
                            self.db.rollback()
                            raise HTTPException(
                                status_code=status.HTTP_409_CONFLICT,
                                detail="Database deadlock detected. Please try again."
                            )
                else:
                    # Not a deadlock, re-raise
                    self.db.rollback()
                    raise
            except Exception as commit_error:
                error_str = str(commit_error).lower()
                # Check if it's a timeout error
                if "timeout" in error_str or "canceled" in error_str:
                    self.db.rollback()
                    raise HTTPException(
                        status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                        detail="Operation timed out. Please try again."
                    )
                # Check for deadlock in other exception types
                if "deadlock" in error_str:
                    if attempt < max_retries - 1:
                        time.sleep(0.1 * (2 ** attempt))
                        try:
                            self.db.rollback()
                        except:
                            pass
                        continue
                    else:
                        # Final attempt - try flush() as fallback
                        try:
                            self.db.flush()
                            return
                        except Exception as flush_error:
                            self.db.rollback()
                            raise HTTPException(
                                status_code=status.HTTP_409_CONFLICT,
                                detail="Database deadlock detected. Please try again."
                            )
                # Other errors - rollback and raise
                self.db.rollback()
                raise
    
    def _get_emergency_procedure_optimized(self, procedure_id: int):
        """Get emergency procedure with optimized query to avoid relationship loading."""
        # Set statement timeout for this query
        try:
            self.db.execute(text("SET LOCAL statement_timeout = '10s'"))
        except:
            pass
        # Use with_entities to only load needed columns, avoiding relationship loading
        result = self.db.query(EmergencyProcedure).with_entities(
            EmergencyProcedure.id,
            EmergencyProcedure.name,
            EmergencyProcedure.description,
            EmergencyProcedure.procedure_type,
            EmergencyProcedure.class_id,
            EmergencyProcedure.steps,
            EmergencyProcedure.contact_info,
            EmergencyProcedure.is_active,
            EmergencyProcedure.last_drill_date,
            EmergencyProcedure.next_drill_date,
            EmergencyProcedure.created_by,
            EmergencyProcedure.created_at,
            EmergencyProcedure.updated_at
        ).filter(EmergencyProcedure.id == procedure_id).first()
        
        if result:
            # Create a minimal object with the needed attributes
            class MinimalProcedure:
                def __init__(self, id, name, description, procedure_type, class_id, steps, 
                           contact_info, is_active, last_drill_date, next_drill_date, 
                           created_by, created_at, updated_at):
                    self.id = id
                    self.name = name
                    self.description = description
                    self.procedure_type = procedure_type
                    self.class_id = class_id
                    self.steps = steps
                    self.contact_info = contact_info
                    self.is_active = is_active
                    self.last_drill_date = last_drill_date
                    self.next_drill_date = next_drill_date
                    self.created_by = created_by
                    self.created_at = created_at
                    self.updated_at = updated_at
            
            return MinimalProcedure(*result)
        return None
    
    def _get_risk_assessment_optimized(self, assessment_id: int):
        """Get risk assessment with optimized query to avoid relationship loading."""
        # Set statement timeout for this query
        try:
            self.db.execute(text("SET LOCAL statement_timeout = '10s'"))
        except:
            pass
        # Use with_entities to only load needed columns
        result = self.db.query(RiskAssessment).with_entities(
            RiskAssessment.id,
            RiskAssessment.incident_id,
            RiskAssessment.class_id,
            RiskAssessment.activity_id,
            RiskAssessment.activity_type,
            RiskAssessment.environment,
            RiskAssessment.risk_level,
            RiskAssessment.assessment_date,
            RiskAssessment.assessed_by,
            RiskAssessment.environmental_risks,
            RiskAssessment.student_risks,
            RiskAssessment.activity_risks,
            RiskAssessment.mitigation_plan,
            RiskAssessment.mitigation_strategies,
            RiskAssessment.follow_up_date
        ).filter(RiskAssessment.id == assessment_id).first()
        
        if result:
            class MinimalAssessment:
                def __init__(self, id, incident_id, class_id, activity_id, activity_type, 
                           environment, risk_level, assessment_date, assessed_by,
                           environmental_risks, student_risks, activity_risks,
                           mitigation_plan, mitigation_strategies, follow_up_date):
                    self.id = id
                    self.incident_id = incident_id
                    self.class_id = class_id
                    self.activity_id = activity_id
                    self.activity_type = activity_type
                    self.environment = environment
                    self.risk_level = risk_level
                    self.assessment_date = assessment_date
                    self.assessed_by = assessed_by
                    self.environmental_risks = environmental_risks
                    self.student_risks = student_risks
                    self.activity_risks = activity_risks
                    self.mitigation_plan = mitigation_plan
                    self.mitigation_strategies = mitigation_strategies
                    self.follow_up_date = follow_up_date
            
            return MinimalAssessment(*result)
        return None
    
    def _get_safety_incident_optimized(self, incident_id: int):
        """Get safety incident with optimized query to avoid relationship loading."""
        # Set statement timeout for this query
        try:
            self.db.execute(text("SET LOCAL statement_timeout = '10s'"))
        except:
            pass
        # Use with_entities to only load needed columns
        result = self.db.query(SafetyIncident).with_entities(
            SafetyIncident.id,
            SafetyIncident.student_id,
            SafetyIncident.activity_id,
            SafetyIncident.protocol_id,
            SafetyIncident.incident_date,
            SafetyIncident.incident_type,
            SafetyIncident.severity,
            SafetyIncident.description,
            SafetyIncident.location,
            SafetyIncident.teacher_id,
            SafetyIncident.equipment_id,
            SafetyIncident.action_taken,
            SafetyIncident.follow_up_required,
            SafetyIncident.follow_up_notes,
            SafetyIncident.incident_metadata
        ).filter(SafetyIncident.id == incident_id).first()
        
        if result:
            class MinimalIncident:
                def __init__(self, id, student_id, activity_id, protocol_id, incident_date,
                           incident_type, severity, description, location, teacher_id,
                           equipment_id, action_taken, follow_up_required, follow_up_notes,
                           incident_metadata):
                    self.id = id
                    self.student_id = student_id
                    self.activity_id = activity_id
                    self.protocol_id = protocol_id
                    self.incident_date = incident_date
                    self.incident_type = incident_type
                    self.severity = severity
                    self.description = description
                    self.location = location
                    self.teacher_id = teacher_id
                    self.equipment_id = equipment_id
                    self.action_taken = action_taken
                    self.follow_up_required = follow_up_required
                    self.follow_up_notes = follow_up_notes
                    self.incident_metadata = incident_metadata
            
            return MinimalIncident(*result)
        return None

    # Safety Protocols CRUD
    
    async def get_safety_protocols(self) -> List[Dict]:
        """Get all safety protocols."""
        try:
            protocols = self.db.query(SafetyProtocol).filter(
                SafetyProtocol.is_active == True
            ).all()
            return [self._protocol_to_dict(p) for p in protocols]
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving safety protocols: {str(e)}"
            )

    async def create_safety_protocol(self, protocol: Dict) -> Dict:
        """Create a new safety protocol."""
        try:
            # Validate required fields
            required_fields = ['name', 'description', 'category', 'requirements', 'procedures', 'created_by']
            missing_fields = [field for field in required_fields if field not in protocol]
            if missing_fields:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Missing required fields: {', '.join(missing_fields)}"
                )
            
            # Create new protocol
            # Convert emergency_contacts dict to JSON string if it's a dict
            emergency_contacts = protocol.get('emergency_contacts')
            if isinstance(emergency_contacts, dict):
                import json
                emergency_contacts = json.dumps(emergency_contacts)
            
            new_protocol = SafetyProtocol(
                name=protocol['name'],
                description=protocol['description'],
                category=protocol['category'],
                requirements=protocol['requirements'],
                procedures=protocol['procedures'],
                emergency_contacts=emergency_contacts,
                is_active=protocol.get('is_active', True),
                created_by=protocol['created_by'],
                reviewed_by=protocol.get('reviewed_by'),
                last_reviewed=datetime.utcnow() if protocol.get('reviewed_by') else None
            )
            
            self.db.add(new_protocol)
            self.db.flush()  # Flush to get ID before commit
            self.db.commit()
            self.db.refresh(new_protocol)
            
            return self._protocol_to_dict(new_protocol)
        except HTTPException:
            raise
        except IntegrityError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Database integrity error: {str(e)}"
            )
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating safety protocol: {str(e)}"
            )

    async def update_safety_protocol(self, protocol_id: int, protocol: Dict) -> Dict:
        """Update an existing safety protocol."""
        try:
            existing_protocol = self.db.query(SafetyProtocol).filter(
                SafetyProtocol.id == protocol_id
            ).first()
            
            if not existing_protocol:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Safety protocol with id {protocol_id} not found"
                )
            
            # Update fields
            if 'name' in protocol:
                existing_protocol.name = protocol['name']
            if 'description' in protocol:
                existing_protocol.description = protocol['description']
            if 'category' in protocol:
                existing_protocol.category = protocol['category']
            if 'requirements' in protocol:
                existing_protocol.requirements = protocol['requirements']
            if 'procedures' in protocol:
                existing_protocol.procedures = protocol['procedures']
            if 'emergency_contacts' in protocol:
                existing_protocol.emergency_contacts = protocol['emergency_contacts']
            if 'is_active' in protocol:
                existing_protocol.is_active = protocol['is_active']
            if 'reviewed_by' in protocol:
                existing_protocol.reviewed_by = protocol['reviewed_by']
                existing_protocol.last_reviewed = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(existing_protocol)
            
            return self._protocol_to_dict(existing_protocol)
        except HTTPException:
            raise
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error updating safety protocol: {str(e)}"
            )

    async def delete_safety_protocol(self, protocol_id: int) -> Dict:
        """Delete a safety protocol (soft delete)."""
        try:
            protocol = self.db.query(SafetyProtocol).filter(
                SafetyProtocol.id == protocol_id
            ).first()
            
            if not protocol:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Safety protocol with id {protocol_id} not found"
                )
            
            # Soft delete - set is_active to False
            protocol.is_active = False
            self.db.commit()
            
            return {"status": "success", "message": f"Safety protocol {protocol_id} deleted successfully"}
        except HTTPException:
            raise
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error deleting safety protocol: {str(e)}"
            )

    # Emergency Procedures CRUD
    
    async def get_emergency_procedures(self) -> List[Dict]:
        """Get all emergency procedures."""
        try:
            # Use with_entities to avoid loading relationships
            results = self.db.query(EmergencyProcedure).with_entities(
                EmergencyProcedure.id,
                EmergencyProcedure.name,
                EmergencyProcedure.description,
                EmergencyProcedure.procedure_type,
                EmergencyProcedure.class_id,
                EmergencyProcedure.steps,
                EmergencyProcedure.contact_info,
                EmergencyProcedure.is_active,
                EmergencyProcedure.last_drill_date,
                EmergencyProcedure.next_drill_date,
                EmergencyProcedure.created_by,
                EmergencyProcedure.created_at,
                EmergencyProcedure.updated_at
            ).filter(EmergencyProcedure.is_active == True).all()
            
            # Create minimal objects and convert to dict
            class MinimalProcedure:
                def __init__(self, id, name, description, procedure_type, class_id, steps, 
                           contact_info, is_active, last_drill_date, next_drill_date, 
                           created_by, created_at, updated_at):
                    self.id = id
                    self.name = name
                    self.description = description
                    self.procedure_type = procedure_type
                    self.class_id = class_id
                    self.steps = steps
                    self.contact_info = contact_info
                    self.is_active = is_active
                    self.last_drill_date = last_drill_date
                    self.next_drill_date = next_drill_date
                    self.created_by = created_by
                    self.created_at = created_at
                    self.updated_at = updated_at
            
            procedures = [MinimalProcedure(*r) for r in results]
            return [self._procedure_to_dict(p) for p in procedures]
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving emergency procedures: {str(e)}"
            )

    async def create_emergency_procedure(self, procedure: Dict) -> Dict:
        """Create a new emergency procedure."""
        try:
            # Validate required fields
            required_fields = ['name', 'description', 'procedure_type', 'steps', 'created_by']
            missing_fields = [field for field in required_fields if field not in procedure]
            if missing_fields:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Missing required fields: {', '.join(missing_fields)}"
                )
            
            # Validate procedure_type
            valid_types = ['fire', 'medical', 'weather', 'security', 'other']
            if procedure['procedure_type'] not in valid_types:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid procedure_type. Must be one of: {', '.join(valid_types)}"
                )
            
            # Validate foreign keys before insert to prevent hangs
            if procedure.get('class_id'):
                class_exists = self.db.execute(
                    text("SELECT 1 FROM physical_education_classes WHERE id = :class_id"),
                    {"class_id": procedure['class_id']}
                ).scalar()
                if not class_exists:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Class ID {procedure['class_id']} does not exist"
                    )
            
            # Validate created_by user exists
            user_exists = self.db.execute(
                text("SELECT 1 FROM users WHERE id = :user_id"),
                {"user_id": procedure['created_by']}
            ).scalar()
            if not user_exists:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"User ID {procedure['created_by']} does not exist"
                )
            
            # Create new procedure
            new_procedure = EmergencyProcedure(
                name=procedure['name'],
                description=procedure['description'],
                procedure_type=procedure['procedure_type'],
                class_id=procedure.get('class_id'),
                steps=procedure['steps'],  # Should be a list
                contact_info=procedure.get('contact_info'),  # Should be a dict
                is_active=procedure.get('is_active', True),
                last_drill_date=procedure.get('last_drill_date'),
                next_drill_date=procedure.get('next_drill_date'),
                created_by=procedure['created_by']
            )
            
            # Get timestamp and build data dict before any database operations
            now = datetime.utcnow()
            
            # Build return dictionary from input data before database operations
            # This avoids any object attribute access that might trigger queries
            procedure_dict = {
                "id": None,  # Will be set after flush
                "name": procedure['name'],
                "description": procedure['description'],
                "procedure_type": procedure['procedure_type'],
                "class_id": procedure.get('class_id'),
                "steps": procedure['steps'],
                "contact_info": procedure.get('contact_info'),
                "is_active": procedure.get('is_active', True),
                "last_drill_date": procedure.get('last_drill_date').isoformat() if procedure.get('last_drill_date') else None,
                "next_drill_date": procedure.get('next_drill_date').isoformat() if procedure.get('next_drill_date') else None,
                "created_by": procedure['created_by'],
                "created_at": now.isoformat(),
                "updated_at": now.isoformat()
            }
            
            self.db.add(new_procedure)
            self.db.flush()  # Flush to get ID
            
            # Only set ID after flush - this is the only attribute we need from the object
            procedure_dict["id"] = new_procedure.id
            
            # Commit with timeout protection
            self._safe_commit()
            
            return procedure_dict
        except HTTPException:
            raise
        except IntegrityError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Database integrity error: {str(e)}"
            )
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating emergency procedure: {str(e)}"
            )

    async def update_emergency_procedure(self, procedure_id: int, procedure: Dict) -> Dict:
        """Update an existing emergency procedure."""
        try:
            # Get current values using optimized query (avoids relationship loading)
            current = self._get_emergency_procedure_optimized(procedure_id)
            
            if not current:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Emergency procedure with id {procedure_id} not found"
                )
            
            # Build update dict
            update_dict = {}
            if 'name' in procedure:
                update_dict['name'] = procedure['name']
            if 'description' in procedure:
                update_dict['description'] = procedure['description']
            if 'procedure_type' in procedure:
                if procedure['procedure_type'] not in ['fire', 'medical', 'weather', 'security', 'other']:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid procedure_type"
                    )
                update_dict['procedure_type'] = procedure['procedure_type']
            if 'class_id' in procedure:
                update_dict['class_id'] = procedure['class_id']
            if 'steps' in procedure:
                update_dict['steps'] = procedure['steps']
            if 'contact_info' in procedure:
                update_dict['contact_info'] = procedure['contact_info']
            if 'is_active' in procedure:
                update_dict['is_active'] = procedure['is_active']
            if 'last_drill_date' in procedure:
                update_dict['last_drill_date'] = procedure['last_drill_date']
            if 'next_drill_date' in procedure:
                update_dict['next_drill_date'] = procedure['next_drill_date']
            
            update_dict['updated_at'] = datetime.utcnow()
            
            # Use bulk update to avoid loading object with relationships
            self.db.query(EmergencyProcedure).filter(
                EmergencyProcedure.id == procedure_id
            ).update(update_dict, synchronize_session=False)
            
            # Build return dict from current + updates
            now = datetime.utcnow()
            procedure_dict = {
                "id": current.id,
                "name": update_dict.get('name', current.name),
                "description": update_dict.get('description', current.description),
                "procedure_type": update_dict.get('procedure_type', current.procedure_type),
                "class_id": update_dict.get('class_id', current.class_id),
                "steps": update_dict.get('steps', current.steps),
                "contact_info": update_dict.get('contact_info', current.contact_info),
                "is_active": update_dict.get('is_active', current.is_active),
                "last_drill_date": (update_dict.get('last_drill_date').isoformat() if update_dict.get('last_drill_date') else None) or (current.last_drill_date.isoformat() if current.last_drill_date else None),
                "next_drill_date": (update_dict.get('next_drill_date').isoformat() if update_dict.get('next_drill_date') else None) or (current.next_drill_date.isoformat() if current.next_drill_date else None),
                "created_by": current.created_by,
                "created_at": current.created_at.isoformat() if current.created_at else now.isoformat(),
                "updated_at": now.isoformat()
            }
            
            self._safe_commit()
            
            return procedure_dict
        except HTTPException:
            raise
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error updating emergency procedure: {str(e)}"
            )

    async def delete_emergency_procedure(self, procedure_id: int) -> Dict:
        """Delete an emergency procedure (soft delete)."""
        try:
            # Check existence with raw SQL to avoid ORM overhead
            try:
                self.db.execute(text("SET LOCAL statement_timeout = '5s'"))
            except:
                pass
            exists = self.db.execute(
                text("SELECT id FROM emergency_procedures WHERE id = :id"),
                {"id": procedure_id}
            ).fetchone()
            
            if not exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Emergency procedure with id {procedure_id} not found"
                )
            
            # Use bulk update for soft delete (avoids loading object with relationships)
            self.db.query(EmergencyProcedure).filter(
                EmergencyProcedure.id == procedure_id
            ).update({
                'is_active': False,
                'updated_at': datetime.utcnow()
            }, synchronize_session=False)
            
            self._safe_commit()
            
            return {"status": "success", "message": f"Emergency procedure {procedure_id} deleted successfully"}
        except HTTPException:
            raise
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error deleting emergency procedure: {str(e)}"
            )

    # Risk Assessments CRUD
    
    async def get_risk_assessments(self) -> List[Dict]:
        """Get all risk assessments."""
        try:
            # Use with_entities to avoid loading relationships
            results = self.db.query(RiskAssessment).with_entities(
                RiskAssessment.id,
                RiskAssessment.incident_id,
                RiskAssessment.class_id,
                RiskAssessment.activity_id,
                RiskAssessment.activity_type,
                RiskAssessment.environment,
                RiskAssessment.risk_level,
                RiskAssessment.assessment_date,
                RiskAssessment.assessed_by,
                RiskAssessment.environmental_risks,
                RiskAssessment.student_risks,
                RiskAssessment.activity_risks,
                RiskAssessment.mitigation_plan,
                RiskAssessment.mitigation_strategies,
                RiskAssessment.follow_up_date
            ).all()
            
            # Create minimal objects and convert to dict
            class MinimalAssessment:
                def __init__(self, id, incident_id, class_id, activity_id, activity_type, 
                           environment, risk_level, assessment_date, assessed_by,
                           environmental_risks, student_risks, activity_risks,
                           mitigation_plan, mitigation_strategies, follow_up_date):
                    self.id = id
                    self.incident_id = incident_id
                    self.class_id = class_id
                    self.activity_id = activity_id
                    self.activity_type = activity_type
                    self.environment = environment
                    self.risk_level = risk_level
                    self.assessment_date = assessment_date
                    self.assessed_by = assessed_by
                    self.environmental_risks = environmental_risks
                    self.student_risks = student_risks
                    self.activity_risks = activity_risks
                    self.mitigation_plan = mitigation_plan
                    self.mitigation_strategies = mitigation_strategies
                    self.follow_up_date = follow_up_date
            
            assessments = [MinimalAssessment(*r) for r in results]
            return [self._risk_assessment_to_dict(a) for a in assessments]
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving risk assessments: {str(e)}"
            )

    async def create_risk_assessment(self, assessment: Dict) -> Dict:
        """Create a new risk assessment."""
        try:
            # Validate required fields
            required_fields = ['activity_id', 'risk_level', 'assessment_date', 'assessed_by']
            missing_fields = [field for field in required_fields if field not in assessment]
            if missing_fields:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Missing required fields: {', '.join(missing_fields)}"
                )
            
            # Create new assessment
            new_assessment = RiskAssessment(
                incident_id=assessment.get('incident_id'),
                class_id=assessment.get('class_id'),
                activity_id=assessment['activity_id'],
                activity_type=assessment.get('activity_type'),
                environment=assessment.get('environment'),
                risk_level=assessment['risk_level'].upper() if assessment.get('risk_level') else "LOW",
                assessment_date=assessment['assessment_date'],
                assessed_by=assessment['assessed_by'],
                environmental_risks=assessment.get('environmental_risks'),
                student_risks=assessment.get('student_risks'),
                activity_risks=assessment.get('activity_risks'),
                mitigation_plan=assessment.get('mitigation_plan'),
                mitigation_strategies=assessment.get('mitigation_strategies'),
                follow_up_date=assessment.get('follow_up_date')
            )
            
            # Build return dict before commit to avoid refresh
            now = datetime.utcnow()
            
            self.db.add(new_assessment)
            self.db.flush()  # Flush to get ID
            
            assessment_dict = {
                "id": new_assessment.id,
                "incident_id": new_assessment.incident_id,
                "class_id": new_assessment.class_id,
                "activity_id": new_assessment.activity_id,
                "activity_type": new_assessment.activity_type,
                "environment": new_assessment.environment,
                "risk_level": new_assessment.risk_level.upper() if hasattr(new_assessment.risk_level, 'upper') else str(new_assessment.risk_level).upper(),
                "assessment_date": new_assessment.assessment_date.isoformat() if hasattr(new_assessment.assessment_date, 'isoformat') else str(new_assessment.assessment_date),
                "assessed_by": new_assessment.assessed_by,
                "environmental_risks": new_assessment.environmental_risks,
                "student_risks": new_assessment.student_risks,
                "activity_risks": new_assessment.activity_risks,
                "mitigation_plan": new_assessment.mitigation_plan,
                "mitigation_strategies": new_assessment.mitigation_strategies,
                "follow_up_date": new_assessment.follow_up_date.isoformat() if new_assessment.follow_up_date and hasattr(new_assessment.follow_up_date, 'isoformat') else (str(new_assessment.follow_up_date) if new_assessment.follow_up_date else None)
            }
            
            # Add timestamp fields only if they exist on the model
            if hasattr(new_assessment, 'created_at'):
                assessment_dict["created_at"] = now.isoformat()
            if hasattr(new_assessment, 'updated_at'):
                assessment_dict["updated_at"] = now.isoformat()
            
            self._safe_commit()
            
            return assessment_dict
        except HTTPException:
            raise
        except IntegrityError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Database integrity error: {str(e)}"
            )
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating risk assessment: {str(e)}"
            )

    async def update_risk_assessment(self, assessment_id: int, assessment: Dict) -> Dict:
        """Update an existing risk assessment."""
        try:
            # Get current values using optimized query
            current = self._get_risk_assessment_optimized(assessment_id)
            
            if not current:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Risk assessment with id {assessment_id} not found"
                )
            
            # Build update dict
            update_dict = {}
            if 'incident_id' in assessment:
                update_dict['incident_id'] = assessment['incident_id']
            if 'class_id' in assessment:
                update_dict['class_id'] = assessment['class_id']
            if 'activity_id' in assessment:
                update_dict['activity_id'] = assessment['activity_id']
            if 'activity_type' in assessment:
                update_dict['activity_type'] = assessment['activity_type']
            if 'environment' in assessment:
                update_dict['environment'] = assessment['environment']
            if 'risk_level' in assessment:
                update_dict['risk_level'] = assessment['risk_level'].upper() if assessment['risk_level'] else "LOW"
            if 'assessment_date' in assessment:
                update_dict['assessment_date'] = assessment['assessment_date']
            if 'assessed_by' in assessment:
                update_dict['assessed_by'] = assessment['assessed_by']
            if 'environmental_risks' in assessment:
                update_dict['environmental_risks'] = assessment['environmental_risks']
            if 'student_risks' in assessment:
                update_dict['student_risks'] = assessment['student_risks']
            if 'activity_risks' in assessment:
                update_dict['activity_risks'] = assessment['activity_risks']
            if 'mitigation_plan' in assessment:
                update_dict['mitigation_plan'] = assessment['mitigation_plan']
            if 'mitigation_strategies' in assessment:
                update_dict['mitigation_strategies'] = assessment['mitigation_strategies']
            if 'follow_up_date' in assessment:
                update_dict['follow_up_date'] = assessment['follow_up_date']
            
            # Use bulk update to avoid loading object with relationships
            if update_dict:
                self.db.query(RiskAssessment).filter(
                    RiskAssessment.id == assessment_id
                ).update(update_dict, synchronize_session=False)
            
            # Build return dict from current + updates
            now = datetime.utcnow()
            assessment_dict = {
                "id": current.id,
                "incident_id": update_dict.get('incident_id', current.incident_id),
                "class_id": update_dict.get('class_id', current.class_id),
                "activity_id": update_dict.get('activity_id', current.activity_id),
                "activity_type": update_dict.get('activity_type', current.activity_type),
                "environment": update_dict.get('environment', current.environment),
                "risk_level": (update_dict.get('risk_level') or current.risk_level).upper() if update_dict.get('risk_level') or current.risk_level else "LOW",
                "assessment_date": (update_dict.get('assessment_date') or current.assessment_date).isoformat() if hasattr(update_dict.get('assessment_date') or current.assessment_date, 'isoformat') else str(update_dict.get('assessment_date') or current.assessment_date),
                "assessed_by": update_dict.get('assessed_by', current.assessed_by),
                "environmental_risks": update_dict.get('environmental_risks', current.environmental_risks),
                "student_risks": update_dict.get('student_risks', current.student_risks),
                "activity_risks": update_dict.get('activity_risks', current.activity_risks),
                "mitigation_plan": update_dict.get('mitigation_plan', current.mitigation_plan),
                "mitigation_strategies": update_dict.get('mitigation_strategies', current.mitigation_strategies),
                "follow_up_date": (update_dict.get('follow_up_date') or current.follow_up_date).isoformat() if (update_dict.get('follow_up_date') or current.follow_up_date) and hasattr(update_dict.get('follow_up_date') or current.follow_up_date, 'isoformat') else (str(update_dict.get('follow_up_date') or current.follow_up_date) if (update_dict.get('follow_up_date') or current.follow_up_date) else None)
            }
            
            self._safe_commit()
            
            return assessment_dict
        except HTTPException:
            raise
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error updating risk assessment: {str(e)}"
            )

    async def delete_risk_assessment(self, assessment_id: int) -> Dict:
        """Delete a risk assessment."""
        try:
            # Check existence with optimized query
            exists = self.db.query(RiskAssessment.id).filter(
                RiskAssessment.id == assessment_id
            ).first()
            
            if not exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Risk assessment with id {assessment_id} not found"
                )
            
            # Use bulk delete to avoid loading object with relationships
            self.db.query(RiskAssessment).filter(
                RiskAssessment.id == assessment_id
            ).delete(synchronize_session=False)
            
            self._safe_commit()
            
            return {"status": "success", "message": f"Risk assessment {assessment_id} deleted successfully"}
        except HTTPException:
            raise
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error deleting risk assessment: {str(e)}"
            )

    # Incident Reports CRUD
    
    async def get_incident_reports(self) -> List[Dict]:
        """Get all incident reports."""
        try:
            # Use with_entities to avoid loading relationships
            results = self.db.query(SafetyIncident).with_entities(
                SafetyIncident.id,
                SafetyIncident.student_id,
                SafetyIncident.activity_id,
                SafetyIncident.protocol_id,
                SafetyIncident.incident_date,
                SafetyIncident.incident_type,
                SafetyIncident.severity,
                SafetyIncident.description,
                SafetyIncident.location,
                SafetyIncident.teacher_id,
                SafetyIncident.equipment_id,
                SafetyIncident.action_taken,
                SafetyIncident.follow_up_required,
                SafetyIncident.follow_up_notes,
                SafetyIncident.incident_metadata
            ).all()
            
            # Create minimal objects and convert to dict
            class MinimalIncident:
                def __init__(self, id, student_id, activity_id, protocol_id, incident_date,
                           incident_type, severity, description, location, teacher_id,
                           equipment_id, action_taken, follow_up_required, follow_up_notes,
                           incident_metadata):
                    self.id = id
                    self.student_id = student_id
                    self.activity_id = activity_id
                    self.protocol_id = protocol_id
                    self.incident_date = incident_date
                    self.incident_type = incident_type
                    self.severity = severity
                    self.description = description
                    self.location = location
                    self.teacher_id = teacher_id
                    self.equipment_id = equipment_id
                    self.action_taken = action_taken
                    self.follow_up_required = follow_up_required
                    self.follow_up_notes = follow_up_notes
                    self.incident_metadata = incident_metadata
            
            incidents = [MinimalIncident(*r) for r in results]
            return [self._incident_to_dict(i) for i in incidents]
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving incident reports: {str(e)}"
            )

    async def create_incident_report(self, report: Dict) -> Dict:
        """Create a new incident report."""
        try:
            # Validate required fields
            required_fields = ['student_id', 'activity_id', 'incident_date', 'incident_type', 'severity']
            missing_fields = [field for field in required_fields if field not in report]
            if missing_fields:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Missing required fields: {', '.join(missing_fields)}"
                )
            
            # Create new incident
            new_incident = SafetyIncident(
                student_id=report['student_id'],
                activity_id=report['activity_id'],
                protocol_id=report.get('protocol_id'),
                incident_date=report['incident_date'],
                incident_type=report['incident_type'],
                severity=report['severity'],
                description=report.get('description'),
                location=report.get('location'),
                teacher_id=report.get('teacher_id'),
                equipment_id=report.get('equipment_id'),
                action_taken=report.get('action_taken'),
                follow_up_required=report.get('follow_up_required', False),
                follow_up_notes=report.get('follow_up_notes'),
                incident_metadata=report.get('incident_metadata')
            )
            
            self.db.add(new_incident)
            self.db.flush()  # Flush to get ID before commit
            
            # Build return dict before commit to avoid refresh/relationship loading
            now = datetime.utcnow()
            incident_dict = {
                "id": new_incident.id,
                "student_id": new_incident.student_id,
                "activity_id": new_incident.activity_id,
                "protocol_id": new_incident.protocol_id,
                "incident_date": new_incident.incident_date.isoformat() if hasattr(new_incident.incident_date, 'isoformat') else str(new_incident.incident_date),
                "incident_type": new_incident.incident_type.value if hasattr(new_incident.incident_type, 'value') else str(new_incident.incident_type),
                "severity": new_incident.severity.value if hasattr(new_incident.severity, 'value') else str(new_incident.severity),
                "description": new_incident.description,
                "location": new_incident.location,
                "teacher_id": new_incident.teacher_id,
                "equipment_id": new_incident.equipment_id,
                "action_taken": new_incident.action_taken,
                "follow_up_required": new_incident.follow_up_required,
                "follow_up_notes": new_incident.follow_up_notes,
                "incident_metadata": new_incident.incident_metadata
            }
            
            # Add timestamp fields if they exist
            if hasattr(new_incident, 'created_at'):
                incident_dict["created_at"] = now.isoformat()
            if hasattr(new_incident, 'updated_at'):
                incident_dict["updated_at"] = now.isoformat()
            
            # Use safe_commit instead of commit
            self._safe_commit()
            
            return incident_dict
        except HTTPException:
            raise
        except IntegrityError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Database integrity error: {str(e)}"
            )
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating incident report: {str(e)}"
            )

    async def update_incident_report(self, report_id: int, report: Dict) -> Dict:
        """Update an existing incident report."""
        try:
            # Get current values using optimized query
            current = self._get_safety_incident_optimized(report_id)
            
            if not current:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Incident report with id {report_id} not found"
                )
            
            # Build update dict
            update_dict = {}
            if 'student_id' in report:
                update_dict['student_id'] = report['student_id']
            if 'activity_id' in report:
                update_dict['activity_id'] = report['activity_id']
            if 'protocol_id' in report:
                update_dict['protocol_id'] = report['protocol_id']
            if 'incident_date' in report:
                update_dict['incident_date'] = report['incident_date']
            if 'incident_type' in report:
                update_dict['incident_type'] = report['incident_type']
            if 'severity' in report:
                update_dict['severity'] = report['severity']
            if 'description' in report:
                update_dict['description'] = report['description']
            if 'location' in report:
                update_dict['location'] = report['location']
            if 'teacher_id' in report:
                update_dict['teacher_id'] = report['teacher_id']
            if 'equipment_id' in report:
                update_dict['equipment_id'] = report['equipment_id']
            if 'action_taken' in report:
                update_dict['action_taken'] = report['action_taken']
            if 'follow_up_required' in report:
                update_dict['follow_up_required'] = report['follow_up_required']
            if 'follow_up_notes' in report:
                update_dict['follow_up_notes'] = report['follow_up_notes']
            if 'incident_metadata' in report:
                update_dict['incident_metadata'] = report['incident_metadata']
            
            # Use bulk update to avoid loading object with relationships
            if update_dict:
                self.db.query(SafetyIncident).filter(
                    SafetyIncident.id == report_id
                ).update(update_dict, synchronize_session=False)
            
            # Build return dict from current + updates
            incident_dict = {
                "id": current.id,
                "student_id": update_dict.get('student_id', current.student_id),
                "activity_id": update_dict.get('activity_id', current.activity_id),
                "protocol_id": update_dict.get('protocol_id', current.protocol_id),
                "incident_date": (update_dict.get('incident_date') or current.incident_date).isoformat() if (update_dict.get('incident_date') or current.incident_date) and hasattr(update_dict.get('incident_date') or current.incident_date, 'isoformat') else (str(update_dict.get('incident_date') or current.incident_date) if (update_dict.get('incident_date') or current.incident_date) else None),
                "incident_type": update_dict.get('incident_type', current.incident_type),
                "severity": update_dict.get('severity', current.severity),
                "description": update_dict.get('description', current.description),
                "location": update_dict.get('location', current.location),
                "teacher_id": update_dict.get('teacher_id', current.teacher_id),
                "equipment_id": update_dict.get('equipment_id', current.equipment_id),
                "action_taken": update_dict.get('action_taken', current.action_taken),
                "follow_up_required": update_dict.get('follow_up_required', current.follow_up_required),
                "follow_up_notes": update_dict.get('follow_up_notes', current.follow_up_notes),
                "incident_metadata": update_dict.get('incident_metadata', current.incident_metadata)
            }
            
            self._safe_commit()
            
            return incident_dict
        except HTTPException:
            raise
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error updating incident report: {str(e)}"
            )

    async def delete_incident_report(self, report_id: int) -> Dict:
        """Delete an incident report."""
        try:
            # Check existence with raw SQL to avoid ORM overhead
            try:
                self.db.execute(text("SET LOCAL statement_timeout = '5s'"))
            except:
                pass
            exists = self.db.execute(
                text("SELECT id FROM safety_incidents WHERE id = :id"),
                {"id": report_id}
            ).fetchone()
            
            if not exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Incident report with id {report_id} not found"
                )
            
            # Use bulk delete to avoid loading object with relationships
            self.db.query(SafetyIncident).filter(
                SafetyIncident.id == report_id
            ).delete(synchronize_session=False)
            
            self._safe_commit()
            
            return {"status": "success", "message": f"Incident report {report_id} deleted successfully"}
        except HTTPException:
            raise
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error deleting incident report: {str(e)}"
            )

    # Helper methods for converting models to dictionaries
    
    def _protocol_to_dict(self, protocol: SafetyProtocol) -> Dict:
        """Convert SafetyProtocol model to dictionary."""
        return {
            "id": protocol.id,
            "name": protocol.name,
            "description": protocol.description,
            "category": protocol.category,
            "requirements": protocol.requirements,
            "procedures": protocol.procedures,
            "emergency_contacts": protocol.emergency_contacts,
            "is_active": protocol.is_active,
            "last_reviewed": protocol.last_reviewed.isoformat() if protocol.last_reviewed else None,
            "reviewed_by": protocol.reviewed_by,
            "created_by": protocol.created_by,
            "created_at": protocol.created_at.isoformat() if hasattr(protocol, 'created_at') and protocol.created_at else None,
            "updated_at": protocol.updated_at.isoformat() if hasattr(protocol, 'updated_at') and protocol.updated_at else None
        }
    
    def _procedure_to_dict(self, procedure: EmergencyProcedure) -> Dict:
        """Convert EmergencyProcedure model to dictionary."""
        return {
            "id": procedure.id,
            "name": procedure.name,
            "description": procedure.description,
            "procedure_type": procedure.procedure_type,
            "class_id": procedure.class_id,
            "steps": procedure.steps,
            "contact_info": procedure.contact_info,
            "is_active": procedure.is_active,
            "last_drill_date": procedure.last_drill_date.isoformat() if procedure.last_drill_date else None,
            "next_drill_date": procedure.next_drill_date.isoformat() if procedure.next_drill_date else None,
            "created_by": procedure.created_by,
            "created_at": procedure.created_at.isoformat() if procedure.created_at else None,
            "updated_at": procedure.updated_at.isoformat() if procedure.updated_at else None
        }
    
    def _risk_assessment_to_dict(self, assessment: RiskAssessment) -> Dict:
        """Convert RiskAssessment model to dictionary."""
        # Ensure risk_level is uppercase (LOW, MEDIUM, HIGH, CRITICAL)
        risk_level = assessment.risk_level
        if risk_level:
            risk_level = risk_level.upper()
        
        return {
            "id": assessment.id,
            "incident_id": assessment.incident_id,
            "class_id": assessment.class_id,
            "activity_id": assessment.activity_id,
            "activity_type": assessment.activity_type,
            "environment": assessment.environment,
            "risk_level": risk_level,
            "assessment_date": assessment.assessment_date.isoformat() if assessment.assessment_date else None,
            "assessed_by": assessment.assessed_by,
            "environmental_risks": assessment.environmental_risks,
            "student_risks": assessment.student_risks,
            "activity_risks": assessment.activity_risks,
            "mitigation_plan": assessment.mitigation_plan,
            "mitigation_strategies": assessment.mitigation_strategies,
            "follow_up_date": assessment.follow_up_date.isoformat() if assessment.follow_up_date else None
        }
    
    def _incident_to_dict(self, incident: SafetyIncident) -> Dict:
        """Convert SafetyIncident model to dictionary."""
        return {
            "id": incident.id,
            "student_id": incident.student_id,
            "activity_id": incident.activity_id,
            "protocol_id": incident.protocol_id,
            "incident_date": incident.incident_date.isoformat() if incident.incident_date else None,
            "incident_type": incident.incident_type,
            "severity": incident.severity,
            "description": incident.description,
            "location": incident.location,
            "teacher_id": incident.teacher_id,
            "equipment_id": incident.equipment_id,
            "action_taken": incident.action_taken,
            "follow_up_required": incident.follow_up_required,
            "follow_up_notes": incident.follow_up_notes,
            "incident_metadata": incident.incident_metadata
        }
    
    # Migration Methods
    
    async def migrate_existing_safety_data(self) -> Dict[str, int]:
        """Migrate existing safety data from skill_assessment_safety_* tables to Phase 1 tables."""
        migrated_counts = {
            "protocols": 0,
            "incidents": 0,
            "risk_assessments": 0,
            "emergency_procedures": 0
        }
        
        try:
            # 1. Migrate skill_assessment_safety_protocols -> safety_protocols
            from sqlalchemy import text
            # Use with_entities to avoid relationship loading
            skill_protocols = self.db.query(SkillAssessmentSafetyProtocol).with_entities(
                SkillAssessmentSafetyProtocol.id,
                SkillAssessmentSafetyProtocol.description,
                SkillAssessmentSafetyProtocol.protocol_type,
                SkillAssessmentSafetyProtocol.steps,
                SkillAssessmentSafetyProtocol.emergency_contacts,
                SkillAssessmentSafetyProtocol.created_by,
                SkillAssessmentSafetyProtocol.last_reviewed
            ).all()
            
            for sp_row in skill_protocols:
                # Check if already migrated by checking description
                if sp_row.description and "migrated_from" in sp_row.description:
                    continue
                
                # Check if already migrated using raw SQL to avoid ORM overhead
                if sp_row.description:
                    try:
                        self.db.execute(text("SET LOCAL statement_timeout = '5s'"))
                    except:
                        pass
                    existing = self.db.execute(
                        text("SELECT id FROM safety_protocols WHERE description ILIKE :desc_pattern AND created_by = :created_by LIMIT 1"),
                        {"desc_pattern": f"%{sp_row.description[:50]}%", "created_by": sp_row.created_by}
                    ).fetchone()
                else:
                    existing = None
                
                if not existing:
                    # Create new SafetyProtocol from SkillAssessmentSafetyProtocol
                    protocol_name = sp_row.description[:100] if sp_row.description else f"Protocol {sp_row.id}"
                    import json
                    # Convert emergency_contacts to JSON string if it's a dict/list
                    emergency_contacts_str = None
                    if sp_row.emergency_contacts:
                        if isinstance(sp_row.emergency_contacts, (dict, list)):
                            emergency_contacts_str = json.dumps(sp_row.emergency_contacts)
                        else:
                            emergency_contacts_str = str(sp_row.emergency_contacts)
                    
                    protocol = SafetyProtocol(
                        name=f"Migrated: {protocol_name}",
                        description=sp_row.description or "Migrated protocol",
                        category=sp_row.protocol_type or "general",
                        requirements=sp_row.steps if isinstance(sp_row.steps, str) else str(sp_row.steps) if sp_row.steps else "",
                        procedures=sp_row.steps if isinstance(sp_row.steps, str) else str(sp_row.steps) if sp_row.steps else "",
                        emergency_contacts=emergency_contacts_str,
                        is_active=True,
                        created_by=sp_row.created_by,
                        reviewed_by=sp_row.created_by,
                        last_reviewed=sp_row.last_reviewed or datetime.utcnow()
                    )
                    self.db.add(protocol)
                    migrated_counts["protocols"] += 1
            
            # 2. Migrate skill_assessment_safety_incidents -> safety_incidents
            # Use raw SQL to avoid enum conversion issues
            from sqlalchemy import text
            skill_incidents_raw = self.db.execute(text("""
                SELECT id, activity_id, student_id, incident_type, severity, description, 
                       response_taken, reported_by, location, equipment_involved, witnesses,
                       follow_up_required, follow_up_notes, date
                FROM skill_assessment_safety_incidents
            """)).fetchall()
            
            # Map incident types from source to target (handle enum mismatches)
            incident_type_map = {
                'INJURY': 'injury',
                'EQUIPMENT_FAILURE': 'equipment_failure',
                'ENVIRONMENTAL': 'environmental',
                'BEHAVIORAL': 'behavioral',
                'NEAR_MISS': 'near_miss',  # Source enum doesn't have this, but DB does
                'MEDICAL': 'injury',  # Map to closest match
                'OTHER': 'injury'  # Map to closest match
            }
            
            # Map severity values
            severity_map = {
                'LOW': 'low',
                'MEDIUM': 'medium',
                'HIGH': 'high',
                'CRITICAL': 'critical'
            }
            
            for si_row in skill_incidents_raw:
                # Get raw values from database
                source_incident_type = si_row.incident_type.upper() if si_row.incident_type else 'OTHER'
                source_severity = si_row.severity.upper() if si_row.severity else 'MEDIUM'
                
                # Map to target enum values
                target_incident_type = incident_type_map.get(source_incident_type, 'injury')
                target_severity = severity_map.get(source_severity, 'medium')
                
                # Check if already migrated using optimized query
                existing = self.db.query(SafetyIncident.id).filter(
                    SafetyIncident.student_id == si_row.student_id,
                    SafetyIncident.activity_id == si_row.activity_id,
                    SafetyIncident.incident_date == (si_row.date if si_row.date else datetime.utcnow())
                ).first()
                
                if not existing and si_row.student_id:
                    # Create new SafetyIncident from SkillAssessmentSafetyIncident
                    incident = SafetyIncident(
                        student_id=si_row.student_id,
                        activity_id=si_row.activity_id,
                        incident_date=si_row.date or datetime.utcnow(),
                        incident_type=target_incident_type,
                        severity=target_severity,
                        description=si_row.description,
                        location=si_row.location,
                        teacher_id=si_row.reported_by,
                        action_taken=si_row.response_taken,
                        follow_up_required=si_row.follow_up_required or False,
                        follow_up_notes=si_row.follow_up_notes,
                        incident_metadata={
                            "migrated_from": "skill_assessment_safety_incidents",
                            "original_id": si_row.id,
                            "equipment_involved": si_row.equipment_involved,
                            "witnesses": si_row.witnesses,
                            "original_incident_type": source_incident_type,
                            "original_severity": source_severity
                        }
                    )
                    self.db.add(incident)
                    migrated_counts["incidents"] += 1
            
            # 3. Migrate skill_assessment_risk_assessments -> risk_assessments
            # Use with_entities to avoid relationship loading
            skill_risks = self.db.query(SkillAssessmentRiskAssessment).with_entities(
                SkillAssessmentRiskAssessment.id,
                SkillAssessmentRiskAssessment.activity_id,
                SkillAssessmentRiskAssessment.risk_level,
                SkillAssessmentRiskAssessment.factors,
                SkillAssessmentRiskAssessment.mitigation_measures,
                SkillAssessmentRiskAssessment.environmental_conditions,
                SkillAssessmentRiskAssessment.student_health_considerations,
                SkillAssessmentRiskAssessment.assessed_by
            ).all()
            
            for sr_row in skill_risks:
                # Check if already migrated using raw SQL to avoid ORM overhead
                try:
                    self.db.execute(text("SET LOCAL statement_timeout = '5s'"))
                except:
                    pass
                existing = self.db.execute(
                    text("SELECT id FROM risk_assessments WHERE activity_id = :activity_id AND assessed_by = :assessed_by LIMIT 1"),
                    {"activity_id": sr_row.activity_id, "assessed_by": sr_row.assessed_by}
                ).fetchone()
                
                if not existing:
                    # Create new RiskAssessment from SkillAssessmentRiskAssessment
                    from app.models.physical_education.pe_enums.pe_types import RiskLevel, RiskStatus
                    
                    # Handle risk_level - it might be an enum or string
                    risk_level_value = sr_row.risk_level
                    if hasattr(sr_row.risk_level, 'value'):
                        risk_level_value = sr_row.risk_level.value
                    elif hasattr(sr_row.risk_level, 'name'):
                        risk_level_value = sr_row.risk_level.name
                    else:
                        risk_level_value = str(sr_row.risk_level)
                    
                    risk = RiskAssessment(
                        activity_id=sr_row.activity_id,
                        activity_type="general",
                        environment="indoor",
                        assessment_date=datetime.utcnow(),
                        assessed_by=sr_row.assessed_by,
                        risk_level=RiskLevel(risk_level_value) if isinstance(risk_level_value, str) else risk_level_value,
                        environmental_risks=sr_row.environmental_conditions.get("risks", []) if isinstance(sr_row.environmental_conditions, dict) else [],
                        student_risks=sr_row.student_health_considerations.get("risks", []) if isinstance(sr_row.student_health_considerations, dict) else [],
                        activity_risks=sr_row.factors if isinstance(sr_row.factors, list) else [],
                        mitigation_strategies=sr_row.mitigation_measures if isinstance(sr_row.mitigation_measures, list) else [],
                        mitigation_plan="Migrated from skill assessment risk assessment"
                    )
                    self.db.add(risk)
                    migrated_counts["risk_assessments"] += 1
            
            # Flush before commit to ensure all objects are persisted
            self.db.flush()
            
            # Use _safe_commit which handles deadlocks and SAVEPOINT transactions
            self._safe_commit()
            
            return migrated_counts
            
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error migrating safety data: {str(e)}"
            )
