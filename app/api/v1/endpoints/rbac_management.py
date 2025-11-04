"""
Enhanced RBAC Management API Endpoints

This module provides enhanced role-based access control endpoints
specifically for the user system in Phase 2.
"""

from typing import List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.core.auth import get_current_user
from app.core.security import (
    require_permission, 
    require_any_permission,
    Permission,
    UserRole
)
from app.models.core.user import User
from app.services.access_control_service import AccessControlService
from app.dashboard.services.access_control_service import AccessControlService as DashboardAccessControlService

router = APIRouter(prefix="/rbac", tags=["rbac-management"])


# Pydantic models for RBAC management
class RoleCreate(BaseModel):
    name: str
    description: Optional[str] = None
    permissions: List[str] = []
    is_system: bool = False
    is_template: bool = False


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    permissions: Optional[List[str]] = None
    is_active: Optional[bool] = None


class RoleResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    permissions: List[str] = []
    is_system: bool
    is_template: bool
    is_active: bool
    created_at: str
    updated_at: str


class PermissionCreate(BaseModel):
    name: str
    description: Optional[str] = None
    resource_type: str
    action: str
    scope: Optional[str] = None


class PermissionResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    resource_type: str
    action: str
    scope: Optional[str] = None
    is_active: bool
    created_at: str
    updated_at: str


class RoleAssignmentCreate(BaseModel):
    user_id: int
    role_id: str
    expires_at: Optional[str] = None
    metadata: Optional[Dict] = None


class RoleAssignmentResponse(BaseModel):
    id: str
    user_id: int
    role_id: str
    expires_at: Optional[str] = None
    metadata: Optional[Dict] = None
    is_active: bool
    created_at: str
    updated_at: str


class PermissionCheckRequest(BaseModel):
    user_id: int
    permission: str
    resource_id: Optional[str] = None


class PermissionCheckResponse(BaseModel):
    has_permission: bool
    user_id: int
    permission: str
    resource_id: Optional[str] = None


class UserPermissionsResponse(BaseModel):
    user_id: int
    roles: List[str] = []
    permissions: List[str] = []
    effective_permissions: Dict[str, List[str]] = {}


# Role Management Endpoints
@router.post("/roles", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    role: RoleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.EDIT_USERS))
):
    """Create a new role. Requires user management permission."""
    try:
        service = DashboardAccessControlService(db)
        return await service.create_role(role)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create role: {str(e)}"
        )


@router.get("/roles", response_model=List[RoleResponse])
async def list_roles(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.VIEW_USERS))
):
    """List all roles. Requires user management permission."""
    try:
        service = DashboardAccessControlService(db)
        return await service.list_roles()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list roles: {str(e)}"
        )


@router.get("/roles/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.VIEW_USERS))
):
    """Get a role by ID. Requires user management permission."""
    try:
        service = DashboardAccessControlService(db)
        role = await service.get_role(role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        return role
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get role: {str(e)}"
        )


@router.patch("/roles/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: str,
    role_update: RoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.EDIT_USERS))
):
    """Update a role. Requires user management permission."""
    try:
        service = DashboardAccessControlService(db)
        updated_role = await service.update_role(role_id, role_update)
        if not updated_role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        return updated_role
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update role: {str(e)}"
        )


# Permission Management Endpoints
@router.post("/permissions", response_model=PermissionResponse, status_code=status.HTTP_201_CREATED)
async def create_permission(
    permission: PermissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.EDIT_USERS))
):
    """Create a new permission. Requires user management permission."""
    try:
        service = DashboardAccessControlService(db)
        return await service.create_permission(permission)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create permission: {str(e)}"
        )


@router.get("/permissions", response_model=List[PermissionResponse])
async def list_permissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.VIEW_USERS))
):
    """List all permissions. Requires user management permission."""
    try:
        service = DashboardAccessControlService(db)
        permissions = await service.list_permissions()
        # Convert model objects to response schema
        result = []
        for perm in permissions:
            result.append(PermissionResponse(
                id=str(perm.id),
                name=perm.name or "",
                description=perm.description,
                resource_type=perm.resource_type or "",
                action=perm.action or "",
                scope=perm.scope,
                is_active=bool(perm.is_active) if perm.is_active is not None else True,
                created_at=perm.created_at.isoformat() if perm.created_at else "",
                updated_at=perm.updated_at.isoformat() if perm.updated_at else ""
            ))
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list permissions: {str(e)}"
        )


# Role Assignment Endpoints
@router.post("/role-assignments", response_model=RoleAssignmentResponse, status_code=status.HTTP_201_CREATED)
async def assign_role_to_user(
    assignment: RoleAssignmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.EDIT_USERS))
):
    """Assign a role to a user. Requires user management permission."""
    try:
        service = DashboardAccessControlService(db)
        return await service.assign_role(assignment)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to assign role: {str(e)}"
        )


@router.get("/users/{user_id}/permissions", response_model=UserPermissionsResponse)
async def get_user_permissions(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.VIEW_USERS))
):
    """Get all permissions for a user. Requires user management permission."""
    try:
        service = DashboardAccessControlService(db)
        effective_permissions = await service.get_effective_permissions(str(user_id))
        user_roles = await service.get_user_roles(str(user_id))
        
        # Extract role names and permissions
        roles = [role.name for role in user_roles]
        permissions = []
        for resource_action, scopes in effective_permissions.items():
            permissions.append(resource_action)
        
        return UserPermissionsResponse(
            user_id=user_id,
            roles=roles,
            permissions=permissions,
            effective_permissions=effective_permissions
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user permissions: {str(e)}"
        )


# Permission Check Endpoints
@router.post("/check-permission", response_model=PermissionCheckResponse)
async def check_user_permission(
    request: PermissionCheckRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.VIEW_USERS))
):
    """Check if a user has a specific permission. Requires user management permission."""
    try:
        service = DashboardAccessControlService(db)
        has_perm = await service.check_permission(
            str(request.user_id),
            request.permission,
            request.resource_id
        )
        
        return PermissionCheckResponse(
            has_permission=has_perm,
            user_id=request.user_id,
            permission=request.permission,
            resource_id=request.resource_id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check permission: {str(e)}"
        )


# System Role Templates
@router.get("/role-templates", response_model=List[RoleResponse])
async def get_role_templates(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.VIEW_USERS))
):
    """Get system role templates. Requires user management permission."""
    try:
        service = DashboardAccessControlService(db)
        return await service.list_role_templates()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get role templates: {str(e)}"
        )


# Bulk Operations
@router.post("/bulk-assign-roles", response_model=List[RoleAssignmentResponse])
async def bulk_assign_roles(
    assignments: List[RoleAssignmentCreate],
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.EDIT_USERS))
):
    """Bulk assign roles to users. Requires user management permission."""
    try:
        service = DashboardAccessControlService(db)
        results = []
        for assignment in assignments:
            result = await service.assign_role(assignment)
            results.append(result)
        return results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to bulk assign roles: {str(e)}"
        ) 