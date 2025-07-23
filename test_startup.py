#!/usr/bin/env python3
"""
Test script to isolate SQLAlchemy Session error during FastAPI startup.
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

def test_minimal_app():
    """Test with minimal FastAPI app to see if the error persists."""
    print("Testing minimal FastAPI app...")
    
    app = FastAPI(title="Test App")
    
    @app.get("/test")
    def test_endpoint():
        return {"message": "test"}
    
    print("✓ Minimal app created successfully")
    return app

def test_with_db_dependency():
    """Test with database dependency to see if that causes the error."""
    print("\nTesting with database dependency...")
    
    app = FastAPI(title="Test App with DB")
    
    # Mock database dependency
    def get_db():
        return None  # Mock session
    
    @app.get("/test")
    def test_endpoint(db: Session = Depends(get_db)):
        return {"message": "test with db"}
    
    print("✓ App with DB dependency created successfully")
    return app

def test_import_routers():
    """Test importing routers one by one to find the problematic one."""
    print("\nTesting router imports...")
    
    routers_to_test = [
        ("auth", "app.api.auth"),
        ("memory", "app.api.v1.endpoints.core.memory"),
        ("physical_education", "app.api.v1.endpoints.physical_education"),
        ("health_fitness", "app.api.v1.endpoints.physical_education.health_fitness"),
        ("ai_analysis", "app.api.v1.endpoints.management.ai_analysis"),
        ("activity_management", "app.api.v1.endpoints.management.activity_management"),
        ("math_assistant", "app.api.v1.endpoints.assistants.math_assistant"),
        ("science_assistant", "app.api.v1.endpoints.assistants.science_assistant"),
        ("health", "app.core.health"),
        ("dashboard", "app.dashboard.api.v1.endpoints.dashboard"),
        ("analytics", "app.dashboard.api.v1.endpoints.analytics"),
        ("compatibility", "app.dashboard.api.v1.endpoints.compatibility"),
        ("gpt_context", "app.dashboard.api.v1.endpoints.gpt_context"),
        ("gpt_manager", "app.dashboard.api.v1.endpoints.gpt_manager"),
        ("resource_optimization", "app.dashboard.api.v1.endpoints.resource_optimization"),
        ("access_control", "app.dashboard.api.v1.endpoints.access_control"),
        ("resource_sharing", "app.dashboard.api.v1.endpoints.resource_sharing"),
        ("optimization_monitoring", "app.dashboard.api.v1.endpoints.optimization_monitoring"),
        ("notifications", "app.dashboard.api.v1.endpoints.notifications"),
        ("educational", "app.api.v1.endpoints.educational"),
    ]
    
    for router_name, module_path in routers_to_test:
        try:
            print(f"Testing import: {router_name}")
            module = __import__(module_path, fromlist=['router'])
            router = getattr(module, 'router', None)
            if router:
                print(f"✓ {router_name} imported successfully")
            else:
                print(f"⚠ {router_name} - no router found")
        except Exception as e:
            print(f"✗ {router_name} - Error: {str(e)}")
            if "sqlalchemy.orm.session.Session" in str(e):
                print(f"  → This router has the SQLAlchemy Session issue!")
                return router_name, module_path
        except ImportError as e:
            print(f"✗ {router_name} - ImportError: {str(e)}")
    
    return None, None

def test_service_dependencies():
    """Test service dependency functions to find the problematic one."""
    print("\nTesting service dependencies...")
    
    services_to_test = [
        ("get_pe_service", "app.main"),
        ("get_gpt_manager_service", "app.main"),
        ("get_resource_sharing_service", "app.main"),
        ("get_realtime_collaboration_service", "app.main"),
        ("get_file_processing_service", "app.main"),
        ("get_ai_analytics_service", "app.main"),
    ]
    
    for service_name, module_path in services_to_test:
        try:
            print(f"Testing service: {service_name}")
            module = __import__(module_path, fromlist=[service_name])
            service_func = getattr(module, service_name, None)
            if service_func:
                # Try to call the function
                result = service_func()
                print(f"✓ {service_name} called successfully")
            else:
                print(f"⚠ {service_name} - function not found")
        except Exception as e:
            print(f"✗ {service_name} - Error: {str(e)}")
            if "sqlalchemy.orm.session.Session" in str(e):
                print(f"  → This service has the SQLAlchemy Session issue!")
                return service_name, module_path
    
    return None, None

if __name__ == "__main__":
    print("=== FastAPI Startup Error Isolation Test ===\n")
    
    # Test 1: Minimal app
    test_minimal_app()
    
    # Test 2: App with DB dependency
    test_with_db_dependency()
    
    # Test 3: Router imports
    problematic_router, router_path = test_import_routers()
    
    # Test 4: Service dependencies
    problematic_service, service_path = test_service_dependencies()
    
    print("\n=== Test Results ===")
    if problematic_router:
        print(f"Problematic router: {problematic_router} in {router_path}")
    if problematic_service:
        print(f"Problematic service: {problematic_service} in {service_path}")
    
    if not problematic_router and not problematic_service:
        print("No obvious issues found in isolated tests.")
        print("The error might be in the main app startup or router registration.") 