#!/usr/bin/env python3
"""
Fix Missing Teacher References
Updates tables that have NULL teacher references to use valid teacher IDs
"""

import os
import sys
from pathlib import Path
import random

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

def fix_missing_teacher_references():
    """Fix missing teacher references in tables"""
    
    print("🔧 FIXING MISSING TEACHER REFERENCES")
    print("=" * 60)
    
    # Use the Azure PostgreSQL connection
    DATABASE_URL = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        raise RuntimeError('DATABASE_URL must be set in the environment')
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Get available teacher IDs
        result = session.execute(text("SELECT id FROM teachers ORDER BY id"))
        teacher_ids = [row[0] for row in result.fetchall()]
        print(f"📊 Available teacher IDs: {len(teacher_ids)} teachers")
        
        if not teacher_ids:
            print("❌ No teachers found! Cannot fix references.")
            return False
        
        # 1. Fix pe_lesson_plans
        print("\n1️⃣ FIXING PE_LESSON_PLANS")
        print("-" * 40)
        
        result = session.execute(text("SELECT COUNT(*) FROM pe_lesson_plans WHERE teacher_id IS NULL"))
        null_count = result.scalar()
        print(f"Records with NULL teacher_id: {null_count}")
        
        if null_count > 0:
            # Update with random teacher IDs
            session.execute(text("""
                UPDATE pe_lesson_plans 
                SET teacher_id = (
                    SELECT id FROM teachers 
                    ORDER BY RANDOM() 
                    LIMIT 1
                )
                WHERE teacher_id IS NULL
            """))
            session.commit()
            print(f"✅ Updated {null_count} pe_lesson_plans with teacher references")
        
        # 2. Fix exercises
        print("\n2️⃣ FIXING EXERCISES")
        print("-" * 40)
        
        result = session.execute(text("SELECT COUNT(*) FROM exercises WHERE created_by IS NULL"))
        null_count = result.scalar()
        print(f"Records with NULL created_by: {null_count}")
        
        if null_count > 0:
            # Update with random teacher IDs
            session.execute(text("""
                UPDATE exercises 
                SET created_by = (
                    SELECT id FROM teachers 
                    ORDER BY RANDOM() 
                    LIMIT 1
                )
                WHERE created_by IS NULL
            """))
            session.commit()
            print(f"✅ Updated {null_count} exercises with teacher references")
        
        # 3. Fix grades
        print("\n3️⃣ FIXING GRADES")
        print("-" * 40)
        
        result = session.execute(text("SELECT COUNT(*) FROM grades WHERE grader_id IS NULL"))
        null_count = result.scalar()
        print(f"Records with NULL grader_id: {null_count}")
        
        if null_count > 0:
            # Update with random teacher IDs
            session.execute(text("""
                UPDATE grades 
                SET grader_id = (
                    SELECT id FROM teachers 
                    ORDER BY RANDOM() 
                    LIMIT 1
                )
                WHERE grader_id IS NULL
            """))
            session.commit()
            print(f"✅ Updated {null_count} grades with teacher references")
        
        # 4. Verify fixes
        print("\n4️⃣ VERIFICATION")
        print("-" * 40)
        
        # Check pe_lesson_plans
        result = session.execute(text("SELECT COUNT(*) FROM pe_lesson_plans WHERE teacher_id IN (SELECT id FROM teachers)"))
        valid_pe_lesson_plans = result.scalar()
        print(f"pe_lesson_plans with valid teacher_id: {valid_pe_lesson_plans}")
        
        # Check exercises
        result = session.execute(text("SELECT COUNT(*) FROM exercises WHERE created_by IN (SELECT id FROM teachers)"))
        valid_exercises = result.scalar()
        print(f"exercises with valid created_by: {valid_exercises}")
        
        # Check grades
        result = session.execute(text("SELECT COUNT(*) FROM grades WHERE grader_id IN (SELECT id FROM teachers)"))
        valid_grades = result.scalar()
        print(f"grades with valid grader_id: {valid_grades}")
        
        # Check for any remaining NULL values
        result = session.execute(text("SELECT COUNT(*) FROM pe_lesson_plans WHERE teacher_id IS NULL"))
        remaining_pe = result.scalar()
        result = session.execute(text("SELECT COUNT(*) FROM exercises WHERE created_by IS NULL"))
        remaining_ex = result.scalar()
        result = session.execute(text("SELECT COUNT(*) FROM grades WHERE grader_id IS NULL"))
        remaining_gr = result.scalar()
        
        print(f"\nRemaining NULL values:")
        print(f"  pe_lesson_plans: {remaining_pe}")
        print(f"  exercises: {remaining_ex}")
        print(f"  grades: {remaining_gr}")
        
        if remaining_pe == 0 and remaining_ex == 0 and remaining_gr == 0:
            print("\n🎉 ALL TEACHER REFERENCES FIXED SUCCESSFULLY!")
            return True
        else:
            print("\n⚠️  SOME NULL VALUES REMAIN")
            return False
            
    except Exception as e:
        print(f"❌ Fix failed: {e}")
        session.rollback()
        return False
    finally:
        session.close()

if __name__ == "__main__":
    success = fix_missing_teacher_references()
    if success:
        print("\n✅ TEACHER REFERENCES FIXED - READY FOR FULL SCRIPT")
    else:
        print("\n❌ FIX FAILED - CHECK ISSUES")
