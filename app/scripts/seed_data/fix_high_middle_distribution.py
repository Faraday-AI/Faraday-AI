#!/usr/bin/env python3
"""
Fix High School vs Middle School Distribution

High school should have more students than middle school since it covers 4 grades vs 3 grades.
Target: Middle ~600 students, High ~800 students
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from sqlalchemy import create_engine, text
from app.core.database import SessionLocal

def fix_high_middle_distribution():
    """Fix the distribution between middle and high school"""
    print("🔧 FIXING HIGH SCHOOL vs MIDDLE SCHOOL DISTRIBUTION")
    print("=" * 60)
    
    session = SessionLocal()
    
    try:
        # Step 1: Get current middle/high school distribution
        print("\n📊 CURRENT MIDDLE/HIGH DISTRIBUTION:")
        result = session.execute(text("""
            SELECT s.id, s.name, s.school_type, s.min_grade, s.max_grade, 
                   COUNT(ss.student_id) as student_count
            FROM schools s
            LEFT JOIN student_school_enrollments ss ON s.id = ss.school_id
            WHERE s.school_type IN ('MIDDLE', 'HIGH')
            GROUP BY s.id, s.name, s.school_type, s.min_grade, s.max_grade
            ORDER BY s.school_type
        """))
        
        middle_school = None
        high_school = None
        
        for row in result:
            school_info = {
                'id': row[0],
                'name': row[1],
                'type': row[2],
                'min_grade': row[3],
                'max_grade': row[4],
                'students': row[5]
            }
            print(f"  {row[1]} ({row[2]}) - Grades {row[3]}-{row[4]}: {row[5]:,} students")
            
            if row[2] == 'MIDDLE':
                middle_school = school_info
            elif row[2] == 'HIGH':
                high_school = school_info
        
        if not middle_school or not high_school:
            print("❌ Could not find both middle and high schools")
            return
        
        # Step 2: Calculate target distribution
        total_middle_high_students = middle_school['students'] + high_school['students']
        print(f"\nTotal middle + high students: {total_middle_high_students:,}")
        
        # Target: Middle ~600, High ~800 (more realistic for 3 vs 4 grades)
        target_middle = 600
        target_high = 800
        
        # If we don't have enough students, adjust proportionally
        if total_middle_high_students < (target_middle + target_high):
            # Scale down proportionally
            scale_factor = total_middle_high_students / (target_middle + target_high)
            target_middle = int(target_middle * scale_factor)
            target_high = int(target_high * scale_factor)
        
        print(f"\n🎯 TARGET DISTRIBUTION:")
        print(f"  Middle School (6-8): ~{target_middle:,} students (~{target_middle//3:,} per grade)")
        print(f"  High School (9-12): ~{target_high:,} students (~{target_high//4:,} per grade)")
        
        # Step 3: Get all middle and high school students
        print(f"\n🔄 REDISTRIBUTING STUDENTS...")
        
        # Get all middle and high school students
        middle_high_students = session.execute(text("""
            SELECT s.id, s.grade_level, ss.school_id
            FROM students s
            JOIN student_school_enrollments ss ON s.id = ss.student_id
            JOIN schools sch ON ss.school_id = sch.id
            WHERE sch.school_type IN ('MIDDLE', 'HIGH')
            ORDER BY s.grade_level, s.id
        """)).fetchall()
        
        print(f"  Found {len(middle_high_students)} middle/high students to redistribute")
        
        # Step 4: Redistribute students
        middle_students = []
        high_students = []
        
        for student_id, grade_level, current_school_id in middle_high_students:
            if grade_level in ['SIXTH', 'SEVENTH', 'EIGHTH']:
                middle_students.append(student_id)
            elif grade_level in ['NINTH', 'TENTH', 'ELEVENTH', 'TWELFTH']:
                high_students.append(student_id)
        
        print(f"  Middle school students (6-8): {len(middle_students)}")
        print(f"  High school students (9-12): {len(high_students)}")
        
        # If we need to move students between schools
        if len(middle_students) > target_middle:
            # Move excess middle students to high school
            excess = len(middle_students) - target_middle
            students_to_move = middle_students[target_middle:]
            
            print(f"  Moving {excess} students from middle to high school...")
            for student_id in students_to_move:
                session.execute(text("""
                    UPDATE student_school_enrollments 
                    SET school_id = :new_school_id
                    WHERE student_id = :student_id
                """), {
                    "new_school_id": high_school['id'],
                    "student_id": student_id
                })
        
        elif len(high_students) > target_high:
            # Move excess high students to middle school
            excess = len(high_students) - target_high
            students_to_move = high_students[target_high:]
            
            print(f"  Moving {excess} students from high to middle school...")
            for student_id in students_to_move:
                session.execute(text("""
                    UPDATE student_school_enrollments 
                    SET school_id = :new_school_id
                    WHERE student_id = :student_id
                """), {
                    "new_school_id": middle_school['id'],
                    "student_id": student_id
                })
        
        # Step 5: Update school enrollment counts
        print(f"\n📊 Updating school enrollment counts...")
        session.execute(text("""
            UPDATE schools 
            SET current_enrollment = (
                SELECT COUNT(*) 
                FROM student_school_enrollments ss 
                WHERE ss.school_id = schools.id
            )
        """))
        
        session.commit()
        
        # Step 6: Show final distribution
        print(f"\n✅ FINAL DISTRIBUTION:")
        result = session.execute(text("""
            SELECT s.name, s.school_type, s.min_grade, s.max_grade, 
                   COUNT(ss.student_id) as student_count
            FROM schools s
            LEFT JOIN student_school_enrollments ss ON s.id = ss.school_id
            GROUP BY s.id, s.name, s.school_type, s.min_grade, s.max_grade
            ORDER BY s.school_type, s.name
        """))
        
        total_students = 0
        for row in result:
            print(f"  {row[0]} ({row[1]}) - Grades {row[2]}-{row[3]}: {row[4]:,} students")
            total_students += row[4]
        
        print(f"\n📊 Total students: {total_students:,}")
        print(f"📊 Total schools: 6")
        
        print("\n🎉 High school vs middle school distribution fixed!")
        
    except Exception as e:
        print(f"❌ Error fixing distribution: {e}")
        session.rollback()
        raise
    finally:
        session.close()

if __name__ == "__main__":
    fix_high_middle_distribution()
