#!/usr/bin/env python3
"""
Balance Elementary School Distribution

This script redistributes students evenly among the 4 elementary schools
to create a realistic distribution of ~400-500 students each.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from sqlalchemy import create_engine, text
from app.core.database import SessionLocal

def balance_elementary_distribution():
    """Balance students across the 4 elementary schools"""
    print("🔧 BALANCING ELEMENTARY SCHOOL DISTRIBUTION")
    print("=" * 50)
    
    session = SessionLocal()
    
    try:
        # Step 1: Get current elementary school distribution
        print("\n📊 CURRENT ELEMENTARY DISTRIBUTION:")
        result = session.execute(text("""
            SELECT s.id, s.name, COUNT(ss.student_id) as student_count
            FROM schools s
            LEFT JOIN student_school_enrollments ss ON s.id = ss.school_id
            WHERE s.school_type = 'ELEMENTARY'
            GROUP BY s.id, s.name
            ORDER BY s.name
        """))
        
        elementary_schools = []
        total_elementary_students = 0
        for row in result:
            elementary_schools.append({
                'id': row[0],
                'name': row[1],
                'students': row[2]
            })
            total_elementary_students += row[2]
            print(f"  {row[1]}: {row[2]:,} students")
        
        print(f"\nTotal elementary students: {total_elementary_students:,}")
        
        # Step 2: Calculate target distribution
        target_per_school = total_elementary_students // len(elementary_schools)
        remainder = total_elementary_students % len(elementary_schools)
        
        print(f"\n🎯 TARGET DISTRIBUTION:")
        print(f"  Target per school: ~{target_per_school:,} students")
        print(f"  Remainder: {remainder} students")
        
        # Step 3: Get all elementary students with their current school
        print(f"\n🔄 REDISTRIBUTING STUDENTS...")
        
        # Get all elementary students (K-5)
        elementary_students = session.execute(text("""
            SELECT s.id, s.grade_level, ss.school_id
            FROM students s
            JOIN student_school_enrollments ss ON s.id = ss.student_id
            JOIN schools sch ON ss.school_id = sch.id
            WHERE sch.school_type = 'ELEMENTARY'
            ORDER BY s.id
        """)).fetchall()
        
        print(f"  Found {len(elementary_students)} elementary students to redistribute")
        
        # Step 4: Redistribute students evenly
        students_per_school = len(elementary_students) // len(elementary_schools)
        extra_students = len(elementary_students) % len(elementary_schools)
        
        student_index = 0
        for i, school in enumerate(elementary_schools):
            # Calculate how many students this school should get
            students_for_this_school = students_per_school
            if i < extra_students:  # Distribute remainder to first few schools
                students_for_this_school += 1
            
            print(f"  {school['name']}: {students_for_this_school} students")
            
            # Assign students to this school
            for j in range(students_for_this_school):
                if student_index < len(elementary_students):
                    student_id = elementary_students[student_index][0]
                    
                    # Update student school enrollment
                    session.execute(text("""
                        UPDATE student_school_enrollments 
                        SET school_id = :new_school_id
                        WHERE student_id = :student_id
                    """), {
                        "new_school_id": school['id'],
                        "student_id": student_id
                    })
                    
                    student_index += 1
        
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
        print(f"\n✅ FINAL ELEMENTARY DISTRIBUTION:")
        result = session.execute(text("""
            SELECT s.name, COUNT(ss.student_id) as student_count
            FROM schools s
            LEFT JOIN student_school_enrollments ss ON s.id = ss.school_id
            WHERE s.school_type = 'ELEMENTARY'
            GROUP BY s.id, s.name
            ORDER BY s.name
        """))
        
        total_students = 0
        for row in result:
            print(f"  {row[0]}: {row[1]:,} students")
            total_students += row[1]
        
        print(f"\n📊 Total elementary students: {total_students:,}")
        print(f"📊 Average per elementary school: {total_students // len(elementary_schools):,}")
        
        # Show overall distribution
        print(f"\n📊 OVERALL SCHOOL DISTRIBUTION:")
        result = session.execute(text("""
            SELECT s.name, s.school_type, s.min_grade, s.max_grade, 
                   COUNT(ss.student_id) as student_count
            FROM schools s
            LEFT JOIN student_school_enrollments ss ON s.id = ss.school_id
            GROUP BY s.id, s.name, s.school_type, s.min_grade, s.max_grade
            ORDER BY s.school_type, s.name
        """))
        
        total_all_students = 0
        for row in result:
            print(f"  {row[0]} ({row[1]}) - Grades {row[2]}-{row[3]}: {row[4]:,} students")
            total_all_students += row[4]
        
        print(f"\n📊 Total students: {total_all_students:,}")
        print(f"📊 Total schools: 6")
        
        print("\n🎉 Elementary school distribution balanced successfully!")
        
    except Exception as e:
        print(f"❌ Error balancing distribution: {e}")
        session.rollback()
        raise
    finally:
        session.close()

if __name__ == "__main__":
    balance_elementary_distribution()
