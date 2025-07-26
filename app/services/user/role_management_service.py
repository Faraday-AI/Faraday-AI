"""
Role Management Service

This module provides comprehensive role management functionality
including CRUD operations, role hierarchy, and role assignment.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, Depends

from app.models.user_management.user.user_management import Role, UserRole
from app.models.core.user import User
from app.core.database import get_db
from app.schemas.role_management import (
    RoleCreate,
    RoleUpdate,
    RoleResponse,
    RoleAssignment,
    RoleHierarchy
)


class RoleManagementService:
    """Service for managing user roles."""
    
    def __init__(self, db: Session):
        self.db = db
        self.role_hierarchy = {
            UserRole.SUPER_ADMIN: 100,
            UserRole.ADMIN: 80,
            UserRole.TEACHER: 60,
            UserRole.STAFF: 50,
            UserRole.STUDENT: 30,
            UserRole.PARENT: 20
        }
    
    def get_role_by_id(self, role_id: int) -> Optional[Role]:
        """Get role by ID."""
        return self.db.query(Role).filter(Role.id == role_id).first()
    
    def get_role_by_name(self, role_name: str) -> Optional[Role]:
        """Get role by name."""
        return self.db.query(Role).filter(Role.name == role_name).first()
    
    def get_all_roles(self) -> List[Role]:
        """Get all roles."""
        return self.db.query(Role).all()
    
    def get_active_roles(self) -> List[Role]:
        """Get all active roles."""
        return self.db.query(Role).filter(Role.status == "active").all()
    
    def create_role(self, role_data: RoleCreate) -> Role:
        """Create a new role."""
        # Check if role already exists
        existing_role = self.get_role_by_name(role_data.name)
        if existing_role:
            raise HTTPException(status_code=400, detail="Role already exists")
        
        # Validate role hierarchy
        if role_data.parent_role:
            parent_role = self.get_role_by_name(role_data.parent_role)
            if not parent_role:
                raise HTTPException(status_code=400, detail="Parent role not found")
        
        # Create new role
        role = Role(
            name=role_data.name,
            description=role_data.description,
            is_custom=role_data.is_custom
        )
        
        try:
            self.db.add(role)
            self.db.commit()
            self.db.refresh(role)
            return role
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Failed to create role")
    
    def update_role(self, role_id: int, role_data: RoleUpdate) -> Role:
        """Update role."""
        role = self.get_role_by_id(role_id)
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        
        # Prevent updating system roles
        if not role.is_custom and role_data.name != role.name:
            raise HTTPException(status_code=400, detail="Cannot modify system roles")
        
        # Update role fields
        update_data = role_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(role, field, value)
        
        role.updated_at = datetime.utcnow()
        
        try:
            self.db.commit()
            self.db.refresh(role)
            return role
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Failed to update role")
    
    def delete_role(self, role_id: int) -> bool:
        """Delete role."""
        role = self.get_role_by_id(role_id)
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        
        # Prevent deleting system roles
        if not role.is_custom:
            raise HTTPException(status_code=400, detail="Cannot delete system roles")
        
        # Check if role is assigned to any users
        if role.users:
            raise HTTPException(status_code=400, detail="Cannot delete role that is assigned to users")
        
        try:
            self.db.delete(role)
            self.db.commit()
            return True
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Failed to delete role")
    
    def assign_role_to_user(self, user_id: int, role_name: str) -> bool:
        """Assign role to user."""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        role = self.get_role_by_name(role_name)
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        
        # Check if user already has this role
        if role in user.roles:
            raise HTTPException(status_code=400, detail="User already has this role")
        
        try:
            user.roles.append(role)
            self.db.commit()
            return True
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Failed to assign role")
    
    def remove_role_from_user(self, user_id: int, role_name: str) -> bool:
        """Remove role from user."""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        role = self.get_role_by_name(role_name)
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        
        # Check if user has this role
        if role not in user.roles:
            raise HTTPException(status_code=400, detail="User does not have this role")
        
        # Prevent removing primary role
        if role.name == user.role:
            raise HTTPException(status_code=400, detail="Cannot remove user's primary role")
        
        try:
            user.roles.remove(role)
            self.db.commit()
            return True
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Failed to remove role")
    
    def get_user_roles(self, user_id: int) -> List[Role]:
        """Get all roles assigned to a user."""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return list(user.roles)
    
    def get_users_with_role(self, role_name: str) -> List[User]:
        """Get all users with a specific role."""
        role = self.get_role_by_name(role_name)
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        
        return list(role.users)
    
    def get_role_hierarchy(self) -> Dict[str, Any]:
        """Get role hierarchy information."""
        roles = self.get_all_roles()
        hierarchy = {}
        
        for role in roles:
            hierarchy[role.name] = {
                "id": role.id,
                "name": role.name,
                "description": role.description,
                "is_custom": role.is_custom,
                "level": self.role_hierarchy.get(role.name, 0),
                "user_count": len(role.users),
                "permissions": [perm.name for perm in role.permissions]
            }
        
        return hierarchy
    
    def check_role_permission(self, user_id: int, required_role: str) -> bool:
        """Check if user has required role or higher."""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        # Check primary role
        if user.role == required_role:
            return True
        
        # Check assigned roles
        user_roles = [role.name for role in user.roles]
        if required_role in user_roles:
            return True
        
        # Check role hierarchy
        required_level = self.role_hierarchy.get(required_role, 0)
        user_level = self.role_hierarchy.get(user.role, 0)
        
        return user_level >= required_level
    
    def get_available_roles(self, current_user_id: int) -> List[Role]:
        """Get roles available for assignment by current user."""
        current_user = self.db.query(User).filter(User.id == current_user_id).first()
        if not current_user:
            raise HTTPException(status_code=404, detail="Current user not found")
        
        current_level = self.role_hierarchy.get(current_user.role, 0)
        available_roles = []
        
        for role in self.get_all_roles():
            role_level = self.role_hierarchy.get(role.name, 0)
            if role_level < current_level:  # Can only assign lower-level roles
                available_roles.append(role)
        
        return available_roles
    
    def bulk_assign_roles(self, assignments: List[RoleAssignment]) -> Dict[str, Any]:
        """Bulk assign roles to multiple users."""
        results = {
            "success": [],
            "failed": []
        }
        
        for assignment in assignments:
            try:
                self.assign_role_to_user(assignment.user_id, assignment.role_name)
                results["success"].append({
                    "user_id": assignment.user_id,
                    "role_name": assignment.role_name
                })
            except Exception as e:
                results["failed"].append({
                    "user_id": assignment.user_id,
                    "role_name": assignment.role_name,
                    "error": str(e)
                })
        
        return results


def get_role_management_service(db: Session = Depends(get_db)) -> RoleManagementService:
    """Dependency to get role management service."""
    return RoleManagementService(db) 