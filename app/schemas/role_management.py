"""
Role Management Schemas

This module defines Pydantic schemas for role management.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

from app.models.user_management.user.user_management import UserRole


class RoleLevel(str, Enum):
    """Role hierarchy levels."""
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    TEACHER = "teacher"
    STAFF = "staff"
    STUDENT = "student"
    PARENT = "parent"


class RoleBase(BaseModel):
    """Base role schema."""
    name: str = Field(..., description="Role name")
    description: Optional[str] = Field(None, description="Role description")
    is_custom: bool = Field(False, description="Whether this is a custom role")


class RoleCreate(RoleBase):
    """Schema for creating a role."""
    parent_role: Optional[str] = Field(None, description="Parent role name")


class RoleUpdate(BaseModel):
    """Schema for updating a role."""
    name: Optional[str] = Field(None, description="Role name")
    description: Optional[str] = Field(None, description="Role description")
    parent_role: Optional[str] = Field(None, description="Parent role name")


class RoleResponse(RoleBase):
    """Schema for role responses."""
    id: int
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class RoleAssignment(BaseModel):
    """Schema for role assignment."""
    user_id: int = Field(..., description="User ID")
    role_name: str = Field(..., description="Role name to assign")


class RoleRemoval(BaseModel):
    """Schema for role removal."""
    user_id: int = Field(..., description="User ID")
    role_name: str = Field(..., description="Role name to remove")


class RoleHierarchy(BaseModel):
    """Schema for role hierarchy information."""
    role_name: str
    level: int
    user_count: int
    permissions: List[str]
    description: Optional[str] = None
    is_custom: bool = False


class RoleSummary(BaseModel):
    """Schema for role summary."""
    id: int
    name: str
    description: Optional[str] = None
    user_count: int
    permission_count: int
    is_custom: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserRoleSummary(BaseModel):
    """Schema for user role summary."""
    user_id: int
    primary_role: str
    assigned_roles: List[str]
    role_count: int
    is_superuser: bool
    
    class Config:
        from_attributes = True


class BulkRoleAssignment(BaseModel):
    """Schema for bulk role assignment."""
    assignments: List[RoleAssignment] = Field(..., description="List of role assignments")
    overwrite_existing: bool = Field(False, description="Whether to overwrite existing roles")


class RolePermissionAssignment(BaseModel):
    """Schema for assigning permissions to roles."""
    role_id: int = Field(..., description="Role ID")
    permission_ids: List[int] = Field(..., description="List of permission IDs")


class RoleSearch(BaseModel):
    """Schema for role search."""
    query: Optional[str] = Field(None, description="Search query")
    is_custom: Optional[bool] = Field(None, description="Filter by custom roles")
    status: Optional[str] = Field(None, description="Filter by status")
    limit: int = Field(10, description="Maximum number of results")


class RoleFilter(BaseModel):
    """Schema for role filtering."""
    name_contains: Optional[str] = Field(None, description="Role name contains")
    is_custom: Optional[bool] = Field(None, description="Custom roles only")
    has_permissions: Optional[List[str]] = Field(None, description="Roles with specific permissions")
    user_count_min: Optional[int] = Field(None, description="Minimum user count")
    user_count_max: Optional[int] = Field(None, description="Maximum user count")


class RoleAudit(BaseModel):
    """Schema for role audit information."""
    role_id: int
    action: str  # created, updated, deleted, assigned, removed
    user_id: int
    timestamp: datetime
    details: Dict[str, Any]
    
    class Config:
        from_attributes = True


class RoleTemplate(BaseModel):
    """Schema for role templates."""
    name: str = Field(..., description="Template name")
    description: Optional[str] = Field(None, description="Template description")
    permissions: List[str] = Field(..., description="List of permission names")
    is_system: bool = Field(False, description="Whether this is a system template")


class RoleTemplateCreate(BaseModel):
    """Schema for creating role templates."""
    name: str = Field(..., description="Template name")
    description: Optional[str] = Field(None, description="Template description")
    permissions: List[str] = Field(..., description="List of permission names")


class RoleTemplateUpdate(BaseModel):
    """Schema for updating role templates."""
    name: Optional[str] = Field(None, description="Template name")
    description: Optional[str] = Field(None, description="Template description")
    permissions: Optional[List[str]] = Field(None, description="List of permission names")


class RoleTemplateResponse(BaseModel):
    """Schema for role template responses."""
    id: int
    name: str
    description: Optional[str] = None
    permissions: List[str]
    is_system: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class RoleImport(BaseModel):
    """Schema for role import."""
    roles: List[RoleCreate] = Field(..., description="List of roles to import")
    overwrite_existing: bool = Field(False, description="Whether to overwrite existing roles")


class RoleExport(BaseModel):
    """Schema for role export."""
    roles: List[RoleResponse] = Field(..., description="List of exported roles")
    exported_at: datetime
    version: str = Field("1.0", description="Export format version")


class RoleStatistics(BaseModel):
    """Schema for role statistics."""
    total_roles: int
    custom_roles: int
    system_roles: int
    active_roles: int
    inactive_roles: int
    roles_with_users: int
    roles_without_users: int
    average_users_per_role: float
    most_used_role: Optional[str] = None
    least_used_role: Optional[str] = None 