"""Activity collaboration manager for physical education."""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from app.core.database import get_db

# Import models
from app.models.activity import (
    Activity,
    ActivityType,
    ActivityCategoryAssociation
)
from app.models.student import Student
from app.models.physical_education.class_ import PhysicalEducationClass
from app.models.physical_education.activity.models import (
    StudentActivityPerformance,
    StudentActivityPreference
)
from app.models.physical_education.pe_enums.pe_types import (
    DifficultyLevel,
    EquipmentRequirement,
    CollaborationType,
    CollaborationLevel,
    CollaborationStatus,
    CollaborationTrigger,
    AccessLevel,
    SharingStatus,
    NotificationType
)

class ActivityCollaborationManager:
    """Service for managing collaboration on physical education activities."""
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ActivityCollaborationManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.logger = logging.getLogger("activity_collaboration_manager")
        self.db = None
        
        # Collaboration settings
        self.settings = {
            "default_access_level": "read",
            "sharing": {
                "enabled": True,
                "max_collaborators": 10,
                "require_approval": True
            },
            "notifications": {
                "enabled": True,
                "channels": ["email", "in_app"],
                "frequency": "real_time"
            },
            "sync": {
                "enabled": True,
                "interval": 300,  # 5 minutes
                "retry_attempts": 3
            }
        }
        
        # Collaboration components
        self.active_collaborations = {}
        self.pending_invitations = {}
        self.access_controls = {}
        self.change_history = []
        
        # Caching and optimization
        self.collaboration_cache = {}
        self.user_permissions_cache = {}
    
    async def initialize(self):
        """Initialize the collaboration manager."""
        try:
            # Get database session using context manager
            db_gen = get_db()
            self.db = await anext(db_gen)
            
            # Initialize collaboration components
            self.initialize_collaboration_components()
            
            self.logger.info("Activity Collaboration Manager initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing Activity Collaboration Manager: {str(e)}")
            raise
    
    async def cleanup(self):
        """Cleanup the collaboration manager."""
        try:
            # Clear all data
            self.active_collaborations.clear()
            self.pending_invitations.clear()
            self.access_controls.clear()
            self.change_history.clear()
            self.collaboration_cache.clear()
            self.user_permissions_cache.clear()
            
            # Reset service references
            self.db = None
            
            self.logger.info("Activity Collaboration Manager cleaned up successfully")
        except Exception as e:
            self.logger.error(f"Error cleaning up Activity Collaboration Manager: {str(e)}")
            raise

    def initialize_collaboration_components(self):
        """Initialize collaboration components."""
        try:
            # Initialize access controls
            self.access_controls = {
                "read": {
                    "view": True,
                    "export": True,
                    "comment": True,
                    "share": False,
                    "edit": False,
                    "delete": False
                },
                "write": {
                    "view": True,
                    "export": True,
                    "comment": True,
                    "share": True,
                    "edit": True,
                    "delete": False
                },
                "admin": {
                    "view": True,
                    "export": True,
                    "comment": True,
                    "share": True,
                    "edit": True,
                    "delete": True
                }
            }
            
            self.logger.info("Collaboration components initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing collaboration components: {str(e)}")
            raise

    async def create_collaboration(
        self,
        activity_id: str,
        collaborator_ids: List[str],
        access_level: str = "read",
        message: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new collaboration for an activity."""
        try:
            if not self.settings["sharing"]["enabled"]:
                raise ValueError("Collaboration sharing is disabled")
            
            if len(collaborator_ids) > self.settings["sharing"]["max_collaborators"]:
                raise ValueError("Maximum number of collaborators exceeded")
            
            if access_level not in self.access_controls:
                raise ValueError(f"Invalid access level: {access_level}")
            
            collaboration = {
                "id": str(uuid.uuid4()),
                "activity_id": activity_id,
                "collaborators": collaborator_ids,
                "access_level": access_level,
                "status": "pending" if self.settings["sharing"]["require_approval"] else "active",
                "created_at": datetime.now().isoformat(),
                "message": message
            }
            
            # Add to active collaborations
            self.active_collaborations[collaboration["id"]] = collaboration
            
            # Send notifications
            if self.settings["notifications"]["enabled"]:
                await self._send_collaboration_notifications(
                    collaboration, "created"
                )
            
            # Update change history
            self._update_change_history(
                collaboration["id"],
                "created",
                {"collaborators": collaborator_ids}
            )
            
            return collaboration
            
        except Exception as e:
            self.logger.error(f"Error creating collaboration: {str(e)}")
            raise

    async def update_collaboration(
        self,
        collaboration_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update an existing collaboration."""
        try:
            if collaboration_id not in self.active_collaborations:
                raise ValueError(f"Collaboration not found: {collaboration_id}")
            
            collaboration = self.active_collaborations[collaboration_id]
            
            # Validate updates
            if "access_level" in updates:
                if updates["access_level"] not in self.access_controls:
                    raise ValueError(f"Invalid access level: {updates['access_level']}")
            
            if "collaborators" in updates:
                if len(updates["collaborators"]) > self.settings["sharing"]["max_collaborators"]:
                    raise ValueError("Maximum number of collaborators exceeded")
            
            # Apply updates
            collaboration.update(updates)
            collaboration["updated_at"] = datetime.now().isoformat()
            
            # Send notifications
            if self.settings["notifications"]["enabled"]:
                await self._send_collaboration_notifications(
                    collaboration, "updated"
                )
            
            # Update change history
            self._update_change_history(
                collaboration_id,
                "updated",
                updates
            )
            
            # Clear cache
            self.collaboration_cache.pop(collaboration_id, None)
            for user_id in collaboration["collaborators"]:
                self.user_permissions_cache.pop(user_id, None)
            
            return collaboration
            
        except Exception as e:
            self.logger.error(f"Error updating collaboration: {str(e)}")
            raise

    async def delete_collaboration(
        self,
        collaboration_id: str
    ) -> None:
        """Delete an existing collaboration."""
        try:
            if collaboration_id not in self.active_collaborations:
                raise ValueError(f"Collaboration not found: {collaboration_id}")
            
            collaboration = self.active_collaborations[collaboration_id]
            
            # Send notifications
            if self.settings["notifications"]["enabled"]:
                await self._send_collaboration_notifications(
                    collaboration, "deleted"
                )
            
            # Update change history
            self._update_change_history(
                collaboration_id,
                "deleted",
                {}
            )
            
            # Remove collaboration
            del self.active_collaborations[collaboration_id]
            
            # Clear cache
            self.collaboration_cache.pop(collaboration_id, None)
            for user_id in collaboration["collaborators"]:
                self.user_permissions_cache.pop(user_id, None)
            
        except Exception as e:
            self.logger.error(f"Error deleting collaboration: {str(e)}")
            raise

    async def get_user_collaborations(
        self,
        user_id: str
    ) -> List[Dict[str, Any]]:
        """Get all collaborations for a user."""
        try:
            # Check cache
            if user_id in self.user_permissions_cache:
                return self.user_permissions_cache[user_id]
            
            collaborations = []
            for collab in self.active_collaborations.values():
                if user_id in collab["collaborators"]:
                    collaborations.append(collab)
            
            # Update cache
            self.user_permissions_cache[user_id] = collaborations
            
            return collaborations
            
        except Exception as e:
            self.logger.error(f"Error getting user collaborations: {str(e)}")
            raise

    async def check_user_permission(
        self,
        user_id: str,
        activity_id: str,
        permission: str
    ) -> bool:
        """Check if a user has a specific permission for an activity."""
        try:
            for collab in self.active_collaborations.values():
                if (collab["activity_id"] == activity_id and
                    user_id in collab["collaborators"] and
                    collab["status"] == "active"):
                    
                    access_level = collab["access_level"]
                    return self.access_controls[access_level].get(permission, False)
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking user permission: {str(e)}")
            raise

    async def _send_collaboration_notifications(
        self,
        collaboration: Dict[str, Any],
        event_type: str
    ) -> None:
        """Send notifications for collaboration events."""
        try:
            if not self.settings["notifications"]["enabled"]:
                return
            
            notification = {
                "type": event_type,
                "collaboration_id": collaboration["id"],
                "activity_id": collaboration["activity_id"],
                "timestamp": datetime.now().isoformat(),
                "recipients": collaboration["collaborators"]
            }
            
            # Send notifications through configured channels
            for channel in self.settings["notifications"]["channels"]:
                if channel == "email":
                    await self._send_email_notification(notification)
                elif channel == "in_app":
                    await self._send_in_app_notification(notification)
            
        except Exception as e:
            self.logger.error(f"Error sending collaboration notifications: {str(e)}")
            raise

    async def _send_email_notification(
        self,
        notification: Dict[str, Any]
    ) -> None:
        """Send email notification."""
        # Implementation depends on email service
        pass

    async def _send_in_app_notification(
        self,
        notification: Dict[str, Any]
    ) -> None:
        """Send in-app notification."""
        # Implementation depends on notification service
        pass

    def _update_change_history(
        self,
        collaboration_id: str,
        event_type: str,
        changes: Dict[str, Any]
    ) -> None:
        """Update collaboration change history."""
        try:
            self.change_history.append({
                "collaboration_id": collaboration_id,
                "event_type": event_type,
                "changes": changes,
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            self.logger.error(f"Error updating change history: {str(e)}")
            raise 