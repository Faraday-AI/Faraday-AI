"""
User Model

This module defines the User model for the application.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text, Boolean, JSON, Numeric, Table
from sqlalchemy.orm import relationship
from pydantic import BaseModel as PydanticBaseModel, EmailStr, ConfigDict

from app.models.core.base import CoreBase
from app.models.mixins import TimestampedMixin, StatusMixin, MetadataMixin

# Many-to-many relationship table for user roles
user_roles = Table(
    'user_roles',
    CoreBase.metadata,
    Column('user_id', Integer, ForeignKey("users.id")),
    Column('role_id', Integer, ForeignKey('roles.id'))
)

class User(CoreBase, TimestampedMixin, StatusMixin, MetadataMixin):
    """User model for the application (represents teachers)."""
    
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    disabled = Column(Boolean, default=False)  # Alias for is_active for compatibility
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    preferences = Column(JSON, nullable=True)
    role = Column(String(50), nullable=False, default="teacher")
    subscription_status = Column(String, nullable=True)
    api_key = Column(String, unique=True, nullable=True)
    last_api_key_rotation = Column(DateTime, nullable=True)
    user_type = Column(String(50), nullable=True)
    billing_tier = Column(String(50), nullable=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    credits_balance = Column(Numeric(10, 2), default=0)

    # Relationships - using string references to avoid circular imports
    created_routines = relationship("AdaptedRoutine", back_populates="creator", lazy="dynamic")
    created_regular_routines = relationship("Routine", back_populates="creator", lazy="dynamic")
    reported_incidents = relationship("SafetyIncidentBase", back_populates="teacher", lazy="select")
    safety_incidents = relationship("app.models.physical_education.safety.models.SafetyIncident", back_populates="teacher", foreign_keys="[app.models.physical_education.safety.models.SafetyIncident.teacher_id]", lazy="select")
    security_incidents = relationship(
        "app.models.security.incident.security.SecurityIncidentManagement",
        foreign_keys="[app.models.security.incident.security.SecurityIncidentManagement.reported_by]",
        back_populates="reporter",
        lazy="select"
    )
    assigned_incidents = relationship(
        "app.models.security.incident.security.SecurityIncidentManagement",
        foreign_keys="[app.models.security.incident.security.SecurityIncidentManagement.assigned_to]",
        back_populates="assignee",
        lazy="select"
    )
    security_audits = relationship("app.models.security.audit.security.SecurityAudit", back_populates="teacher", lazy="select")
    conducted_assessments = relationship("app.models.physical_education.activity.models.ActivityAssessment", back_populates="assessor", lazy="select")
    conducted_risk_assessments = relationship("app.models.physical_education.safety.models.RiskAssessment", back_populates="assessor", lazy="select")
    skill_assessment_risk_assessments = relationship("app.models.skill_assessment.safety.safety.RiskAssessment", back_populates="assessor", lazy="select")
    conducted_checks = relationship("app.models.physical_education.safety.models.SafetyCheck", back_populates="checker", foreign_keys="[app.models.physical_education.safety.models.SafetyCheck.checked_by]", lazy="select")
    conducted_environmental_checks = relationship("app.models.physical_education.safety.models.EnvironmentalCheck", back_populates="checker", lazy="select")
    reviewed_protocols = relationship("app.models.physical_education.safety.models.SafetyProtocol", back_populates="reviewer", foreign_keys="[app.models.physical_education.safety.models.SafetyProtocol.reviewed_by]", lazy="select")
    created_alerts = relationship("app.models.physical_education.safety.models.SafetyAlert", back_populates="creator", lazy="select")
    skill_assessment_safety_alerts = relationship("app.models.skill_assessment.safety.safety.SafetyAlert", back_populates="creator", lazy="select")
    created_protocols = relationship("app.models.physical_education.safety.models.SafetyProtocol", back_populates="creator", foreign_keys="[app.models.physical_education.safety.models.SafetyProtocol.created_by]", lazy="select")
    skill_assessment_safety_protocols = relationship("app.models.skill_assessment.safety.safety.SafetyProtocol", back_populates="creator", lazy="select")
    performed_checks = relationship("app.models.physical_education.safety.models.SafetyCheck", back_populates="performer", foreign_keys="[app.models.physical_education.safety.models.SafetyCheck.performed_by]", lazy="select")
    skill_assessment_performed_checks = relationship("app.models.skill_assessment.safety.safety.SafetyCheck", back_populates="performer", lazy="select")
    performed_maintenance = relationship("app.models.physical_education.equipment.models.MaintenanceRecord", back_populates="maintainer", foreign_keys="[app.models.physical_education.equipment.models.MaintenanceRecord.maintainer_id]", lazy="select")
    safety_reports = relationship("app.models.skill_assessment.safety.safety.SafetyReport", back_populates="reporter", lazy="select")
    api_keys = relationship("app.models.security.api_key.api_key.APIKey", back_populates="teacher", foreign_keys="[app.models.security.api_key.api_key.APIKey.user_id]", lazy="select")
    dashboard_api_keys = relationship("app.dashboard.models.security.DashboardAPIKey", back_populates="user", lazy="select")
    created_exercises = relationship("app.models.physical_education.exercise.models.Exercise", back_populates="creator", lazy="select")
    physical_education_classes = relationship("app.models.physical_education.class_.models.PhysicalEducationClass", back_populates="teacher", foreign_keys="[app.models.physical_education.class_.models.PhysicalEducationClass.teacher_id]", lazy="select")
    # Phase 11 Resource Management relationships
    resource_usage = relationship("app.models.resource_management_old.resource_management.Phase11ResourceUsage", back_populates="user", lazy="select")
    resource_thresholds = relationship("app.models.resource_management_old.resource_management.Phase11ResourceThreshold", back_populates="user", lazy="select")
    resource_optimizations = relationship("app.models.resource_management_old.resource_management.Phase11ResourceOptimization", back_populates="user", lazy="select")
    optimization_events = relationship("app.models.resource_management_old.resource_management.Phase11OptimizationEvent", back_populates="user", lazy="select")
    # Additional resource management relationships
    resource_optimization_thresholds = relationship("app.models.resource_management_old.optimization.models.ResourceOptimizationThreshold", back_populates="user", lazy="select")
    resource_optimization_recommendations = relationship("app.models.resource_management_old.optimization.models.ResourceOptimizationRecommendation", back_populates="user", lazy="select")
    resource_optimization_events = relationship("app.models.resource_management_old.optimization.models.ResourceOptimizationEvent", back_populates="user", lazy="select")
    # Phase 11 Resource Sharing relationships
    owned_resources = relationship("app.models.resource_management_old.resource_management.Phase11ResourceSharing", foreign_keys="[app.models.resource_management_old.resource_management.Phase11ResourceSharing.owner_id]", back_populates="owner", lazy="select")
    shared_resources = relationship("app.models.resource_management_old.resource_management.Phase11ResourceSharing", foreign_keys="[app.models.resource_management_old.resource_management.Phase11ResourceSharing.shared_with_user_id]", back_populates="shared_with_user", lazy="select")
    # Phase 11 Resource Events relationships
    resource_events = relationship("app.models.resource_management_old.optimization.models.ResourceEvent", back_populates="user", lazy="select")
    resource_alerts = relationship("app.models.resource_management_old.optimization.models.ResourceAlert", back_populates="user", lazy="select")
    memories = relationship("UserMemory", back_populates="user", lazy="select")
    lessons = relationship("Lesson", back_populates="user", lazy="select")
    gpt_subscriptions = relationship("app.models.gpt.subscription.models.CoreGPTSubscription", back_populates="user", lazy="select")
    gpt_definitions = relationship("app.models.gpt.base.gpt.CoreGPTDefinition", back_populates="user", lazy="select")
    gpt_contexts = relationship("app.models.gpt.context.models.GPTContext", back_populates="user", lazy="select")
    context_interactions = relationship("app.models.gpt.context.models.ContextInteraction", back_populates="user", lazy="select")
    context_summaries = relationship("app.models.gpt.context.models.ContextSummary", back_populates="user", lazy="select")
    context_backups = relationship("app.models.gpt.context.models.ContextBackup", back_populates="user", lazy="select")
    owned_shared_contexts = relationship("app.models.gpt.context.models.SharedContext", foreign_keys="[app.models.gpt.context.models.SharedContext.owner_id]", back_populates="owner", lazy="select")
    shared_contexts = relationship("app.models.gpt.context.models.SharedContext", foreign_keys="[app.models.gpt.context.models.SharedContext.shared_with_user_id]", back_populates="shared_with_user", lazy="select")
    context_sharing_instances = relationship("app.models.gpt.context.models.ContextSharing", back_populates="shared_with_user", lazy="select")
    gpt_performance_metrics = relationship("app.models.gpt.performance.models.CoreGPTPerformance", back_populates="user", lazy="select")
    gpt_integrations = relationship("app.models.gpt.integration.models.CoreGPTIntegration", back_populates="user", lazy="select")
    projects = relationship("OrganizationProject", back_populates="user", lazy="select", viewonly=True)
    organization_projects = relationship("OrganizationProject", back_populates="user", lazy="select")
    feedback = relationship("app.models.feedback.base.feedback.Feedback", back_populates="user", lazy="select")
    organization_feedback = relationship("app.models.organization.feedback.project_feedback_management.OrganizationFeedback", back_populates="user")
    feedback_comments = relationship("app.models.organization.feedback.project_feedback_management.FeedbackComment", back_populates="user")
    feedback_responses = relationship("app.models.organization.feedback.project_feedback_management.FeedbackResponse", back_populates="user")
    feedback_actions = relationship("app.models.organization.feedback.project_feedback_management.FeedbackAction", back_populates="user")
    project_feedback = relationship("app.models.organization.feedback.project_feedback_management.ProjectFeedback", back_populates="user")
    
    # School relationships
    school_assignments = relationship("app.models.physical_education.schools.relationships.TeacherSchoolAssignment", back_populates="teacher", lazy="select")
    # Analytics relationships
    activities = relationship("app.models.analytics.user_analytics.UserActivity", back_populates="user")
    behaviors = relationship("app.models.analytics.user_analytics.UserBehavior", back_populates="user")
    performances = relationship("app.models.analytics.user_analytics.UserPerformance", back_populates="user")
    engagements = relationship("app.models.analytics.user_analytics.UserEngagement", back_populates="user")
    predictions = relationship("app.models.analytics.user_analytics.UserPrediction", back_populates="user")
    recommendations = relationship("app.models.analytics.user_analytics.UserRecommendation", back_populates="user")
    analytics_events = relationship("app.models.analytics.user_analytics.AnalyticsEvent", back_populates="user")
    insights = relationship("app.models.analytics.user_analytics.UserInsight", back_populates="user")
    trends = relationship("app.models.analytics.user_analytics.UserTrend", back_populates="user")
    comparisons = relationship("app.models.analytics.user_analytics.UserComparison", back_populates="user")
    # shared_gpts = relationship("app.models.gpt.base.gpt.GPTDefinition", secondary="gpt_sharing", back_populates="shared_with_users", lazy="select")
    audit_logs = relationship("app.models.audit_log.AuditLog", back_populates="user", lazy="select")
    security_audit_logs = relationship("app.models.security.audit.security.SecurityAuditLog", back_populates="user", lazy="select")
    security_policy_audit_logs = relationship("app.models.security.policy.security.SecurityPolicyAuditLog", back_populates="user", lazy="select")
    # ai_suite = relationship("AISuite", back_populates="user", lazy="select")
    # assigned_tools = relationship("AITool", secondary="tool_assignments", back_populates="assigned_users", lazy="select")
    # tool_usage_logs = relationship("ToolUsageLog", back_populates="user", lazy="select")
    organization = relationship("Organization", back_populates="users", lazy="select")
    department = relationship("Department", back_populates="users", lazy="select")
    core_widgets = relationship("app.models.dashboard.widgets.widget.CoreDashboardWidget", back_populates="user", lazy="select")
    themes = relationship("DashboardTheme", back_populates="user", lazy="select")
    dashboard_shares = relationship("app.dashboard.models.dashboard_models.DashboardShare", back_populates="user", lazy="select")
    dashboard_share_configs = relationship("app.models.dashboard.sharing.share.DashboardShareConfig", back_populates="user", lazy="select")
    dashboard_filters = relationship("app.dashboard.models.dashboard_models.DashboardFilter", back_populates="user", lazy="select")
    dashboard_filter_configs = relationship("app.models.dashboard.filters.filter.DashboardFilterConfig", back_populates="user", lazy="select")
    dashboard_exports = relationship("DashboardExport", back_populates="user", lazy="select")
    dashboard_searches = relationship("DashboardSearch", back_populates="user", lazy="select")
    organization_memberships = relationship("OrganizationMember", back_populates="user")
    department_memberships = relationship("DepartmentMember", back_populates="user")
    team_memberships = relationship("TeamMember", back_populates="user")
    project_memberships = relationship("app.models.organization.projects.project_management.ProjectMember", back_populates="user")
    assigned_tasks = relationship("app.models.organization.projects.project_management.ProjectTask", back_populates="assignee")
    assigned_feedback_tasks = relationship("app.models.organization.feedback.project_feedback_management.FeedbackProjectTask", back_populates="assignee")
    project_comments = relationship("app.models.organization.projects.project_management.ProjectComment", back_populates="user")
    avatar_customizations = relationship("app.models.user_management.avatar.customization.AvatarCustomization", back_populates="user")
    voice_preferences = relationship("app.models.user_management.avatar.voice.VoicePreference", back_populates="user")
    voices = relationship("app.models.user_management.avatar.voice.Voice", back_populates="user")
    avatars = relationship("app.models.user_management.avatar.models.UserAvatar", back_populates="user")
    tool_settings = relationship("app.dashboard.models.tool_registry.UserTool", back_populates="user")
    tools = relationship("app.dashboard.models.tool_registry.Tool", secondary="user_tools", back_populates="users")
    roles = relationship("Role", secondary=user_roles, back_populates="users")
    access_control_roles = relationship("app.models.security.access_control.access_control_management.AccessControlRole", secondary="access_control_user_roles", back_populates="users")
    profile = relationship("UserProfile", back_populates="user", uselist=False)
    sessions = relationship("app.models.security.policy.security.Session", back_populates="user", lazy="select")
    user_sessions = relationship("app.models.user_management.user.user_management.UserSession", back_populates="user", lazy="select")
    organizations = relationship("UserOrganization", back_populates="user")
    created_adaptations = relationship("app.models.activity_adaptation.activity.activity_adaptation.ActivityAdaptation", back_populates="creator")
    teacher = relationship("PhysicalEducationTeacher", back_populates="user", uselist=False, lazy="select")
    physical_education_teacher = relationship("app.models.physical_education.teacher.models.PhysicalEducationTeacher", back_populates="user", uselist=False, lazy="select", overlaps="teacher")
    teacher_profile = relationship("app.models.educational.staff.teacher.Teacher", back_populates="user", uselist=False, lazy="select")
    workout_sessions = relationship("app.models.physical_education.workout.models.WorkoutSession", back_populates="teacher", lazy="select")
    workout_plans = relationship("app.models.physical_education.workout.models.WorkoutPlan", back_populates="teacher", lazy="select")
    lesson_plans = relationship("app.models.lesson_plan.models.LessonPlan", back_populates="teacher", lazy="select")
    health_checks = relationship("app.models.physical_education.health.models.HealthCheck", back_populates="teacher")
    ip_allowlist_entries = relationship("app.models.security.policy.security.IPAllowlist", back_populates="created_by_user", lazy="select")
    ip_blocklist_entries = relationship("app.models.security.policy.security.IPBlocklist", back_populates="created_by_user", lazy="select")
    dashboard_user = relationship("app.dashboard.models.user.DashboardUser", back_populates="core_user", uselist=False, lazy="select", foreign_keys="[app.dashboard.models.user.DashboardUser.core_user_id]")
    # context_templates = relationship("app.dashboard.models.context.ContextTemplate", back_populates="created_by_user", lazy="select")
    user_roles = relationship("app.models.security.access_control.access_control_management.UserRole", back_populates="user", lazy="select", overlaps="access_control_roles")
    dashboard_preferences = relationship("app.dashboard.models.user_preferences.UserPreferences", back_populates="user", lazy="select")
    user_management_preferences = relationship("app.models.user_management.preferences.user_preferences_management.UserPreference", back_populates="user", lazy="select")
    preference_templates = relationship("app.models.user_management.preferences.user_preferences_management.UserPreferenceTemplate", secondary="user_preference_template_assignments", back_populates="users")
    dashboard_notifications = relationship("app.dashboard.models.notification_models.Notification", back_populates="user", lazy="select")
    dashboard_notification_preferences = relationship("app.dashboard.models.notification_models.NotificationPreference", back_populates="user", lazy="select")
    dashboard_resource_usage = relationship("app.dashboard.models.resource_models.DashboardResourceUsage", back_populates="user", lazy="select")
    dashboard_resource_thresholds = relationship("app.dashboard.models.resource_models.DashboardResourceThreshold", back_populates="user", lazy="select")
    dashboard_resource_optimizations = relationship("app.dashboard.models.resource_models.DashboardResourceOptimization", back_populates="user", lazy="select")
    dashboard_owned_resources = relationship("app.dashboard.models.resource_models.DashboardResourceSharing", foreign_keys="[app.dashboard.models.resource_models.DashboardResourceSharing.owner_id]", back_populates="owner", lazy="select")
    dashboard_shared_resources = relationship("app.dashboard.models.resource_models.DashboardResourceSharing", foreign_keys="[app.dashboard.models.resource_models.DashboardResourceSharing.shared_with_user_id]", back_populates="shared_with_user", lazy="select")
    dashboard_optimization_events = relationship("app.dashboard.models.resource_models.DashboardOptimizationEvent", back_populates="user", lazy="select")
    dashboard_widgets = relationship("app.dashboard.models.dashboard_models.DashboardWidget", back_populates="user", lazy="select")
    dashboards = relationship("app.dashboard.models.dashboard_models.Dashboard", back_populates="user", lazy="select")

    def __repr__(self):
        return f"<User {self.email}>"

class UserCreate(PydanticBaseModel):
    """Pydantic model for creating users."""
    
    email: EmailStr
    first_name: str
    last_name: str
    role: str = "teacher"
    is_active: bool = True
    is_superuser: bool = False

class UserUpdate(PydanticBaseModel):
    """Pydantic model for updating users."""
    
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None

class UserResponse(PydanticBaseModel):
    """Pydantic model for user responses."""
    
    id: int
    email: str
    first_name: str
    last_name: str
    role: str
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True) 