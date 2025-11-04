#!/usr/bin/env python3
"""
Compare Metadata Tables vs Database Tables
Identify missing tables
"""
import os
import sys
from sqlalchemy import create_engine, text

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.core.database import DATABASE_URL
from app.models.shared_base import SharedBase

def compare_tables():
    """Compare metadata tables with database tables."""
    
    # Get tables from metadata
    metadata_tables = set(SharedBase.metadata.tables.keys())
    print(f"📊 Metadata Tables: {len(metadata_tables)}")
    
    # Get tables from database
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """))
        
        db_tables = set(row[0] for row in result.fetchall())
    
    print(f"📊 Database Tables: {len(db_tables)}")
    
    # Find differences
    in_metadata_not_db = metadata_tables - db_tables
    in_db_not_metadata = db_tables - metadata_tables
    
    print(f"\n{'='*60}")
    print("COMPARISON RESULTS")
    print(f"{'='*60}")
    
    if in_metadata_not_db:
        print(f"\n❌ Tables in METADATA but NOT in DATABASE ({len(in_metadata_not_db)}):")
        for table in sorted(in_metadata_not_db):
            print(f"   • {table}")
    else:
        print("\n✅ All metadata tables exist in database")
    
    if in_db_not_metadata:
        print(f"\n⚠️  Tables in DATABASE but NOT in METADATA ({len(in_db_not_metadata)}):")
        for table in sorted(in_db_not_metadata):
            print(f"   • {table}")
    else:
        print("\n✅ All database tables are in metadata")
    
    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Metadata: {len(metadata_tables)} tables")
    print(f"  Database: {len(db_tables)} tables")
    print(f"  Missing from DB: {len(in_metadata_not_db)} tables")
    print(f"  Extra in DB: {len(in_db_not_metadata)} tables")
    print(f"{'='*60}\n")
    
    return metadata_tables, db_tables, in_metadata_not_db, in_db_not_metadata

if __name__ == "__main__":
    try:
        # Import models to populate metadata
        import app.models
        metadata_tables, db_tables, missing, extra = compare_tables()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

