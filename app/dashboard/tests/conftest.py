"""
Test configuration for the dashboard tests.

This module provides test fixtures and configuration for running dashboard tests.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from fastapi import FastAPI

from app.dashboard.api.v1.endpoints import (
    analytics,
    compatibility,
    gpt_manager,
    resource_optimization
)
from app.dashboard.api.v1.endpoints.access_control import router as access_control_router
from app.dashboard.dependencies import get_current_user
from app.dashboard.dependencies import require_admin
from app.db.session import get_db

# Create FastAPI app for testing
app = FastAPI()

# Include routers
app.include_router(analytics.router, prefix="/api/v1/dashboard/analytics")
app.include_router(compatibility.router, prefix="/api/v1/dashboard/compatibility")
app.include_router(gpt_manager.router, prefix="/api/v1/dashboard/gpt-manager")
app.include_router(resource_optimization.router, prefix="/api/v1/dashboard/resource-optimization")
app.include_router(access_control_router, prefix="/api/v1")

# Debug: Print all routes
print("Available routes:")
for route in app.routes:
    if hasattr(route, 'path'):
        print(f"  {route.path}")

@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)

@pytest.fixture
def mock_db():
    """Create a mock database session."""
    return Mock()

@pytest.fixture
def db():
    """Create a real database session for service tests."""
    from app.db.session import SessionLocal
    from app.db.base_class import Base
    from app.models.shared_base import SharedBase
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    import os
    
    # Import all models to ensure they are registered with their respective metadata
    # This is necessary for foreign key relationships to work properly
    from app.models.core.user import User
    from app.models.security.access_control.access_control_management import (
        AccessControlRole, AccessControlPermission, UserRole, RoleHierarchy, RolePermission
    )
    from app.models.security.preferences.security_preferences_management import PermissionOverride
    
    # Use the same database configuration as the main app
    # For testing, we'll use an in-memory SQLite database to avoid affecting production data
    test_db_url = os.getenv("TEST_DATABASE_URL", "sqlite:///:memory:")
    
    if test_db_url == "sqlite:///:memory:":
        # Use in-memory SQLite for testing
        engine = create_engine(test_db_url)
        TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        # Create all tables from both metadata objects in the correct order
        # First create tables from SharedBase (which includes the users table)
        SharedBase.metadata.create_all(bind=engine)
        # Then create tables from Base (which includes access control tables that reference users)
        Base.metadata.create_all(bind=engine)
        
        # Create a session
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()
            # Drop tables in reverse order to avoid foreign key constraint issues
            # Drop Base tables first (access control tables that reference users)
            try:
                Base.metadata.drop_all(bind=engine)
            except Exception:
                pass  # Ignore foreign key constraint errors during teardown
            # Then drop SharedBase tables (users table)
            try:
                SharedBase.metadata.drop_all(bind=engine)
            except Exception:
                pass  # Ignore any remaining errors during teardown
    else:
        # Use the configured database (Azure PostgreSQL)
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()

@pytest.fixture
def admin_token():
    """Create a mock admin token."""
    return "admin_token_123"

@pytest.fixture
def standard_user_token():
    """Create a mock standard user token."""
    return "user_token_456"

@pytest.fixture
def test_permission():
    """Create a mock test permission."""
    class TestPermission:
        def __init__(self):
            self.id = "permission-1"
            self.name = "test_permission"
            self.description = "Test permission"
            self.resource_type = "tool"
            self.action = "execute"
            self.scope = "*"
            self.is_active = True
            self.created_at = datetime.utcnow()
            self.updated_at = datetime.utcnow()
    
    return TestPermission()

@pytest.fixture
def test_role():
    """Create a mock test role."""
    class TestRole:
        def __init__(self):
            self.id = "role-1"
            self.name = "test_role"
            self.description = "Test role"
            self.is_system = False
            self.is_template = False
            self.is_active = True
            self.created_at = datetime.utcnow()
            self.updated_at = datetime.utcnow()
    
    return TestRole()

@pytest.fixture
def test_role_assignment():
    """Create a mock test role assignment."""
    class TestRoleAssignment:
        def __init__(self):
            self.id = "assignment-1"
            self.user_id = "user-1"
            self.role_id = "role-1"
            self.assigned_by = "admin-1"
            self.is_active = True
            self.assigned_at = datetime.utcnow()
            self.expires_at = datetime.utcnow() + timedelta(days=30)
            self.created_at = datetime.utcnow()
            self.updated_at = datetime.utcnow()
    
    return TestRoleAssignment()

@pytest.fixture
def test_permission_override():
    """Create a mock test permission override."""
    class TestPermissionOverride:
        def __init__(self):
            self.id = "override-1"
            self.user_id = "user-1"
            self.permission_id = "permission-1"
            self.is_allowed = True
            self.is_active = True
            self.granted_by = "admin-1"
            self.granted_at = datetime.utcnow()
            self.expires_at = datetime.utcnow() + timedelta(hours=1)
            self.reason = "Temporary access"
            self.created_at = datetime.utcnow()
            self.updated_at = datetime.utcnow()
    
    return TestPermissionOverride()

def override_get_db():
    """Override database dependency."""
    return Mock()

def override_access_control_service():
    """Override access control service dependency."""
    mock_service = Mock()
    # Mock the create_permission method to return a mock permission
    mock_permission = Mock()
    mock_permission.id = "permission-1"
    mock_permission.name = "new_permission"
    mock_permission.description = "New test permission"
    mock_permission.resource_type = "tool"
    mock_permission.action = "execute"
    mock_permission.scope = "*"
    mock_permission.is_active = True
    mock_permission.created_at = datetime.utcnow()
    mock_permission.updated_at = datetime.utcnow()
    
    mock_service.create_permission = AsyncMock(return_value=mock_permission)
    mock_service.get_permission = AsyncMock(return_value=mock_permission)
    mock_service.update_permission = AsyncMock(return_value=mock_permission)
    mock_service.delete_permission = AsyncMock()
    mock_service.list_permissions = AsyncMock(return_value=[mock_permission])
    
    return mock_service

def override_get_current_user():
    """Override current user dependency."""
    return "user-1"

async def override_require_admin():
    """Override require_admin dependency to always return True (admin privileges)."""
    return True

# Override dependencies
app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user
app.dependency_overrides[require_admin] = override_require_admin 