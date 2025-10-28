#!/usr/bin/env python3
"""
Migration-based script to populate empty tables using existing data from previous phases.
This script migrates data from existing tables to populate empty tables, ensuring
flexibility when IDs change during new runs.
"""

import os
import sys
import json
import random
from datetime import datetime, timedelta
from decimal import Decimal

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

def get_existing_data(session, table_name, limit=100):
    """Get existing data from a table for migration purposes."""
    try:
        result = session.execute(text(f"SELECT * FROM {table_name} LIMIT {limit}"))
        return result.fetchall()
    except Exception as e:
        print(f"Warning: Could not fetch data from {table_name}: {e}")
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

def generate_migrated_data(session, table_name, schema, existing_data):
    """Generate data by migrating from existing tables."""
    data = []
    
    # Get existing IDs from related tables
    user_ids = get_existing_data(session, 'users', 50)
    teacher_ids = get_existing_data(session, 'teachers', 50)
    curriculum_ids = get_existing_data(session, 'curricula', 50)
    lesson_plan_ids = get_existing_data(session, 'lesson_plans', 50)
    activity_ids = get_existing_data(session, 'activities', 50)
    assessment_ids = get_existing_data(session, 'assessments', 50)
    skill_ids = get_existing_data(session, 'skills', 50)
    grade_level_ids = get_existing_data(session, 'grade_levels', 50)
    subject_ids = get_existing_data(session, 'subjects', 50)
    
    # Convert to lists of IDs
    user_id_list = [row[0] for row in user_ids if row[0]]
    teacher_id_list = [row[0] for row in teacher_ids if row[0]]
    curriculum_id_list = [row[0] for row in curriculum_ids if row[0]]
    lesson_plan_id_list = [row[0] for row in lesson_plan_ids if row[0]]
    activity_id_list = [row[0] for row in activity_ids if row[0]]
    assessment_id_list = [row[0] for row in assessment_ids if row[0]]
    skill_id_list = [row[0] for row in skill_ids if row[0]]
    grade_level_id_list = [row[0] for row in grade_level_ids if row[0]]
    subject_id_list = [row[0] for row in subject_ids if row[0]]
    
    for i in range(5):  # Generate 5 records per table
        record = {}
        
        for column_name, column_info in schema.items():
            if column_name == 'id':
                # Skip ID - let database handle it
                continue
            elif column_name.endswith('_id'):
                # Foreign key - use existing ID from related table
                if 'user' in column_name and user_id_list:
                    record[column_name] = random.choice(user_id_list)
                elif 'teacher' in column_name and teacher_id_list:
                    record[column_name] = random.choice(teacher_id_list)
                elif 'curriculum' in column_name and curriculum_id_list:
                    record[column_name] = random.choice(curriculum_id_list)
                elif 'lesson_plan' in column_name and lesson_plan_id_list:
                    record[column_name] = random.choice(lesson_plan_id_list)
                elif 'activity' in column_name and activity_id_list:
                    record[column_name] = random.choice(activity_id_list)
                elif 'assessment' in column_name and assessment_id_list:
                    record[column_name] = random.choice(assessment_id_list)
                elif 'skill' in column_name and skill_id_list:
                    record[column_name] = random.choice(skill_id_list)
                elif 'grade_level' in column_name and grade_level_id_list:
                    record[column_name] = random.choice(grade_level_id_list)
                elif 'subject' in column_name and subject_id_list:
                    record[column_name] = random.choice(subject_id_list)
                else:
                    # Generic foreign key - try to find a suitable ID
                    if user_id_list:
                        record[column_name] = random.choice(user_id_list)
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
        
        # Migrate data to empty tables
        migrated_count = 0
        for table in empty_tables:
            try:
                print(f"\nMigrating data to {table}...")
                
                # Get table schema
                schema = get_table_schema(session, table)
                if not schema:
                    print(f"  Skipping {table} - could not get schema")
                    continue
                
                # Generate migrated data
                migrated_data = generate_migrated_data(session, table, schema, [])
                
                if not migrated_data:
                    print(f"  Skipping {table} - no data generated")
                    continue
                
                # Insert migrated data
                for record in migrated_data:
                    columns = list(record.keys())
                    values = list(record.values())
                    
                    placeholders = ', '.join([f':{col}' for col in columns])
                    insert_sql = f"""
                        INSERT INTO {table} ({', '.join(columns)})
                        VALUES ({placeholders})
                        ON CONFLICT DO NOTHING
                    """
                    
                    session.execute(text(insert_sql), record)
                
                session.commit()
                print(f"  ✓ Migrated {len(migrated_data)} records to {table}")
                migrated_count += 1
                
            except Exception as e:
                print(f"  ✗ Error migrating {table}: {e}")
                session.rollback()
                continue
        
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
