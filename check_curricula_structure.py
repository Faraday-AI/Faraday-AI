#!/usr/bin/env python3
"""Check curricula table structure"""

from app.core.database import SessionLocal
from sqlalchemy import text

def check_curricula_structure():
    session = SessionLocal()
    try:
        # Check curricula table columns
        result = session.execute(text("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'curricula' 
            ORDER BY ordinal_position
        """))
        
        print("Curricula table columns:")
        for row in result.fetchall():
            print(f"  {row[0]}: {row[1]} (nullable: {row[2]})")
            
        # Check if table exists and has data
        count_result = session.execute(text("SELECT COUNT(*) FROM curricula"))
        count = count_result.scalar()
        print(f"\nCurricula table record count: {count}")
        
    finally:
        session.close()

if __name__ == "__main__":
    check_curricula_structure() 