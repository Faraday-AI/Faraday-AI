"""
Permission Management Schemas

This module defines Pydantic schemas for permission management.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class PermissionAction(str, Enum):
    """Permission actions."""
    READ = "read"
    WRITE = "write"
    CREATE = "create"
    DELETE = "delete"
    EXECUTE = "execute"
    ASSIGN = "assign"
    MANAGE = "manage"
    PUBLISH = "publish"
    EXPORT = "export"
    SHARE = "share"
    ADMIN = "admin"


class ResourceType(str, Enum):
    """Resource types."""
    USER = "user"
    ROLE = "role"
    PERMISSION = "permission"
    ORGANIZATION = "organization"
    DASHBOARD = "dashboard"
    ANALYTICS = "analytics"
    CONTENT = "content"
    SYSTEM = "system"


class PermissionBase(BaseModel):
    """Base permission schema."""
    name: str = Field(..., description="Permission name")
    description: Optional[str] = Field(None, description="Permission description")
    resource_type: str = Field(..., description="Resource type")
    action: str = Field(..., description="Permission action")


class PermissionCreate(PermissionBase):
    """Schema for creating a permission."""
    pass


class PermissionUpdate(BaseModel):
    """Schema for updating a permission."""
    name: Optional[str] = Field(None, description="Permission name")
    description: Optional[str] = Field(None, description="Permission description")
    resource_type: Optional[str] = Field(None, description="Resource type")
    action: Optional[str] = Field(None, description="Permission action")


class PermissionResponse(PermissionBase):
    """Schema for permission responses."""
    id: int
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PermissionCheck(BaseModel):
    """Schema for permission checking."""
    user_id: int = Field(..., description="User ID")
    permission_name: str = Field(..., description="Permission name to check")


class ResourcePermission(BaseModel):
    """Schema for resource-based permissions."""
    name: str = Field(..., description="Permission name")
    resource_type: str = Field(..., description="Resource type")
    action: str = Field(..., description="Permission action")
    description: str = Field(..., description="Permission description")


class PermissionAssignment(BaseModel):
    """Schema for permission assignment."""
    role_id: int = Field(..., description="Role ID")
    permission_id: int = Field(..., description="Permission ID")


class PermissionRemoval(BaseModel):
    """Schema for permission removal."""
    role_id: int = Field(..., description="Role ID")
    permission_id: int = Field(..., description="Permission ID")


class BulkPermissionCheck(BaseModel):
    """Schema for bulk permission checking."""
    user_id: int = Field(..., description="User ID")
    permissions: List[str] = Field(..., description="List of permission names to check")


class PermissionSummary(BaseModel):
    """Schema for permission summary."""
    id: int
    name: str
    resource_type: str
    action: str
    role_count: int
    description: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserPermissionSummary(BaseModel):
    """Schema for user permission summary."""
    user_id: int
    total_permissions: int
    permissions: List[str]
    permissions_by_resource: Dict[str, List[str]]
    primary_role: str
    assigned_roles: List[str]
    is_superuser: bool
    
    class Config:
        from_attributes = True


class RolePermissionSummary(BaseModel):
    """Schema for role permission summary."""
    role_id: int
    role_name: str
    total_permissions: int
    permissions: List[str]
    permissions_by_resource: Dict[str, List[str]]
    user_count: int
    
    class Config:
        from_attributes = True


class PermissionSearch(BaseModel):
    """Schema for permission search."""
    query: Optional[str] = Field(None, description="Search query")
    resource_type: Optional[str] = Field(None, description="Filter by resource type")
    action: Optional[str] = Field(None, description="Filter by action")
    limit: int = Field(10, description="Maximum number of results")


class PermissionFilter(BaseModel):
    """Schema for permission filtering."""
    name_contains: Optional[str] = Field(None, description="Permission name contains")
    resource_type: Optional[str] = Field(None, description="Filter by resource type")
    action: Optional[str] = Field(None, description="Filter by action")
    has_roles: Optional[List[str]] = Field(None, description="Permissions assigned to specific roles")
    role_count_min: Optional[int] = Field(None, description="Minimum role count")
    role_count_max: Optional[int] = Field(None, description="Maximum role count")


class PermissionAudit(BaseModel):
    """Schema for permission audit information."""
    permission_id: int
    action: str  # created, updated, deleted, assigned, removed
    user_id: int
    timestamp: datetime
    details: Dict[str, Any]
    
    class Config:
        from_attributes = True


class PermissionTemplate(BaseModel):
    """Schema for permission templates."""
    name: str = Field(..., description="Template name")
    description: Optional[str] = Field(None, description="Template description")
    resource_type: str = Field(..., description="Resource type")
    actions: List[str] = Field(..., description="List of actions")
    is_system: bool = Field(False, description="Whether this is a system template")


class PermissionTemplateCreate(BaseModel):
    """Schema for creating permission templates."""
    name: str = Field(..., description="Template name")
    description: Optional[str] = Field(None, description="Template description")
    resource_type: str = Field(..., description="Resource type")
    actions: List[str] = Field(..., description="List of actions")


class PermissionTemplateUpdate(BaseModel):
    """Schema for updating permission templates."""
    name: Optional[str] = Field(None, description="Template name")
    description: Optional[str] = Field(None, description="Template description")
    resource_type: Optional[str] = Field(None, description="Resource type")
    actions: Optional[List[str]] = Field(None, description="List of actions")


class PermissionTemplateResponse(BaseModel):
    """Schema for permission template responses."""
    id: int
    name: str
    description: Optional[str] = None
    resource_type: str
    actions: List[str]
    is_system: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PermissionImport(BaseModel):
    """Schema for permission import."""
    permissions: List[PermissionCreate] = Field(..., description="List of permissions to import")
    overwrite_existing: bool = Field(False, description="Whether to overwrite existing permissions")


class PermissionExport(BaseModel):
    """Schema for permission export."""
    permissions: List[PermissionResponse] = Field(..., description="List of exported permissions")
    exported_at: datetime
    version: str = Field("1.0", description="Export format version")


class PermissionStatistics(BaseModel):
    """Schema for permission statistics."""
    total_permissions: int
    permissions_by_resource: Dict[str, int]
    permissions_by_action: Dict[str, int]
    most_used_permissions: List[str]
    least_used_permissions: List[str]
    average_roles_per_permission: float
    permissions_without_roles: int
    system_permissions: int
    custom_permissions: int


class ResourcePermissionMatrix(BaseModel):
    """Schema for resource permission matrix."""
    resource_type: str
    available_actions: List[str]
    permissions: List[ResourcePermission]
    description: str = Field(..., description="Resource type description")


class PermissionHierarchy(BaseModel):
    """Schema for permission hierarchy."""
    resource_type: str
    parent_permissions: List[str]
    child_permissions: List[str]
    inheritance_rules: Dict[str, List[str]] 