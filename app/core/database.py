from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.models.base import Base
from app.core.config import get_settings
import logging
import asyncio
import time
from typing import Optional
from sqlalchemy.sql import text

# Configure logging
logger = logging.getLogger(__name__)

settings = get_settings()

# Create SQLAlchemy engine with increased timeouts and connection pooling
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Enable connection health checks
    pool_size=3,  # Reduced pool size to prevent connection exhaustion
    max_overflow=5,  # Reduced max overflow
    pool_timeout=300,  # Increased timeout to 5 minutes
    pool_recycle=900,  # Recycle connections after 15 minutes
    connect_args={
        "connect_timeout": 180,  # Increased connection timeout to 3 minutes
        "keepalives": 1,  # Enable TCP keepalive
        "keepalives_idle": 120,  # Increased time between keepalive packets
        "keepalives_interval": 60,  # Increased time between retries
        "keepalives_count": 15,  # Increased number of retries
        "sslmode": "require",  # Enable SSL for Azure PostgreSQL
        "application_name": "faraday_ai"  # Add application name for better monitoring
    }
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Get database session with retry logic."""
    max_retries = 3
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            db = SessionLocal()
            yield db
            break
        except Exception as e:
            if attempt < max_retries - 1:
                logger.warning(f"Database connection attempt {attempt + 1} failed: {str(e)}")
                time.sleep(retry_delay)
            else:
                logger.error(f"Failed to connect to database after {max_retries} attempts: {str(e)}")
                raise
        finally:
            try:
                db.close()
            except:
                pass

async def init_db() -> bool:
    """Initialize database with retry logic and exponential backoff."""
    max_retries = 20  # Increased retries
    base_delay = 5  # Reduced base delay to start retries faster
    max_delay = 120  # Maximum delay in seconds
    
    for attempt in range(max_retries):
        try:
            # Test connection with timeout
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))  # Fixed: Added text() wrapper
            
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