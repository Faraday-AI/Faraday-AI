#!/usr/bin/env python3
"""
Simple empty tables seeding script
Uses gen_random_uuid() for UUID columns and skips ID columns
"""

import sys
import os
import random
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from app.core.database import SessionLocal
from sqlalchemy import text, inspect

def simple_empty_tables_seeding():
    """Seed all empty tables with simple mock data"""
    session = SessionLocal()
    try:
        print("🌱 SIMPLE SEEDING: Empty Tables for Development")
        print("=" * 50)
        
        # Get all empty tables
        result = session.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """))
        all_tables = [row[0] for row in result.fetchall()]
        
        empty_tables = []
        for table in all_tables:
            try:
                count_result = session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = count_result.fetchone()[0]
                if count == 0:
                    empty_tables.append(table)
            except Exception as e:
                print(f"⚠️  Error checking {table}: {e}")
        
        print(f"📊 Found {len(empty_tables)} empty tables to seed")
        
        # Get some basic IDs for foreign keys
        user_ids = get_ids(session, "users", 10)
        student_ids = get_ids(session, "students", 10)
        teacher_ids = get_ids(session, "teachers", 10)
        
        # Get UUID IDs from tables that have UUID primary keys
        teacher_uuid_ids = get_uuid_ids(session, "teachers", 10)
        student_uuid_ids = get_uuid_ids(session, "students", 10)
        user_uuid_ids = get_uuid_ids(session, "users", 10)
        lesson_plan_uuid_ids = get_uuid_ids(session, "lesson_plan_templates", 10)
        assessment_uuid_ids = get_uuid_ids(session, "assessment_templates", 10)
        resource_uuid_ids = get_uuid_ids(session, "educational_resources", 10)
        beta_program_uuid_ids = get_uuid_ids(session, "beta_testing_programs", 10)
        collection_uuid_ids = get_uuid_ids(session, "resource_collections", 10)
        curriculum_uuid_ids = get_uuid_ids(session, "curriculum", 10)
        
        print(f"📋 Dependencies: {len(user_ids)} users, {len(student_ids)} students, {len(teacher_ids)} teachers")
        print(f"📋 UUID Dependencies: {len(teacher_uuid_ids)} teacher UUIDs, {len(lesson_plan_uuid_ids)} lesson plan UUIDs")
        
        # Seed each empty table with simple data
        seeded_count = 0
        for table in empty_tables:
            try:
                # Clear any transaction issues
                session.rollback()
                
                # Get table schema
                schema = get_table_schema(session, table)
                if not schema:
                    print(f"  ⚠️  {table}: Could not get schema, skipping")
                    continue
                
                # Generate simple data
                data = generate_simple_data(session, table, schema, user_ids, student_ids, teacher_ids,
                                          teacher_uuid_ids, student_uuid_ids, user_uuid_ids,
                                          lesson_plan_uuid_ids, assessment_uuid_ids, resource_uuid_ids,
                                          beta_program_uuid_ids, collection_uuid_ids, curriculum_uuid_ids)
                
                if data:
                    count = insert_simple_data(session, table, data)
                    if count > 0:
                        # Commit this table's data immediately
                        session.commit()
                        print(f"  ✅ {table}: {count} records")
                        seeded_count += 1
                    else:
                        print(f"  ⚠️  {table}: No data inserted")
                        session.rollback()
                else:
                    print(f"  ⚠️  {table}: No suitable data generated")
                    
            except Exception as e:
                print(f"  ❌ {table}: {e}")
                session.rollback()
        
        print(f"\n🎉 Seeded {seeded_count} empty tables successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        session.rollback()
        import traceback
        traceback.print_exc()
    finally:
        session.close()

def get_table_schema(session, table_name):
    """Get table schema information"""
    try:
        inspector = inspect(session.bind)
        columns = inspector.get_columns(table_name)
        return {col['name']: col for col in columns}
    except Exception as e:
        print(f"    ⚠️  Could not get schema for {table_name}: {e}")
        return None

def get_ids(session, table, limit):
    """Get IDs from a table"""
    try:
        result = session.execute(text(f"SELECT id FROM {table} LIMIT {limit}"))
        return [row[0] for row in result.fetchall()]
    except:
        return []

def get_uuid_ids(session, table, limit):
    """Get UUID IDs from a table"""
    try:
        result = session.execute(text(f"SELECT id FROM {table} LIMIT {limit}"))
        return [row[0] for row in result.fetchall()]
    except:
        return []

def generate_simple_data(session, table_name, schema, user_ids, student_ids, teacher_ids, 
                        teacher_uuid_ids, student_uuid_ids, user_uuid_ids, 
                        lesson_plan_uuid_ids, assessment_uuid_ids, resource_uuid_ids,
                        beta_program_uuid_ids, collection_uuid_ids, curriculum_uuid_ids):
    """Generate simple data based on table schema"""
    
    # Generate 5 records
    data = []
    for i in range(5):
        record = {}
        
        for col_name, col_info in schema.items():
            col_type = str(col_info['type']).upper()
            
            # Handle ID columns based on type
            if col_name == 'id':
                if 'UUID' in col_type:
                    # Skip UUID columns - let database generate them with gen_random_uuid()
                    continue
                elif 'SERIAL' in col_type or 'AUTO_INCREMENT' in col_type:
                    # Skip auto-incrementing integer columns
                    continue
                else:
                    # For other integer ID columns, use a random existing ID or generate one
                    if user_ids:
                        record[col_name] = random.choice(user_ids)
                    else:
                        record[col_name] = i + 1
                
            # Generate data based on column name and type
            elif col_name.endswith('_id'):
                # Foreign key - choose appropriate ID based on column type
                if 'UUID' in col_type:
                    # This is a UUID foreign key
                    if 'teacher' in col_name and teacher_uuid_ids:
                        record[col_name] = random.choice(teacher_uuid_ids)
                    elif 'student' in col_name and student_uuid_ids:
                        record[col_name] = random.choice(student_uuid_ids)
                    elif 'user' in col_name and user_uuid_ids:
                        record[col_name] = random.choice(user_uuid_ids)
                    elif 'lesson' in col_name and lesson_plan_uuid_ids:
                        record[col_name] = random.choice(lesson_plan_uuid_ids)
                    elif 'template' in col_name and assessment_uuid_ids:
                        record[col_name] = random.choice(assessment_uuid_ids)
                    elif 'resource' in col_name and resource_uuid_ids:
                        record[col_name] = random.choice(resource_uuid_ids)
                    elif 'program' in col_name and beta_program_uuid_ids:
                        record[col_name] = random.choice(beta_program_uuid_ids)
                    elif 'collection' in col_name and collection_uuid_ids:
                        record[col_name] = random.choice(collection_uuid_ids)
                    elif 'curriculum' in col_name and curriculum_uuid_ids:
                        record[col_name] = random.choice(curriculum_uuid_ids)
                    elif 'category' in col_name:
                        # Try to get category UUIDs
                        try:
                            category_uuid_ids = get_uuid_ids(session, "lesson_plan_categories", 10)
                            if category_uuid_ids:
                                record[col_name] = random.choice(category_uuid_ids)
                            else:
                                continue
                        except:
                            continue
                    elif 'participant' in col_name:
                        # Try to get participant UUIDs
                        try:
                            participant_uuid_ids = get_uuid_ids(session, "beta_testing_participants", 10)
                            if participant_uuid_ids:
                                record[col_name] = random.choice(participant_uuid_ids)
                            else:
                                continue
                        except:
                            continue
                    elif 'survey' in col_name:
                        # Try to get survey UUIDs
                        try:
                            survey_uuid_ids = get_uuid_ids(session, "beta_testing_surveys", 10)
                            if survey_uuid_ids:
                                record[col_name] = random.choice(survey_uuid_ids)
                            else:
                                continue
                        except:
                            continue
                    else:
                        # Fallback to any available UUID
                        if teacher_uuid_ids:
                            record[col_name] = random.choice(teacher_uuid_ids)
                        elif user_uuid_ids:
                            record[col_name] = random.choice(user_uuid_ids)
                        else:
                            # Skip if no UUIDs available
                            continue
                else:
                    # This is an integer foreign key
                    if 'user' in col_name and user_ids:
                        record[col_name] = random.choice(user_ids)
                    elif 'student' in col_name and student_ids:
                        record[col_name] = random.choice(student_ids)
                    elif 'teacher' in col_name and teacher_ids:
                        record[col_name] = random.choice(teacher_ids)
                    else:
                        # Use a random existing ID or 1 as fallback
                        if user_ids:
                            record[col_name] = random.choice(user_ids)
                        else:
                            record[col_name] = 1
            elif col_name in ['name', 'title']:
                record[col_name] = f"{table_name.replace('_', ' ').title()} {i+1}"
            elif col_name in ['description', 'message']:
                record[col_name] = f"Description for {table_name} {i+1}"
            elif col_name == 'content':
                # Handle content column - check if it's JSONB
                if 'JSON' in col_type:
                    record[col_name] = json.dumps({"content": f"Description for {table_name} {i+1}", "type": "test"})
                else:
                    record[col_name] = f"Description for {table_name} {i+1}"
            elif col_name in ['email']:
                record[col_name] = f"user{i+1}@example.com"
            elif col_name in ['status']:
                record[col_name] = random.choice(['ACTIVE', 'INACTIVE', 'PENDING', 'COMPLETED'])
            elif col_name in ['is_active', 'is_enabled', 'is_public']:
                record[col_name] = random.choice([True, False])
            elif col_name in ['created_at', 'updated_at']:
                record[col_name] = datetime.now() - timedelta(days=random.randint(1, 30))
            elif col_name in ['rating', 'score']:
                record[col_name] = random.randint(1, 5)
            elif col_name in ['count', 'usage_count', 'download_count']:
                record[col_name] = random.randint(1, 100)
            elif col_name in ['duration_minutes', 'duration_seconds']:
                record[col_name] = random.randint(10, 120)
            elif col_name in ['percentage', 'completion_percentage']:
                record[col_name] = random.randint(0, 100)
            elif col_name in ['weight', 'success_rate', 'confidence_score']:
                record[col_name] = round(random.uniform(0.1, 1.0), 2)
            elif 'JSON' in col_type:
                record[col_name] = json.dumps({'key': f'value_{i+1}', 'type': 'test'})
            elif 'ARRAY' in col_type:
                # Handle PostgreSQL arrays
                if 'TEXT' in col_type or 'VARCHAR' in col_type:
                    record[col_name] = f"{{item_{i+1},item_{i+2}}}"
                else:
                    record[col_name] = f"{{{i+1},{i+2}}}"
            elif 'INTEGER' in col_type or 'BIGINT' in col_type:
                record[col_name] = random.randint(1, 100)
            elif 'BOOLEAN' in col_type:
                record[col_name] = random.choice([True, False])
            elif 'TIMESTAMP' in col_type or 'DATETIME' in col_type:
                record[col_name] = datetime.now() - timedelta(days=random.randint(1, 30))
            elif 'VARCHAR' in col_type or 'TEXT' in col_type:
                record[col_name] = f"{col_name}_{i+1}"
            else:
                # Default fallback
                record[col_name] = f"value_{i+1}"
        
        data.append(record)
    
    return data

def insert_simple_data(session, table_name, data):
    """Insert/update data into a table using upsert logic for migration"""
    if not data:
        return 0
    
    try:
        # Get column names from first record
        columns = list(data[0].keys())
        columns_str = ', '.join(columns)
        placeholders = ', '.join([f':{col}' for col in columns])
        
        # Check if table has UUID primary key that we need to generate
        schema = get_table_schema(session, table_name)
        has_uuid_id = schema and 'id' in schema and 'UUID' in str(schema['id']['type']).upper()
        has_auto_increment_id = schema and 'id' in schema and ('SERIAL' in str(schema['id']['type']).upper() or schema['id'].get('autoincrement', False))
        
        if has_uuid_id and 'id' not in columns:
            # Use gen_random_uuid() for UUID ID column
            columns_str = 'id, ' + columns_str
            placeholders = 'gen_random_uuid(), ' + placeholders
        elif has_auto_increment_id and 'id' not in columns:
            # Skip auto-increment ID column - let database generate it
            pass
        elif 'id' in columns:
            # ID column is included in data, use it as-is
            pass
        
        # Build upsert query with ON CONFLICT DO UPDATE
        base_query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
        
        # Determine conflict resolution based on primary key
        if has_uuid_id or 'id' in columns:
            # Use ID as conflict target
            update_columns = [f"{col} = EXCLUDED.{col}" for col in columns if col != 'id']
            if update_columns:
                conflict_query = f"{base_query} ON CONFLICT (id) DO UPDATE SET {', '.join(update_columns)}"
            else:
                conflict_query = f"{base_query} ON CONFLICT (id) DO NOTHING"
        else:
            # Try to find a unique column for conflict resolution
            unique_columns = []
            for col_name, col_info in schema.items():
                if col_info.get('unique', False) or col_name in ['name', 'email', 'title']:
                    unique_columns.append(col_name)
            
            if unique_columns:
                # Use first unique column as conflict target
                conflict_col = unique_columns[0]
                update_columns = [f"{col} = EXCLUDED.{col}" for col in columns if col != conflict_col]
                if update_columns:
                    conflict_query = f"{base_query} ON CONFLICT ({conflict_col}) DO UPDATE SET {', '.join(update_columns)}"
                else:
                    conflict_query = f"{base_query} ON CONFLICT ({conflict_col}) DO NOTHING"
            else:
                # No conflict resolution - just insert
                conflict_query = base_query
        
        # Try upsert first, fallback to simple insert if it fails
        try:
            for record in data:
                session.execute(text(conflict_query), record)
        except Exception as upsert_error:
            print(f"    ⚠️  Upsert failed for {table_name}, trying simple insert: {upsert_error}")
            # Fallback to simple insert
            for record in data:
                session.execute(text(base_query), record)
        
        return len(data)
    except Exception as e:
        print(f"    ⚠️  Error inserting into {table_name}: {e}")
        return 0

if __name__ == "__main__":
    simple_empty_tables_seeding()
