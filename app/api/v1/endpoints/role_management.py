"""
Role Management API Endpoints

This module provides API endpoints for role management.
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.core.user import User
from app.services.user.role_management_service import RoleManagementService, get_role_management_service
from app.schemas.role_management import (
    RoleCreate,
    RoleUpdate,
    RoleResponse,
    RoleAssignment,
    RoleRemoval,
    RoleHierarchy,
    RoleSummary,
    UserRoleSummary,
    BulkRoleAssignment,
    RoleSearch,
    RoleFilter
)

router = APIRouter()


@router.get("/roles", response_model=List[RoleResponse])
async def get_all_roles(
    current_user: User = Depends(get_current_user),
    role_service: RoleManagementService = Depends(get_role_management_service)
):
    """Get all roles."""
    # Check if user has permission to view roles
    if not role_service.check_role_permission(current_user.id, "admin"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    return role_service.get_all_roles()


@router.get("/roles/active", response_model=List[RoleResponse])
async def get_active_roles(
    current_user: User = Depends(get_current_user),
    role_service: RoleManagementService = Depends(get_role_management_service)
):
    """Get all active roles."""
    return role_service.get_active_roles()


@router.get("/roles/{role_id}", response_model=RoleResponse)
async def get_role_by_id(
    role_id: int,
    current_user: User = Depends(get_current_user),
    role_service: RoleManagementService = Depends(get_role_management_service)
):
    """Get role by ID."""
    role = role_service.get_role_by_id(role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    return role


@router.post("/roles", response_model=RoleResponse)
async def create_role(
    role_data: RoleCreate,
    current_user: User = Depends(get_current_user),
    role_service: RoleManagementService = Depends(get_role_management_service)
):
    """Create a new role."""
    # Check if user has permission to create roles
    if not role_service.check_role_permission(current_user.id, "admin"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    return role_service.create_role(role_data)


@router.put("/roles/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: int,
    role_data: RoleUpdate,
    current_user: User = Depends(get_current_user),
    role_service: RoleManagementService = Depends(get_role_management_service)
):
    """Update role."""
    # Check if user has permission to update roles
    if not role_service.check_role_permission(current_user.id, "admin"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    return role_service.update_role(role_id, role_data)


@router.delete("/roles/{role_id}")
async def delete_role(
    role_id: int,
    current_user: User = Depends(get_current_user),
    role_service: RoleManagementService = Depends(get_role_management_service)
):
    """Delete role."""
    # Check if user has permission to delete roles
    if not role_service.check_role_permission(current_user.id, "admin"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    success = role_service.delete_role(role_id)
    return {"message": "Role deleted successfully"}


@router.post("/roles/assign")
async def assign_role_to_user(
    assignment: RoleAssignment,
    current_user: User = Depends(get_current_user),
    role_service: RoleManagementService = Depends(get_role_management_service)
):
    """Assign role to user."""
    # Check if user has permission to assign roles
    if not role_service.check_role_permission(current_user.id, "admin"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    success = role_service.assign_role_to_user(assignment.user_id, assignment.role_name)
    return {"message": "Role assigned successfully"}


@router.post("/roles/remove")
async def remove_role_from_user(
    removal: RoleRemoval,
    current_user: User = Depends(get_current_user),
    role_service: RoleManagementService = Depends(get_role_management_service)
):
    """Remove role from user."""
    # Check if user has permission to remove roles
    if not role_service.check_role_permission(current_user.id, "admin"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    success = role_service.remove_role_from_user(removal.user_id, removal.role_name)
    return {"message": "Role removed successfully"}


@router.get("/users/{user_id}/roles", response_model=List[RoleResponse])
async def get_user_roles(
    user_id: int,
    current_user: User = Depends(get_current_user),
    role_service: RoleManagementService = Depends(get_role_management_service)
):
    """Get all roles assigned to a user."""
    # Users can view their own roles, admins can view any user's roles
    if user_id != current_user.id and not role_service.check_role_permission(current_user.id, "admin"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    return role_service.get_user_roles(user_id)


@router.get("/roles/{role_name}/users", response_model=List[UserRoleSummary])
async def get_users_with_role(
    role_name: str,
    current_user: User = Depends(get_current_user),
    role_service: RoleManagementService = Depends(get_role_management_service)
):
    """Get all users with a specific role."""
    # Check if user has permission to view role assignments
    if not role_service.check_role_permission(current_user.id, "admin"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    users = role_service.get_users_with_role(role_name)
    return [
        UserRoleSummary(
            user_id=user.id,
            primary_role=user.role,
            assigned_roles=[role.name for role in user.roles],
            role_count=len(user.roles),
            is_superuser=user.is_superuser
        )
        for user in users
    ]


@router.get("/roles/hierarchy", response_model=Dict[str, Any])
async def get_role_hierarchy(
    current_user: User = Depends(get_current_user),
    role_service: RoleManagementService = Depends(get_role_management_service)
):
    """Get role hierarchy information."""
    return role_service.get_role_hierarchy()


@router.post("/roles/bulk-assign")
async def bulk_assign_roles(
    assignments: BulkRoleAssignment,
    current_user: User = Depends(get_current_user),
    role_service: RoleManagementService = Depends(get_role_management_service)
):
    """Bulk assign roles to multiple users."""
    # Check if user has permission to assign roles
    if not role_service.check_role_permission(current_user.id, "admin"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    results = role_service.bulk_assign_roles(assignments.assignments)
    return {
        "message": f"Bulk role assignment completed. {len(results['success'])} successful, {len(results['failed'])} failed",
        "results": results
    }


@router.get("/roles/available", response_model=List[RoleResponse])
async def get_available_roles(
    current_user: User = Depends(get_current_user),
    role_service: RoleManagementService = Depends(get_role_management_service)
):
    """Get roles available for assignment by current user."""
    return role_service.get_available_roles(current_user.id)


@router.post("/roles/search", response_model=List[RoleResponse])
async def search_roles(
    search: RoleSearch,
    current_user: User = Depends(get_current_user),
    role_service: RoleManagementService = Depends(get_role_management_service)
):
    """Search roles."""
    # Check if user has permission to view roles
    if not role_service.check_role_permission(current_user.id, "admin"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    roles = role_service.get_all_roles()
    
    # Apply filters
    if search.query:
        roles = [role for role in roles if search.query.lower() in role.name.lower()]
    
    if search.is_custom is not None:
        roles = [role for role in roles if role.is_custom == search.is_custom]
    
    if search.status:
        roles = [role for role in roles if role.status == search.status]
    
    return roles[:search.limit]


@router.post("/roles/filter", response_model=List[RoleSummary])
async def filter_roles(
    filter_data: RoleFilter,
    current_user: User = Depends(get_current_user),
    role_service: RoleManagementService = Depends(get_role_management_service)
):
    """Filter roles."""
    # Check if user has permission to view roles
    if not role_service.check_role_permission(current_user.id, "admin"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    roles = role_service.get_all_roles()
    
    # Apply filters
    if filter_data.name_contains:
        roles = [role for role in roles if filter_data.name_contains.lower() in role.name.lower()]
    
    if filter_data.is_custom is not None:
        roles = [role for role in roles if role.is_custom == filter_data.is_custom]
    
    if filter_data.has_permissions:
        roles = [role for role in roles if any(perm.name in filter_data.has_permissions for perm in role.permissions)]
    
    if filter_data.user_count_min is not None:
        roles = [role for role in roles if len(role.users) >= filter_data.user_count_min]
    
    if filter_data.user_count_max is not None:
        roles = [role for role in roles if len(role.users) <= filter_data.user_count_max]
    
    return [
        RoleSummary(
            id=role.id,
            name=role.name,
            description=role.description,
            user_count=len(role.users),
            permission_count=len(role.permissions),
            is_custom=role.is_custom,
            created_at=role.created_at
        )
        for role in roles
    ]


@router.get("/roles/check/{role_name}")
async def check_role_permission(
    role_name: str,
    current_user: User = Depends(get_current_user),
    role_service: RoleManagementService = Depends(get_role_management_service)
):
    """Check if current user has a specific role or higher."""
    has_permission = role_service.check_role_permission(current_user.id, role_name)
    return {
        "user_id": current_user.id,
        "required_role": role_name,
        "has_permission": has_permission
    } 