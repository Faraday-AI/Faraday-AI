#!/usr/bin/env python3
"""
Check actual table counts in the database to identify discrepancies
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from app.core.database import SessionLocal
from sqlalchemy import text

def check_table_counts():
    """Check actual table counts in the database"""
    session = SessionLocal()
    try:
        # Get all table names
        result = session.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """))
        tables = [row[0] for row in result.fetchall()]
        
        print(f"📊 Total tables in database: {len(tables)}")
        print("\n🔍 Checking table population status...")
        
        populated_tables = []
        empty_tables = []
        
        for table in tables:
            try:
                # Check if table has data
                count_result = session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = count_result.fetchone()[0]
                
                if count > 0:
                    populated_tables.append((table, count))
                else:
                    empty_tables.append(table)
            except Exception as e:
                print(f"⚠️  Error checking {table}: {e}")
        
        print(f"\n✅ Populated tables: {len(populated_tables)}")
        print(f"❌ Empty tables: {len(empty_tables)}")
        
        if empty_tables:
            print(f"\n📋 Empty tables ({len(empty_tables)}):")
            for table in sorted(empty_tables):
                print(f"  - {table}")
        
        print(f"\n📊 Summary:")
        print(f"  Total tables: {len(tables)}")
        print(f"  Populated: {len(populated_tables)}")
        print(f"  Empty: {len(empty_tables)}")
        print(f"  Population rate: {len(populated_tables)/len(tables)*100:.1f}%")
        
        return {
            'total_tables': len(tables),
            'populated_tables': len(populated_tables),
            'empty_tables': len(empty_tables),
            'empty_table_list': empty_tables
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        session.close()

if __name__ == "__main__":
    check_table_counts()
