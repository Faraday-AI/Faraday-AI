"""
Organization Management Models

This module defines the database models for organization-related entities
in the Faraday AI system.
"""

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, JSON, DateTime, Table, Numeric
from sqlalchemy.orm import relationship, column_property
from datetime import datetime
from app.models.core.base import CoreBase
from app.models.mixins import TimestampedMixin, StatusMixin, MetadataMixin

class OrganizationRole(CoreBase, TimestampedMixin, StatusMixin, MetadataMixin):
    """Model for organization roles."""
    __tablename__ = "organization_roles"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    permissions = Column(JSON, nullable=False)
    is_system_role = Column(Boolean, default=False)
    settings = Column(JSON, nullable=True)

    # Relationships
    organization = relationship("Organization", back_populates="roles", lazy="joined")
    members = relationship("OrganizationMember", back_populates="role", lazy="joined")

    def __repr__(self):
        return f"<OrganizationRole {self.name}>"

class OrganizationSettings(CoreBase, TimestampedMixin, StatusMixin, MetadataMixin):
    """Model for organization settings."""
    __tablename__ = "organization_settings"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), unique=True)
    
    # General settings
    theme = Column(String, nullable=True)
    language = Column(String, nullable=True)
    timezone = Column(String, nullable=True)
    
    # Feature flags
    features = Column(JSON, nullable=True)
    enabled_modules = Column(JSON, nullable=True)
    experimental_features = Column(JSON, nullable=True)
    
    # Integration settings
    integrations = Column(JSON, nullable=True)
    api_keys = Column(JSON, nullable=True)
    webhooks = Column(JSON, nullable=True)
    
    # Notification settings
    notification_preferences = Column(JSON, nullable=True)
    email_settings = Column(JSON, nullable=True)
    alert_settings = Column(JSON, nullable=True)
    
    # Security settings
    security_policies = Column(JSON, nullable=True)
    access_controls = Column(JSON, nullable=True)
    audit_settings = Column(JSON, nullable=True)
    
    # Custom settings
    custom_settings = Column(JSON, nullable=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="settings", lazy="joined", uselist=False)

    def __repr__(self):
        return f"<OrganizationSettings for {self.organization.name if self.organization else 'Unknown Organization'}>"

class Organization(CoreBase, TimestampedMixin, StatusMixin, MetadataMixin):
    """Model for organizations."""
    __tablename__ = "organizations"
    __table_args__ = {'extend_existing': True}
    __mapper_args__ = {
        'exclude_properties': ['settings']  # Exclude the settings column from the mapper
    }

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # enterprise, academic, research, etc.
    subscription_tier = Column(String, nullable=False)
    settings_data = Column(JSON, nullable=True)
    credits_balance = Column(Numeric(10, 2), default=0)

    # Relationships
    departments = relationship("Department", back_populates="organization", lazy="joined")
    members = relationship("OrganizationMember", back_populates="organization", lazy="joined")
    roles = relationship("OrganizationRole", back_populates="organization", lazy="joined")
    resources = relationship("OrganizationResource", back_populates="organization", lazy="joined")
    settings = relationship("OrganizationSettings", back_populates="organization", lazy="joined", uselist=False)
    source_collaborations = relationship("OrganizationCollaboration", foreign_keys="[OrganizationCollaboration.source_org_id]", back_populates="source_organization", lazy="joined")
    target_collaborations = relationship("OrganizationCollaboration", foreign_keys="[OrganizationCollaboration.target_org_id]", back_populates="target_organization", lazy="joined")
    users = relationship("app.models.core.user.User", back_populates="organization", lazy="joined")
    user_organizations = relationship("app.models.user_management.user.user_management.UserOrganization", back_populates="organization")
    projects = relationship("DashboardProject", back_populates="organization")
    dashboard_teams = relationship("app.dashboard.models.team.DashboardTeam", back_populates="organization")
    dashboard_gpt_subscriptions = relationship("app.dashboard.models.gpt_models.DashboardGPTSubscription", back_populates="organization")
    gpt_usage = relationship("app.dashboard.models.gpt_models.GPTUsage", back_populates="organization")
    gpt_integrations = relationship("app.dashboard.models.gpt_models.GPTIntegration", back_populates="organization")
    gpt_analytics = relationship("app.dashboard.models.gpt_models.GPTAnalytics", back_populates="organization")
    gpt_feedback = relationship("app.dashboard.models.gpt_models.GPTFeedback", back_populates="organization")
    gpt_definitions = relationship("app.dashboard.models.gpt_models.GPTDefinition", back_populates="organization")
    core_gpt_definitions = relationship("app.models.gpt.base.gpt.CoreGPTDefinition", back_populates="organization")
    core_gpt_integrations = relationship("app.models.gpt.integration.models.CoreGPTIntegration", back_populates="organization")
    dashboard_widgets = relationship("app.dashboard.models.dashboard_models.DashboardWidget", back_populates="organization")
    dashboards = relationship("app.dashboard.models.dashboard_models.Dashboard", back_populates="organization")
    dashboard_shares = relationship("app.dashboard.models.dashboard_models.DashboardShare", back_populates="organization")
    dashboard_filters = relationship("app.dashboard.models.dashboard_models.DashboardFilter", back_populates="organization")
    context_interactions = relationship("app.models.gpt.context.models.ContextInteraction", back_populates="organization")
    context_summaries = relationship("app.models.gpt.context.models.ContextSummary", back_populates="organization")
    context_backups = relationship("app.models.gpt.context.models.ContextBackup", back_populates="organization")
    shared_contexts = relationship("app.models.gpt.context.models.SharedContext", back_populates="shared_with_organization")

    def __repr__(self):
        return f"<Organization {self.name}>"

class Department(CoreBase, TimestampedMixin, StatusMixin, MetadataMixin):
    """Model for organization departments."""
    __tablename__ = "departments"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    settings = Column(JSON, nullable=True)

    # Relationships
    organization = relationship("Organization", back_populates="departments", lazy="joined")
    members = relationship("DepartmentMember", back_populates="department", lazy="joined")
    users = relationship("app.models.core.user.User", back_populates="department", lazy="joined")

    def __repr__(self):
        return f"<Department {self.name}>"

class OrganizationMember(CoreBase, TimestampedMixin, StatusMixin, MetadataMixin):
    """Model for organization members."""
    __tablename__ = "organization_members"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    role_id = Column(Integer, ForeignKey("organization_roles.id"))
    permissions = Column(JSON, nullable=True)

    # Relationships
    organization = relationship("Organization", back_populates="members", lazy="joined")
    user = relationship("app.models.core.user.User", back_populates="organization_memberships", lazy="joined")
    role = relationship("OrganizationRole", back_populates="members", lazy="joined")

    def __repr__(self):
        return f"<OrganizationMember {self.role.name if self.role else 'No Role'}>"

class DepartmentMember(CoreBase, TimestampedMixin, StatusMixin, MetadataMixin):
    """Model for department members."""
    __tablename__ = "department_members"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    department_id = Column(Integer, ForeignKey("departments.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    role = Column(String, nullable=False)
    permissions = Column(JSON, nullable=True)

    # Relationships
    department = relationship("Department", back_populates="members", lazy="joined")
    user = relationship("app.models.core.user.User", back_populates="department_memberships", lazy="joined")

    def __repr__(self):
        return f"<DepartmentMember {self.role}>"

class OrganizationResource(CoreBase, TimestampedMixin, StatusMixin, MetadataMixin):
    """Model for organization resources."""
    __tablename__ = "organization_resources"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    settings = Column(JSON, nullable=True)

    # Relationships
    organization = relationship("Organization", back_populates="resources", lazy="joined")

    def __repr__(self):
        return f"<OrganizationResource {self.name}>"

class OrganizationCollaboration(CoreBase, TimestampedMixin, StatusMixin, MetadataMixin):
    """Model for organization collaborations."""
    __tablename__ = "organization_collaborations"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    source_org_id = Column(Integer, ForeignKey("organizations.id"))
    target_org_id = Column(Integer, ForeignKey("organizations.id"))
    type = Column(String, nullable=False)
    settings = Column(JSON, nullable=True)

    # Relationships
    source_organization = relationship("Organization", foreign_keys=[source_org_id], back_populates="source_collaborations", lazy="joined")
    target_organization = relationship("Organization", foreign_keys=[target_org_id], back_populates="target_collaborations", lazy="joined")

    def __repr__(self):
        return f"<OrganizationCollaboration {self.type}>" 