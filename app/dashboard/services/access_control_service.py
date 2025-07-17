from typing import List, Optional, Dict
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from fastapi import HTTPException, status
from app.dashboard.models.access_control import (
    Permission, Role, RoleAssignment, PermissionOverride,
    ResourceType, ActionType, RoleHierarchy, RoleTemplate
)
from app.dashboard.schemas.access_control import (
    PermissionCreate, PermissionUpdate, RoleCreate, RoleUpdate,
    RoleAssignmentCreate, RoleAssignmentUpdate, PermissionOverrideCreate,
    PermissionOverrideUpdate, RoleHierarchyUpdate, RoleTemplateCreate
)
import logging

logger = logging.getLogger(__name__)

class AccessControlService:
    def __init__(self, db: Session):
        self.db = db

    # Permission Management
    async def create_permission(self, permission: PermissionCreate) -> Permission:
        """Create a new permission."""
        try:
            db_permission = Permission(
                name=permission.name,
                description=permission.description,
                resource_type=permission.resource_type,
                action=permission.action,
                scope=permission.scope
            )
            self.db.add(db_permission)
            self.db.commit()
            self.db.refresh(db_permission)
            return db_permission
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating permission: {str(e)}")
            raise

    async def get_permission(self, permission_id: str) -> Permission:
        """Get a permission by ID."""
        permission = self.db.query(Permission).filter(Permission.id == permission_id).first()
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permission not found"
            )
        return permission

    async def update_permission(self, permission_id: str, permission: PermissionUpdate) -> Permission:
        """Update a permission."""
        try:
            db_permission = await self.get_permission(permission_id)
            for key, value in permission.model_dump(exclude_unset=True).items():
                setattr(db_permission, key, value)
            db_permission.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(db_permission)
            return db_permission
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating permission: {str(e)}")
            raise

    async def delete_permission(self, permission_id: str) -> None:
        """Delete a permission."""
        try:
            db_permission = await self.get_permission(permission_id)
            self.db.delete(db_permission)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting permission: {str(e)}")
            raise

    async def list_permissions(
        self,
        resource_type: Optional[ResourceType] = None,
        action: Optional[ActionType] = None,
        scope: Optional[str] = None
    ) -> List[Permission]:
        """List permissions with optional filtering."""
        query = self.db.query(Permission)
        if resource_type:
            query = query.filter(Permission.resource_type == resource_type)
        if action:
            query = query.filter(Permission.action == action)
        if scope:
            query = query.filter(Permission.scope == scope)
        return query.all()

    # Role Management
    async def create_role(self, role: RoleCreate) -> Role:
        """Create a new role."""
        try:
            db_role = Role(
                name=role.name,
                description=role.description,
                is_system=role.is_system,
                is_template=role.is_template
            )
            self.db.add(db_role)
            self.db.commit()
            self.db.refresh(db_role)
            return db_role
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating role: {str(e)}")
            raise

    async def get_role(self, role_id: str) -> Role:
        """Get a role by ID."""
        role = self.db.query(Role).filter(Role.id == role_id).first()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        return role

    async def update_role(self, role_id: str, role: RoleUpdate) -> Role:
        """Update a role."""
        try:
            db_role = await self.get_role(role_id)
            for key, value in role.model_dump(exclude_unset=True).items():
                setattr(db_role, key, value)
            db_role.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(db_role)
            return db_role
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating role: {str(e)}")
            raise

    async def delete_role(self, role_id: str) -> None:
        """Delete a role."""
        try:
            db_role = await self.get_role(role_id)
            self.db.delete(db_role)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting role: {str(e)}")
            raise

    async def assign_permission_to_role(self, role_id: str, permission_id: str) -> Role:
        """Assign a permission to a role."""
        try:
            role = await self.get_role(role_id)
            permission = await self.get_permission(permission_id)
            role.permissions.append(permission)
            self.db.commit()
            self.db.refresh(role)
            return role
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error assigning permission to role: {str(e)}")
            raise

    async def remove_permission_from_role(self, role_id: str, permission_id: str) -> Role:
        """Remove a permission from a role."""
        try:
            role = await self.get_role(role_id)
            permission = await self.get_permission(permission_id)
            role.permissions.remove(permission)
            self.db.commit()
            self.db.refresh(role)
            return role
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error removing permission from role: {str(e)}")
            raise

    # Role Assignment Management
    async def assign_role(self, assignment: RoleAssignmentCreate) -> RoleAssignment:
        """Assign a role to a user."""
        # Check if user already has this role
        existing = self.db.query(RoleAssignment).filter(
            and_(
                RoleAssignment.user_id == assignment.user_id,
                RoleAssignment.role_id == assignment.role_id,
                RoleAssignment.is_active == True
            )
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already has this role"
            )

        db_assignment = RoleAssignment(**assignment.model_dump())
        self.db.add(db_assignment)
        self.db.commit()
        self.db.refresh(db_assignment)
        return db_assignment

    async def update_role_assignment(
        self,
        assignment_id: str,
        assignment: RoleAssignmentUpdate
    ) -> RoleAssignment:
        """Update a role assignment."""
        db_assignment = self.db.query(RoleAssignment).filter(
            RoleAssignment.id == assignment_id
        ).first()
        if not db_assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role assignment not found"
            )

        for key, value in assignment.model_dump(exclude_unset=True).items():
            setattr(db_assignment, key, value)
        db_assignment.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_assignment)
        return db_assignment

    async def revoke_role(self, assignment_id: str) -> None:
        """Revoke a role assignment."""
        db_assignment = self.db.query(RoleAssignment).filter(
            RoleAssignment.id == assignment_id
        ).first()
        if not db_assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role assignment not found"
            )

        db_assignment.is_active = False
        db_assignment.updated_at = datetime.utcnow()
        self.db.commit()

    async def get_user_roles(self, user_id: str) -> List[Role]:
        """Get all active roles for a user."""
        assignments = self.db.query(RoleAssignment).filter(
            and_(
                RoleAssignment.user_id == user_id,
                RoleAssignment.is_active == True,
                or_(
                    RoleAssignment.expires_at == None,
                    RoleAssignment.expires_at > datetime.utcnow()
                )
            )
        ).all()
        return [assignment.role for assignment in assignments]

    # Permission Override Management
    async def create_permission_override(
        self,
        override: PermissionOverrideCreate
    ) -> PermissionOverride:
        """Create a permission override."""
        db_override = PermissionOverride(**override.model_dump())
        self.db.add(db_override)
        self.db.commit()
        self.db.refresh(db_override)
        return db_override

    async def update_permission_override(
        self,
        override_id: str,
        override: PermissionOverrideUpdate
    ) -> PermissionOverride:
        """Update a permission override."""
        db_override = self.db.query(PermissionOverride).filter(
            PermissionOverride.id == override_id
        ).first()
        if not db_override:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permission override not found"
            )

        for key, value in override.model_dump(exclude_unset=True).items():
            setattr(db_override, key, value)
        db_override.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_override)
        return db_override

    async def delete_permission_override(self, override_id: str) -> None:
        """Delete a permission override."""
        db_override = self.db.query(PermissionOverride).filter(
            PermissionOverride.id == override_id
        ).first()
        if not db_override:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permission override not found"
            )

        self.db.delete(db_override)
        self.db.commit()

    # Access Control Checks
    async def check_permission(
        self,
        user_id: str,
        resource_type: ResourceType,
        action: ActionType,
        resource_id: Optional[str] = None
    ) -> bool:
        """Check if a user has permission to perform an action on a resource."""
        # Get user's active roles
        roles = await self.get_user_roles(user_id)
        
        # Check role-based permissions
        for role in roles:
            for permission in role.permissions:
                if (permission.resource_type == resource_type and
                    permission.action == action):
                    return True

        # Check permission overrides
        overrides = self.db.query(PermissionOverride).filter(
            and_(
                PermissionOverride.user_id == user_id,
                PermissionOverride.is_active == True,
                or_(
                    PermissionOverride.expires_at == None,
                    PermissionOverride.expires_at > datetime.utcnow()
                )
            )
        ).all()

        for override in overrides:
            permission = await self.get_permission(override.permission_id)
            if (permission.resource_type == resource_type and
                permission.action == action):
                return override.is_allowed

        return False

    async def get_effective_permissions(self, user_id: str) -> Dict[str, List[str]]:
        """Get all effective permissions for a user."""
        permissions = {}
        
        # Get role-based permissions
        roles = await self.get_user_roles(user_id)
        for role in roles:
            for permission in role.permissions:
                key = f"{permission.resource_type.value}.{permission.action.value}"
                if key not in permissions:
                    permissions[key] = []
                permissions[key].append(permission.scope)

        # Apply permission overrides
        overrides = self.db.query(PermissionOverride).filter(
            and_(
                PermissionOverride.user_id == user_id,
                PermissionOverride.is_active == True,
                or_(
                    PermissionOverride.expires_at == None,
                    PermissionOverride.expires_at > datetime.utcnow()
                )
            )
        ).all()

        for override in overrides:
            permission = await self.get_permission(override.permission_id)
            key = f"{permission.resource_type.value}.{permission.action.value}"
            if override.is_allowed:
                if key not in permissions:
                    permissions[key] = []
                permissions[key].append(permission.scope)
            else:
                if key in permissions:
                    permissions[key] = []

        return permissions

    async def update_role_hierarchy(self, hierarchy: RoleHierarchyUpdate) -> Dict[str, List[str]]:
        """Update the role hierarchy."""
        try:
            parent_role = await self.get_role(hierarchy.parent_role_id)
            child_role = await self.get_role(hierarchy.child_role_id)
            
            if not parent_role or not child_role:
                raise ValueError("Parent or child role not found")

            db_hierarchy = self.db.query(RoleHierarchy).filter(
                RoleHierarchy.parent_role_id == parent_role.id,
                RoleHierarchy.child_role_id == child_role.id
            ).first()

            if hierarchy.is_active:
                if not db_hierarchy:
                    db_hierarchy = RoleHierarchy(
                        parent_role_id=parent_role.id,
                        child_role_id=child_role.id
                    )
                    self.db.add(db_hierarchy)
            else:
                if db_hierarchy:
                    self.db.delete(db_hierarchy)

            self.db.commit()

            # Return the updated hierarchy
            return await self.get_role_hierarchy()
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating role hierarchy: {str(e)}")
            raise

    async def get_role_hierarchy(self) -> Dict[str, List[str]]:
        """Get the current role hierarchy."""
        try:
            hierarchies = self.db.query(RoleHierarchy).all()
            result = {}
            
            for hierarchy in hierarchies:
                if hierarchy.parent_role_id not in result:
                    result[hierarchy.parent_role_id] = []
                result[hierarchy.parent_role_id].append(hierarchy.child_role_id)
                
            return result
        except Exception as e:
            logger.error(f"Error getting role hierarchy: {str(e)}")
            raise

    async def create_role_template(self, template: RoleTemplateCreate) -> Role:
        """Create a new role template."""
        try:
            # Create the role
            role = RoleCreate(
                name=template.name,
                description=template.description,
                is_system=template.is_system,
                is_template=True
            )
            db_role = await self.create_role(role)
            
            # Assign permissions
            for permission_id in template.permissions:
                await self.assign_permission_to_role(db_role.id, permission_id)
            
            return db_role
        except Exception as e:
            logger.error(f"Error creating role template: {str(e)}")
            raise

    async def list_role_templates(self) -> List[Role]:
        """List available role templates."""
        try:
            return self.db.query(Role).filter(Role.is_template == True).all()
        except Exception as e:
            logger.error(f"Error listing role templates: {str(e)}")
            raise 