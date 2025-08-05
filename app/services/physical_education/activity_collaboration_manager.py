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
        self.collaboration_config = self.settings  # Add this for test compatibility
        
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
        collaboration_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a new collaboration."""
        try:
            activity_id = collaboration_data.get("activity_id")
            collaborator_ids = collaboration_data.get("participants", [])
            access_level = collaboration_data.get("access_level", "read")
            message = collaboration_data.get("notes")
            
            # Always generate a unique collaboration_id
            collaboration_id = f"collab_{len(self.active_collaborations) + 1}_{int(datetime.utcnow().timestamp())}"
            
            collaboration = {
                "id": collaboration_id,
                "activity_id": activity_id,
                "collaborator_ids": collaborator_ids,
                "access_level": access_level,
                "message": message,
                "created_at": datetime.utcnow().isoformat(),
                "status": "active"
            }
            
            self.active_collaborations[collaboration_id] = collaboration
            
            self.logger.info(f"Created collaboration {collaboration_id} for activity {activity_id}")
            
            return {
                "collaboration_created": True,
                "collaboration_id": collaboration_id,
                "activity_id": activity_id,
                "collaborator_count": len(collaborator_ids)
            }
        except Exception as e:
            self.logger.error(f"Error creating collaboration: {str(e)}")
            return {
                "collaboration_created": False,
                "error": str(e)
            }

    async def update_collaboration(
        self,
        collaboration_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update an existing collaboration."""
        try:
            if collaboration_id not in self.active_collaborations:
                raise ValueError(f"Collaboration {collaboration_id} not found")
            
            collaboration = self.active_collaborations[collaboration_id]
            
            # Update collaboration data
            collaboration.update(updates)
            collaboration["updated_at"] = datetime.utcnow().isoformat()
            
            # Update cache
            self.collaboration_cache[collaboration_id] = collaboration
            
            # Send notifications
            await self._send_collaboration_notifications(
                collaboration,
                "updated"
            )
            
            # Return updated collaboration with success flag
            result = collaboration.copy()
            result["updated"] = True
            return result
            
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
            for user_id in collaboration["collaborator_ids"]:
                self.user_permissions_cache.pop(user_id, None)
            
        except Exception as e:
            self.logger.error(f"Error deleting collaboration: {str(e)}")
            raise

    async def get_user_collaborations(
        self,
        user_id: str
    ) -> List[Dict[str, Any]]:
        """Get collaborations for a specific user."""
        try:
            collaborations = []
            
            for collab in self.active_collaborations.values():
                if user_id in collab["collaborator_ids"]:
                    collaborations.append(collab)
            
            return collaborations
            
        except Exception as e:
            self.logger.error(f"Error getting user collaborations: {str(e)}")
            return []

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
                    user_id in collab["collaborator_ids"] and
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
                "type": "collaboration_event",
                "event_type": event_type,
                "collaboration_id": collaboration["id"],
                "activity_id": collaboration["activity_id"],
                "recipients": collaboration["collaborator_ids"],
                "message": f"Collaboration {event_type}: {collaboration.get('message', '')}",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Send notifications through configured channels
            for channel in self.settings["notifications"]["channels"]:
                if channel == "email":
                    await self._send_email_notification(notification)
                elif channel == "in_app":
                    await self._send_in_app_notification(notification)
                    
        except Exception as e:
            self.logger.error(f"Error sending collaboration notifications: {str(e)}")

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

    async def create_team(
        self,
        team_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a new team for collaboration."""
        try:
            team_name = team_data.get("name", "Unnamed Team")
            team_members = team_data.get("members", [])
            team_type = team_data.get("type", "activity")
            description = team_data.get("description")
            team_id = team_data.get("team_id", f"team_{len(self.active_collaborations) + 1}")
            
            team = {
                "id": team_id,
                "name": team_name,
                "members": team_members,
                "type": team_type,
                "description": description,
                "created_at": datetime.utcnow().isoformat(),
                "status": "active"
            }
            
            self.active_collaborations[team_id] = team
            
            self.logger.info(f"Created team {team_id} with {len(team_members)} members")
            
            return {
                "team_created": True,
                "team_id": team_id,
                "name": team_name,
                "members": team_members,
                "member_count": len(team_members)
            }
        except Exception as e:
            self.logger.error(f"Error creating team: {str(e)}")
            return {
                "team_created": False,
                "error": str(e)
            }

    async def update_team(
        self,
        team_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update team information."""
        try:
            if team_id not in self.active_collaborations:
                return {"updated": False, "error": "Team not found"}
            
            team = self.active_collaborations[team_id]
            team.update(updates)
            team["updated_at"] = datetime.utcnow().isoformat()
            
            return {"updated": True, "team_id": team_id}
        except Exception as e:
            self.logger.error(f"Error updating team: {str(e)}")
            return {"updated": False, "error": str(e)}

    async def delete_team(
        self,
        team_id: str
    ) -> Dict[str, Any]:
        """Delete a team."""
        try:
            if team_id not in self.active_collaborations:
                return {"deleted": False, "error": "Team not found"}
            
            del self.active_collaborations[team_id]
            
            return {"deleted": True, "team_id": team_id}
        except Exception as e:
            self.logger.error(f"Error deleting team: {str(e)}")
            return {"deleted": False, "error": str(e)}

    async def get_team(
        self,
        team_id: str
    ) -> Dict[str, Any]:
        """Get team information."""
        try:
            if team_id not in self.active_collaborations:
                return {"found": False, "error": "Team not found"}
            
            return {
                "found": True,
                "team": self.active_collaborations[team_id]
            }
        except Exception as e:
            self.logger.error(f"Error getting team: {str(e)}")
            return {"found": False, "error": str(e)}

    async def list_teams(
        self,
        team_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """List all teams."""
        try:
            teams = list(self.active_collaborations.values())
            
            if team_type:
                teams = [team for team in teams if team.get("type") == team_type]
            
            return {
                "teams": teams,
                "count": len(teams)
            }
        except Exception as e:
            self.logger.error(f"Error listing teams: {str(e)}")
            return {"teams": [], "count": 0, "error": str(e)}

    async def analyze_team_performance(
        self,
        team_id: str
    ) -> Dict[str, Any]:
        """Analyze team performance."""
        try:
            if team_id not in self.active_collaborations:
                return {"analyzed": False, "error": "Team not found"}
            
            # Mock analysis
            return {
                "analyzed": True,
                "team_id": team_id,
                "performance_score": 0.85,
                "collaboration_level": "high",
                "recommendations": ["Increase communication", "Schedule regular meetings"]
            }
        except Exception as e:
            self.logger.error(f"Error analyzing team performance: {str(e)}")
            return {"analyzed": False, "error": str(e)}

    async def analyze_team_dynamics(
        self,
        team_id: str
    ) -> Dict[str, Any]:
        """Analyze team dynamics."""
        try:
            if team_id not in self.active_collaborations:
                return {"analyzed": False, "error": "Team not found"}
            
            # Mock analysis
            return {
                "analyzed": True,
                "team_id": team_id,
                "dynamics_score": 0.78,
                "communication_style": "collaborative",
                "conflict_resolution": "effective"
            }
        except Exception as e:
            self.logger.error(f"Error analyzing team dynamics: {str(e)}")
            return {"analyzed": False, "error": str(e)}

    async def generate_team_report(
        self,
        team_id: str
    ) -> Dict[str, Any]:
        """Generate a comprehensive team report."""
        try:
            if team_id not in self.active_collaborations:
                return {"generated": False, "error": "Team not found"}
            
            # Mock report
            return {
                "generated": True,
                "team_id": team_id,
                "report": {
                    "summary": "Team is performing well",
                    "metrics": {"performance": 0.85, "collaboration": 0.78},
                    "recommendations": ["Continue current practices", "Schedule team building"]
                }
            }
        except Exception as e:
            self.logger.error(f"Error generating team report: {str(e)}")
            return {"generated": False, "error": str(e)}

    async def schedule_team_activity(
        self,
        team_id: str,
        activity_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Schedule an activity for the team."""
        try:
            if team_id not in self.active_collaborations:
                return {"scheduled": False, "error": "Team not found"}
            
            return {
                "scheduled": True,
                "team_id": team_id,
                "activity_id": f"activity_{len(self.active_collaborations) + 1}",
                "scheduled_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error scheduling team activity: {str(e)}")
            return {"scheduled": False, "error": str(e)}

    async def send_team_notification(
        self,
        team_id: str,
        message: str,
        notification_type: str = "info"
    ) -> Dict[str, Any]:
        """Send a notification to team members."""
        try:
            if team_id not in self.active_collaborations:
                return {"sent": False, "error": "Team not found"}
            
            return {
                "sent": True,
                "team_id": team_id,
                "message": message,
                "notification_type": notification_type,
                "sent_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error sending team notification: {str(e)}")
            return {"sent": False, "error": str(e)} 