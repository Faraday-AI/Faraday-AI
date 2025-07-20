"""
Permission Management Service

This module provides comprehensive permission management functionality
including CRUD operations, permission checking, and resource-based access control.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Set
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from app.models.user_management.user.user_management import Permission, Role
from app.models.core.user import User
from app.schemas.permission_management import (
    PermissionCreate,
    PermissionUpdate,
    PermissionResponse,
    PermissionCheck,
    ResourcePermission
)


class PermissionManagementService:
    """Service for managing user permissions."""
    
    def __init__(self, db: Session):
        self.db = db
        self.resource_types = {
            "user": ["read", "write", "delete", "create"],
            "role": ["read", "write", "delete", "create", "assign"],
            "permission": ["read", "write", "delete", "create"],
            "organization": ["read", "write", "delete", "create", "manage"],
            "dashboard": ["read", "write", "delete", "create", "share"],
            "analytics": ["read", "write", "export"],
            "content": ["read", "write", "delete", "create", "publish"],
            "system": ["read", "write", "delete", "create", "admin"]
        }
    
    def get_permission_by_id(self, permission_id: int) -> Optional[Permission]:
        """Get permission by ID."""
        return self.db.query(Permission).filter(Permission.id == permission_id).first()
    
    def get_permission_by_name(self, permission_name: str) -> Optional[Permission]:
        """Get permission by name."""
        return self.db.query(Permission).filter(Permission.name == permission_name).first()
    
    def get_all_permissions(self) -> List[Permission]:
        """Get all permissions."""
        return self.db.query(Permission).all()
    
    def get_permissions_by_resource_type(self, resource_type: str) -> List[Permission]:
        """Get permissions by resource type."""
        return self.db.query(Permission).filter(Permission.resource_type == resource_type).all()
    
    def get_permissions_by_action(self, action: str) -> List[Permission]:
        """Get permissions by action."""
        return self.db.query(Permission).filter(Permission.action == action).all()
    
    def create_permission(self, permission_data: PermissionCreate) -> Permission:
        """Create a new permission."""
        # Check if permission already exists
        existing_permission = self.get_permission_by_name(permission_data.name)
        if existing_permission:
            raise HTTPException(status_code=400, detail="Permission already exists")
        
        # Validate resource type and action
        if permission_data.resource_type not in self.resource_types:
            raise HTTPException(status_code=400, detail="Invalid resource type")
        
        if permission_data.action not in self.resource_types[permission_data.resource_type]:
            raise HTTPException(status_code=400, detail="Invalid action for resource type")
        
        # Create new permission
        permission = Permission(
            name=permission_data.name,
            description=permission_data.description,
            resource_type=permission_data.resource_type,
            action=permission_data.action
        )
        
        try:
            self.db.add(permission)
            self.db.commit()
            self.db.refresh(permission)
            return permission
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Failed to create permission")
    
    def update_permission(self, permission_id: int, permission_data: PermissionUpdate) -> Permission:
        """Update permission."""
        permission = self.get_permission_by_id(permission_id)
        if not permission:
            raise HTTPException(status_code=404, detail="Permission not found")
        
        # Update permission fields
        update_data = permission_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(permission, field, value)
        
        permission.updated_at = datetime.utcnow()
        
        try:
            self.db.commit()
            self.db.refresh(permission)
            return permission
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Failed to update permission")
    
    def delete_permission(self, permission_id: int) -> bool:
        """Delete permission."""
        permission = self.get_permission_by_id(permission_id)
        if not permission:
            raise HTTPException(status_code=404, detail="Permission not found")
        
        # Check if permission is assigned to any roles
        if permission.roles:
            raise HTTPException(status_code=400, detail="Cannot delete permission that is assigned to roles")
        
        try:
            self.db.delete(permission)
            self.db.commit()
            return True
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Failed to delete permission")
    
    def assign_permission_to_role(self, role_id: int, permission_id: int) -> bool:
        """Assign permission to role."""
        role = self.db.query(Role).filter(Role.id == role_id).first()
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        
        permission = self.get_permission_by_id(permission_id)
        if not permission:
            raise HTTPException(status_code=404, detail="Permission not found")
        
        # Check if role already has this permission
        if permission in role.permissions:
            raise HTTPException(status_code=400, detail="Role already has this permission")
        
        try:
            role.permissions.append(permission)
            self.db.commit()
            return True
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Failed to assign permission")
    
    def remove_permission_from_role(self, role_id: int, permission_id: int) -> bool:
        """Remove permission from role."""
        role = self.db.query(Role).filter(Role.id == role_id).first()
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        
        permission = self.get_permission_by_id(permission_id)
        if not permission:
            raise HTTPException(status_code=404, detail="Permission not found")
        
        # Check if role has this permission
        if permission not in role.permissions:
            raise HTTPException(status_code=400, detail="Role does not have this permission")
        
        try:
            role.permissions.remove(permission)
            self.db.commit()
            return True
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Failed to remove permission")
    
    def get_role_permissions(self, role_id: int) -> List[Permission]:
        """Get all permissions assigned to a role."""
        role = self.db.query(Role).filter(Role.id == role_id).first()
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        
        return list(role.permissions)
    
    def get_user_permissions(self, user_id: int) -> Set[str]:
        """Get all permissions for a user (from all their roles)."""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        permissions = set()
        
        # Add permissions from primary role
        if user.role:
            primary_role = self.db.query(Role).filter(Role.name == user.role).first()
            if primary_role:
                permissions.update([perm.name for perm in primary_role.permissions])
        
        # Add permissions from assigned roles
        for role in user.roles:
            permissions.update([perm.name for perm in role.permissions])
        
        return permissions
    
    def check_user_permission(self, user_id: int, permission_name: str) -> bool:
        """Check if user has a specific permission."""
        user_permissions = self.get_user_permissions(user_id)
        return permission_name in user_permissions
    
    def check_user_resource_permission(self, user_id: int, resource_type: str, action: str) -> bool:
        """Check if user has permission for a specific resource and action."""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        # Check if user is super admin (has all permissions)
        if user.role == "super_admin" or user.is_superuser:
            return True
        
        # Get user's permissions
        user_permissions = self.get_user_permissions(user_id)
        
        # Check for specific permission
        specific_permission = f"{resource_type}_{action}"
        if specific_permission in user_permissions:
            return True
        
        # Check for wildcard permissions
        wildcard_permission = f"{resource_type}_*"
        if wildcard_permission in user_permissions:
            return True
        
        return False
    
    def get_available_permissions(self, current_user_id: int) -> List[Permission]:
        """Get permissions available for assignment by current user."""
        current_user = self.db.query(User).filter(User.id == current_user_id).first()
        if not current_user:
            raise HTTPException(status_code=404, detail="Current user not found")
        
        # Super admins can assign all permissions
        if current_user.role == "super_admin" or current_user.is_superuser:
            return self.get_all_permissions()
        
        # Other users can only assign permissions they have
        user_permissions = self.get_user_permissions(current_user_id)
        available_permissions = []
        
        for permission in self.get_all_permissions():
            if permission.name in user_permissions:
                available_permissions.append(permission)
        
        return available_permissions
    
    def bulk_check_permissions(self, user_id: int, permissions: List[str]) -> Dict[str, bool]:
        """Bulk check multiple permissions for a user."""
        user_permissions = self.get_user_permissions(user_id)
        results = {}
        
        for permission in permissions:
            results[permission] = permission in user_permissions
        
        return results
    
    def get_permission_summary(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive permission summary for a user."""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_permissions = self.get_user_permissions(user_id)
        
        # Group permissions by resource type
        permissions_by_resource = {}
        for permission_name in user_permissions:
            parts = permission_name.split("_", 1)
            if len(parts) == 2:
                resource_type, action = parts
                if resource_type not in permissions_by_resource:
                    permissions_by_resource[resource_type] = []
                permissions_by_resource[resource_type].append(action)
        
        return {
            "user_id": user_id,
            "primary_role": user.role,
            "assigned_roles": [role.name for role in user.roles],
            "total_permissions": len(user_permissions),
            "permissions": list(user_permissions),
            "permissions_by_resource": permissions_by_resource,
            "is_superuser": user.is_superuser
        }
    
    def get_resource_permissions(self, resource_type: str) -> List[ResourcePermission]:
        """Get all available permissions for a resource type."""
        if resource_type not in self.resource_types:
            raise HTTPException(status_code=400, detail="Invalid resource type")
        
        permissions = []
        for action in self.resource_types[resource_type]:
            permission_name = f"{resource_type}_{action}"
            permissions.append(ResourcePermission(
                name=permission_name,
                resource_type=resource_type,
                action=action,
                description=f"Permission to {action} {resource_type}"
            ))
        
        return permissions


def get_permission_management_service(db: Session) -> PermissionManagementService:
    """Dependency to get permission management service."""
    return PermissionManagementService(db) 