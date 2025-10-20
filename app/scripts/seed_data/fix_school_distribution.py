#!/usr/bin/env python3
"""
Fix School Distribution - Realistic K-12 School Structure

This script fixes the unrealistic school distribution by:
1. Reducing to 3 elementary schools (K-5)
2. 1 middle school (6-8) 
3. 1 high school (9-12)
4. Properly distributing students by grade level
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from sqlalchemy import create_engine, text
from app.core.database import SessionLocal

def fix_school_distribution():
    """Fix the school distribution to be realistic"""
    print("🔧 FIXING SCHOOL DISTRIBUTION - REALISTIC K-12 STRUCTURE")
    print("=" * 60)
    
    session = SessionLocal()
    
    try:
        # Step 1: Check current distribution
        print("\n📊 CURRENT DISTRIBUTION:")
        result = session.execute(text("""
            SELECT s.id, s.name, s.school_type, s.min_grade, s.max_grade, 
                   COUNT(ss.student_id) as student_count
            FROM schools s
            LEFT JOIN student_school_enrollments ss ON s.id = ss.school_id
            GROUP BY s.id, s.name, s.school_type, s.min_grade, s.max_grade
            ORDER BY s.school_type, s.name
        """))
        
        current_schools = []
        for row in result:
            current_schools.append({
                'id': row[0],
                'name': row[1], 
                'type': row[2],
                'min_grade': row[3],
                'max_grade': row[4],
                'students': row[5]
            })
            print(f"  {row[1]} ({row[2]}) - Grades {row[3]}-{row[4]}: {row[5]} students")
        
        # Step 2: Identify schools to keep and remove
        print("\n🎯 TARGET STRUCTURE:")
        print("  - 4 Elementary Schools (K-5): ~400-500 students each")
        print("  - 1 Middle School (6-8): ~600 students") 
        print("  - 1 High School (9-12): ~800 students")
        print("  - Total: ~2,800 students across 6 schools")
        
        # Keep the 4 largest elementary schools, 1 middle, 1 high
        elementary_schools = [s for s in current_schools if s['type'] == 'ELEMENTARY']
        middle_schools = [s for s in current_schools if s['type'] == 'MIDDLE']
        high_schools = [s for s in current_schools if s['type'] == 'HIGH']
        
        # Sort by student count and keep the top 4 elementary schools
        elementary_schools.sort(key=lambda x: x['students'], reverse=True)
        schools_to_keep = elementary_schools[:4] + middle_schools + high_schools
        schools_to_remove = [s for s in current_schools if s not in schools_to_keep]
        
        print(f"\n📋 Schools to keep ({len(schools_to_keep)}):")
        for school in schools_to_keep:
            print(f"  ✅ {school['name']} ({school['type']}) - {school['students']} students")
            
        print(f"\n📋 Schools to remove ({len(schools_to_remove)}):")
        for school in schools_to_remove:
            print(f"  ❌ {school['name']} ({school['type']}) - {school['students']} students")
        
        # Step 3: Move students from removed schools to kept schools
        if schools_to_remove:
            print(f"\n🔄 Moving students from removed schools...")
            
            for school_to_remove in schools_to_remove:
                if school_to_remove['students'] == 0:
                    continue
                    
                print(f"  Moving {school_to_remove['students']} students from {school_to_remove['name']}...")
                
                # Find appropriate target school based on grade level
                students_to_move = session.execute(text("""
                    SELECT s.id, s.grade_level
                    FROM students s
                    JOIN student_school_enrollments ss ON s.id = ss.student_id
                    WHERE ss.school_id = :school_id
                """), {"school_id": school_to_remove['id']}).fetchall()
                
                for student_id, grade_level in students_to_move:
                    # Find appropriate target school
                    target_school = None
                    
                    if grade_level in ['KINDERGARTEN', 'FIRST', 'SECOND', 'THIRD', 'FOURTH', 'FIFTH']:
                        # Elementary school
                        target_school = schools_to_keep[0]  # Use first elementary school
                    elif grade_level in ['SIXTH', 'SEVENTH', 'EIGHTH']:
                        # Middle school
                        target_school = next((s for s in schools_to_keep if s['type'] == 'MIDDLE'), None)
                    else:
                        # High school
                        target_school = next((s for s in schools_to_keep if s['type'] == 'HIGH'), None)
                    
                    if target_school:
                        # Update student school enrollment
                        session.execute(text("""
                            UPDATE student_school_enrollments 
                            SET school_id = :new_school_id
                            WHERE student_id = :student_id
                        """), {
                            "new_school_id": target_school['id'],
                            "student_id": student_id
                        })
                        
                        # Note: Students don't have direct school_id, only through enrollments
        
        # Step 4: Move related data from removed schools
        print(f"\n🔄 Moving related data from removed schools...")
        for school_to_remove in schools_to_remove:
            print(f"  Processing {school_to_remove['name']}...")
            
            # Find appropriate target school based on school type
            target_school = None
            if school_to_remove['type'] == 'ELEMENTARY':
                target_school = schools_to_keep[0]  # First elementary school
            elif school_to_remove['type'] == 'MIDDLE':
                target_school = next((s for s in schools_to_keep if s['type'] == 'MIDDLE'), None)
            elif school_to_remove['type'] == 'HIGH':
                target_school = next((s for s in schools_to_keep if s['type'] == 'HIGH'), None)
            
            if not target_school:
                print(f"    ⚠️  No target school found for {school_to_remove['name']}")
                continue
                
            # Move class assignments
            class_assignments = session.execute(text("""
                SELECT class_id, school_id 
                FROM class_school_assignments 
                WHERE school_id = :school_id
            """), {"school_id": school_to_remove['id']}).fetchall()
            
            if class_assignments:
                print(f"    Moving {len(class_assignments)} class assignments...")
                for class_id, old_school_id in class_assignments:
                    session.execute(text("""
                        UPDATE class_school_assignments 
                        SET school_id = :new_school_id
                        WHERE class_id = :class_id AND school_id = :old_school_id
                    """), {
                        "new_school_id": target_school['id'],
                        "class_id": class_id,
                        "old_school_id": old_school_id
                    })
            
            # Move school facilities
            facilities = session.execute(text("""
                SELECT COUNT(*) FROM school_facilities 
                WHERE school_id = :school_id
            """), {"school_id": school_to_remove['id']}).scalar()
            
            if facilities > 0:
                print(f"    Moving {facilities} school facilities...")
                session.execute(text("""
                    UPDATE school_facilities 
                    SET school_id = :new_school_id
                    WHERE school_id = :old_school_id
                """), {
                    "new_school_id": target_school['id'],
                    "old_school_id": school_to_remove['id']
                })
            
            # Move school academic years
            academic_years = session.execute(text("""
                SELECT COUNT(*) FROM school_academic_years 
                WHERE school_id = :school_id
            """), {"school_id": school_to_remove['id']}).scalar()
            
            if academic_years > 0:
                print(f"    Moving {academic_years} school academic years...")
                session.execute(text("""
                    UPDATE school_academic_years 
                    SET school_id = :new_school_id
                    WHERE school_id = :old_school_id
                """), {
                    "new_school_id": target_school['id'],
                    "old_school_id": school_to_remove['id']
                })
            
            # Move any other school-related data
            related_tables = [
                'school_administrators',
                'school_contacts', 
                'school_emergency_contacts',
                'school_health_services',
                'school_policies',
                'school_schedules',
                'school_transportation'
            ]
            
            for table in related_tables:
                try:
                    count = session.execute(text(f"""
                        SELECT COUNT(*) FROM {table} 
                        WHERE school_id = :school_id
                    """), {"school_id": school_to_remove['id']}).scalar()
                    
                    if count > 0:
                        print(f"    Moving {count} records from {table}...")
                        session.execute(text(f"""
                            UPDATE {table} 
                            SET school_id = :new_school_id
                            WHERE school_id = :old_school_id
                        """), {
                            "new_school_id": target_school['id'],
                            "old_school_id": school_to_remove['id']
                        })
                except Exception as e:
                    # Table might not exist, skip silently
                    pass
        
        # Step 5: Remove empty schools
        print(f"\n🗑️  Removing empty schools...")
        for school_to_remove in schools_to_remove:
            print(f"  Removing {school_to_remove['name']}...")
            session.execute(text("DELETE FROM schools WHERE id = :school_id"), 
                          {"school_id": school_to_remove['id']})
        
        # Step 6: Update school enrollment counts
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
        
        # Step 7: Show final distribution
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
            print(f"  {row[0]} ({row[1]}) - Grades {row[2]}-{row[3]}: {row[4]} students")
            total_students += row[4]
        
        print(f"\n📊 Total students: {total_students:,}")
        print(f"📊 Total schools: {len(schools_to_keep)}")
        print(f"📊 Average per school: {total_students // len(schools_to_keep):,}")
        
        print("\n🎉 School distribution fixed successfully!")
        
    except Exception as e:
        print(f"❌ Error fixing school distribution: {e}")
        session.rollback()
        raise
    finally:
        session.close()

if __name__ == "__main__":
    fix_school_distribution()
