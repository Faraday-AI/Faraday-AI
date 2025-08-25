import os
import sys
from datetime import datetime
from typing import List, Dict, Any
import json
from sqlalchemy.orm import Session
from pathlib import Path
from sqlalchemy import text

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.core.database import SessionLocal
from app.core.config import settings
from app.models.core.user import User
from app.models.mixins.status import BaseStatus

def seed_users(session: Session) -> None:
    """Seed the database with 32 PE teachers for our 6-school district structure."""
    print("Seeding PE teachers...")
    
    # Get school IDs for proper assignment
    schools = session.execute(text("SELECT id, name FROM schools ORDER BY name")).fetchall()
    school_map = {school.name: school.id for school in schools}
    
    if not school_map:
        print("Warning: No schools found. Teachers will not have school assignments.")
        school_map = {}
    
    # PE Teacher data for 6-school district structure
    users_data = [
        # Lincoln Elementary (3-4 Teachers)
        {
            "email": "jennifer.rodriguez@springfield.edu",
            "password_hash": "hashed_password_1",
            "first_name": "Jennifer",
            "last_name": "Rodriguez",
            "role": "teacher",
            "is_active": True,
            "user_type": "teacher",
            
            "preferences": {
                "school": "Lincoln Elementary School",
                "department": "Physical Education",
                "subjects": ["Physical Education", "Fundamental Movement"],
                "grade_levels": ["K", "1", "2"],
                "specialization": "K-2 PE Specialist (Fundamental Movement)"
            }
        },
        {
            "email": "david.johnson@springfield.edu",
            "password_hash": "hashed_password_2",
            "first_name": "David",
            "last_name": "Johnson",
            "role": "teacher",
            "is_active": True,
            "user_type": "teacher",
            "preferences": {
                "school": "Lincoln Elementary School",
                "department": "Physical Education",
                "subjects": ["Physical Education", "Basic Sports"],
                "grade_levels": ["3", "4", "5"],
                "specialization": "3-5 PE Specialist (Basic Sports)"
            }
        },
        {
            "email": "amanda.foster@springfield.edu",
            "password_hash": "hashed_password_3",
            "first_name": "Amanda",
            "last_name": "Foster",
            "role": "teacher",
            "is_active": True,
            "user_type": "teacher",
            "preferences": {
                "school": "Lincoln Elementary School",
                "department": "Physical Education",
                "subjects": ["Physical Education", "Adaptive PE"],
                "grade_levels": ["K", "1", "2", "3", "4", "5"],
                "specialization": "Adaptive PE Specialist"
            }
        },
        {
            "email": "rachel.green@springfield.edu",
            "password_hash": "hashed_password_4",
            "first_name": "Rachel",
            "last_name": "Green",
            "role": "teacher",
            "is_active": True,
            "user_type": "teacher",
            "preferences": {
                "school": "Lincoln Elementary School",
                "department": "Physical Education",
                "subjects": ["Physical Education", "Wellness"],
                "grade_levels": ["K", "1", "2", "3", "4", "5"],
                "specialization": "Wellness & Fitness Coordinator"
            }
        },
        
        # Washington Elementary (3-4 Teachers)
        {
            "email": "michael.chen@springfield.edu",
            "password_hash": "hashed_password_5",
            "first_name": "Michael",
            "last_name": "Chen",
            "role": "teacher",
            "is_active": True,
            "user_type": "teacher",
            "preferences": {
                "school": "Washington Elementary School",
                "department": "Physical Education",
                "subjects": ["Physical Education", "Coordination Development"],
                "grade_levels": ["K", "1", "2"],
                "specialization": "K-2 PE Specialist (Coordination Development)"
            }
        },
        {
            "email": "lisa.thompson@springfield.edu",
            "password_hash": "hashed_password_6",
            "first_name": "Lisa",
            "last_name": "Thompson",
            "role": "teacher",
            "is_active": True,
            "user_type": "teacher",
            "preferences": {
                "school": "Washington Elementary School",
                "department": "Physical Education",
                "subjects": ["Physical Education", "Team Sports"],
                "grade_levels": ["3", "4", "5"],
                "specialization": "3-5 PE Specialist (Team Sports)"
            }
        },
        {
            "email": "kevin.lee@springfield.edu",
            "password_hash": "hashed_password_7",
            "first_name": "Kevin",
            "last_name": "Lee",
            "role": "teacher",
            "is_active": True,
            "user_type": "teacher",
            "preferences": {
                "school": "Washington Elementary School",
                "department": "Physical Education",
                "subjects": ["Physical Education", "Adaptive PE"],
                "grade_levels": ["K", "1", "2", "3", "4", "5"],
                "specialization": "Adaptive PE Specialist"
            }
        },
        {
            "email": "sarah.wilson@springfield.edu",
            "password_hash": "hashed_password_8",
            "first_name": "Sarah",
            "last_name": "Wilson",
            "role": "teacher",
            "is_active": True,
            "user_type": "teacher",
            "preferences": {
                "school": "Washington Elementary School",
                "department": "Physical Education",
                "subjects": ["Physical Education", "Sports Skills"],
                "grade_levels": ["K", "1", "2", "3", "4", "5"],
                "specialization": "Sports Skills Coordinator"
            }
        },
        
        # Roosevelt Elementary (3-4 Teachers)
        {
            "email": "emily.davis@springfield.edu",
            "password_hash": "hashed_password_9",
            "first_name": "Emily",
            "last_name": "Davis",
            "role": "teacher",
            "is_active": True,
            "user_type": "teacher",
            "preferences": {
                "school": "Roosevelt Elementary School",
                "department": "Physical Education",
                "subjects": ["Physical Education", "Fitness & Wellness"],
                "grade_levels": ["K", "1", "2"],
                "specialization": "K-2 PE Specialist (Fitness & Wellness)"
            }
        },
        {
            "email": "robert.garcia@springfield.edu",
            "password_hash": "hashed_password_10",
            "first_name": "Robert",
            "last_name": "Garcia",
            "role": "teacher",
            "is_active": True,
            "user_type": "teacher",
            "preferences": {
                "school": "Roosevelt Elementary School",
                "department": "Physical Education",
                "subjects": ["Physical Education", "Basic Athletics"],
                "grade_levels": ["3", "4", "5"],
                "specialization": "3-5 PE Specialist (Basic Athletics)"
            }
        },
        {
            "email": "patricia.brown@springfield.edu",
            "password_hash": "hashed_password_11",
            "first_name": "Patricia",
            "last_name": "Brown",
            "role": "teacher",
            "is_active": True,
            "user_type": "teacher",
            "preferences": {
                "school": "Roosevelt Elementary School",
                "department": "Physical Education",
                "subjects": ["Physical Education", "Adaptive PE"],
                "grade_levels": ["K", "1", "2", "3", "4", "5"],
                "specialization": "Adaptive PE Specialist"
            }
        },
        {
            "email": "james.wilson@springfield.edu",
            "password_hash": "hashed_password_12",
            "first_name": "James",
            "last_name": "Wilson",
            "role": "teacher",
            "is_active": True,
            "user_type": "teacher",
            "preferences": {
                "school": "Roosevelt Elementary School",
                "department": "Physical Education",
                "subjects": ["Physical Education", "Health & Wellness"],
                "grade_levels": ["K", "1", "2", "3", "4", "5"],
                "specialization": "Health & Wellness Coordinator"
            }
        },
        
        # Jefferson Elementary (3-4 Teachers)
        {
            "email": "daniel.martinez@springfield.edu",
            "password_hash": "hashed_password_13",
            "first_name": "Daniel",
            "last_name": "Martinez",
            "role": "teacher",
            "is_active": True,
            "user_type": "teacher",
            "preferences": {
                "school": "Jefferson Elementary School",
                "department": "Physical Education",
                "subjects": ["Physical Education", "Inclusive Sports"],
                "grade_levels": ["K", "1", "2"],
                "specialization": "K-2 PE Specialist (Inclusive Sports)"
            }
        },
        {
            "email": "stephanie.clark@springfield.edu",
            "password_hash": "hashed_password_14",
            "first_name": "Stephanie",
            "last_name": "Clark",
            "role": "teacher",
            "is_active": True,
            "user_type": "teacher",
            "preferences": {
                "school": "Jefferson Elementary School",
                "department": "Physical Education",
                "subjects": ["Physical Education", "Adaptive PE"],
                "grade_levels": ["3", "4", "5"],
                "specialization": "3-5 PE Specialist (Adaptive PE)"
            }
        },
        {
            "email": "nicole.foster@springfield.edu",
            "password_hash": "hashed_password_15",
            "first_name": "Nicole",
            "last_name": "Foster",
            "role": "teacher",
            "is_active": True,
            "user_type": "teacher",
            "preferences": {
                "school": "Jefferson Elementary School",
                "department": "Physical Education",
                "subjects": ["Physical Education", "Special Needs PE"],
                "grade_levels": ["K", "1", "2", "3", "4", "5"],
                "specialization": "Special Needs PE Specialist"
            }
        },
        {
            "email": "andrew.thompson@springfield.edu",
            "password_hash": "hashed_password_16",
            "first_name": "Andrew",
            "last_name": "Thompson",
            "role": "teacher",
            "is_active": True,
            "user_type": "teacher",
            "preferences": {
                "school": "Jefferson Elementary School",
                "department": "Physical Education",
                "subjects": ["Physical Education", "Adaptive Sports"],
                "grade_levels": ["K", "1", "2", "3", "4", "5"],
                "specialization": "Adaptive Sports Coordinator"
            }
        },
        
        # Springfield Middle School (6-7 Teachers)
        {
            "email": "thomas.williams@springfield.edu",
            "password_hash": "hashed_password_17",
            "first_name": "Thomas",
            "last_name": "Williams",
            "role": "teacher",
            "is_active": True,
            "user_type": "teacher",
            "preferences": {
                "school": "Springfield Middle School",
                "department": "Physical Education",
                "subjects": ["Physical Education", "Advanced Skills"],
                "grade_levels": ["6"],
                "specialization": "6th Grade PE Specialist (Advanced Skills)"
            }
        },
        {
            "email": "michelle.rodriguez@springfield.edu",
            "password_hash": "hashed_password_18",
            "first_name": "Michelle",
            "last_name": "Rodriguez",
            "role": "teacher",
            "is_active": True,
            "user_type": "teacher",
            "preferences": {
                "school": "Springfield Middle School",
                "department": "Physical Education",
                "subjects": ["Physical Education", "Fitness Training"],
                "grade_levels": ["7"],
                "specialization": "7th Grade PE Specialist (Fitness Training)"
            }
        },
        {
            "email": "christopher.anderson@springfield.edu",
            "password_hash": "hashed_password_19",
            "first_name": "Christopher",
            "last_name": "Anderson",
            "role": "teacher",
            "is_active": True,
            "user_type": "teacher",
            "preferences": {
                "school": "Springfield Middle School",
                "department": "Physical Education",
                "subjects": ["Physical Education", "Sports Leadership"],
                "grade_levels": ["8"],
                "specialization": "8th Grade PE Specialist (Sports Leadership)"
            }
        },
        {
            "email": "jennifer.taylor@springfield.edu",
            "password_hash": "hashed_password_20",
            "first_name": "Jennifer",
            "last_name": "Taylor",
            "role": "teacher",
            "is_active": True,
            "user_type": "teacher",
            "preferences": {
                "school": "Springfield Middle School",
                "department": "Physical Education",
                "subjects": ["Physical Education", "Competitive Athletics"],
                "grade_levels": ["6", "7", "8"],
                "specialization": "Athletic Director & Competitive Sports"
            }
        },
        {
            "email": "michael.rodriguez@springfield.edu",
            "password_hash": "hashed_password_21",
            "first_name": "Michael",
            "last_name": "Rodriguez",
            "role": "teacher",
            "is_active": True,
            "user_type": "teacher",
            "preferences": {
                "school": "Springfield Middle School",
                "department": "Physical Education",
                "subjects": ["Physical Education", "Competitive Sports"],
                "grade_levels": ["6", "7", "8"],
                "specialization": "Competitive Sports Coordinator"
            }
        },
        {
            "email": "jessica.lee@springfield.edu",
            "password_hash": "hashed_password_22",
            "first_name": "Jessica",
            "last_name": "Lee",
            "role": "teacher",
            "is_active": True,
            "user_type": "teacher",
            "preferences": {
                "school": "Springfield Middle School",
            "department": "Physical Education",
                "subjects": ["Physical Education", "Leadership Development"],
                "grade_levels": ["6", "7", "8"],
                "specialization": "Leadership Development Specialist"
            }
        },
        {
            "email": "brian.anderson@springfield.edu",
            "password_hash": "hashed_password_23",
            "first_name": "Brian",
            "last_name": "Anderson",
            "role": "teacher",
            "is_active": True,
            "user_type": "teacher",
            "preferences": {
                "school": "Springfield Middle School",
                "department": "Physical Education",
                "subjects": ["Physical Education", "Sports Academy"],
                "grade_levels": ["6", "7", "8"],
                "specialization": "Sports Academy Coordinator"
            }
        },
        
        # Springfield High School (8-9 Teachers)
        {
            "email": "richard.davis@springfield.edu",
            "password_hash": "hashed_password_24",
            "first_name": "Richard",
            "last_name": "Davis",
            "role": "teacher",
            "is_active": True,
            "user_type": "teacher",
            "preferences": {
                "school": "Springfield High School",
                "department": "Physical Education",
                "subjects": ["Physical Education", "Advanced Athletics"],
                "grade_levels": ["9"],
                "specialization": "9th Grade PE Specialist (Advanced Athletics)"
            }
        },
        {
            "email": "lisa.chen@springfield.edu",
            "password_hash": "hashed_password_25",
            "first_name": "Lisa",
            "last_name": "Chen",
            "role": "teacher",
            "is_active": True,
            "user_type": "teacher",
            "preferences": {
                "school": "Springfield High School",
                "department": "Physical Education",
                "subjects": ["Physical Education", "Sports Medicine"],
                "grade_levels": ["10"],
                "specialization": "10th Grade PE Specialist (Sports Medicine)"
            }
        },
        {
            "email": "robert.johnson@springfield.edu",
            "password_hash": "hashed_password_26",
            "first_name": "Robert",
            "last_name": "Johnson",
            "role": "teacher",
            "is_active": True,
            "user_type": "teacher",
            "preferences": {
                "school": "Springfield High School",
                "department": "Physical Education",
                "subjects": ["Physical Education", "Fitness Science"],
                "grade_levels": ["11"],
                "specialization": "11th Grade PE Specialist (Fitness Science)"
            }
        },
        {
            "email": "maria.gonzalez@springfield.edu",
            "password_hash": "hashed_password_27",
            "first_name": "Maria",
            "last_name": "Gonzalez",
            "role": "teacher",
            "is_active": True,
            "user_type": "teacher",
            "preferences": {
                "school": "Springfield High School",
                "department": "Physical Education",
                "subjects": ["Physical Education", "Wellness & Nutrition"],
                "grade_levels": ["12"],
                "specialization": "12th Grade PE Specialist (Wellness & Nutrition)"
            }
        },
        {
            "email": "christopher.thompson@springfield.edu",
            "password_hash": "hashed_password_28",
            "first_name": "Christopher",
            "last_name": "Thompson",
            "role": "teacher",
            "is_active": True,
            "user_type": "teacher",
            "preferences": {
                "school": "Springfield High School",
                "department": "Physical Education",
                "subjects": ["Physical Education", "Athletic Administration"],
                "grade_levels": ["9", "10", "11", "12"],
                "specialization": "Athletic Director"
            }
        },
        {
            "email": "alexander.lee@springfield.edu",
            "password_hash": "hashed_password_29",
            "first_name": "Alexander",
            "last_name": "Lee",
            "role": "teacher",
            "is_active": True,
            "user_type": "teacher",
            "preferences": {
                "school": "Springfield High School",
                "department": "Physical Education",
                "subjects": ["Physical Education", "Sports Medicine"],
                "grade_levels": ["9", "10", "11", "12"],
                "specialization": "Sports Medicine Coordinator"
            }
        },
        {
            "email": "victoria.wilson@springfield.edu",
            "password_hash": "hashed_password_30",
            "first_name": "Victoria",
            "last_name": "Wilson",
            "role": "teacher",
            "is_active": True,
            "user_type": "teacher",
            "preferences": {
                "school": "Springfield High School",
                "department": "Physical Education",
                "subjects": ["Physical Education", "Sports Academies"],
                "grade_levels": ["9", "10", "11", "12"],
                "specialization": "Sports Academies Director"
            }
        },
        {
            "email": "william.wilson@springfield.edu",
            "password_hash": "hashed_password_31",
            "first_name": "William",
            "last_name": "Wilson",
            "role": "teacher",
            "is_active": True,
            "user_type": "teacher",
            "preferences": {
                "school": "Springfield High School",
                "department": "Physical Education",
                "subjects": ["Physical Education", "Competitive Programs"],
                "grade_levels": ["9", "10", "11", "12"],
                "specialization": "Competitive Programs Coordinator"
            }
        },
        {
            "email": "sophia.davis@springfield.edu",
            "password_hash": "hashed_password_32",
            "first_name": "Sophia",
            "last_name": "Davis",
            "role": "teacher",
            "is_active": True,
            "user_type": "teacher",
            "preferences": {
                "school": "Springfield High School",
                "department": "Physical Education",
                "subjects": ["Physical Education", "Advanced Training"],
                "grade_levels": ["9", "10", "11", "12"],
                "specialization": "Advanced Training Specialist"
            }
        }
    ]
    
    # Create users using SQLAlchemy ORM
    for user_data in users_data:
        # Check if user already exists
        existing_user = session.query(User).filter(User.email == user_data["email"]).first()
        if existing_user:
            print(f"User {user_data['email']} already exists, skipping...")
            continue
            
        # Create user using ORM
        user = User(
            email=user_data["email"],
            password_hash=user_data["password_hash"],
            first_name=user_data["first_name"],
            last_name=user_data["last_name"],
            role=user_data["role"],
            is_active=user_data["is_active"],
            user_type=user_data["user_type"],
            preferences=user_data["preferences"],
            status=BaseStatus.ACTIVE
        )
        
        session.add(user)
    
    session.commit()
    
    # Count and display the actual number of users seeded
    user_count = session.query(User).count()
    print(f"PE teachers seeded successfully! Total users in database: {user_count}")
    print(f"Expected: 32 PE teachers for 6-school district structure")
    
    # Create teacher-school assignments
    print("\nCreating teacher-school assignments...")
    from app.models.physical_education.schools.relationships import TeacherSchoolAssignment
    
    # Get current academic year
    academic_year_result = session.execute(text("SELECT academic_year FROM school_academic_years WHERE is_current = true LIMIT 1")).fetchall()
    current_academic_year = academic_year_result[0].academic_year if academic_year_result else "2025-2026"
    
    # Create assignments for each teacher based on their preferences
    assignments_created = 0
    for user_data in users_data:
        # Find the user by email
        user = session.query(User).filter(User.email == user_data["email"]).first()
        if user and "school" in user_data["preferences"]:
            school_name = user_data["preferences"]["school"]
            school_id = school_map.get(school_name)
            
            if school_id:
                # Create assignment
                assignment = TeacherSchoolAssignment(
                    teacher_id=user.id,
                    school_id=school_id,
                    assignment_type="Primary",
                    grade_levels=", ".join(user_data["preferences"].get("grade_levels", [])),
                    subjects=", ".join(user_data["preferences"].get("subjects", [])),
                    start_date=datetime.now(),
                    status="ACTIVE",
                    is_department_head="department_head" in user_data["preferences"].get("specialization", "").lower(),
                    is_lead_teacher="coordinator" in user_data["preferences"].get("specialization", "").lower() or "director" in user_data["preferences"].get("specialization", "").lower(),
                    responsibilities=user_data["preferences"].get("specialization", "")
                )
                session.add(assignment)
                assignments_created += 1
    
    session.commit()
    print(f"Created {assignments_created} teacher-school assignments")

if __name__ == "__main__":
    seed_users(SessionLocal()) 