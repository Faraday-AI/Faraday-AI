"""
Safety Incident Manager Service

This module provides safety incident management functionality for physical education activities.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db

logger = logging.getLogger(__name__)

class SafetyIncident(BaseModel):
    """Model for safety incidents."""
    incident_id: str
    incident_type: str
    severity: str
    description: str
    location: str
    student_id: Optional[str] = None
    activity_id: Optional[str] = None
    reported_by: str
    reported_at: datetime
    status: str = "open"
    resolution: Optional[str] = None
    resolved_at: Optional[datetime] = None

class SafetyIncidentManager:
    """Service for managing safety incidents in the physical education system."""
    
    def __init__(self, db: Session = None):
        self.logger = logging.getLogger("safety_incident_manager")
        self.db = db
        self._incidents = {}
        self._incident_counter = 0
        
    async def report_incident(
        self,
        incident_type: str,
        severity: str,
        description: str,
        location: str,
        reported_by: str,
        student_id: Optional[str] = None,
        activity_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Report a new safety incident."""
        try:
            self._incident_counter += 1
            incident_id = f"incident_{self._incident_counter:06d}"
            
            incident = SafetyIncident(
                incident_id=incident_id,
                incident_type=incident_type,
                severity=severity,
                description=description,
                location=location,
                student_id=student_id,
                activity_id=activity_id,
                reported_by=reported_by,
                reported_at=datetime.utcnow()
            )
            
            self._incidents[incident_id] = incident
            
            # Log the incident
            self.logger.warning(
                f"Safety incident reported: {incident_type} - {severity} - {description}"
            )
            
            # For high severity incidents, trigger immediate notifications
            if severity in ["high", "critical"]:
                await self._trigger_emergency_notifications(incident)
            
            return {
                "incident_id": incident_id,
                "status": "reported",
                "message": "Incident reported successfully"
            }
            
        except Exception as e:
            self.logger.error(f"Error reporting incident: {str(e)}")
            raise
    
    async def get_incident(
        self,
        incident_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get incident details by ID."""
        try:
            incident = self._incidents.get(incident_id)
            if incident:
                return incident.dict()
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting incident: {str(e)}")
            return None
    
    async def list_incidents(
        self,
        status: Optional[str] = None,
        severity: Optional[str] = None,
        incident_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List incidents with optional filtering."""
        try:
            incidents = list(self._incidents.values())
            
            # Apply filters
            if status:
                incidents = [i for i in incidents if i.status == status]
            
            if severity:
                incidents = [i for i in incidents if i.severity == severity]
            
            if incident_type:
                incidents = [i for i in incidents if i.incident_type == incident_type]
            
            # Sort by reported_at (newest first)
            incidents.sort(key=lambda x: x.reported_at, reverse=True)
            
            # Apply pagination
            incidents = incidents[offset:offset + limit]
            
            return [incident.dict() for incident in incidents]
            
        except Exception as e:
            self.logger.error(f"Error listing incidents: {str(e)}")
            return []
    
    async def update_incident(
        self,
        incident_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """Update incident details."""
        try:
            if incident_id not in self._incidents:
                return False
            
            incident = self._incidents[incident_id]
            
            # Update allowed fields
            allowed_fields = ["status", "resolution", "description", "severity"]
            for field, value in updates.items():
                if field in allowed_fields:
                    setattr(incident, field, value)
            
            # Update resolved_at if status is resolved
            if updates.get("status") == "resolved" and not incident.resolved_at:
                incident.resolved_at = datetime.utcnow()
            
            incident.updated_at = datetime.utcnow()
            
            self.logger.info(f"Incident {incident_id} updated: {updates}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating incident: {str(e)}")
            return False
    
    async def resolve_incident(
        self,
        incident_id: str,
        resolution: str,
        resolved_by: str
    ) -> bool:
        """Resolve an incident."""
        try:
            if incident_id not in self._incidents:
                return False
            
            incident = self._incidents[incident_id]
            incident.status = "resolved"
            incident.resolution = resolution
            incident.resolved_at = datetime.utcnow()
            
            self.logger.info(f"Incident {incident_id} resolved by {resolved_by}: {resolution}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error resolving incident: {str(e)}")
            return False
    
    async def get_incident_statistics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get incident statistics."""
        try:
            incidents = list(self._incidents.values())
            
            # Filter by date range if provided
            if start_date:
                incidents = [i for i in incidents if i.reported_at >= start_date]
            if end_date:
                incidents = [i for i in incidents if i.reported_at <= end_date]
            
            # Calculate statistics
            total_incidents = len(incidents)
            open_incidents = len([i for i in incidents if i.status == "open"])
            resolved_incidents = len([i for i in incidents if i.status == "resolved"])
            
            # Severity breakdown
            severity_counts = {}
            for incident in incidents:
                severity_counts[incident.severity] = severity_counts.get(incident.severity, 0) + 1
            
            # Type breakdown
            type_counts = {}
            for incident in incidents:
                type_counts[incident.incident_type] = type_counts.get(incident.incident_type, 0) + 1
            
            # Average resolution time
            resolved_with_time = [
                i for i in incidents 
                if i.status == "resolved" and i.resolved_at
            ]
            
            avg_resolution_hours = 0
            if resolved_with_time:
                total_hours = sum(
                    (i.resolved_at - i.reported_at).total_seconds() / 3600
                    for i in resolved_with_time
                )
                avg_resolution_hours = total_hours / len(resolved_with_time)
            
            return {
                "total_incidents": total_incidents,
                "open_incidents": open_incidents,
                "resolved_incidents": resolved_incidents,
                "resolution_rate": (resolved_incidents / total_incidents * 100) if total_incidents > 0 else 0,
                "severity_breakdown": severity_counts,
                "type_breakdown": type_counts,
                "avg_resolution_hours": round(avg_resolution_hours, 2),
                "period": {
                    "start_date": start_date.isoformat() if start_date else None,
                    "end_date": end_date.isoformat() if end_date else None
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting incident statistics: {str(e)}")
            return {}
    
    async def generate_safety_report(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Generate a comprehensive safety report."""
        try:
            stats = await self.get_incident_statistics(start_date, end_date)
            
            # Get recent incidents
            recent_incidents = await self.list_incidents(limit=10)
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(stats)
            
            return {
                "report_generated_at": datetime.utcnow().isoformat(),
                "statistics": stats,
                "recent_incidents": recent_incidents,
                "recommendations": recommendations,
                "summary": {
                    "total_incidents": stats.get("total_incidents", 0),
                    "trend": "stable",  # Mock trend analysis
                    "risk_level": "low" if stats.get("total_incidents", 0) < 5 else "medium"
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error generating safety report: {str(e)}")
            return {"error": str(e)}
    
    # Helper methods
    async def _trigger_emergency_notifications(self, incident: SafetyIncident):
        """Trigger emergency notifications for high severity incidents."""
        try:
            # Mock emergency notification system
            self.logger.critical(
                f"EMERGENCY: {incident.incident_type} incident at {incident.location} - "
                f"Severity: {incident.severity} - {incident.description}"
            )
            
            # In a real implementation, this would:
            # - Send SMS/email alerts to administrators
            # - Notify emergency services if needed
            # - Update dashboard with emergency status
            # - Trigger automated safety protocols
            
        except Exception as e:
            self.logger.error(f"Error triggering emergency notifications: {str(e)}")
    
    async def _generate_recommendations(self, stats: Dict[str, Any]) -> List[str]:
        """Generate safety recommendations based on statistics."""
        recommendations = []
        
        total_incidents = stats.get("total_incidents", 0)
        severity_breakdown = stats.get("severity_breakdown", {})
        
        if total_incidents > 10:
            recommendations.append("Consider implementing additional safety training programs")
        
        if severity_breakdown.get("high", 0) > 2:
            recommendations.append("Review high-severity incident patterns and implement preventive measures")
        
        if severity_breakdown.get("critical", 0) > 0:
            recommendations.append("Conduct immediate safety audit and update emergency protocols")
        
        if not recommendations:
            recommendations.append("Current safety measures appear adequate")
        
        return recommendations 