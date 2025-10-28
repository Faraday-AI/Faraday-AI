#!/usr/bin/env python3
"""
Simple migration script to populate empty tables using existing data from previous phases.
This script uses individual transactions for each table to avoid cascading failures.
"""

import os
import sys
import json
import random
from datetime import datetime, timedelta

# Add the app directory to the Python path
sys.path.append('/app')

from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from app.core.database import DATABASE_URL

def get_database_connection():
    """Get database connection using the app's database configuration."""
    try:
        engine = create_engine(DATABASE_URL)
        Session = sessionmaker(bind=engine)
        return Session()
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def get_existing_ids(session, table_name, id_column='id', limit=50):
    """Get existing IDs from a table for foreign key references."""
    try:
        result = session.execute(text(f"SELECT {id_column} FROM {table_name} LIMIT {limit}"))
        ids = [row[0] for row in result.fetchall() if row[0] is not None]
        return ids
    except Exception as e:
        print(f"Warning: Could not fetch IDs from {table_name}: {e}")
        return []

def get_table_schema(session, table_name):
    """Get table schema information."""
    try:
        inspector = inspect(session.bind)
        columns = inspector.get_columns(table_name)
        return {col['name']: col for col in columns}
    except Exception as e:
        print(f"Warning: Could not get schema for {table_name}: {e}")
        return {}

def generate_simple_data(session, table_name, schema):
    """Generate simple data for a table."""
    data = []
    
    # Get existing IDs from common tables
    user_ids = get_existing_ids(session, 'users', 'id', 20)
    teacher_ids = get_existing_ids(session, 'teachers', 'id', 20)
    lesson_plan_template_ids = get_existing_ids(session, 'lesson_plan_templates', 'id', 20)
    assessment_template_ids = get_existing_ids(session, 'assessment_templates', 'id', 20)
    resource_ids = get_existing_ids(session, 'resources', 'id', 20)
    category_ids = get_existing_ids(session, 'resource_categories', 'id', 20)
    beta_program_ids = get_existing_ids(session, 'beta_testing_programs', 'id', 20)
    survey_ids = get_existing_ids(session, 'beta_testing_surveys', 'id', 20)
    
    for i in range(3):  # Generate 3 records per table
        record = {}
        
        for column_name, column_info in schema.items():
            if column_name == 'id':
                # Skip ID - let database handle it
                continue
            elif column_name.endswith('_id'):
                # Foreign key - use existing ID from related table
                if 'user' in column_name and user_ids:
                    record[column_name] = random.choice(user_ids)
                elif 'teacher' in column_name and teacher_ids:
                    record[column_name] = random.choice(teacher_ids)
                elif 'template' in column_name and 'lesson_plan' in column_name and lesson_plan_template_ids:
                    record[column_name] = random.choice(lesson_plan_template_ids)
                elif 'template' in column_name and 'assessment' in column_name and assessment_template_ids:
                    record[column_name] = random.choice(assessment_template_ids)
                elif 'resource' in column_name and resource_ids:
                    record[column_name] = random.choice(resource_ids)
                elif 'category' in column_name and category_ids:
                    record[column_name] = random.choice(category_ids)
                elif 'beta_program' in column_name and beta_program_ids:
                    record[column_name] = random.choice(beta_program_ids)
                elif 'survey' in column_name and survey_ids:
                    record[column_name] = random.choice(survey_ids)
                elif 'participant' in column_name and user_ids:
                    record[column_name] = random.choice(user_ids)
                else:
                    # Generic foreign key - try to find a suitable ID
                    if user_ids:
                        record[column_name] = random.choice(user_ids)
                    else:
                        record[column_name] = 1  # Fallback
            elif column_info['type'].python_type == str:
                record[column_name] = f"migrated_{table_name}_{i+1}_{column_name}"
            elif column_info['type'].python_type == int:
                record[column_name] = random.randint(1, 100)
            elif column_info['type'].python_type == float:
                record[column_name] = round(random.uniform(0.0, 100.0), 2)
            elif column_info['type'].python_type == bool:
                record[column_name] = random.choice([True, False])
            elif column_info['type'].python_type == datetime:
                record[column_name] = datetime.now() - timedelta(days=random.randint(1, 365))
            elif 'json' in str(column_info['type']).lower():
                record[column_name] = json.dumps({"migrated": True, "table": table_name, "record": i+1})
            elif 'array' in str(column_info['type']).lower():
                record[column_name] = f"{{item_{i+1}_1,item_{i+1}_2}}"
            else:
                # Default fallback
                record[column_name] = f"migrated_value_{i+1}"
        
        data.append(record)
    
    return data

def migrate_single_table(session, table_name):
    """Migrate data to a single table with individual transaction."""
    try:
        print(f"Migrating data to {table_name}...")
        
        # Get table schema
        schema = get_table_schema(session, table_name)
        if not schema:
            print(f"  Skipping {table_name} - could not get schema")
            return False
        
        # Generate data
        data = generate_simple_data(session, table_name, schema)
        
        if not data:
            print(f"  Skipping {table_name} - no data generated")
            return False
        
        # Insert data with individual transaction
        for record in data:
            columns = list(record.keys())
            placeholders = ', '.join([f':{col}' for col in columns])
            insert_sql = f"""
                INSERT INTO {table_name} ({', '.join(columns)})
                VALUES ({placeholders})
                ON CONFLICT DO NOTHING
            """
            
            session.execute(text(insert_sql), record)
        
        session.commit()
        print(f"  ✓ Migrated {len(data)} records to {table_name}")
        return True
        
    except Exception as e:
        print(f"  ✗ Error migrating {table_name}: {e}")
        session.rollback()
        return False

def migrate_empty_tables():
    """Migrate data to populate empty tables."""
    session = get_database_connection()
    if not session:
        print("Failed to connect to database")
        return
    
    try:
        # Get all tables
        result = session.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """))
        all_tables = [row[0] for row in result.fetchall()]
        
        # Get table counts
        table_counts = {}
        for table in all_tables:
            try:
                count_result = session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = count_result.scalar()
                table_counts[table] = count
            except Exception as e:
                print(f"Warning: Could not count {table}: {e}")
                table_counts[table] = 0
        
        # Find empty tables
        empty_tables = [table for table, count in table_counts.items() if count == 0]
        
        print(f"Found {len(empty_tables)} empty tables to migrate:")
        for table in empty_tables:
            print(f"  - {table}")
        
        if not empty_tables:
            print("No empty tables found!")
            return
        
        # Migrate data to empty tables one by one
        migrated_count = 0
        for table in empty_tables:
            if migrate_single_table(session, table):
                migrated_count += 1
        
        print(f"\nMigration complete! Successfully migrated {migrated_count} tables.")
        
        # Show final counts
        print("\nFinal table counts:")
        for table in empty_tables:
            try:
                count_result = session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = count_result.scalar()
                print(f"  {table}: {count} records")
            except Exception as e:
                print(f"  {table}: Error getting count - {e}")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    migrate_empty_tables()
