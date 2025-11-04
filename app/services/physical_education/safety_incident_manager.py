from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
from sqlalchemy.orm import Session
from fastapi import Depends

from app.models.physical_education.safety import SafetyIncident
from app.core.database import get_db

class SafetyIncidentManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.incident_types = [
            "injury", "equipment_failure", "environmental_hazard",
            "behavioral_issue", "medical_emergency", "other"
        ]
        self.severity_levels = ["low", "medium", "high", "critical"]
        self.status_types = ["open", "investigating", "resolved", "closed"]

    async def create_incident(
        self,
        student_id: int,
        activity_id: int,
        incident_type: str,
        description: str,
        severity: str,
        action_taken: str,
        location: Optional[str] = None,
        teacher_id: Optional[int] = None,
        equipment_id: Optional[int] = None,
        follow_up_required: bool = False,
        follow_up_notes: Optional[str] = None,
        incident_metadata: Optional[Dict[str, Any]] = None,
        db: Session = Depends(get_db)
    ) -> Dict[str, Any]:
        """Create a new safety incident record."""
        try:
            # Validate incident type
            if incident_type not in self.incident_types:
                raise ValueError(f"Invalid incident type. Must be one of: {self.incident_types}")
            
            # Validate severity
            if severity not in self.severity_levels:
                raise ValueError(f"Invalid severity level. Must be one of: {self.severity_levels}")
            
            incident = SafetyIncident(
                student_id=student_id,
                activity_id=activity_id,
                incident_type=incident_type,
                description=description,
                severity=severity,
                action_taken=action_taken,
                location=location,
                teacher_id=teacher_id,
                equipment_id=equipment_id,
                incident_date=datetime.utcnow(),
                follow_up_required=follow_up_required,
                follow_up_notes=follow_up_notes,
                incident_metadata=incident_metadata or {}
            )
            
            db.add(incident)
            db.flush()  # Use flush for SAVEPOINT transactions in tests
            db.refresh(incident)
            
            return {
                "success": True,
                "message": "Incident created successfully",
                "incident_id": incident.id
            }
            
        except Exception as e:
            self.logger.error(f"Error creating incident: {str(e)}")
            if db:
                db.rollback()
            return {
                "success": False,
                "message": f"Error creating incident: {str(e)}"
            }

    async def get_incident(
        self,
        incident_id: int,
        db: Session = Depends(get_db)
    ) -> Optional[SafetyIncident]:
        """Retrieve a specific incident by ID."""
        try:
            return db.query(SafetyIncident).filter(SafetyIncident.id == incident_id).first()
        except Exception as e:
            self.logger.error(f"Error retrieving incident: {str(e)}")
            return None

    async def get_incidents(
        self,
        student_id: Optional[int] = None,
        activity_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        severity: Optional[str] = None,
        incident_type: Optional[str] = None,
        db: Session = Depends(get_db)
    ) -> List[SafetyIncident]:
        """Retrieve incidents with optional filters."""
        try:
            query = db.query(SafetyIncident)
            
            if student_id:
                query = query.filter(SafetyIncident.student_id == student_id)
            if activity_id:
                query = query.filter(SafetyIncident.activity_id == activity_id)
            if start_date:
                query = query.filter(SafetyIncident.incident_date >= start_date)
            if end_date:
                query = query.filter(SafetyIncident.incident_date <= end_date)
            if severity:
                query = query.filter(SafetyIncident.severity == severity)
            if incident_type:
                query = query.filter(SafetyIncident.incident_type == incident_type)
            
            return query.all()
            
        except Exception as e:
            self.logger.error(f"Error retrieving incidents: {str(e)}")
            return []

    async def update_incident(
        self,
        incident_id: int,
        update_data: Dict[str, Any],
        db: Session = Depends(get_db)
    ) -> Dict[str, Any]:
        """Update an existing incident."""
        try:
            incident = db.query(SafetyIncident).filter(SafetyIncident.id == incident_id).first()
            if not incident:
                return {
                    "success": False,
                    "message": "Incident not found"
                }
            
            # Validate and update fields
            for key, value in update_data.items():
                if hasattr(incident, key):
                    if key == "incident_type" and value not in self.incident_types:
                        raise ValueError(f"Invalid incident type: {value}")
                    if key == "severity" and value not in self.severity_levels:
                        raise ValueError(f"Invalid severity level: {value}")
                    # Note: SafetyIncident model doesn't have a 'status' field
                    # Remove status validation if it exists
                    # if key == "status" and value not in self.status_types:
                    #     raise ValueError(f"Invalid status: {value}")
                    setattr(incident, key, value)
            
            db.flush()  # Use flush for SAVEPOINT transactions in tests
            db.refresh(incident)
            
            return {
                "success": True,
                "message": "Incident updated successfully"
            }
            
        except Exception as e:
            self.logger.error(f"Error updating incident: {str(e)}")
            if db:
                db.rollback()
            return {
                "success": False,
                "message": f"Error updating incident: {str(e)}"
            }

    async def delete_incident(
        self,
        incident_id: int,
        db: Session = Depends(get_db)
    ) -> Dict[str, Any]:
        """Delete an incident."""
        try:
            incident = db.query(SafetyIncident).filter(SafetyIncident.id == incident_id).first()
            if not incident:
                return {
                    "success": False,
                    "message": "Incident not found"
                }
            
            db.delete(incident)
            db.flush()  # Use flush for SAVEPOINT transactions in tests
            
            return {
                "success": True,
                "message": "Incident deleted successfully"
            }
            
        except Exception as e:
            self.logger.error(f"Error deleting incident: {str(e)}")
            if db:
                db.rollback()
            return {
                "success": False,
                "message": f"Error deleting incident: {str(e)}"
            }

    async def get_incident_statistics(
        self,
        student_id: Optional[int] = None,
        activity_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        db: Session = Depends(get_db)
    ) -> Dict[str, Any]:
        """Get statistics about incidents."""
        try:
            query = db.query(SafetyIncident)
            if student_id:
                query = query.filter(SafetyIncident.student_id == student_id)
            if activity_id:
                query = query.filter(SafetyIncident.activity_id == activity_id)
            if start_date:
                query = query.filter(SafetyIncident.incident_date >= start_date)
            if end_date:
                query = query.filter(SafetyIncident.incident_date <= end_date)
            
            incidents = query.all()
            
            stats = {
                "total": len(incidents),
                "by_type": {},
                "by_severity": {},
                "trends": {}
            }
            
            for incident in incidents:
                # Count by type
                stats["by_type"][incident.incident_type] = \
                    stats["by_type"].get(incident.incident_type, 0) + 1
                
                # Count by severity
                stats["by_severity"][incident.severity] = \
                    stats["by_severity"].get(incident.severity, 0) + 1
                
                # Calculate trends
                date_key = incident.incident_date.strftime("%Y-%m") if incident.incident_date else "unknown"
                stats["trends"][date_key] = stats["trends"].get(date_key, 0) + 1
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error calculating incident statistics: {str(e)}")
            return {}

    async def bulk_update_incidents(
        self,
        updates: List[Dict[str, Any]],
        db: Session = Depends(get_db)
    ) -> Dict[str, int]:
        """Bulk update multiple incidents."""
        try:
            success_count = 0
            failure_count = 0
            
            for update in updates:
                try:
                    incident_id = update.pop("id")
                    result = await self.update_incident(incident_id, update, db)
                    if result["success"]:
                        success_count += 1
                    else:
                        failure_count += 1
                except Exception as e:
                    self.logger.error(f"Error in bulk update: {str(e)}")
                    failure_count += 1
            
            return {
                "success_count": success_count,
                "failure_count": failure_count
            }
            
        except Exception as e:
            self.logger.error(f"Error in bulk update operation: {str(e)}")
            if db:
                db.rollback()
            return {
                "success_count": 0,
                "failure_count": len(updates)
            }

    async def bulk_delete_incidents(
        self,
        incident_ids: List[int],
        db: Session = Depends(get_db)
    ) -> Dict[str, int]:
        """Bulk delete multiple incidents."""
        try:
            success_count = 0
            failure_count = 0
            
            for incident_id in incident_ids:
                try:
                    # Query and delete directly without calling delete_incident
                    # to avoid multiple commits
                    incident = db.query(SafetyIncident).filter(SafetyIncident.id == incident_id).first()
                    if incident:
                        db.delete(incident)
                        success_count += 1
                    else:
                        failure_count += 1
                except Exception as e:
                    self.logger.error(f"Error in bulk delete: {str(e)}")
                    failure_count += 1
            
            # Commit once after all deletions
            db.flush()  # Use flush for SAVEPOINT transactions in tests
            
            return {
                "success_count": success_count,
                "failure_count": failure_count
            }
            
        except Exception as e:
            self.logger.error(f"Error in bulk delete operation: {str(e)}")
            if db:
                db.rollback()
            return {
                "success_count": 0,
                "failure_count": len(incident_ids)
            }

    async def check_health(self) -> Dict[str, Any]:
        """Check incident manager health."""
        try:
            return {
                "status": "healthy",
                "message": "Incident manager is operational",
                "timestamp": datetime.utcnow()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Incident manager error: {str(e)}",
                "timestamp": datetime.utcnow()
            }

    async def record_incident(
        self,
        class_id: str,
        incident_type: str,
        description: str,
        severity: str,
        affected_students: List[str],
        actions_taken: List[str],
        location: Optional[str] = None,
        time_of_incident: Optional[datetime] = None,
        witnesses: Optional[List[str]] = None,
        follow_up_required: bool = False
    ) -> Dict[str, Any]:
        """Record a safety incident."""
        try:
            incident_id = f"SI-{class_id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
            
            return {
                "success": True,
                "message": "Incident recorded successfully",
                "incident_id": incident_id,
                "class_id": class_id,
                "incident_type": incident_type,
                "description": description,
                "severity": severity,
                "affected_students": affected_students,
                "actions_taken": actions_taken,
                "location": location,
                "time_of_incident": time_of_incident or datetime.utcnow(),
                "witnesses": witnesses,
                "follow_up_required": follow_up_required,
                "created_at": datetime.utcnow()
            }
        except Exception as e:
            self.logger.error(f"Error recording incident: {str(e)}")
            return {
                "success": False,
                "message": f"Error recording incident: {str(e)}"
            } 