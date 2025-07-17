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
    reported_incidents = relationship("SafetyIncidentBase", back_populates="teacher", lazy="joined")
    security_incidents = relationship(
        "app.models.security.incident.security.SecurityIncidentManagement",
        foreign_keys="[app.models.security.incident.security.SecurityIncidentManagement.reported_by]",
        back_populates="reporter",
        lazy="joined"
    )
    assigned_incidents = relationship(
        "app.models.security.incident.security.SecurityIncidentManagement",
        foreign_keys="[app.models.security.incident.security.SecurityIncidentManagement.assigned_to]",
        back_populates="assignee",
        lazy="joined"
    )
    security_audits = relationship("app.models.security.audit.security.SecurityAudit", back_populates="teacher", lazy="joined")
    conducted_assessments = relationship("app.models.physical_education.activity.models.ActivityAssessment", back_populates="assessor", lazy="joined")
    conducted_risk_assessments = relationship("RiskAssessment", back_populates="assessor", lazy="joined")
    conducted_checks = relationship("SafetyCheck", back_populates="checker", foreign_keys="[SafetyCheck.checked_by]", lazy="joined")
    conducted_environmental_checks = relationship("EnvironmentalCheck", back_populates="checker", lazy="joined")
    reviewed_protocols = relationship("SafetyProtocol", back_populates="reviewer", foreign_keys="[SafetyProtocol.reviewed_by]", lazy="joined")
    created_alerts = relationship("SafetyAlert", back_populates="creator", lazy="joined")
    created_protocols = relationship("SafetyProtocol", back_populates="creator", foreign_keys="[SafetyProtocol.created_by]", lazy="joined")
    performed_checks = relationship("SafetyCheck", back_populates="performer", foreign_keys="[SafetyCheck.performed_by]", lazy="joined")
    # safety_reports = relationship("SafetyReport", back_populates="reporter", lazy="joined")
    api_keys = relationship("app.models.security.api_key.api_key.APIKey", back_populates="teacher", foreign_keys="[app.models.security.api_key.api_key.APIKey.user_id]", lazy="joined")
    dashboard_api_keys = relationship("app.dashboard.models.security.DashboardAPIKey", back_populates="user", lazy="joined")
    created_exercises = relationship("app.models.physical_education.exercise.models.Exercise", back_populates="creator", lazy="joined")
    physical_education_classes = relationship("app.models.physical_education.class_.models.PhysicalEducationClass", back_populates="teacher", foreign_keys="[app.models.physical_education.class_.models.PhysicalEducationClass.teacher_id]", lazy="joined")
    resource_usage = relationship("app.models.resource_management.resource_management.ResourceUsage", back_populates="user", lazy="joined")
    resource_thresholds = relationship("app.models.resource_management.resource_management.ResourceThreshold", back_populates="user", lazy="joined")
    resource_optimization_thresholds = relationship("app.models.resource_management.optimization.models.ResourceOptimizationThreshold", back_populates="user", lazy="joined")
    resource_optimizations = relationship("app.models.resource_management.resource_management.ResourceOptimization", back_populates="user", lazy="joined")
    resource_optimization_recommendations = relationship("app.models.resource_management.optimization.models.ResourceOptimizationRecommendation", back_populates="user", lazy="joined")
    optimization_events = relationship("app.models.resource_management.resource_management.OptimizationEvent", back_populates="user", lazy="joined")
    resource_optimization_events = relationship("app.models.resource_management.optimization.models.ResourceOptimizationEvent", back_populates="user", lazy="joined")
    resource_events = relationship("ResourceEvent", back_populates="user", lazy="joined", overlaps="user")
    resource_alerts = relationship("ResourceAlert", back_populates="user", lazy="joined", overlaps="user")
    owned_resources = relationship("app.models.resource_management.resource_management.ResourceSharing", foreign_keys="[app.models.resource_management.resource_management.ResourceSharing.owner_id]", back_populates="owner", lazy="joined")
    shared_resources = relationship("app.models.resource_management.resource_management.ResourceSharing", foreign_keys="[app.models.resource_management.resource_management.ResourceSharing.shared_with_user_id]", back_populates="shared_with_user", lazy="joined")
    memories = relationship("UserMemory", back_populates="user", lazy="joined")
    lessons = relationship("Lesson", back_populates="user", lazy="joined")
    gpt_subscriptions = relationship("app.models.gpt.subscription.models.CoreGPTSubscription", back_populates="user", lazy="joined")
    gpt_definitions = relationship("app.models.gpt.base.gpt.CoreGPTDefinition", back_populates="user", lazy="joined")
    gpt_contexts = relationship("app.models.gpt.context.models.GPTContext", back_populates="user", lazy="joined")
    context_interactions = relationship("app.models.gpt.context.models.ContextInteraction", back_populates="user", lazy="joined")
    context_summaries = relationship("app.models.gpt.context.models.ContextSummary", back_populates="user", lazy="joined")
    context_backups = relationship("app.models.gpt.context.models.ContextBackup", back_populates="user", lazy="joined")
    owned_shared_contexts = relationship("app.models.gpt.context.models.SharedContext", foreign_keys="[app.models.gpt.context.models.SharedContext.owner_id]", back_populates="owner", lazy="joined")
    shared_contexts = relationship("app.models.gpt.context.models.SharedContext", foreign_keys="[app.models.gpt.context.models.SharedContext.shared_with_user_id]", back_populates="shared_with_user", lazy="joined")
    context_sharing_instances = relationship("app.models.gpt.context.models.ContextSharing", back_populates="shared_with_user", lazy="joined")
    gpt_performance_metrics = relationship("app.models.gpt.performance.models.CoreGPTPerformance", back_populates="user", lazy="joined")
    gpt_integrations = relationship("app.models.gpt.integration.models.CoreGPTIntegration", back_populates="user", lazy="joined")
    projects = relationship("app.models.organization.projects.project_management.OrganizationProject", back_populates="user", lazy="joined", viewonly=True)
    organization_projects = relationship("app.models.organization.projects.project_management.OrganizationProject", back_populates="user", lazy="joined")
    feedback = relationship("app.models.feedback.base.feedback.Feedback", back_populates="user", lazy="joined")
    # shared_gpts = relationship("app.models.gpt.base.gpt.GPTDefinition", secondary="gpt_sharing", back_populates="shared_with_users", lazy="joined")
    audit_logs = relationship("app.models.audit_log.AuditLog", back_populates="user", lazy="joined")
    security_audit_logs = relationship("app.models.security.audit.security.SecurityAuditLog", back_populates="user", lazy="joined")
    security_policy_audit_logs = relationship("app.models.security.policy.security.SecurityPolicyAuditLog", back_populates="user", lazy="joined")
    # ai_suite = relationship("AISuite", back_populates="user", lazy="joined")
    # assigned_tools = relationship("AITool", secondary="tool_assignments", back_populates="assigned_users", lazy="joined")
    # tool_usage_logs = relationship("ToolUsageLog", back_populates="user", lazy="joined")
    organization = relationship("Organization", back_populates="users", lazy="joined")
    department = relationship("Department", back_populates="users", lazy="joined")
    core_widgets = relationship("app.models.dashboard.widgets.widget.CoreDashboardWidget", back_populates="user", lazy="joined")
    themes = relationship("DashboardTheme", back_populates="user", lazy="joined")
    dashboard_shares = relationship("app.dashboard.models.dashboard_models.DashboardShare", back_populates="user", lazy="joined")
    dashboard_share_configs = relationship("app.models.dashboard.sharing.share.DashboardShareConfig", back_populates="user", lazy="joined")
    dashboard_filters = relationship("app.dashboard.models.dashboard_models.DashboardFilter", back_populates="user", lazy="joined")
    dashboard_filter_configs = relationship("app.models.dashboard.filters.filter.DashboardFilterConfig", back_populates="user", lazy="joined")
    dashboard_exports = relationship("DashboardExport", back_populates="user", lazy="joined")
    dashboard_searches = relationship("DashboardSearch", back_populates="user", lazy="joined")
    organization_memberships = relationship("OrganizationMember", back_populates="user")
    department_memberships = relationship("DepartmentMember", back_populates="user")
    team_memberships = relationship("app.models.organization.team.TeamMember", back_populates="user")
    project_memberships = relationship("app.models.organization.projects.project_management.ProjectMember", back_populates="user")
    assigned_tasks = relationship("app.models.organization.projects.project_management.ProjectTask", back_populates="assignee")
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
    sessions = relationship("app.models.security.policy.security.Session", back_populates="user", lazy="joined")
    user_sessions = relationship("app.models.user_management.user.user_management.UserSession", back_populates="user", lazy="joined")
    organizations = relationship("UserOrganization", back_populates="user")
    created_adaptations = relationship("app.models.activity_adaptation.activity.activity_adaptation.ActivityAdaptation", back_populates="creator")
    teacher = relationship("PhysicalEducationTeacher", back_populates="user", uselist=False, lazy="joined")
    physical_education_teacher = relationship("app.models.physical_education.teacher.models.PhysicalEducationTeacher", back_populates="user", uselist=False, lazy="joined", overlaps="teacher")
    teacher_profile = relationship("app.models.educational.staff.teacher.Teacher", back_populates="user", uselist=False, lazy="joined")
    workout_sessions = relationship("app.models.physical_education.workout.models.WorkoutSession", back_populates="teacher", lazy="joined")
    workout_plans = relationship("app.models.physical_education.workout.models.WorkoutPlan", back_populates="teacher", lazy="joined")
    # health_checks = relationship("app.models.health_fitness.metrics.health.HealthCheck", back_populates="teacher")
    ip_allowlist_entries = relationship("app.models.security.policy.security.IPAllowlist", back_populates="created_by_user", lazy="joined")
    ip_blocklist_entries = relationship("app.models.security.policy.security.IPBlocklist", back_populates="created_by_user", lazy="joined")
    dashboard_user = relationship("app.dashboard.models.user.DashboardUser", back_populates="core_user", uselist=False, lazy="joined", foreign_keys="[app.dashboard.models.user.DashboardUser.core_user_id]")
    # context_templates = relationship("app.dashboard.models.context.ContextTemplate", back_populates="created_by_user", lazy="joined")
    user_roles = relationship("app.models.security.access_control.access_control_management.UserRole", back_populates="user", lazy="joined", overlaps="access_control_roles")
    dashboard_preferences = relationship("app.dashboard.models.user_preferences.UserPreferences", back_populates="user", lazy="joined")
    user_management_preferences = relationship("app.models.user_management.preferences.user_preferences_management.UserPreference", back_populates="user", lazy="joined")
    preference_templates = relationship("app.models.user_management.preferences.user_preferences_management.UserPreferenceTemplate", secondary="user_preference_template_assignments", back_populates="users")
    dashboard_notifications = relationship("app.dashboard.models.notification_models.Notification", back_populates="user", lazy="joined")
    dashboard_notification_preferences = relationship("app.dashboard.models.notification_models.NotificationPreference", back_populates="user", lazy="joined")
    dashboard_resource_usage = relationship("app.dashboard.models.resource_models.DashboardResourceUsage", back_populates="user", lazy="joined")
    dashboard_resource_thresholds = relationship("app.dashboard.models.resource_models.DashboardResourceThreshold", back_populates="user", lazy="joined")
    dashboard_resource_optimizations = relationship("app.dashboard.models.resource_models.DashboardResourceOptimization", back_populates="user", lazy="joined")
    dashboard_owned_resources = relationship("app.dashboard.models.resource_models.DashboardResourceSharing", foreign_keys="[app.dashboard.models.resource_models.DashboardResourceSharing.owner_id]", back_populates="owner", lazy="joined")
    dashboard_shared_resources = relationship("app.dashboard.models.resource_models.DashboardResourceSharing", foreign_keys="[app.dashboard.models.resource_models.DashboardResourceSharing.shared_with_user_id]", back_populates="shared_with_user", lazy="joined")
    dashboard_optimization_events = relationship("app.dashboard.models.resource_models.DashboardOptimizationEvent", back_populates="user", lazy="joined")
    dashboard_widgets = relationship("app.dashboard.models.dashboard_models.DashboardWidget", back_populates="user", lazy="joined")
    dashboards = relationship("app.dashboard.models.dashboard_models.Dashboard", back_populates="user", lazy="joined")

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