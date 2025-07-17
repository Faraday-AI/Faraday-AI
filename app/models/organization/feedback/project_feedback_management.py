"""
Project and Feedback Management Models

This module defines the database models for project management,
feedback handling, and related functionality in the Faraday AI application.
"""

from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime, JSON, Enum, Boolean, Text, Table
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.base_class import Base
from app.models.mixins import StatusMixin, MetadataMixin, AuditableModel

# Project Management Enums
class ProjectStatus(str, enum.Enum):
    """Enumeration of project statuses."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"
    COMPLETED = "completed"
    ON_HOLD = "on_hold"
    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"

class ProjectPriority(str, enum.Enum):
    """Enumeration of project priorities."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"

class ProjectType(str, enum.Enum):
    """Enumeration of project types."""
    PERSONAL = "personal"
    TEAM = "team"
    ORGANIZATION = "organization"
    TEMPLATE = "template"
    RESEARCH = "research"
    DEVELOPMENT = "development"
    PRODUCTION = "production"

# Feedback Management Enums
class FeedbackType(str, enum.Enum):
    """Enumeration of feedback types."""
    BUG = "bug"
    FEATURE = "feature"
    IMPROVEMENT = "improvement"
    QUESTION = "question"
    COMPLAINT = "complaint"
    PRAISE = "praise"
    SUGGESTION = "suggestion"
    OTHER = "other"

class FeedbackStatus(str, enum.Enum):
    """Enumeration of feedback statuses."""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"
    REOPENED = "reopened"
    DUPLICATE = "duplicate"
    WONT_FIX = "wont_fix"

class FeedbackPriority(str, enum.Enum):
    """Enumeration of feedback priorities."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"

# Project Management Models
class FeedbackProject(Base, StatusMixin, MetadataMixin):
    """Model for managing feedback projects and their configurations."""
    __tablename__ = "feedback_projects"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    project_type = Column(Enum(ProjectType), nullable=False)
    status = Column(Enum(ProjectStatus), nullable=False, default=ProjectStatus.ACTIVE)
    priority = Column(Enum(ProjectPriority), nullable=True)
    
    # Configuration
    configuration = Column(JSON, nullable=True)
    settings = Column(JSON, nullable=True)
    metadata_data = Column(JSON, nullable=True)
    
    # Timestamps
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    last_activity = Column(DateTime, nullable=True)
    
    # Flags
    is_template = Column(Boolean, default=False)
    is_archived = Column(Boolean, default=False)
    is_public = Column(Boolean, default=False)
    
    # Foreign keys
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    parent_project_id = Column(Integer, ForeignKey("feedback_projects.id"), nullable=True)
    
    # Relationships
    owner = relationship("User", foreign_keys=[owner_id], back_populates="owned_feedback_projects")
    team = relationship("Team", back_populates="feedback_projects")
    organization = relationship("Organization", back_populates="feedback_projects")
    parent_project = relationship("FeedbackProject", remote_side=[id], back_populates="sub_projects")
    sub_projects = relationship("FeedbackProject", back_populates="parent_project")
    members = relationship("ProjectMember", back_populates="project")
    feedback = relationship("Feedback", back_populates="project")
    comments = relationship("Comment", back_populates="project")
    resources = relationship("ProjectResource", back_populates="project")
    tasks = relationship("ProjectTask", back_populates="project")
    milestones = relationship("ProjectMilestone", back_populates="project")

    def dict(self):
        """Convert model to dictionary."""
        return {
            **super().dict(),
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "project_type": self.project_type.value if self.project_type else None,
            "status": self.status.value if self.status else None,
            "priority": self.priority.value if self.priority else None,
            "configuration": self.configuration,
            "settings": self.settings,
            "metadata": self.metadata_data,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None,
            "is_template": self.is_template,
            "is_archived": self.is_archived,
            "is_public": self.is_public,
            "owner_id": self.owner_id,
            "team_id": self.team_id,
            "organization_id": self.organization_id,
            "parent_project_id": self.parent_project_id
        }

class ProjectMember(Base, StatusMixin, MetadataMixin):
    """Model for managing project memberships."""
    __tablename__ = "project_members"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("feedback_projects.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String, nullable=False)
    permissions = Column(JSON, nullable=True)
    joined_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, nullable=True)
    
    # Relationships
    project = relationship("FeedbackProject", back_populates="members")
    user = relationship("User", back_populates="project_memberships")

    def dict(self):
        """Convert model to dictionary."""
        return {
            **super().dict(),
            "id": self.id,
            "project_id": self.project_id,
            "user_id": self.user_id,
            "role": self.role,
            "permissions": self.permissions,
            "joined_at": self.joined_at.isoformat() if self.joined_at else None,
            "last_active": self.last_active.isoformat() if self.last_active else None
        }

class ProjectResource(Base, StatusMixin, MetadataMixin):
    """Model for managing project resources."""
    __tablename__ = "project_resources"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("feedback_projects.id"), nullable=False)
    resource_type = Column(String, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    url = Column(String, nullable=True)
    metadata_data = Column(JSON, nullable=True)
    
    # Relationships
    project = relationship("FeedbackProject", back_populates="resources")

    def dict(self):
        """Convert model to dictionary."""
        return {
            **super().dict(),
            "id": self.id,
            "project_id": self.project_id,
            "resource_type": self.resource_type,
            "name": self.name,
            "description": self.description,
            "url": self.url,
            "metadata": self.metadata_data
        }

class ProjectTask(Base, StatusMixin, MetadataMixin):
    """Model for managing project tasks."""
    __tablename__ = "project_tasks"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("feedback_projects.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String, nullable=False)
    priority = Column(String, nullable=True)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    due_date = Column(DateTime, nullable=True)
    
    # Relationships
    project = relationship("FeedbackProject", back_populates="tasks")
    assignee = relationship("User", back_populates="assigned_tasks")

    def dict(self):
        """Convert model to dictionary."""
        return {
            **super().dict(),
            "id": self.id,
            "project_id": self.project_id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "assigned_to": self.assigned_to,
            "due_date": self.due_date.isoformat() if self.due_date else None
        }

class ProjectMilestone(Base, StatusMixin, MetadataMixin):
    """Model for managing project milestones."""
    __tablename__ = "project_milestones"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("feedback_projects.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    due_date = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    project = relationship("FeedbackProject", back_populates="milestones")

    def dict(self):
        """Convert model to dictionary."""
        return {
            **super().dict(),
            "id": self.id,
            "project_id": self.project_id,
            "title": self.title,
            "description": self.description,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }

# Feedback Management Models
class Feedback(Base, StatusMixin, MetadataMixin):
    """Model for managing user feedback."""
    __tablename__ = "organization_feedback"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("feedback_projects.id"), nullable=True)
    gpt_id = Column(Integer, ForeignKey("core_gpt_definitions.id"), nullable=True)
    category_id = Column(Integer, ForeignKey("feedback_categories.id"), nullable=True)
    feedback_type = Column(Enum(FeedbackType), nullable=False)
    status = Column(Enum(FeedbackStatus), nullable=False, default=FeedbackStatus.OPEN)
    priority = Column(Enum(FeedbackPriority), nullable=True)
    
    # Content
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    rating = Column(Integer, nullable=True)
    tags = Column(JSON, nullable=True)
    
    # Metadata
    source = Column(String, nullable=True)
    browser_info = Column(JSON, nullable=True)
    device_info = Column(JSON, nullable=True)
    
    # Timestamps
    resolved_at = Column(DateTime, nullable=True)
    closed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="feedback")
    project = relationship("FeedbackProject", back_populates="feedback")
    gpt = relationship("app.models.gpt.base.gpt.GPTDefinition", back_populates="feedback")
    category = relationship("FeedbackCategory", back_populates="feedback")
    responses = relationship("FeedbackResponse", back_populates="feedback")
    actions = relationship("FeedbackAction", back_populates="feedback")
    comments = relationship("FeedbackComment", back_populates="feedback")
    attachments = relationship("FeedbackAttachment", back_populates="feedback")

    def dict(self):
        """Convert model to dictionary."""
        return {
            **super().dict(),
            "id": self.id,
            "user_id": self.user_id,
            "project_id": self.project_id,
            "gpt_id": self.gpt_id,
            "category_id": self.category_id,
            "feedback_type": self.feedback_type.value if self.feedback_type else None,
            "status": self.status.value if self.status else None,
            "priority": self.priority.value if self.priority else None,
            "title": self.title,
            "content": self.content,
            "rating": self.rating,
            "tags": self.tags,
            "source": self.source,
            "browser_info": self.browser_info,
            "device_info": self.device_info,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "closed_at": self.closed_at.isoformat() if self.closed_at else None
        }

class FeedbackComment(Base, MetadataMixin):
    """Model for managing feedback comments."""
    __tablename__ = "feedback_comments"

    id = Column(Integer, primary_key=True)
    feedback_id = Column(Integer, ForeignKey("feedback.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    is_internal = Column(Boolean, default=False)
    
    # Relationships
    feedback = relationship("Feedback", back_populates="comments")
    user = relationship("User", back_populates="feedback_comments")

    def dict(self):
        """Convert model to dictionary."""
        return {
            **super().dict(),
            "id": self.id,
            "feedback_id": self.feedback_id,
            "user_id": self.user_id,
            "content": self.content,
            "is_internal": self.is_internal
        }

class FeedbackAttachment(Base, MetadataMixin):
    """Model for managing feedback attachments."""
    __tablename__ = "feedback_attachments"

    id = Column(Integer, primary_key=True)
    feedback_id = Column(Integer, ForeignKey("feedback.id"), nullable=False)
    file_name = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    file_url = Column(String, nullable=False)
    metadata_data = Column(JSON, nullable=True)
    
    # Relationships
    feedback = relationship("Feedback", back_populates="attachments")

    def dict(self):
        """Convert model to dictionary."""
        return {
            **super().dict(),
            "id": self.id,
            "feedback_id": self.feedback_id,
            "file_name": self.file_name,
            "file_type": self.file_type,
            "file_size": self.file_size,
            "file_url": self.file_url,
            "metadata": self.metadata_data
        }

class ProjectFeedback(Base, StatusMixin, MetadataMixin):
    """Model for managing project-specific feedback."""
    __tablename__ = "project_feedback"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("feedback_projects.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("feedback_categories.id"), nullable=True)
    feedback_type = Column(Enum(FeedbackType), nullable=False)
    status = Column(Enum(FeedbackStatus), nullable=False, default=FeedbackStatus.OPEN)
    priority = Column(Enum(FeedbackPriority), nullable=True)
    
    # Content
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    rating = Column(Integer, nullable=True)
    tags = Column(JSON, nullable=True)
    
    # Metadata
    source = Column(String, nullable=True)
    browser_info = Column(JSON, nullable=True)
    device_info = Column(JSON, nullable=True)
    
    # Timestamps
    resolved_at = Column(DateTime, nullable=True)
    closed_at = Column(DateTime, nullable=True)
    
    # Relationships
    project = relationship("FeedbackProject", back_populates="project_feedback")
    user = relationship("User", back_populates="project_feedback")
    category = relationship("FeedbackCategory", back_populates="project_feedback")
    comments = relationship("FeedbackComment", back_populates="project_feedback")
    attachments = relationship("FeedbackAttachment", back_populates="project_feedback")

    def dict(self):
        """Convert model to dictionary."""
        return {
            **super().dict(),
            "id": self.id,
            "project_id": self.project_id,
            "user_id": self.user_id,
            "category_id": self.category_id,
            "feedback_type": self.feedback_type.value if self.feedback_type else None,
            "status": self.status.value if self.status else None,
            "priority": self.priority.value if self.priority else None,
            "title": self.title,
            "content": self.content,
            "rating": self.rating,
            "tags": self.tags,
            "source": self.source,
            "browser_info": self.browser_info,
            "device_info": self.device_info,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "closed_at": self.closed_at.isoformat() if self.closed_at else None
        }

class FeedbackCategory(Base, StatusMixin, MetadataMixin):
    """Model for managing feedback categories."""
    __tablename__ = "feedback_categories"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    color = Column(String, nullable=True)  # For UI display
    icon = Column(String, nullable=True)   # For UI display
    settings = Column(JSON, nullable=True)
    
    # Relationships
    feedback = relationship("Feedback", back_populates="category")
    project_feedback = relationship("ProjectFeedback", back_populates="category")

    def dict(self):
        """Convert model to dictionary."""
        return {
            **super().dict(),
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "color": self.color,
            "icon": self.icon,
            "settings": self.settings
        }

class FeedbackResponse(Base, StatusMixin, MetadataMixin):
    """Model for managing feedback responses."""
    __tablename__ = "feedback_responses"

    id = Column(Integer, primary_key=True)
    feedback_id = Column(Integer, ForeignKey("feedback.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    is_internal = Column(Boolean, default=False)
    is_resolution = Column(Boolean, default=False)
    resolution_type = Column(String, nullable=True)  # e.g., "fixed", "wont_fix", "duplicate"
    resolution_notes = Column(Text, nullable=True)
    
    # Timestamps
    responded_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    feedback = relationship("Feedback", back_populates="responses")
    user = relationship("User", back_populates="feedback_responses")
    attachments = relationship("FeedbackAttachment", back_populates="response")

    def dict(self):
        """Convert model to dictionary."""
        return {
            **super().dict(),
            "id": self.id,
            "feedback_id": self.feedback_id,
            "user_id": self.user_id,
            "content": self.content,
            "is_internal": self.is_internal,
            "is_resolution": self.is_resolution,
            "resolution_type": self.resolution_type,
            "resolution_notes": self.resolution_notes,
            "responded_at": self.responded_at.isoformat() if self.responded_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class FeedbackAction(Base, StatusMixin, MetadataMixin):
    """Model for managing feedback actions."""
    __tablename__ = "feedback_actions"

    id = Column(Integer, primary_key=True)
    feedback_id = Column(Integer, ForeignKey("feedback.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action_type = Column(String, nullable=False)  # e.g., "assign", "close", "reopen", "change_priority"
    action_data = Column(JSON, nullable=True)  # Additional data specific to the action type
    notes = Column(Text, nullable=True)
    
    # Timestamps
    performed_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    feedback = relationship("Feedback", back_populates="actions")
    user = relationship("User", back_populates="feedback_actions")

    def dict(self):
        """Convert model to dictionary."""
        return {
            **super().dict(),
            "id": self.id,
            "feedback_id": self.feedback_id,
            "user_id": self.user_id,
            "action_type": self.action_type,
            "action_data": self.action_data,
            "notes": self.notes,
            "performed_at": self.performed_at.isoformat() if self.performed_at else None
        } 