#!/usr/bin/env python3
"""
Seed Remaining Empty Tables
===========================
This script identifies and populates the 40 tables that remain empty after the main seeding process.
"""

import os
import sys
import json
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from app.core.database import DATABASE_URL

def get_empty_tables(session):
    """Get list of tables with 0 records"""
    empty_tables = []
    
    # Get all table names
    result = session.execute(text("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE'
        ORDER BY table_name
    """)).fetchall()
    
    for table_name in result:
        table_name = table_name[0]
        try:
            count_result = session.execute(text(f"SELECT COUNT(*) FROM {table_name}")).fetchone()
            count = count_result[0] if count_result else 0
            if count == 0:
                empty_tables.append(table_name)
        except Exception as e:
            print(f"⚠️  Could not check table {table_name}: {e}")
    
    return empty_tables

def get_table_schema(session, table_name):
    """Get table schema information"""
    try:
        inspector = inspect(session.bind)
        columns = inspector.get_columns(table_name)
        return columns
    except Exception as e:
        print(f"⚠️  Could not get schema for {table_name}: {e}")
        return []

def seed_table_with_mock_data(session, table_name, columns):
    """Seed a table with mock data based on its schema"""
    try:
        # Get primary key column
        pk_column = None
        for col in columns:
            if col.get('primary_key', False):
                pk_column = col['name']
                break
        
        # Get foreign key columns
        fk_columns = []
        for col in columns:
            if col.get('foreign_keys'):
                fk_columns.append(col['name'])
        
        # Generate mock data based on column types
        mock_data = {}
        for col in columns:
            col_name = col['name']
            col_type = str(col['type']).lower()
            nullable = col.get('nullable', True)
            
            if col_name == pk_column:
                # Skip primary key, let DB handle it
                continue
            elif col_name in fk_columns:
                # Handle foreign keys by getting existing IDs
                if 'user' in col_name.lower():
                    result = session.execute(text("SELECT id FROM users LIMIT 1")).fetchone()
                    mock_data[col_name] = result[0] if result else 1
                elif 'student' in col_name.lower():
                    result = session.execute(text("SELECT id FROM students LIMIT 1")).fetchone()
                    mock_data[col_name] = result[0] if result else 1
                elif 'activity' in col_name.lower():
                    result = session.execute(text("SELECT id FROM activities LIMIT 1")).fetchone()
                    mock_data[col_name] = result[0] if result else 1
                elif 'school' in col_name.lower():
                    result = session.execute(text("SELECT id FROM schools LIMIT 1")).fetchone()
                    mock_data[col_name] = result[0] if result else 1
                else:
                    # Generic foreign key handling
                    mock_data[col_name] = 1
            elif 'uuid' in col_type:
                mock_data[col_name] = f"gen_random_uuid()"
            elif 'json' in col_type or 'jsonb' in col_type:
                mock_data[col_name] = json.dumps({"mock": "data", "created_at": datetime.utcnow().isoformat()})
            elif 'timestamp' in col_type:
                mock_data[col_name] = datetime.utcnow()
            elif 'boolean' in col_type:
                mock_data[col_name] = True
            elif 'integer' in col_type:
                mock_data[col_name] = 1
            elif 'text' in col_type or 'varchar' in col_type:
                mock_data[col_name] = f"Mock {table_name} data"
            elif 'decimal' in col_type or 'numeric' in col_type:
                mock_data[col_name] = 1.0
            else:
                mock_data[col_name] = f"Mock {col_name}"
        
        # Insert mock data
        if mock_data:
            # Build INSERT statement
            columns_str = ', '.join(mock_data.keys())
            values_str = ', '.join([f":{col}" for col in mock_data.keys()])
            
            # Handle UUID generation in SQL
            if 'gen_random_uuid()' in str(mock_data.values()):
                # Use raw SQL for UUID generation
                sql = f"""
                INSERT INTO {table_name} ({columns_str})
                VALUES ({values_str.replace('gen_random_uuid()', 'gen_random_uuid()')})
                """
                session.execute(text(sql), mock_data)
            else:
                sql = f"""
                INSERT INTO {table_name} ({columns_str})
                VALUES ({values_str})
                """
                session.execute(text(sql), mock_data)
            
            print(f"  ✅ Created mock data for {table_name}")
            return True
        else:
            print(f"  ⚠️  No data to insert for {table_name}")
            return False
            
    except Exception as e:
        print(f"  ❌ Error seeding {table_name}: {e}")
        return False

def main():
    """Main function to seed remaining empty tables"""
    print("🔍 IDENTIFYING AND SEEDING REMAINING EMPTY TABLES")
    print("=" * 60)
    
    # Create database connection
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Get empty tables
        print("🔍 Finding empty tables...")
        empty_tables = get_empty_tables(session)
        
        print(f"📊 Found {len(empty_tables)} empty tables:")
        for table in empty_tables:
            print(f"  - {table}")
        
        if not empty_tables:
            print("✅ No empty tables found!")
            return
        
        print(f"\n🌱 Seeding {len(empty_tables)} empty tables...")
        
        success_count = 0
        for table_name in empty_tables:
            print(f"\n📋 Processing {table_name}...")
            
            # Get table schema
            columns = get_table_schema(session, table_name)
            if not columns:
                print(f"  ⚠️  Could not get schema for {table_name}, skipping")
                continue
            
            # Seed with mock data
            if seed_table_with_mock_data(session, table_name, columns):
                success_count += 1
        
        # Commit all changes
        session.commit()
        
        print(f"\n🎉 SEEDING COMPLETE!")
        print(f"✅ Successfully seeded: {success_count}/{len(empty_tables)} tables")
        
        # Verify results
        print(f"\n🔍 Verifying results...")
        final_empty = get_empty_tables(session)
        print(f"📊 Remaining empty tables: {len(final_empty)}")
        
        if final_empty:
            print("Remaining empty tables:")
            for table in final_empty:
                print(f"  - {table}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    main()

