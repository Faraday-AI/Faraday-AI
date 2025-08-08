"""
Test configuration for the physical education models.

This module provides test fixtures and configuration for running model tests.
"""

import os
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from app.models.shared_base import SharedBase

def get_test_db_url():
    """Get database URL based on environment."""
    if os.getenv("TEST_MODE") == "true":
        # Use Azure database for tests
        return os.getenv("DATABASE_URL", "sqlite:///:memory:")
    elif os.getenv("CI") == "true":
        return "sqlite:///./test.db"
    else:
        # For local development, use the same database as development
        return os.getenv("DATABASE_URL", "sqlite:///:memory:")

@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """Set up test environment variables."""
    # Force set environment variables for all tests
    os.environ["TEST_MODE"] = "true"
    os.environ["SCHEMA"] = os.getenv("TEST_SCHEMA", "test_schema")
    os.environ["ENVIRONMENT"] = "test"
    os.environ["LOG_LEVEL"] = "DEBUG"
    os.environ["REDIS_URL"] = "redis://redis:6379/0"
    
    # Set DATABASE_URL for tests if not already set
    if not os.getenv("DATABASE_URL"):
        os.environ["DATABASE_URL"] = get_test_db_url()
    
    # Verify environment is set correctly
    assert os.getenv("TEST_MODE") == "true", "TEST_MODE must be set to 'true'"
    assert os.getenv("DATABASE_URL") is not None, "DATABASE_URL must be set"
    
    yield
    
    # Cleanup
    if os.getenv("TEST_MODE") == "true" and os.getenv("DATABASE_URL", "").startswith("sqlite"):
        try:
            os.remove("./test.db")
        except:
            pass

# Model relationships are now handled with full module paths - no dynamic setup needed

@pytest.fixture(scope="session")
def engine():
    """Create a test database engine."""
    db_url = get_test_db_url()
    if db_url.startswith("sqlite"):
        return create_engine(db_url)
    else:
        # Azure-specific configuration
        return create_engine(
            db_url,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=1800
        )

@pytest.fixture(scope="session")
def test_schema(engine):
    """Use existing schema for Azure PostgreSQL."""
    if not get_test_db_url().startswith("sqlite"):
        # For Azure, use the existing schema (public)
        yield "public"
    else:
        yield None

@pytest.fixture(scope="session")
def tables(engine, test_schema):
    """Use existing tables for Azure PostgreSQL."""
    # For Azure, tables are already created and seeded
    # No need to create/drop tables
    yield

@pytest.fixture
def db_session(engine, tables, test_schema):
    """Create a new database session for a test."""
    connection = engine.connect()
    
    # Set the search path to use the test schema for PostgreSQL
    if test_schema:
        connection.execute(text(f"SET search_path TO {test_schema}, public"))
        connection.commit()
    
    # Create session
    Session = sessionmaker(bind=connection)
    session = Session()
    
    yield session
    
    # Cleanup
    session.close()
    connection.close()

@pytest.fixture
def sample_data(db_session):
    """Create sample data for testing."""
    # This will be implemented with specific test data
    pass

def pytest_configure(config):
    """Configure pytest and ensure environment variables are set."""
    # Ensure environment variables are set at the very beginning
    os.environ["TEST_MODE"] = "true"
    os.environ["SCHEMA"] = os.getenv("TEST_SCHEMA", "test_schema")
    os.environ["ENVIRONMENT"] = "test"
    os.environ["LOG_LEVEL"] = "DEBUG"
    os.environ["REDIS_URL"] = "redis://redis:6379/0"
    
    # Set DATABASE_URL for tests if not already set
    if not os.getenv("DATABASE_URL"):
        os.environ["DATABASE_URL"] = get_test_db_url()
    
    # Verify environment is set correctly
    assert os.getenv("TEST_MODE") == "true", "TEST_MODE must be set to 'true'"
    assert os.getenv("DATABASE_URL") is not None, "DATABASE_URL must be set"

def pytest_unconfigure(config):
    """Cleanup after tests."""
    pass 