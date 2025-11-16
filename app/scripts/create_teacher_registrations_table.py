"""
Create Teacher Registrations Table

This script creates the teacher_registrations table directly using SQLAlchemy.
Run this to ensure the table exists before using the registration service.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.core.database import engine
from app.models.teacher_registration import TeacherRegistration
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_table():
    """Create teacher_registrations table."""
    try:
        logger.info("Creating teacher_registrations table...")
        
        # Create table
        TeacherRegistration.__table__.create(engine, checkfirst=True)
        
        logger.info("✅ Successfully created teacher_registrations table")
        
        # Verify table exists
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        if 'teacher_registrations' in tables:
            logger.info("✅ Verified: teacher_registrations table exists")
        else:
            logger.error("❌ teacher_registrations table not found")
            
        logger.info("Teacher registrations table created successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error creating table: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = create_table()
    sys.exit(0 if success else 1)

