"""
Pydantic schemas for Beta Teacher Dashboard
Defines request/response models for beta teacher dashboard configuration and management
This is a separate system from the main teacher dashboard, designed to work independently
without school district or student data.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator


# ==================== DASHBOARD CONFIGURATION ====================

class DashboardConfigResponse(BaseModel):
    """Dashboard configuration response"""
    id: str
    teacher_id: str
    layout_name: Optional[str] = None
    layout_config: Optional[Dict[str, Any]] = None
    widgets: List['BetaDashboardWidgetResponse'] = Field(default_factory=list)
    is_default: bool = False
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== DASHBOARD WIDGETS ====================

class BetaDashboardWidgetResponse(BaseModel):
    """Dashboard widget response"""
    id: str
    name: str
    widget_type: str
    configuration: Optional[Dict[str, Any]] = None
    position_x: Optional[int] = None
    position_y: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BetaDashboardWidgetConfigUpdate(BaseModel):
    """Update dashboard widget configuration"""
    configuration: Optional[Dict[str, Any]] = None
    position_x: Optional[int] = None
    position_y: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    is_active: Optional[bool] = None


# ==================== DASHBOARD LAYOUT ====================

class DashboardLayoutUpdate(BaseModel):
    """Update dashboard layout"""
    layout_name: Optional[str] = None
    layout_config: Optional[Dict[str, Any]] = None
    is_default: Optional[bool] = None
    is_active: Optional[bool] = None


# ==================== DASHBOARD PREFERENCES ====================

class DashboardPreferencesUpdate(BaseModel):
    """Update dashboard preferences"""
    theme: Optional[str] = None
    default_view: Optional[str] = None
    notifications_enabled: Optional[bool] = None
    preferences: Optional[Dict[str, Any]] = None


# ==================== DASHBOARD ANALYTICS ====================

class DashboardAnalyticsResponse(BaseModel):
    """Dashboard analytics response"""
    total_widgets: int
    active_widgets: int
    widget_usage_stats: Dict[str, int]
    recent_activity: List[Dict[str, Any]]
    performance_metrics: Dict[str, Any]
    last_updated: datetime


# ==================== DASHBOARD FEEDBACK ====================

class DashboardFeedbackResponse(BaseModel):
    """Dashboard feedback response"""
    id: str
    teacher_id: str
    feedback_type: str
    feedback_text: str
    rating: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== ADDITIONAL SCHEMAS FOR SERVICE ====================

# Layout schemas
class TeacherDashboardLayoutCreate(BaseModel):
    """Create dashboard layout"""
    layout_name: str
    layout_description: Optional[str] = None
    is_default: bool = False
    widget_instances: Optional[List['BetaDashboardWidgetInstanceCreate']] = None

class TeacherDashboardLayoutUpdate(BaseModel):
    """Update dashboard layout"""
    layout_name: Optional[str] = None
    layout_description: Optional[str] = None
    is_default: Optional[bool] = None
    is_active: Optional[bool] = None
    widget_instances: Optional[List['BetaDashboardWidgetInstanceCreate']] = None

class TeacherDashboardLayoutResponse(BaseModel):
    """Dashboard layout response"""
    id: str
    teacher_id: str
    layout_name: str
    layout_description: Optional[str] = None
    is_default: bool = False
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    widget_instances: List['BetaDashboardWidgetInstanceResponse'] = Field(default_factory=list)

    class Config:
        from_attributes = True


# Widget instance schemas
class BetaDashboardWidgetInstanceCreate(BaseModel):
    """Create widget instance"""
    widget_id: str
    position_x: int = 0
    position_y: int = 0
    width: int = 4
    height: int = 4
    widget_config: Optional[Dict[str, Any]] = None

class BetaDashboardWidgetInstanceUpdate(BaseModel):
    """Update widget instance"""
    widget_id: Optional[str] = None
    position_x: Optional[int] = None
    position_y: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    widget_config: Optional[Dict[str, Any]] = None
    is_visible: Optional[bool] = None

class BetaDashboardWidgetInstanceResponse(BaseModel):
    """Widget instance response"""
    id: str
    layout_id: str
    widget_id: str
    position_x: int
    position_y: int
    width: int
    height: int
    widget_config: Optional[Dict[str, Any]] = None
    is_visible: bool = True
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Activity log schemas
class TeacherActivityLogCreate(BaseModel):
    """Create activity log"""
    activity_type: str
    activity_description: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    resource_title: Optional[str] = None
    activity_metadata: Optional[Dict[str, Any]] = None

class TeacherActivityLogResponse(BaseModel):
    """Activity log response"""
    id: str
    teacher_id: str
    activity_type: str
    activity_description: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    resource_title: Optional[str] = None
    activity_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Notification schemas
class TeacherNotificationResponse(BaseModel):
    """Notification response"""
    id: str
    teacher_id: str
    notification_type: str
    title: str
    message: Optional[str] = None
    is_read: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


# Achievement schemas
class TeacherAchievementResponse(BaseModel):
    """Achievement response"""
    id: str
    achievement_code: str
    achievement_name: str
    achievement_description: Optional[str] = None
    points: int = 0
    is_active: bool = True
    created_at: datetime

    class Config:
        from_attributes = True

class TeacherAchievementProgressResponse(BaseModel):
    """Achievement progress response"""
    id: str
    teacher_id: str
    achievement_id: str
    progress_value: float = 0
    target_value: float = 100
    is_completed: bool = False
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Quick action schemas
class TeacherQuickActionCreate(BaseModel):
    """Create quick action"""
    action_name: str
    action_description: Optional[str] = None
    action_type: str
    action_url: Optional[str] = None
    display_order: int = 0

class TeacherQuickActionUpdate(BaseModel):
    """Update quick action"""
    action_name: Optional[str] = None
    action_description: Optional[str] = None
    action_type: Optional[str] = None
    action_url: Optional[str] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None

class TeacherQuickActionResponse(BaseModel):
    """Quick action response"""
    id: str
    teacher_id: str
    action_name: str
    action_description: Optional[str] = None
    action_type: str
    action_url: Optional[str] = None
    display_order: int = 0
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Preference schemas
class BetaTeacherPreferenceCreate(BaseModel):
    """Create preference"""
    preference_key: str
    preference_value: Optional[str] = None
    preference_type: Optional[str] = None

class BetaTeacherPreferenceUpdate(BaseModel):
    """Update preference"""
    preference_key: Optional[str] = None
    preference_value: Optional[str] = None
    preference_type: Optional[str] = None

class BetaTeacherPreferenceResponse(BaseModel):
    """Preference response"""
    id: str
    teacher_id: str
    preference_key: str
    preference_value: Optional[str] = None
    preference_type: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Statistics schemas
class TeacherStatisticsResponse(BaseModel):
    """Statistics response"""
    id: str
    teacher_id: str
    stat_date: datetime
    stat_type: str
    lessons_created: int = 0
    resources_uploaded: int = 0
    created_at: datetime

    class Config:
        from_attributes = True


# Goal schemas
class TeacherGoalCreate(BaseModel):
    """Create goal"""
    goal_title: str
    goal_description: Optional[str] = None
    goal_type: str
    target_value: Optional[float] = None
    target_date: Optional[datetime] = None

class TeacherGoalUpdate(BaseModel):
    """Update goal"""
    goal_title: Optional[str] = None
    goal_description: Optional[str] = None
    goal_type: Optional[str] = None
    target_value: Optional[float] = None
    current_value: Optional[float] = None
    target_date: Optional[datetime] = None
    is_completed: Optional[bool] = None
    is_active: Optional[bool] = None

class TeacherGoalResponse(BaseModel):
    """Goal response"""
    id: str
    teacher_id: str
    goal_title: str
    goal_description: Optional[str] = None
    goal_type: str
    target_value: Optional[float] = None
    current_value: float = 0
    is_completed: bool = False
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Learning path schemas
class TeacherLearningPathCreate(BaseModel):
    """Create learning path"""
    path_name: str
    path_description: Optional[str] = None
    path_category: Optional[str] = None
    difficulty_level: Optional[str] = None

class TeacherLearningPathUpdate(BaseModel):
    """Update learning path"""
    path_name: Optional[str] = None
    path_description: Optional[str] = None
    is_completed: Optional[bool] = None
    is_active: Optional[bool] = None

class TeacherLearningPathResponse(BaseModel):
    """Learning path response"""
    id: str
    teacher_id: str
    path_name: str
    path_description: Optional[str] = None
    is_completed: bool = False
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    steps: List['LearningPathStepResponse'] = Field(default_factory=list)

    class Config:
        from_attributes = True

class LearningPathStepCreate(BaseModel):
    """Create learning path step"""
    step_title: str
    step_description: Optional[str] = None
    step_type: Optional[str] = None
    step_order: int = 0

class LearningPathStepResponse(BaseModel):
    """Learning path step response"""
    id: str
    learning_path_id: str
    step_title: str
    step_description: Optional[str] = None
    step_type: Optional[str] = None
    is_completed: bool = False
    step_order: int = 0
    created_at: datetime

    class Config:
        from_attributes = True


# Dashboard summary schema
class TeacherDashboardSummaryResponse(BaseModel):
    """Dashboard summary response"""
    teacher_id: str
    total_widgets: int = 0
    active_widgets: int = 0
    total_achievements: int = 0
    total_goals: int = 0
    active_goals: int = 0


# Update forward references
DashboardConfigResponse.model_rebuild()
BetaDashboardWidgetResponse.model_rebuild()
TeacherDashboardLayoutCreate.model_rebuild()
TeacherDashboardLayoutResponse.model_rebuild()
BetaDashboardWidgetInstanceCreate.model_rebuild()
BetaDashboardWidgetInstanceResponse.model_rebuild()
TeacherLearningPathResponse.model_rebuild()

