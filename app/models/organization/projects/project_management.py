"""
Project Management Models

This module defines the database models for project management functionality.
"""

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, JSON, DateTime, Table
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.shared_base import SharedBase as Base
from app.models.mixins import TimestampedMixin, StatusMixin, MetadataMixin
from app.models.organization.team import Team

class ProjectResource(Base, TimestampedMixin, StatusMixin, MetadataMixin):
    """Model for project resources."""
    __tablename__ = "project_resources"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("organization_projects.id"))
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # file, link, api, etc.
    description = Column(String, nullable=True)
    url = Column(String, nullable=True)
    settings = Column(JSON, nullable=True)

    # Relationships
    project = relationship("OrganizationProject", back_populates="resources")

    def __repr__(self):
        return f"<ProjectResource {self.name}>"

class ProjectSettings(Base, TimestampedMixin, StatusMixin, MetadataMixin):
    """Model for project settings."""
    __tablename__ = "project_settings"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("organization_projects.id"), unique=True)
    
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
    project = relationship("OrganizationProject", back_populates="settings", uselist=False)

    def __repr__(self):
        return f"<ProjectSettings for {self.project.name if self.project else 'Unknown Project'}>"

class ProjectRole(Base, TimestampedMixin, StatusMixin, MetadataMixin):
    """Model for project roles."""
    __tablename__ = "project_roles"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("organization_projects.id"))
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    permissions = Column(JSON, nullable=False)
    is_system_role = Column(Boolean, default=False)
    settings = Column(JSON, nullable=True)

    # Relationships
    members = relationship("ProjectMember", back_populates="role")

    def __repr__(self):
        return f"<ProjectRole {self.name}>"

class OrganizationProject(Base, TimestampedMixin, StatusMixin, MetadataMixin):
    """Model for organizing GPT activities and projects."""
    __tablename__ = "organization_projects"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    active_gpt_id = Column(String, nullable=True)
    configuration = Column(JSON, nullable=True)
    is_template = Column(Boolean, default=False)

    # Foreign Keys
    user_id = Column(Integer, ForeignKey("users.id"))
    team_id = Column(Integer, ForeignKey("teams.id"))

    # Relationships
    user = relationship("app.models.core.user.User", back_populates="organization_projects")
    team = relationship("Team", back_populates="organization_projects")
    comments = relationship("ProjectComment", back_populates="project")
    members = relationship("ProjectMember", back_populates="project")
    tasks = relationship("ProjectTask", back_populates="project")
    settings = relationship("ProjectSettings", back_populates="project", uselist=False)
    resources = relationship("ProjectResource", back_populates="project")
    gpt_definitions = relationship("app.models.gpt.base.gpt.CoreGPTDefinition", back_populates="project")
    gpt_integrations = relationship("app.models.gpt.integration.models.CoreGPTIntegration", back_populates="project")

    def __repr__(self):
        return f"<OrganizationProject {self.name}>"

class ProjectMember(Base, TimestampedMixin, StatusMixin, MetadataMixin):
    """Model for project members."""
    __tablename__ = "project_members"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("organization_projects.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    role_id = Column(Integer, ForeignKey("project_roles.id"))
    permissions = Column(JSON, nullable=True)

    # Relationships
    project = relationship("OrganizationProject", back_populates="members")
    user = relationship("User", back_populates="project_memberships")
    role = relationship("ProjectRole", back_populates="members")

    def __repr__(self):
        return f"<ProjectMember {self.role.name if self.role else 'No Role'}>"

class ProjectTask(Base, TimestampedMixin, StatusMixin, MetadataMixin):
    """Model for project tasks."""
    __tablename__ = "project_tasks"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("organization_projects.id"))
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    status = Column(String, nullable=False)
    priority = Column(String, nullable=True)
    due_date = Column(DateTime, nullable=True)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    project = relationship("OrganizationProject", back_populates="tasks")
    assignee = relationship("User", back_populates="assigned_tasks")

    def __repr__(self):
        return f"<ProjectTask {self.name}>"

class ProjectComment(Base, TimestampedMixin, StatusMixin, MetadataMixin):
    """Model for project comments."""
    __tablename__ = "project_comments"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("organization_projects.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    content = Column(String, nullable=False)
    parent_id = Column(Integer, ForeignKey("project_comments.id"), nullable=True)

    # Relationships
    project = relationship("OrganizationProject", back_populates="comments")
    user = relationship("User", back_populates="project_comments")
    parent = relationship("ProjectComment", remote_side=[id], backref="replies")

    def __repr__(self):
        return f"<Comment {self.id}>" 