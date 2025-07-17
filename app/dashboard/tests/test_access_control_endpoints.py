import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta

from app.dashboard.models.access_control import (
    ResourceType,
    ActionType
)

class TestAccessControlEndpoints:
    def test_create_permission(self, client: TestClient, admin_token: str):
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
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == permission_data["name"]
        assert data["resource_type"] == permission_data["resource_type"]
        assert data["action"] == permission_data["action"]
    
    def test_get_permission(self, client: TestClient, admin_token: str, test_permission):
        response = client.get(
            f"/api/v1/access-control/permissions/{test_permission.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_permission.id
        assert data["name"] == test_permission.name
    
    def test_update_permission(self, client: TestClient, admin_token: str, test_permission):
        update_data = {
            "description": "Updated description",
            "scope": "specific_scope"
        }
        
        response = client.patch(
            f"/api/v1/access-control/permissions/{test_permission.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == update_data["description"]
        assert data["scope"] == update_data["scope"]
    
    def test_delete_permission(self, client: TestClient, admin_token: str, test_permission):
        response = client.delete(
            f"/api/v1/access-control/permissions/{test_permission.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 204
        
        # Verify deletion
        response = client.get(
            f"/api/v1/access-control/permissions/{test_permission.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 404
    
    def test_create_role(self, client: TestClient, admin_token: str):
        role_data = {
            "name": "new_role",
            "description": "New test role",
            "is_system": False,
            "is_template": False
        }
        
        response = client.post(
            "/api/v1/access-control/roles",
            json=role_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == role_data["name"]
        assert data["description"] == role_data["description"]
    
    def test_assign_permission_to_role(
        self,
        client: TestClient,
        admin_token: str,
        test_role,
        test_permission
    ):
        response = client.post(
            f"/api/v1/access-control/roles/{test_role.id}/permissions/{test_permission.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 201
        
        # Verify assignment
        response = client.get(
            f"/api/v1/access-control/roles/{test_role.id}/permissions",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        permissions = response.json()
        assert test_permission.id in [p["id"] for p in permissions]
    
    def test_remove_permission_from_role(
        self,
        client: TestClient,
        admin_token: str,
        test_role,
        test_permission
    ):
        # First assign the permission
        client.post(
            f"/api/v1/access-control/roles/{test_role.id}/permissions/{test_permission.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        # Then remove it
        response = client.delete(
            f"/api/v1/access-control/roles/{test_role.id}/permissions/{test_permission.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 204
        
        # Verify removal
        response = client.get(
            f"/api/v1/access-control/roles/{test_role.id}/permissions",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        permissions = response.json()
        assert test_permission.id not in [p["id"] for p in permissions]
    
    def test_assign_role_to_user(
        self,
        client: TestClient,
        admin_token: str,
        test_role
    ):
        assignment_data = {
            "user_id": "new_user_id",
            "assigned_by": "system"
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
        assert data["assigned_by"] == assignment_data["assigned_by"]
    
    def test_revoke_role_assignment(
        self,
        client: TestClient,
        admin_token: str,
        test_role_assignment
    ):
        response = client.delete(
            f"/api/v1/access-control/role-assignments/{test_role_assignment.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 204
        
        # Verify revocation
        response = client.get(
            f"/api/v1/access-control/users/{test_role_assignment.user_id}/roles",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        roles = response.json()
        assert test_role_assignment.role_id not in [r["id"] for r in roles]
    
    def test_create_permission_override(
        self,
        client: TestClient,
        admin_token: str,
        test_permission
    ):
        override_data = {
            "user_id": "test_user_id",
            "is_allowed": True,
            "reason": "Test override",
            "expires_at": (datetime.utcnow() + timedelta(days=1)).isoformat()
        }
        
        response = client.post(
            f"/api/v1/access-control/permissions/{test_permission.id}/overrides",
            json=override_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["user_id"] == override_data["user_id"]
        assert data["permission_id"] == test_permission.id
        assert data["is_allowed"] == override_data["is_allowed"]
    
    def test_check_permission(
        self,
        client: TestClient,
        admin_token: str,
        test_role,
        test_permission
    ):
        # First assign the permission to role and role to user
        client.post(
            f"/api/v1/access-control/roles/{test_role.id}/permissions/{test_permission.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        client.post(
            f"/api/v1/access-control/roles/{test_role.id}/assignments",
            json={"user_id": "test_user", "assigned_by": "system"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        # Then check permission
        check_data = {
            "user_id": "test_user",
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
    
    def test_check_bulk_permissions(
        self,
        client: TestClient,
        admin_token: str,
        test_role,
        test_permission
    ):
        # First assign the permission to role and role to user
        client.post(
            f"/api/v1/access-control/roles/{test_role.id}/permissions/{test_permission.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        client.post(
            f"/api/v1/access-control/roles/{test_role.id}/assignments",
            json={"user_id": "test_user", "assigned_by": "system"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        # Then check multiple permissions
        check_data = {
            "user_id": "test_user",
            "permissions": [
                {
                    "resource_type": test_permission.resource_type,
                    "action": test_permission.action,
                    "resource_id": "test_resource"
                },
                {
                    "resource_type": ResourceType.API,
                    "action": ActionType.EXECUTE,
                    "resource_id": "test_api"
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
        assert any(r["has_permission"] for r in data["results"])
    
    def test_get_role_hierarchy(
        self,
        client: TestClient,
        admin_token: str,
        test_role
    ):
        # First create a child role
        child_role_data = {
            "name": "child_role",
            "description": "Child role",
            "is_system": False,
            "is_template": False
        }
        
        response = client.post(
            "/api/v1/access-control/roles",
            json=child_role_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        child_role_id = response.json()["id"]
        
        # Then create the hierarchy
        hierarchy_data = {
            "parent_role_id": test_role.id,
            "child_role_id": child_role_id
        }
        
        response = client.post(
            "/api/v1/access-control/role-hierarchy",
            json=hierarchy_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 201
        
        # Get the hierarchy
        response = client.get(
            "/api/v1/access-control/role-hierarchy",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        hierarchy = response.json()
        assert any(
            h["parent_role_id"] == test_role.id and h["child_role_id"] == child_role_id
            for h in hierarchy
        )
    
    def test_create_duplicate_permission(self, client: TestClient, admin_token: str, test_permission):
        permission_data = {
            "name": test_permission.name,  # Same name as existing permission
            "description": "Duplicate permission",
            "resource_type": ResourceType.TOOL,
            "action": ActionType.EXECUTE,
            "scope": "*"
        }
        
        response = client.post(
            "/api/v1/access-control/permissions",
            json=permission_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 409
    
    def test_get_nonexistent_permission(self, client: TestClient, admin_token: str):
        response = client.get(
            "/api/v1/access-control/permissions/nonexistent_id",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 404
    
    def test_expired_permission_override(
        self,
        client: TestClient,
        admin_token: str,
        test_permission
    ):
        # Create an expired override
        override_data = {
            "user_id": "test_user_id",
            "is_allowed": True,
            "reason": "Test override",
            "expires_at": (datetime.utcnow() - timedelta(days=1)).isoformat()  # Expired
        }
        
        response = client.post(
            f"/api/v1/access-control/permissions/{test_permission.id}/overrides",
            json=override_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 201
        
        # Check permission - should not be affected by expired override
        check_data = {
            "user_id": override_data["user_id"],
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
    
    def test_circular_role_hierarchy(
        self,
        client: TestClient,
        admin_token: str,
        test_role
    ):
        # Create two more roles
        role2_data = {
            "name": "role2",
            "description": "Role 2",
            "is_system": False,
            "is_template": False
        }
        
        role3_data = {
            "name": "role3",
            "description": "Role 3",
            "is_system": False,
            "is_template": False
        }
        
        response = client.post(
            "/api/v1/access-control/roles",
            json=role2_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        role2_id = response.json()["id"]
        
        response = client.post(
            "/api/v1/access-control/roles",
            json=role3_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        role3_id = response.json()["id"]
        
        # Create valid hierarchy: test_role -> role2 -> role3
        client.post(
            "/api/v1/access-control/role-hierarchy",
            json={"parent_role_id": test_role.id, "child_role_id": role2_id},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        client.post(
            "/api/v1/access-control/role-hierarchy",
            json={"parent_role_id": role2_id, "child_role_id": role3_id},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        # Attempt to create circular dependency: role3 -> test_role
        response = client.post(
            "/api/v1/access-control/role-hierarchy",
            json={"parent_role_id": role3_id, "child_role_id": test_role.id},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 400
    
    def test_permission_inheritance_through_hierarchy(
        self,
        client: TestClient,
        admin_token: str,
        test_role,
        test_permission
    ):
        # Create child role
        child_role_data = {
            "name": "child_role",
            "description": "Child role",
            "is_system": False,
            "is_template": False
        }
        
        response = client.post(
            "/api/v1/access-control/roles",
            json=child_role_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        child_role_id = response.json()["id"]
        
        # Set up hierarchy
        client.post(
            "/api/v1/access-control/role-hierarchy",
            json={"parent_role_id": test_role.id, "child_role_id": child_role_id},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        # Assign permission to parent role
        client.post(
            f"/api/v1/access-control/roles/{test_role.id}/permissions/{test_permission.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        # Assign child role to user
        client.post(
            f"/api/v1/access-control/roles/{child_role_id}/assignments",
            json={"user_id": "test_user", "assigned_by": "system"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        # Check permission through inheritance
        check_data = {
            "user_id": "test_user",
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
    
    def test_unauthorized_access(self, client: TestClient):
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
        client: TestClient,
        standard_user_token: str,  # Assuming this fixture exists
        test_permission
    ):
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