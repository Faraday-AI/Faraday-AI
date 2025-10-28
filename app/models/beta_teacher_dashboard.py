"""
Beta Teacher Dashboard Models

This module defines the database models for the beta teacher dashboard system.
This is a separate system from the main teacher dashboard, designed to work independently
without school district or student data.
"""

from sqlalchemy import Column, String, JSON, Boolean, DateTime, ForeignKey, Integer, Float, Text, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.models.shared_base import SharedBase


class BetaDashboardWidget(SharedBase):
    """Model for dashboard widgets configuration - Beta system"""
    __tablename__ = "dashboard_widgets"
    __table_args__ = {'extend_existing': True}

    # Use existing columns from the table
    # Note: This table has many columns, we're only defining the ones we use
    id = Column(String, primary_key=True)
    name = Column(String)  # Map widget_name to name
    description = Column(Text)  # Map widget_description to description
    widget_type = Column(String)
    is_active = Column(Boolean)
    created_at = Column(DateTime)
    configuration = Column(JSON)  # Map widget_config to configuration
    
    # Don't query these columns - use getattr() in service to fall back
    # These are virtual columns for compatibility
    widget_name = None  # Will use 'name' field via getattr()
    widget_description = None  # Will use 'description' field via getattr()
    widget_config = None  # Will use 'configuration' field via getattr()
    is_system_widget = None  # Default to False
    display_order = None  # Default to 0
    updated_at = None


class TeacherDashboardLayout(SharedBase):
    """Model for teacher dashboard layouts"""
    __tablename__ = "teacher_dashboard_layouts"
    __table_args__ = {'extend_existing': True}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    teacher_id = Column(String, nullable=False, index=True)
    layout_name = Column(String(255), nullable=False)
    layout_description = Column(Text, nullable=True)
    is_default = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DashboardWidgetInstance(SharedBase):
    """Model for widget instances in a dashboard layout"""
    __tablename__ = "dashboard_widget_instances"
    __table_args__ = {'extend_existing': True}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    layout_id = Column(String, ForeignKey("teacher_dashboard_layouts.id"), nullable=False)
    widget_id = Column(String, nullable=False)
    position_x = Column(Integer, default=0)
    position_y = Column(Integer, default=0)
    width = Column(Integer, default=4)
    height = Column(Integer, default=4)
    widget_config = Column(JSON)
    is_visible = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TeacherActivityLog(SharedBase):
    """Model for teacher activity logging"""
    __tablename__ = "teacher_activity_logs"
    __table_args__ = {'extend_existing': True}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    teacher_id = Column(String, nullable=False, index=True)
    activity_type = Column(String(100), nullable=False)
    activity_description = Column(Text, nullable=True)
    resource_type = Column(String(100), nullable=True)
    resource_id = Column(String, nullable=True)
    resource_title = Column(String(255), nullable=True)
    activity_metadata = Column(JSON)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    session_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class TeacherNotification(SharedBase):
    """Model for teacher notifications"""
    __tablename__ = "teacher_notifications"
    __table_args__ = {'extend_existing': True}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    teacher_id = Column(String, nullable=False, index=True)
    notification_type = Column(String(100), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=True)
    action_url = Column(String(500), nullable=True)
    action_label = Column(String(100), nullable=True)
    is_read = Column(Boolean, default=False)
    is_important = Column(Boolean, default=False)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    read_at = Column(DateTime, nullable=True)


class TeacherAchievement(SharedBase):
    """Model for teacher achievements"""
    __tablename__ = "teacher_achievements"
    __table_args__ = {'extend_existing': True}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    achievement_code = Column(String(100), unique=True, nullable=False)
    achievement_name = Column(String(255), nullable=False)
    achievement_description = Column(Text, nullable=True)
    achievement_category = Column(String(100), nullable=True)
    icon_name = Column(String(100), nullable=True)
    color_code = Column(String(7), nullable=True)
    points = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class TeacherAchievementProgress(SharedBase):
    """Model for teacher achievement progress"""
    __tablename__ = "teacher_achievement_progress"
    __table_args__ = {'extend_existing': True}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    teacher_id = Column(String, nullable=False, index=True)
    achievement_id = Column(String, nullable=False, index=True)
    progress_value = Column(Float, default=0)
    target_value = Column(Float, default=100)
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TeacherQuickAction(SharedBase):
    """Model for teacher quick actions"""
    __tablename__ = "teacher_quick_actions"
    __table_args__ = {'extend_existing': True}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    teacher_id = Column(String, nullable=False, index=True)
    action_name = Column(String(255), nullable=False)
    action_description = Column(Text, nullable=True)
    action_type = Column(String(100), nullable=False)
    action_url = Column(String(500), nullable=True)
    icon_name = Column(String(100), nullable=True)
    color_code = Column(String(7), nullable=True)
    display_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class BetaTeacherPreference(SharedBase):
    """Model for teacher preferences - Beta system"""
    __tablename__ = "beta_teacher_preferences"
    __table_args__ = {'extend_existing': True}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    teacher_id = Column(String, nullable=False, index=True)
    preference_key = Column(String(100), nullable=False)
    preference_value = Column(Text, nullable=True)
    preference_type = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TeacherStatistics(SharedBase):
    """Model for teacher statistics"""
    __tablename__ = "teacher_statistics"
    __table_args__ = {'extend_existing': True}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    teacher_id = Column(String, nullable=False, index=True)
    stat_date = Column(Date, nullable=False)
    stat_type = Column(String(100), nullable=False)
    lessons_created = Column(Integer, default=0)
    assessments_created = Column(Integer, default=0)
    resources_uploaded = Column(Integer, default=0)
    resources_downloaded = Column(Integer, default=0)
    resources_shared = Column(Integer, default=0)
    resources_received = Column(Integer, default=0)
    collections_created = Column(Integer, default=0)
    reviews_written = Column(Integer, default=0)
    time_spent_minutes = Column(Integer, default=0)
    login_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class TeacherGoal(SharedBase):
    """Model for teacher goals"""
    __tablename__ = "teacher_goals"
    __table_args__ = {'extend_existing': True}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    teacher_id = Column(String, nullable=False, index=True)
    goal_title = Column(String(255), nullable=False)
    goal_description = Column(Text, nullable=True)
    goal_type = Column(String(100), nullable=False)
    goal_category = Column(String(100), nullable=True)
    target_value = Column(Float, nullable=True)
    current_value = Column(Float, default=0)
    target_date = Column(Date, nullable=True)
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)
    priority_level = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TeacherLearningPath(SharedBase):
    """Model for teacher learning paths"""
    __tablename__ = "teacher_learning_paths"
    __table_args__ = {'extend_existing': True}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    teacher_id = Column(String, nullable=False, index=True)
    path_name = Column(String(255), nullable=False)
    path_description = Column(Text, nullable=True)
    path_category = Column(String(100), nullable=True)
    difficulty_level = Column(String(50), nullable=True)
    estimated_hours = Column(Float, nullable=True)
    is_completed = Column(Boolean, default=False)
    completion_percentage = Column(Float, default=0)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class LearningPathStep(SharedBase):
    """Model for learning path steps"""
    __tablename__ = "learning_path_steps"
    __table_args__ = {'extend_existing': True}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    learning_path_id = Column(String, ForeignKey("teacher_learning_paths.id"), nullable=False)
    step_title = Column(String(255), nullable=False)
    step_description = Column(Text, nullable=True)
    step_type = Column(String(100), nullable=True)
    step_url = Column(String(500), nullable=True)
    step_content = Column(Text, nullable=True)
    estimated_minutes = Column(Integer, nullable=True)
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)
    step_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

