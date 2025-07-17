import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.dashboard.services.access_control_service import AccessControlService
from app.dashboard.models.access_control import (
    Permission,
    Role,
    RoleAssignment,
    PermissionOverride,
    RoleHierarchy,
    ResourceType,
    ActionType
)

@pytest.fixture
def access_control_service(db: Session) -> AccessControlService:
    return AccessControlService(db)

@pytest.fixture
def test_permission(db: Session) -> Permission:
    permission = Permission(
        id="test_permission_id",
        name="test_permission",
        description="Test permission",
        resource_type=ResourceType.TOOL,
        action=ActionType.EXECUTE,
        scope="*",
        is_active=True
    )
    db.add(permission)
    db.commit()
    return permission

@pytest.fixture
def test_role(db: Session) -> Role:
    role = Role(
        id="test_role_id",
        name="test_role",
        description="Test role",
        is_system=False,
        is_template=False,
        is_active=True
    )
    db.add(role)
    db.commit()
    return role

@pytest.fixture
def test_role_assignment(db: Session, test_role: Role) -> RoleAssignment:
    assignment = RoleAssignment(
        id="test_assignment_id",
        user_id="test_user_id",
        role_id=test_role.id,
        assigned_by="system",
        is_active=True
    )
    db.add(assignment)
    db.commit()
    return assignment

class TestAccessControlService:
    async def test_create_permission(self, access_control_service: AccessControlService, db: Session):
        permission_data = {
            "name": "new_permission",
            "description": "New test permission",
            "resource_type": ResourceType.TOOL,
            "action": ActionType.EXECUTE,
            "scope": "*"
        }
        
        permission = await access_control_service.create_permission(**permission_data)
        
        assert permission.name == permission_data["name"]
        assert permission.resource_type == permission_data["resource_type"]
        assert permission.action == permission_data["action"]
        assert permission.is_active is True
        
        # Cleanup
        db.delete(permission)
        db.commit()
    
    async def test_get_permission(self, access_control_service: AccessControlService, test_permission: Permission):
        permission = await access_control_service.get_permission(test_permission.id)
        assert permission.id == test_permission.id
        assert permission.name == test_permission.name
    
    async def test_update_permission(self, access_control_service: AccessControlService, test_permission: Permission):
        update_data = {
            "description": "Updated description",
            "scope": "specific_scope"
        }
        
        updated_permission = await access_control_service.update_permission(
            test_permission.id,
            **update_data
        )
        
        assert updated_permission.description == update_data["description"]
        assert updated_permission.scope == update_data["scope"]
    
    async def test_delete_permission(self, access_control_service: AccessControlService, test_permission: Permission):
        await access_control_service.delete_permission(test_permission.id)
        
        with pytest.raises(HTTPException) as exc_info:
            await access_control_service.get_permission(test_permission.id)
        assert exc_info.value.status_code == 404
    
    async def test_create_role(self, access_control_service: AccessControlService, db: Session):
        role_data = {
            "name": "new_role",
            "description": "New test role",
            "is_system": False,
            "is_template": False
        }
        
        role = await access_control_service.create_role(**role_data)
        
        assert role.name == role_data["name"]
        assert role.description == role_data["description"]
        assert role.is_active is True
        
        # Cleanup
        db.delete(role)
        db.commit()
    
    async def test_assign_permission_to_role(
        self,
        access_control_service: AccessControlService,
        test_role: Role,
        test_permission: Permission
    ):
        await access_control_service.assign_permission_to_role(
            test_role.id,
            test_permission.id
        )
        
        role_permissions = await access_control_service.get_role_permissions(test_role.id)
        assert test_permission.id in [p.id for p in role_permissions]
    
    async def test_remove_permission_from_role(
        self,
        access_control_service: AccessControlService,
        test_role: Role,
        test_permission: Permission
    ):
        # First assign the permission
        await access_control_service.assign_permission_to_role(
            test_role.id,
            test_permission.id
        )
        
        # Then remove it
        await access_control_service.remove_permission_from_role(
            test_role.id,
            test_permission.id
        )
        
        role_permissions = await access_control_service.get_role_permissions(test_role.id)
        assert test_permission.id not in [p.id for p in role_permissions]
    
    async def test_assign_role_to_user(
        self,
        access_control_service: AccessControlService,
        test_role: Role
    ):
        user_id = "new_user_id"
        assigned_by = "system"
        
        assignment = await access_control_service.assign_role_to_user(
            user_id=user_id,
            role_id=test_role.id,
            assigned_by=assigned_by
        )
        
        assert assignment.user_id == user_id
        assert assignment.role_id == test_role.id
        assert assignment.assigned_by == assigned_by
        assert assignment.is_active is True
    
    async def test_revoke_role_assignment(
        self,
        access_control_service: AccessControlService,
        test_role_assignment: RoleAssignment
    ):
        await access_control_service.revoke_role_assignment(
            test_role_assignment.id
        )
        
        assignments = await access_control_service.get_user_roles(
            test_role_assignment.user_id
        )
        assert test_role_assignment.role_id not in [a.role_id for a in assignments]
    
    async def test_create_permission_override(
        self,
        access_control_service: AccessControlService,
        test_permission: Permission
    ):
        override_data = {
            "user_id": "test_user_id",
            "permission_id": test_permission.id,
            "is_allowed": True,
            "reason": "Test override",
            "expires_at": datetime.utcnow() + timedelta(days=1)
        }
        
        override = await access_control_service.create_permission_override(**override_data)
        
        assert override.user_id == override_data["user_id"]
        assert override.permission_id == override_data["permission_id"]
        assert override.is_allowed == override_data["is_allowed"]
        assert override.reason == override_data["reason"]
    
    async def test_check_permission(
        self,
        access_control_service: AccessControlService,
        test_role: Role,
        test_permission: Permission
    ):
        # Assign permission to role
        await access_control_service.assign_permission_to_role(
            test_role.id,
            test_permission.id
        )
        
        # Assign role to user
        user_id = "test_user"
        await access_control_service.assign_role_to_user(
            user_id=user_id,
            role_id=test_role.id,
            assigned_by="system"
        )
        
        # Check permission
        has_permission = await access_control_service.check_permission(
            user_id=user_id,
            resource_type=test_permission.resource_type,
            action=test_permission.action,
            resource_id="test_resource"
        )
        
        assert has_permission is True
    
    async def test_check_permission_with_override(
        self,
        access_control_service: AccessControlService,
        test_permission: Permission
    ):
        user_id = "test_user"
        
        # Create permission override
        await access_control_service.create_permission_override(
            user_id=user_id,
            permission_id=test_permission.id,
            is_allowed=False,
            reason="Test override"
        )
        
        # Check permission
        has_permission = await access_control_service.check_permission(
            user_id=user_id,
            resource_type=test_permission.resource_type,
            action=test_permission.action,
            resource_id="test_resource"
        )
        
        assert has_permission is False
    
    async def test_get_effective_permissions(
        self,
        access_control_service: AccessControlService,
        test_role: Role,
        test_permission: Permission
    ):
        # Assign permission to role
        await access_control_service.assign_permission_to_role(
            test_role.id,
            test_permission.id
        )
        
        # Assign role to user
        user_id = "test_user"
        await access_control_service.assign_role_to_user(
            user_id=user_id,
            role_id=test_role.id,
            assigned_by="system"
        )
        
        # Get effective permissions
        permissions = await access_control_service.get_effective_permissions(user_id)
        
        assert test_permission.id in [p.id for p in permissions]
    
    async def test_update_role_hierarchy(
        self,
        access_control_service: AccessControlService,
        test_role: Role
    ):
        child_role = Role(
            id="child_role_id",
            name="child_role",
            description="Child role",
            is_system=False,
            is_template=False,
            is_active=True
        )
        access_control_service.db.add(child_role)
        access_control_service.db.commit()
        
        await access_control_service.update_role_hierarchy(
            parent_role_id=test_role.id,
            child_role_id=child_role.id
        )
        
        hierarchy = await access_control_service.get_role_hierarchy()
        assert (test_role.id, child_role.id) in [(h.parent_role_id, h.child_role_id) for h in hierarchy]
    
    async def test_create_duplicate_permission(
        self,
        access_control_service: AccessControlService,
        test_permission: Permission
    ):
        duplicate_data = {
            "name": test_permission.name,  # Same name as existing permission
            "description": "Duplicate permission",
            "resource_type": ResourceType.TOOL,
            "action": ActionType.EXECUTE,
            "scope": "*"
        }
        
        with pytest.raises(HTTPException) as exc_info:
            await access_control_service.create_permission(**duplicate_data)
        assert exc_info.value.status_code == 409
    
    async def test_get_nonexistent_permission(self, access_control_service: AccessControlService):
        with pytest.raises(HTTPException) as exc_info:
            await access_control_service.get_permission("nonexistent_id")
        assert exc_info.value.status_code == 404
    
    async def test_expired_permission_override(
        self,
        access_control_service: AccessControlService,
        test_permission: Permission
    ):
        # Create an expired override
        override_data = {
            "user_id": "test_user_id",
            "permission_id": test_permission.id,
            "is_allowed": True,
            "reason": "Test override",
            "expires_at": datetime.utcnow() - timedelta(days=1)  # Expired
        }
        
        await access_control_service.create_permission_override(**override_data)
        
        # Check permission - should not be affected by expired override
        has_permission = await access_control_service.check_permission(
            user_id=override_data["user_id"],
            resource_type=test_permission.resource_type,
            action=test_permission.action,
            resource_id="test_resource"
        )
        
        assert has_permission is False
    
    async def test_circular_role_hierarchy(
        self,
        access_control_service: AccessControlService,
        test_role: Role
    ):
        # Create two more roles for testing circular dependency
        role2 = Role(
            id="role2_id",
            name="role2",
            description="Role 2",
            is_system=False,
            is_template=False,
            is_active=True
        )
        role3 = Role(
            id="role3_id",
            name="role3",
            description="Role 3",
            is_system=False,
            is_template=False,
            is_active=True
        )
        access_control_service.db.add_all([role2, role3])
        access_control_service.db.commit()
        
        # Create valid hierarchy: test_role -> role2 -> role3
        await access_control_service.update_role_hierarchy(
            parent_role_id=test_role.id,
            child_role_id=role2.id
        )
        await access_control_service.update_role_hierarchy(
            parent_role_id=role2.id,
            child_role_id=role3.id
        )
        
        # Attempt to create circular dependency: role3 -> test_role
        with pytest.raises(HTTPException) as exc_info:
            await access_control_service.update_role_hierarchy(
                parent_role_id=role3.id,
                child_role_id=test_role.id
            )
        assert exc_info.value.status_code == 400
    
    async def test_permission_inheritance(
        self,
        access_control_service: AccessControlService,
        test_role: Role,
        test_permission: Permission
    ):
        # Create child role
        child_role = Role(
            id="child_role_id",
            name="child_role",
            description="Child role",
            is_system=False,
            is_template=False,
            is_active=True
        )
        access_control_service.db.add(child_role)
        access_control_service.db.commit()
        
        # Set up hierarchy
        await access_control_service.update_role_hierarchy(
            parent_role_id=test_role.id,
            child_role_id=child_role.id
        )
        
        # Assign permission to parent role
        await access_control_service.assign_permission_to_role(
            test_role.id,
            test_permission.id
        )
        
        # Assign child role to user
        user_id = "test_user"
        await access_control_service.assign_role_to_user(
            user_id=user_id,
            role_id=child_role.id,
            assigned_by="system"
        )
        
        # User should have permission through inheritance
        has_permission = await access_control_service.check_permission(
            user_id=user_id,
            resource_type=test_permission.resource_type,
            action=test_permission.action,
            resource_id="test_resource"
        )
        
        assert has_permission is True
    
    async def test_multi_level_inheritance(
        self,
        access_control_service: AccessControlService,
        test_role: Role,
        test_permission: Permission
    ):
        # Create middle and bottom roles
        middle_role = Role(
            id="middle_role_id",
            name="middle_role",
            description="Middle role",
            is_system=False,
            is_template=False,
            is_active=True
        )
        bottom_role = Role(
            id="bottom_role_id",
            name="bottom_role",
            description="Bottom role",
            is_system=False,
            is_template=False,
            is_active=True
        )
        access_control_service.db.add_all([middle_role, bottom_role])
        access_control_service.db.commit()
        
        # Set up hierarchy: test_role -> middle_role -> bottom_role
        await access_control_service.update_role_hierarchy(
            parent_role_id=test_role.id,
            child_role_id=middle_role.id
        )
        await access_control_service.update_role_hierarchy(
            parent_role_id=middle_role.id,
            child_role_id=bottom_role.id
        )
        
        # Assign permission to top role
        await access_control_service.assign_permission_to_role(
            test_role.id,
            test_permission.id
        )
        
        # Assign bottom role to user
        user_id = "test_user"
        await access_control_service.assign_role_to_user(
            user_id=user_id,
            role_id=bottom_role.id,
            assigned_by="system"
        )
        
        # User should have permission through multi-level inheritance
        has_permission = await access_control_service.check_permission(
            user_id=user_id,
            resource_type=test_permission.resource_type,
            action=test_permission.action,
            resource_id="test_resource"
        )
        
        assert has_permission is True
        
        # Verify effective permissions include inherited ones
        effective_permissions = await access_control_service.get_effective_permissions(user_id)
        assert test_permission.id in [p.id for p in effective_permissions] 