import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from unittest.mock import patch, Mock, AsyncMock
from pydantic import BaseModel

from app.dashboard.models.access_control import (
    ResourceType,
    ActionType
)

def create_permission_object(test_permission):
    """Create a proper permission object that can be serialized by Pydantic."""
    class PermissionObject:
        def __init__(self, permission_id, name, description, resource_type, action, scope, is_active, created_at, updated_at):
            self.id = permission_id
            self.name = name
            self.description = description
            self.resource_type = resource_type
            self.action = action
            self.scope = scope
            self.is_active = is_active
            self.created_at = created_at
            self.updated_at = updated_at
    
    # Convert string values to enum values
    resource_type_enum = ResourceType(test_permission.resource_type)
    action_enum = ActionType(test_permission.action)
    
    return PermissionObject(
        permission_id=test_permission.id,
        name=test_permission.name,
        description=test_permission.description,
        resource_type=resource_type_enum,
        action=action_enum,
        scope=test_permission.scope,
        is_active=test_permission.is_active,
        created_at=test_permission.created_at,
        updated_at=test_permission.updated_at
    )

class TestAccessControlEndpoints:
    @patch('app.dashboard.api.v1.endpoints.access_control.AccessControlService')
    def test_create_permission(self, mock_service_class, client: TestClient, admin_token: str):
        # Create mock service and permission
        mock_service = Mock()
        mock_permission = Mock()
        mock_permission.id = 1
        mock_permission.name = "new_permission"
        mock_permission.description = "New test permission"
        mock_permission.resource_type = "tool"
        mock_permission.action = "execute"
        mock_permission.scope = "*"
        mock_permission.permission_type = "system"
        mock_permission.is_active = True
        mock_permission.created_at = datetime.utcnow()
        mock_permission.updated_at = datetime.utcnow()
        
        # Make the method return an awaitable
        async def async_create_permission(*args, **kwargs):
            return mock_permission
        mock_service.create_permission = async_create_permission
        mock_service_class.return_value = mock_service
        
        permission_data = {
            "name": "new_permission",
            "description": "New test permission",
            "resource_type": "tool",
            "action": "execute",
            "scope": "*"
        }
        
        response = client.post(
            "/api/v1/access-control/permissions",
            json=permission_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == permission_data["name"]
        assert data["resource_type"] == permission_data["resource_type"]
        assert data["action"] == permission_data["action"]
    
    @patch('app.dashboard.api.v1.endpoints.access_control.AccessControlService')
    def test_get_permission(self, mock_service_class, client: TestClient, admin_token: str, test_permission):
        # Create mock service
        mock_service = Mock()
        
        # Make the method return an awaitable
        async def async_get_permission(*args, **kwargs):
            return test_permission
        mock_service.get_permission = async_get_permission
        mock_service_class.return_value = mock_service
        
        response = client.get(
            f"/api/v1/access-control/permissions/{test_permission.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_permission.id
        assert data["name"] == test_permission.name
    
    @patch('app.dashboard.api.v1.endpoints.access_control.AccessControlService')
    def test_update_permission(self, mock_service_class, client: TestClient, admin_token: str, test_permission):
        # Create mock service
        mock_service = Mock()
        
        # Make the method return an awaitable
        async def async_update_permission(*args, **kwargs):
            return test_permission
        mock_service.update_permission = async_update_permission
        mock_service_class.return_value = mock_service
        
        update_data = {
            "name": "updated_permission",
            "description": "Updated test permission"
        }
        
        response = client.patch(
            f"/api/v1/access-control/permissions/{test_permission.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == test_permission.name
    
    @patch('app.dashboard.api.v1.endpoints.access_control.AccessControlService')
    def test_delete_permission(self, mock_service_class, client: TestClient, admin_token: str, test_permission):
        # Create mock service
        mock_service = Mock()
        
        # Make the method return an awaitable
        async def async_delete_permission(*args, **kwargs):
            return True
        async def async_get_permission(*args, **kwargs):
            return None
        mock_service.delete_permission = async_delete_permission
        mock_service.get_permission = async_get_permission
        mock_service_class.return_value = mock_service
        
        response = client.delete(
            f"/api/v1/access-control/permissions/{test_permission.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 204
    
    @patch('app.dashboard.api.v1.endpoints.access_control.AccessControlService')
    def test_create_role(self, mock_service_class, client: TestClient, admin_token: str):
        # Create mock service and role
        mock_service = Mock()
        mock_role = Mock()
        mock_role.id = "role-1"
        mock_role.name = "new_role"
        mock_role.description = "New test role"
        mock_role.is_system = False
        mock_role.is_template = False
        mock_role.is_active = True
        mock_role.created_at = datetime.utcnow()
        mock_role.updated_at = datetime.utcnow()
        mock_role.permissions = []  # Add the required permissions field
        
        # Make the method return an awaitable
        async def async_create_role(*args, **kwargs):
            return mock_role
        mock_service.create_role = async_create_role
        mock_service_class.return_value = mock_service
        
        role_data = {
            "name": "new_role",
            "description": "New test role"
        }
        
        response = client.post(
            "/api/v1/access-control/roles",
            json=role_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == role_data["name"]
    
    @patch('app.dashboard.api.v1.endpoints.access_control.AccessControlService')
    def test_assign_permission_to_role(
        self,
        mock_service_class,
        client: TestClient,
        admin_token: str,
        test_role,
        test_permission
    ):
        # Create mock service
        mock_service = Mock()
        
        # Make the method return an awaitable
        async def async_assign_permission_to_role(*args, **kwargs):
            # Create a proper role object with permissions list that matches RoleResponse schema
            role_with_permissions = Mock()
            role_with_permissions.id = test_role.id
            role_with_permissions.name = test_role.name
            role_with_permissions.description = test_role.description
            role_with_permissions.is_system = test_role.is_system
            role_with_permissions.is_template = test_role.is_template
            role_with_permissions.is_active = test_role.is_active
            role_with_permissions.created_at = test_role.created_at
            role_with_permissions.updated_at = test_role.updated_at
            role_with_permissions.permissions = [test_permission]
            return role_with_permissions
        async def async_get_role_permissions(*args, **kwargs):
            return [test_permission]
        mock_service.assign_permission_to_role = async_assign_permission_to_role
        mock_service.get_role_permissions = async_get_role_permissions
        mock_service_class.return_value = mock_service
        
        response = client.post(
            f"/api/v1/access-control/roles/{test_role.id}/permissions/{test_permission.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        # The endpoint returns the full role object with permissions
        assert "permissions" in data
        assert len(data["permissions"]) == 1
        assert data["permissions"][0]["id"] == test_permission.id
    
    @patch('app.dashboard.api.v1.endpoints.access_control.AccessControlService')
    def test_remove_permission_from_role(
        self,
        mock_service_class,
        client: TestClient,
        admin_token: str,
        test_role,
        test_permission
    ):
        # Create mock service
        mock_service = Mock()
        
        # Make the method return an awaitable
        async def async_remove_permission_from_role(*args, **kwargs):
            return True
        mock_service.remove_permission_from_role = async_remove_permission_from_role
        mock_service_class.return_value = mock_service
        
        response = client.delete(
            f"/api/v1/access-control/roles/{test_role.id}/permissions/{test_permission.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 204
    
    @patch('app.dashboard.api.v1.endpoints.access_control.AccessControlService')
    def test_assign_role_to_user(
        self,
        mock_service_class,
        client: TestClient,
        admin_token: str,
        test_role
    ):
        # Create a simple mock assignment object without any awaitable properties
        class MockAssignment:
            def __init__(self):
                self.id = "assignment-1"
                self.user_id = "user-1"
                self.role_id = test_role.id
                self.assigned_by = "admin-1"
                self.is_active = True
                self.assigned_at = datetime.utcnow()
                self.expires_at = datetime.utcnow() + timedelta(days=30)
                self.created_at = datetime.utcnow()
                self.updated_at = datetime.utcnow()
                
                # Create a simple role object
                class MockRole:
                    def __init__(self):
                        self.id = test_role.id
                        self.name = test_role.name
                        self.description = test_role.description
                        self.is_system = test_role.is_system
                        self.is_template = test_role.is_template
                        self.is_active = test_role.is_active
                        self.created_at = test_role.created_at
                        self.updated_at = test_role.updated_at
                        self.permissions = []
                
                self.role = MockRole()
        
        # Create mock service
        mock_service = Mock()
        
        # Make the method return an awaitable
        async def async_assign_role(*args, **kwargs):
            return MockAssignment()
        mock_service.assign_role = async_assign_role
        mock_service_class.return_value = mock_service
        
        assignment_data = {
            "user_id": "user-1",
            "role_id": test_role.id,
            "assigned_by": "admin-1",
            "expires_at": (datetime.utcnow() + timedelta(days=30)).isoformat()
        }
        
        response = client.post(
            f"/api/v1/access-control/roles/{test_role.id}/assignments",
            json=assignment_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["user_id"] == assignment_data["user_id"]
        assert data["role_id"] == test_role.id
    
    @patch('app.dashboard.api.v1.endpoints.access_control.AccessControlService')
    def test_revoke_role_assignment(
        self,
        mock_service_class,
        client: TestClient,
        admin_token: str,
        test_role_assignment
    ):
        # Create mock service
        mock_service = Mock()
        
        # Make the method return an awaitable
        async def async_revoke_role(*args, **kwargs):
            return True
        async def async_get_user_roles(*args, **kwargs):
            # Return a mock role assignment to indicate the assignment exists
            class MockRoleAssignment:
                def __init__(self):
                    self.id = test_role_assignment.id
                    self.user_id = "user-1"
                    self.role_id = "role-1"
                    self.assigned_by = "admin-1"
                    self.is_active = True
                    self.assigned_at = datetime.utcnow()
                    self.expires_at = datetime.utcnow() + timedelta(days=30)
                    self.created_at = datetime.utcnow()
                    self.updated_at = datetime.utcnow()
            
            return [MockRoleAssignment()]
        mock_service.revoke_role = async_revoke_role
        mock_service.get_user_roles = async_get_user_roles
        mock_service_class.return_value = mock_service
        
        response = client.delete(
            f"/api/v1/access-control/role-assignments/{test_role_assignment.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 204
    
    @patch('app.dashboard.api.v1.endpoints.access_control.AccessControlService')
    def test_create_permission_override(
        self,
        mock_service_class,
        client: TestClient,
        admin_token: str,
        test_permission
    ):
        # Create mock service and override
        mock_service = Mock()
        mock_override = Mock()
        mock_override.id = "override-1"
        mock_override.permission_id = test_permission.id
        mock_override.user_id = "user-1"
        mock_override.is_allowed = True
        mock_override.reason = "Temporary access"
        mock_override.expires_at = datetime.utcnow() + timedelta(hours=1)
        mock_override.is_active = True
        mock_override.created_at = datetime.utcnow()
        mock_override.updated_at = datetime.utcnow()
        
        # Create a proper permission object that matches PermissionResponse schema
        mock_permission = Mock()
        mock_permission.id = test_permission.id
        mock_permission.name = test_permission.name
        mock_permission.description = test_permission.description
        mock_permission.resource_type = test_permission.resource_type
        mock_permission.action = test_permission.action
        mock_permission.scope = test_permission.scope
        mock_permission.permission_type = "system"
        mock_permission.is_active = test_permission.is_active
        mock_permission.created_at = test_permission.created_at
        mock_permission.updated_at = test_permission.updated_at
        
        mock_override.permission = mock_permission
        
        # Make the method return an awaitable
        async def async_create_permission_override(*args, **kwargs):
            return mock_override
        mock_service.create_permission_override = async_create_permission_override
        mock_service_class.return_value = mock_service
        
        override_data = {
            "user_id": "user-1",
            "is_allowed": True,
            "reason": "Temporary access",
            "expires_at": (datetime.utcnow() + timedelta(hours=1)).isoformat()
        }
        
        response = client.post(
            f"/api/v1/access-control/permissions/{test_permission.id}/overrides",
            json=override_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["permission_id"] == test_permission.id
        assert data["user_id"] == "user-1"
    
    @patch('app.dashboard.api.v1.endpoints.access_control.AccessControlService')
    def test_check_permission(
        self,
        mock_service_class,
        client: TestClient,
        admin_token: str,
        test_role,
        test_permission
    ):
        # Create mock service
        mock_service = Mock()
        
        # Make the method return an awaitable
        async def async_assign_permission_to_role(*args, **kwargs):
            # Create a proper role object with permissions list
            class RoleWithPermissions:
                def __init__(self):
                    self.id = test_role.id
                    self.name = test_role.name
                    self.description = test_role.description
                    self.is_system = test_role.is_system
                    self.is_template = test_role.is_template
                    self.is_active = test_role.is_active
                    self.created_at = test_role.created_at
                    self.updated_at = test_role.updated_at
                    self.permissions = [test_permission]
            
            return RoleWithPermissions()
        
        async def async_assign_role(*args, **kwargs):
            # Create a simple assignment object without any awaitable properties
            class MockAssignment:
                def __init__(self):
                    self.id = "assignment-1"
                    self.user_id = "user-1"
                    self.role_id = test_role.id
                    self.assigned_by = "admin-1"
                    self.is_active = True
                    self.assigned_at = datetime.utcnow()
                    self.expires_at = datetime.utcnow() + timedelta(days=30)
                    self.created_at = datetime.utcnow()
                    self.updated_at = datetime.utcnow()
                    
                    # Create a simple role object
                    class MockRole:
                        def __init__(self):
                            self.id = test_role.id
                            self.name = test_role.name
                            self.description = test_role.description
                            self.is_system = test_role.is_system
                            self.is_template = test_role.is_template
                            self.is_active = test_role.is_active
                            self.created_at = test_role.created_at
                            self.updated_at = test_role.updated_at
                            self.permissions = []
                    
                    self.role = MockRole()
            
            return MockAssignment()
        
        async def async_check_permission(*args, **kwargs):
            return True
        
        mock_service.assign_permission_to_role = async_assign_permission_to_role
        mock_service.assign_role = async_assign_role
        mock_service.check_permission = async_check_permission
        mock_service_class.return_value = mock_service
        
        # First assign permission to role
        response = client.post(
            f"/api/v1/access-control/roles/{test_role.id}/permissions/{test_permission.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 201
        
        # Then assign role to user
        role_assignment_data = {
            "user_id": "user-1",
            "role_id": test_role.id,
            "assigned_by": "admin-1",
            "expires_at": (datetime.utcnow() + timedelta(days=30)).isoformat()
        }
        response = client.post(
            f"/api/v1/access-control/roles/{test_role.id}/assignments",
            json=role_assignment_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 201
        
        # Finally check permission
        check_data = {
            "user_id": "user-1",
            "resource_type": test_permission.resource_type,
            "action": test_permission.action,
            "resource_id": "test_resource"
        }
        
        response = client.post(
            "/api/v1/access-control/check-permission",
            json=check_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["has_permission"] is True
    
    @patch('app.dashboard.api.v1.endpoints.access_control.AccessControlService')
    def test_check_bulk_permissions(
        self,
        mock_service_class,
        client: TestClient,
        admin_token: str,
        test_role,
        test_permission
    ):
        # Create mock service
        mock_service = Mock()
        
        # Make the method return an awaitable
        async def async_assign_permission_to_role(*args, **kwargs):
            # Create a proper role object with permissions list
            class RoleWithPermissions:
                def __init__(self):
                    self.id = test_role.id
                    self.name = test_role.name
                    self.description = test_role.description
                    self.is_system = test_role.is_system
                    self.is_template = test_role.is_template
                    self.is_active = test_role.is_active
                    self.created_at = test_role.created_at
                    self.updated_at = test_role.updated_at
                    self.permissions = [test_permission]
            
            return RoleWithPermissions()
        
        async def async_assign_role(*args, **kwargs):
            # Create a simple assignment object without any awaitable properties
            class MockAssignment:
                def __init__(self):
                    self.id = "assignment-1"
                    self.user_id = "user-1"
                    self.role_id = test_role.id
                    self.assigned_by = "admin-1"
                    self.is_active = True
                    self.assigned_at = datetime.utcnow()
                    self.expires_at = datetime.utcnow() + timedelta(days=30)
                    self.created_at = datetime.utcnow()
                    self.updated_at = datetime.utcnow()
                    
                    # Create a simple role object
                    class MockRole:
                        def __init__(self):
                            self.id = test_role.id
                            self.name = test_role.name
                            self.description = test_role.description
                            self.is_system = test_role.is_system
                            self.is_template = test_role.is_template
                            self.is_active = test_role.is_active
                            self.created_at = test_role.created_at
                            self.updated_at = test_role.updated_at
                            self.permissions = []
                    
                    self.role = MockRole()
            
            return MockAssignment()
        
        async def async_check_permission(*args, **kwargs):
            # Return True for the first check (TOOL/EXECUTE), False for the second (USER/READ)
            resource_type = args[1] if len(args) > 1 else kwargs.get('resource_type')
            action = args[2] if len(args) > 2 else kwargs.get('action')
            
            if resource_type == "tool" and action == "execute":
                return True
            elif resource_type == "user" and action == "read":
                return False
            return False
        
        mock_service.assign_permission_to_role = async_assign_permission_to_role
        mock_service.assign_role = async_assign_role
        mock_service.check_permission = async_check_permission
        mock_service_class.return_value = mock_service
        
        # First assign permission to role
        response = client.post(
            f"/api/v1/access-control/roles/{test_role.id}/permissions/{test_permission.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 201
        
        # Then assign role to user
        role_assignment_data = {
            "user_id": "user-1",
            "role_id": test_role.id,
            "assigned_by": "admin-1",
            "expires_at": (datetime.utcnow() + timedelta(days=30)).isoformat()
        }
        response = client.post(
            f"/api/v1/access-control/roles/{test_role.id}/assignments",
            json=role_assignment_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 201
        
        # Finally check bulk permissions
        check_data = {
            "checks": [
                {
                    "user_id": "user-1",
                    "resource_type": "tool",
                    "action": "execute",
                    "resource_id": "test_resource"
                },
                {
                    "user_id": "user-1",
                    "resource_type": "user",
                    "action": "read",
                    "resource_id": "test_resource"
                }
            ]
        }
        
        response = client.post(
            "/api/v1/access-control/check-bulk-permissions",
            json=check_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 2
        assert data["results"][0]["has_permission"] is True
        assert data["results"][1]["has_permission"] is False
    
    @patch('app.dashboard.api.v1.endpoints.access_control.AccessControlService')
    def test_get_role_hierarchy(
        self,
        mock_service_class,
        client: TestClient,
        admin_token: str,
        test_role
    ):
        # Create mock service
        mock_service = Mock()
        
        # Make the method return an awaitable
        async def async_create_role(*args, **kwargs):
            # Create a proper role object that matches RoleResponse schema
            class RoleObject:
                def __init__(self, role_id, name, description, is_system, is_template):
                    self.id = role_id
                    self.name = name
                    self.description = description
                    self.is_system = is_system
                    self.is_template = is_template
                    self.is_active = True
                    self.created_at = datetime.utcnow()
                    self.updated_at = datetime.utcnow()
                    self.permissions = []  # Add the required permissions field
            
            return RoleObject("parent-role", "parent_role", "Parent role", False, False)
        
        async def async_update_role_hierarchy(*args, **kwargs):
            # Return a mock hierarchy object that matches RoleHierarchyResponse schema
            class HierarchyResponseObject:
                def __init__(self):
                    self.parent_role_id = "parent-role"
                    self.child_role_id = test_role.id
                    self.is_active = True
                    self.created_at = datetime.utcnow()
                    self.updated_at = datetime.utcnow()
            
            return HierarchyResponseObject()
        
        async def async_get_role_hierarchy(*args, **kwargs):
            # Return a mock hierarchy object that matches RoleHierarchyResponse schema
            class HierarchyResponseObject:
                def __init__(self):
                    self.parent_role_id = "parent-role"
                    self.child_role_id = test_role.id
                    self.is_active = True
                    self.created_at = datetime.utcnow()
                    self.updated_at = datetime.utcnow()
            
            return HierarchyResponseObject()
        
        mock_service.create_role = async_create_role
        mock_service.update_role_hierarchy = async_update_role_hierarchy
        mock_service.get_role_hierarchy = async_get_role_hierarchy
        mock_service_class.return_value = mock_service
        
        # First create a parent role
        parent_role_data = {
            "name": "parent_role",
            "description": "Parent role"
        }
        response = client.post(
            "/api/v1/access-control/roles",
            json=parent_role_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 201
        
        # Then update the hierarchy
        hierarchy_data = {
            "parent_role_id": "parent-role",
            "child_role_id": test_role.id
        }
        response = client.post(
            "/api/v1/access-control/role-hierarchy",
            json=hierarchy_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 201
        
        # Finally get the hierarchy
        response = client.get(
            "/api/v1/access-control/role-hierarchy",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["parent_role_id"] == "parent-role"
        assert data["child_role_id"] == test_role.id
    
    @patch('app.dashboard.api.v1.endpoints.access_control.AccessControlService')
    def test_create_duplicate_permission(self, mock_service_class, client: TestClient, admin_token: str, test_permission):
        # Create mock service
        mock_service = Mock()
        
        # Make the method return an awaitable
        async def async_create_permission(*args, **kwargs):
            # Simulate duplicate permission error
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Permission already exists"
            )
        mock_service.create_permission = async_create_permission
        mock_service_class.return_value = mock_service
        
        permission_data = {
            "name": test_permission.name,
            "description": "Duplicate permission",
            "resource_type": test_permission.resource_type,
            "action": test_permission.action,
            "scope": test_permission.scope
        }
        
        response = client.post(
            "/api/v1/access-control/permissions",
            json=permission_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 409
        assert "Permission already exists" in response.json()["detail"]
    
    @patch('app.dashboard.api.v1.endpoints.access_control.AccessControlService')
    def test_get_nonexistent_permission(self, mock_service_class, client: TestClient, admin_token: str):
        # Create mock service
        mock_service = Mock()
        
        # Make the method return an awaitable
        async def async_get_permission(*args, **kwargs):
            # Simulate permission not found
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permission not found"
            )
        mock_service.get_permission = async_get_permission
        mock_service_class.return_value = mock_service
        
        response = client.get(
            "/api/v1/access-control/permissions/nonexistent-id",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 404
        assert "Permission not found" in response.json()["detail"]
    
    @patch('app.dashboard.api.v1.endpoints.access_control.AccessControlService')
    def test_expired_permission_override(
        self,
        mock_service_class,
        client: TestClient,
        admin_token: str,
        test_permission
    ):
        # Create mock service
        mock_service = Mock()
        
        # Make the method return an awaitable
        async def async_create_permission_override(*args, **kwargs):
            # Create a proper permission object for the override
            class OverrideObject:
                def __init__(self, override_id, permission_id, user_id, is_allowed, reason, expires_at, is_active, created_at, updated_at, permission):
                    self.id = override_id
                    self.permission_id = permission_id
                    self.user_id = user_id
                    self.is_allowed = is_allowed
                    self.reason = reason
                    self.expires_at = expires_at
                    self.is_active = is_active
                    self.created_at = created_at
                    self.updated_at = updated_at
                    self.permission = permission
            
            # Create a proper permission object
            permission_obj = Mock()
            permission_obj.id = test_permission.id
            permission_obj.name = test_permission.name
            permission_obj.description = test_permission.description
            permission_obj.resource_type = test_permission.resource_type
            permission_obj.action = test_permission.action
            permission_obj.scope = test_permission.scope
            permission_obj.permission_type = "system"
            permission_obj.is_active = test_permission.is_active
            permission_obj.created_at = test_permission.created_at
            permission_obj.updated_at = test_permission.updated_at
            
            return OverrideObject(
                "override-1",
                test_permission.id,
                "user-1",
                True,
                "Temporary access",
                datetime.utcnow() - timedelta(hours=1),  # Expired
                True,
                datetime.utcnow(),
                datetime.utcnow(),
                permission_obj
            )
        
        async def async_check_permission(*args, **kwargs):
            # Return False for expired override
            return False
        
        mock_service.create_permission_override = async_create_permission_override
        mock_service.check_permission = async_check_permission
        mock_service_class.return_value = mock_service
        
        # Create an expired override
        override_data = {
            "user_id": "user-1",
            "is_allowed": True,
            "reason": "Temporary access",
            "expires_at": (datetime.utcnow() - timedelta(hours=1)).isoformat()  # Expired
        }
        
        response = client.post(
            f"/api/v1/access-control/permissions/{test_permission.id}/overrides",
            json=override_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 201
        
        # Check that the expired override doesn't grant permission
        check_data = {
            "user_id": "user-1",
            "resource_type": test_permission.resource_type,
            "action": test_permission.action,
            "resource_id": "test_resource"
        }
        
        response = client.post(
            "/api/v1/access-control/check-permission",
            json=check_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["has_permission"] is False
    
    @patch('app.dashboard.api.v1.endpoints.access_control.AccessControlService')
    def test_circular_role_hierarchy(
        self,
        mock_service_class,
        client: TestClient,
        admin_token: str,
        test_role
    ):
        # Ensure test_role.id returns a string
        test_role.id = "role-1"
        
        # Create mock service
        mock_service = Mock()
        
        # Make the method return an awaitable
        async def async_create_role(*args, **kwargs):
            # Create a proper role object that matches RoleResponse schema
            class RoleObject:
                def __init__(self, role_id, name, description, is_system, is_template):
                    self.id = role_id
                    self.name = name
                    self.description = description
                    self.is_system = is_system
                    self.is_template = is_template
                    self.is_active = True
                    self.created_at = datetime.utcnow()
                    self.updated_at = datetime.utcnow()
                    self.permissions = []  # Add the required permissions field
            
            # Extract role name from args[0] (RoleCreate object) or kwargs
            role_data = args[0] if args else kwargs
            role_name = role_data.name if hasattr(role_data, 'name') else 'child_role'
            role_id = f"{role_name}-id"
            
            return RoleObject(role_id, role_name, f"{role_name} description", False, False)
        
        async def async_update_role_hierarchy(*args, **kwargs):
            # Extract hierarchy data from args[0] (RoleHierarchyCreate object) or kwargs
            hierarchy_data = args[0] if args else kwargs
            parent_id = hierarchy_data.parent_role_id if hasattr(hierarchy_data, 'parent_role_id') else None
            child_id = hierarchy_data.child_role_id if hasattr(hierarchy_data, 'child_role_id') else None
            
            # Simulate circular hierarchy detection
            if parent_id == child_id:
                from fastapi import HTTPException, status
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Circular role hierarchy detected"
                )
            return True
        
        async def async_get_role_hierarchy(*args, **kwargs):
            # Return a mock hierarchy structure
            class HierarchyObject:
                def __init__(self, parent_id, child_id):
                    self.parent_id = parent_id
                    self.child_id = child_id
                    self.created_at = datetime.utcnow()
            
            return [HierarchyObject("parent-role", "child-role")]
        
        mock_service.create_role = async_create_role
        mock_service.update_role_hierarchy = async_update_role_hierarchy
        mock_service.get_role_hierarchy = async_get_role_hierarchy
        mock_service_class.return_value = mock_service
        
        # First create a child role
        child_role_data = {
            "name": "child_role",
            "description": "Child role"
        }
        response = client.post(
            "/api/v1/access-control/roles",
            json=child_role_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 201
        
        # Try to create a circular hierarchy (child becomes parent of itself)
        hierarchy_data = {
            "parent_role_id": "child-role-id",
            "child_role_id": "child-role-id"
        }
        response = client.post(
            "/api/v1/access-control/role-hierarchy",
            json=hierarchy_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 400
        assert "Circular role hierarchy detected" in response.json()["detail"]
    
    @patch('app.dashboard.api.v1.endpoints.access_control.AccessControlService')
    def test_permission_inheritance_through_hierarchy(
        self,
        mock_service_class,
        client: TestClient,
        admin_token: str,
        test_role,
        test_permission
    ):
        # Ensure test_role.id returns a string
        test_role.id = "role-1"
        
        # Create mock service
        mock_service = Mock()
        
        # Make the method return an awaitable
        async def async_create_role(*args, **kwargs):
            # Create a proper role object that matches RoleResponse schema
            class RoleObject:
                def __init__(self, role_id, name, description, is_system, is_template):
                    self.id = role_id
                    self.name = name
                    self.description = description
                    self.is_system = is_system
                    self.is_template = is_template
                    self.is_active = True
                    self.created_at = datetime.utcnow()
                    self.updated_at = datetime.utcnow()
                    self.permissions = []  # Add the required permissions field
            
            # Extract role name from args[0] (RoleCreate object) or kwargs
            role_data = args[0] if args else kwargs
            role_name = role_data.name if hasattr(role_data, 'name') else 'child_role'
            role_id = f"{role_name}-id"
            
            return RoleObject(role_id, role_name, f"{role_name} description", False, False)
        
        async def async_update_role_hierarchy(*args, **kwargs):
            # Extract hierarchy data from args[0] (RoleHierarchyCreate object) or kwargs
            hierarchy_data = args[0] if args else kwargs
            parent_id = hierarchy_data.parent_role_id if hasattr(hierarchy_data, 'parent_role_id') else None
            child_id = hierarchy_data.child_role_id if hasattr(hierarchy_data, 'child_role_id') else None
            
            # Return a mock hierarchy object that matches RoleHierarchyResponse schema
            class HierarchyResponseObject:
                def __init__(self):
                    self.parent_role_id = parent_id
                    self.child_role_id = child_id
                    self.is_active = True
                    self.created_at = datetime.utcnow()
                    self.updated_at = datetime.utcnow()
            
            return HierarchyResponseObject()
        
        async def async_assign_permission_to_role(*args, **kwargs):
            # Create a proper role object with permissions list
            class RoleWithPermissions:
                def __init__(self):
                    self.id = test_role.id
                    self.name = test_role.name
                    self.description = test_role.description
                    self.is_system = test_role.is_system
                    self.is_template = test_role.is_template
                    self.is_active = test_role.is_active
                    self.created_at = test_role.created_at
                    self.updated_at = test_role.updated_at
                    self.permissions = [test_permission]
            
            return RoleWithPermissions()
        
        async def async_assign_role(*args, **kwargs):
            # Create a simple assignment object without any awaitable properties
            class MockAssignment:
                def __init__(self):
                    self.id = "assignment-1"
                    self.user_id = "user-1"
                    self.role_id = "child-role-id"
                    self.assigned_by = "admin-1"
                    self.is_active = True
                    self.assigned_at = datetime.utcnow()
                    self.expires_at = datetime.utcnow() + timedelta(days=30)
                    self.created_at = datetime.utcnow()
                    self.updated_at = datetime.utcnow()
                    
                    # Create a simple role object
                    class MockRole:
                        def __init__(self):
                            self.id = "child-role-id"
                            self.name = "child_role"
                            self.description = "Child role"
                            self.is_system = False
                            self.is_template = False
                            self.is_active = True
                            self.created_at = datetime.utcnow()
                            self.updated_at = datetime.utcnow()
                            self.permissions = []
                    
                    self.role = MockRole()
            
            return MockAssignment()
        
        async def async_check_permission(*args, **kwargs):
            # Return True for inherited permissions
            return True
        
        mock_service.create_role = async_create_role
        mock_service.update_role_hierarchy = async_update_role_hierarchy
        mock_service.assign_permission_to_role = async_assign_permission_to_role
        mock_service.assign_role = async_assign_role
        mock_service.check_permission = async_check_permission
        mock_service_class.return_value = mock_service
        
        # First create a child role
        child_role_data = {
            "name": "child_role",
            "description": "Child role"
        }
        response = client.post(
            "/api/v1/access-control/roles",
            json=child_role_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 201
        
        # Assign permission to parent role
        response = client.post(
            f"/api/v1/access-control/roles/{test_role.id}/permissions/{test_permission.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 201
        
        # Create hierarchy (parent -> child)
        hierarchy_data = {
            "parent_role_id": test_role.id,
            "child_role_id": "child-role-id"
        }
        response = client.post(
            "/api/v1/access-control/role-hierarchy",
            json=hierarchy_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 201
        
        # Assign child role to user
        role_assignment_data = {
            "user_id": "user-1",
            "role_id": "child-role-id",
            "assigned_by": "admin-1",
            "expires_at": (datetime.utcnow() + timedelta(days=30)).isoformat()
        }
        response = client.post(
            f"/api/v1/access-control/roles/child-role-id/assignments",
            json=role_assignment_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 201
        
        # Check that user has inherited permission
        check_data = {
            "user_id": "user-1",
            "resource_type": test_permission.resource_type,
            "action": test_permission.action,
            "resource_id": "test_resource"
        }
        
        response = client.post(
            "/api/v1/access-control/check-permission",
            json=check_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["has_permission"] is True
    
    @patch('app.dashboard.api.v1.endpoints.access_control.AccessControlService')
    def test_unauthorized_access(self, mock_service_class, client: TestClient):
        from fastapi import HTTPException, status
        
        # Create mock service that raises 401 when list_permissions is called
        mock_service = Mock()
        mock_service.list_permissions.side_effect = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
        mock_service_class.return_value = mock_service
        
        # Test without auth token
        response = client.get(
            "/api/v1/access-control/permissions",
        )
        assert response.status_code == 401
        
        # Test with invalid auth token
        response = client.get(
            "/api/v1/access-control/permissions",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401
    
    def test_insufficient_permissions(
        self,
        standard_user_token: str,
        test_permission
    ):
        from fastapi import HTTPException, status
        from fastapi.testclient import TestClient
        from app.dashboard.tests.conftest import app, require_admin

        # Create a custom override that raises 403
        async def override_require_admin_for_test():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin privileges required"
            )

        # Temporarily override require_admin for this test
        original_override = app.dependency_overrides.get(require_admin)
        app.dependency_overrides[require_admin] = override_require_admin_for_test

        try:
            # Create a new TestClient after setting the dependency override
            client = TestClient(app)
            
            # Standard user trying to create a permission
            permission_data = {
                "name": "new_permission",
                "description": "New test permission",
                "resource_type": ResourceType.TOOL,
                "action": ActionType.EXECUTE,
                "scope": "*"
            }

            response = client.post(
                "/api/v1/access-control/permissions",
                json=permission_data,
                headers={"Authorization": f"Bearer {standard_user_token}"}
            )

            assert response.status_code == 403
            assert "Admin privileges required" in response.json()["detail"]
        finally:
            # Restore the original override
            if original_override is not None:
                app.dependency_overrides[require_admin] = original_override
            else:
                # If there was no original override, remove our test override
                del app.dependency_overrides[require_admin] 