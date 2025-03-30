from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.base import Base
from app.core.config import get_settings
import logging
import asyncio

settings = get_settings()
logger = logging.getLogger(__name__)

# Create database URL
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# Create SQLAlchemy engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800
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

async def init_db():
    """Initialize database tables."""
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
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        raise 