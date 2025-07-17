"""
Access Control Service

This module provides access control functionality for the application.
"""

from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime

from app.dashboard.models.access_control import (
    ResourceType,
    ActionType,
    Permission,
    Role,
    RoleAssignment,
    PermissionOverride,
    RoleHierarchy,
    RoleTemplate
)

class AccessControlService:
    """Service for managing access control."""
    
    def __init__(self, db: Session):
        """Initialize the service with a database session."""
        self.db = db
    
    async def check_access(
        self,
        user_id: str,
        resource_type: ResourceType,
        resource_id: str,
        action: ActionType
    ) -> bool:
        """
        Check if a user has access to perform an action on a resource.
        
        Args:
            user_id: The ID of the user
            resource_type: The type of resource
            resource_id: The ID of the resource
            action: The action to perform
            
        Returns:
            bool: True if access is granted, False otherwise
        """
        try:
            # Get user's role assignments
            role_assignments = self.db.query(RoleAssignment).filter(
                RoleAssignment.user_id == user_id,
                RoleAssignment.is_active == True,
                RoleAssignment.expires_at > datetime.utcnow()
            ).all()
            
            if not role_assignments:
                return False
                
            # Get all permissions from user's roles
            role_ids = [assignment.role_id for assignment in role_assignments]
            roles = self.db.query(Role).filter(
                Role.id.in_(role_ids),
                Role.is_active == True
            ).all()
            
            # Check for permission overrides
            overrides = self.db.query(PermissionOverride).filter(
                PermissionOverride.user_id == user_id,
                PermissionOverride.is_active == True,
                PermissionOverride.expires_at > datetime.utcnow()
            ).all()
            
            # Check if any override explicitly denies access
            for override in overrides:
                if not override.is_allowed:
                    return False
            
            # Check if any role has the required permission
            for role in roles:
                for permission in role.permissions:
                    if (permission.resource_type == resource_type and 
                        permission.action == action and 
                        permission.is_active):
                        return True
            
            return False
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error checking access: {str(e)}"
            )
    
    async def grant_access(
        self,
        user_id: str,
        role_id: str,
        assigned_by: str,
        expires_at: Optional[datetime] = None
    ) -> Dict[str, str]:
        """
        Grant access to a user by assigning a role.
        
        Args:
            user_id: The ID of the user
            role_id: The ID of the role to assign
            assigned_by: The ID of the user making the assignment
            expires_at: Optional expiration date for the assignment
            
        Returns:
            Dict[str, str]: Success message
        """
        try:
            # Check if role exists and is active
            role = self.db.query(Role).filter(
                Role.id == role_id,
                Role.is_active == True
            ).first()
            
            if not role:
                raise HTTPException(
                    status_code=404,
                    detail="Role not found or inactive"
                )
            
            # Create role assignment
            assignment = RoleAssignment(
                user_id=user_id,
                role_id=role_id,
                assigned_by=assigned_by,
                expires_at=expires_at
            )
            
            self.db.add(assignment)
            self.db.commit()
            
            return {"message": "Access granted successfully"}
            
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Error granting access: {str(e)}"
            )
    
    async def revoke_access(
        self,
        user_id: str,
        role_id: str
    ) -> Dict[str, str]:
        """
        Revoke access from a user by deactivating a role assignment.
        
        Args:
            user_id: The ID of the user
            role_id: The ID of the role to revoke
            
        Returns:
            Dict[str, str]: Success message
        """
        try:
            # Find and deactivate the role assignment
            assignment = self.db.query(RoleAssignment).filter(
                RoleAssignment.user_id == user_id,
                RoleAssignment.role_id == role_id,
                RoleAssignment.is_active == True
            ).first()
            
            if not assignment:
                raise HTTPException(
                    status_code=404,
                    detail="Active role assignment not found"
                )
            
            assignment.is_active = False
            self.db.commit()
            
            return {"message": "Access revoked successfully"}
            
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Error revoking access: {str(e)}"
            )
    
    async def get_user_permissions(
        self,
        user_id: str
    ) -> List[Dict[str, str]]:
        """
        Get all permissions for a user.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            List[Dict[str, str]]: List of permissions
        """
        try:
            # Get user's active role assignments
            role_assignments = self.db.query(RoleAssignment).filter(
                RoleAssignment.user_id == user_id,
                RoleAssignment.is_active == True,
                RoleAssignment.expires_at > datetime.utcnow()
            ).all()
            
            if not role_assignments:
                return []
            
            # Get all permissions from user's roles
            role_ids = [assignment.role_id for assignment in role_assignments]
            roles = self.db.query(Role).filter(
                Role.id.in_(role_ids),
                Role.is_active == True
            ).all()
            
            # Get permission overrides
            overrides = self.db.query(PermissionOverride).filter(
                PermissionOverride.user_id == user_id,
                PermissionOverride.is_active == True,
                PermissionOverride.expires_at > datetime.utcnow()
            ).all()
            
            # Build permission list
            permissions = []
            for role in roles:
                for permission in role.permissions:
                    if permission.is_active:
                        perm_dict = {
                            "id": permission.id,
                            "name": permission.name,
                            "resource_type": permission.resource_type,
                            "action": permission.action,
                            "scope": permission.scope
                        }
                        permissions.append(perm_dict)
            
            # Apply overrides
            for override in overrides:
                if not override.is_allowed:
                    permissions = [p for p in permissions if p["id"] != override.permission_id]
            
            return permissions
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error getting user permissions: {str(e)}"
            ) 