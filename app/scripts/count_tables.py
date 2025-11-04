#!/usr/bin/env python3
"""
Count Total Tables in Database
Including all tables in the public schema
"""
import os
import sys
from sqlalchemy import create_engine, text, inspect

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.core.database import DATABASE_URL

def count_tables():
    """Count all tables in the database."""
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # Query for all tables in public schema
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """))
        
        tables = [row[0] for row in result.fetchall()]
        
        # Separate into different categories
        jobs_tables = [t for t in tables if 'job' in t.lower() or 'celery' in t.lower() or 'task' in t.lower()]
        other_tables = [t for t in tables if t not in jobs_tables]
        
        print("=" * 60)
        print("DATABASE TABLE COUNT")
        print("=" * 60)
        print(f"\n📊 Total Tables: {len(tables)}")
        print(f"   • Regular Tables: {len(other_tables)}")
        print(f"   • Jobs/Queue Tables: {len(jobs_tables)}")
        
        if jobs_tables:
            print(f"\n📋 Jobs/Queue Tables ({len(jobs_tables)}):")
            for table in sorted(jobs_tables):
                print(f"   • {table}")
        
        print(f"\n📋 All Tables ({len(tables)}):")
        for i, table in enumerate(sorted(tables), 1):
            print(f"   {i:3d}. {table}")
        
        print("\n" + "=" * 60)
        return len(tables)

if __name__ == "__main__":
    try:
        count = count_tables()
        print(f"\n✅ Count complete: {count} total tables")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

