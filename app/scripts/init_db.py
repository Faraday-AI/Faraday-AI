from sqlalchemy import create_engine, text
from app.core.config import get_settings
import logging

settings = get_settings()
logger = logging.getLogger(__name__)

def init_database():
    """Initialize database by dropping and recreating all tables."""
    try:
        # Create engine
        engine = create_engine(settings.DATABASE_URL)
        
        # Import all models to ensure they are registered
        from app.models.base import Base
        from app.models.subject import SubjectCategory, AssistantProfile, AssistantCapability
        from app.models.lesson import UserPreferences, Lesson
        from app.models.user import User
        from app.models.memory import UserMemory, MemoryInteraction
        
        # Drop all tables with CASCADE
        with engine.connect() as conn:
            conn.execute(text("DROP SCHEMA public CASCADE"))
            conn.execute(text("CREATE SCHEMA public"))
            conn.execute(text("GRANT ALL ON SCHEMA public TO postgres"))
            conn.execute(text("GRANT ALL ON SCHEMA public TO public"))
            conn.commit()
        
        logger.info("Dropped all existing tables and schema")
        
        # Create all tables
        Base.metadata.create_all(engine)
        logger.info("Created all tables successfully")
        
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise

if __name__ == "__main__":
    init_database() 