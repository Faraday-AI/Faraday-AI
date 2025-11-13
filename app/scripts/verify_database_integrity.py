"""
Verify Database Integrity

Checks that all tables exist and are populated (except jobs tables).
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.core.database import engine
from sqlalchemy import inspect, text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_database_integrity():
    """Verify database has all tables and data."""
    try:
        inspector = inspect(engine)
        all_tables = inspector.get_table_names()
        
        logger.info(f"Found {len(all_tables)} tables in database")
        
        # Expected table count
        expected_count = 545
        if len(all_tables) != expected_count:
            logger.warning(f"⚠️  Table count mismatch: Expected {expected_count}, found {len(all_tables)}")
        else:
            logger.info(f"✅ Table count correct: {len(all_tables)} tables")
        
        # Check which tables are empty
        empty_tables = []
        populated_tables = []
        jobs_tables = []
        
        with engine.connect() as conn:
            for table_name in sorted(all_tables):
                # Check if it's a jobs table
                is_jobs_table = 'job' in table_name.lower() or 'queue' in table_name.lower() or 'task' in table_name.lower()
                
                if is_jobs_table:
                    jobs_tables.append(table_name)
                    continue
                
                # Count rows
                try:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                    count = result.scalar()
                    
                    if count == 0:
                        empty_tables.append(table_name)
                    else:
                        populated_tables.append((table_name, count))
                except Exception as e:
                    logger.warning(f"⚠️  Could not check table {table_name}: {str(e)}")
                    empty_tables.append(table_name)
        
        # Summary
        logger.info("\n" + "="*80)
        logger.info("DATABASE INTEGRITY VERIFICATION SUMMARY")
        logger.info("="*80)
        logger.info(f"Total tables: {len(all_tables)}")
        logger.info(f"Populated tables (non-jobs): {len(populated_tables)}")
        logger.info(f"Empty tables (non-jobs): {len(empty_tables)}")
        logger.info(f"Jobs tables (excluded from check): {len(jobs_tables)}")
        
        if empty_tables:
            logger.warning(f"\n⚠️  Empty tables found ({len(empty_tables)}):")
            for table in empty_tables[:20]:  # Show first 20
                logger.warning(f"  - {table}")
            if len(empty_tables) > 20:
                logger.warning(f"  ... and {len(empty_tables) - 20} more")
        else:
            logger.info("\n✅ All non-jobs tables are populated!")
        
        if jobs_tables:
            logger.info(f"\n📋 Jobs tables (excluded from population check): {len(jobs_tables)}")
            for table in jobs_tables[:10]:  # Show first 10
                logger.info(f"  - {table}")
            if len(jobs_tables) > 10:
                logger.info(f"  ... and {len(jobs_tables) - 10} more")
        
        # Check some key tables
        logger.info("\n" + "="*80)
        logger.info("KEY TABLES VERIFICATION")
        logger.info("="*80)
        
        key_tables = [
            'users', 'activities', 'activity_logs', 'activity_plans',
            'teacher_registrations', 'microsoft_oauth_tokens', 'beta_microsoft_oauth_tokens'
        ]
        
        with engine.connect() as conn:
            for table_name in key_tables:
                if table_name in all_tables:
                    try:
                        result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                        count = result.scalar()
                        status = "✅" if count > 0 else "⚠️  EMPTY"
                        logger.info(f"{status} {table_name}: {count:,} records")
                    except Exception as e:
                        logger.warning(f"⚠️  {table_name}: Error - {str(e)}")
                else:
                    logger.warning(f"⚠️  {table_name}: Table not found")
        
        # Final status
        logger.info("\n" + "="*80)
        if len(empty_tables) == 0:
            logger.info("✅ DATABASE INTEGRITY VERIFICATION PASSED")
            logger.info("   All non-jobs tables are populated")
        else:
            logger.warning("⚠️  DATABASE INTEGRITY VERIFICATION: Some tables are empty")
            logger.warning(f"   {len(empty_tables)} empty tables found (excluding jobs tables)")
        
        logger.info("="*80)
        
        return len(empty_tables) == 0
        
    except Exception as e:
        logger.error(f"❌ Error verifying database: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = verify_database_integrity()
    sys.exit(0 if success else 1)

