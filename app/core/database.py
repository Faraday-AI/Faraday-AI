"""
Database Module

This module provides database configuration and models for the Faraday AI Dashboard.
"""

from sqlalchemy import create_engine, MetaData, text, inspect
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import QueuePool
from sqlalchemy.schema import CreateTable
from typing import Generator
import os
import time
import fcntl
import tempfile

# Create base declarative base
Base = declarative_base()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/faraday")

def get_region_db_url(region: str) -> str:
    """Get database URL for a specific region."""
    base_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/faraday")
    if region and region != "default":
        # Modify the URL to include region-specific database
        if "postgresql://" in base_url:
            # Extract components and modify database name
            parts = base_url.split("/")
            if len(parts) >= 4:
                db_name = parts[-1]
                new_db_name = f"{db_name}_{region}"
                parts[-1] = new_db_name
                return "/".join(parts)
    return base_url

# Create SQLAlchemy engine with connection pooling and SSL configuration
engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False
    } if DATABASE_URL.startswith("sqlite") else {
        "sslmode": "require",  # Always require SSL for security
        "application_name": "faraday-ai"  # Add application name for better monitoring
    },
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
    pool_pre_ping=True  # Enable connection health checks
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Initialize engines dictionary for regional failover
engines = {}
async_engines = {}

def get_session_factory():
    """Get the session factory."""
    return SessionLocal

def acquire_db_lock():
    """Acquire a file-based lock to prevent multiple database initializations."""
    lock_file = os.path.join(tempfile.gettempdir(), "faraday_db_init.lock")
    
    # Use a more reliable locking mechanism
    try:
        # Create the lock file if it doesn't exist
        with open(lock_file, 'w') as f:
            f.write(str(os.getpid()))
        
        # Try to acquire an exclusive lock with timeout
        lock_fd = open(lock_file, 'r+')
        fcntl.flock(lock_fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        
        # Check if another process has already initialized the database
        try:
            with open(lock_file, 'r') as f:
                content = f.read().strip()
                if content and content != str(os.getpid()):
                    # Another process is handling initialization
                    fcntl.flock(lock_fd.fileno(), fcntl.LOCK_UN)
                    lock_fd.close()
                    return None
        except (IOError, ValueError):
            pass
        
        return lock_fd
    except (IOError, OSError) as e:
        # Lock is held by another process or file doesn't exist
        print(f"Database initialization already in progress by another process, skipping... (Error: {e})")
        return None

def release_db_lock(lock_fd):
    """Release the database initialization lock."""
    if lock_fd:
        fcntl.flock(lock_fd.fileno(), fcntl.LOCK_UN)
        lock_fd.close()

def initialize_engines():
    """Initialize database engines and create tables."""
    # Check if we should skip initialization (for worker processes)
    if os.environ.get('SKIP_DB_INIT') == 'true':
        print("Database initialization skipped for worker process")
        return
    
    # Try to acquire the database initialization lock
    lock_fd = acquire_db_lock()
    if not lock_fd:
        print("Database initialization already in progress by another process, skipping...")
        return
    
    try:
        # Set environment variable to prevent other workers from initializing
        os.environ['SKIP_DB_INIT'] = 'true'
        
        # Import models here to avoid circular imports
        from app.models.shared_base import SharedBase
        
        # Import all models to ensure they are registered with SharedBase metadata
        import app.models
        
        # Create a new metadata instance
        metadata = MetaData()
        
        # Drop and recreate all enum types first
        if not DATABASE_URL.startswith("sqlite"):
            # Create enums in separate transactions to avoid cascading failures
            enum_creation_queries = [
                "CREATE TYPE analysis_type_enum AS ENUM ('movement', 'performance', 'progress', 'safety', 'technique', 'engagement', 'adaptation', 'assessment')",
                "CREATE TYPE metric_type_enum AS ENUM ('speed', 'accuracy', 'power', 'endurance', 'flexibility', 'balance', 'coordination')",
                "CREATE TYPE activity_type_enum AS ENUM ('running', 'jumping', 'throwing', 'catching', 'kicking', 'striking', 'dribbling', 'passing', 'shooting', 'defending')",
                "CREATE TYPE difficulty_level_enum AS ENUM ('beginner', 'intermediate', 'advanced', 'expert')",
                "CREATE TYPE feedback_type_enum AS ENUM ('movement', 'performance', 'progress', 'safety', 'technique', 'engagement', 'adaptation', 'assessment')",
                "CREATE TYPE feedback_severity_enum AS ENUM ('excellent', 'good', 'satisfactory', 'needs_improvement', 'poor')",
                "CREATE TYPE sequence_type_enum AS ENUM ('strength', 'cardio', 'flexibility', 'balance', 'coordination', 'endurance', 'speed', 'agility')",
                "CREATE TYPE base_status_enum AS ENUM ('active', 'inactive', 'pending', 'in_progress', 'completed', 'cancelled', 'on_hold', 'archived')",
                "CREATE TYPE skilllevel AS ENUM ('beginner', 'intermediate', 'advanced', 'expert')",
                "CREATE TYPE performancelevel AS ENUM ('excellent', 'good', 'satisfactory', 'needs_improvement', 'poor')",
                "CREATE TYPE confidencelevel AS ENUM ('high', 'medium', 'low', 'uncertain')",
                "CREATE TYPE risklevel AS ENUM ('low', 'medium', 'high', 'critical')",
                "CREATE TYPE analysistype AS ENUM ('movement', 'performance', 'progress', 'safety', 'technique', 'engagement', 'adaptation', 'assessment')",
                "CREATE TYPE analysislevel AS ENUM ('basic', 'standard', 'detailed', 'comprehensive', 'expert')",
                "CREATE TYPE analysisstatus AS ENUM ('pending', 'in_progress', 'completed', 'failed', 'cancelled')",
                "CREATE TYPE analysistrigger AS ENUM ('manual', 'scheduled', 'performance', 'progress', 'safety', 'adaptation', 'system')",
                "CREATE TYPE preferenceactivitytype AS ENUM ('WARM_UP', 'SKILL_DEVELOPMENT', 'FITNESS_TRAINING', 'GAME', 'COOL_DOWN')"
            ]
            
            for query in enum_creation_queries:
                try:
                    with engine.connect() as conn:
                        conn.execute(text(query))
                        conn.commit()
                except Exception as e:
                    if "already exists" not in str(e).lower():
                        print(f"Error creating enum: {e}")
                    # Continue with other enums even if one fails
        
        # Create tables using a simpler approach that handles foreign key issues
        try:
            inspector = inspect(engine)
            existing_tables = inspector.get_table_names()
            
            # Get all tables that need to be created
            tables_to_create = []
            for table_name, table_obj in SharedBase.metadata.tables.items():
                if table_name not in existing_tables:
                    tables_to_create.append((table_name, table_obj))
            
            # Create tables in multiple passes to handle dependencies
            max_passes = 10  # Prevent infinite loops
            pass_count = 0
            
            while tables_to_create and pass_count < max_passes:
                pass_count += 1
                created_this_pass = []
                
                for table_name, table_obj in tables_to_create[:]:  # Copy list to avoid modification during iteration
                    try:
                        print(f"Creating table: {table_name}")
                        table_obj.create(bind=engine, checkfirst=True)
                        created_this_pass.append(table_name)
                        tables_to_create.remove((table_name, table_obj))
                    except Exception as e:
                        error_msg = str(e).lower()
                        if "already exists" in error_msg or "relation" in error_msg:
                            print(f"Table {table_name} already exists, skipping...")
                            created_this_pass.append(table_name)
                            tables_to_create.remove((table_name, table_obj))
                        elif "foreign key" in error_msg or "referenced table" in error_msg:
                            # Skip tables with foreign key issues for now, they'll be retried in next pass
                            print(f"Table {table_name} has dependency issues, will retry in next pass...")
                            continue
                        else:
                            print(f"Error creating table {table_name}: {e}")
                            # Continue with other tables instead of failing completely
                            continue
                
                if not created_this_pass:
                    # If no tables were created this pass, we might have circular dependencies
                    print(f"No tables created in pass {pass_count}, attempting to create remaining tables...")
                    for table_name, table_obj in tables_to_create:
                        try:
                            print(f"Attempting to create table: {table_name}")
                            table_obj.create(bind=engine, checkfirst=True)
                        except Exception as e:
                            print(f"Failed to create {table_name}: {e}")
                            # Continue with other tables
                            continue
                    break
            
            if tables_to_create:
                print(f"Warning: {len(tables_to_create)} tables could not be created: {[t[0] for t in tables_to_create]}")
                        
        except Exception as e:
            if "already exists" in str(e):
                # If the error is about existing objects, we can safely ignore it
                pass
            else:
                # For other errors, we should raise them
                raise
        
        # Verify all tables were created
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"Created tables: {tables}")
        
    finally:
        # Always release the lock
        release_db_lock(lock_fd)

async def init_db() -> bool:
    """Initialize the database with required data.
    
    Returns:
        bool: True if initialization was successful, False otherwise
    """
    try:
        # Initialize database engines first
        initialize_engines()
        
        # Create a test connection to verify database is working
        with engine.connect() as conn:
            # Test query
            conn.execute(text("SELECT 1"))
            
        return True
    except Exception as e:
        print(f"Error initializing database: {e}")
        return False

def get_db() -> Generator[Session, None, None]:
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Export session factory
__all__ = ['Base', 'engine', 'SessionLocal', 'get_db', 'initialize_engines', 'init_db'] 