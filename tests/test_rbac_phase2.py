"""
Test Phase 2: Enhanced Role and Permission Management

This module tests the enhanced RBAC system implemented in Phase 2.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.core.database import get_db
from app.core.security import Permission, UserRole, has_permission, require_permission
from app.models.core.user import User
from app.services.access_control_service import AccessControlService

client = TestClient(app)


class TestPhase2RBAC:
    """Test Phase 2 RBAC implementation."""
    
    def test_user_profile_permissions(self):
        """Test user profile permissions are properly defined."""
        # Test that user profile permissions exist
        assert Permission.VIEW_USER_PROFILES in Permission
        assert Permission.EDIT_USER_PROFILES in Permission
        assert Permission.CREATE_USER_PROFILES in Permission
        assert Permission.DELETE_USER_PROFILES in Permission
        assert Permission.UPLOAD_PROFILE_PICTURES in Permission
        assert Permission.REMOVE_PROFILE_PICTURES in Permission
    
    def test_user_preferences_permissions(self):
        """Test user preferences permissions are properly defined."""
        # Test that user preferences permissions exist
        assert Permission.VIEW_USER_PREFERENCES in Permission
        assert Permission.EDIT_USER_PREFERENCES in Permission
        assert Permission.RESET_USER_PREFERENCES in Permission
        assert Permission.EXPORT_USER_PREFERENCES in Permission
        assert Permission.IMPORT_USER_PREFERENCES in Permission
    
    def test_user_privacy_permissions(self):
        """Test user privacy permissions are properly defined."""
        # Test that user privacy permissions exist
        assert Permission.VIEW_USER_PRIVACY in Permission
        assert Permission.EDIT_USER_PRIVACY in Permission
        assert Permission.MANAGE_USER_PRIVACY in Permission
    
    def test_role_permission_mapping(self):
        """Test role-permission mapping includes new permissions."""
        # Test admin has all user permissions
        admin_permissions = [
            Permission.VIEW_USER_PROFILES,
            Permission.EDIT_USER_PROFILES,
            Permission.CREATE_USER_PROFILES,
            Permission.DELETE_USER_PROFILES,
            Permission.UPLOAD_PROFILE_PICTURES,
            Permission.REMOVE_PROFILE_PICTURES,
            Permission.VIEW_USER_PREFERENCES,
            Permission.EDIT_USER_PREFERENCES,
            Permission.RESET_USER_PREFERENCES,
            Permission.EXPORT_USER_PREFERENCES,
            Permission.IMPORT_USER_PREFERENCES,
            Permission.VIEW_USER_PRIVACY,
            Permission.EDIT_USER_PRIVACY,
            Permission.MANAGE_USER_PRIVACY
        ]
        
        for permission in admin_permissions:
            assert has_permission(UserRole.ADMIN, permission)
        
        # Test teacher has limited user permissions
        teacher_permissions = [
            Permission.VIEW_USER_PROFILES,
            Permission.EDIT_USER_PROFILES,
            Permission.VIEW_USER_PREFERENCES,
            Permission.EDIT_USER_PREFERENCES,
            Permission.VIEW_USER_PRIVACY
        ]
        
        for permission in teacher_permissions:
            assert has_permission(UserRole.TEACHER, permission)
        
        # Test student has basic user permissions
        student_permissions = [
            Permission.VIEW_USER_PROFILES,
            Permission.EDIT_USER_PROFILES,
            Permission.VIEW_USER_PREFERENCES,
            Permission.EDIT_USER_PREFERENCES,
            Permission.VIEW_USER_PRIVACY,
            Permission.EDIT_USER_PRIVACY
        ]
        
        for permission in student_permissions:
            assert has_permission(UserRole.STUDENT, permission)
    
    def test_permission_validation_functions(self):
        """Test permission validation functions work correctly."""
        # Test has_permission function
        assert has_permission(UserRole.ADMIN, Permission.VIEW_USER_PROFILES) == True
        assert has_permission(UserRole.STUDENT, Permission.DELETE_USER_PROFILES) == False
        assert has_permission(UserRole.TEACHER, Permission.VIEW_USER_PREFERENCES) == True
    
    def test_rbac_endpoints_exist(self):
        """Test that RBAC management endpoints are available."""
        # Test role management endpoints
        response = client.get("/api/v1/rbac-management/roles")
        # Should return 401 (unauthorized) or 403 (forbidden), not 404 (not found)
        assert response.status_code in [401, 403]
        
        # Test permission management endpoints
        response = client.get("/api/v1/rbac-management/permissions")
        assert response.status_code in [401, 403]
        
        # Test role assignment endpoints
        response = client.get("/api/v1/rbac-management/users/1/permissions")
        assert response.status_code in [401, 403]
    
    def test_user_profile_endpoints_with_rbac(self):
        """Test user profile endpoints have RBAC protection."""
        # Test profile endpoints require authentication and permissions
        response = client.get("/api/v1/user/profile")
        assert response.status_code in [401, 403]
        
        response = client.post("/api/v1/user/profile")
        assert response.status_code in [401, 403]
        
        response = client.put("/api/v1/user/profile")
        assert response.status_code in [401, 403]
    
    def test_user_preferences_endpoints_with_rbac(self):
        """Test user preferences endpoints have RBAC protection."""
        # Test preferences endpoints require authentication and permissions
        response = client.get("/api/v1/user/preferences")
        assert response.status_code in [401, 403]
        
        response = client.put("/api/v1/user/preferences")
        assert response.status_code in [401, 403]
        
        response = client.get("/api/v1/user/preferences/theme")
        assert response.status_code in [401, 403]


class TestRBACServiceIntegration:
    """Test RBAC service integration."""
    
    def test_access_control_service_exists(self):
        """Test that access control service is properly configured."""
        # This test verifies the service can be instantiated
        db = next(get_db())
        service = AccessControlService(db)
        assert service is not None
        db.close()
    
    def test_permission_check_functionality(self):
        """Test permission checking functionality."""
        # Test that permission checking works with different roles
        assert has_permission(UserRole.ADMIN, Permission.VIEW_USERS) == True
        assert has_permission(UserRole.STUDENT, Permission.VIEW_USERS) == False
        assert has_permission(UserRole.TEACHER, Permission.VIEW_COURSES) == True


class TestRBACMiddleware:
    """Test RBAC middleware functionality."""
    
    def test_require_permission_decorator(self):
        """Test require_permission decorator functionality."""
        # Test that require_permission returns a function
        permission_checker = require_permission(Permission.VIEW_USER_PROFILES)
        assert callable(permission_checker)
    
    def test_require_any_permission_decorator(self):
        """Test require_any_permission decorator functionality."""
        # Test that require_any_permission returns a function
        permission_checker = require_any_permission(
            Permission.VIEW_USER_PROFILES,
            Permission.EDIT_USER_PROFILES
        )
        assert callable(permission_checker)


class TestRBACSecurity:
    """Test RBAC security features."""
    
    def test_permission_enumeration(self):
        """Test that all permissions are properly enumerated."""
        # Test that all user-related permissions are in the enum
        user_permissions = [
            "VIEW_USER_PROFILES",
            "EDIT_USER_PROFILES", 
            "CREATE_USER_PROFILES",
            "DELETE_USER_PROFILES",
            "UPLOAD_PROFILE_PICTURES",
            "REMOVE_PROFILE_PICTURES",
            "VIEW_USER_PREFERENCES",
            "EDIT_USER_PREFERENCES",
            "RESET_USER_PREFERENCES",
            "EXPORT_USER_PREFERENCES",
            "IMPORT_USER_PREFERENCES",
            "VIEW_USER_PRIVACY",
            "EDIT_USER_PRIVACY",
            "MANAGE_USER_PRIVACY"
        ]
        
        for permission_name in user_permissions:
            assert hasattr(Permission, permission_name)
    
    def test_role_enumeration(self):
        """Test that all roles are properly enumerated."""
        # Test that all user roles are in the enum
        user_roles = [
            "SUPER_ADMIN",
            "ADMIN",
            "TEACHER", 
            "STUDENT",
            "PARENT",
            "STAFF"
        ]
        
        for role_name in user_roles:
            assert hasattr(UserRole, role_name)


if __name__ == "__main__":
    pytest.main([__file__]) 