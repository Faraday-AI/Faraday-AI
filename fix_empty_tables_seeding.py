#!/usr/bin/env python3
"""
Fixed version of empty tables seeding script
Checks actual table schemas before inserting data
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

def fix_empty_tables_seeding():
    """Seed all empty tables with mock data for development"""
    session = SessionLocal()
    try:
        print("🌱 FIXED SEEDING: Empty Tables for Development")
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
        
        # Get dependency IDs
        user_ids = get_ids(session, "users", 50)
        student_ids = get_ids(session, "students", 100)
        teacher_ids = get_ids(session, "teachers", 20)
        activity_ids = get_ids(session, "activities", 50)
        lesson_plan_ids = get_ids(session, "pe_lesson_plans", 20)
        assessment_ids = get_ids(session, "skill_assessment_assessments", 20)
        organization_ids = get_ids(session, "organizations", 10)
        dashboard_user_ids = get_ids(session, "dashboard_users", 20)
        
        print(f"📋 Dependencies: {len(user_ids)} users, {len(student_ids)} students, {len(teacher_ids)} teachers")
        
        # Seed each empty table with schema checking
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
                
                # Generate data based on actual schema
                data = generate_data_for_table(table, schema, user_ids, student_ids, teacher_ids, 
                                             activity_ids, lesson_plan_ids, assessment_ids, 
                                             organization_ids, dashboard_user_ids)
                
                if data:
                    count = insert_data_safe(session, table, data)
                    if count > 0:
                        print(f"  ✅ {table}: {count} records")
                        seeded_count += 1
                    else:
                        print(f"  ⚠️  {table}: No data inserted")
                else:
                    print(f"  ⚠️  {table}: No suitable data generated")
                    
            except Exception as e:
                print(f"  ❌ {table}: {e}")
                session.rollback()
        
        session.commit()
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

def generate_data_for_table(table_name, schema, user_ids, student_ids, teacher_ids, 
                           activity_ids, lesson_plan_ids, assessment_ids, organization_ids, dashboard_user_ids):
    """Generate data based on actual table schema"""
    
    # Get column names and types
    columns = list(schema.keys())
    
    # Generate 10 records
    data = []
    for i in range(10):
        record = {}
        
        for col_name, col_info in schema.items():
            col_type = str(col_info['type']).upper()
            
            # Skip auto-generated columns
            if col_name in ['id'] and 'SERIAL' in col_type or 'AUTO_INCREMENT' in col_type:
                continue
                
            # Generate data based on column name and type
            if col_name == 'id':
                record[col_name] = i + 1
            elif col_name.endswith('_id'):
                # Foreign key - choose appropriate ID
                if 'user' in col_name and user_ids:
                    record[col_name] = random.choice(user_ids)
                elif 'student' in col_name and student_ids:
                    record[col_name] = random.choice(student_ids)
                elif 'teacher' in col_name and teacher_ids:
                    record[col_name] = random.choice(teacher_ids)
                elif 'activity' in col_name and activity_ids:
                    record[col_name] = random.choice(activity_ids)
                elif 'lesson' in col_name and lesson_plan_ids:
                    record[col_name] = random.choice(lesson_plan_ids)
                elif 'assessment' in col_name and assessment_ids:
                    record[col_name] = random.choice(assessment_ids)
                elif 'organization' in col_name and organization_ids:
                    record[col_name] = random.choice(organization_ids)
                else:
                    record[col_name] = random.randint(1, 100)
            elif col_name in ['name', 'title']:
                record[col_name] = f"{table_name.title()} {i+1}"
            elif col_name in ['description', 'content', 'message']:
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
            elif 'JSON' in col_type or 'TEXT' in col_type:
                if col_name in ['config', 'metadata', 'settings']:
                    record[col_name] = json.dumps({'key': f'value_{i+1}', 'type': 'test'})
                else:
                    record[col_name] = f"Text content for {col_name} {i+1}"
            elif 'INTEGER' in col_type or 'BIGINT' in col_type:
                record[col_name] = random.randint(1, 1000)
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

def insert_data_safe(session, table_name, data):
    """Safely insert data into a table"""
    if not data:
        return 0
    
    try:
        # Get column names from first record
        columns = list(data[0].keys())
        columns_str = ', '.join(columns)
        placeholders = ', '.join([f':{col}' for col in columns])
        
        query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
        
        for record in data:
            session.execute(text(query), record)
        
        return len(data)
    except Exception as e:
        print(f"    ⚠️  Error inserting into {table_name}: {e}")
        return 0

if __name__ == "__main__":
    fix_empty_tables_seeding()
