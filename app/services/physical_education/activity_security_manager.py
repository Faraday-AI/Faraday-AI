"""Activity security manager for physical education."""


import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import numpy as np
from sqlalchemy.orm import Session
from app.core.database import get_db

# Import models
from app.models.activity import (
    Activity,
    ActivityType,
    ActivityCategoryAssociation
)
from app.models.student import Student
from app.models.security import (
    SecurityPolicy,
    SecurityRule,
    SecurityAudit,
    SecurityIncidentManagement
)
from app.models.physical_education.activity.models import (
    StudentActivityPerformance,
    StudentActivityPreference
)
from app.models.physical_education.pe_enums.pe_types import (
    SecurityType,
    SecurityLevel,
    SecurityStatus,
    SecurityTrigger,
    SecurityAction,
    DifficultyLevel,
    EquipmentRequirement
)
from app.models.app_models import (
    SecurityType,
    SecurityLevel,
    SecurityStatus,
    SecurityTrigger,
    SecurityAction
)

class ActivitySecurityManager:
    """Service for managing physical education activity security."""
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ActivitySecurityManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.logger = logging.getLogger("activity_security_manager")
        self.db = None
        
        # Security settings
        self.settings = {
            "security_enabled": True,
            "auto_enforce": True,
            "min_data_points": 5,
            "audit_window": 30,  # days
            "thresholds": {
                "low_risk": 0.2,
                "medium_risk": 0.5,
                "high_risk": 0.8
            },
            "weights": {
                "severity": 0.4,
                "likelihood": 0.3,
                "impact": 0.3
            }
        }
        
        # Security components
        self.security_policies = {}
        self.security_rules = {}
        self.audit_history = []
        self.incident_history = []
    
    async def initialize(self):
        """Initialize the security manager."""
        try:
            # Get database session using context manager
            db_gen = get_db()
            self.db = await anext(db_gen)
            
            # Initialize security components
            self.initialize_security_components()
            
            self.logger.info("Activity Security Manager initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing Activity Security Manager: {str(e)}")
            raise
    
    async def cleanup(self):
        """Cleanup the security manager."""
        try:
            # Clear all data
            self.security_policies.clear()
            self.security_rules.clear()
            self.audit_history.clear()
            self.incident_history.clear()
            
            # Reset service references
            self.db = None
            
            self.logger.info("Activity Security Manager cleaned up successfully")
        except Exception as e:
            self.logger.error(f"Error cleaning up Activity Security Manager: {str(e)}")
            raise

    def initialize_security_components(self):
        """Initialize security components."""
        try:
            # Initialize security policies
            self.security_policies = {
                "access_control": {
                    "description": "Controls access to activities and resources",
                    "rules": [
                        "verify_user_permissions",
                        "check_role_assignments",
                        "validate_access_tokens"
                    ]
                },
                "data_protection": {
                    "description": "Protects sensitive student and activity data",
                    "rules": [
                        "encrypt_sensitive_data",
                        "enforce_data_retention",
                        "manage_data_access"
                    ]
                },
                "activity_safety": {
                    "description": "Ensures safe activity execution",
                    "rules": [
                        "validate_equipment_safety",
                        "check_environment_safety",
                        "verify_student_readiness"
                    ]
                }
            }
            
            # Initialize security rules
            self.security_rules = {
                "verify_user_permissions": {
                    "type": "access_control",
                    "severity": "high",
                    "action": self._verify_user_permissions
                },
                "check_role_assignments": {
                    "type": "access_control",
                    "severity": "medium",
                    "action": self._check_role_assignments
                },
                "validate_access_tokens": {
                    "type": "access_control",
                    "severity": "high",
                    "action": self._validate_access_tokens
                },
                "encrypt_sensitive_data": {
                    "type": "data_protection",
                    "severity": "high",
                    "action": self._encrypt_sensitive_data
                },
                "enforce_data_retention": {
                    "type": "data_protection",
                    "severity": "medium",
                    "action": self._enforce_data_retention
                },
                "manage_data_access": {
                    "type": "data_protection",
                    "severity": "high",
                    "action": self._manage_data_access
                },
                "validate_equipment_safety": {
                    "type": "activity_safety",
                    "severity": "high",
                    "action": self._validate_equipment_safety
                },
                "check_environment_safety": {
                    "type": "activity_safety",
                    "severity": "high",
                    "action": self._check_environment_safety
                },
                "verify_student_readiness": {
                    "type": "activity_safety",
                    "severity": "medium",
                    "action": self._verify_student_readiness
                }
            }
            
            self.logger.info("Security components initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing security components: {str(e)}")
            raise

    async def enforce_security(
        self,
        activity_id: str,
        student_id: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Enforce security policies for an activity."""
        try:
            if not self.settings["security_enabled"]:
                raise ValueError("Activity security is disabled")
            
            # Apply security rules
            results = {}
            for rule_name, rule in self.security_rules.items():
                result = await rule["action"](
                    activity_id,
                    student_id,
                    context
                )
                results[rule_name] = result
            
            # Create audit record
            audit = {
                "activity_id": activity_id,
                "student_id": student_id,
                "context": context,
                "results": results,
                "timestamp": datetime.now().isoformat()
            }
            
            # Update audit history
            self._update_audit_history(audit)
            
            # Check for security incidents
            incidents = self._check_security_incidents(results)
            if incidents:
                self._handle_security_incidents(incidents)
            
            return {
                "status": "success" if not incidents else "warning",
                "results": results,
                "incidents": incidents
            }
            
        except Exception as e:
            self.logger.error(f"Error enforcing security: {str(e)}")
            raise

    async def get_audit_history(
        self,
        activity_id: Optional[str] = None,
        student_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get security audit history."""
        try:
            history = self.audit_history
            
            if activity_id:
                history = [h for h in history if h["activity_id"] == activity_id]
            
            if student_id:
                history = [h for h in history if h["student_id"] == student_id]
            
            return history
            
        except Exception as e:
            self.logger.error(f"Error getting audit history: {str(e)}")
            raise

    async def get_incident_history(
        self,
        activity_id: Optional[str] = None,
        student_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get security incident history."""
        try:
            history = self.incident_history
            
            if activity_id:
                history = [h for h in history if h["activity_id"] == activity_id]
            
            if student_id:
                history = [h for h in history if h["student_id"] == student_id]
            
            return history
            
        except Exception as e:
            self.logger.error(f"Error getting incident history: {str(e)}")
            raise

    def _update_audit_history(
        self,
        audit: Dict[str, Any]
    ) -> None:
        """Update security audit history."""
        try:
            self.audit_history.append(audit)
            
            # Trim history if needed
            if len(self.audit_history) > 1000:  # Keep last 1000 records
                self.audit_history = self.audit_history[-1000:]
            
        except Exception as e:
            self.logger.error(f"Error updating audit history: {str(e)}")
            raise

    def _check_security_incidents(
        self,
        results: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Check for security incidents in rule results."""
        try:
            incidents = []
            
            for rule_name, result in results.items():
                if not result.get("success"):
                    rule = self.security_rules[rule_name]
                    incidents.append({
                        "rule": rule_name,
                        "type": rule["type"],
                        "severity": rule["severity"],
                        "details": result.get("details", "Unknown error"),
                        "timestamp": datetime.now().isoformat()
                    })
            
            return incidents
            
        except Exception as e:
            self.logger.error(f"Error checking security incidents: {str(e)}")
            raise

    def _handle_security_incidents(
        self,
        incidents: List[Dict[str, Any]]
    ) -> None:
        """Handle security incidents."""
        try:
            for incident in incidents:
                # Add to incident history
                self.incident_history.append(incident)
                
                # Log incident
                self.logger.warning(
                    f"Security incident: {incident['rule']} - {incident['details']}"
                )
                
                # Implement incident response based on severity
                if incident["severity"] == "high":
                    self._handle_high_severity_incident(incident)
                elif incident["severity"] == "medium":
                    self._handle_medium_severity_incident(incident)
                else:
                    self._handle_low_severity_incident(incident)
            
            # Trim incident history if needed
            if len(self.incident_history) > 1000:  # Keep last 1000 records
                self.incident_history = self.incident_history[-1000:]
            
        except Exception as e:
            self.logger.error(f"Error handling security incidents: {str(e)}")
            raise

    # Security rule implementations
    async def _verify_user_permissions(
        self,
        activity_id: str,
        student_id: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Verify user permissions."""
        # Implementation depends on permission system
        pass

    async def _check_role_assignments(
        self,
        activity_id: str,
        student_id: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check role assignments."""
        # Implementation depends on role system
        pass

    async def _validate_access_tokens(
        self,
        activity_id: str,
        student_id: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate access tokens."""
        # Implementation depends on authentication system
        pass

    async def _encrypt_sensitive_data(
        self,
        activity_id: str,
        student_id: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Encrypt sensitive data."""
        # Implementation depends on encryption system
        pass

    async def _enforce_data_retention(
        self,
        activity_id: str,
        student_id: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Enforce data retention policies."""
        # Implementation depends on data retention system
        pass

    async def _manage_data_access(
        self,
        activity_id: str,
        student_id: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Manage data access."""
        # Implementation depends on data access system
        pass

    async def _validate_equipment_safety(
        self,
        activity_id: str,
        student_id: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate equipment safety."""
        # Implementation depends on equipment system
        pass

    async def _check_environment_safety(
        self,
        activity_id: str,
        student_id: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check environment safety."""
        # Implementation depends on environment system
        pass

    async def _verify_student_readiness(
        self,
        activity_id: str,
        student_id: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Verify student readiness."""
        # Implementation depends on student system
        pass

    # Incident handling implementations
    def _handle_high_severity_incident(
        self,
        incident: Dict[str, Any]
    ) -> None:
        """Handle high severity security incident."""
        # Implementation depends on incident response system
        pass

    def _handle_medium_severity_incident(
        self,
        incident: Dict[str, Any]
    ) -> None:
        """Handle medium severity security incident."""
        # Implementation depends on incident response system
        pass

    def _handle_low_severity_incident(
        self,
        incident: Dict[str, Any]
    ) -> None:
        """Handle low severity security incident."""
        # Implementation depends on incident response system
        pass 