from typing import List, Optional, Dict, Union
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from fastapi import HTTPException, status
from app.dashboard.models.access_control import (
    Permission, Role, RoleAssignment, PermissionOverride,
    ResourceType, ActionType, RoleHierarchy, RoleTemplate, RolePermission
)
from app.dashboard.schemas.access_control import (
    PermissionCreate, PermissionUpdate, RoleCreate, RoleUpdate,
    RoleAssignmentCreate, RoleAssignmentUpdate, PermissionOverrideCreate,
    PermissionOverrideUpdate, RoleHierarchyCreate, RoleTemplateCreate
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
            # Check if permission with same name already exists
            existing_permission = self.db.query(Permission).filter(Permission.name == permission.name).first()
            if existing_permission:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Permission with this name already exists"
                )
            
            db_permission = Permission(
                name=permission.name,
                description=permission.description,
                resource_type=permission.resource_type,
                action=permission.action,
                scope=permission.scope,
                permission_type=permission.permission_type
            )
            self.db.add(db_permission)
            self.db.commit()
            self.db.refresh(db_permission)
            return db_permission
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating permission: {str(e)}")
            raise

    async def get_permission(self, permission_id: Union[str, int]) -> Permission:
        """Get a permission by ID."""
        permission = self.db.query(Permission).filter(Permission.id == permission_id).first()
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permission not found"
            )
        return permission

    async def update_permission(self, permission_id: Union[str, int], permission: PermissionUpdate) -> Permission:
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

    async def delete_permission(self, permission_id: Union[str, int]) -> None:
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
                description=role.description
            )
            self.db.add(db_role)
            self.db.commit()
            self.db.refresh(db_role)
            return db_role
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating role: {str(e)}")
            raise

    async def get_role(self, role_id: Union[str, int]) -> Role:
        """Get a role by ID."""
        role = self.db.query(Role).filter(Role.id == role_id).first()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        return role

    async def update_role(self, role_id: Union[str, int], role: RoleUpdate) -> Role:
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

    async def delete_role(self, role_id: Union[str, int]) -> None:
        """Delete a role."""
        try:
            db_role = await self.get_role(role_id)
            self.db.delete(db_role)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting role: {str(e)}")
            raise

    async def assign_permission_to_role(self, role_id: Union[str, int], permission_id: Union[str, int]) -> Role:
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

    async def remove_permission_from_role(self, role_id: Union[str, int], permission_id: Union[str, int]) -> Role:
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

    async def get_role_permissions(self, role_id: Union[str, int]) -> List[Permission]:
        """Get all permissions for a role."""
        try:
            role = await self.get_role(role_id)
            return role.permissions
        except Exception as e:
            logger.error(f"Error getting role permissions: {str(e)}")
            raise

    # Role Assignment Management
    async def assign_role(self, assignment: RoleAssignmentCreate) -> RoleAssignment:
        """Assign a role to a user."""
        try:
            db_assignment = RoleAssignment(
                user_id=assignment.user_id,
                role_id=assignment.role_id
            )
            self.db.add(db_assignment)
            self.db.commit()
            self.db.refresh(db_assignment)
            return db_assignment
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error assigning role: {str(e)}")
            raise

    async def assign_role_to_user(self, user_id: Union[str, int], role_id: Union[str, int], assigned_by: str) -> RoleAssignment:
        """Assign a role to a user."""
        try:
            from app.dashboard.schemas.access_control import RoleAssignmentCreate
            
            assignment_data = RoleAssignmentCreate(
                user_id=user_id,
                role_id=role_id,
                assigned_by=assigned_by
            )
            return await self.assign_role(assignment_data)
        except Exception as e:
            logger.error(f"Error assigning role to user: {str(e)}")
            raise

    async def update_role_assignment(
        self,
        assignment_id: Union[str, int],
        assignment: RoleAssignmentUpdate
    ) -> RoleAssignment:
        """Update a role assignment."""
        try:
            db_assignment = self.db.query(RoleAssignment).filter(RoleAssignment.id == assignment_id).first()
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
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating role assignment: {str(e)}")
            raise

    async def revoke_role(self, assignment_id: Union[str, int]) -> None:
        """Revoke a role assignment."""
        try:
            db_assignment = self.db.query(RoleAssignment).filter(RoleAssignment.id == assignment_id).first()
            if not db_assignment:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Role assignment not found"
                )
            self.db.delete(db_assignment)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error revoking role: {str(e)}")
            raise

    async def get_user_roles(self, user_id: Union[str, int]) -> List[Role]:
        """Get all roles assigned to a user."""
        user_roles = self.db.query(RoleAssignment).filter(
            RoleAssignment.user_id == user_id,
            RoleAssignment.is_active == True
        ).all()
        return [user_role.role for user_role in user_roles]

    # Permission Override Management
    async def create_permission_override(
        self,
        override: PermissionOverrideCreate
    ) -> PermissionOverride:
        """Create a permission override."""
        try:
            db_override = PermissionOverride(
                user_id=override.user_id,
                permission_id=override.permission_id,
                is_allowed=override.is_allowed,
                reason=override.reason,
                expires_at=override.expires_at
            )
            self.db.add(db_override)
            self.db.commit()
            self.db.refresh(db_override)
            return db_override
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating permission override: {str(e)}")
            raise

    async def update_permission_override(
        self,
        override_id: Union[str, int],
        override: PermissionOverrideUpdate
    ) -> PermissionOverride:
        """Update a permission override."""
        try:
            db_override = self.db.query(PermissionOverride).filter(PermissionOverride.id == override_id).first()
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
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating permission override: {str(e)}")
            raise

    async def delete_permission_override(self, override_id: Union[str, int]) -> None:
        """Delete a permission override."""
        try:
            db_override = self.db.query(PermissionOverride).filter(PermissionOverride.id == override_id).first()
            if not db_override:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Permission override not found"
                )
            self.db.delete(db_override)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting permission override: {str(e)}")
            raise

    # Access Control Checks
    async def check_permission(
        self,
        user_id: Union[str, int],
        resource_type: ResourceType,
        action: ActionType,
        resource_id: Optional[str] = None
    ) -> bool:
        """Check if a user has permission to perform an action on a resource."""
        try:
            # Get user's active roles
            roles = await self.get_user_roles(user_id)
            
            # Get all roles including inherited ones
            all_roles = set()
            for role in roles:
                all_roles.add(role.id)
                # Add inherited roles
                inherited_roles = await self._get_inherited_roles(role.id)
                all_roles.update(inherited_roles)
            
            # Check role-based permissions through RolePermission table
            for role_id in all_roles:
                role_permissions = self.db.query(Permission).join(
                    RolePermission, Permission.id == RolePermission.permission_id
                ).filter(RolePermission.role_id == role_id).all()
                
                for permission in role_permissions:
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
        except Exception as e:
            logger.error(f"Error checking permission: {str(e)}")
            return False

    async def _get_inherited_roles(self, role_id: Union[str, int]) -> set:
        """Get all inherited roles for a given role."""
        try:
            inherited_roles = set()
            visited = set()
            to_visit = [role_id]
            
            while to_visit:
                current_id = to_visit.pop(0)
                if current_id in visited:
                    continue
                visited.add(current_id)
                
                # Get all parent roles of current role
                parents = self.db.query(RoleHierarchy).filter(
                    RoleHierarchy.child_role_id == current_id
                ).all()
                
                for parent in parents:
                    inherited_roles.add(parent.parent_role_id)
                    to_visit.append(parent.parent_role_id)
            
            return inherited_roles
        except Exception as e:
            logger.error(f"Error getting inherited roles: {str(e)}")
            return set()

    async def get_effective_permissions(self, user_id: Union[str, int]) -> List[Permission]:
        """Get effective permissions for a user through role inheritance."""
        try:
            # Get user's direct roles
            user_roles = await self.get_user_roles(user_id)
            
            # Get all roles including inherited ones
            all_roles = set()
            for role in user_roles:
                all_roles.add(role.id)
                # Add inherited roles
                inherited_roles = await self._get_inherited_roles(role.id)
                all_roles.update(inherited_roles)
            
            # Get all permissions from user's roles
            effective_permissions = []
            for role_id in all_roles:
                role_permissions = self.db.query(Permission).join(
                    RolePermission, Permission.id == RolePermission.permission_id
                ).filter(RolePermission.role_id == role_id).all()
                
                effective_permissions.extend(role_permissions)
            
            return effective_permissions
        except Exception as e:
            logger.error(f"Error getting effective permissions: {str(e)}")
            raise

    async def update_role_hierarchy(self, hierarchy: RoleHierarchyCreate) -> Dict[str, List[str]]:
        """Update the role hierarchy."""
        try:
            parent_role = await self.get_role(hierarchy.parent_role_id)
            child_role = await self.get_role(hierarchy.child_role_id)
            
            if not parent_role or not child_role:
                raise ValueError("Parent or child role not found")

            # Check for circular dependency
            if await self._would_create_circular_dependency(parent_role.id, child_role.id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Creating this hierarchy would create a circular dependency"
                )

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

    async def _would_create_circular_dependency(self, parent_id: Union[str, int], child_id: Union[str, int]) -> bool:
        """Check if creating a hierarchy would create a circular dependency."""
        try:
            # Check if child is already a parent of the parent (direct or indirect)
            visited = set()
            to_visit = [child_id]
            
            while to_visit:
                current_id = to_visit.pop(0)
                if current_id in visited:
                    continue
                visited.add(current_id)
                
                # If we reach the parent, there's a circular dependency
                if current_id == parent_id:
                    return True
                
                # Get all children of current role
                children = self.db.query(RoleHierarchy).filter(
                    RoleHierarchy.parent_role_id == current_id
                ).all()
                
                for child in children:
                    to_visit.append(child.child_role_id)
            
            return False
        except Exception as e:
            logger.error(f"Error checking circular dependency: {str(e)}")
            return False

    async def update_role_hierarchy_simple(self, parent_role_id: Union[str, int], child_role_id: Union[str, int]) -> Dict[str, List[str]]:
        """Update the role hierarchy with individual parameters."""
        try:
            from app.dashboard.schemas.access_control import RoleHierarchyCreate
            
            hierarchy_data = RoleHierarchyCreate(
                parent_role_id=parent_role_id,
                child_role_id=child_role_id,
                is_active=True
            )
            return await self.update_role_hierarchy(hierarchy_data)
        except Exception as e:
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