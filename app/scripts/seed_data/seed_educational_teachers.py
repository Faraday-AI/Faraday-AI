#!/usr/bin/env python3
"""
Seed educational_teachers table with basic teacher records.
This is needed before seeding lesson_plans since they reference this table.
"""

import json
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import SessionLocal


def seed_educational_teachers(session: Session) -> None:
    """Seed the educational_teachers table with basic teacher records."""
    print("Seeding educational teachers...")
    
    try:
        # Check if table already has data
        result = session.execute(text("SELECT COUNT(*) FROM educational_teachers")).scalar()
        if result > 0:
            print(f"Educational teachers table already has {result} records. Skipping seeding.")
            return
        
        # Get existing dashboard users to reference
        dashboard_users = session.execute(text("SELECT id, full_name FROM dashboard_users WHERE role = 'TEACHER' ORDER BY id")).fetchall()
        if not dashboard_users:
            print("No TEACHER users found in dashboard_users table.")
            return
        
        print(f"Found {len(dashboard_users)} TEACHER users to reference...")
        
        # Create basic teacher records, referencing existing dashboard users
        teachers_data = [
            {
                "user_id": dashboard_users[0][0],  # Reference first teacher
                "name": "Sarah Johnson",
                "school": "Lincoln Elementary",
                "department": "Physical Education",
                "subjects": json.dumps(["Physical Education", "Health"]),
                "grade_levels": json.dumps(["K", "1", "2", "3", "4", "5"]),
                "certifications": json.dumps(["PE Teacher Certification", "First Aid"]),
                "specialties": json.dumps(["Elementary PE", "Adaptive PE"]),
                "bio": "Experienced elementary PE teacher with 8 years of experience.",
                "status": "ACTIVE",
                "is_active": True
            },
            {
                "user_id": dashboard_users[1][0] if len(dashboard_users) > 1 else dashboard_users[0][0],  # Reference second teacher
                "name": "Michael Chen",
                "school": "Riverside Middle School",
                "department": "Physical Education",
                "subjects": json.dumps(["Physical Education", "Sports"]),
                "grade_levels": json.dumps(["6", "7", "8"]),
                "certifications": json.dumps(["PE Teacher Certification", "Coaching License"]),
                "specialties": json.dumps(["Team Sports", "Fitness"]),
                "bio": "Middle school PE teacher and basketball coach.",
                "status": "ACTIVE",
                "is_active": True
            },
            {
                "user_id": dashboard_users[2][0] if len(dashboard_users) > 2 else dashboard_users[0][0],  # Reference third teacher
                "name": "Emily Rodriguez",
                "school": "Central High School",
                "department": "Physical Education",
                "subjects": json.dumps(["Physical Education", "Health Science"]),
                "grade_levels": json.dumps(["9", "10", "11", "12"]),
                "certifications": json.dumps(["PE Teacher Certification", "Health Education"]),
                "specialties": json.dumps(["High School PE", "Health Education"]),
                "bio": "High school PE teacher with focus on health and wellness.",
                "status": "ACTIVE",
                "is_active": True
            },
            {
                "user_id": dashboard_users[3][0] if len(dashboard_users) > 3 else dashboard_users[0][0],  # Reference fourth teacher
                "name": "David Thompson",
                "school": "Oakwood Elementary",
                "department": "Physical Education",
                "subjects": json.dumps(["Physical Education"]),
                "grade_levels": json.dumps(["K", "1", "2", "3", "4", "5"]),
                "certifications": json.dumps(["PE Teacher Certification"]),
                "specialties": json.dumps(["Elementary PE", "Movement Education"]),
                "bio": "Elementary PE teacher specializing in fundamental movement skills.",
                "status": "ACTIVE",
                "is_active": True
            },
            {
                "user_id": dashboard_users[4][0] if len(dashboard_users) > 4 else dashboard_users[0][0],  # Reference fifth teacher
                "name": "Lisa Park",
                "school": "Maple Middle School",
                "department": "Physical Education",
                "subjects": json.dumps(["Physical Education", "Dance"]),
                "grade_levels": json.dumps(["6", "7", "8"]),
                "certifications": json.dumps(["PE Teacher Certification", "Dance Instruction"]),
                "specialties": json.dumps(["Dance", "Creative Movement"]),
                "bio": "Middle school PE teacher with dance and creative movement expertise.",
                "status": "ACTIVE",
                "is_active": True
            }
        ]
        
        # Insert teachers
        for i, teacher_data in enumerate(teachers_data, 1):
            try:
                # Insert with current timestamp
                now = datetime.now(timezone.utc)
                insert_query = text("""
                    INSERT INTO educational_teachers (
                        user_id, name, school, department, subjects, grade_levels, certifications,
                        specialties, bio, status, is_active, created_at, updated_at
                    ) VALUES (
                        :user_id, :name, :school, :department, :subjects, :grade_levels, :certifications,
                        :specialties, :bio, :status, :is_active, :created_at, :updated_at
                    ) RETURNING id
                """)
                
                result = session.execute(insert_query, {
                    **teacher_data,
                    "created_at": now,
                    "updated_at": now
                })
                
                teacher_id = result.scalar()
                print(f"  ✅ Created teacher {i}/5: {teacher_data['name']} (ID: {teacher_id})")
                
            except Exception as e:
                print(f"  ❌ Error creating teacher {teacher_data['name']}: {e}")
                session.rollback()
                return
        
        session.commit()
        print(f"✅ Successfully seeded {len(teachers_data)} educational teachers!")
        
        # Verify the seeding
        count = session.execute(text("SELECT COUNT(*) FROM educational_teachers")).scalar()
        print(f"📊 Total educational teachers in database: {count} records")
        
    except Exception as e:
        print(f"❌ Error seeding educational teachers: {e}")
        session.rollback()


def main():
    """Main function to run the seeding."""
    session = SessionLocal()
    try:
        seed_educational_teachers(session)
    finally:
        session.close()


if __name__ == "__main__":
    main() 