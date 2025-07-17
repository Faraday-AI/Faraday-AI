"""
Access Control Management Models

This module defines the database models for role-based access control,
permissions, and security in the Faraday AI system.
"""

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Table, Integer, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base
from app.models.core.base import BaseModel, StatusMixin, MetadataMixin, TimestampedMixin
from enum import Enum

class ResourceType(str, Enum):
    """Enumeration of resource types for access control."""
    USER = "user"
    ROLE = "role"
    PERMISSION = "permission"
    TOOL = "tool"
    AVATAR = "avatar"
    SETTING = "setting"
    API = "api"
    SYSTEM = "system"

class ActionType(str, Enum):
    """Enumeration of action types for access control."""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    EXECUTE = "execute"
    MANAGE = "manage"
    ADMINISTER = "administer"

# Association table for user-role many-to-many relationship
access_control_user_roles = Table(
    "access_control_user_roles",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("role_id", Integer, ForeignKey("access_control_roles.id"), primary_key=True),
    Column("created_at", DateTime, default=func.now()),
    Column("updated_at", DateTime, default=func.now(), onupdate=func.now()),
    extend_existing=True
)

class AccessControlRole(BaseModel, TimestampedMixin, StatusMixin, MetadataMixin):
    """Model for access control roles."""
    __tablename__ = "access_control_roles"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    permissions = Column(JSON, nullable=True)
    role_metadata = Column(JSON, nullable=True)

    # Relationships
    users = relationship("User", secondary="access_control_user_roles", back_populates="access_control_roles", overlaps="user_roles")
    user_roles = relationship("UserRole", back_populates="role", overlaps="access_control_roles,users")
    permissions = relationship("AccessControlPermission", secondary="access_control_role_permissions", back_populates="roles", overlaps="role_permissions")
    role_permissions = relationship("RolePermission", back_populates="role", overlaps="permissions")
    parent_roles = relationship(
        "AccessControlRole", 
        secondary="role_hierarchy", 
        primaryjoin="AccessControlRole.id == RoleHierarchy.child_role_id",
        secondaryjoin="AccessControlRole.id == RoleHierarchy.parent_role_id",
        back_populates="child_roles"
    )
    child_roles = relationship(
        "AccessControlRole", 
        secondary="role_hierarchy", 
        primaryjoin="AccessControlRole.id == RoleHierarchy.parent_role_id",
        secondaryjoin="AccessControlRole.id == RoleHierarchy.child_role_id",
        back_populates="parent_roles"
    )

class AccessControlPermission(BaseModel, TimestampedMixin, StatusMixin, MetadataMixin):
    """Model for access control permissions."""
    __tablename__ = "access_control_permissions"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    permission_type = Column(String, nullable=False)
    permission_metadata = Column(JSON, nullable=True)

    # Relationships
    roles = relationship("AccessControlRole", secondary="access_control_role_permissions", back_populates="permissions", overlaps="role_permissions")
    role_permissions = relationship("RolePermission", back_populates="permission", overlaps="permissions,roles")
    overrides = relationship("app.models.security.preferences.security_preferences_management.PermissionOverride", back_populates="permission")

class RoleHierarchy(BaseModel, TimestampedMixin, StatusMixin, MetadataMixin):
    """Model for role hierarchy."""
    __tablename__ = "role_hierarchy"
    __table_args__ = {'extend_existing': True}

    parent_role_id = Column(Integer, ForeignKey("access_control_roles.id"), primary_key=True)
    child_role_id = Column(Integer, ForeignKey("access_control_roles.id"), primary_key=True)
    hierarchy_metadata = Column(JSON, nullable=True)

    # Relationships
    parent_role = relationship("AccessControlRole", foreign_keys=[parent_role_id], overlaps="child_roles,parent_roles")
    child_role = relationship("AccessControlRole", foreign_keys=[child_role_id], overlaps="child_roles,parent_roles")

class UserRole(BaseModel, TimestampedMixin, StatusMixin, MetadataMixin):
    """Model for user roles."""
    __tablename__ = "access_control_user_roles"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role_id = Column(Integer, ForeignKey("access_control_roles.id"), nullable=False)
    user_role_metadata = Column(JSON, nullable=True)

    # Relationships
    user = relationship("User", back_populates="user_roles", overlaps="access_control_roles,users")
    role = relationship("AccessControlRole", back_populates="user_roles", overlaps="access_control_roles,users")

class RolePermission(BaseModel, TimestampedMixin, StatusMixin, MetadataMixin):
    """Model for role permissions."""
    __tablename__ = "access_control_role_permissions"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("access_control_roles.id"), nullable=False)
    permission_id = Column(Integer, ForeignKey("access_control_permissions.id"), nullable=False)
    role_permission_metadata = Column(JSON, nullable=True)

    # Relationships
    role = relationship("AccessControlRole", back_populates="role_permissions", overlaps="permissions,roles")
    permission = relationship("AccessControlPermission", back_populates="role_permissions", overlaps="permissions,roles")

class RoleTemplate(BaseModel, StatusMixin, MetadataMixin):
    """Model for role templates."""
    __tablename__ = "role_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    description = Column(String, nullable=True)
    is_system = Column(Boolean, default=False)

    # Relationships
    # Note: RoleTemplate doesn't have a direct many-to-many relationship with permissions
    # through access_control_role_permissions since that table only links roles and permissions
    # through access_control_role_permissions table. 