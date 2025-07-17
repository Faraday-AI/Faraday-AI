"""
User Management Models

This module defines the database models for user management, roles,
and permissions in the Faraday AI application.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON, Table, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.models.shared_base import SharedBase
from app.models.mixins import TimestampedMixin, StatusMixin, MetadataMixin
from app.models.user_management.avatar.base import Avatar

# Re-export for backward compatibility
BaseModelMixin = SharedBase
TimestampedMixin = TimestampedMixin

class UserRole(str, enum.Enum):
    """Enumeration of user roles."""
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    TEACHER = "teacher"
    STUDENT = "student"
    PARENT = "parent"
    STAFF = "staff"
    # Extensible for future roles

# Many-to-many relationship tables
# user_roles table is now defined in app.models.core.user to avoid circular imports
role_permissions = Table(
    'role_permissions',
    SharedBase.metadata,
    Column('role_id', Integer, ForeignKey('roles.id')),
    Column('permission_id', Integer, ForeignKey('permissions.id'))
)

class Role(SharedBase, StatusMixin):
    """Role model for defining user roles and associated permissions."""
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String)
    is_custom = Column(Boolean, default=False)

    # Relationships
    users = relationship("app.models.core.user.User", secondary="user_roles", back_populates="roles")
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")

    def dict(self):
        """Convert model to dictionary."""
        return {
            **super().dict(),
            "name": self.name,
            "description": self.description,
            "is_custom": self.is_custom,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class Permission(SharedBase, StatusMixin):
    """Permission model for defining granular access controls."""
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String)
    resource_type = Column(String, nullable=False)  # GPT, Analytics, etc.
    action = Column(String, nullable=False)  # read, write, execute, etc.

    # Relationships
    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")

    def dict(self):
        """Convert model to dictionary."""
        return {
            **super().dict(),
            "name": self.name,
            "description": self.description,
            "resource_type": self.resource_type,
            "action": self.action,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class UserProfile(SharedBase, MetadataMixin):
    """Extended user profile information."""
    __tablename__ = "user_profiles"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    avatar_id = Column(Integer, ForeignKey("avatars.id"))
    bio = Column(String)
    timezone = Column(String)
    language = Column(String)
    notification_preferences = Column(JSON)
    custom_settings = Column(JSON)

    # Relationships
    user = relationship("app.models.core.user.User", back_populates="profile")
    avatar = relationship("Avatar", back_populates="user_profile", uselist=False)

    def dict(self):
        """Convert model to dictionary."""
        return {
            **super().dict(),
            "user_id": self.user_id,
            "avatar_id": self.avatar_id,
            "bio": self.bio,
            "timezone": self.timezone,
            "language": self.language,
            "notification_preferences": self.notification_preferences,
            "custom_settings": self.custom_settings,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class UserOrganization(SharedBase, StatusMixin):
    """Model for managing user-organization relationships."""
    __tablename__ = "user_management_user_organizations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    role = Column(String, nullable=False)  # admin, member, etc.

    # Relationships
    user = relationship("app.models.core.user.User", back_populates="organizations")
    organization = relationship("Organization", back_populates="user_organizations")

    def dict(self):
        """Convert model to dictionary."""
        return {
            **super().dict(),
            "user_id": self.user_id,
            "organization_id": self.organization_id,
            "role": self.role,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class UserSession(SharedBase, StatusMixin):
    """Model for tracking user sessions and activity."""
    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_token = Column(String, nullable=False)
    ip_address = Column(String)
    user_agent = Column(String)
    last_activity = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)

    # Relationships
    user = relationship("app.models.core.user.User", back_populates="user_sessions")

    def dict(self):
        """Convert model to dictionary."""
        return {
            **super().dict(),
            "user_id": self.user_id,
            "session_token": self.session_token,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        } 