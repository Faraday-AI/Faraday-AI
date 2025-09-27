#!/usr/bin/env python3
"""Check curriculum_units table structure"""

import sys
sys.path.insert(0, '/app')

from sqlalchemy import text
from app.db.session import get_db

def check_table_structure():
    session = next(get_db())
    
    # Check if table exists
    result = session.execute(text("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'curriculum_units'
        )
    """))
    table_exists = result.scalar()
    print(f"curriculum_units table exists: {table_exists}")
    
    if table_exists:
        # Get table structure
        result = session.execute(text("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'curriculum_units' 
            ORDER BY ordinal_position
        """))
        
        print("\ncurriculum_units table structure:")
        for row in result:
            nullable = "NULL" if row[2] == "YES" else "NOT NULL"
            print(f"  {row[0]}: {row[1]} ({nullable})")
    
    session.close()

if __name__ == "__main__":
    check_table_structure()
