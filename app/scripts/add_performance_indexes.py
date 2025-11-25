#!/usr/bin/env python3
"""
Add database indexes for performance optimization.
Improves query speed for teacher lookups, class queries, and attendance patterns.
"""

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.database import SessionLocal
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def add_performance_indexes():
    """Add indexes for common query patterns."""
    db = SessionLocal()
    
    try:
        logger.info("="*80)
        logger.info("ADDING PERFORMANCE INDEXES")
        logger.info("="*80)
        
        indexes = [
            # User table indexes
            ("CREATE INDEX IF NOT EXISTS idx_users_email_lower ON users (LOWER(email))", "users.email (case-insensitive)"),
            ("CREATE INDEX IF NOT EXISTS idx_users_is_superuser ON users (is_superuser) WHERE is_superuser = FALSE", "users.is_superuser (non-admin filter)"),
            
            # TeacherRegistration indexes
            ("CREATE INDEX IF NOT EXISTS idx_teacher_reg_email_lower ON teacher_registrations (LOWER(email))", "teacher_registrations.email (case-insensitive)"),
            ("CREATE INDEX IF NOT EXISTS idx_teacher_reg_created_at ON teacher_registrations (created_at)", "teacher_registrations.created_at (sorting)"),
            
            # PhysicalEducationClass indexes
            ("CREATE INDEX IF NOT EXISTS idx_pe_classes_teacher_id ON physical_education_classes (teacher_id)", "physical_education_classes.teacher_id"),
            # Azure-compatible alternatives for text search (pg_trgm not available)
            # Standard B-tree indexes help with exact matches and prefix searches
            ("CREATE INDEX IF NOT EXISTS idx_pe_classes_name ON physical_education_classes (name)", "physical_education_classes.name (standard index)"),
            # For schedule field: use text pattern index (helps with LIKE queries)
            # Note: PostgreSQL can use this for prefix searches (schedule LIKE 'Period%')
            ("CREATE INDEX IF NOT EXISTS idx_pe_classes_schedule_text ON physical_education_classes (schedule text_pattern_ops)", "physical_education_classes.schedule (text pattern ops)"),
            # Also add a case-insensitive index for schedule (helps with ILIKE queries)
            ("CREATE INDEX IF NOT EXISTS idx_pe_classes_schedule_lower ON physical_education_classes (LOWER(schedule))", "physical_education_classes.schedule (case-insensitive)"),
            
            # Attendance indexes
            ("CREATE INDEX IF NOT EXISTS idx_attendance_student_id ON physical_education_attendance (student_id)", "physical_education_attendance.student_id"),
            ("CREATE INDEX IF NOT EXISTS idx_attendance_date ON physical_education_attendance (date)", "physical_education_attendance.date"),
            ("CREATE INDEX IF NOT EXISTS idx_attendance_student_date ON physical_education_attendance (student_id, date)", "physical_education_attendance (student_id, date composite)"),
        ]
        
        created_count = 0
        skipped_count = 0
        
        for index_sql, description in indexes:
            try:
                db.execute(text(index_sql))
                db.commit()
                logger.info(f"✅ Created index: {description}")
                created_count += 1
            except Exception as e:
                db.rollback()
                if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                    logger.info(f"⏭️  Index already exists: {description}")
                    skipped_count += 1
                else:
                    logger.warning(f"⚠️  Error creating index {description}: {e}")
        
        logger.info("\n" + "="*80)
        logger.info("INDEX CREATION SUMMARY")
        logger.info("="*80)
        logger.info(f"✅ Created: {created_count} indexes")
        logger.info(f"⏭️  Skipped: {skipped_count} (already exist)")
        logger.info(f"📊 Total: {len(indexes)} indexes")
        
        # Enable pg_trgm extension if needed (for text search indexes)
        try:
            db.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
            db.commit()
            logger.info("✅ Enabled pg_trgm extension for text search")
        except Exception as e:
            db.rollback()
            if "already exists" in str(e).lower():
                logger.info("⏭️  pg_trgm extension already exists")
            else:
                logger.warning(f"⚠️  Could not enable pg_trgm: {e}")
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    add_performance_indexes()

