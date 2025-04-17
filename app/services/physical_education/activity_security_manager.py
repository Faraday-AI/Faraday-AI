import logging
from typing import Dict, Any, Optional
from fastapi import Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.physical_education.security_service import SecurityService
from app.services.physical_education.activity_manager import ActivityManager

logger = logging.getLogger(__name__)

class ActivitySecurityManager:
    """Service for managing activity-specific security concerns."""
    
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
        self.logger = logging.getLogger(__name__)
        self.security_service = SecurityService()
        self.activity_manager = ActivityManager(db)
        
        # Security settings
        self.settings = {
            'max_activities_per_student': 100,
            'max_activity_duration': 7200,  # 2 hours in seconds
            'max_file_size': 50 * 1024 * 1024,  # 50MB
            'allowed_file_types': ['mp4', 'mov', 'avi', 'jpg', 'jpeg', 'png'],
            'max_concurrent_activities': 5
        }
        
    async def validate_activity_creation(self, activity_data: Dict[str, Any]) -> bool:
        """Validate activity creation request."""
        try:
            # Check student activity count
            student_activities = await self.activity_manager.get_student_activities(
                activity_data['student_id']
            )
            if len(student_activities) >= self.settings['max_activities_per_student']:
                self.logger.warning(f"Student {activity_data['student_id']} has reached maximum activity limit")
                return False
                
            # Check activity duration
            if activity_data.get('duration', 0) > self.settings['max_activity_duration']:
                self.logger.warning(f"Activity duration exceeds maximum allowed duration")
                return False
                
            # Check file attachments
            if 'attachments' in activity_data:
                for attachment in activity_data['attachments']:
                    if attachment['size'] > self.settings['max_file_size']:
                        self.logger.warning(f"File size exceeds maximum allowed size")
                        return False
                    if attachment['type'] not in self.settings['allowed_file_types']:
                        self.logger.warning(f"File type {attachment['type']} not allowed")
                        return False
                        
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating activity creation: {str(e)}")
            return False
            
    async def validate_activity_update(self, activity_id: str, update_data: Dict[str, Any]) -> bool:
        """Validate activity update request."""
        try:
            # Get current activity
            activity = await self.activity_manager.get_activity(activity_id)
            if not activity:
                return False
                
            # Check if update is allowed
            if 'status' in update_data and update_data['status'] == 'completed':
                # Additional validation for completing activities
                if not self._validate_activity_completion(activity):
                    return False
                    
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating activity update: {str(e)}")
            return False
            
    def _validate_activity_completion(self, activity: Dict[str, Any]) -> bool:
        """Validate activity completion requirements."""
        try:
            # Check if all required fields are present
            required_fields = ['duration', 'performance_metrics', 'feedback']
            for field in required_fields:
                if field not in activity:
                    self.logger.warning(f"Missing required field for completion: {field}")
                    return False
                    
            # Check if performance metrics meet minimum requirements
            if activity['performance_metrics'].get('score', 0) < 0.5:
                self.logger.warning("Activity score below minimum threshold")
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating activity completion: {str(e)}")
            return False
            
    async def check_concurrent_activities(self, student_id: str) -> bool:
        """Check if student has too many concurrent activities."""
        try:
            active_activities = await self.activity_manager.get_active_activities(student_id)
            return len(active_activities) < self.settings['max_concurrent_activities']
            
        except Exception as e:
            self.logger.error(f"Error checking concurrent activities: {str(e)}")
            return False
            
    async def validate_activity_access(self, activity_id: str, user_id: str) -> bool:
        """Validate if user has access to the activity."""
        try:
            activity = await self.activity_manager.get_activity(activity_id)
            if not activity:
                return False
                
            # Check if user is the student or has appropriate role
            if activity['student_id'] == user_id:
                return True
                
            # TODO: Add role-based access control
            return False
            
        except Exception as e:
            self.logger.error(f"Error validating activity access: {str(e)}")
            return False 