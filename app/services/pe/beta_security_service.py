"""
Beta Security Service
Provides security management for beta teachers (access validation, event logging, input sanitization)
Independent from district-level security management.
"""

from typing import Dict, Any, Optional, Union, List
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.services.physical_education.services.security_service import SecurityService
from app.models.security.event.security_event import SecurityEvent
from app.models.teacher_registration import TeacherRegistration


class BetaSecurityService(SecurityService):
    """Security service for beta teachers - filters to teacher's context."""
    
    def __init__(self, db: Session, teacher_id: int):
        super().__init__()
        self.db = db
        self.teacher_id = teacher_id
    
    async def validate_access(
        self,
        user_id: Union[str, int],
        required_level: str,
        db: Optional[Session] = None
    ) -> bool:
        """Validate if a user (beta teacher) has the required access level."""
        # Use the provided db session or fallback to self.db
        session = db or self.db
        
        # For beta teachers, validate their access
        # Beta teachers typically have "teacher" level access
        if int(user_id) == self.teacher_id:
            # Beta teacher validating their own access
            return await super().validate_access(user_id, required_level, session)
        else:
            # For beta system, we might want to restrict access validation
            # to only the current teacher's context
            self.logger.warning(
                f"Beta teacher {self.teacher_id} attempted to validate access for user {user_id}"
            )
            return False
    
    async def log_security_event(
        self,
        event_type: str,
        user_id: Optional[Union[str, int]] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        action: Optional[str] = None,
        severity: str = "info",
        description: Optional[str] = None,
        success: str = "unknown",
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """Log a security-related event for beta teacher."""
        # Use the provided db session or fallback to self.db
        session = db or self.db
        
        # Get the actual user_id from User table using TeacherRegistration email
        # security_events.user_id is Integer, not UUID (TeacherRegistration.id is UUID)
        from app.models.teacher_registration import TeacherRegistration
        from app.models.core.user import User
        
        teacher = session.query(TeacherRegistration).filter(
            TeacherRegistration.id == self.teacher_id
        ).first()
        
        # Get user_id from User table using teacher's email
        actual_user_id = None
        if teacher and teacher.email:
            user = session.query(User).filter(User.email == teacher.email).first()
            if user:
                actual_user_id = user.id
        
        # Use provided user_id or fallback to teacher's user_id
        if user_id is None:
            user_id = actual_user_id
        
        # Add beta context to details
        if details is None:
            details = {}
        
        # Convert UUID to string for JSON serialization
        teacher_id_str = str(self.teacher_id) if self.teacher_id else None
        details["beta_teacher_id"] = teacher_id_str
        details["beta_system"] = True
        
        # Set resource_type to beta context if not provided
        if resource_type is None:
            resource_type = "beta_teacher_system"
        
        return await super().log_security_event(
            event_type=event_type,
            user_id=user_id,
            details=details,
            ip_address=ip_address,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            severity=severity,
            description=description,
            success=success,
            db=session
        )
    
    async def sanitize_input(
        self,
        input_data: Any,
        input_type: str = "string",
        db: Optional[Session] = None
    ) -> Any:
        """Sanitize input data for beta teacher."""
        # Use the provided db session or fallback to self.db
        session = db or self.db
        
        return await super().sanitize_input(input_data, input_type, session)
    
    async def get_security_events(
        self,
        limit: int = 100,
        offset: int = 0,
        event_type: Optional[str] = None,
        severity: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get security events for this beta teacher."""
        try:
            from sqlalchemy import text
            
            # Get the actual user_id from User table using TeacherRegistration email
            # security_events.user_id is Integer, not UUID (TeacherRegistration.id is UUID)
            from app.models.teacher_registration import TeacherRegistration
            from app.models.core.user import User
            
            teacher = self.db.query(TeacherRegistration).filter(
                TeacherRegistration.id == self.teacher_id
            ).first()
            
            # Get user_id from User table using teacher's email
            actual_user_id = None
            if teacher and teacher.email:
                user = self.db.query(User).filter(User.email == teacher.email).first()
                if user:
                    actual_user_id = user.id
            
            # Convert UUID to string for filtering in details JSONB
            teacher_id_str = str(self.teacher_id) if self.teacher_id else None
            
            # Filter by user_id (Integer) and beta context in details
            query = self.db.query(SecurityEvent)
            
            if actual_user_id:
                query = query.filter(SecurityEvent.user_id == actual_user_id)
            
            # Filter by beta teacher context in details JSONB
            # Use PostgreSQL JSONB text search (safe parameterized query)
            if teacher_id_str:
                query = query.filter(
                    text("details::text LIKE :pattern").bindparams(
                        pattern=f'%"beta_teacher_id": "{teacher_id_str}"%'
                    )
                )
            
            if event_type:
                query = query.filter(SecurityEvent.event_type == event_type)
            
            if severity:
                query = query.filter(SecurityEvent.severity == severity)
            
            events = query.order_by(SecurityEvent.created_at.desc()).limit(limit).offset(offset).all()
            
            return [self._event_to_dict(e) for e in events]
            
        except Exception as e:
            self.logger.error(f"Error retrieving security events: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving security events: {str(e)}"
            )
    
    def _event_to_dict(self, event: SecurityEvent) -> Dict[str, Any]:
        """Convert SecurityEvent to dictionary."""
        return {
            "id": event.id,
            "event_type": event.event_type,
            "user_id": event.user_id,
            "ip_address": event.ip_address,
            "details": event.details,
            "description": event.description,
            "severity": event.severity,
            "resource_type": event.resource_type,
            "resource_id": event.resource_id,
            "action": event.action,
            "success": event.success,
            "created_at": event.created_at.isoformat() if event.created_at else None,
            "updated_at": event.updated_at.isoformat() if event.updated_at else None
        }

