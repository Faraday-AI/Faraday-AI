"""
Teacher Dashboard Service
Handles personal workspace, activity analytics, and dashboard management for beta teachers
"""

from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta, date
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc, text
import uuid
import json

from app.models.teacher_dashboard import (
    DashboardWidget,
    TeacherDashboardLayout,
    DashboardWidgetInstance,
    TeacherActivityLog,
    TeacherNotification,
    TeacherAchievement,
    TeacherAchievementProgress,
    TeacherQuickAction,
    TeacherPreference,
    TeacherStatistics,
    TeacherGoal,
    TeacherLearningPath,
    LearningPathStep
)
from app.schemas.teacher_dashboard import (
    DashboardWidgetResponse,
    TeacherDashboardLayoutCreate,
    TeacherDashboardLayoutUpdate,
    TeacherDashboardLayoutResponse,
    DashboardWidgetInstanceCreate,
    DashboardWidgetInstanceUpdate,
    DashboardWidgetInstanceResponse,
    TeacherActivityLogCreate,
    TeacherActivityLogResponse,
    TeacherNotificationResponse,
    TeacherAchievementResponse,
    TeacherAchievementProgressResponse,
    TeacherQuickActionCreate,
    TeacherQuickActionUpdate,
    TeacherQuickActionResponse,
    TeacherPreferenceCreate,
    TeacherPreferenceUpdate,
    TeacherPreferenceResponse,
    TeacherStatisticsResponse,
    TeacherGoalCreate,
    TeacherGoalUpdate,
    TeacherGoalResponse,
    TeacherLearningPathCreate,
    TeacherLearningPathUpdate,
    TeacherLearningPathResponse,
    LearningPathStepCreate,
    LearningPathStepResponse,
    DashboardAnalyticsResponse,
    TeacherDashboardSummaryResponse
)


class TeacherDashboardService:
    def __init__(self, db: Session):
        self.db = db

    # ==================== DASHBOARD LAYOUTS ====================
    
    def create_dashboard_layout(
        self, 
        teacher_id: str, 
        layout_data: TeacherDashboardLayoutCreate
    ) -> TeacherDashboardLayoutResponse:
        """Create a new dashboard layout"""
        try:
            # If this is set as default, unset other defaults
            if layout_data.is_default:
                self.db.query(TeacherDashboardLayout).filter(
                    and_(
                        TeacherDashboardLayout.teacher_id == teacher_id,
                        TeacherDashboardLayout.is_default == True
                    )
                ).update({"is_default": False})
            
            layout = TeacherDashboardLayout(
                id=str(uuid.uuid4()),
                teacher_id=teacher_id,
                layout_name=layout_data.layout_name,
                layout_description=layout_data.layout_description,
                is_default=layout_data.is_default
            )
            
            self.db.add(layout)
            self.db.flush()  # Get the ID
            
            # Add widget instances if provided
            if layout_data.widget_instances:
                for widget_instance_data in layout_data.widget_instances:
                    widget_instance = DashboardWidgetInstance(
                        id=str(uuid.uuid4()),
                        layout_id=layout.id,
                        widget_id=widget_instance_data.widget_id,
                        position_x=widget_instance_data.position_x,
                        position_y=widget_instance_data.position_y,
                        width=widget_instance_data.width,
                        height=widget_instance_data.height,
                        widget_config=widget_instance_data.widget_config
                    )
                    self.db.add(widget_instance)
            
            self.db.commit()
            
            return self._layout_to_response(layout)
            
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Failed to create dashboard layout: {str(e)}")

    def get_teacher_dashboard_layouts(
        self, 
        teacher_id: str, 
        include_inactive: bool = False
    ) -> List[TeacherDashboardLayoutResponse]:
        """Get all dashboard layouts for a teacher"""
        query = self.db.query(TeacherDashboardLayout).filter(
            TeacherDashboardLayout.teacher_id == teacher_id
        )
        
        if not include_inactive:
            query = query.filter(TeacherDashboardLayout.is_active == True)
        
        layouts = query.order_by(desc(TeacherDashboardLayout.is_default), asc(TeacherDashboardLayout.layout_name)).all()
        
        return [self._layout_to_response(layout) for layout in layouts]

    def get_default_dashboard_layout(
        self, 
        teacher_id: str
    ) -> Optional[TeacherDashboardLayoutResponse]:
        """Get the default dashboard layout for a teacher"""
        layout = self.db.query(TeacherDashboardLayout).filter(
            and_(
                TeacherDashboardLayout.teacher_id == teacher_id,
                TeacherDashboardLayout.is_default == True,
                TeacherDashboardLayout.is_active == True
            )
        ).first()
        
        if not layout:
            # Create default layout if none exists
            layout = self._create_default_layout(teacher_id)
        
        return self._layout_to_response(layout) if layout else None

    def update_dashboard_layout(
        self, 
        layout_id: str, 
        teacher_id: str, 
        update_data: TeacherDashboardLayoutUpdate
    ) -> Optional[TeacherDashboardLayoutResponse]:
        """Update a dashboard layout"""
        layout = self.db.query(TeacherDashboardLayout).filter(
            and_(
                TeacherDashboardLayout.id == layout_id,
                TeacherDashboardLayout.teacher_id == teacher_id
            )
        ).first()
        
        if not layout:
            return None
        
        # If setting as default, unset other defaults
        if update_data.is_default:
            self.db.query(TeacherDashboardLayout).filter(
                and_(
                    TeacherDashboardLayout.teacher_id == teacher_id,
                    TeacherDashboardLayout.id != layout_id,
                    TeacherDashboardLayout.is_default == True
                )
            ).update({"is_default": False})
        
        # Update layout fields
        for field, value in update_data.dict(exclude_unset=True).items():
            if field != "widget_instances":
                setattr(layout, field, value)
        
        # Update widget instances if provided
        if update_data.widget_instances is not None:
            # Delete existing widget instances
            self.db.query(DashboardWidgetInstance).filter(
                DashboardWidgetInstance.layout_id == layout_id
            ).delete()
            
            # Add new widget instances
            for widget_instance_data in update_data.widget_instances:
                widget_instance = DashboardWidgetInstance(
                    id=str(uuid.uuid4()),
                    layout_id=layout.id,
                    widget_id=widget_instance_data.widget_id,
                    position_x=widget_instance_data.position_x,
                    position_y=widget_instance_data.position_y,
                    width=widget_instance_data.width,
                    height=widget_instance_data.height,
                    widget_config=widget_instance_data.widget_config
                )
                self.db.add(widget_instance)
        
        layout.updated_at = datetime.utcnow()
        self.db.commit()
        
        return self._layout_to_response(layout)

    def delete_dashboard_layout(self, layout_id: str, teacher_id: str) -> bool:
        """Delete a dashboard layout"""
        layout = self.db.query(TeacherDashboardLayout).filter(
            and_(
                TeacherDashboardLayout.id == layout_id,
                TeacherDashboardLayout.teacher_id == teacher_id
            )
        ).first()
        
        if not layout:
            return False
        
        # Don't allow deletion of default layout
        if layout.is_default:
            return False
        
        self.db.delete(layout)
        self.db.commit()
        
        return True

    # ==================== WIDGET MANAGEMENT ====================
    
    def get_available_widgets(self) -> List[DashboardWidgetResponse]:
        """Get all available dashboard widgets"""
        widgets = self.db.query(DashboardWidget).filter(
            DashboardWidget.is_active == True
        ).order_by(asc(DashboardWidget.display_order)).all()
        
        return [self._widget_to_response(widget) for widget in widgets]

    def add_widget_to_layout(
        self, 
        layout_id: str, 
        teacher_id: str, 
        widget_instance_data: DashboardWidgetInstanceCreate
    ) -> Optional[DashboardWidgetInstanceResponse]:
        """Add a widget to a dashboard layout"""
        # Verify layout ownership
        layout = self.db.query(TeacherDashboardLayout).filter(
            and_(
                TeacherDashboardLayout.id == layout_id,
                TeacherDashboardLayout.teacher_id == teacher_id
            )
        ).first()
        
        if not layout:
            return None
        
        widget_instance = DashboardWidgetInstance(
            id=str(uuid.uuid4()),
            layout_id=layout_id,
            widget_id=widget_instance_data.widget_id,
            position_x=widget_instance_data.position_x,
            position_y=widget_instance_data.position_y,
            width=widget_instance_data.width,
            height=widget_instance_data.height,
            widget_config=widget_instance_data.widget_config
        )
        
        self.db.add(widget_instance)
        self.db.commit()
        
        return self._widget_instance_to_response(widget_instance)

    def update_widget_instance(
        self, 
        instance_id: str, 
        teacher_id: str, 
        update_data: DashboardWidgetInstanceUpdate
    ) -> Optional[DashboardWidgetInstanceResponse]:
        """Update a widget instance"""
        widget_instance = self.db.query(DashboardWidgetInstance).join(TeacherDashboardLayout).filter(
            and_(
                DashboardWidgetInstance.id == instance_id,
                TeacherDashboardLayout.teacher_id == teacher_id
            )
        ).first()
        
        if not widget_instance:
            return None
        
        # Update widget instance fields
        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(widget_instance, field, value)
        
        widget_instance.updated_at = datetime.utcnow()
        self.db.commit()
        
        return self._widget_instance_to_response(widget_instance)

    def remove_widget_from_layout(
        self, 
        instance_id: str, 
        teacher_id: str
    ) -> bool:
        """Remove a widget from a dashboard layout"""
        widget_instance = self.db.query(DashboardWidgetInstance).join(TeacherDashboardLayout).filter(
            and_(
                DashboardWidgetInstance.id == instance_id,
                TeacherDashboardLayout.teacher_id == teacher_id
            )
        ).first()
        
        if not widget_instance:
            return False
        
        self.db.delete(widget_instance)
        self.db.commit()
        
        return True

    # ==================== ACTIVITY LOGGING ====================
    
    def log_teacher_activity(
        self, 
        teacher_id: str, 
        activity_data: TeacherActivityLogCreate
    ) -> TeacherActivityLogResponse:
        """Log teacher activity"""
        activity_log = TeacherActivityLog(
            id=str(uuid.uuid4()),
            teacher_id=teacher_id,
            activity_type=activity_data.activity_type,
            activity_description=activity_data.activity_description,
            resource_type=activity_data.resource_type,
            resource_id=activity_data.resource_id,
            resource_title=activity_data.resource_title,
            metadata=activity_data.metadata,
            ip_address=activity_data.ip_address,
            user_agent=activity_data.user_agent,
            session_id=activity_data.session_id
        )
        
        self.db.add(activity_log)
        self.db.commit()
        
        # Update achievement progress based on activity
        self._update_achievement_progress(teacher_id, activity_data.activity_type)
        
        return self._activity_log_to_response(activity_log)

    def get_teacher_activity_logs(
        self, 
        teacher_id: str, 
        activity_type: Optional[str] = None,
        days: int = 30,
        limit: int = 100,
        offset: int = 0
    ) -> List[TeacherActivityLogResponse]:
        """Get teacher activity logs"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        query = self.db.query(TeacherActivityLog).filter(
            and_(
                TeacherActivityLog.teacher_id == teacher_id,
                TeacherActivityLog.created_at >= start_date
            )
        )
        
        if activity_type:
            query = query.filter(TeacherActivityLog.activity_type == activity_type)
        
        logs = query.order_by(desc(TeacherActivityLog.created_at)).offset(offset).limit(limit).all()
        
        return [self._activity_log_to_response(log) for log in logs]

    # ==================== NOTIFICATIONS ====================
    
    def get_teacher_notifications(
        self, 
        teacher_id: str, 
        unread_only: bool = False,
        limit: int = 50,
        offset: int = 0
    ) -> List[TeacherNotificationResponse]:
        """Get teacher notifications"""
        query = self.db.query(TeacherNotification).filter(
            TeacherNotification.teacher_id == teacher_id
        )
        
        if unread_only:
            query = query.filter(TeacherNotification.is_read == False)
        
        # Filter out expired notifications
        query = query.filter(
            or_(
                TeacherNotification.expires_at.is_(None),
                TeacherNotification.expires_at > datetime.utcnow()
            )
        )
        
        notifications = query.order_by(desc(TeacherNotification.is_important), desc(TeacherNotification.created_at)).offset(offset).limit(limit).all()
        
        return [self._notification_to_response(notification) for notification in notifications]

    def mark_notification_as_read(
        self, 
        notification_id: str, 
        teacher_id: str
    ) -> bool:
        """Mark a notification as read"""
        notification = self.db.query(TeacherNotification).filter(
            and_(
                TeacherNotification.id == notification_id,
                TeacherNotification.teacher_id == teacher_id
            )
        ).first()
        
        if not notification:
            return False
        
        notification.is_read = True
        notification.read_at = datetime.utcnow()
        self.db.commit()
        
        return True

    def mark_all_notifications_as_read(self, teacher_id: str) -> int:
        """Mark all notifications as read for a teacher"""
        result = self.db.query(TeacherNotification).filter(
            and_(
                TeacherNotification.teacher_id == teacher_id,
                TeacherNotification.is_read == False
            )
        ).update({
            "is_read": True,
            "read_at": datetime.utcnow()
        })
        
        self.db.commit()
        return result

    def create_notification(
        self, 
        teacher_id: str, 
        notification_type: str,
        title: str,
        message: str,
        action_url: Optional[str] = None,
        action_label: Optional[str] = None,
        is_important: bool = False,
        expires_at: Optional[datetime] = None
    ) -> TeacherNotificationResponse:
        """Create a notification for a teacher"""
        notification = TeacherNotification(
            id=str(uuid.uuid4()),
            teacher_id=teacher_id,
            notification_type=notification_type,
            title=title,
            message=message,
            action_url=action_url,
            action_label=action_label,
            is_important=is_important,
            expires_at=expires_at
        )
        
        self.db.add(notification)
        self.db.commit()
        
        return self._notification_to_response(notification)

    # ==================== ACHIEVEMENTS ====================
    
    def get_teacher_achievements(
        self, 
        teacher_id: str, 
        completed_only: bool = False
    ) -> List[TeacherAchievementProgressResponse]:
        """Get teacher achievement progress"""
        query = self.db.query(TeacherAchievementProgress).join(TeacherAchievement).filter(
            TeacherAchievementProgress.teacher_id == teacher_id
        )
        
        if completed_only:
            query = query.filter(TeacherAchievementProgress.is_completed == True)
        
        achievements = query.order_by(desc(TeacherAchievementProgress.completed_at), asc(TeacherAchievement.achievement_name)).all()
        
        return [self._achievement_progress_to_response(achievement) for achievement in achievements]

    def get_available_achievements(self) -> List[TeacherAchievementResponse]:
        """Get all available achievements"""
        achievements = self.db.query(TeacherAchievement).filter(
            TeacherAchievement.is_active == True
        ).order_by(asc(TeacherAchievement.achievement_name)).all()
        
        return [self._achievement_to_response(achievement) for achievement in achievements]

    # ==================== QUICK ACTIONS ====================
    
    def get_teacher_quick_actions(
        self, 
        teacher_id: str
    ) -> List[TeacherQuickActionResponse]:
        """Get teacher's quick actions"""
        actions = self.db.query(TeacherQuickAction).filter(
            and_(
                TeacherQuickAction.teacher_id == teacher_id,
                TeacherQuickAction.is_active == True
            )
        ).order_by(asc(TeacherQuickAction.display_order)).all()
        
        return [self._quick_action_to_response(action) for action in actions]

    def create_quick_action(
        self, 
        teacher_id: str, 
        action_data: TeacherQuickActionCreate
    ) -> TeacherQuickActionResponse:
        """Create a quick action for a teacher"""
        action = TeacherQuickAction(
            id=str(uuid.uuid4()),
            teacher_id=teacher_id,
            action_name=action_data.action_name,
            action_description=action_data.action_description,
            action_type=action_data.action_type,
            action_url=action_data.action_url,
            icon_name=action_data.icon_name,
            color_code=action_data.color_code,
            display_order=action_data.display_order
        )
        
        self.db.add(action)
        self.db.commit()
        
        return self._quick_action_to_response(action)

    def update_quick_action(
        self, 
        action_id: str, 
        teacher_id: str, 
        update_data: TeacherQuickActionUpdate
    ) -> Optional[TeacherQuickActionResponse]:
        """Update a quick action"""
        action = self.db.query(TeacherQuickAction).filter(
            and_(
                TeacherQuickAction.id == action_id,
                TeacherQuickAction.teacher_id == teacher_id
            )
        ).first()
        
        if not action:
            return None
        
        # Update action fields
        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(action, field, value)
        
        action.updated_at = datetime.utcnow()
        self.db.commit()
        
        return self._quick_action_to_response(action)

    def delete_quick_action(self, action_id: str, teacher_id: str) -> bool:
        """Delete a quick action"""
        action = self.db.query(TeacherQuickAction).filter(
            and_(
                TeacherQuickAction.id == action_id,
                TeacherQuickAction.teacher_id == teacher_id
            )
        ).first()
        
        if not action:
            return False
        
        self.db.delete(action)
        self.db.commit()
        
        return True

    # ==================== PREFERENCES ====================
    
    def get_teacher_preferences(
        self, 
        teacher_id: str
    ) -> List[TeacherPreferenceResponse]:
        """Get teacher preferences"""
        preferences = self.db.query(TeacherPreference).filter(
            TeacherPreference.teacher_id == teacher_id
        ).order_by(asc(TeacherPreference.preference_key)).all()
        
        return [self._preference_to_response(preference) for preference in preferences]

    def set_teacher_preference(
        self, 
        teacher_id: str, 
        preference_data: TeacherPreferenceCreate
    ) -> TeacherPreferenceResponse:
        """Set a teacher preference"""
        # Check if preference already exists
        existing = self.db.query(TeacherPreference).filter(
            and_(
                TeacherPreference.teacher_id == teacher_id,
                TeacherPreference.preference_key == preference_data.preference_key
            )
        ).first()
        
        if existing:
            # Update existing preference
            existing.preference_value = preference_data.preference_value
            existing.preference_type = preference_data.preference_type
            existing.updated_at = datetime.utcnow()
            self.db.commit()
            return self._preference_to_response(existing)
        
        # Create new preference
        preference = TeacherPreference(
            id=str(uuid.uuid4()),
            teacher_id=teacher_id,
            preference_key=preference_data.preference_key,
            preference_value=preference_data.preference_value,
            preference_type=preference_data.preference_type
        )
        
        self.db.add(preference)
        self.db.commit()
        
        return self._preference_to_response(preference)

    # ==================== STATISTICS ====================
    
    def get_teacher_statistics(
        self, 
        teacher_id: str, 
        stat_type: str = "daily",
        days: int = 30
    ) -> List[TeacherStatisticsResponse]:
        """Get teacher statistics"""
        start_date = date.today() - timedelta(days=days)
        
        stats = self.db.query(TeacherStatistics).filter(
            and_(
                TeacherStatistics.teacher_id == teacher_id,
                TeacherStatistics.stat_type == stat_type,
                TeacherStatistics.stat_date >= start_date
            )
        ).order_by(desc(TeacherStatistics.stat_date)).all()
        
        return [self._statistics_to_response(stat) for stat in stats]

    def update_teacher_statistics(
        self, 
        teacher_id: str, 
        stat_date: date,
        stat_type: str,
        **kwargs
    ) -> TeacherStatisticsResponse:
        """Update teacher statistics"""
        # Check if statistics already exist for this date
        existing = self.db.query(TeacherStatistics).filter(
            and_(
                TeacherStatistics.teacher_id == teacher_id,
                TeacherStatistics.stat_date == stat_date,
                TeacherStatistics.stat_type == stat_type
            )
        ).first()
        
        if existing:
            # Update existing statistics
            for key, value in kwargs.items():
                if hasattr(existing, key):
                    setattr(existing, key, value)
            self.db.commit()
            return self._statistics_to_response(existing)
        
        # Create new statistics
        stats = TeacherStatistics(
            id=str(uuid.uuid4()),
            teacher_id=teacher_id,
            stat_date=stat_date,
            stat_type=stat_type,
            **kwargs
        )
        
        self.db.add(stats)
        self.db.commit()
        
        return self._statistics_to_response(stats)

    # ==================== GOALS ====================
    
    def get_teacher_goals(
        self, 
        teacher_id: str, 
        active_only: bool = True
    ) -> List[TeacherGoalResponse]:
        """Get teacher goals"""
        query = self.db.query(TeacherGoal).filter(
            TeacherGoal.teacher_id == teacher_id
        )
        
        if active_only:
            query = query.filter(TeacherGoal.is_active == True)
        
        goals = query.order_by(desc(TeacherGoal.priority_level), asc(TeacherGoal.target_date)).all()
        
        return [self._goal_to_response(goal) for goal in goals]

    def create_goal(
        self, 
        teacher_id: str, 
        goal_data: TeacherGoalCreate
    ) -> TeacherGoalResponse:
        """Create a teacher goal"""
        goal = TeacherGoal(
            id=str(uuid.uuid4()),
            teacher_id=teacher_id,
            goal_title=goal_data.goal_title,
            goal_description=goal_data.goal_description,
            goal_type=goal_data.goal_type,
            goal_category=goal_data.goal_category,
            target_value=goal_data.target_value,
            target_date=goal_data.target_date,
            priority_level=goal_data.priority_level
        )
        
        self.db.add(goal)
        self.db.commit()
        
        return self._goal_to_response(goal)

    def update_goal_progress(
        self, 
        goal_id: str, 
        teacher_id: str, 
        progress_value: int
    ) -> Optional[TeacherGoalResponse]:
        """Update goal progress"""
        goal = self.db.query(TeacherGoal).filter(
            and_(
                TeacherGoal.id == goal_id,
                TeacherGoal.teacher_id == teacher_id
            )
        ).first()
        
        if not goal:
            return None
        
        goal.current_value = progress_value
        
        # Check if goal is completed
        if progress_value >= goal.target_value and not goal.is_completed:
            goal.is_completed = True
            goal.completed_at = datetime.utcnow()
        
        goal.updated_at = datetime.utcnow()
        self.db.commit()
        
        return self._goal_to_response(goal)

    # ==================== LEARNING PATHS ====================
    
    def get_teacher_learning_paths(
        self, 
        teacher_id: str, 
        active_only: bool = True
    ) -> List[TeacherLearningPathResponse]:
        """Get teacher learning paths"""
        query = self.db.query(TeacherLearningPath).filter(
            TeacherLearningPath.teacher_id == teacher_id
        )
        
        if active_only:
            query = query.filter(TeacherLearningPath.is_active == True)
        
        paths = query.order_by(desc(TeacherLearningPath.is_completed), asc(TeacherLearningPath.path_name)).all()
        
        return [self._learning_path_to_response(path) for path in paths]

    def create_learning_path(
        self, 
        teacher_id: str, 
        path_data: TeacherLearningPathCreate
    ) -> TeacherLearningPathResponse:
        """Create a learning path for a teacher"""
        path = TeacherLearningPath(
            id=str(uuid.uuid4()),
            teacher_id=teacher_id,
            path_name=path_data.path_name,
            path_description=path_data.path_description,
            path_category=path_data.path_category,
            difficulty_level=path_data.difficulty_level,
            estimated_hours=path_data.estimated_hours
        )
        
        self.db.add(path)
        self.db.flush()  # Get the ID
        
        # Add learning path steps if provided
        if path_data.steps:
            for i, step_data in enumerate(path_data.steps):
                step = LearningPathStep(
                    id=str(uuid.uuid4()),
                    learning_path_id=path.id,
                    step_title=step_data.step_title,
                    step_description=step_data.step_description,
                    step_type=step_data.step_type,
                    step_url=step_data.step_url,
                    step_content=step_data.step_content,
                    estimated_minutes=step_data.estimated_minutes,
                    step_order=i + 1
                )
                self.db.add(step)
        
        self.db.commit()
        
        return self._learning_path_to_response(path)

    # ==================== DASHBOARD ANALYTICS ====================
    
    def get_dashboard_analytics(
        self, 
        teacher_id: str, 
        days: int = 30
    ) -> DashboardAnalyticsResponse:
        """Get comprehensive dashboard analytics"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Activity summary
        activity_summary = self.db.query(
            TeacherActivityLog.activity_type,
            func.count(TeacherActivityLog.id).label('count')
        ).filter(
            and_(
                TeacherActivityLog.teacher_id == teacher_id,
                TeacherActivityLog.created_at >= start_date
            )
        ).group_by(TeacherActivityLog.activity_type).all()
        
        # Recent achievements
        recent_achievements = self.db.query(TeacherAchievementProgress).join(TeacherAchievement).filter(
            and_(
                TeacherAchievementProgress.teacher_id == teacher_id,
                TeacherAchievementProgress.is_completed == True,
                TeacherAchievementProgress.completed_at >= start_date
            )
        ).order_by(desc(TeacherAchievementProgress.completed_at)).limit(5).all()
        
        # Goal progress
        active_goals = self.db.query(TeacherGoal).filter(
            and_(
                TeacherGoal.teacher_id == teacher_id,
                TeacherGoal.is_active == True,
                TeacherGoal.is_completed == False
            )
        ).all()
        
        # Notification count
        unread_notifications = self.db.query(func.count(TeacherNotification.id)).filter(
            and_(
                TeacherNotification.teacher_id == teacher_id,
                TeacherNotification.is_read == False
            )
        ).scalar()
        
        return DashboardAnalyticsResponse(
            activity_summary={item.activity_type: item.count for item in activity_summary},
            recent_achievements=[self._achievement_progress_to_response(achievement) for achievement in recent_achievements],
            active_goals=[self._goal_to_response(goal) for goal in active_goals],
            unread_notifications=unread_notifications,
            total_achievements=self.db.query(func.count(TeacherAchievementProgress.id)).filter(
                and_(
                    TeacherAchievementProgress.teacher_id == teacher_id,
                    TeacherAchievementProgress.is_completed == True
                )
            ).scalar(),
            completion_rate=self._calculate_completion_rate(teacher_id)
        )

    def get_dashboard_summary(
        self, 
        teacher_id: str
    ) -> TeacherDashboardSummaryResponse:
        """Get dashboard summary for quick overview"""
        # Get recent activity count
        recent_activity_count = self.db.query(func.count(TeacherActivityLog.id)).filter(
            and_(
                TeacherActivityLog.teacher_id == teacher_id,
                TeacherActivityLog.created_at >= datetime.utcnow() - timedelta(days=7)
            )
        ).scalar()
        
        # Get unread notifications count
        unread_notifications = self.db.query(func.count(TeacherNotification.id)).filter(
            and_(
                TeacherNotification.teacher_id == teacher_id,
                TeacherNotification.is_read == False
            )
        ).scalar()
        
        # Get active goals count
        active_goals = self.db.query(func.count(TeacherGoal.id)).filter(
            and_(
                TeacherGoal.teacher_id == teacher_id,
                TeacherGoal.is_active == True,
                TeacherGoal.is_completed == False
            )
        ).scalar()
        
        # Get learning paths in progress
        learning_paths_in_progress = self.db.query(func.count(TeacherLearningPath.id)).filter(
            and_(
                TeacherLearningPath.teacher_id == teacher_id,
                TeacherLearningPath.is_active == True,
                TeacherLearningPath.is_completed == False
            )
        ).scalar()
        
        return TeacherDashboardSummaryResponse(
            recent_activity_count=recent_activity_count,
            unread_notifications=unread_notifications,
            active_goals=active_goals,
            learning_paths_in_progress=learning_paths_in_progress,
            last_login=self._get_last_login(teacher_id),
            dashboard_last_updated=datetime.utcnow()
        )

    # ==================== HELPER METHODS ====================
    
    def _create_default_layout(self, teacher_id: str) -> Optional[TeacherDashboardLayout]:
        """Create default dashboard layout for a teacher"""
        try:
            # Get default widgets
            default_widgets = self.db.query(DashboardWidget).filter(
                DashboardWidget.is_system_widget == True
            ).order_by(asc(DashboardWidget.display_order)).all()
            
            # Create default layout
            layout = TeacherDashboardLayout(
                id=str(uuid.uuid4()),
                teacher_id=teacher_id,
                layout_name="Default Layout",
                layout_description="Default dashboard layout",
                is_default=True
            )
            
            self.db.add(layout)
            self.db.flush()
            
            # Add default widgets
            for i, widget in enumerate(default_widgets):
                widget_instance = DashboardWidgetInstance(
                    id=str(uuid.uuid4()),
                    layout_id=layout.id,
                    widget_id=widget.id,
                    position_x=(i % 3) * 4,
                    position_y=(i // 3) * 3,
                    width=4,
                    height=3,
                    widget_config=widget.widget_config
                )
                self.db.add(widget_instance)
            
            self.db.commit()
            return layout
            
        except Exception as e:
            self.db.rollback()
            return None

    def _update_achievement_progress(self, teacher_id: str, activity_type: str) -> None:
        """Update achievement progress based on activity"""
        # This would contain logic to update specific achievements
        # based on the activity type (e.g., lessons created, resources uploaded)
        pass

    def _calculate_completion_rate(self, teacher_id: str) -> float:
        """Calculate overall completion rate for teacher goals and learning paths"""
        total_items = self.db.query(func.count(TeacherGoal.id)).filter(
            TeacherGoal.teacher_id == teacher_id
        ).scalar() + self.db.query(func.count(TeacherLearningPath.id)).filter(
            TeacherLearningPath.teacher_id == teacher_id
        ).scalar()
        
        if total_items == 0:
            return 0.0
        
        completed_items = self.db.query(func.count(TeacherGoal.id)).filter(
            and_(
                TeacherGoal.teacher_id == teacher_id,
                TeacherGoal.is_completed == True
            )
        ).scalar() + self.db.query(func.count(TeacherLearningPath.id)).filter(
            and_(
                TeacherLearningPath.teacher_id == teacher_id,
                TeacherLearningPath.is_completed == True
            )
        ).scalar()
        
        return (completed_items / total_items) * 100.0

    def _get_last_login(self, teacher_id: str) -> Optional[datetime]:
        """Get teacher's last login time"""
        last_login = self.db.query(TeacherActivityLog.created_at).filter(
            and_(
                TeacherActivityLog.teacher_id == teacher_id,
                TeacherActivityLog.activity_type == "login"
            )
        ).order_by(desc(TeacherActivityLog.created_at)).first()
        
        return last_login[0] if last_login else None

    # ==================== RESPONSE CONVERTERS ====================
    
    def _layout_to_response(self, layout: TeacherDashboardLayout) -> TeacherDashboardLayoutResponse:
        """Convert layout model to response"""
        # Get widget instances
        widget_instances = self.db.query(DashboardWidgetInstance).filter(
            DashboardWidgetInstance.layout_id == layout.id
        ).order_by(asc(DashboardWidgetInstance.position_y), asc(DashboardWidgetInstance.position_x)).all()
        
        return TeacherDashboardLayoutResponse(
            id=layout.id,
            teacher_id=layout.teacher_id,
            layout_name=layout.layout_name,
            layout_description=layout.layout_description,
            is_default=layout.is_default,
            is_active=layout.is_active,
            created_at=layout.created_at,
            updated_at=layout.updated_at,
            widget_instances=[self._widget_instance_to_response(instance) for instance in widget_instances]
        )

    def _widget_to_response(self, widget: DashboardWidget) -> DashboardWidgetResponse:
        """Convert widget model to response"""
        return DashboardWidgetResponse(
            id=widget.id,
            widget_type=widget.widget_type,
            widget_name=widget.widget_name,
            widget_description=widget.widget_description,
            widget_config=widget.widget_config,
            is_system_widget=widget.is_system_widget,
            is_active=widget.is_active,
            display_order=widget.display_order,
            created_at=widget.created_at
        )

    def _widget_instance_to_response(self, instance: DashboardWidgetInstance) -> DashboardWidgetInstanceResponse:
        """Convert widget instance model to response"""
        return DashboardWidgetInstanceResponse(
            id=instance.id,
            layout_id=instance.layout_id,
            widget_id=instance.widget_id,
            position_x=instance.position_x,
            position_y=instance.position_y,
            width=instance.width,
            height=instance.height,
            widget_config=instance.widget_config,
            is_visible=instance.is_visible,
            created_at=instance.created_at,
            updated_at=instance.updated_at
        )

    def _activity_log_to_response(self, log: TeacherActivityLog) -> TeacherActivityLogResponse:
        """Convert activity log model to response"""
        return TeacherActivityLogResponse(
            id=log.id,
            teacher_id=log.teacher_id,
            activity_type=log.activity_type,
            activity_description=log.activity_description,
            resource_type=log.resource_type,
            resource_id=log.resource_id,
            resource_title=log.resource_title,
            metadata=log.metadata,
            ip_address=str(log.ip_address) if log.ip_address else None,
            user_agent=log.user_agent,
            session_id=log.session_id,
            created_at=log.created_at
        )

    def _notification_to_response(self, notification: TeacherNotification) -> TeacherNotificationResponse:
        """Convert notification model to response"""
        return TeacherNotificationResponse(
            id=notification.id,
            teacher_id=notification.teacher_id,
            notification_type=notification.notification_type,
            title=notification.title,
            message=notification.message,
            action_url=notification.action_url,
            action_label=notification.action_label,
            is_read=notification.is_read,
            is_important=notification.is_important,
            expires_at=notification.expires_at,
            created_at=notification.created_at,
            read_at=notification.read_at
        )

    def _achievement_to_response(self, achievement: TeacherAchievement) -> TeacherAchievementResponse:
        """Convert achievement model to response"""
        return TeacherAchievementResponse(
            id=achievement.id,
            achievement_code=achievement.achievement_code,
            achievement_name=achievement.achievement_name,
            achievement_description=achievement.achievement_description,
            achievement_category=achievement.achievement_category,
            icon_name=achievement.icon_name,
            color_code=achievement.color_code,
            points=achievement.points,
            is_active=achievement.is_active,
            created_at=achievement.created_at
        )

    def _achievement_progress_to_response(self, progress: TeacherAchievementProgress) -> TeacherAchievementProgressResponse:
        """Convert achievement progress model to response"""
        achievement = self.db.query(TeacherAchievement).filter(
            TeacherAchievement.id == progress.achievement_id
        ).first()
        
        return TeacherAchievementProgressResponse(
            id=progress.id,
            teacher_id=progress.teacher_id,
            achievement_id=progress.achievement_id,
            achievement=self._achievement_to_response(achievement) if achievement else None,
            progress_value=progress.progress_value,
            target_value=progress.target_value,
            is_completed=progress.is_completed,
            completed_at=progress.completed_at,
            created_at=progress.created_at,
            updated_at=progress.updated_at
        )

    def _quick_action_to_response(self, action: TeacherQuickAction) -> TeacherQuickActionResponse:
        """Convert quick action model to response"""
        return TeacherQuickActionResponse(
            id=action.id,
            teacher_id=action.teacher_id,
            action_name=action.action_name,
            action_description=action.action_description,
            action_type=action.action_type,
            action_url=action.action_url,
            icon_name=action.icon_name,
            color_code=action.color_code,
            display_order=action.display_order,
            is_active=action.is_active,
            created_at=action.created_at,
            updated_at=action.updated_at
        )

    def _preference_to_response(self, preference: TeacherPreference) -> TeacherPreferenceResponse:
        """Convert preference model to response"""
        return TeacherPreferenceResponse(
            id=preference.id,
            teacher_id=preference.teacher_id,
            preference_key=preference.preference_key,
            preference_value=preference.preference_value,
            preference_type=preference.preference_type,
            created_at=preference.created_at,
            updated_at=preference.updated_at
        )

    def _statistics_to_response(self, stats: TeacherStatistics) -> TeacherStatisticsResponse:
        """Convert statistics model to response"""
        return TeacherStatisticsResponse(
            id=stats.id,
            teacher_id=stats.teacher_id,
            stat_date=stats.stat_date,
            stat_type=stats.stat_type,
            lessons_created=stats.lessons_created,
            assessments_created=stats.assessments_created,
            resources_uploaded=stats.resources_uploaded,
            resources_downloaded=stats.resources_downloaded,
            resources_shared=stats.resources_shared,
            resources_received=stats.resources_received,
            collections_created=stats.collections_created,
            reviews_written=stats.reviews_written,
            time_spent_minutes=stats.time_spent_minutes,
            login_count=stats.login_count,
            created_at=stats.created_at
        )

    def _goal_to_response(self, goal: TeacherGoal) -> TeacherGoalResponse:
        """Convert goal model to response"""
        return TeacherGoalResponse(
            id=goal.id,
            teacher_id=goal.teacher_id,
            goal_title=goal.goal_title,
            goal_description=goal.goal_description,
            goal_type=goal.goal_type,
            goal_category=goal.goal_category,
            target_value=goal.target_value,
            current_value=goal.current_value,
            target_date=goal.target_date,
            is_completed=goal.is_completed,
            completed_at=goal.completed_at,
            priority_level=goal.priority_level,
            is_active=goal.is_active,
            created_at=goal.created_at,
            updated_at=goal.updated_at
        )

    def _learning_path_to_response(self, path: TeacherLearningPath) -> TeacherLearningPathResponse:
        """Convert learning path model to response"""
        # Get learning path steps
        steps = self.db.query(LearningPathStep).filter(
            LearningPathStep.learning_path_id == path.id
        ).order_by(asc(LearningPathStep.step_order)).all()
        
        return TeacherLearningPathResponse(
            id=path.id,
            teacher_id=path.teacher_id,
            path_name=path.path_name,
            path_description=path.path_description,
            path_category=path.path_category,
            difficulty_level=path.difficulty_level,
            estimated_hours=path.estimated_hours,
            is_completed=path.is_completed,
            completion_percentage=path.completion_percentage,
            started_at=path.started_at,
            completed_at=path.completed_at,
            is_active=path.is_active,
            created_at=path.created_at,
            updated_at=path.updated_at,
            steps=[self._learning_path_step_to_response(step) for step in steps]
        )

    def _learning_path_step_to_response(self, step: LearningPathStep) -> LearningPathStepResponse:
        """Convert learning path step model to response"""
        return LearningPathStepResponse(
            id=step.id,
            learning_path_id=step.learning_path_id,
            step_title=step.step_title,
            step_description=step.step_description,
            step_type=step.step_type,
            step_url=step.step_url,
            step_content=step.step_content,
            estimated_minutes=step.estimated_minutes,
            is_completed=step.is_completed,
            completed_at=step.completed_at,
            step_order=step.step_order,
            created_at=step.created_at
        )
