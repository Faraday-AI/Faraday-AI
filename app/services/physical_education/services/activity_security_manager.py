"""
Activity Security Manager Service

This module provides security functionality for physical education activities.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.core.database import get_db

logger = logging.getLogger(__name__)

class SecurityViolation:
    """Model for security violations."""
    
    def __init__(
        self,
        violation_type: str,
        severity: str,
        description: str,
        user_id: Optional[str] = None,
        activity_id: Optional[str] = None
    ):
        self.violation_type = violation_type
        self.severity = severity
        self.description = description
        self.user_id = user_id
        self.activity_id = activity_id
        self.timestamp = datetime.utcnow()

class ActivitySecurityManager:
    """Service for managing security for physical education activities."""
    
    def __init__(self, db: Session = None):
        self.logger = logging.getLogger("activity_security_manager")
        self.db = db
        self._violations = []
        self._blocked_users = set()
        self._suspicious_activities = []
        
    async def validate_activity_access(
        self,
        user_id: str,
        activity_id: str,
        action: str
    ) -> Dict[str, Any]:
        """Validate if a user can access an activity."""
        try:
            # Check if user is blocked
            if user_id in self._blocked_users:
                return {
                    "allowed": False,
                    "reason": "User is blocked due to security violations",
                    "violation_type": "access_denied"
                }
            
            # Mock validation logic
            # In a real implementation, this would check permissions, roles, etc.
            allowed = True
            reason = None
            violation_type = None
            
            # Example validation rules
            if action == "delete" and not await self._has_admin_role(user_id):
                allowed = False
                reason = "Insufficient permissions for delete action"
                violation_type = "permission_denied"
            
            if not allowed:
                await self._record_violation(
                    violation_type or "access_denied",
                    "medium",
                    f"Access denied for {action} on activity {activity_id}",
                    user_id,
                    activity_id
                )
            
            return {
                "allowed": allowed,
                "reason": reason,
                "violation_type": violation_type
            }
            
        except Exception as e:
            self.logger.error(f"Error validating activity access: {str(e)}")
            return {"allowed": False, "reason": "Validation error", "violation_type": "error"}
    
    async def validate_concurrent_activity_limits(
        self,
        user_id: str,
        max_concurrent: int = 5
    ) -> Dict[str, Any]:
        """Validate concurrent activity limits for a user."""
        try:
            # Mock implementation - in real system, this would check active sessions
            current_activities = await self._get_user_active_activities(user_id)
            
            if len(current_activities) >= max_concurrent:
                await self._record_violation(
                    "concurrent_limit_exceeded",
                    "low",
                    f"User exceeded concurrent activity limit of {max_concurrent}",
                    user_id
                )
                
                return {
                    "allowed": False,
                    "reason": f"Maximum concurrent activities ({max_concurrent}) exceeded",
                    "current_count": len(current_activities),
                    "max_allowed": max_concurrent
                }
            
            return {
                "allowed": True,
                "current_count": len(current_activities),
                "max_allowed": max_concurrent
            }
            
        except Exception as e:
            self.logger.error(f"Error validating concurrent activity limits: {str(e)}")
            return {"allowed": False, "reason": "Validation error"}
    
    async def validate_file_upload(
        self,
        user_id: str,
        file_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate file uploads for activities."""
        try:
            # Mock file validation
            allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.mp4', '.mov', '.pdf']
            max_size_mb = 50
            
            file_extension = file_info.get('extension', '').lower()
            file_size_mb = file_info.get('size_mb', 0)
            
            if file_extension not in allowed_extensions:
                await self._record_violation(
                    "invalid_file_type",
                    "medium",
                    f"Attempted upload of disallowed file type: {file_extension}",
                    user_id
                )
                
                return {
                    "allowed": False,
                    "reason": f"File type {file_extension} not allowed",
                    "allowed_types": allowed_extensions
                }
            
            if file_size_mb > max_size_mb:
                await self._record_violation(
                    "file_too_large",
                    "low",
                    f"Attempted upload of oversized file: {file_size_mb}MB",
                    user_id
                )
                
                return {
                    "allowed": False,
                    "reason": f"File size {file_size_mb}MB exceeds maximum of {max_size_mb}MB",
                    "max_size_mb": max_size_mb
                }
            
            return {
                "allowed": True,
                "file_extension": file_extension,
                "file_size_mb": file_size_mb
            }
            
        except Exception as e:
            self.logger.error(f"Error validating file upload: {str(e)}")
            return {"allowed": False, "reason": "Validation error"}
    
    async def validate_user_permissions(
        self,
        user_id: str,
        required_permissions: List[str]
    ) -> Dict[str, Any]:
        """Validate user permissions for activities."""
        try:
            # Mock permission validation
            user_permissions = await self._get_user_permissions(user_id)
            
            missing_permissions = [
                perm for perm in required_permissions
                if perm not in user_permissions
            ]
            
            if missing_permissions:
                await self._record_violation(
                    "insufficient_permissions",
                    "medium",
                    f"User lacks required permissions: {missing_permissions}",
                    user_id
                )
                
                return {
                    "allowed": False,
                    "reason": f"Missing permissions: {missing_permissions}",
                    "missing_permissions": missing_permissions,
                    "user_permissions": user_permissions
                }
            
            return {
                "allowed": True,
                "user_permissions": user_permissions
            }
            
        except Exception as e:
            self.logger.error(f"Error validating user permissions: {str(e)}")
            return {"allowed": False, "reason": "Validation error"}
    
    async def get_security_violations(
        self,
        user_id: Optional[str] = None,
        severity: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get security violations with optional filtering."""
        try:
            violations = self._violations
            
            if user_id:
                violations = [v for v in violations if v.user_id == user_id]
            
            if severity:
                violations = [v for v in violations if v.severity == severity]
            
            # Sort by timestamp (newest first) and limit results
            violations.sort(key=lambda x: x.timestamp, reverse=True)
            violations = violations[:limit]
            
            return [
                {
                    "violation_type": v.violation_type,
                    "severity": v.severity,
                    "description": v.description,
                    "user_id": v.user_id,
                    "activity_id": v.activity_id,
                    "timestamp": v.timestamp.isoformat()
                }
                for v in violations
            ]
            
        except Exception as e:
            self.logger.error(f"Error getting security violations: {str(e)}")
            return []
    
    async def block_user(
        self,
        user_id: str,
        reason: str,
        duration_hours: Optional[int] = None
    ) -> bool:
        """Block a user due to security violations."""
        try:
            self._blocked_users.add(user_id)
            
            await self._record_violation(
                "user_blocked",
                "high",
                f"User blocked: {reason}",
                user_id
            )
            
            self.logger.warning(f"User {user_id} blocked: {reason}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error blocking user: {str(e)}")
            return False
    
    async def unblock_user(
        self,
        user_id: str
    ) -> bool:
        """Unblock a user."""
        try:
            if user_id in self._blocked_users:
                self._blocked_users.remove(user_id)
                self.logger.info(f"User {user_id} unblocked")
            return True
            
        except Exception as e:
            self.logger.error(f"Error unblocking user: {str(e)}")
            return False
    
    async def get_blocked_users(self) -> List[str]:
        """Get list of blocked users."""
        return list(self._blocked_users)
    
    # Helper methods (mock implementations)
    async def _has_admin_role(self, user_id: str) -> bool:
        """Check if user has admin role."""
        # Mock implementation
        return user_id.startswith("admin_")
    
    async def _get_user_active_activities(self, user_id: str) -> List[str]:
        """Get user's active activities."""
        # Mock implementation
        return [f"activity_{i}" for i in range(2)]  # Mock 2 active activities
    
    async def _get_user_permissions(self, user_id: str) -> List[str]:
        """Get user's permissions."""
        # Mock implementation
        base_permissions = ["view_activities", "participate_activities"]
        if user_id.startswith("teacher_"):
            base_permissions.extend(["create_activities", "edit_activities"])
        if user_id.startswith("admin_"):
            base_permissions.extend(["delete_activities", "manage_users"])
        return base_permissions
    
    async def _record_violation(
        self,
        violation_type: str,
        severity: str,
        description: str,
        user_id: Optional[str] = None,
        activity_id: Optional[str] = None
    ):
        """Record a security violation."""
        violation = SecurityViolation(
            violation_type=violation_type,
            severity=severity,
            description=description,
            user_id=user_id,
            activity_id=activity_id
        )
        self._violations.append(violation)
        
        # Log violation
        self.logger.warning(f"Security violation: {violation_type} - {description}")
        
        # Auto-block for high severity violations
        if severity == "high" and user_id:
            await self.block_user(user_id, f"High severity violation: {violation_type}") 