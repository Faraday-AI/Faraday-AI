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
        return "sqlite:///:memory:"
    elif os.getenv("CI") == "true":
        return "sqlite:///./test.db"
    else:
        # For local development, use the same database as development
        return os.getenv("DATABASE_URL", "sqlite:///:memory:")

@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """Set up test environment variables."""
    os.environ["TEST_MODE"] = "true"
    os.environ["SCHEMA"] = os.getenv("TEST_SCHEMA", "test_schema")
    os.environ["ENVIRONMENT"] = "test"
    
    # Set DATABASE_URL for tests if not already set
    if not os.getenv("DATABASE_URL"):
        os.environ["DATABASE_URL"] = get_test_db_url()
    
    yield
    
    # Cleanup
    if os.getenv("TEST_MODE") == "true" and os.getenv("DATABASE_URL", "").startswith("sqlite"):
        try:
            os.remove("./test.db")
        except:
            pass

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
    """Create and use test schema."""
    if not get_test_db_url().startswith("sqlite"):
        schema_name = os.getenv("TEST_SCHEMA", "test_schema")
        engine.execute(f"CREATE SCHEMA IF NOT EXISTS {schema_name}")
        engine.execute(f"SET search_path TO {schema_name}")
        yield schema_name
        engine.execute(f"DROP SCHEMA IF EXISTS {schema_name} CASCADE")
    else:
        yield None

@pytest.fixture(scope="session")
def tables(engine, test_schema):
    """Create all database tables."""
    if get_test_db_url().startswith("sqlite"):
        # Create all tables using SharedBase
        SharedBase.metadata.create_all(engine)
        yield
        # Drop all tables
        SharedBase.metadata.drop_all(engine)
    else:
        # For Azure, tables are managed through migrations
        yield

@pytest.fixture
def db_session(engine, tables, test_schema):
    """Create a new database session for a test."""
    connection = engine.connect()
    
    # Start transaction
    transaction = connection.begin()
    
    # Create session
    Session = sessionmaker(bind=connection)
    session = Session()
    
    if not get_test_db_url().startswith("sqlite"):
        # For Azure, use nested transactions
        session.begin_nested()
    
    yield session
    
    # Cleanup
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def sample_data(db_session):
    """Create sample data for testing."""
    # This will be implemented with specific test data
    pass

def pytest_configure(config):
    """Configure test environment."""
    pass

def pytest_unconfigure(config):
    """Cleanup after tests."""
    pass 