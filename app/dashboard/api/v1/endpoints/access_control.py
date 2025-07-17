"""Access Control API endpoints."""

from typing import List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.dashboard.services.access_control_service import AccessControlService
from app.dashboard.schemas.access_control import (
    PermissionCreate, PermissionUpdate, PermissionResponse,
    RoleCreate, RoleUpdate, RoleResponse,
    RoleAssignmentCreate, RoleAssignmentUpdate, RoleAssignmentResponse,
    PermissionOverrideCreate, PermissionOverrideUpdate, PermissionOverrideResponse,
    ResourceType, ActionType,
    BulkPermissionCheck,
    RoleHierarchyUpdate,
    RoleHierarchyResponse,
    PermissionCheckRequest, PermissionCheckResponse,
    BulkPermissionCheckRequest, BulkPermissionCheckResponse,
    RoleTemplateCreate, RoleTemplateResponse
)
from pydantic import BaseModel
import logging
from app.dashboard.dependencies import get_current_user, require_admin
from app.dashboard.models import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/access-control", tags=["access-control"])

# Permission Endpoints
@router.post("/permissions", response_model=PermissionResponse, status_code=status.HTTP_201_CREATED)
async def create_permission(
    permission: PermissionCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin)
):
    """Create a new permission. Requires admin access."""
    try:
        service = AccessControlService(db)
        return await service.create_permission(permission)
    except Exception as e:
        logger.error(f"Error creating permission: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create permission"
        )

@router.get("/permissions/{permission_id}", response_model=PermissionResponse)
async def get_permission(
    permission_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user)
):
    """Get a permission by ID."""
    try:
        service = AccessControlService(db)
        permission = await service.get_permission(permission_id)
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permission not found"
            )
        return permission
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting permission: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get permission"
        )

@router.patch("/permissions/{permission_id}", response_model=PermissionResponse)
async def update_permission(
    permission_id: str,
    permission: PermissionUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin)
):
    """Update a permission. Requires admin access."""
    try:
        service = AccessControlService(db)
        updated = await service.update_permission(permission_id, permission)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permission not found"
            )
        return updated
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating permission: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update permission"
        )

@router.delete("/permissions/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_permission(
    permission_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin)
):
    """Delete a permission. Requires admin access."""
    try:
        service = AccessControlService(db)
        success = await service.delete_permission(permission_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permission not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting permission: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete permission"
        )

@router.get("/permissions", response_model=List[PermissionResponse])
async def list_permissions(
    resource_type: Optional[ResourceType] = None,
    action: Optional[ActionType] = None,
    scope: Optional[str] = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user)
):
    """List permissions with optional filtering."""
    try:
        service = AccessControlService(db)
        return await service.list_permissions(resource_type, action, scope)
    except Exception as e:
        logger.error(f"Error listing permissions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list permissions"
        )

# Role Endpoints
@router.post("/roles", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    role: RoleCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin)
):
    """Create a new role. Requires admin access."""
    try:
        service = AccessControlService(db)
        return await service.create_role(role)
    except Exception as e:
        logger.error(f"Error creating role: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create role"
        )

@router.get("/roles/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user)
):
    """Get a role by ID."""
    try:
        service = AccessControlService(db)
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
        logger.error(f"Error getting role: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get role"
        )

@router.patch("/roles/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: str,
    role: RoleUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin)
):
    """Update a role. Requires admin access."""
    try:
        service = AccessControlService(db)
        updated = await service.update_role(role_id, role)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        return updated
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating role: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update role"
        )

@router.delete("/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    role_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin)
):
    """Delete a role. Requires admin access."""
    try:
        service = AccessControlService(db)
        success = await service.delete_role(role_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting role: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete role"
        )

@router.post("/roles/{role_id}/permissions/{permission_id}", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def assign_permission_to_role(
    role_id: str,
    permission_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin)
):
    """Assign a permission to a role. Requires admin access."""
    try:
        service = AccessControlService(db)
        return await service.assign_permission_to_role(role_id, permission_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error assigning permission to role: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to assign permission to role"
        )

@router.delete("/roles/{role_id}/permissions/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_permission_from_role(
    role_id: str,
    permission_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin)
):
    """Remove a permission from a role. Requires admin access."""
    try:
        service = AccessControlService(db)
        success = await service.remove_permission_from_role(role_id, permission_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role or permission not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing permission from role: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove permission from role"
        )

# Role Assignment Endpoints
@router.post("/roles/{role_id}/assignments", response_model=RoleAssignmentResponse, status_code=status.HTTP_201_CREATED)
async def assign_role_to_user(
    role_id: str,
    assignment: RoleAssignmentCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin)
):
    """Assign a role to a user. Requires admin access."""
    try:
        service = AccessControlService(db)
        return await service.assign_role(assignment)
    except Exception as e:
        logger.error(f"Error assigning role to user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to assign role to user"
        )

@router.delete("/role-assignments/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_role_assignment(
    assignment_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin)
):
    """Revoke a role assignment. Requires admin access."""
    try:
        service = AccessControlService(db)
        success = await service.revoke_role(assignment_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role assignment not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error revoking role assignment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to revoke role assignment"
        )

@router.get("/users/{user_id}/roles", response_model=List[RoleResponse])
async def get_user_roles(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get all active roles for a user."""
    service = AccessControlService(db)
    return await service.get_user_roles(user_id)

# Permission Override Endpoints
@router.post("/permissions/{permission_id}/overrides", response_model=PermissionOverrideResponse, status_code=status.HTTP_201_CREATED)
async def create_permission_override(
    permission_id: str,
    override: PermissionOverrideCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin)
):
    """Create a permission override. Requires admin access."""
    try:
        service = AccessControlService(db)
        override.permission_id = permission_id
        return await service.create_permission_override(override)
    except Exception as e:
        logger.error(f"Error creating permission override: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create permission override"
        )

@router.put("/permission-overrides/{override_id}", response_model=PermissionOverrideResponse)
async def update_permission_override(
    override_id: str,
    override: PermissionOverrideUpdate,
    db: Session = Depends(get_db)
):
    """Update a permission override."""
    try:
        service = AccessControlService(db)
        updated = await service.update_permission_override(override_id, override)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permission override not found"
            )
        return updated
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating permission override: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update permission override"
        )

@router.delete("/permission-overrides/{override_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_permission_override(
    override_id: str,
    db: Session = Depends(get_db)
):
    """Delete a permission override."""
    try:
        service = AccessControlService(db)
        success = await service.delete_permission_override(override_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permission override not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting permission override: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete permission override"
        )

# Access Control Check Endpoints
@router.post("/check-permission", response_model=PermissionCheckResponse)
async def check_permission(
    request: PermissionCheckRequest,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user)
):
    """Check if a user has a specific permission."""
    service = AccessControlService(db)
    has_permission = await service.check_permission(
        request.user_id,
        request.resource_type,
        request.action,
        request.resource_id
    )
    return PermissionCheckResponse(has_permission=has_permission)

@router.post("/check-bulk-permissions", response_model=BulkPermissionCheckResponse)
async def check_bulk_permissions(
    request: BulkPermissionCheckRequest,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user)
):
    """Check multiple permissions for a user."""
    service = AccessControlService(db)
    results = []
    for permission in request.permissions:
        has_permission = await service.check_permission(
            request.user_id,
            permission.resource_type,
            permission.action,
            permission.resource_id
        )
        results.append({
            "resource_type": permission.resource_type,
            "action": permission.action,
            "resource_id": permission.resource_id,
            "has_permission": has_permission
        })
    return BulkPermissionCheckResponse(results=results)

# Role Hierarchy Management
@router.post("/role-hierarchy", response_model=RoleHierarchyResponse, status_code=status.HTTP_201_CREATED)
async def update_role_hierarchy(
    hierarchy: RoleHierarchyUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin)
):
    """Update role hierarchy. Requires admin access."""
    try:
        service = AccessControlService(db)
        return await service.update_role_hierarchy(hierarchy)
    except Exception as e:
        logger.error(f"Error updating role hierarchy: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update role hierarchy"
        )

@router.get("/role-hierarchy", response_model=RoleHierarchyResponse)
async def get_role_hierarchy(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user)
):
    """Get the current role hierarchy."""
    try:
        service = AccessControlService(db)
        return await service.get_role_hierarchy()
    except Exception as e:
        logger.error(f"Error getting role hierarchy: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get role hierarchy"
        )

# Role Templates
@router.post("/roles/templates", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role_template(
    template: RoleTemplateCreate,
    db: Session = Depends(get_db)
):
    """Create a new role template."""
    try:
        service = AccessControlService(db)
        return await service.create_role_template(template)
    except Exception as e:
        logger.error(f"Error creating role template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create role template"
        )

@router.get("/roles/templates", response_model=List[RoleResponse])
async def list_role_templates(
    db: Session = Depends(get_db)
):
    """List available role templates."""
    try:
        service = AccessControlService(db)
        return await service.list_role_templates()
    except Exception as e:
        logger.error(f"Error listing role templates: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list role templates"
        )

# Permission Inheritance
@router.post("/permissions/inherit")
async def set_permission_inheritance(
    permission_id: str,
    inherits_from: str,
    db: Session = Depends(get_db)
):
    """Set up permission inheritance between two permissions."""
    service = AccessControlService(db)
    permission = await service.get_permission(permission_id)
    parent_permission = await service.get_permission(inherits_from)
    
    permission.inherits_from = parent_permission.id
    self.db.commit()
    return {"status": "success"}

@router.get("/permissions/{permission_id}/inheritance")
async def get_permission_inheritance(
    permission_id: str,
    db: Session = Depends(get_db)
):
    """Get the inheritance chain for a permission."""
    service = AccessControlService(db)
    permission = await service.get_permission(permission_id)
    
    inheritance_chain = []
    current = permission
    while current.inherits_from:
        parent = await service.get_permission(current.inherits_from)
        inheritance_chain.append(parent)
        current = parent
    
    return {
        "permission": permission,
        "inheritance_chain": inheritance_chain
    } 