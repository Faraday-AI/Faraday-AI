#!/usr/bin/env python3
"""
Analyze record distribution across all tables to ensure consistency for district size
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

def analyze_record_distribution():
    """Analyze record distribution across all tables"""
    
    # Use the Azure PostgreSQL connection from run.sh
    DATABASE_URL = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        raise RuntimeError('DATABASE_URL must be set in the environment')
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    print('📊 TABLE RECORD DISTRIBUTION ANALYSIS')
    print('=' * 80)
    print(f'{"Table Name":<50} {"Records":<10} {"Status":<15}')
    print('-' * 80)

    # Get all table names and their record counts
    result = session.execute(text("""
        SELECT 
            schemaname,
            relname as tablename,
            n_tup_ins as inserts,
            n_tup_upd as updates,
            n_tup_del as deletes,
            n_live_tup as live_tuples,
            n_dead_tup as dead_tuples
        FROM pg_stat_user_tables 
        ORDER BY n_live_tup DESC
    """))

    total_tables = 0
    total_records = 0
    empty_tables = []
    low_tables = []
    ok_tables = []
    good_tables = []
    excellent_tables = []

    for row in result:
        schema, table, inserts, updates, deletes, live_tuples, dead_tuples = row
        total_tables += 1
        total_records += live_tuples
        
        # Categorize tables by record count
        if live_tuples == 0:
            status = '❌ EMPTY'
            empty_tables.append((table, live_tuples))
        elif live_tuples < 10:
            status = '⚠️  LOW'
            low_tables.append((table, live_tuples))
        elif live_tuples < 100:
            status = '✅ OK'
            ok_tables.append((table, live_tuples))
        elif live_tuples < 1000:
            status = '✅ GOOD'
            good_tables.append((table, live_tuples))
        else:
            status = '✅ EXCELLENT'
            excellent_tables.append((table, live_tuples))
        
        print(f'{table:<50} {live_tuples:<10,} {status:<15}')

    print('-' * 80)
    print(f'Total Tables: {total_tables}')
    print(f'Total Records: {total_records:,}')
    print(f'Average Records per Table: {total_records/total_tables:,.0f}')

    print(f'\n📈 DISTRIBUTION SUMMARY:')
    print(f'  ❌ Empty Tables: {len(empty_tables)}')
    print(f'  ⚠️  Low Tables (<10): {len(low_tables)}')
    print(f'  ✅ OK Tables (10-99): {len(ok_tables)}')
    print(f'  ✅ Good Tables (100-999): {len(good_tables)}')
    print(f'  ✅ Excellent Tables (1000+): {len(excellent_tables)}')

    if empty_tables:
        print(f'\n❌ EMPTY TABLES ({len(empty_tables)}):')
        for table, count in empty_tables:
            print(f'  - {table}: {count} records')

    if low_tables:
        print(f'\n⚠️  LOW RECORD TABLES ({len(low_tables)}):')
        for table, count in low_tables:
            print(f'  - {table}: {count} records')

    # Analyze specific table categories for district consistency
    print(f'\n🏫 DISTRICT SIZE CONSISTENCY ANALYSIS:')
    print('=' * 60)
    
    # Check student-related tables
    student_tables = [t for t in empty_tables + low_tables if 'student' in t[0].lower()]
    if student_tables:
        print(f'⚠️  Student-related tables with low records: {len(student_tables)}')
        for table, count in student_tables:
            print(f'  - {table}: {count} records')
    
    # Check teacher-related tables
    teacher_tables = [t for t in empty_tables + low_tables if 'teacher' in t[0].lower()]
    if teacher_tables:
        print(f'⚠️  Teacher-related tables with low records: {len(teacher_tables)}')
        for table, count in teacher_tables:
            print(f'  - {table}: {count} records')
    
    # Check class-related tables
    class_tables = [t for t in empty_tables + low_tables if 'class' in t[0].lower()]
    if class_tables:
        print(f'⚠️  Class-related tables with low records: {len(class_tables)}')
        for table, count in class_tables:
            print(f'  - {table}: {count} records')
    
    # Check activity-related tables
    activity_tables = [t for t in empty_tables + low_tables if 'activity' in t[0].lower()]
    if activity_tables:
        print(f'⚠️  Activity-related tables with low records: {len(activity_tables)}')
        for table, count in activity_tables:
            print(f'  - {table}: {count} records')

    session.close()
    return {
        'total_tables': total_tables,
        'total_records': total_records,
        'empty_tables': empty_tables,
        'low_tables': low_tables,
        'ok_tables': ok_tables,
        'good_tables': good_tables,
        'excellent_tables': excellent_tables
    }

if __name__ == "__main__":
    analyze_record_distribution()
