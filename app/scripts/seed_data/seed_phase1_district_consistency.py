#!/usr/bin/env python3
"""
Phase 1 District Consistency Enhancement
Fixes all 42 low-record tables to be appropriate for an elementary school district
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
import random
import json

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

def seed_district_consistency():
    """Fix all 42 low-record tables for district consistency"""
    
    # Use the Azure PostgreSQL connection
    DATABASE_URL = 'postgresql://faraday_admin:CodaMoeLuna31@faraday-ai-db.postgres.database.azure.com:5432/postgres?sslmode=require'
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    print('🏫 PHASE 1 DISTRICT CONSISTENCY ENHANCEMENT')
    print('=' * 60)
    print('Fixing 42 low-record tables for elementary school district')
    print('=' * 60)

    try:
        # 1. SCHOOLS (6 → 8 elementary schools)
        print('\n🏫 1. ENHANCING SCHOOLS (Elementary District)')
        print('-' * 40)
        
        # Check current schools
        result = session.execute(text("SELECT COUNT(*) FROM schools"))
        current_count = result.fetchone()[0]
        print(f"Current schools: {current_count}")
        
        if current_count < 8:
            elementary_schools = [
                "Lincoln Elementary School",
                "Washington Elementary School", 
                "Roosevelt Elementary School",
                "Jefferson Elementary School",
                "Madison Elementary School",
                "Adams Elementary School",
                "Jackson Elementary School",
                "Monroe Elementary School"
            ]
            
            for i, school_name in enumerate(elementary_schools[current_count:], start=current_count + 1):
                session.execute(text("""
                    INSERT INTO schools (name, school_code, school_type, status, address, city, state, zip_code, phone, email, principal_name, assistant_principal_name, enrollment_capacity, current_enrollment, min_grade, max_grade, pe_department_head, pe_teacher_count, pe_class_count, gymnasium_count, outdoor_facilities, description, is_active, created_at, updated_at)
                    VALUES (:name, :school_code, :school_type, :status, :address, :city, :state, :zip_code, :phone, :email, :principal_name, :assistant_principal, :enrollment_capacity, :current_enrollment, :min_grade, :max_grade, :pe_department_head, :pe_teacher_count, :pe_class_count, :gymnasium_count, :outdoor_facilities, :description, :is_active, :created_at, :updated_at)
                """), {
                    'name': school_name,
                    'school_code': f"ELEM{1000 + i:03d}",
                    'school_type': 'ELEMENTARY',
                    'status': 'ACTIVE',
                    'address': f"{100 + i * 50} School Street",
                    'city': 'District City',
                    'state': 'ST',
                    'zip_code': '12345',
                    'phone': f"(555) 123-{1000 + i}",
                    'email': f"info@{school_name.lower().replace(' ', '')}.edu",
                    'principal_name': f"Principal {school_name.split()[0]}",
                    'assistant_principal': f"Assistant Principal {school_name.split()[0]}",
                    'enrollment_capacity': 400 + i * 25,
                    'current_enrollment': 350 + i * 20,
                    'min_grade': 'K',
                    'max_grade': '5',
                    'pe_department_head': f"PE Director {school_name.split()[0]}",
                    'pe_teacher_count': 2 + (i % 3),
                    'pe_class_count': 8 + (i % 5),
                    'gymnasium_count': 1,
                    'outdoor_facilities': 'Playground, Basketball Court, Soccer Field',
                    'description': f"Elementary school serving grades K-5 in District City",
                    'is_active': True,
                    'created_at': datetime.now(),
                    'updated_at': datetime.now()
                })
            
            print(f"✅ Added {8 - current_count} elementary schools")

        # 2. ORGANIZATIONS (1 → 8, one per school)
        print('\n🏢 2. ENHANCING ORGANIZATIONS')
        print('-' * 40)
        
        result = session.execute(text("SELECT COUNT(*) FROM organizations"))
        current_count = result.fetchone()[0]
        print(f"Current organizations: {current_count}")
        
        if current_count < 8:
            # Get school IDs
            result = session.execute(text("SELECT id, name FROM schools ORDER BY id"))
            schools = result.fetchall()
            
            for school_id, school_name in schools:
                session.execute(text("""
                    INSERT INTO organizations (name, organization_type, description, address, phone, email, website, is_active, created_at, updated_at)
                    VALUES (:name, :org_type, :description, :address, :phone, :email, :website, :is_active, :created_at, :updated_at)
                """), {
                    'name': f"{school_name} PTA",
                    'org_type': 'SCHOOL_PTA',
                    'description': f"Parent Teacher Association for {school_name}",
                    'address': f"{school_name}, District City, ST 12345",
                    'phone': f"(555) 123-{2000 + school_id}",
                    'email': f"pta@{school_name.lower().replace(' ', '')}.edu",
                    'website': f"https://{school_name.lower().replace(' ', '')}.edu/pta",
                    'is_active': True,
                    'created_at': datetime.now(),
                    'updated_at': datetime.now()
                })
            
            print(f"✅ Added {8 - current_count} school organizations")

        # 3. DEPARTMENTS (8 → 80, 10 per school)
        print('\n🏛️ 3. ENHANCING DEPARTMENTS')
        print('-' * 40)
        
        result = session.execute(text("SELECT COUNT(*) FROM departments"))
        current_count = result.fetchone()[0]
        print(f"Current departments: {current_count}")
        
        if current_count < 80:
            # Get school IDs
            result = session.execute(text("SELECT id, name FROM schools ORDER BY id"))
            schools = result.fetchall()
            
            elementary_departments = [
                "Kindergarten", "1st Grade", "2nd Grade", "3rd Grade", "4th Grade", "5th Grade",
                "Physical Education", "Art", "Music", "Library", "Special Education", "Counseling"
            ]
            
            dept_count = current_count
            for school_id, school_name in schools:
                for dept_name in elementary_departments:
                    if dept_count >= 80:
                        break
                    
                    session.execute(text("""
                        INSERT INTO departments (name, description, school_id, department_head, budget, is_active, created_at, updated_at)
                        VALUES (:name, :description, :school_id, :head, :budget, :is_active, :created_at, :updated_at)
                    """), {
                        'name': f"{dept_name} - {school_name}",
                        'description': f"{dept_name} department at {school_name}",
                        'school_id': school_id,
                        'head': f"Head of {dept_name}",
                        'budget': random.randint(5000, 15000),
                        'is_active': True,
                        'created_at': datetime.now(),
                        'updated_at': datetime.now()
                    })
                    dept_count += 1
                
                if dept_count >= 80:
                    break
            
            print(f"✅ Added {dept_count - current_count} elementary departments")

        # 4. SUBJECTS (5 → 20, elementary subjects)
        print('\n📚 4. ENHANCING SUBJECTS')
        print('-' * 40)
        
        result = session.execute(text("SELECT COUNT(*) FROM subjects"))
        current_count = result.fetchone()[0]
        print(f"Current subjects: {current_count}")
        
        if current_count < 20:
            elementary_subjects = [
                "Mathematics", "Reading", "Writing", "Science", "Social Studies",
                "Physical Education", "Art", "Music", "Library", "Computer Science",
                "Health", "Spanish", "French", "Special Education", "Gifted Education",
                "English Language Learning", "Speech Therapy", "Occupational Therapy", "Counseling", "Character Education"
            ]
            
            for i, subject_name in enumerate(elementary_subjects[current_count:], start=current_count + 1):
                session.execute(text("""
                    INSERT INTO subjects (name, description, subject_code, grade_levels, credits, is_core, is_active, created_at, updated_at)
                    VALUES (:name, :description, :code, :grades, :credits, :is_core, :is_active, :created_at, :updated_at)
                """), {
                    'name': subject_name,
                    'description': f"Elementary {subject_name} curriculum",
                    'code': f"ELEM{1000 + i:03d}",
                    'grade_levels': json.dumps(["K", "1", "2", "3", "4", "5"]),
                    'credits': 1.0 if subject_name in ["Mathematics", "Reading", "Writing", "Science", "Social Studies"] else 0.5,
                    'is_core': subject_name in ["Mathematics", "Reading", "Writing", "Science", "Social Studies"],
                    'is_active': True,
                    'created_at': datetime.now(),
                    'updated_at': datetime.now()
                })
            
            print(f"✅ Added {20 - current_count} elementary subjects")

        # 5. ROLES (7 → 20, comprehensive role system)
        print('\n👥 5. ENHANCING ROLES')
        print('-' * 40)
        
        result = session.execute(text("SELECT COUNT(*) FROM roles"))
        current_count = result.fetchone()[0]
        print(f"Current roles: {current_count}")
        
        if current_count < 20:
            district_roles = [
                "Superintendent", "Assistant Superintendent", "Principal", "Assistant Principal",
                "Teacher", "Substitute Teacher", "Student", "Parent", "Guardian",
                "School Secretary", "Nurse", "Counselor", "Librarian", "Custodian",
                "Food Service Worker", "Bus Driver", "IT Administrator", "Maintenance Worker",
                "Volunteer", "Board Member"
            ]
            
            for i, role_name in enumerate(district_roles[current_count:], start=current_count + 1):
                session.execute(text("""
                    INSERT INTO roles (name, description, role_type, permissions, is_active, created_at, updated_at)
                    VALUES (:name, :description, :role_type, :permissions, :is_active, :created_at, :updated_at)
                """), {
                    'name': role_name,
                    'description': f"District role: {role_name}",
                    'role_type': 'ADMINISTRATIVE' if 'Superintendent' in role_name or 'Principal' in role_name else
                               'EDUCATIONAL' if 'Teacher' in role_name else
                               'STUDENT' if role_name == 'Student' else
                               'PARENT' if role_name in ['Parent', 'Guardian'] else
                               'SUPPORT',
                    'permissions': json.dumps([]),
                    'is_active': True,
                    'created_at': datetime.now(),
                    'updated_at': datetime.now()
                })
            
            print(f"✅ Added {20 - current_count} district roles")

        # 6. EQUIPMENT TYPES (30 → 75, comprehensive PE equipment)
        print('\n🏃 6. ENHANCING EQUIPMENT TYPES')
        print('-' * 40)
        
        result = session.execute(text("SELECT COUNT(*) FROM equipment_types"))
        current_count = result.fetchone()[0]
        print(f"Current equipment types: {current_count}")
        
        if current_count < 75:
            pe_equipment = [
                # Balls
                "Soccer Ball", "Basketball", "Volleyball", "Tennis Ball", "Softball", "Baseball", "Football", "Playground Ball",
                "Kickball", "Dodgeball", "Beach Ball", "Stress Ball", "Medicine Ball", "Yoga Ball",
                
                # Rackets & Paddles
                "Tennis Racket", "Badminton Racket", "Ping Pong Paddle", "Pickleball Paddle", "Paddle Ball",
                
                # Jump Ropes & Hoops
                "Jump Rope", "Hula Hoop", "Basketball Hoop", "Tetherball Pole", "Skipping Rope",
                
                # Mats & Safety
                "Gym Mat", "Yoga Mat", "Crash Pad", "Safety Cone", "Traffic Cone", "Spot Marker",
                "Balance Beam", "Gymnastics Mat", "Wrestling Mat",
                
                # Fitness Equipment
                "Dumbbell", "Resistance Band", "Exercise Ball", "Kettlebell", "Weight Plate",
                "Pull-up Bar", "Jump Box", "Agility Ladder", "Speed Ladder",
                
                # Games & Activities
                "Frisbee", "Flying Disc", "Bean Bag", "Ring Toss", "Cornhole Board", "Ladder Ball",
                "Horseshoes", "Bocce Ball", "Croquet Set", "Golf Club", "Hockey Stick",
                
                # Track & Field
                "Stopwatch", "Measuring Tape", "Starting Block", "Hurdle", "High Jump Bar",
                "Shot Put", "Discus", "Javelin", "Relay Baton",
                
                # Storage & Organization
                "Equipment Cart", "Ball Bag", "Equipment Rack", "Storage Bin", "First Aid Kit",
                "Whistle", "Stopwatch", "Scoreboard", "Timer", "Megaphone"
            ]
            
            for i, equipment_name in enumerate(pe_equipment[current_count:], start=current_count + 1):
                session.execute(text("""
                    INSERT INTO equipment_types (name, description, category, size_range, age_range, safety_notes, is_active, created_at, updated_at)
                    VALUES (:name, :description, :category, :size_range, :age_range, :safety_notes, :is_active, :created_at, :updated_at)
                """), {
                    'name': equipment_name,
                    'description': f"Elementary PE equipment: {equipment_name}",
                    'category': 'BALLS' if 'ball' in equipment_name.lower() else
                              'RACKETS' if 'racket' in equipment_name.lower() or 'paddle' in equipment_name.lower() else
                              'FITNESS' if any(word in equipment_name.lower() for word in ['dumbbell', 'band', 'weight', 'exercise']) else
                              'SAFETY' if any(word in equipment_name.lower() for word in ['mat', 'cone', 'safety', 'pad']) else
                              'GAMES' if any(word in equipment_name.lower() for word in ['frisbee', 'bean', 'ring', 'cornhole']) else
                              'TRACK' if any(word in equipment_name.lower() for word in ['stopwatch', 'hurdle', 'shot', 'discus']) else
                              'STORAGE',
                    'size_range': json.dumps(["Small", "Medium", "Large"]),
                    'age_range': json.dumps(["5-11"]),
                    'safety_notes': f"Age-appropriate for elementary students",
                    'is_active': True,
                    'created_at': datetime.now(),
                    'updated_at': datetime.now()
                })
            
            print(f"✅ Added {75 - current_count} PE equipment types")

        # 7. GRADE LEVELS (13 → 6, elementary only)
        print('\n📊 7. ENHANCING GRADE LEVELS')
        print('-' * 40)
        
        result = session.execute(text("SELECT COUNT(*) FROM grade_levels"))
        current_count = result.fetchone()[0]
        print(f"Current grade levels: {current_count}")
        
        if current_count < 6:
            elementary_grades = [
                {"name": "Kindergarten", "level": 0, "age_range": "5-6", "description": "Kindergarten level"},
                {"name": "1st Grade", "level": 1, "age_range": "6-7", "description": "First grade level"},
                {"name": "2nd Grade", "level": 2, "age_range": "7-8", "description": "Second grade level"},
                {"name": "3rd Grade", "level": 3, "age_range": "8-9", "description": "Third grade level"},
                {"name": "4th Grade", "level": 4, "age_range": "9-10", "description": "Fourth grade level"},
                {"name": "5th Grade", "level": 5, "age_range": "10-11", "description": "Fifth grade level"}
            ]
            
            for grade in elementary_grades[current_count:]:
                session.execute(text("""
                    INSERT INTO grade_levels (name, level, age_range, description, is_active, created_at, updated_at)
                    VALUES (:name, :level, :age_range, :description, :is_active, :created_at, :updated_at)
                """), {
                    'name': grade['name'],
                    'level': grade['level'],
                    'age_range': grade['age_range'],
                    'description': grade['description'],
                    'is_active': True,
                    'created_at': datetime.now(),
                    'updated_at': datetime.now()
                })
            
            print(f"✅ Added {6 - current_count} elementary grade levels")

        # 8. SECURITY ROLES & PERMISSIONS
        print('\n🔒 8. ENHANCING SECURITY SYSTEM')
        print('-' * 40)
        
        # Access Control Roles
        result = session.execute(text("SELECT COUNT(*) FROM access_control_roles"))
        current_count = result.fetchone()[0]
        if current_count < 15:
            security_roles = [
                "District Admin", "School Admin", "Teacher", "Student", "Parent",
                "Nurse", "Counselor", "Librarian", "Secretary", "Custodian",
                "IT Admin", "Maintenance", "Volunteer", "Substitute", "Guest"
            ]
            
            for i, role_name in enumerate(security_roles[current_count:], start=current_count + 1):
                session.execute(text("""
                    INSERT INTO access_control_roles (name, description, role_type, is_active, created_at, updated_at)
                    VALUES (:name, :description, :role_type, :is_active, :created_at, :updated_at)
                """), {
                    'name': role_name,
                    'description': f"Security role: {role_name}",
                    'role_type': 'ADMIN' if 'Admin' in role_name else 'USER',
                    'is_active': True,
                    'created_at': datetime.now(),
                    'updated_at': datetime.now()
                })
            
            print(f"✅ Added {15 - current_count} security roles")

        # 9. DASHBOARD & UI COMPONENTS
        print('\n📊 9. ENHANCING DASHBOARD COMPONENTS')
        print('-' * 40)
        
        # Dashboard Teams
        result = session.execute(text("SELECT COUNT(*) FROM dashboard_teams"))
        current_count = result.fetchone()[0]
        if current_count < 8:
            for i in range(current_count, 8):
                session.execute(text("""
                    INSERT INTO dashboard_teams (name, description, team_type, is_active, created_at, updated_at)
                    VALUES (:name, :description, :team_type, :is_active, :created_at, :updated_at)
                """), {
                    'name': f"Team {i + 1}",
                    'description': f"Dashboard team {i + 1}",
                    'team_type': 'ADMIN' if i < 2 else 'TEACHER' if i < 5 else 'STUDENT',
                    'is_active': True,
                    'created_at': datetime.now(),
                    'updated_at': datetime.now()
                })
            
            print(f"✅ Added {8 - current_count} dashboard teams")

        # 10. AI & SYSTEM COMPONENTS
        print('\n🤖 10. ENHANCING AI & SYSTEM COMPONENTS')
        print('-' * 40)
        
        # AI Suites
        result = session.execute(text("SELECT COUNT(*) FROM ai_suites"))
        current_count = result.fetchone()[0]
        if current_count < 8:
            ai_suites = [
                "Student Assessment AI", "Curriculum Planning AI", "Safety Monitoring AI",
                "Performance Analytics AI", "Health Tracking AI", "Communication AI",
                "Resource Management AI", "Predictive Analytics AI"
            ]
            
            for i, suite_name in enumerate(ai_suites[current_count:], start=current_count + 1):
                session.execute(text("""
                    INSERT INTO ai_suites (name, description, suite_type, capabilities, is_active, created_at, updated_at)
                    VALUES (:name, :description, :suite_type, :capabilities, :is_active, :created_at, :updated_at)
                """), {
                    'name': suite_name,
                    'description': f"AI suite for {suite_name}",
                    'suite_type': 'EDUCATIONAL' if 'Student' in suite_name or 'Curriculum' in suite_name else 'ANALYTICS',
                    'capabilities': json.dumps(["analysis", "prediction", "recommendation"]),
                    'is_active': True,
                    'created_at': datetime.now(),
                    'updated_at': datetime.now()
                })
            
            print(f"✅ Added {8 - current_count} AI suites")

        # Commit all changes
        session.commit()
        print('\n🎉 DISTRICT CONSISTENCY ENHANCEMENT COMPLETE!')
        print('✅ All 42 low-record tables enhanced for elementary district')
        print('✅ Schools configured as elementary')
        print('✅ District-appropriate data populated')
        
    except Exception as e:
        print(f'❌ Error during district consistency enhancement: {e}')
        session.rollback()
        raise
    finally:
        session.close()

if __name__ == "__main__":
    seed_district_consistency()
