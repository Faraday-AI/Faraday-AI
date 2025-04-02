from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.models.base import Base
from app.core.config import get_settings
import logging
import asyncio
import time
from typing import Optional

# Configure logging
logger = logging.getLogger(__name__)

settings = get_settings()

# Create SQLAlchemy engine with increased timeouts and connection pooling
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Enable connection health checks
    pool_size=5,  # Maintain a pool of connections
    max_overflow=10,  # Allow up to 10 connections beyond pool_size
    pool_timeout=60,  # Increase pool timeout to 60 seconds
    pool_recycle=3600,  # Recycle connections after 1 hour
    connect_args={
        "connect_timeout": 30,  # Connection timeout in seconds
        "keepalives": 1,  # Enable TCP keepalive
        "keepalives_idle": 30,  # Time between keepalive packets
        "keepalives_interval": 10,  # Time between retries
        "keepalives_count": 5  # Number of retries
    }
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def init_db() -> bool:
    """Initialize database with retry logic."""
    max_retries = 3
    retry_delay = 5  # seconds
    
    for attempt in range(max_retries):
        try:
            # Test connection
            with engine.connect() as conn:
                conn.execute("SELECT 1")
            
            # Create tables
            Base.metadata.create_all(bind=engine)
            logger.info("Database initialized successfully")
            return True
            
        except Exception as e:
            logger.warning(f"Database initialization attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
            else:
                logger.error(f"Failed to initialize database after {max_retries} attempts: {str(e)}")
                if settings.DEBUG:
                    logger.warning("Running in debug mode - continuing with limited functionality")
                    return False
                raise 