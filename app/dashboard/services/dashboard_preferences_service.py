"""
Dashboard Preferences Service for Phase 6

This service handles dashboard preferences, widgets, notifications, themes, and filters
including migration from Phase 6 source tables to dashboard_* tables.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from fastapi import HTTPException, status
import logging
import json

from app.dashboard.models.dashboard_models import (
    DashboardWidget,
    Dashboard,
    DashboardShare,
    DashboardFilter,
    DashboardAnalytics,
    WidgetType,
    WidgetLayout
)
from app.dashboard.models.notification_models import (
    NotificationPreference,
    NotificationChannel,
    NotificationType,
    NotificationPriority
)
from app.dashboard.models.user import DashboardUser

logger = logging.getLogger(__name__)


class DashboardPreferencesService:
    """Service for managing dashboard preferences with migration support."""
    
    def __init__(self, db: Session):
        self.db = db
        self.logger = logger
    
    # ==================== WIDGET OPERATIONS ====================
    
    async def get_widgets(
        self,
        user_id: Optional[int] = None,
        dashboard_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        limit: int = 100
    ) -> List[Dict]:
        """Get dashboard widget records."""
        try:
            query = self.db.query(DashboardWidget)
            
            if user_id:
                query = query.filter(DashboardWidget.user_id == user_id)
            if dashboard_id:
                query = query.filter(DashboardWidget.dashboard_id == dashboard_id)
            if is_active is not None:
                query = query.filter(DashboardWidget.is_active == is_active)
            
            widgets = query.limit(limit).all()
            
            return [
                {
                    "id": w.id,
                    "name": w.name,
                    "description": w.description,
                    "widget_type": w.widget_type.value if hasattr(w.widget_type, 'value') else str(w.widget_type),
                    "layout_position": w.layout_position.value if hasattr(w.layout_position, 'value') else str(w.layout_position),
                    "size": w.size,
                    "configuration": w.configuration,
                    "refresh_interval": w.refresh_interval,
                    "is_active": w.is_active,
                    "is_visible": w.is_visible,
                    "user_id": w.user_id,
                    "dashboard_id": w.dashboard_id,
                    "meta_data": w.meta_data,
                    "created_at": w.created_at.isoformat() if w.created_at else None,
                    "updated_at": w.updated_at.isoformat() if w.updated_at else None
                }
                for w in widgets
            ]
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving widgets: {str(e)}"
            )
    
    async def create_widget(self, widget_data: Dict) -> Dict:
        """Create a new dashboard widget."""
        try:
            required_fields = ['name', 'widget_type', 'layout_position', 'size', 'configuration', 'dashboard_id']
            missing_fields = [field for field in required_fields if field not in widget_data]
            if missing_fields:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Missing required fields: {', '.join(missing_fields)}"
                )
            
            # Convert string to enum if needed
            widget_type = widget_data['widget_type']
            if isinstance(widget_type, str):
                try:
                    widget_type = WidgetType[widget_type.upper()]
                except KeyError:
                    widget_type = WidgetType.CUSTOM
            
            layout_position = widget_data['layout_position']
            if isinstance(layout_position, str):
                try:
                    layout_position = WidgetLayout[layout_position.upper()]
                except KeyError:
                    layout_position = WidgetLayout.CENTER
            
            new_widget = DashboardWidget(
                name=widget_data['name'],
                description=widget_data.get('description'),
                widget_type=widget_type,
                layout_position=layout_position,
                size=widget_data['size'],
                configuration=widget_data['configuration'],
                refresh_interval=widget_data.get('refresh_interval'),
                is_active=widget_data.get('is_active', True),
                is_visible=widget_data.get('is_visible', True),
                user_id=widget_data.get('user_id'),
                dashboard_id=widget_data['dashboard_id'],
                project_id=widget_data.get('project_id'),
                organization_id=widget_data.get('organization_id'),
                meta_data=widget_data.get('meta_data')
            )
            
            self.db.add(new_widget)
            self.db.commit()
            self.db.refresh(new_widget)
            
            return {
                "id": new_widget.id,
                "name": new_widget.name,
                "description": new_widget.description,
                "widget_type": new_widget.widget_type.value if hasattr(new_widget.widget_type, 'value') else str(new_widget.widget_type),
                "layout_position": new_widget.layout_position.value if hasattr(new_widget.layout_position, 'value') else str(new_widget.layout_position),
                "size": new_widget.size,
                "configuration": new_widget.configuration,
                "is_active": new_widget.is_active,
                "user_id": new_widget.user_id,
                "dashboard_id": new_widget.dashboard_id,
                "created_at": new_widget.created_at.isoformat() if new_widget.created_at else None
            }
        except HTTPException:
            raise
        except IntegrityError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error creating widget: {str(e)}"
            )
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating widget: {str(e)}"
            )
    
    async def update_widget(self, widget_id: int, widget_data: Dict) -> Dict:
        """Update an existing dashboard widget."""
        try:
            widget = self.db.query(DashboardWidget).filter(DashboardWidget.id == widget_id).first()
            if not widget:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Widget {widget_id} not found"
                )
            
            if 'name' in widget_data:
                widget.name = widget_data['name']
            if 'description' in widget_data:
                widget.description = widget_data['description']
            if 'widget_type' in widget_data:
                widget_type = widget_data['widget_type']
                if isinstance(widget_type, str):
                    try:
                        widget.widget_type = WidgetType[widget_type.upper()]
                    except KeyError:
                        widget.widget_type = WidgetType.CUSTOM
                else:
                    widget.widget_type = widget_type
            if 'layout_position' in widget_data:
                layout_position = widget_data['layout_position']
                if isinstance(layout_position, str):
                    try:
                        widget.layout_position = WidgetLayout[layout_position.upper()]
                    except KeyError:
                        widget.layout_position = WidgetLayout.CENTER
                else:
                    widget.layout_position = layout_position
            if 'size' in widget_data:
                widget.size = widget_data['size']
            if 'configuration' in widget_data:
                widget.configuration = widget_data['configuration']
            if 'is_active' in widget_data:
                widget.is_active = widget_data['is_active']
            if 'is_visible' in widget_data:
                widget.is_visible = widget_data['is_visible']
            if 'meta_data' in widget_data:
                widget.meta_data = widget_data['meta_data']
            
            widget.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(widget)
            
            return {
                "id": widget.id,
                "name": widget.name,
                "description": widget.description,
                "widget_type": widget.widget_type.value if hasattr(widget.widget_type, 'value') else str(widget.widget_type),
                "is_active": widget.is_active,
                "updated_at": widget.updated_at.isoformat() if widget.updated_at else None
            }
        except HTTPException:
            raise
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error updating widget: {str(e)}"
            )
    
    async def delete_widget(self, widget_id: int) -> Dict:
        """Delete a dashboard widget (soft delete)."""
        try:
            widget = self.db.query(DashboardWidget).filter(DashboardWidget.id == widget_id).first()
            if not widget:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Widget {widget_id} not found"
                )
            
            widget.is_active = False
            widget.updated_at = datetime.utcnow()
            
            self.db.commit()
            
            return {
                "success": True,
                "message": f"Widget {widget_id} deleted successfully"
            }
        except HTTPException:
            raise
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error deleting widget: {str(e)}"
            )
    
    # ==================== USER PREFERENCES OPERATIONS ====================
    
    async def get_user_preferences(self, user_id: int) -> Dict:
        """Get user preferences from dashboard_users.preferences JSON field."""
        try:
            dashboard_user = self.db.query(DashboardUser).filter(
                DashboardUser.core_user_id == user_id
            ).first()
            
            if not dashboard_user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Dashboard user not found for user_id {user_id}"
                )
            
            preferences = dashboard_user.preferences or {}
            
            return {
                "user_id": user_id,
                "preferences": preferences,
                "dashboard_user_id": dashboard_user.id
            }
        except HTTPException:
            raise
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving user preferences: {str(e)}"
            )
    
    async def update_user_preferences(self, user_id: int, preferences: Dict) -> Dict:
        """Update user preferences in dashboard_users.preferences JSON field."""
        try:
            dashboard_user = self.db.query(DashboardUser).filter(
                DashboardUser.core_user_id == user_id
            ).first()
            
            if not dashboard_user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Dashboard user not found for user_id {user_id}"
                )
            
            # Merge with existing preferences
            existing_prefs = dashboard_user.preferences or {}
            existing_prefs.update(preferences)
            dashboard_user.preferences = existing_prefs
            
            self.db.commit()
            self.db.refresh(dashboard_user)
            
            return {
                "success": True,
                "user_id": user_id,
                "preferences": dashboard_user.preferences,
                "message": "User preferences updated successfully"
            }
        except HTTPException:
            raise
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error updating user preferences: {str(e)}"
            )
    
    # ==================== NOTIFICATION PREFERENCES OPERATIONS ====================
    
    async def get_notification_preferences(
        self,
        user_id: int,
        channel: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """Get notification preferences for a user."""
        try:
            query = self.db.query(NotificationPreference).filter(
                NotificationPreference.user_id == user_id
            )
            
            if channel:
                try:
                    channel_enum = NotificationChannel[channel.upper()]
                    query = query.filter(NotificationPreference.channel == channel_enum)
                except KeyError:
                    pass  # Invalid channel, return empty
            
            prefs = query.limit(limit).all()
            
            return [
                {
                    "id": p.id,
                    "user_id": p.user_id,
                    "channel": p.channel.value if hasattr(p.channel, 'value') else str(p.channel),
                    "type": p.type.value if hasattr(p.type, 'value') else str(p.type),
                    "enabled": p.enabled,
                    "priority_threshold": p.priority_threshold.value if hasattr(p.priority_threshold, 'value') else str(p.priority_threshold),
                    "quiet_hours_start": p.quiet_hours_start,
                    "quiet_hours_end": p.quiet_hours_end,
                    "timezone": p.timezone,
                    "batching_enabled": p.batching_enabled,
                    "batching_interval": p.batching_interval
                }
                for p in prefs
            ]
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving notification preferences: {str(e)}"
            )
    
    async def create_notification_preference(self, pref_data: Dict) -> Dict:
        """Create a new notification preference."""
        try:
            required_fields = ['user_id', 'channel', 'type']
            missing_fields = [field for field in required_fields if field not in pref_data]
            if missing_fields:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Missing required fields: {', '.join(missing_fields)}"
                )
            
            # Convert strings to enums (string enums: use __members__ to find by value)
            channel = pref_data['channel']
            if isinstance(channel, str):
                channel_lower = channel.lower()
                # Find enum member by value using __members__
                channel_enum = None
                if hasattr(NotificationChannel, '__members__'):
                    for name, member in NotificationChannel.__members__.items():
                        if member.value == channel_lower:
                            channel_enum = member
                            break
                
                if channel_enum is None:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid channel: {channel}. Must be one of: email, push, sms, websocket, in_app"
                    )
                channel = channel_enum
            
            notif_type = pref_data['type']
            if isinstance(notif_type, str):
                type_lower = notif_type.lower()
                # Find enum member by value using __members__
                type_enum = None
                if hasattr(NotificationType, '__members__'):
                    for name, member in NotificationType.__members__.items():
                        if member.value == type_lower:
                            type_enum = member
                            break
                
                if type_enum is None:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid notification type: {notif_type}. Must be one of: system, alert, update, reminder, achievement"
                    )
                notif_type = type_enum
            
            priority = pref_data.get('priority_threshold', 'low')
            if isinstance(priority, str):
                priority_lower = priority.lower()
                # Find enum member by value using __members__
                priority_enum = None
                if hasattr(NotificationPriority, '__members__'):
                    for name, member in NotificationPriority.__members__.items():
                        if member.value == priority_lower:
                            priority_enum = member
                            break
                
                if priority_enum is None:
                    priority_enum = NotificationPriority.LOW
                priority = priority_enum
            
            new_pref = NotificationPreference(
                user_id=pref_data['user_id'],
                channel=channel,
                type=notif_type,
                enabled=pref_data.get('enabled', True),
                priority_threshold=priority,
                quiet_hours_start=pref_data.get('quiet_hours_start'),
                quiet_hours_end=pref_data.get('quiet_hours_end'),
                timezone=pref_data.get('timezone', 'UTC'),
                batching_enabled=pref_data.get('batching_enabled', False),
                batching_interval=pref_data.get('batching_interval', 5)
            )
            
            self.db.add(new_pref)
            self.db.commit()
            self.db.refresh(new_pref)
            
            return {
                "id": new_pref.id,
                "user_id": new_pref.user_id,
                "channel": new_pref.channel.value if hasattr(new_pref.channel, 'value') else str(new_pref.channel),
                "type": new_pref.type.value if hasattr(new_pref.type, 'value') else str(new_pref.type),
                "enabled": new_pref.enabled,
                "created_at": getattr(new_pref, 'created_at', None).isoformat() if getattr(new_pref, 'created_at', None) else None
            }
        except HTTPException:
            raise
        except IntegrityError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error creating notification preference: {str(e)}"
            )
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating notification preference: {str(e)}"
            )
    
    # ==================== MIGRATION ====================
    
    async def migrate_existing_preferences_data(self) -> Dict:
        """Migrate existing preferences data from source tables."""
        try:
            from app.scripts.seed_data.migrate_phase6_data import migrate_phase6_data
            
            results = migrate_phase6_data(self.db)
            
            return {
                "success": True,
                "message": "Preferences migration completed",
                "results": results
            }
        except Exception as e:
            self.logger.error(f"Error migrating preferences data: {str(e)}")
            return {
                "success": False,
                "message": f"Error migrating preferences data: {str(e)}",
                "results": {}
            }

