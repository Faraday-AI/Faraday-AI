"""
Database session management.
"""

import os
import threading
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool

from app.core.config import get_settings

settings = get_settings()

# Create SQLAlchemy engine with connection pooling
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,  # Recycle connections after 30 minutes
    pool_pre_ping=True  # Enable connection health checks
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)

# Context-local storage for test sessions (used in test mode)
# Import from app.core.database to use the SAME context variable instance
# This ensures both get_db() functions (from core.database and db.session) use the same test session
from app.core.database import _test_session_context

def set_test_session(session: Session):
    """Set the test session for use in test mode (called by test fixtures)."""
    # Use the same context variable as app.core.database
    _test_session_context.set(session)

def clear_test_session():
    """Clear the test session (called by test fixtures after test)."""
    # Use the same context variable as app.core.database
    _test_session_context.set(None)

def get_db() -> Generator[Session, None, None]:
    """
    Get a database session.
    
    In test mode (TEST_MODE=true), uses the test session from fixtures if available.
    Otherwise, creates a new session from SessionLocal.
    
    Uses thread-local storage to ensure each test thread has its own isolated session.
    
    Yields:
        Session: SQLAlchemy database session
    
    Example:
        >>> from app.db.session import get_db
        >>> db = next(get_db())
        >>> try:
        >>>     # Use the session
        >>>     result = db.query(Model).first()
        >>> finally:
        >>>     db.close()
    """
    # In test mode, use the test session if it's been set by test fixtures for this context
    if os.getenv("TEST_MODE") == "true":
        test_session = _test_session_context.get()
        if test_session is not None:
            yield test_session
            return
    
    # Normal operation: create a new session
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 