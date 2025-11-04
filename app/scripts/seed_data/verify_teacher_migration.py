#!/usr/bin/env python3
"""
Verify Teacher Migration Data Integrity
Checks all tables that should reference teachers to ensure correct data migration
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

def verify_teacher_migration():
    """Verify all teacher-related tables have correct data"""
    
    print("🔍 TEACHER MIGRATION DATA VERIFICATION")
    print("=" * 60)
    
    # Use the Azure PostgreSQL connection
    DATABASE_URL = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        raise RuntimeError('DATABASE_URL must be set in the environment')
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # 1. Check teachers table
        print("\n1️⃣ TEACHERS TABLE")
        print("-" * 40)
        
        result = session.execute(text("SELECT COUNT(*) FROM teachers"))
        teacher_count = result.scalar()
        print(f"✅ Teachers table: {teacher_count} records")
        
        # Show sample teachers
        result = session.execute(text("SELECT id, first_name, last_name, email FROM teachers LIMIT 5"))
        teachers = result.fetchall()
        print("Sample teachers:")
        for teacher in teachers:
            print(f"  ID: {teacher[0]}, Name: {teacher[1]} {teacher[2]}, Email: {teacher[3]}")
        
        # 2. Check tables that should reference teachers
        print("\n2️⃣ TEACHER-RELATED TABLES VERIFICATION")
        print("-" * 40)
        
        # Define tables that should have teacher references
        teacher_tables = [
            ('educational_teachers', 'teacher_id'),
            ('physical_education_teachers', 'teacher_id'),
            ('teacher_school_assignments', 'teacher_id'),
            ('pe_lesson_plans', 'teacher_id'),
            ('physical_education_classes', 'teacher_id'),
            ('workout_plans', 'teacher_id'),
            ('workout_sessions', 'teacher_id'),
            ('safety_incident_base', 'teacher_id'),
            ('safety_incidents', 'teacher_id'),
            ('activity_assessments', 'assessor_id'),
            ('skill_assessment_assessments', 'assessor_id'),
            ('lessons', 'teacher_id'),
            ('exercises', 'created_by'),
            ('adapted_routines', 'creator_id'),
            ('physical_education_routines', 'created_by'),
            ('grades', 'grader_id'),
            ('feedback', 'teacher_id'),
            ('feedback_actions', 'teacher_id'),
            ('feedback_comments', 'teacher_id')
        ]
        
        total_records = 0
        verified_tables = 0
        
        for table_name, column_name in teacher_tables:
            try:
                # Check if table exists and has records
                result = session.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                count = result.scalar()
                
                if count > 0:
                    # Check if the teacher_id column has valid references
                    result = session.execute(text(f"""
                        SELECT COUNT(*) 
                        FROM {table_name} 
                        WHERE {column_name} IN (SELECT id FROM teachers)
                    """))
                    valid_refs = result.scalar()
                    
                    if valid_refs == count:
                        print(f"✅ {table_name}: {count} records, all {column_name} references valid")
                        verified_tables += 1
                    else:
                        print(f"⚠️  {table_name}: {count} records, {valid_refs}/{count} {column_name} references valid")
                    
                    total_records += count
                else:
                    print(f"ℹ️  {table_name}: 0 records (empty table)")
                    
            except Exception as e:
                print(f"❌ {table_name}: Error checking - {e}")
        
        # 3. Check for orphaned references
        print("\n3️⃣ ORPHANED REFERENCES CHECK")
        print("-" * 40)
        
        orphaned_tables = []
        for table_name, column_name in teacher_tables:
            try:
                result = session.execute(text(f"""
                    SELECT COUNT(*) 
                    FROM {table_name} 
                    WHERE {column_name} IS NOT NULL 
                    AND {column_name} NOT IN (SELECT id FROM teachers)
                """))
                orphaned_count = result.scalar()
                
                if orphaned_count > 0:
                    print(f"⚠️  {table_name}: {orphaned_count} orphaned {column_name} references")
                    orphaned_tables.append((table_name, orphaned_count))
                else:
                    print(f"✅ {table_name}: No orphaned {column_name} references")
                    
            except Exception as e:
                print(f"❌ {table_name}: Error checking orphaned references - {e}")
        
        # 4. Check users table still has teachers
        print("\n4️⃣ USERS TABLE VERIFICATION")
        print("-" * 40)
        
        result = session.execute(text("SELECT COUNT(*) FROM users"))
        user_count = result.scalar()
        print(f"📊 Users table: {user_count} records")
        
        # Check if users still have teacher records
        result = session.execute(text("""
            SELECT COUNT(*) 
            FROM users u 
            WHERE EXISTS (SELECT 1 FROM teachers t WHERE t.user_id = u.id)
        """))
        users_with_teachers = result.scalar()
        print(f"📊 Users with teacher records: {users_with_teachers}")
        
        # 5. Summary
        print("\n5️⃣ VERIFICATION SUMMARY")
        print("-" * 40)
        print(f"✅ Teachers table: {teacher_count} records")
        print(f"✅ Verified tables: {verified_tables}/{len(teacher_tables)}")
        print(f"✅ Total records in teacher-related tables: {total_records}")
        print(f"✅ Orphaned references: {len(orphaned_tables)} tables")
        
        if len(orphaned_tables) == 0:
            print("🎉 ALL TEACHER MIGRATIONS VERIFIED SUCCESSFULLY!")
            return True
        else:
            print("⚠️  SOME ISSUES FOUND - CHECK ORPHANED REFERENCES")
            return False
            
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False
    finally:
        session.close()

if __name__ == "__main__":
    success = verify_teacher_migration()
    if success:
        print("\n✅ TEACHER MIGRATION DATA INTEGRITY VERIFIED")
    else:
        print("\n❌ TEACHER MIGRATION DATA INTEGRITY ISSUES FOUND")
