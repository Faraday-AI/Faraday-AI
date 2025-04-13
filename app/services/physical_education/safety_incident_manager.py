from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
from sqlalchemy.orm import Session
from fastapi import Depends

from ..models.safety import SafetyIncident
from ..database import get_db

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
        class_id: str,
        incident_type: str,
        description: str,
        severity: str,
        affected_students: List[str],
        actions_taken: List[str],
        metadata: Optional[Dict[str, Any]] = None,
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
                class_id=class_id,
                incident_type=incident_type,
                description=description,
                severity=severity,
                affected_students=affected_students,
                actions_taken=actions_taken,
                date=datetime.utcnow(),
                status="open",
                reported=False,
                metadata=metadata or {}
            )
            
            db.add(incident)
            db.commit()
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
        incident_id: str,
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
        class_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        severity: Optional[str] = None,
        status: Optional[str] = None,
        db: Session = Depends(get_db)
    ) -> List[SafetyIncident]:
        """Retrieve incidents with optional filters."""
        try:
            query = db.query(SafetyIncident)
            
            if class_id:
                query = query.filter(SafetyIncident.class_id == class_id)
            if start_date:
                query = query.filter(SafetyIncident.date >= start_date)
            if end_date:
                query = query.filter(SafetyIncident.date <= end_date)
            if severity:
                query = query.filter(SafetyIncident.severity == severity)
            if status:
                query = query.filter(SafetyIncident.status == status)
            
            return query.all()
            
        except Exception as e:
            self.logger.error(f"Error retrieving incidents: {str(e)}")
            return []

    async def update_incident(
        self,
        incident_id: str,
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
                    if key == "status" and value not in self.status_types:
                        raise ValueError(f"Invalid status: {value}")
                    setattr(incident, key, value)
            
            db.commit()
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
        incident_id: str,
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
            db.commit()
            
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
        class_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        db: Session = Depends(get_db)
    ) -> Dict[str, Any]:
        """Get statistics about incidents."""
        try:
            query = db.query(SafetyIncident)
            if class_id:
                query = query.filter(SafetyIncident.class_id == class_id)
            if start_date:
                query = query.filter(SafetyIncident.date >= start_date)
            if end_date:
                query = query.filter(SafetyIncident.date <= end_date)
            
            incidents = query.all()
            
            stats = {
                "total": len(incidents),
                "by_type": {},
                "by_severity": {},
                "by_status": {},
                "trends": {}
            }
            
            for incident in incidents:
                # Count by type
                stats["by_type"][incident.incident_type] = \
                    stats["by_type"].get(incident.incident_type, 0) + 1
                
                # Count by severity
                stats["by_severity"][incident.severity] = \
                    stats["by_severity"].get(incident.severity, 0) + 1
                
                # Count by status
                stats["by_status"][incident.status] = \
                    stats["by_status"].get(incident.status, 0) + 1
                
                # Calculate trends
                date_key = incident.date.strftime("%Y-%m")
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
                "success": success_count,
                "failure": failure_count
            }
            
        except Exception as e:
            self.logger.error(f"Error in bulk update operation: {str(e)}")
            if db:
                db.rollback()
            return {
                "success": 0,
                "failure": len(updates)
            }

    async def bulk_delete_incidents(
        self,
        incident_ids: List[str],
        db: Session = Depends(get_db)
    ) -> Dict[str, int]:
        """Bulk delete multiple incidents."""
        try:
            success_count = 0
            failure_count = 0
            
            for incident_id in incident_ids:
                try:
                    result = await self.delete_incident(incident_id, db)
                    if result["success"]:
                        success_count += 1
                    else:
                        failure_count += 1
                except Exception as e:
                    self.logger.error(f"Error in bulk delete: {str(e)}")
                    failure_count += 1
            
            return {
                "success": success_count,
                "failure": failure_count
            }
            
        except Exception as e:
            self.logger.error(f"Error in bulk delete operation: {str(e)}")
            if db:
                db.rollback()
            return {
                "success": 0,
                "failure": len(incident_ids)
            } 