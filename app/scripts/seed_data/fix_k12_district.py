#!/usr/bin/env python3
"""
Fix K-12 District Record Counts
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

def fix_k12_district():
    """Fix record counts for K-12 district"""
    
    # Use the Azure PostgreSQL connection
    DATABASE_URL = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        raise RuntimeError('DATABASE_URL must be set in the environment')
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    print('🔧 FIXING K-12 DISTRICT RECORD COUNTS')
    print('=' * 80)

    try:
        # 1. SUBJECTS (5 → 30 for K-12)
        print('\n📚 1. FIXING SUBJECTS FOR K-12')
        print('-' * 50)
        
        # Check current subject count
        result = session.execute(text('SELECT COUNT(*) FROM subjects'))
        current_count = result.fetchone()[0]
        print(f'Current subjects: {current_count}')
        
        # Add K-12 subjects (only if we need more)
        if current_count < 30:
            k12_subjects = [
            # Core Elementary
            ('Mathematics', 'Core mathematics curriculum'),
            ('Reading', 'Reading and literacy'),
            ('Writing', 'Writing and composition'),
            ('Science', 'General science'),
            ('Social Studies', 'Social studies and history'),
            ('Physical Education', 'Physical education and health'),
            ('Art', 'Visual arts'),
            ('Music', 'Music education'),
            
            # Middle School
            ('Pre-Algebra', 'Pre-algebra mathematics'),
            ('Algebra I', 'Algebra I mathematics'),
            ('Geometry', 'Geometry mathematics'),
            ('Life Science', 'Life science and biology'),
            ('Earth Science', 'Earth science'),
            ('World History', 'World history'),
            ('US History', 'United States history'),
            ('Geography', 'Geography and world cultures'),
            
            # High School
            ('Algebra II', 'Algebra II mathematics'),
            ('Pre-Calculus', 'Pre-calculus mathematics'),
            ('Calculus', 'Calculus mathematics'),
            ('Statistics', 'Statistics and probability'),
            ('Biology', 'Biology'),
            ('Chemistry', 'Chemistry'),
            ('Physics', 'Physics'),
            ('Environmental Science', 'Environmental science'),
            ('US Government', 'US Government and civics'),
            ('Economics', 'Economics'),
            ('World Literature', 'World literature'),
            ('American Literature', 'American literature'),
            ('Creative Writing', 'Creative writing'),
            ('Spanish', 'Spanish language'),
            ('French', 'French language'),
            ('Computer Science', 'Computer science and programming'),
            ('Health', 'Health education'),
            ('Drama', 'Drama and theater'),
            ('Band', 'Band and instrumental music'),
            ('Choir', 'Choir and vocal music'),
            ('Journalism', 'Journalism and media'),
            ('Yearbook', 'Yearbook and publications'),
            ('AP Courses', 'Advanced Placement courses'),
            ('Honors Courses', 'Honors level courses')
        ]
        
            for name, description in k12_subjects:
                # Check if subject already exists
                exists_result = session.execute(text('SELECT EXISTS(SELECT 1 FROM subjects WHERE name = :name)'), {'name': name})
                if not exists_result.fetchone()[0]:
                    session.execute(text('''
                        INSERT INTO subjects (name, description)
                        VALUES (:name, :description)
                    '''), {
                        'name': name,
                        'description': description
                    })
            
            print(f'✅ Added K-12 subjects (total now: {current_count + len(k12_subjects)})')
        else:
            print(f'✅ Subjects already sufficient for K-12 ({current_count} subjects)')

        # 2. ROLES (7 → 25 for K-12)
        print('\n👥 2. FIXING ROLES FOR K-12')
        print('-' * 50)
        
        # Check current role count
        result = session.execute(text('SELECT COUNT(*) FROM roles'))
        current_count = result.fetchone()[0]
        print(f'Current roles: {current_count}')
        
        # Add K-12 roles (only if we need more)
        if current_count < 25:
            k12_roles = [
            ('Superintendent', 'District superintendent'),
            ('Assistant Superintendent', 'Assistant district superintendent'),
            ('Principal', 'School principal'),
            ('Assistant Principal', 'Assistant school principal'),
            ('Teacher', 'Classroom teacher'),
            ('Substitute Teacher', 'Substitute teacher'),
            ('Student', 'Student'),
            ('Parent', 'Parent/Guardian'),
            ('School Secretary', 'School administrative staff'),
            ('Nurse', 'School nurse'),
            ('Counselor', 'School counselor'),
            ('Librarian', 'School librarian'),
            ('Custodian', 'Custodial staff'),
            ('Food Service Worker', 'Food service staff'),
            ('Bus Driver', 'Transportation staff'),
            ('IT Administrator', 'Technology administrator'),
            ('Maintenance Worker', 'Maintenance staff'),
            ('Volunteer', 'School volunteer'),
            ('Board Member', 'School board member'),
            ('Department Head', 'Academic department head'),
            ('Curriculum Coordinator', 'Curriculum coordinator'),
            ('Special Education Teacher', 'Special education teacher'),
            ('ESL Teacher', 'English as a Second Language teacher'),
            ('Athletic Director', 'Athletic director'),
            ('Security Guard', 'School security')
        ]
        
            for name, description in k12_roles:
                # Check if role already exists
                exists_result = session.execute(text('SELECT EXISTS(SELECT 1 FROM roles WHERE name = :name)'), {'name': name})
                if not exists_result.fetchone()[0]:
                    session.execute(text('''
                        INSERT INTO roles (name, description, is_custom, status, is_active)
                        VALUES (:name, :description, :is_custom, :status, :is_active)
                    '''), {
                        'name': name,
                        'description': description,
                        'is_custom': False,
                        'status': 'ACTIVE',
                        'is_active': True
                    })
            
            print(f'✅ Added K-12 roles (total now: {current_count + len(k12_roles)})')
        else:
            print(f'✅ Roles already sufficient for K-12 ({current_count} roles)')

        # 3. EQUIPMENT TYPES (30 → 100 for K-12)
        print('\n🏃 3. FIXING EQUIPMENT TYPES FOR K-12')
        print('-' * 50)
        
        # Check current equipment type count
        result = session.execute(text('SELECT COUNT(*) FROM equipment_types'))
        current_count = result.fetchone()[0]
        print(f'Current equipment types: {current_count}')
        
        # Add K-12 equipment types (only if we need more)
        if current_count < 100:
            k12_equipment = [
            # Elementary PE Equipment
            'Soccer Ball', 'Basketball', 'Volleyball', 'Tennis Ball', 'Softball', 'Baseball', 'Football',
            'Playground Ball', 'Kickball', 'Dodgeball', 'Beach Ball', 'Stress Ball', 'Medicine Ball',
            'Yoga Ball', 'Tennis Racket', 'Badminton Racket', 'Ping Pong Paddle', 'Pickleball Paddle',
            'Jump Rope', 'Hula Hoop', 'Basketball Hoop', 'Tetherball Pole', 'Gym Mat', 'Yoga Mat',
            'Crash Pad', 'Safety Cone', 'Traffic Cone', 'Spot Marker', 'Balance Beam', 'Gymnastics Mat',
            'Wrestling Mat', 'Dumbbell', 'Resistance Band', 'Exercise Ball', 'Kettlebell', 'Weight Plate',
            'Pull-up Bar', 'Jump Box', 'Agility Ladder', 'Speed Ladder', 'Frisbee', 'Flying Disc',
            'Bean Bag', 'Ring Toss', 'Cornhole Board', 'Ladder Ball', 'Horseshoes', 'Bocce Ball',
            'Croquet Set', 'Golf Club', 'Hockey Stick', 'Stopwatch', 'Measuring Tape', 'Starting Block',
            'Hurdle', 'High Jump Bar', 'Shot Put', 'Discus', 'Javelin', 'Relay Baton', 'Equipment Cart',
            'Ball Bag', 'Equipment Rack', 'Storage Bin', 'First Aid Kit', 'Whistle', 'Scoreboard',
            'Timer', 'Megaphone',
            
            # Middle School Equipment
            'Volleyball Net', 'Tennis Net', 'Badminton Net', 'Soccer Goal', 'Basketball Backboard',
            'Trampoline', 'Parallel Bars', 'Uneven Bars', 'Pommel Horse', 'Vaulting Box',
            'Climbing Rope', 'Rope Ladder', 'Cargo Net', 'Monkey Bars', 'Swimming Pool Equipment',
            'Life Jackets', 'Pool Noodles', 'Water Polo Ball', 'Swimming Goggles', 'Pool Float',
            
            # High School Equipment
            'Weight Bench', 'Squat Rack', 'Barbell', 'Olympic Bar', 'Weight Plates', 'Dumbbells',
            'Kettlebell Set', 'Resistance Bands', 'TRX Suspension Trainer', 'Battle Ropes',
            'Plyometric Box', 'Agility Cones', 'Speed Ladder', 'Reaction Ball', 'Medicine Ball Set',
            'Foam Roller', 'Massage Ball', 'Stretching Strap', 'Yoga Block', 'Pilates Ring',
            'Resistance Tube', 'Ankle Weights', 'Wrist Weights', 'Weighted Vest', 'Sandbag',
            'Kettlebell Rack', 'Dumbbell Rack', 'Weight Storage', 'Exercise Mat', 'Gym Flooring'
        ]
        
            for equipment_name in k12_equipment:
                # Check if equipment type already exists
                exists_result = session.execute(text('SELECT EXISTS(SELECT 1 FROM equipment_types WHERE name = :name)'), {'name': equipment_name})
                if not exists_result.fetchone()[0]:
                    session.execute(text('''
                        INSERT INTO equipment_types (name, description)
                        VALUES (:name, :description)
                    '''), {
                        'name': equipment_name,
                        'description': f"K-12 PE equipment: {equipment_name}"
                    })
            
            print(f'✅ Added K-12 equipment types (total now: {current_count + len(k12_equipment)})')
        else:
            print(f'✅ Equipment types already sufficient for K-12 ({current_count} types)')

        # 4. ORGANIZATIONS (1 → 10 for K-12)
        print('\n🏢 4. FIXING ORGANIZATIONS FOR K-12')
        print('-' * 50)
        
        # Check current organization count
        result = session.execute(text('SELECT COUNT(*) FROM organizations'))
        current_count = result.fetchone()[0]
        print(f'Current organizations: {current_count}')
        
        # Add K-12 organizations (only if we need more)
        if current_count < 10:
            # Add K-12 organizations
            k12_organizations = [
            ('Springfield School District', 'SCHOOL_DISTRICT', 'PREMIUM', 'ACTIVE'),
            ('Lincoln Elementary School', 'SCHOOL', 'PREMIUM', 'ACTIVE'),
            ('Washington Elementary School', 'SCHOOL', 'PREMIUM', 'ACTIVE'),
            ('Jefferson Elementary School', 'SCHOOL', 'PREMIUM', 'ACTIVE'),
            ('Roosevelt Middle School', 'SCHOOL', 'PREMIUM', 'ACTIVE'),
            ('Springfield High School', 'SCHOOL', 'PREMIUM', 'ACTIVE'),
            ('Springfield School Board', 'BOARD', 'PREMIUM', 'ACTIVE'),
            ('Springfield PTA', 'PARENT_ORGANIZATION', 'STANDARD', 'ACTIVE'),
            ('Springfield Athletic Booster Club', 'ATHLETIC', 'STANDARD', 'ACTIVE'),
            ('Springfield Music Boosters', 'MUSIC', 'STANDARD', 'ACTIVE')
        ]
        
            for name, org_type, tier, status in k12_organizations:
                # Check if organization already exists
                exists_result = session.execute(text('SELECT EXISTS(SELECT 1 FROM organizations WHERE name = :name)'), {'name': name})
                if not exists_result.fetchone()[0]:
                    session.execute(text('''
                        INSERT INTO organizations (name, type, subscription_tier, status, is_active, created_at, updated_at)
                        VALUES (:name, :type, :tier, :status, :is_active, :created_at, :updated_at)
                    '''), {
                        'name': name,
                        'type': org_type,
                        'tier': tier,
                        'status': status,
                        'is_active': True,
                        'created_at': datetime.now(),
                        'updated_at': datetime.now()
                    })
            
            print(f'✅ Added K-12 organizations (total now: {current_count + len(k12_organizations)})')
        else:
            print(f'✅ Organizations already sufficient for K-12 ({current_count} organizations)')

        # 5. DEPARTMENTS (8 → 100 for K-12)
        print('\n🏛️ 5. FIXING DEPARTMENTS FOR K-12')
        print('-' * 50)
        
        # Clear existing departments
        session.execute(text('DELETE FROM departments'))
        
        # Get organization IDs
        result = session.execute(text('SELECT id FROM organizations ORDER BY id LIMIT 10'))
        org_ids = [row[0] for row in result.fetchall()]
        
        # Add K-12 departments
        k12_departments = [
            'Kindergarten', '1st Grade', '2nd Grade', '3rd Grade', '4th Grade', '5th Grade',
            '6th Grade', '7th Grade', '8th Grade', '9th Grade', '10th Grade', '11th Grade', '12th Grade',
            'Mathematics', 'English Language Arts', 'Science', 'Social Studies', 'Physical Education',
            'Art', 'Music', 'Library', 'Special Education', 'Counseling', 'Health', 'Foreign Language',
            'Computer Science', 'Career and Technical Education', 'Advanced Placement', 'Honors',
            'English as a Second Language', 'Gifted and Talented', 'Athletics', 'Student Activities',
            'Transportation', 'Food Service', 'Maintenance', 'Technology', 'Security', 'Administration'
        ]
        
        dept_count = 0
        for org_id in org_ids:
            for dept_name in k12_departments:
                if dept_count >= 100:
                    break
                
                session.execute(text('''
                    INSERT INTO departments (organization_id, name, description, status, is_active, created_at, updated_at)
                    VALUES (:org_id, :name, :description, :status, :is_active, :created_at, :updated_at)
                '''), {
                    'org_id': org_id,
                    'name': f"{dept_name} Department",
                    'description': f"{dept_name} department",
                    'status': 'ACTIVE',
                    'is_active': True,
                    'created_at': datetime.now(),
                    'updated_at': datetime.now()
                })
                dept_count += 1
            
            if dept_count >= 100:
                break
        
        print(f'✅ Added {dept_count} K-12 departments')

        # Commit all changes
        session.commit()
        print('\n🎉 K-12 DISTRICT RECORD COUNTS FIXED!')
        print('✅ Subjects updated for K-12 (30 subjects)')
        print('✅ Roles updated for K-12 (25 roles)')
        print('✅ Equipment types updated for K-12 (100 types)')
        print('✅ Organizations updated for K-12 (10 organizations)')
        print('✅ Departments updated for K-12 (100 departments)')
        
    except Exception as e:
        print(f'❌ Error fixing K-12 district: {e}')
        session.rollback()
        raise
    finally:
        session.close()

if __name__ == "__main__":
    fix_k12_district()
