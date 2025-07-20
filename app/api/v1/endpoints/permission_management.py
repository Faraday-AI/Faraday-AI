"""
Permission Management API Endpoints

This module provides API endpoints for permission management.
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.core.user import User
from app.services.user.permission_management_service import PermissionManagementService, get_permission_management_service
from app.schemas.permission_management import (
    PermissionCreate,
    PermissionUpdate,
    PermissionResponse,
    PermissionCheck,
    ResourcePermission,
    PermissionAssignment,
    PermissionRemoval,
    BulkPermissionCheck,
    PermissionSummary,
    UserPermissionSummary,
    RolePermissionSummary,
    PermissionSearch,
    PermissionFilter,
    ResourcePermissionMatrix
)

router = APIRouter()


@router.get("/permissions", response_model=List[PermissionResponse])
async def get_all_permissions(
    current_user: User = Depends(get_current_user),
    permission_service: PermissionManagementService = Depends(get_permission_management_service)
):
    """Get all permissions."""
    # Check if user has permission to view permissions
    if not permission_service.check_user_resource_permission(current_user.id, "permission", "read"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    return permission_service.get_all_permissions()


@router.get("/permissions/resource/{resource_type}", response_model=List[PermissionResponse])
async def get_permissions_by_resource_type(
    resource_type: str,
    current_user: User = Depends(get_current_user),
    permission_service: PermissionManagementService = Depends(get_permission_management_service)
):
    """Get permissions by resource type."""
    return permission_service.get_permissions_by_resource_type(resource_type)


@router.get("/permissions/action/{action}", response_model=List[PermissionResponse])
async def get_permissions_by_action(
    action: str,
    current_user: User = Depends(get_current_user),
    permission_service: PermissionManagementService = Depends(get_permission_management_service)
):
    """Get permissions by action."""
    return permission_service.get_permissions_by_action(action)


@router.get("/permissions/{permission_id}", response_model=PermissionResponse)
async def get_permission_by_id(
    permission_id: int,
    current_user: User = Depends(get_current_user),
    permission_service: PermissionManagementService = Depends(get_permission_management_service)
):
    """Get permission by ID."""
    permission = permission_service.get_permission_by_id(permission_id)
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    
    return permission


@router.post("/permissions", response_model=PermissionResponse)
async def create_permission(
    permission_data: PermissionCreate,
    current_user: User = Depends(get_current_user),
    permission_service: PermissionManagementService = Depends(get_permission_management_service)
):
    """Create a new permission."""
    # Check if user has permission to create permissions
    if not permission_service.check_user_resource_permission(current_user.id, "permission", "create"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    return permission_service.create_permission(permission_data)


@router.put("/permissions/{permission_id}", response_model=PermissionResponse)
async def update_permission(
    permission_id: int,
    permission_data: PermissionUpdate,
    current_user: User = Depends(get_current_user),
    permission_service: PermissionManagementService = Depends(get_permission_management_service)
):
    """Update permission."""
    # Check if user has permission to update permissions
    if not permission_service.check_user_resource_permission(current_user.id, "permission", "write"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    return permission_service.update_permission(permission_id, permission_data)


@router.delete("/permissions/{permission_id}")
async def delete_permission(
    permission_id: int,
    current_user: User = Depends(get_current_user),
    permission_service: PermissionManagementService = Depends(get_permission_management_service)
):
    """Delete permission."""
    # Check if user has permission to delete permissions
    if not permission_service.check_user_resource_permission(current_user.id, "permission", "delete"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    success = permission_service.delete_permission(permission_id)
    return {"message": "Permission deleted successfully"}


@router.post("/permissions/assign")
async def assign_permission_to_role(
    assignment: PermissionAssignment,
    current_user: User = Depends(get_current_user),
    permission_service: PermissionManagementService = Depends(get_permission_management_service)
):
    """Assign permission to role."""
    # Check if user has permission to assign permissions
    if not permission_service.check_user_resource_permission(current_user.id, "permission", "assign"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    success = permission_service.assign_permission_to_role(assignment.role_id, assignment.permission_id)
    return {"message": "Permission assigned successfully"}


@router.post("/permissions/remove")
async def remove_permission_from_role(
    removal: PermissionRemoval,
    current_user: User = Depends(get_current_user),
    permission_service: PermissionManagementService = Depends(get_permission_management_service)
):
    """Remove permission from role."""
    # Check if user has permission to remove permissions
    if not permission_service.check_user_resource_permission(current_user.id, "permission", "assign"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    success = permission_service.remove_permission_from_role(removal.role_id, removal.permission_id)
    return {"message": "Permission removed successfully"}


@router.get("/roles/{role_id}/permissions", response_model=List[PermissionResponse])
async def get_role_permissions(
    role_id: int,
    current_user: User = Depends(get_current_user),
    permission_service: PermissionManagementService = Depends(get_permission_management_service)
):
    """Get all permissions assigned to a role."""
    return permission_service.get_role_permissions(role_id)


@router.get("/users/{user_id}/permissions", response_model=UserPermissionSummary)
async def get_user_permissions(
    user_id: int,
    current_user: User = Depends(get_current_user),
    permission_service: PermissionManagementService = Depends(get_permission_management_service)
):
    """Get all permissions for a user."""
    # Users can view their own permissions, admins can view any user's permissions
    if user_id != current_user.id and not permission_service.check_user_resource_permission(current_user.id, "user", "read"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    return permission_service.get_permission_summary(user_id)


@router.post("/permissions/check")
async def check_user_permission(
    check: PermissionCheck,
    current_user: User = Depends(get_current_user),
    permission_service: PermissionManagementService = Depends(get_permission_management_service)
):
    """Check if user has a specific permission."""
    has_permission = permission_service.check_user_permission(check.user_id, check.permission_name)
    return {
        "user_id": check.user_id,
        "permission_name": check.permission_name,
        "has_permission": has_permission
    }


@router.post("/permissions/check-resource")
async def check_user_resource_permission(
    resource_type: str,
    action: str,
    current_user: User = Depends(get_current_user),
    permission_service: PermissionManagementService = Depends(get_permission_management_service)
):
    """Check if current user has permission for a specific resource and action."""
    has_permission = permission_service.check_user_resource_permission(current_user.id, resource_type, action)
    return {
        "user_id": current_user.id,
        "resource_type": resource_type,
        "action": action,
        "has_permission": has_permission
    }


@router.post("/permissions/bulk-check")
async def bulk_check_permissions(
    check: BulkPermissionCheck,
    current_user: User = Depends(get_current_user),
    permission_service: PermissionManagementService = Depends(get_permission_management_service)
):
    """Bulk check multiple permissions for a user."""
    results = permission_service.bulk_check_permissions(check.user_id, check.permissions)
    return {
        "user_id": check.user_id,
        "permissions": results
    }


@router.get("/permissions/available", response_model=List[PermissionResponse])
async def get_available_permissions(
    current_user: User = Depends(get_current_user),
    permission_service: PermissionManagementService = Depends(get_permission_management_service)
):
    """Get permissions available for assignment by current user."""
    return permission_service.get_available_permissions(current_user.id)


@router.get("/permissions/resource-matrix/{resource_type}", response_model=ResourcePermissionMatrix)
async def get_resource_permission_matrix(
    resource_type: str,
    current_user: User = Depends(get_current_user),
    permission_service: PermissionManagementService = Depends(get_permission_management_service)
):
    """Get all available permissions for a resource type."""
    permissions = permission_service.get_resource_permissions(resource_type)
    return ResourcePermissionMatrix(
        resource_type=resource_type,
        available_actions=permission_service.resource_types.get(resource_type, []),
        permissions=permissions,
        description=f"Permissions for {resource_type} resources"
    )


@router.post("/permissions/search", response_model=List[PermissionResponse])
async def search_permissions(
    search: PermissionSearch,
    current_user: User = Depends(get_current_user),
    permission_service: PermissionManagementService = Depends(get_permission_management_service)
):
    """Search permissions."""
    # Check if user has permission to view permissions
    if not permission_service.check_user_resource_permission(current_user.id, "permission", "read"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    permissions = permission_service.get_all_permissions()
    
    # Apply filters
    if search.query:
        permissions = [perm for perm in permissions if search.query.lower() in perm.name.lower()]
    
    if search.resource_type:
        permissions = [perm for perm in permissions if perm.resource_type == search.resource_type]
    
    if search.action:
        permissions = [perm for perm in permissions if perm.action == search.action]
    
    return permissions[:search.limit]


@router.post("/permissions/filter", response_model=List[PermissionSummary])
async def filter_permissions(
    filter_data: PermissionFilter,
    current_user: User = Depends(get_current_user),
    permission_service: PermissionManagementService = Depends(get_permission_management_service)
):
    """Filter permissions."""
    # Check if user has permission to view permissions
    if not permission_service.check_user_resource_permission(current_user.id, "permission", "read"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    permissions = permission_service.get_all_permissions()
    
    # Apply filters
    if filter_data.name_contains:
        permissions = [perm for perm in permissions if filter_data.name_contains.lower() in perm.name.lower()]
    
    if filter_data.resource_type:
        permissions = [perm for perm in permissions if perm.resource_type == filter_data.resource_type]
    
    if filter_data.action:
        permissions = [perm for perm in permissions if perm.action == filter_data.action]
    
    if filter_data.has_roles:
        permissions = [perm for perm in permissions if any(role.name in filter_data.has_roles for role in perm.roles)]
    
    if filter_data.role_count_min is not None:
        permissions = [perm for perm in permissions if len(perm.roles) >= filter_data.role_count_min]
    
    if filter_data.role_count_max is not None:
        permissions = [perm for perm in permissions if len(perm.roles) <= filter_data.role_count_max]
    
    return [
        PermissionSummary(
            id=perm.id,
            name=perm.name,
            resource_type=perm.resource_type,
            action=perm.action,
            role_count=len(perm.roles),
            description=perm.description,
            created_at=perm.created_at
        )
        for perm in permissions
    ]


@router.get("/permissions/check-current")
async def check_current_user_permissions(
    current_user: User = Depends(get_current_user),
    permission_service: PermissionManagementService = Depends(get_permission_management_service)
):
    """Get comprehensive permission summary for current user."""
    return permission_service.get_permission_summary(current_user.id) 