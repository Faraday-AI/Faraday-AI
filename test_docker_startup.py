#!/usr/bin/env python3
"""
Test script to mimic Docker startup and isolate SQLAlchemy Session error.
"""

import sys
import os
import logging
from fastapi import FastAPI

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_docker_startup():
    """Test that mimics the exact Docker startup process."""
    print("=== Docker Startup Simulation Test ===")
    
    try:
        # Import the exact same modules as main.py
        print("Testing main.py imports...")
        
        # Test importing the main app module
        print("Importing main app module...")
        from app.main import app
        print("✓ Main app module imported successfully")
        
        # Test creating the FastAPI app instance
        print("Creating FastAPI app instance...")
        app_instance = app
        print("✓ FastAPI app instance created successfully")
        
        # Test that the app has the expected routers
        print("Checking app routers...")
        print(f"App title: {app_instance.title}")
        print(f"Number of routes: {len(app_instance.routes)}")
        print("✓ App routers loaded successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Error during Docker startup simulation: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_individual_imports():
    """Test importing individual modules that might cause issues."""
    print("\n=== Individual Module Import Test ===")
    
    modules_to_test = [
        "app.main",
        "app.api.v1.endpoints.auth",
        "app.api.v1.endpoints.memory", 
        "app.api.v1.endpoints.physical_education",
        "app.api.v1.endpoints.health_fitness",
        "app.api.v1.endpoints.ai_analysis",
        "app.api.v1.endpoints.activity_management",
        "app.api.v1.endpoints.math_assistant",
        "app.api.v1.endpoints.science_assistant",
        "app.api.v1.endpoints.health",
        "app.dashboard.api.v1.endpoints.notifications",
        "app.dashboard.api.v1.endpoints.access_control",
        "app.dashboard.api.v1.endpoints.resource_sharing",
        "app.dashboard.api.v1.endpoints.optimization_monitoring",
        "app.services.physical_education.student_service",
        "app.services.physical_education.safety_service",
        "app.services.physical_education.activity_service",
        "app.dashboard.dependencies.auth",
        "app.dashboard.dependencies"
    ]
    
    for module_name in modules_to_test:
        try:
            print(f"Testing import: {module_name}")
            __import__(module_name)
            print(f"✓ {module_name} imported successfully")
        except Exception as e:
            print(f"✗ {module_name} - Error: {e}")

if __name__ == "__main__":
    print("Starting Docker startup simulation...")
    
    # Test individual imports first
    test_individual_imports()
    
    # Test the full Docker startup process
    success = test_docker_startup()
    
    if success:
        print("\n🎉 Docker startup simulation completed successfully!")
    else:
        print("\n❌ Docker startup simulation failed!") 