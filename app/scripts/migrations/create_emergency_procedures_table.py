"""
Migration script to create emergency_procedures table.

This script creates the emergency_procedures table for Phase 1 implementation.
Run this script once to create the table in the database.

Usage:
    python -m app.scripts.migrations.create_emergency_procedures_table
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, project_root)

from app.core.config import settings

def create_emergency_procedures_table():
    """Create the emergency_procedures table if it doesn't exist."""
    db_url = os.getenv("DATABASE_URL") or settings.DATABASE_URL
    
    if not db_url:
        print("❌ ERROR: DATABASE_URL environment variable not set")
        return False
    
    engine = create_engine(db_url)
    conn = engine.connect()
    
    try:
        # Check if table already exists
        result = conn.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'emergency_procedures'
            )
        """))
        table_exists = result.scalar()
        
        if table_exists:
            print("✅ emergency_procedures table already exists")
            return True
        
        # Create the table
        conn.execute(text("""
            CREATE TABLE emergency_procedures (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                description TEXT NOT NULL,
                procedure_type VARCHAR(50) NOT NULL,
                class_id INTEGER REFERENCES physical_education_classes(id),
                steps JSONB NOT NULL,
                contact_info JSONB,
                is_active BOOLEAN DEFAULT TRUE,
                last_drill_date TIMESTAMP,
                next_drill_date TIMESTAMP,
                created_by INTEGER NOT NULL REFERENCES users(id),
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
        """))
        
        # Create indexes for better query performance
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_emergency_procedures_class_id 
            ON emergency_procedures(class_id)
        """))
        
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_emergency_procedures_created_by 
            ON emergency_procedures(created_by)
        """))
        
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_emergency_procedures_is_active 
            ON emergency_procedures(is_active)
        """))
        
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_emergency_procedures_procedure_type 
            ON emergency_procedures(procedure_type)
        """))
        
        conn.commit()
        print("✅ emergency_procedures table created successfully")
        print("✅ Indexes created successfully")
        return True
        
    except ProgrammingError as e:
        print(f"❌ ERROR creating table: {e}")
        conn.rollback()
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()
        engine.dispose()

if __name__ == "__main__":
    success = create_emergency_procedures_table()
    sys.exit(0 if success else 1)

