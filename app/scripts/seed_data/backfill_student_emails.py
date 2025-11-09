"""
Backfill missing student email addresses and parent contact information.

This script adds email addresses to students and beta_students that don't have them,
and ensures parent contact information is populated for communication tests.
"""

from sqlalchemy.orm import Session
from sqlalchemy import text
import random
import string
from datetime import datetime, timedelta


def backfill_student_emails(session: Session) -> dict:
    """
    Backfill email addresses for students and beta_students that don't have them.
    Also ensures parent contact information is populated.
    
    Returns:
        dict with counts of updated records
    """
    results = {
        'main_students_updated': 0,
        'beta_students_updated': 0,
        'main_parent_info_updated': 0,
        'beta_parent_info_updated': 0
    }
    
    print("\n📧 BACKFILLING STUDENT EMAIL ADDRESSES...")
    
    # 0. Check if students table is empty but enrollments exist - create students from enrollments
    student_count = session.execute(text("SELECT COUNT(*) FROM students")).scalar()
    enrollment_count = session.execute(text("SELECT COUNT(DISTINCT student_id) FROM physical_education_class_students")).scalar()
    
    if student_count == 0 and enrollment_count > 0:
        print(f"\n  ⚠️  Students table is empty but {enrollment_count:,} student enrollments exist")
        print(f"  🔄 Creating students from enrollment data...")
        
        # Get unique student_ids from enrollments
        student_ids = session.execute(text("""
            SELECT DISTINCT student_id
            FROM physical_education_class_students
            ORDER BY student_id
            LIMIT 5000
        """)).fetchall()
        
        created = 0
        for (student_id,) in student_ids:
            # Generate realistic student data
            first_names = ["Alex", "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Avery", "Quinn", "Sage", "River",
                          "Emma", "Noah", "Olivia", "Liam", "Sophia", "Mason", "Isabella", "Ethan", "Mia", "James"]
            last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
                         "Anderson", "Taylor", "Thomas", "Hernandez", "Moore", "Martin", "Jackson", "Thompson", "White", "Harris"]
            
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            email = f"{first_name.lower()}.{last_name.lower()}{student_id}@springfield.edu"
            parent_name = f"Parent {last_name}"
            parent_phone = f"973-555-{random.randint(1000, 9999)}"
            
            # Create student
            try:
                session.execute(text("""
                    INSERT INTO students (
                        id, first_name, last_name, email, date_of_birth,
                        gender, grade_level, status, level, category,
                        parent_name, parent_phone, emergency_contact,
                        created_at, updated_at
                    ) VALUES (
                        :id, :first_name, :last_name, :email, :dob,
                        :gender, :grade_level, :status, :level, :category,
                        :parent_name, :parent_phone, :emergency_contact,
                        NOW(), NOW()
                    ) ON CONFLICT (id) DO NOTHING
                """), {
                    'id': student_id,
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'dob': datetime.now() - timedelta(days=random.randint(365*13, 365*18)),
                    'gender': random.choice(['MALE', 'FEMALE']),
                    'grade_level': random.choice(['NINTH', 'TENTH', 'ELEVENTH', 'TWELFTH']),
                    'status': 'ACTIVE',
                    'level': random.choice(['BEGINNER', 'INTERMEDIATE', 'ADVANCED']),
                    'category': 'REGULAR',
                    'parent_name': parent_name,
                    'parent_phone': parent_phone,
                    'emergency_contact': parent_phone
                })
                created += 1
            except Exception as e:
                # Skip if student already exists or other error
                pass
        
        session.commit()
        print(f"    ✅ Created {created} students from enrollment data")
        results['main_students_updated'] += created
    
    # 1. Backfill main system students - process in batches
    print("\n  🔄 Processing main system students...")
    
    # Process in batches to handle large datasets efficiently
    batch_size = 1000
    offset = 0
    
    while True:
        # Get students without email
        students_batch = session.execute(text("""
            SELECT id, first_name, last_name, parent_phone, parent_name
            FROM students
            WHERE email IS NULL OR email = ''
            ORDER BY id
            LIMIT :limit OFFSET :offset
        """), {'limit': batch_size, 'offset': offset}).fetchall()
        
        if not students_batch:
            break
        
        if offset == 0:
            print(f"    Found students without email, processing in batches of {batch_size}...")
        
        for student in students_batch:
            student_id, first_name, last_name, parent_phone, parent_name = student
            
            # Generate email if missing
            if first_name and last_name:
                # Clean names for email
                first_clean = ''.join(c for c in first_name.lower() if c.isalnum())
                last_clean = ''.join(c for c in last_name.lower() if c.isalnum())
                email = f"{first_clean}.{last_clean}{student_id}@springfield.edu"
            else:
                email = f"student{student_id}@springfield.edu"
            
            # Generate parent info if missing
            parent_phone_new = parent_phone
            parent_name_new = parent_name
            
            if not parent_phone or parent_phone == '':
                parent_phone_new = f"973-555-{random.randint(1000, 9999)}"
            
            if not parent_name or parent_name == '':
                if last_name:
                    parent_name_new = f"Parent {last_name}"
                else:
                    parent_name_new = f"Parent of Student {student_id}"
            
            # Update student
            session.execute(text("""
                UPDATE students
                SET email = :email,
                    parent_phone = COALESCE(NULLIF(parent_phone, ''), :parent_phone),
                    parent_name = COALESCE(NULLIF(parent_name, ''), :parent_name),
                    updated_at = NOW()
                WHERE id = :student_id
            """), {
                'email': email,
                'parent_phone': parent_phone_new,
                'parent_name': parent_name_new,
                'student_id': student_id
            })
            
            results['main_students_updated'] += 1
            if not parent_phone or not parent_name:
                results['main_parent_info_updated'] += 1
        
        session.commit()
        offset += batch_size
        
        if offset % 5000 == 0:
            print(f"    Progress: {offset:,} students processed...")
    
    if results['main_students_updated'] > 0:
        print(f"    ✅ Updated {results['main_students_updated']:,} main system students")
    
    # 2. Backfill beta system students
    print("\n  🔄 Processing beta system students...")
    
    # Get beta students without email
    beta_students_without_email = session.execute(text("""
        SELECT id, first_name, last_name, parent_phone, parent_name
        FROM beta_students
        WHERE email IS NULL OR email = ''
    """)).fetchall()
    
    if beta_students_without_email:
        print(f"    Found {len(beta_students_without_email)} beta students without email")
        
        for student in beta_students_without_email:
            student_id, first_name, last_name, parent_phone, parent_name = student
            
            # Generate email if missing
            if first_name and last_name:
                first_clean = ''.join(c for c in first_name.lower() if c.isalnum())
                last_clean = ''.join(c for c in last_name.lower() if c.isalnum())
                # Use beta.test domain for beta students
                email = f"{first_clean}.{last_clean}.{str(student_id)[:8]}@beta.test"
            else:
                email = f"beta.student.{str(student_id)[:8]}@beta.test"
            
            # Generate parent info if missing
            parent_phone_new = parent_phone
            parent_name_new = parent_name
            
            if not parent_phone or parent_phone == '':
                parent_phone_new = f"973-555-{random.randint(1000, 9999)}"
            
            if not parent_name or parent_name == '':
                if last_name:
                    parent_name_new = f"Parent {last_name}"
                else:
                    parent_name_new = f"Parent of Beta Student {str(student_id)[:8]}"
            
            # Update beta student
            session.execute(text("""
                UPDATE beta_students
                SET email = :email,
                    parent_phone = COALESCE(NULLIF(parent_phone, ''), :parent_phone),
                    parent_name = COALESCE(NULLIF(parent_name, ''), :parent_name),
                    updated_at = NOW()
                WHERE id = :student_id
            """), {
                'email': email,
                'parent_phone': parent_phone_new,
                'parent_name': parent_name_new,
                'student_id': student_id
            })
            
            results['beta_students_updated'] += 1
            if not parent_phone or not parent_name:
                results['beta_parent_info_updated'] += 1
        
        session.commit()
        print(f"    ✅ Updated {results['beta_students_updated']} beta system students")
    
    
    print(f"\n✅ Email backfill complete!")
    print(f"   Main students updated: {results['main_students_updated']:,}")
    print(f"   Beta students updated: {results['beta_students_updated']:,}")
    print(f"   Parent info added: {results['main_parent_info_updated'] + results['beta_parent_info_updated']:,}")
    
    return results

