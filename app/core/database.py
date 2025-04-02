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
    pool_size=10,  # Increased pool size for Pro plan
    max_overflow=20,  # Increased max overflow for Pro plan
    pool_timeout=120,  # Increased timeout for Pro plan
    pool_recycle=3600,  # Recycle connections after 1 hour
    connect_args={
        "connect_timeout": 60,  # Increased connection timeout
        "keepalives": 1,  # Enable TCP keepalive
        "keepalives_idle": 30,  # Time between keepalive packets
        "keepalives_interval": 10,  # Time between retries
        "keepalives_count": 5,  # Number of retries
        "sslmode": "require"  # Enable SSL for Azure PostgreSQL
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
    """Initialize database with retry logic and exponential backoff."""
    max_retries = 10  # Increased retries
    base_delay = 5  # Base delay in seconds
    max_delay = 60  # Maximum delay in seconds
    
    for attempt in range(max_retries):
        try:
            # Test connection with timeout
            with engine.connect() as conn:
                conn.execute("SELECT 1")
            
            # Create tables
            Base.metadata.create_all(bind=engine)
            logger.info("Database initialized successfully")
            return True
            
        except Exception as e:
            logger.warning(f"Database initialization attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                # Calculate delay with exponential backoff
                delay = min(base_delay * (2 ** attempt), max_delay)
                logger.info(f"Retrying in {delay} seconds...")
                await asyncio.sleep(delay)
            else:
                logger.error(f"Failed to initialize database after {max_retries} attempts: {str(e)}")
                if settings.DEBUG:
                    logger.warning("Running in debug mode - continuing with limited functionality")
                    return False
                raise 