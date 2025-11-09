"""
Beta Dashboard Preferences Service
Provides dashboard preferences for beta teachers (widgets, preferences, notifications)
Independent from district-level dashboard preferences.
"""

from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.dashboard.services.dashboard_preferences_service import DashboardPreferencesService
from app.dashboard.models.dashboard_models import DashboardWidget
from app.dashboard.models.notification_models import NotificationPreference
from app.models.teacher_registration import TeacherRegistration
from app.models.core.user import User
from app.dashboard.models.user import DashboardUser


class BetaDashboardPreferencesService(DashboardPreferencesService):
    """Dashboard preferences service for beta teachers - filters to teacher's preferences."""
    
    def __init__(self, db: Session, teacher_id: Union[str, int]):
        super().__init__(db)
        self.teacher_id = teacher_id
        self.logger = __import__('logging').getLogger("beta_dashboard_preferences_service")
    
    def _get_teacher_user_id(self) -> Optional[int]:
        """Get the dashboard_user.id for this beta teacher."""
        teacher = self.db.query(TeacherRegistration).filter(
            TeacherRegistration.id == self.teacher_id
        ).first()
        
        if not teacher or not teacher.email:
            return None
        
        # Get User from core.users table
        user = self.db.query(User).filter(User.email == teacher.email).first()
        if not user:
            return None
        
        # Get DashboardUser from dashboard_users table using core_user_id
        dashboard_user = self.db.query(DashboardUser).filter(
            DashboardUser.core_user_id == user.id
        ).first()
        
        if dashboard_user:
            return dashboard_user.id
        
        return None
    
    def _get_teacher_core_user_id(self) -> Optional[int]:
        """Get the core users.id for this beta teacher."""
        teacher = self.db.query(TeacherRegistration).filter(
            TeacherRegistration.id == self.teacher_id
        ).first()
        
        if not teacher or not teacher.email:
            return None
        
        # Get User from core.users table
        user = self.db.query(User).filter(User.email == teacher.email).first()
        if not user:
            return None
        
        return user.id
    
    async def get_widgets(
        self,
        user_id: Optional[int] = None,
        dashboard_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        limit: int = 100
    ) -> List[Dict]:
        """Get dashboard widgets for beta teacher (filtered by teacher's user_id)."""
        # Get the core user.id for this teacher (widgets.user_id points to users.id)
        teacher_core_user_id = self._get_teacher_core_user_id()
        
        if not teacher_core_user_id:
            return []  # No user, return empty
        
        # Override user_id to ensure only this teacher's widgets are returned
        if user_id and user_id != teacher_core_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Beta teachers can only access their own widgets"
            )
        
        # Get widgets filtered by teacher's core user_id and beta metadata
        widgets = await super().get_widgets(
            user_id=teacher_core_user_id,
            dashboard_id=dashboard_id,
            is_active=is_active,
            limit=limit
        )
        
        # Filter to only beta widgets (those with beta_system in meta_data)
        beta_widgets = []
        for widget in widgets:
            meta_data = widget.get('meta_data', {})
            if meta_data.get('beta_system') is True or meta_data.get('beta_teacher_id') == str(self.teacher_id):
                beta_widgets.append(widget)
        
        return beta_widgets
    
    async def create_widget(self, widget_data: Dict) -> Dict:
        """Create a new dashboard widget for beta teacher."""
        # Get the core user.id for this teacher (widgets.user_id points to users.id, not dashboard_users.id)
        teacher_core_user_id = self._get_teacher_core_user_id()
        
        if not teacher_core_user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Beta teacher user not found"
            )
        
        # Ensure beta teacher can only create widgets for themselves
        if widget_data.get('user_id') and widget_data.get('user_id') != teacher_core_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Beta teachers can only create widgets for themselves"
            )
        
        # Set user_id to teacher's core user.id (widgets.user_id FK points to users.id)
        widget_data['user_id'] = teacher_core_user_id
        
        # Add beta metadata
        if 'meta_data' not in widget_data:
            widget_data['meta_data'] = {}
        
        widget_data['meta_data']['beta_teacher_id'] = str(self.teacher_id)
        widget_data['meta_data']['beta_system'] = True
        
        result = await super().create_widget(widget_data)
        
        # Add beta fields to response
        result['beta_teacher_id'] = str(self.teacher_id)
        result['beta_system'] = True
        
        return result
    
    async def get_user_preferences(self, user_id: Optional[int] = None) -> Dict:
        """Get user preferences for beta teacher."""
        # Get the core user_id for this teacher
        teacher_core_user_id = self._get_teacher_core_user_id()
        
        if not teacher_core_user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Beta teacher user not found"
            )
        
        # Override user_id to ensure only this teacher's preferences are returned
        if user_id and user_id != teacher_core_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Beta teachers can only access their own preferences"
            )
        
        result = await super().get_user_preferences(teacher_core_user_id)
        
        # Add beta metadata
        result['beta_teacher_id'] = str(self.teacher_id)
        result['beta_system'] = True
        
        return result
    
    async def update_user_preferences(self, user_id: Optional[int] = None, preferences: Dict = None) -> Dict:
        """Update user preferences for beta teacher."""
        # Get the core user_id for this teacher
        teacher_core_user_id = self._get_teacher_core_user_id()
        
        if not teacher_core_user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Beta teacher user not found"
            )
        
        # Override user_id to ensure only this teacher's preferences are updated
        if user_id and user_id != teacher_core_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Beta teachers can only update their own preferences"
            )
        
        # Add beta metadata to preferences
        if preferences:
            preferences['beta_teacher_id'] = str(self.teacher_id)
            preferences['beta_system'] = True
        
        result = await super().update_user_preferences(teacher_core_user_id, preferences or {})
        
        # Add beta fields to response
        result['beta_teacher_id'] = str(self.teacher_id)
        result['beta_system'] = True
        
        return result
    
    async def get_notification_preferences(
        self,
        user_id: Optional[int] = None,
        channel: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """Get notification preferences for beta teacher."""
        # Get the core user_id for this teacher
        teacher_core_user_id = self._get_teacher_core_user_id()
        
        if not teacher_core_user_id:
            return []  # No user, return empty
        
        # Override user_id to ensure only this teacher's preferences are returned
        if user_id and user_id != teacher_core_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Beta teachers can only access their own notification preferences"
            )
        
        prefs = await super().get_notification_preferences(
            user_id=teacher_core_user_id,
            channel=channel,
            limit=limit
        )
        
        # Add beta metadata to each preference
        for pref in prefs:
            pref['beta_teacher_id'] = str(self.teacher_id)
            pref['beta_system'] = True
        
        return prefs
    
    async def create_notification_preference(self, pref_data: Dict) -> Dict:
        """Create a new notification preference for beta teacher."""
        # Get the core user_id for this teacher
        teacher_core_user_id = self._get_teacher_core_user_id()
        
        if not teacher_core_user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Beta teacher user not found"
            )
        
        # Ensure beta teacher can only create preferences for themselves
        if pref_data.get('user_id') and pref_data.get('user_id') != teacher_core_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Beta teachers can only create notification preferences for themselves"
            )
        
        # Set user_id to teacher's core user_id
        pref_data['user_id'] = teacher_core_user_id
        
        result = await super().create_notification_preference(pref_data)
        
        # Add beta metadata
        result['beta_teacher_id'] = str(self.teacher_id)
        result['beta_system'] = True
        
        return result
    
    async def migrate_existing_preferences_data(self) -> Dict:
        """Migrate existing preferences data for beta teachers."""
        try:
            from app.scripts.seed_data.migrate_phase6_data import migrate_phase6_data
            
            results = migrate_phase6_data(self.db)
            
            # Filter results to show beta-specific migrations
            beta_results = {
                "beta_widgets": results.get("beta_widgets", 0),
                "teacher_preferences": results.get("teacher_preferences", 0),
                "total": results.get("beta_widgets", 0) + results.get("teacher_preferences", 0)
            }
            
            return {
                "success": True,
                "message": "Beta preferences migration completed",
                "results": beta_results
            }
        except Exception as e:
            self.logger.error(f"Error migrating beta preferences data: {str(e)}")
            return {
                "success": False,
                "message": f"Error migrating beta preferences data: {str(e)}",
                "results": {}
            }

