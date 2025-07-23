#!/usr/bin/env python3
"""
Targeted test to isolate SQLAlchemy Session error.
"""

import sys
import os
import logging
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_fastapi_startup():
    """Test FastAPI startup with minimal configuration."""
    print("=== Testing FastAPI Startup ===")
    
    try:
        # Create minimal FastAPI app
        app = FastAPI(title="Test App")
        
        # Test basic endpoint
        @app.get("/test")
        def test_endpoint():
            return {"message": "test"}
        
        print("✓ Basic FastAPI app created successfully")
        
        # Test with database dependency
        from app.db.session import get_db
        
        @app.get("/test-db")
        def test_db_endpoint(db: Session = Depends(get_db)):
            return {"message": "db test"}
        
        print("✓ FastAPI app with DB dependency created successfully")
        
        # Test importing main app
        print("Testing main app import...")
        from app.main import app as main_app
        print("✓ Main app imported successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_service_imports():
    """Test importing individual services that might cause issues."""
    print("\n=== Testing Service Imports ===")
    
    services_to_test = [
        "app.services.physical_education.student_service",
        "app.services.physical_education.safety_service", 
        "app.services.physical_education.activity_service",
        "app.dashboard.dependencies.auth",
        "app.dashboard.dependencies",
        "app.services.ai.enhanced_assistant_service",
        "app.services.content.content_management_service"
    ]
    
    for service_name in services_to_test:
        try:
            print(f"Testing import: {service_name}")
            __import__(service_name)
            print(f"✓ {service_name} imported successfully")
        except Exception as e:
            print(f"✗ {service_name} - Error: {e}")

def test_dependency_functions():
    """Test dependency functions that might cause issues."""
    print("\n=== Testing Dependency Functions ===")
    
    try:
        # Test get_db function
        from app.db.session import get_db
        print("✓ get_db function imported successfully")
        
        # Test service getter functions
        from app.main import get_pe_service, get_resource_sharing_service
        print("✓ Service getter functions imported successfully")
        
        # Test dashboard dependencies
        from app.dashboard.dependencies import get_current_user
        print("✓ Dashboard dependencies imported successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing dependency functions: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Starting targeted SQLAlchemy Session error test...")
    
    # Test service imports first
    test_service_imports()
    
    # Test dependency functions
    test_dependency_functions()
    
    # Test FastAPI startup
    success = test_fastapi_startup()
    
    if success:
        print("\n🎉 All tests passed!")
    else:
        print("\n❌ Tests failed!") 