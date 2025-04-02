from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.base import Base
from app.core.config import get_settings
import logging
import asyncio
import time
from typing import Optional

settings = get_settings()
logger = logging.getLogger(__name__)

# Create database URL
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# Create SQLAlchemy engine with longer timeouts
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_timeout=60,  # Increased from 30
    pool_recycle=1800,
    connect_args={
        "connect_timeout": 30,  # 30 seconds connection timeout
    }
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def init_db(max_retries: int = 3, retry_delay: int = 5) -> bool:
    """Initialize database tables with retry logic."""
    for attempt in range(max_retries):
        try:
            # Import all models here to ensure they are registered
            from app.models.subject import SubjectCategory, AssistantProfile, AssistantCapability
            from app.models.lesson import UserPreferences, Lesson
            from app.models.user import User
            from app.models.memory import UserMemory, MemoryInteraction
            
            # Create all tables
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, Base.metadata.create_all, engine)
            logger.info("Database tables created successfully")
            return True
        except Exception as e:
            if attempt < max_retries - 1:
                logger.warning(f"Database initialization attempt {attempt + 1} failed: {str(e)}")
                logger.info(f"Retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
            else:
                logger.error(f"Failed to initialize database after {max_retries} attempts: {str(e)}")
                if settings.DEBUG:
                    logger.warning("Running in debug mode - continuing without database")
                    return True
                return False
    return False 