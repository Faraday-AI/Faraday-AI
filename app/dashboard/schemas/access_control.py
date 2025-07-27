from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, List, Union
from datetime import datetime
from enum import Enum
from pydantic import ConfigDict

class ResourceType(str, Enum):
    """Enumeration of resource types."""
    USER = "user"
    ROLE = "role"
    PERMISSION = "permission"
    TOOL = "tool"
    AVATAR = "avatar"
    SETTING = "setting"
    API = "api"
    SYSTEM = "system"

class ActionType(str, Enum):
    """Enumeration of action types."""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    EXECUTE = "execute"
    MANAGE = "manage"
    ADMINISTER = "administer"

class PermissionBase(BaseModel):
    """Base schema for permissions."""
    name: str
    description: Optional[str] = None
    resource_type: ResourceType
    action: ActionType
    scope: Optional[str] = None
    permission_type: str = "system"

class RoleBase(BaseModel):
    """Base schema for roles."""
    name: str
    description: Optional[str] = None
    is_system: bool = False
    is_template: bool = False

class RoleAssignmentBase(BaseModel):
    """Base schema for role assignments."""
    user_id: Union[str, int]
    role_id: Union[str, int]
    assigned_by: str
    expires_at: Optional[datetime] = None

class PermissionOverrideBase(BaseModel):
    """Base schema for permission overrides."""
    user_id: Union[str, int]
    permission_id: Union[str, int]
    is_allowed: bool
    reason: Optional[str] = None
    expires_at: Optional[datetime] = None

class RoleHierarchyBase(BaseModel):
    """Base schema for role hierarchy."""
    parent_role_id: Union[str, int]
    child_role_id: Union[str, int]
    is_active: bool = True

class RoleTemplateBase(BaseModel):
    """Base schema for role templates."""
    name: str
    description: Optional[str] = None
    is_system: bool = False
    permissions: List[str]

class PermissionCreate(PermissionBase):
    """Schema for creating a permission."""
    pass

class RoleCreate(RoleBase):
    """Schema for creating a role."""
    pass

class RoleAssignmentCreate(RoleAssignmentBase):
    """Schema for creating a role assignment."""
    pass

class PermissionOverrideCreate(PermissionOverrideBase):
    """Schema for creating a permission override."""
    pass

class PermissionOverrideCreateRequest(BaseModel):
    """Schema for creating a permission override request (without permission_id)."""
    user_id: str
    is_allowed: bool
    reason: Optional[str] = None
    expires_at: Optional[datetime] = None

class RoleHierarchyCreate(RoleHierarchyBase):
    """Schema for creating a role hierarchy."""
    pass

class RoleTemplateCreate(RoleTemplateBase):
    """Schema for creating a role template."""
    pass

class PermissionUpdate(BaseModel):
    """Schema for updating a permission."""
    name: Optional[str] = None
    description: Optional[str] = None
    resource_type: Optional[ResourceType] = None
    action: Optional[ActionType] = None
    scope: Optional[str] = None
    is_active: Optional[bool] = None

class RoleUpdate(BaseModel):
    """Schema for updating a role."""
    name: Optional[str] = None
    description: Optional[str] = None
    is_system: Optional[bool] = None
    is_template: Optional[bool] = None
    is_active: Optional[bool] = None

class RoleAssignmentUpdate(BaseModel):
    """Schema for updating a role assignment."""
    is_active: Optional[bool] = None
    expires_at: Optional[datetime] = None

class PermissionOverrideUpdate(BaseModel):
    """Schema for updating a permission override."""
    is_allowed: Optional[bool] = None
    reason: Optional[str] = None
    is_active: Optional[bool] = None
    expires_at: Optional[datetime] = None

class RoleHierarchyUpdate(BaseModel):
    """Schema for updating a role hierarchy."""
    is_active: Optional[bool] = None

class RoleTemplateUpdate(BaseModel):
    """Schema for updating a role template."""
    name: Optional[str] = None
    description: Optional[str] = None
    is_system: Optional[bool] = None
    is_active: Optional[bool] = None
    permissions: Optional[List[str]] = None

class PermissionResponse(PermissionBase):
    """Schema for permission response."""
    id: Union[str, int]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class RoleResponse(RoleBase):
    """Schema for role response."""
    id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    permissions: List[PermissionResponse]

    class Config:
        from_attributes = True

class RoleAssignmentResponse(RoleAssignmentBase):
    """Schema for role assignment response."""
    id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    role: RoleResponse

    class Config:
        from_attributes = True

class PermissionOverrideResponse(PermissionOverrideBase):
    """Schema for permission override response."""
    id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    permission: PermissionResponse

    model_config = ConfigDict(from_attributes=True)

class RoleHierarchyResponse(RoleHierarchyBase):
    """Schema for role hierarchy response."""
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class RoleTemplateResponse(RoleTemplateBase):
    """Schema for role template response."""
    id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    permissions: List[PermissionResponse]

    class Config:
        from_attributes = True

class BulkPermissionCheck(BaseModel):
    """Schema for bulk permission check."""
    user_id: str
    resource_type: ResourceType
    action: ActionType
    resource_id: Optional[str] = None

class PermissionCheckRequest(BaseModel):
    """Schema for permission check request."""
    user_id: str
    resource_type: ResourceType
    action: ActionType
    resource_id: Optional[str] = None

class PermissionCheckResponse(BaseModel):
    """Schema for permission check response."""
    has_permission: bool
    reason: Optional[str] = None

class BulkPermissionCheckRequest(BaseModel):
    """Schema for bulk permission check request."""
    checks: List[BulkPermissionCheck]

class BulkPermissionCheckResponse(BaseModel):
    """Schema for bulk permission check response."""
    results: List[PermissionCheckResponse] 