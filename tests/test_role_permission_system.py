"""
Test Role and Permission System

This module tests the role and permission management implementation.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from app.schemas.role_management import RoleCreate, RoleUpdate, RoleAssignment
from app.schemas.permission_management import PermissionCreate, PermissionUpdate, PermissionCheck


class TestRoleManagementService:
    """Test role management service."""
    
    def test_get_role_by_id_nonexistent(self):
        """Test getting non-existent role by ID."""
        mock_db = Mock()
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_db.query.return_value = mock_query
        
        with patch('app.services.user.role_management_service.Role') as mock_role:
            from app.services.user.role_management_service import RoleManagementService
            
            service = RoleManagementService(mock_db)
            role = service.get_role_by_id(1)
            
            assert role is None
            mock_db.query.assert_called_once_with(mock_role)
    
    def test_create_role_success(self):
        """Test creating role successfully."""
        mock_db = Mock()
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_db.query.return_value = mock_query
        
        mock_role_instance = Mock()
        mock_role_instance.id = 1
        mock_role_instance.name = "test_role"
        mock_role_instance.description = "Test role"
        mock_role_instance.is_custom = True
        
        with patch('app.services.user.role_management_service.Role') as mock_role:
            mock_role.return_value = mock_role_instance
            
            from app.services.user.role_management_service import RoleManagementService
            
            service = RoleManagementService(mock_db)
            
            role_data = RoleCreate(
                name="test_role",
                description="Test role",
                is_custom=True
            )
            
            role = service.create_role(role_data)
            
            assert role.id == 1
            assert role.name == "test_role"
            assert role.description == "Test role"
            assert role.is_custom is True
            
            mock_db.add.assert_called_once_with(mock_role_instance)
            mock_db.commit.assert_called_once()
            mock_db.refresh.assert_called_once_with(mock_role_instance)
    
    def test_create_role_already_exists(self):
        """Test creating role when it already exists."""
        mock_existing_role = Mock()
        mock_db = Mock()
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_existing_role
        mock_db.query.return_value = mock_query
        
        with patch('app.services.user.role_management_service.Role'):
            from app.services.user.role_management_service import RoleManagementService
            
            service = RoleManagementService(mock_db)
            
            role_data = RoleCreate(
                name="existing_role",
                description="Existing role",
                is_custom=True
            )
            
            with pytest.raises(Exception):
                service.create_role(role_data)
    
    def test_assign_role_to_user_success(self):
        """Test assigning role to user successfully."""
        mock_user = Mock()
        mock_user.id = 1
        mock_user.roles = []
        
        mock_role = Mock()
        mock_role.name = "test_role"
        
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.side_effect = [mock_user, mock_role]
        
        with patch('app.services.user.role_management_service.Role'):
            from app.services.user.role_management_service import RoleManagementService
            
            service = RoleManagementService(mock_db)
            
            success = service.assign_role_to_user(1, "test_role")
            
            assert success is True
            # Check that the role was added to user's roles list
            assert mock_role in mock_user.roles
            mock_db.commit.assert_called_once()


class TestPermissionManagementService:
    """Test permission management service."""
    
    def test_get_permission_by_id_nonexistent(self):
        """Test getting non-existent permission by ID."""
        mock_db = Mock()
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_db.query.return_value = mock_query
        
        with patch('app.services.user.permission_management_service.Permission') as mock_permission:
            from app.services.user.permission_management_service import PermissionManagementService
            
            service = PermissionManagementService(mock_db)
            permission = service.get_permission_by_id(1)
            
            assert permission is None
            mock_db.query.assert_called_once_with(mock_permission)
    
    def test_create_permission_success(self):
        """Test creating permission successfully."""
        mock_db = Mock()
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_db.query.return_value = mock_query
        
        mock_permission_instance = Mock()
        mock_permission_instance.id = 1
        mock_permission_instance.name = "user_read"
        mock_permission_instance.resource_type = "user"
        mock_permission_instance.action = "read"
        
        with patch('app.services.user.permission_management_service.Permission') as mock_permission:
            mock_permission.return_value = mock_permission_instance
            
            from app.services.user.permission_management_service import PermissionManagementService
            
            service = PermissionManagementService(mock_db)
            
            permission_data = PermissionCreate(
                name="user_read",
                description="Read user data",
                resource_type="user",
                action="read"
            )
            
            permission = service.create_permission(permission_data)
            
            assert permission.id == 1
            assert permission.name == "user_read"
            assert permission.resource_type == "user"
            assert permission.action == "read"
            
            mock_db.add.assert_called_once_with(mock_permission_instance)
            mock_db.commit.assert_called_once()
            mock_db.refresh.assert_called_once_with(mock_permission_instance)
    
    def test_check_user_permission(self):
        """Test checking user permission."""
        # Create mock user with roles and permissions
        mock_user = Mock()
        mock_user.id = 1
        mock_user.role = "teacher"
        mock_user.is_superuser = False
        
        # Create mock role with permissions
        mock_role = Mock()
        mock_permission = Mock()
        mock_permission.name = "user_read"
        mock_role.permissions = [mock_permission]
        
        mock_user.roles = [mock_role]
        
        # Create mock primary role
        mock_primary_role = Mock()
        mock_primary_permission = Mock()
        mock_primary_permission.name = "user_read"
        mock_primary_role.permissions = [mock_primary_permission]
        
        # Mock the database to return user first, then primary role for each call
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            mock_user, mock_primary_role,  # First call to check_user_permission
            mock_user, mock_primary_role   # Second call to check_user_permission
        ]
        
        with patch('app.services.user.permission_management_service.Permission'):
            from app.services.user.permission_management_service import PermissionManagementService
            
            service = PermissionManagementService(mock_db)
            
            # Test that user has the permission
            has_permission = service.check_user_permission(1, "user_read")
            assert has_permission is True
            
            # Test that user doesn't have a different permission
            has_permission = service.check_user_permission(1, "user_write")
            assert has_permission is False


class TestRoleSchemas:
    """Test role schemas."""
    
    def test_role_create_schema(self):
        """Test RoleCreate schema."""
        role_data = RoleCreate(
            name="test_role",
            description="Test role description",
            is_custom=True
        )
        
        assert role_data.name == "test_role"
        assert role_data.description == "Test role description"
        assert role_data.is_custom is True
    
    def test_role_update_schema(self):
        """Test RoleUpdate schema."""
        role_data = RoleUpdate(
            name="updated_role",
            description="Updated description"
        )
        
        assert role_data.name == "updated_role"
        assert role_data.description == "Updated description"
        # is_custom is not in RoleUpdate schema, so it should not be accessible
        with pytest.raises(AttributeError):
            _ = role_data.is_custom
    
    def test_role_assignment_schema(self):
        """Test RoleAssignment schema."""
        assignment = RoleAssignment(
            user_id=1,
            role_name="teacher"
        )
        
        assert assignment.user_id == 1
        assert assignment.role_name == "teacher"


class TestPermissionSchemas:
    """Test permission schemas."""
    
    def test_permission_create_schema(self):
        """Test PermissionCreate schema."""
        permission_data = PermissionCreate(
            name="user_read",
            description="Read user data",
            resource_type="user",
            action="read"
        )
        
        assert permission_data.name == "user_read"
        assert permission_data.description == "Read user data"
        assert permission_data.resource_type == "user"
        assert permission_data.action == "read"
    
    def test_permission_update_schema(self):
        """Test PermissionUpdate schema."""
        permission_data = PermissionUpdate(
            name="user_write",
            description="Write user data"
        )
        
        assert permission_data.name == "user_write"
        assert permission_data.description == "Write user data"
        assert permission_data.resource_type is None  # Not set
    
    def test_permission_check_schema(self):
        """Test PermissionCheck schema."""
        check = PermissionCheck(
            user_id=1,
            permission_name="user_read"
        )
        
        assert check.user_id == 1
        assert check.permission_name == "user_read"


class TestRoleHierarchy:
    """Test role hierarchy functionality."""
    
    def test_role_hierarchy_levels(self):
        """Test role hierarchy levels."""
        mock_db = Mock()
        
        with patch('app.services.user.role_management_service.Role'):
            from app.services.user.role_management_service import RoleManagementService
            
            service = RoleManagementService(mock_db)
            
            # Test hierarchy levels
            assert service.role_hierarchy["super_admin"] == 100
            assert service.role_hierarchy["admin"] == 80
            assert service.role_hierarchy["teacher"] == 60
            assert service.role_hierarchy["student"] == 30
    
    def test_check_role_permission_hierarchy(self):
        """Test role permission checking with hierarchy."""
        mock_user = Mock()
        mock_user.id = 1
        mock_user.role = "admin"
        mock_user.roles = []
        mock_user.is_superuser = False
        
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        
        with patch('app.services.user.role_management_service.Role'):
            from app.services.user.role_management_service import RoleManagementService
            
            service = RoleManagementService(mock_db)
            
            # Admin should have permission for teacher-level access
            has_permission = service.check_role_permission(1, "teacher")
            assert has_permission is True
            
            # Admin should not have permission for super_admin-level access
            has_permission = service.check_role_permission(1, "super_admin")
            assert has_permission is False


class TestPermissionValidation:
    """Test permission validation."""
    
    def test_invalid_resource_type(self):
        """Test creating permission with invalid resource type."""
        mock_db = Mock()
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_db.query.return_value = mock_query
        
        with patch('app.services.user.permission_management_service.Permission'):
            from app.services.user.permission_management_service import PermissionManagementService
            
            service = PermissionManagementService(mock_db)
            
            permission_data = PermissionCreate(
                name="invalid_permission",
                description="Invalid permission",
                resource_type="invalid_resource",
                action="read"
            )
            
            with pytest.raises(Exception):
                service.create_permission(permission_data)
    
    def test_invalid_action(self):
        """Test creating permission with invalid action."""
        mock_db = Mock()
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_db.query.return_value = mock_query
        
        with patch('app.services.user.permission_management_service.Permission'):
            from app.services.user.permission_management_service import PermissionManagementService
            
            service = PermissionManagementService(mock_db)
            
            permission_data = PermissionCreate(
                name="invalid_permission",
                description="Invalid permission",
                resource_type="user",
                action="invalid_action"
            )
            
            with pytest.raises(Exception):
                service.create_permission(permission_data)


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 