#!/usr/bin/env python3
"""
Phase 2: Educational System Enhancement Seeding Script
Seeds 38 tables for advanced educational features, teacher management, and organization structure
"""

import os
import sys
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import random
import logging

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.core.database import SessionLocal
from app.core.logging import get_logger
from sqlalchemy.orm import Session
from sqlalchemy import text

# Import models for Phase 2 tables
from app.models.educational.curriculum.lesson_plan import LessonPlan
from app.models.educational.curriculum.curriculum import Curriculum
from app.models.educational.curriculum.course import Course
from app.models.educational.base.assignment import Assignment
from app.models.educational.base.grade import Grade
from app.models.educational.base.rubric import Rubric
from app.models.educational.teacher_management import (
    TeacherAvailability, TeacherCertification, TeacherPreference,
    TeacherQualification, TeacherSchedule, TeacherSpecialization
)
from app.models.educational.class_management import (
    EducationalClass, EducationalClassStudent, EducationalTeacherAvailability,
    EducationalTeacherCertification, ClassAttendance, ClassPlan, ClassSchedule
)
from app.models.organization.organization_management import (
    Department, DepartmentMember, OrganizationRole, OrganizationMember,
    OrganizationCollaboration, OrganizationProject, OrganizationResource,
    OrganizationSetting, OrganizationFeedback, Team, TeamMember
)

logger = get_logger(__name__)

# ============================================================================
# SECTION 2.1: ADVANCED EDUCATIONAL FEATURES SEEDING FUNCTIONS
# ============================================================================

def seed_physical_education_teachers(session: Session) -> int:
    """Seed physical_education_teachers table"""
    try:
        # Check if table exists and has data
        result = session.execute(text("SELECT COUNT(*) FROM physical_education_teachers"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  🔄 physical_education_teachers already has {existing_count} records, continuing with migration...")
        
        # Get actual user IDs from the users table to ensure flexibility
        user_result = session.execute(text("SELECT id FROM users ORDER BY id"))
        user_ids = [row[0] for row in user_result.fetchall()]
        
        if not user_ids:
            print("  ❌ No users found, cannot create physical education teachers")
            return 0
        
        # Create physical education teachers for existing users
        teachers = []
        for i, user_id in enumerate(user_ids):
            teacher = {
                'user_id': user_id,  # Use actual user ID from database
                'first_name': f'PE Teacher {i + 1}',
                'last_name': f'Smith{i + 1}',
                'email': f'pe.teacher{i + 1}@school.edu',
                'phone': f'555-{1000 + i}',
                'specialization': random.choice(['Basketball', 'Soccer', 'Track & Field', 'Swimming', 'Gymnastics']),
                'certification': random.choice(['CPR Certified', 'First Aid', 'Coaching License', 'PE Teaching Certificate']),
                'experience_years': random.randint(1, 20),
                'is_active': True,
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now(),
                'teacher_metadata': json.dumps({
                    "bio": f"Experienced PE teacher specializing in {random.choice(['team sports', 'individual sports', 'fitness', 'recreation'])}",
                    "interests": ["fitness", "sports", "health education"],
                    "achievements": ["Teacher of the Year 2023", "State Championship Coach"]
                }),
                'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'archived_at': None,
                'deleted_at': None,
                'scheduled_deletion_at': None,
                'retention_period': random.randint(30, 365)
            }
            teachers.append(teacher)
        
        # Insert/update teachers with proper conflict handling
        for teacher in teachers:
            # Check if teacher with this user_id already exists
            existing = session.execute(text("""
                SELECT id FROM physical_education_teachers WHERE user_id = :user_id
            """), {"user_id": teacher["user_id"]}).fetchone()
            
            if existing:
                # Update existing teacher
                session.execute(text("""
                    UPDATE physical_education_teachers SET
                        first_name = :first_name,
                        last_name = :last_name,
                        email = :email,
                        phone = :phone,
                        specialization = :specialization,
                        certification = :certification,
                        experience_years = :experience_years,
                        is_active = :is_active,
                        updated_at = :updated_at,
                        teacher_metadata = :teacher_metadata,
                        last_accessed_at = :last_accessed_at,
                        retention_period = :retention_period
                    WHERE user_id = :user_id
                """), teacher)
            else:
                # Insert new teacher
                session.execute(text("""
                    INSERT INTO physical_education_teachers (user_id, first_name, last_name, email, phone, 
                                                           specialization, certification, experience_years, 
                                                           is_active, created_at, updated_at, teacher_metadata,
                                                           last_accessed_at, archived_at, deleted_at, 
                                                           scheduled_deletion_at, retention_period)
                    VALUES (:user_id, :first_name, :last_name, :email, :phone, :specialization, 
                           :certification, :experience_years, :is_active, :created_at, :updated_at, 
                           :teacher_metadata, :last_accessed_at, :archived_at, :deleted_at, 
                           :scheduled_deletion_at, :retention_period)
                """), teacher)
        
        session.commit()
        print(f"  ✅ Migrated {len(teachers)} physical education teachers (based on {len(user_ids)} users)")
        return len(teachers)
        
    except Exception as e:
        print(f"  ❌ Error seeding physical_education_teachers: {e}")
        session.rollback()
        return 0

def seed_physical_education_classes(session: Session) -> int:
    """Seed physical_education_classes table"""
    try:
        # Check if table exists and has data
        result = session.execute(text("SELECT COUNT(*) FROM physical_education_classes"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  📊 physical_education_classes already has {existing_count} records, migrating additional data...")
        
        # Get actual teacher IDs from physical_education_teachers table
        teacher_result = session.execute(text("SELECT id FROM physical_education_teachers ORDER BY id"))
        teacher_ids = [row[0] for row in teacher_result.fetchall()]
        
        if not teacher_ids:
            print("  ⚠️  No teachers found, skipping physical education classes...")
            return 0
        
        # Create additional physical education classes (always migrate)
        classes = []
        additional_count = 50  # Always create 50 additional classes
        for i in range(additional_count):
            class_data = {
                'teacher_id': random.choice(teacher_ids),
                'name': f'PE Class {i + 1}',
                'description': f'Physical Education class focusing on {random.choice(["fitness", "team sports", "individual sports", "recreation"])}',
                'class_type': random.choice(['REGULAR', 'ADVANCED', 'BEGINNER', 'SPECIAL_NEEDS']),
                'start_date': datetime.now() - timedelta(days=random.randint(1, 365)),
                'end_date': datetime.now() + timedelta(days=random.randint(30, 365)),
                'max_students': random.randint(15, 30),
                'location': f"Gym {random.randint(1, 5)}",
                'schedule': random.choice(['M-W-F', 'T-TH', 'M-F', 'T-W-TH-F']),
                'grade_level': random.choice(['KINDERGARTEN', 'FIRST', 'SECOND', 'THIRD', 'FOURTH', 'FIFTH', 'SIXTH', 'SEVENTH', 'EIGHTH', 'NINTH', 'TENTH', 'ELEVENTH', 'TWELFTH']),
                'curriculum_focus': f'Focus on {random.choice(["cardiovascular fitness", "strength training", "flexibility", "coordination"])}',
                'assessment_methods': f'Assessment via {random.choice(["skill tests", "fitness tests", "participation", "peer evaluation"])}',
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now()
            }
            classes.append(class_data)
        
        # Insert classes
        session.execute(text("""
            INSERT INTO physical_education_classes (teacher_id, name, description, class_type, 
                                                  start_date, end_date, max_students, location, 
                                                  schedule, grade_level, curriculum_focus, 
                                                  assessment_methods, created_at, updated_at)
            VALUES (:teacher_id, :name, :description, :class_type, :start_date, :end_date, 
                   :max_students, :location, :schedule, :grade_level, :curriculum_focus, 
                   :assessment_methods, :created_at, :updated_at)
        """), classes)
        
        session.commit()
        print(f"  ✅ Created {len(classes)} additional physical education classes")
        return existing_count + len(classes)
        
    except Exception as e:
        print(f"  ❌ Error seeding physical_education_classes: {e}")
        session.rollback()
        return 0

def seed_activity_plans(session: Session) -> int:
    """Seed activity_plans table"""
    try:
        # Check if table exists and has data
        result = session.execute(text("SELECT COUNT(*) FROM activity_plans"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  📊 activity_plans already has {existing_count} records, migrating additional data...")
        
        # Create additional activity plans (always migrate)
        plans = []
        additional_count = 150  # Always create 150 additional activity plans
        for i in range(additional_count):
            plan = {
                'name': f'Activity Plan {i + 1}',
                'description': f'Physical activity plan focusing on {random.choice(["cardiovascular fitness", "strength training", "flexibility", "coordination", "team building"])}',
                'grade_level': random.choice(['KINDERGARTEN', 'FIRST', 'SECOND', 'THIRD', 'FOURTH', 'FIFTH', 'SIXTH', 'SEVENTH', 'EIGHTH', 'NINTH', 'TENTH', 'ELEVENTH', 'TWELFTH']),
                'duration': random.randint(30, 120),
                'difficulty': random.choice(['Beginner', 'Intermediate', 'Advanced']),
                'student_id': random.choice(range(1, 100)),  # Random student ID
                'is_completed': random.choice([True, False]),
                'plan_metadata': json.dumps({
                    'activity_type': random.choice(['Cardio', 'Strength', 'Flexibility', 'Sports', 'Games', 'Dance', 'Yoga']),
                    'equipment_needed': random.sample(['balls', 'mats', 'cones', 'jump ropes', 'weights', 'resistance bands'], random.randint(1, 3)),
                    'instructions': f'Step-by-step instructions for activity plan {i + 1}',
                    'safety_notes': f'Safety considerations for activity plan {i + 1}'
                }),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now(),
                'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'archived_at': None,
                'deleted_at': None,
                'scheduled_deletion_at': None,
                'retention_period': random.randint(30, 365)
            }
            plans.append(plan)
        
        # Insert activity plans
        session.execute(text("""
            INSERT INTO activity_plans (name, description, grade_level, duration, difficulty, 
                                      student_id, is_completed, plan_metadata, created_at, updated_at, 
                                      last_accessed_at, archived_at, deleted_at, scheduled_deletion_at, 
                                      retention_period)
            VALUES (:name, :description, :grade_level, :duration, :difficulty, :student_id, 
                   :is_completed, :plan_metadata, :created_at, :updated_at, :last_accessed_at, 
                   :archived_at, :deleted_at, :scheduled_deletion_at, :retention_period)
        """), plans)
        
        session.commit()
        print(f"  ✅ Created {len(plans)} additional activity plans")
        
        # Now seed activity_plan_objectives for the plans we just created
        objectives_count = seed_activity_plan_objectives(session, len(plans))
        
        return existing_count + len(plans)
        
    except Exception as e:
        print(f"  ❌ Error seeding activity_plans: {e}")
        session.rollback()
        return 0

def seed_activity_plan_objectives(session: Session, plan_count: int) -> int:
    """Seed activity_plan_objectives table"""
    try:
        # Check if table exists and has data
        result = session.execute(text("SELECT COUNT(*) FROM activity_plan_objectives"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  📊 activity_plan_objectives already has {existing_count} records, migrating additional data...")
        
        # Get the latest activity plan IDs that were just created
        plan_result = session.execute(text("SELECT id FROM activity_plans ORDER BY id DESC LIMIT :count"), {"count": plan_count})
        plan_ids = [row[0] for row in plan_result.fetchall()]
        
        if not plan_ids:
            print("  ⚠️ No activity plan IDs found for objectives")
            return 0
        
        # Create objectives for each plan (2-4 objectives per plan)
        objectives = []
        objective_templates = [
            "Improve cardiovascular endurance through sustained physical activity",
            "Develop fundamental movement skills and coordination",
            "Enhance muscular strength and endurance",
            "Promote flexibility and range of motion",
            "Build teamwork and communication skills",
            "Increase confidence in physical abilities",
            "Learn proper exercise techniques and safety",
            "Develop healthy lifestyle habits",
            "Improve balance and spatial awareness",
            "Enhance problem-solving through physical challenges"
        ]
        
        for plan_id in plan_ids:
            num_objectives = random.randint(2, 4)  # 2-4 objectives per plan
            selected_objectives = random.sample(objective_templates, num_objectives)
            
            for i, objective_text in enumerate(selected_objectives):
                objective = {
                    'plan_id': plan_id,
                    'objective': objective_text,
                    'objective_metadata': json.dumps({
                        'priority': random.choice(['HIGH', 'MEDIUM', 'LOW']),
                        'target_achievement': random.randint(70, 100),  # percentage
                        'assessment_method': random.choice(['OBSERVATION', 'PERFORMANCE_TEST', 'SELF_ASSESSMENT', 'PEER_REVIEW']),
                        'timeline': random.choice(['SHORT_TERM', 'MEDIUM_TERM', 'LONG_TERM']),
                        'success_criteria': f'Success criteria for: {objective_text[:50]}...',
                        'notes': f'Additional notes for objective {i+1} of plan {plan_id}'
                    }),
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                    'updated_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                    'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 7)),
                    'archived_at': None,
                    'deleted_at': None,
                    'scheduled_deletion_at': None,
                    'retention_period': random.randint(30, 365)
                }
                objectives.append(objective)
        
        # Insert objectives
        session.execute(text("""
            INSERT INTO activity_plan_objectives (plan_id, objective, objective_metadata, created_at, updated_at, 
                                                last_accessed_at, archived_at, deleted_at, scheduled_deletion_at, 
                                                retention_period)
            VALUES (:plan_id, :objective, :objective_metadata, :created_at, :updated_at, :last_accessed_at, 
                   :archived_at, :deleted_at, :scheduled_deletion_at, :retention_period)
        """), objectives)
        
        print(f"  ✅ activity_plan_objectives: +{len(objectives)} records (migrated from activity_plans)")
        return len(objectives)
        
    except Exception as e:
        print(f"  ❌ activity_plan_objectives: {e}")
        session.rollback()
        return 0

def seed_activity_plans_planning(session: Session) -> int:
    """Seed activity_plans_planning table"""
    try:
        # Check if table exists and has data
        result = session.execute(text("SELECT COUNT(*) FROM activity_plans_planning"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  📊 activity_plans_planning already has {existing_count} records, migrating additional data...")
        
        # Get student IDs for planning
        student_result = session.execute(text("SELECT id FROM students LIMIT 50"))
        student_ids = [row[0] for row in student_result.fetchall()]
        
        if not student_ids:
            print("  ⚠️ No student IDs found for planning")
            return 0
        
        # Create activity plans for planning
        planning_plans = []
        planning_types = ['INDIVIDUAL', 'GROUP', 'CLASS', 'TEAM', 'CUSTOM']
        planning_levels = ['BASIC', 'INTERMEDIATE', 'ADVANCED', 'EXPERT']
        planning_statuses = ['DRAFT', 'PENDING', 'APPROVED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED']
        
        for i in range(1500):  # Create 1500 planning activity plans for district scale
            start_date = datetime.now() - timedelta(days=random.randint(1, 30))
            end_date = start_date + timedelta(days=random.randint(7, 90))
            
            planning_plan = {
                'plan_name': f'Planning Activity Plan {i + 1}',
                'plan_description': f'Comprehensive planning for {random.choice(["fitness development", "skill building", "assessment preparation", "remedial support", "enrichment activities"])}',
                'student_id': random.choice(student_ids),
                'planning_type': random.choice(planning_types),
                'planning_level': random.choice(planning_levels),
                'planning_status': random.choice(planning_statuses),
                'start_date': start_date,
                'end_date': end_date,
                'planning_notes': f'Planning notes for activity plan {i + 1} - focus on {random.choice(["cardiovascular fitness", "muscular strength", "flexibility", "coordination", "teamwork"])}',
                'planning_metadata': json.dumps({
                    'priority': random.choice(['HIGH', 'MEDIUM', 'LOW']),
                    'complexity': random.choice(['SIMPLE', 'MODERATE', 'COMPLEX']),
                    'estimated_hours': random.randint(10, 100),
                    'required_resources': random.sample(['equipment', 'facilities', 'personnel', 'materials'], random.randint(1, 3)),
                    'success_metrics': [f'Metric {j}' for j in range(random.randint(2, 5))],
                    'risk_factors': [f'Risk {j}' for j in range(random.randint(1, 3))],
                    'contingency_plans': [f'Contingency {j}' for j in range(random.randint(1, 2))]
                }),
                'created_at': start_date - timedelta(days=random.randint(1, 7)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 7)),
                'archived_at': None,
                'deleted_at': None,
                'scheduled_deletion_at': None,
                'retention_period': random.randint(365, 2555)  # 1-7 years
            }
            planning_plans.append(planning_plan)
        
        # Insert planning plans
        session.execute(text("""
            INSERT INTO activity_plans_planning (plan_name, plan_description, student_id, planning_type, 
                                               planning_level, planning_status, start_date, end_date, 
                                               planning_notes, planning_metadata, created_at, updated_at, 
                                               last_accessed_at, archived_at, deleted_at, scheduled_deletion_at, 
                                               retention_period)
            VALUES (:plan_name, :plan_description, :student_id, :planning_type, :planning_level, 
                   :planning_status, :start_date, :end_date, :planning_notes, :planning_metadata, 
                   :created_at, :updated_at, :last_accessed_at, :archived_at, :deleted_at, 
                   :scheduled_deletion_at, :retention_period)
        """), planning_plans)
        
        print(f"  ✅ activity_plans_planning: +{len(planning_plans)} records (migrated from students)")
        return len(planning_plans)
        
    except Exception as e:
        print(f"  ❌ activity_plans_planning: {e}")
        session.rollback()
        return 0

def seed_pe_lesson_plans(session: Session) -> int:
    """Seed PE lesson plans table"""
    try:
        # Check if table exists and has data
        result = session.execute(text("SELECT COUNT(*) FROM pe_lesson_plans"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  🔄 pe_lesson_plans already has {existing_count} records, continuing with migration...")
            # Continue with seeding - let ON CONFLICT clauses handle duplicates
        
        # Create sample PE lesson plans
        lesson_plans = []
        pe_subjects = ['Physical Education', 'Health Education', 'Sports Science']
        grade_levels = ['K-2', '3-5', '6-8', '9-12']
        difficulties = ['Beginner', 'Intermediate', 'Advanced']
        
        for i in range(400):
            lesson_plan = {
                'title': f"PE Lesson Plan {i+1}",
                'description': f"Learning objectives for lesson {i+1}. Equipment and materials for lesson {i+1}.",
                'grade_level': random.choice(grade_levels),
                'duration': random.randint(30, 90),
                'difficulty': random.choice(difficulties),
                'class_id': None,  # Set to None to avoid foreign key constraint issues
                'teacher_id': None,  # Set to None to avoid foreign key constraint issues
                'is_completed': random.choice([True, False]),
                'lesson_metadata': f'{{"subject": "{random.choice(pe_subjects)}", "objectives": "Learning objectives for lesson {i+1}", "materials": "Equipment and materials for lesson {i+1}"}}',
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now()
            }
            lesson_plans.append(lesson_plan)
        
        # Insert lesson plans
        session.execute(text("""
            INSERT INTO pe_lesson_plans (title, description, grade_level, duration, 
                                       difficulty, class_id, teacher_id, is_completed, 
                                       lesson_metadata, created_at, updated_at)
            VALUES (:title, :description, :grade_level, :duration, 
                    :difficulty, :class_id, :teacher_id, :is_completed, 
                    :lesson_metadata, :created_at, :updated_at)
        """), lesson_plans)
        
        return len(lesson_plans)
        
    except Exception as e:
        print(f"  ❌ Error seeding pe_lesson_plans: {e}")
        return 0

def seed_lesson_plan_activities(session: Session) -> int:
    """Seed lesson plan activities table"""
    try:
        # Check if table exists and has data
        result = session.execute(text("SELECT COUNT(*) FROM lesson_plan_activities"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  🔄 lesson_plan_activities already has {existing_count} records, continuing with migration...")
            # Continue with seeding - let ON CONFLICT clauses handle duplicates
        
        # Get actual lesson plan IDs from the database
        lesson_plan_result = session.execute(text("SELECT id FROM pe_lesson_plans ORDER BY id"))
        lesson_plan_ids = [row[0] for row in lesson_plan_result.fetchall()]
        
        if not lesson_plan_ids:
            print("  ⚠️  No lesson plans found, skipping activities...")
            return 0
        
        # Create sample lesson plan activities
        activities = []
        activity_types = ['Warm-up', 'Main Activity', 'Cool-down', 'Assessment', 'Game']
        
        for i in range(1200):
            activity = {
                'lesson_plan_id': random.choice(lesson_plan_ids),  # Use actual lesson plan IDs
                'activity_id': random.randint(1, 100),  # Assuming 100 activities exist
                'sequence': random.randint(1, 10),
                'duration': random.randint(5, 30),
                'is_completed': random.choice([True, False]),
                'activity_metadata': f'{{"activity_type": "{random.choice(activity_types)}", "title": "Activity {i+1}", "description": "Description for activity {i+1}"}}',
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now()
            }
            activities.append(activity)
        
        # Insert activities
        session.execute(text("""
            INSERT INTO lesson_plan_activities (lesson_plan_id, activity_id, sequence, 
                                              duration, is_completed, activity_metadata, 
                                              created_at, updated_at)
            VALUES (:lesson_plan_id, :activity_id, :sequence, :duration, 
                    :is_completed, :activity_metadata, :created_at, :updated_at)
        """), activities)
        
        return len(activities)
        
    except Exception as e:
        print(f"  ❌ Error seeding lesson_plan_activities: {e}")
        return 0

def seed_lesson_plan_objectives(session: Session) -> int:
    """Seed lesson plan objectives table"""
    try:
        # Check if table exists and has data
        result = session.execute(text("SELECT COUNT(*) FROM lesson_plan_objectives"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  ⚠️  lesson_plan_objectives already has {existing_count} records, skipping...")
            return existing_count
        
        # Get actual lesson plan IDs from the database
        lesson_plan_result = session.execute(text("SELECT id FROM pe_lesson_plans ORDER BY id"))
        lesson_plan_ids = [row[0] for row in lesson_plan_result.fetchall()]
        
        if not lesson_plan_ids:
            print("  ⚠️  No lesson plans found, skipping objectives...")
            return 0
        
        # Create sample lesson plan objectives
        objectives = []
        objective_types = ['Knowledge', 'Skill', 'Attitude', 'Behavior']
        
        for i in range(2400):
            objective = {
                'lesson_plan_id': random.choice(lesson_plan_ids),  # Use actual lesson plan IDs
                'objective': f"Objective {i+1} for lesson plan",
                'objective_metadata': f'{{"objective_type": "{random.choice(objective_types)}", "is_measurable": {str(random.choice([True, False])).lower()}, "description": "Detailed description for objective {i+1}"}}',
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now()
            }
            objectives.append(objective)
        
        # Insert objectives
        session.execute(text("""
            INSERT INTO lesson_plan_objectives (lesson_plan_id, objective, objective_metadata, 
                                              created_at, updated_at)
            VALUES (:lesson_plan_id, :objective, :objective_metadata, 
                    :created_at, :updated_at)
        """), objectives)
        
        return len(objectives)
        
    except Exception as e:
        print(f"  ❌ Error seeding lesson_plan_objectives: {e}")
        return 0

def seed_curriculum_lessons(session: Session) -> int:
    """Seed curriculum lessons table"""
    try:
        # Check if table exists and has data
        result = session.execute(text("SELECT COUNT(*) FROM curriculum_lessons"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  ⚠️  curriculum_lessons already has {existing_count} records, skipping...")
            return existing_count
        
        # Check if any curriculum-related table has records
        curriculum_ids = []
        possible_curriculum_tables = [
            'curriculum',
            'physical_education_curriculum_units',
            'curriculum_units'
        ]
        
        for table_name in possible_curriculum_tables:
            try:
                result = session.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                count = result.scalar()
                if count > 0:
                    result = session.execute(text(f"SELECT id FROM {table_name} ORDER BY id"))
                    curriculum_ids = [row[0] for row in result.fetchall()]
                    print(f"  📋 Found {len(curriculum_ids)} curriculum records in {table_name}")
                    break
            except Exception as e:
                continue
        
        if not curriculum_ids:
            print(f"  📝 Creating curriculum first...")
            # First create some curriculum records
            curriculums = []
            academic_years = ['2023-2024', '2024-2025', '2025-2026']
            for i in range(5):
                curriculum = {
                    'name': f"PE Curriculum {i+1}",
                    'description': f"Physical Education Curriculum {i+1} for comprehensive PE education",
                    'grade_level': random.choice(['KINDERGARTEN', 'FIRST', 'SECOND', 'THIRD', 'FOURTH', 'FIFTH', 'SIXTH', 'SEVENTH', 'EIGHTH', 'NINTH', 'TENTH', 'ELEVENTH', 'TWELFTH']),
                    'academic_year': random.choice(academic_years),
                    'curriculum_metadata': f'{{"subject": "Physical Education", "focus": "Comprehensive PE Education", "standards": "National PE Standards"}}',
                    'learning_standards': f'{{"national_standards": ["PE.1", "PE.2", "PE.3"], "state_standards": ["S.1", "S.2"], "grade_level": "{random.choice(["K-2", "3-5", "6-8", "9-12"])}"}}',
                    'learning_objectives': f'{{"motor_skills": ["Running", "Jumping", "Throwing"], "fitness": ["Cardiovascular", "Strength", "Flexibility"], "social": ["Teamwork", "Sportsmanship"]}}',
                    'core_competencies': f'{{"physical": ["Coordination", "Balance", "Agility"], "cognitive": ["Strategy", "Rules", "Safety"], "social": ["Communication", "Leadership"]}}',
                    'unit_data': f'{{"units": ["Unit 1: PE Fundamentals", "Unit 2: PE Applications", "Unit 3: PE Mastery"], "unit_count": 3, "unit_duration": "4-6 weeks each"}}',
                    'progression_path': f'{{"beginner": ["Basic PE Concepts", "Introduction to PE Skills"], "intermediate": ["Advanced PE Applications", "Complex PE Problems"], "advanced": ["Mastery of PE", "Independent PE Projects"]}}',
                    'time_allocation': f'{{"total_hours": 120, "weekly_hours": 3, "unit_breakdown": {{"Unit 1": 40, "Unit 2": 40, "Unit 3": 40}}}}',
                    'assessment_criteria': f'{{"formative": ["PE Quizzes", "PE Class Participation"], "summative": ["PE Exams", "PE Projects"], "weighting": {{"Quizzes": 30, "Exams": 50, "Projects": 20}}}}',
                    'evaluation_methods': f'{{"methods": ["PE Written Tests", "PE Practical Assessments", "PE Portfolio Reviews"], "frequency": "Weekly quizzes, monthly exams, semester projects"}}',
                    'version': 1,
                    'is_valid': True,
                    'status': 'ACTIVE',
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                    'updated_at': datetime.now()
                }
                curriculums.append(curriculum)
            
            # Insert curriculum records
            session.execute(text("""
                INSERT INTO curriculum (name, description, grade_level, academic_year, curriculum_metadata, 
                                      learning_standards, learning_objectives, core_competencies,
                                      unit_data, progression_path, time_allocation, assessment_criteria, evaluation_methods,
                                      version, is_valid, status, created_at, updated_at)
                VALUES (:name, :description, :grade_level, :academic_year, :curriculum_metadata, 
                        :learning_standards, :learning_objectives, :core_competencies,
                        :unit_data, :progression_path, :time_allocation, :assessment_criteria, :evaluation_methods,
                        :version, :is_valid, :status, :created_at, :updated_at)
            """), curriculums)
            print(f"  ✅ Created {len(curriculums)} curriculum records")
            
            # Get the curriculum IDs
            curriculum_result = session.execute(text("SELECT id FROM curriculum ORDER BY id"))
            curriculum_ids = [row[0] for row in curriculum_result.fetchall()]
        
        # Always create curriculum units if they don't exist
        print(f"  📝 Creating curriculum units...")
        # Check if units already exist
        existing_units = session.execute(text("SELECT COUNT(*) FROM physical_education_curriculum_units")).scalar()
        if existing_units == 0:
            # Create some curriculum units
            units = []
            for i in range(30):
                unit = {
                    'curriculum_id': random.choice(curriculum_ids),  # Use actual curriculum IDs
                    'name': f"PE Unit {i+1}",
                    'description': f"Physical Education Unit {i+1} covering various activities and skills",
                    'sequence': i + 1,
                    'duration': random.randint(60, 180),
                    'unit_metadata': f'{{"grade_level": "{random.choice(["K-2", "3-5", "6-8", "9-12"])}", "subject": "Physical Education", "focus": "General PE Activities"}}',
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                    'updated_at': datetime.now()
                }
                units.append(unit)
            
            # Insert curriculum units
            session.execute(text("""
                INSERT INTO physical_education_curriculum_units (curriculum_id, name, description, sequence, 
                                                               duration, unit_metadata, created_at, updated_at)
                VALUES (:curriculum_id, :name, :description, :sequence, 
                        :duration, :unit_metadata, :created_at, :updated_at)
            """), units)
            session.commit()  # Commit the curriculum units
            print(f"  ✅ Created {len(units)} curriculum units")
        else:
            print(f"  📋 Found {existing_units} existing curriculum units")
        
        # Get actual unit IDs from the database
        unit_result = session.execute(text("SELECT id FROM physical_education_curriculum_units ORDER BY id"))
        unit_ids = [row[0] for row in unit_result.fetchall()]
        
        if not unit_ids:
            print("  ⚠️  No curriculum units found, skipping lessons...")
            return 0
        
        # Create sample curriculum lessons
        lessons = []
        subjects = ['Physical Education', 'Health Education', 'Sports Science', 'Nutrition']
        grade_levels = ['K-2', '3-5', '6-8', '9-12']
        
        print(f"  📝 Creating 600 curriculum lessons using {len(unit_ids)} available units...")
        
        for i in range(600):
            lesson = {
                'unit_id': random.choice(unit_ids),  # Use actual unit IDs
                'name': f"Curriculum Lesson {i+1}",
                'description': f"Description for curriculum lesson {i+1} covering {random.choice(subjects)} for {random.choice(grade_levels)} students",
                'duration': random.randint(30, 120),
                'lesson_metadata': f'{{"subject": "{random.choice(subjects)}", "grade_level": "{random.choice(grade_levels)}", "sequence_order": {random.randint(1, 50)}, "estimated_duration": {random.randint(30, 120)}}}',
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now()
            }
            lessons.append(lesson)
        
        # Insert lessons
        session.execute(text("""
            INSERT INTO curriculum_lessons (unit_id, name, description, duration, 
                                          lesson_metadata, created_at, updated_at)
            VALUES (:unit_id, :name, :description, :duration, 
                    :lesson_metadata, :created_at, :updated_at)
        """), lessons)
        
        return len(lessons)
        
    except Exception as e:
        print(f"  ❌ Error seeding curriculum_lessons: {e}")
        return 0

def seed_curriculum_standards(session: Session) -> int:
    """Seed curriculum standards table"""
    try:
        # Check if table exists and has data
        result = session.execute(text("SELECT COUNT(*) FROM curriculum_standards"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  ⚠️  curriculum_standards already has {existing_count} records, skipping...")
            return existing_count
        
        # Get actual unit IDs from the database - must use physical_education_curriculum_units due to FK constraint
        unit_ids = []
        
        # First try the required table for the foreign key constraint
        try:
            unit_result = session.execute(text("SELECT id FROM physical_education_curriculum_units ORDER BY id"))
            unit_ids = [row[0] for row in unit_result.fetchall()]
            if unit_ids:
                print(f"  📋 Found {len(unit_ids)} units in physical_education_curriculum_units")
            else:
                print("  📝 No units found in physical_education_curriculum_units, creating some first...")
                # Create some curriculum units first
                curriculum_result = session.execute(text("SELECT id FROM curriculum ORDER BY id LIMIT 5"))
                curriculum_ids = [row[0] for row in curriculum_result.fetchall()]
                
                if curriculum_ids:
                    units = []
                    for i in range(10):
                        unit = {
                            'curriculum_id': random.choice(curriculum_ids),
                            'name': f"PE Unit {i+1}",
                            'description': f"Physical Education Unit {i+1}",
                            'sequence': i + 1,
                            'duration': random.randint(60, 180),
                            'unit_metadata': json.dumps({"subject": "Physical Education", "focus": "General PE Activities"}),
                            'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                            'updated_at': datetime.now()
                        }
                        units.append(unit)
                    
                    session.execute(text("""
                        INSERT INTO physical_education_curriculum_units 
                        (curriculum_id, name, description, sequence, duration, unit_metadata, created_at, updated_at)
                        VALUES (:curriculum_id, :name, :description, :sequence, :duration, :unit_metadata, :created_at, :updated_at)
                    """), units)
                    
                    # Get the newly created unit IDs
                    unit_result = session.execute(text("SELECT id FROM physical_education_curriculum_units ORDER BY id"))
                    unit_ids = [row[0] for row in unit_result.fetchall()]
                    print(f"  ✅ Created {len(unit_ids)} curriculum units")
                else:
                    print("  ⚠️  No curriculum found, skipping standards...")
                    return 0
        except Exception as e:
            print(f"  ⚠️  Error accessing physical_education_curriculum_units: {e}")
            return 0
        
        # Create sample curriculum standards
        standards = []
        categories = ['Motor Skills', 'Fitness', 'Knowledge', 'Behavior', 'Social']
        levels = ['Beginner', 'Intermediate', 'Advanced', 'Expert']
        grade_levels = ['K-2', '3-5', '6-8', '9-12']
        
        print(f"  📝 Creating 50 curriculum standards using {len(unit_ids)} available units...")
        
        for i in range(50):
            standard = {
                'unit_id': random.choice(unit_ids),  # Use actual unit IDs
                'code': f"PE.{random.randint(1, 12)}.{random.randint(1, 5)}",
                'name': f"Standard {i+1}",
                'description': f"Description for standard {i+1} covering {random.choice(categories)} skills",
                'category': random.choice(categories),
                'level': random.choice(levels),
                'grade_level': random.choice(grade_levels),
                'assessment_criteria': f'{{"criteria": "Assessment criteria for standard {i+1}", "rubric": "Standard rubric"}}',
                'performance_indicators': f'{{"indicators": ["Indicator 1", "Indicator 2", "Indicator 3"]}}',
                'learning_outcomes': f'{{"outcomes": ["Outcome 1", "Outcome 2"]}}',
                'version': 1,
                'is_valid': True,
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now()
            }
            standards.append(standard)
        
        # Insert standards
        session.execute(text("""
            INSERT INTO curriculum_standards (unit_id, code, name, description, category, level, 
                                            grade_level, assessment_criteria, performance_indicators, 
                                            learning_outcomes, version, is_valid, created_at, updated_at)
            VALUES (:unit_id, :code, :name, :description, :category, :level, 
                    :grade_level, :assessment_criteria, :performance_indicators, 
                    :learning_outcomes, :version, :is_valid, :created_at, :updated_at)
        """), standards)
        
        session.commit()  # Commit the curriculum standards
        return len(standards)
        
    except Exception as e:
        print(f"  ❌ Error seeding curriculum_standards: {e}")
        return 0

def seed_curriculum_standard_associations(session: Session) -> int:
    """Seed curriculum standard associations table"""
    try:
        # Check if table exists and has data
        result = session.execute(text("SELECT COUNT(*) FROM curriculum_standard_association"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  ⚠️  curriculum_standard_association already has {existing_count} records, skipping...")
            return existing_count
        
        # Get actual curriculum and standard IDs from the database - try multiple tables
        curriculum_ids = []
        standard_ids = []
        
        # Use the correct hardcoded table names - look for the table that actually has data
        curriculum_ids = []
        possible_curriculum_tables = ['curriculum', 'curricula']  # Try curriculum first since that's what's actually seeded
        
        for table_name in possible_curriculum_tables:
            try:
                curriculum_result = session.execute(text(f"SELECT id FROM {table_name} ORDER BY id"))
                curriculum_ids = [row[0] for row in curriculum_result.fetchall()]
                if curriculum_ids:
                    print(f"  📋 Found {len(curriculum_ids)} curriculum records in {table_name}")
                    break
            except Exception as e:
                print(f"  ❌ Error checking {table_name}: {e}")
                continue
        
        # If no curriculum found, skip associations creation (don't create our own data)
        if not curriculum_ids:
            print("  ⚠️  No curriculum found in any table, skipping associations...")
            return 0
        
        # Foreign key constraint now points to curriculum.id, so we can use curriculum_ids directly
        print(f"  📋 Using {len(curriculum_ids)} curriculum records for associations")
        
        # Find the correct standards table that exists and has data
        standard_ids = []
        standard_table_name = None
        
        # Check all possible standards table names
        possible_standards_tables = ['curriculum_standards', 'standards', 'educational_standards']
        
        for table_name in possible_standards_tables:
            try:
                # Check if table exists and has data
                count_result = session.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                count = count_result.scalar()
                if count > 0:
                    # Table exists and has data, get the IDs
                    standard_result = session.execute(text(f"SELECT id FROM {table_name} ORDER BY id"))
                    standard_ids = [row[0] for row in standard_result.fetchall()]
                    standard_table_name = table_name
                    print(f"  📋 Found {len(standard_ids)} standard records in {table_name} table")
                    break
                else:
                    print(f"  📋 Table {table_name} exists but has 0 records")
            except Exception as e:
                print(f"  📋 Table {table_name} does not exist or error: {e}")
                continue
        
        if not standard_ids:
            print("  ⚠️  No standards table found with data, skipping associations...")
            return 0
        
        if not curriculum_ids or not standard_ids:
            print("  ⚠️  No curriculum or standards found, skipping associations...")
            return 0
        
        # Create sample associations with unique combinations
        associations = []
        used_combinations = set()
        
        # Calculate max possible unique combinations
        max_combinations = len(curriculum_ids) * len(standard_ids)
        num_associations = min(200, max_combinations)
        
        for i in range(num_associations):
            # Keep trying until we get a unique combination
            while True:
                curriculum_id = random.choice(curriculum_ids)
                standard_id = random.choice(standard_ids)
                combination = (curriculum_id, standard_id)
                
                if combination not in used_combinations:
                    used_combinations.add(combination)
                    association = {
                        'curriculum_id': curriculum_id,
                        'standard_id': standard_id,
                    }
                    associations.append(association)
                    break
        
        # Insert associations
        session.execute(text("""
            INSERT INTO curriculum_standard_association (curriculum_id, standard_id)
            VALUES (:curriculum_id, :standard_id)
        """), associations)
        
        session.commit()  # Commit the curriculum standard associations
        return len(associations)
        
    except Exception as e:
        print(f"  ❌ Error seeding curriculum_standard_association: {e}")
        return 0

def seed_curriculum(session: Session) -> int:
    """Seed curriculum table"""
    try:
        print(f"  🔍 Checking curriculum table...")
        # Check if table exists and has data
        result = session.execute(text("SELECT COUNT(*) FROM curriculum"))
        existing_count = result.scalar()
        print(f"  📊 Found {existing_count} existing records in curriculum table")
        
        if existing_count > 0:
            print(f"  ⚠️  curriculum already has {existing_count} records, skipping...")
            return existing_count
        
        print(f"  📝 Creating 300+ curriculum records for district-wide coverage...")
        # Create comprehensive curriculum records for entire district
        curriculum_records = []
        grade_levels = ['K', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']
        academic_years = ['2022-2023', '2023-2024', '2024-2025', '2025-2026']
        subjects = ['Physical Education', 'Health Education', 'Mathematics', 'Science', 'English Language Arts', 'Social Studies', 'Art', 'Music', 'Technology', 'Foreign Language']
        schools = ['Elementary School', 'Middle School', 'High School']
        
        # Create curriculum for each subject, grade level, and school combination
        for subject in subjects:
            for grade in grade_levels:
                for school in schools:
                    # Only create relevant combinations (e.g., high school subjects for 9-12)
                    if grade == 'K':
                        grade_num = 0
                    else:
                        grade_num = int(grade)
                    
                    if school == 'Elementary School' and grade_num > 5:
                        continue
                    elif school == 'Middle School' and (grade_num < 6 or grade_num > 8):
                        continue
                    elif school == 'High School' and grade_num < 9:
                        continue
                    
                    for year in academic_years:
                        curriculum_records.append({
                            'name': f"{subject} - Grade {grade} - {school}",
                            'description': f"Comprehensive {subject} curriculum for Grade {grade} at {school}",
                            'grade_level': grade,
                            'academic_year': year,
                            'curriculum_metadata': json.dumps({
                                'subject': subject,
                                'school': school,
                                'grade_level': grade,
                                'academic_year': year,
                                'standards': 'State and National Standards',
                                'focus': f'{subject} Education for Grade {grade}'
                            }),
                            'learning_standards': json.dumps({
                                'national_standards': [f"{subject.upper()}.1", f"{subject.upper()}.2", f"{subject.upper()}.3"],
                                'state_standards': [f"S.{grade}", f"S.{grade}.1"],
                                'grade_level': grade
                            }),
                            'learning_objectives': json.dumps({
                                'cognitive': [f"{subject} Knowledge", f"{subject} Understanding", f"{subject} Application"],
                                'affective': [f"{subject} Appreciation", f"{subject} Interest", f"{subject} Motivation"],
                                'psychomotor': [f"{subject} Skills", f"{subject} Practice", f"{subject} Mastery"]
                            }),
                            'core_competencies': json.dumps({
                                'knowledge': [f"{subject} Concepts", f"{subject} Principles", f"{subject} Theories"],
                                'skills': [f"{subject} Analysis", f"{subject} Problem Solving", f"{subject} Critical Thinking"],
                                'attitudes': [f"{subject} Appreciation", f"{subject} Curiosity", f"{subject} Persistence"]
                            }),
                            'unit_data': json.dumps({
                                'units': [f"Unit 1: {subject} Fundamentals", f"Unit 2: {subject} Applications", f"Unit 3: {subject} Mastery"],
                                'unit_count': 3,
                                'unit_duration': "4-6 weeks each"
                            }),
                            'progression_path': json.dumps({
                                'beginner': [f"Basic {subject} Concepts", f"Introduction to {subject} Skills"],
                                'intermediate': [f"Advanced {subject} Applications", f"Complex {subject} Problems"],
                                'advanced': [f"Mastery of {subject}", f"Independent {subject} Projects"]
                            }),
                            'time_allocation': json.dumps({
                                'total_hours': 120,
                                'weekly_hours': 3,
                                'unit_breakdown': {"Unit 1": 40, "Unit 2": 40, "Unit 3": 40}
                            }),
                            'assessment_criteria': json.dumps({
                                'formative': [f"{subject} Quizzes", f"{subject} Class Participation"],
                                'summative': [f"{subject} Exams", f"{subject} Projects"],
                                'weighting': {"Quizzes": 30, "Exams": 50, "Projects": 20}
                            }),
                            'evaluation_methods': json.dumps({
                                'methods': [f"{subject} Written Tests", f"{subject} Practical Assessments", f"{subject} Portfolio Reviews"],
                                'frequency': "Weekly quizzes, monthly exams, semester projects"
                            }),
                            'version': 1,
                            'is_valid': True,
                            'status': 'ACTIVE',
                            'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                            'updated_at': datetime.now()
                        })
        
        # Limit to reasonable number but ensure good coverage
        curriculum_records = curriculum_records[:300]
        
        print(f"  💾 Inserting {len(curriculum_records)} curriculum records...")
        # Insert curriculum records
        session.execute(text("""
            INSERT INTO curriculum (name, description, grade_level, academic_year, curriculum_metadata, 
                                  learning_standards, learning_objectives, core_competencies,
                                  unit_data, progression_path, time_allocation, assessment_criteria, evaluation_methods,
                                  version, is_valid, status, created_at, updated_at)
            VALUES (:name, :description, :grade_level, :academic_year, :curriculum_metadata, 
                    :learning_standards, :learning_objectives, :core_competencies,
                    :unit_data, :progression_path, :time_allocation, :assessment_criteria, :evaluation_methods,
                    :version, :is_valid, :status, :created_at, :updated_at)
        """), curriculum_records)
        
        print(f"  ✅ Successfully created {len(curriculum_records)} curriculum records")
        return len(curriculum_records)
        
    except Exception as e:
        print(f"  ❌ Error seeding curriculum: {e}")
        import traceback
        traceback.print_exc()
        return 0

def seed_courses(session: Session) -> int:
    """Seed courses table - completely flexible for development"""
    print("  🚀 STARTING seed_courses function")
    try:
        print("  🔍 Checking if courses table exists...")
        # Check if table exists and has data
        result = session.execute(text("SELECT COUNT(*) FROM courses"))
        existing_count = result.scalar()
        print(f"  📊 Current courses count: {existing_count}")
        
        # In development, skip if data already exists (additive only after CASCADE DROP)
        if existing_count > 0:
            print(f"  ⚠️  courses already has {existing_count} records, skipping...")
            return existing_count
        
        # Get user IDs from the correct hardcoded table names - flexible for whatever data exists
        user_ids = []
        possible_user_tables = ['users', 'dashboard_users', 'students', 'teachers']
        
        print(f"  🔍 Looking for user data in tables: {possible_user_tables}")
        for table_name in possible_user_tables:
            try:
                print(f"  🔍 Checking table: {table_name}")
                user_result = session.execute(text(f"SELECT id FROM {table_name} ORDER BY id"))
                user_ids = [row[0] for row in user_result.fetchall()]
                print(f"  📊 {table_name}: {len(user_ids)} records")
                if user_ids:
                    print(f"  📋 Found {len(user_ids)} user records in {table_name}")
                    break
            except Exception as e:
                print(f"  ❌ Error checking {table_name}: {e}")
                import traceback
                print(f"  🔍 Full traceback: {traceback.format_exc()}")
                continue
        
        # If no users found, try one more time with a fresh query
        if not user_ids:
            print("  ⚠️  No users found in any table, trying fresh query...")
            try:
                # Try a fresh query to users table
                user_result = session.execute(text("SELECT id FROM users ORDER BY id"))
                user_ids = [row[0] for row in user_result.fetchall()]
                if user_ids:
                    print(f"  📋 Found {len(user_ids)} user records on retry")
                else:
                    print("  ⚠️  Still no users found, skipping courses creation...")
                    return 0
            except Exception as e:
                print(f"  ⚠️  Error on retry: {e}, skipping courses creation...")
                import traceback
                print(f"  🔍 Full traceback: {traceback.format_exc()}")
                return 0
        
        print(f"  🎯 Proceeding with {len(user_ids)} users to create courses...")
        
        # Create sample courses with unique codes
        courses = []
        course_names = ['Physical Education Fundamentals', 'Health and Wellness', 'Sports Science', 'Nutrition Basics', 'Fitness Training', 'Team Sports', 'Individual Sports', 'Outdoor Education']
        used_codes = set()
        
        print("  🔨 Creating course data...")
        for i in range(25):
            # Generate unique course code
            while True:
                code = f"PE{random.randint(100, 999)}"
                if code not in used_codes:
                    used_codes.add(code)
                    break
            
            course = {
                'name': f"{random.choice(course_names)} {i+1}",
                'code': code,
                'description': f"Description for {random.choice(course_names)} course {i+1}",
                'created_by': random.choice(user_ids),  # Use actual user ID
                'is_active': random.choice([True, False]),
                'start_date': datetime.now() - timedelta(days=random.randint(1, 365)),
                'end_date': datetime.now() + timedelta(days=random.randint(30, 365)),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now()
            }
            courses.append(course)
        
        print(f"  📝 Created {len(courses)} course records, inserting into database...")
        
        # Insert courses
        session.execute(text("""
            INSERT INTO courses (name, code, description, created_by, is_active, 
                               start_date, end_date, created_at, updated_at)
            VALUES (:name, :code, :description, :created_by, :is_active, 
                    :start_date, :end_date, :created_at, :updated_at)
        """), courses)
        
        print("  💾 Committing courses to database...")
        session.commit()  # Commit the courses
        
        print(f"  ✅ Successfully created {len(courses)} courses")
        return len(courses)
        
    except Exception as e:
        print(f"  ❌ Error seeding courses: {e}")
        import traceback
        print(f"  🔍 Full traceback: {traceback.format_exc()}")
        return 0

def seed_course_enrollments(session: Session) -> int:
    """Seed course enrollments table"""
    try:
        # Check if table exists first
        table_exists = session.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'course_enrollments'
            )
        """)).scalar()
        
        if not table_exists:
            print("  ⚠️  course_enrollments table does not exist, skipping...")
            return 0
        
        # Check if table has data
        result = session.execute(text("SELECT COUNT(*) FROM course_enrollments"))
        existing_count = result.scalar()
        
        # In development, skip if data already exists (additive only after CASCADE DROP)
        if existing_count > 0:
            print(f"  ⚠️  course_enrollments already has {existing_count} records, skipping...")
            return existing_count
        
        # Get actual course IDs and user IDs from the database - try multiple tables
        course_ids = []
        user_ids = []
        
        # Only use course IDs from the courses table to avoid foreign key violations
        course_ids = []
        try:
            course_result = session.execute(text("SELECT id FROM courses ORDER BY id"))
            course_ids = [row[0] for row in course_result.fetchall()]
            if course_ids:
                print(f"  📋 Found {len(course_ids)} course records in courses table")
            else:
                print("  ⚠️  No courses found in courses table, skipping enrollments...")
                return 0
        except Exception as e:
            print(f"  ⚠️  Error accessing courses table: {e}")
            return 0
        
        # Try to find user IDs - try multiple sources for flexibility
        user_ids = []
        possible_user_tables = ['users', 'dashboard_users', 'students', 'teachers']
        for table_name in possible_user_tables:
            try:
                user_result = session.execute(text(f"SELECT id FROM {table_name} ORDER BY id"))
                user_ids = [row[0] for row in user_result.fetchall()]
                if user_ids:
                    print(f"  📋 Found {len(user_ids)} user records in {table_name}")
                    break
            except Exception as e:
                continue
        
        if not user_ids:
            print("  ⚠️  No users found in any table, skipping enrollments...")
            return 0
        
        # Create sample enrollments with unique combinations
        enrollments = []
        used_combinations = set()
        roles = ['student', 'teacher', 'assistant', 'observer']
        
        # Calculate max possible unique combinations
        max_combinations = len(course_ids) * len(user_ids)
        num_enrollments = min(500, max_combinations)
        
        for i in range(num_enrollments):
            # Keep trying until we get a unique combination
            while True:
                course_id = random.choice(course_ids)
                user_id = random.choice(user_ids)
                combination = (course_id, user_id)
                
                if combination not in used_combinations:
                    used_combinations.add(combination)
                    enrollment = {
                        'course_id': course_id,
                        'user_id': user_id,
                        'role': random.choice(roles)
                    }
                    enrollments.append(enrollment)
                    break
        
        # Insert enrollments
        session.execute(text("""
            INSERT INTO course_enrollments (course_id, user_id, role)
            VALUES (:course_id, :user_id, :role)
        """), enrollments)
        
        session.commit()  # Commit the course enrollments
        return len(enrollments)
        
    except Exception as e:
        print(f"  ❌ Error seeding course_enrollments: {e}")
        return 0

def seed_assignments(session: Session) -> int:
    """Seed assignments table"""
    print("  🚀 STARTING seed_assignments function")
    try:
        print("  🔍 Checking if assignments table exists...")
        # Check if table exists and has data
        result = session.execute(text("SELECT COUNT(*) FROM assignments"))
        existing_count = result.scalar()
        print(f"  📊 Current assignments count: {existing_count}")
        
        # In development, skip if data already exists (additive only after CASCADE DROP)
        if existing_count > 0:
            print(f"  ⚠️  assignments already has {existing_count} records, skipping...")
            return existing_count
        
        print("  🔍 Looking for course IDs...")
        # Get actual course IDs from the database
        course_result = session.execute(text("SELECT id FROM courses ORDER BY id"))
        course_ids = [row[0] for row in course_result.fetchall()]
        print(f"  📊 Found {len(course_ids)} course IDs")
        
        if not course_ids:
            print("  ⚠️  No courses found, skipping assignments...")
            return 0
        
        print("  🔨 Creating assignment data...")
        # Create sample assignments using only existing columns
        assignments = []
        statuses = ['DRAFT', 'PUBLISHED', 'CLOSED', 'GRADED']
        
        for i in range(800):
            assignment = {
                'course_id': random.choice(course_ids),  # Use actual course IDs
                'title': f"Assignment {i+1}",
                'description': f"Description for assignment {i+1}",
                'due_date': datetime.now() + timedelta(days=random.randint(1, 30)),
                'created_by': 1,  # Default user ID
                'rubric_id': None,  # No rubric for now
                'status': random.choice(statuses),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now()
            }
            assignments.append(assignment)
        
        print(f"  📝 Created {len(assignments)} assignment records, inserting into database...")
        
        # Insert assignments using only existing columns
        session.execute(text("""
            INSERT INTO assignments (course_id, title, description, due_date, 
                                   created_by, rubric_id, status, created_at, updated_at)
            VALUES (:course_id, :title, :description, :due_date, 
                    :created_by, :rubric_id, :status, :created_at, :updated_at)
        """), assignments)
        
        print("  💾 Committing assignments to database...")
        session.commit()  # Commit the assignments
        
        print(f"  ✅ Successfully created {len(assignments)} assignments")
        return len(assignments)
        
    except Exception as e:
        print(f"  ❌ Error seeding assignments: {e}")
        import traceback
        print(f"  🔍 Full traceback: {traceback.format_exc()}")
        return 0

def seed_grades(session: Session) -> int:
    """Seed grades table"""
    try:
        # Check if table exists first
        table_exists = session.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'grades'
            )
        """)).scalar()
        
        if not table_exists:
            print("  ⚠️  grades table does not exist, skipping...")
            return 0
        
        # Check if table has data
        result = session.execute(text("SELECT COUNT(*) FROM grades"))
        existing_count = result.scalar()
        
        # In development, skip if data already exists (additive only after CASCADE DROP)
        if existing_count > 0:
            print(f"  ⚠️  grades already has {existing_count} records, skipping...")
            return existing_count
        
        # Get actual assignment and student IDs from the database
        assignment_result = session.execute(text("SELECT id FROM assignments ORDER BY id"))
        assignment_ids = [row[0] for row in assignment_result.fetchall()]
        
        # Try multiple sources for user IDs
        user_ids = []
        possible_user_tables = ['users', 'dashboard_users', 'students']
        
        for table_name in possible_user_tables:
            try:
                user_result = session.execute(text(f"SELECT id FROM {table_name} ORDER BY id"))
                user_ids = [row[0] for row in user_result.fetchall()]
                if user_ids:
                    print(f"  📋 Found {len(user_ids)} user records in {table_name}")
                    break
            except Exception as e:
                continue
        
        if not user_ids:
            print("  ⚠️  No users found in any table, skipping enrollments...")
            return 0
        
        if not assignment_ids:
            print("  ⚠️  No assignments found, skipping grades...")
            return 0
        
        # Create sample grades using only existing columns
        grades = []
        statuses = ['GRADED', 'PENDING', 'INCOMPLETE']
        
        for i in range(1200):
            numeric_score = random.randint(60, 100)
            grade = {
                'assignment_id': random.choice(assignment_ids),  # Use actual assignment IDs
                'student_id': random.choice(user_ids),           # Use actual user IDs
                'grade': numeric_score / 100.0,  # Convert to decimal
                'feedback': f"Feedback for assignment {i+1}",
                'submitted_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'graded_at': datetime.now() - timedelta(days=random.randint(1, 15)),
                'grader_id': random.choice(user_ids),
                'status': random.choice(statuses)
            }
            grades.append(grade)
        
        # Insert grades using only existing columns
        session.execute(text("""
            INSERT INTO grades (assignment_id, student_id, grade, feedback, submitted_at, 
                               graded_at, grader_id, status)
            VALUES (:assignment_id, :student_id, :grade, :feedback, :submitted_at, 
                    :graded_at, :grader_id, :status)
        """), grades)
        
        return len(grades)
        
    except Exception as e:
        print(f"  ❌ Error seeding grades: {e}")
        return 0

def seed_rubrics(session: Session) -> int:
    """Seed rubrics table"""
    try:
        # Check if table exists and has data
        result = session.execute(text("SELECT COUNT(*) FROM rubrics"))
        existing_count = result.scalar()
        
        # In development, skip if data already exists (additive only after CASCADE DROP)
        if existing_count > 0:
            print(f"  ⚠️  rubrics already has {existing_count} records, skipping...")
            return existing_count
        
        # Get actual user IDs for created_by field
        user_result = session.execute(text("SELECT id FROM dashboard_users ORDER BY id"))
        user_ids = [row[0] for row in user_result.fetchall()]
        
        if not user_ids:
            print("  ⚠️  No users found, skipping rubrics...")
            return 0
        
        # Create sample rubrics
        rubrics = []
        
        for i in range(40):
            # Create sample criteria as JSON
            criteria = {
                "criteria_1": {
                    "description": f"Criteria 1 for rubric {i+1}",
                    "points": random.randint(5, 25)
                },
                "criteria_2": {
                    "description": f"Criteria 2 for rubric {i+1}",
                    "points": random.randint(5, 25)
                },
                "criteria_3": {
                    "description": f"Criteria 3 for rubric {i+1}",
                    "points": random.randint(5, 25)
                }
            }
            
            rubric = {
                'name': f"Rubric {i+1}",
                'criteria': json.dumps(criteria),  # Convert dict to JSON string
                'total_points': sum(c['points'] for c in criteria.values()),
                'created_by': random.choice(user_ids),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now()
            }
            rubrics.append(rubric)
        
        # Insert rubrics
        session.execute(text("""
            INSERT INTO rubrics (name, criteria, total_points, created_by, 
                               created_at, updated_at)
            VALUES (:name, :criteria, :total_points, :created_by, 
                    :created_at, :updated_at)
        """), rubrics)
        
        return len(rubrics)
        
    except Exception as e:
        print(f"  ❌ Error seeding rubrics: {e}")
        return 0

# ============================================================================
# SECTION 2.2: TEACHER & CLASS MANAGEMENT SEEDING FUNCTIONS
# ============================================================================

def seed_teacher_availability(session: Session) -> int:
    """Seed teacher availability table"""
    try:
        # Check if table exists and has data
        result = session.execute(text("SELECT COUNT(*) FROM teacher_availability"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  ⚠️  teacher_availability already has {existing_count} records, skipping...")
            return existing_count
        
        # Get actual teacher IDs from physical_education_teachers table
        teacher_result = session.execute(text("SELECT id FROM physical_education_teachers ORDER BY id"))
        teacher_ids = [row[0] for row in teacher_result.fetchall()]
        
        if not teacher_ids:
            print("  ⚠️  No teachers found, skipping teacher availability...")
            return 0
        
        # Create sample teacher availability records
        availability_records = []
        
        for i in range(100):
            # Create availability metadata as JSON
            availability_metadata = {
                "notes": f"Availability notes for teacher {i+1}",
                "location": f"Room {random.randint(100, 999)}",
                "contact_method": random.choice(["email", "phone", "in-person"])
            }
            
            availability = {
                'teacher_id': random.choice(teacher_ids),
                'day_of_week': random.randint(0, 6),  # 0=Sunday, 6=Saturday
                'start_time': datetime.now() + timedelta(hours=random.randint(0, 24)),
                'end_time': datetime.now() + timedelta(hours=random.randint(1, 8)),
                'is_available': random.choice([True, False]),
                'availability_metadata': json.dumps(availability_metadata),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now(),
                'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'archived_at': None,
                'deleted_at': None,
                'scheduled_deletion_at': None,
                'retention_period': random.randint(30, 365)
            }
            availability_records.append(availability)
        
        # Insert availability records
        session.execute(text("""
            INSERT INTO teacher_availability (teacher_id, day_of_week, start_time, end_time, 
                                            is_available, availability_metadata, created_at, 
                                            updated_at, last_accessed_at, archived_at, deleted_at, 
                                            scheduled_deletion_at, retention_period)
            VALUES (:teacher_id, :day_of_week, :start_time, :end_time, :is_available, 
                    :availability_metadata, :created_at, :updated_at, :last_accessed_at, 
                    :archived_at, :deleted_at, :scheduled_deletion_at, :retention_period)
        """), availability_records)
        
        return len(availability_records)
        
    except Exception as e:
        print(f"  ❌ Error seeding teacher_availability: {e}")
        return 0

def seed_teacher_certifications(session: Session) -> int:
    """Seed teacher certifications table"""
    try:
        # Check if table exists and has data
        result = session.execute(text("SELECT COUNT(*) FROM teacher_certifications"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  ⚠️  teacher_certifications already has {existing_count} records, skipping...")
            return existing_count
        
        # Get actual teacher IDs from physical_education_teachers table
        teacher_result = session.execute(text("SELECT id FROM physical_education_teachers ORDER BY id"))
        teacher_ids = [row[0] for row in teacher_result.fetchall()]
        
        if not teacher_ids:
            print("  ⚠️  No teachers found, skipping teacher certifications...")
            return 0
        
        # Create sample teacher certifications
        certifications = []
        cert_types = ['CPR', 'FIRST_AID', 'PHYSICAL_EDUCATION', 'COACHING', 'SPORTS_MEDICINE', 'NUTRITION', 'FITNESS', 'SPECIAL_NEEDS', 'ATHLETIC_TRAINING', 'EXERCISE_SCIENCE', 'HEALTH_EDUCATION', 'ADAPTIVE_PE', 'YOGA', 'PILATES', 'DANCE', 'MARTIAL_ARTS', 'AQUATICS', 'OUTDOOR_EDUCATION', 'ADVENTURE_SPORTS', 'TEAM_SPORTS', 'INDIVIDUAL_SPORTS', 'STRENGTH_TRAINING', 'CARDIOVASCULAR', 'FLEXIBILITY', 'BALANCE', 'COORDINATION']
        
        for i in range(80):
            # Create certification metadata as JSON
            certification_metadata = {
                "description": f"Certification details for {random.choice(cert_types)}",
                "requirements": ["Background check", "Training completion", "Exam passed"],
                "renewal_required": random.choice([True, False])
            }
            
            certification = {
                'teacher_id': random.choice(teacher_ids),
                'type': random.choice(cert_types),
                'certification_number': f"CERT-{random.randint(10000, 99999)}",
                'issue_date': datetime.now() - timedelta(days=random.randint(1, 1825)),  # Up to 5 years ago
                'expiry_date': datetime.now() + timedelta(days=random.randint(1, 1825)),  # Up to 5 years in future
                'issuing_organization': f"Organization {random.randint(1, 10)}",
                'certification_metadata': json.dumps(certification_metadata),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now(),
                'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'archived_at': None,
                'deleted_at': None,
                'scheduled_deletion_at': None,
                'retention_period': random.randint(30, 365)
            }
            certifications.append(certification)
        
        # Insert certifications
        session.execute(text("""
            INSERT INTO teacher_certifications (teacher_id, type, certification_number, 
                                              issue_date, expiry_date, issuing_organization, 
                                              certification_metadata, created_at, updated_at, 
                                              last_accessed_at, archived_at, deleted_at, 
                                              scheduled_deletion_at, retention_period)
            VALUES (:teacher_id, :type, :certification_number, :issue_date, 
                    :expiry_date, :issuing_organization, :certification_metadata, :created_at, 
                    :updated_at, :last_accessed_at, :archived_at, :deleted_at, 
                    :scheduled_deletion_at, :retention_period)
        """), certifications)
        
        return len(certifications)
        
    except Exception as e:
        print(f"  ❌ Error seeding teacher_certifications: {e}")
        return 0

def seed_teacher_preferences(session: Session) -> int:
    """Seed teacher preferences table"""
    try:
        # Check if table exists and has data
        result = session.execute(text("SELECT COUNT(*) FROM teacher_preferences"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  ⚠️  teacher_preferences already has {existing_count} records, skipping...")
            return existing_count
        
        # Get actual teacher IDs from physical_education_teachers table
        teacher_result = session.execute(text("SELECT id FROM physical_education_teachers ORDER BY id"))
        teacher_ids = [row[0] for row in teacher_result.fetchall()]
        
        if not teacher_ids:
            print("  ⚠️  No teachers found, skipping teacher preferences...")
            return 0
        
        # Create sample teacher preferences
        preferences = []
        preference_types = ['Class Size', 'Teaching Style', 'Assessment Method', 'Technology Usage']
        
        for i in range(50):
            # Create preference metadata as JSON
            preference_metadata = {
                "description": f"Preference details for {random.choice(preference_types)}",
                "category": random.choice(["academic", "administrative", "personal"]),
                "importance": random.choice(["high", "medium", "low"]),
                "is_active": random.choice([True, False])
            }
            
            preference = {
                'teacher_id': random.choice(teacher_ids),
                'preference_type': random.choice(preference_types),
                'preference_value': f"Preference value {i+1}",
                'preference_metadata': json.dumps(preference_metadata),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now(),
                'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'archived_at': None,
                'deleted_at': None,
                'scheduled_deletion_at': None,
                'retention_period': random.randint(30, 365)
            }
            preferences.append(preference)
        
        # Insert preferences
        session.execute(text("""
            INSERT INTO teacher_preferences (teacher_id, preference_type, preference_value, 
                                           preference_metadata, created_at, updated_at, 
                                           last_accessed_at, archived_at, deleted_at, 
                                           scheduled_deletion_at, retention_period)
            VALUES (:teacher_id, :preference_type, :preference_value, :preference_metadata, 
                    :created_at, :updated_at, :last_accessed_at, :archived_at, :deleted_at, 
                    :scheduled_deletion_at, :retention_period)
        """), preferences)
        
        return len(preferences)
        
    except Exception as e:
        print(f"  ❌ Error seeding teacher_preferences: {e}")
        return 0

def seed_teacher_qualifications(session: Session) -> int:
    """Seed teacher qualifications table"""
    try:
        # Check if table exists and has data
        result = session.execute(text("SELECT COUNT(*) FROM teacher_qualifications"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  ⚠️  teacher_qualifications already has {existing_count} records, skipping...")
            return existing_count
        
        # Get actual teacher IDs from physical_education_teachers table
        teacher_result = session.execute(text("SELECT id FROM physical_education_teachers ORDER BY id"))
        teacher_ids = [row[0] for row in teacher_result.fetchall()]
        
        if not teacher_ids:
            print("  ⚠️  No teachers found, skipping teacher qualifications...")
            return 0
        
        # Create sample teacher qualifications
        qualifications = []
        qualification_names = ['Bachelor of Physical Education', 'Master of Sports Science', 'PhD in Health Education', 'Associate in Education', 'Certified Personal Trainer', 'Sports Medicine Certification']
        organizations = ['University of Sports', 'National Education Board', 'International Sports Federation', 'Health Education Council', 'Physical Education Institute']
        
        for i in range(60):
            # Create qualification metadata as JSON
            qualification_metadata = {
                "description": f"Qualification details for {random.choice(qualification_names)}",
                "category": random.choice(["academic", "professional", "certification"]),
                "level": random.choice(["beginner", "intermediate", "advanced", "expert"]),
                "is_verified": random.choice([True, False])
            }
            
            qualification = {
                'teacher_id': random.choice(teacher_ids),
                'qualification_name': random.choice(qualification_names),
                'issuing_organization': random.choice(organizations),
                'issue_date': datetime.now() - timedelta(days=random.randint(1, 1825)),
                'expiry_date': datetime.now() + timedelta(days=random.randint(1, 1825)),
                'qualification_notes': f"Qualification notes for teacher {i+1}",
                'qualification_metadata': json.dumps(qualification_metadata),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now(),
                'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'archived_at': None,
                'deleted_at': None,
                'scheduled_deletion_at': None,
                'retention_period': random.randint(30, 365)
            }
            qualifications.append(qualification)
        
        # Insert qualifications
        session.execute(text("""
            INSERT INTO teacher_qualifications (teacher_id, qualification_name, issuing_organization, 
                                              issue_date, expiry_date, qualification_notes, 
                                              qualification_metadata, created_at, updated_at, 
                                              last_accessed_at, archived_at, deleted_at, 
                                              scheduled_deletion_at, retention_period)
            VALUES (:teacher_id, :qualification_name, :issuing_organization, :issue_date, 
                    :expiry_date, :qualification_notes, :qualification_metadata, :created_at, 
                    :updated_at, :last_accessed_at, :archived_at, :deleted_at, 
                    :scheduled_deletion_at, :retention_period)
        """), qualifications)
        
        return len(qualifications)
        
    except Exception as e:
        print(f"  ❌ Error seeding teacher_qualifications: {e}")
        return 0

def seed_teacher_schedules(session: Session) -> int:
    """Seed teacher schedules table"""
    try:
        # Check if table exists and has data
        result = session.execute(text("SELECT COUNT(*) FROM teacher_schedules"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  ⚠️  teacher_schedules already has {existing_count} records, skipping...")
            return existing_count
        
        # Get actual teacher IDs from physical_education_teachers table
        teacher_result = session.execute(text("SELECT id FROM physical_education_teachers ORDER BY id"))
        teacher_ids = [row[0] for row in teacher_result.fetchall()]
        
        if not teacher_ids:
            print("  ⚠️  No teachers found, skipping teacher schedules...")
            return 0
        
        # Get actual class IDs from physical_education_classes table
        class_result = session.execute(text("SELECT id FROM physical_education_classes ORDER BY id"))
        class_ids = [row[0] for row in class_result.fetchall()]
        
        if not class_ids:
            print("  ⚠️  No classes found, skipping teacher schedules...")
            return 0
        
        # Create sample teacher schedules
        schedules = []
        schedule_types = ['Regular', 'Substitute', 'Special Event', 'Professional Development']
        statuses = ['scheduled', 'confirmed', 'cancelled', 'completed']
        
        for i in range(100):
            # Create schedule metadata as JSON
            schedule_metadata = {
                "description": f"Schedule details for {random.choice(schedule_types)}",
                "category": random.choice(["teaching", "administrative", "professional", "special"]),
                "priority": random.choice(["high", "medium", "low"]),
                "is_recurring": random.choice([True, False])
            }
            
            schedule = {
                'teacher_id': random.choice(teacher_ids),
                'class_id': random.choice(class_ids),  # Use actual class IDs
                'schedule_date': datetime.now() + timedelta(days=random.randint(1, 30)),
                'start_time': datetime.now() + timedelta(hours=random.randint(7, 17)),  # 7 AM to 5 PM
                'end_time': datetime.now() + timedelta(hours=random.randint(8, 18)),   # 8 AM to 6 PM
                'status': random.choice(statuses),
                'schedule_notes': f"Schedule notes for teacher {i+1}",
                'schedule_metadata': json.dumps(schedule_metadata),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now(),
                'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'archived_at': None,
                'deleted_at': None,
                'scheduled_deletion_at': None,
                'retention_period': random.randint(30, 365)
            }
            schedules.append(schedule)
        
        # Insert schedules
        session.execute(text("""
            INSERT INTO teacher_schedules (teacher_id, class_id, schedule_date, start_time, 
                                         end_time, status, schedule_notes, schedule_metadata, 
                                         created_at, updated_at, last_accessed_at, archived_at, 
                                         deleted_at, scheduled_deletion_at, retention_period)
            VALUES (:teacher_id, :class_id, :schedule_date, :start_time, :end_time, :status, 
                    :schedule_notes, :schedule_metadata, :created_at, :updated_at, 
                    :last_accessed_at, :archived_at, :deleted_at, :scheduled_deletion_at, 
                    :retention_period)
        """), schedules)
        
        return len(schedules)
        
    except Exception as e:
        print(f"  ❌ Error seeding teacher_schedules: {e}")
        return 0

def seed_teacher_specializations(session: Session) -> int:
    """Seed teacher specializations table"""
    try:
        # Check if table exists and has data
        result = session.execute(text("SELECT COUNT(*) FROM teacher_specializations"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  ⚠️  teacher_specializations already has {existing_count} records, skipping...")
            return existing_count
        
        # Get actual teacher IDs from physical_education_teachers table
        teacher_result = session.execute(text("SELECT id FROM physical_education_teachers ORDER BY id"))
        teacher_ids = [row[0] for row in teacher_result.fetchall()]
        
        if not teacher_ids:
            print("  ⚠️  No teachers found, skipping teacher specializations...")
            return 0
        
        # Create sample teacher specializations
        specializations = []
        spec_names = ['Elementary PE', 'Secondary PE', 'Adaptive PE', 'Health Education', 'Sports Coaching', 'Fitness Training', 'Recreation Management']
        
        for i in range(75):
            # Create specialization metadata as JSON
            specialization_metadata = {
                "area": random.choice(['Elementary PE', 'Secondary PE', 'Adaptive PE', 'Health Education', 'Sports Coaching']),
                "certification_level": random.choice(['Basic', 'Intermediate', 'Advanced', 'Expert']),
                "is_primary": random.choice([True, False]),
                "focus_areas": random.sample(['Team Sports', 'Individual Sports', 'Fitness', 'Health', 'Adaptive'], random.randint(1, 3))
            }
            
            specialization = {
                'teacher_id': random.choice(teacher_ids),
                'specialization_name': random.choice(spec_names),
                'description': f"Specialization in {random.choice(spec_names)} with {random.randint(1, 20)} years of experience",
                'years_experience': random.randint(1, 20),
                'specialization_metadata': json.dumps(specialization_metadata),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now(),
                'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'archived_at': None,
                'deleted_at': None,
                'scheduled_deletion_at': None,
                'retention_period': random.randint(30, 365)
            }
            specializations.append(specialization)
        
        # Insert specializations
        session.execute(text("""
            INSERT INTO teacher_specializations (teacher_id, specialization_name, description, years_experience, 
                                               specialization_metadata, created_at, updated_at, last_accessed_at, 
                                               archived_at, deleted_at, scheduled_deletion_at, retention_period)
            VALUES (:teacher_id, :specialization_name, :description, :years_experience, :specialization_metadata, 
                    :created_at, :updated_at, :last_accessed_at, :archived_at, :deleted_at, 
                    :scheduled_deletion_at, :retention_period)
        """), specializations)
        
        return len(specializations)
        
    except Exception as e:
        print(f"  ❌ Error seeding teacher_specializations: {e}")
        return 0

def seed_educational_classes(session: Session) -> int:
    """Seed educational classes table"""
    try:
        print(f"  🔍 Checking educational_classes table...")
        # Check if table exists and has data
        result = session.execute(text("SELECT COUNT(*) FROM educational_classes"))
        existing_count = result.scalar()
        print(f"  📊 Found {existing_count} existing records in educational_classes table")
        
        # Additive approach - work with existing data
        if existing_count > 0:
            print(f"  ⚠️  educational_classes already has {existing_count} records, skipping...")
            return existing_count
        
        print(f"  🔍 Querying educational_teachers table...")
        # Get actual teacher IDs from educational_teachers table
        teacher_result = session.execute(text("SELECT id FROM educational_teachers ORDER BY id"))
        teacher_ids = [row[0] for row in teacher_result.fetchall()]
        print(f"  📊 Found {len(teacher_ids)} educational teachers")
        
        if not teacher_ids:
            print("  ⚠️  No educational teachers found, skipping educational classes...")
            return 0
        
        # Create sample educational classes
        classes = []
        class_types = ['REGULAR', 'SPECIAL_NEEDS', 'ATHLETIC', 'RECREATIONAL', 'COMPETITIVE', 'ADVANCED', 'BEGINNER']
        subjects = ['Physical Education', 'Health Education', 'Sports Science']
        statuses = ['PLANNED', 'ACTIVE', 'COMPLETED', 'CANCELLED', 'ON_HOLD']
        locations = ['Gymnasium A', 'Gymnasium B', 'Outdoor Field', 'Classroom 101', 'Classroom 102']
        
        # Calculate appropriate number of classes based on teachers and students
        # Each teacher should have 6-8 classes, with 20-30 students per class
        # For a district with 4000+ students, we need more classes
        num_classes = len(teacher_ids) * random.randint(6, 8)  # 6-8 classes per teacher
        print(f"  📝 Creating {num_classes} educational classes for {len(teacher_ids)} teachers...")
        
        for i in range(num_classes):
            # Create schedule metadata as JSON
            schedule_metadata = {
                "days": random.sample(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'], random.randint(2, 5)),
                "start_time": f"{random.randint(8, 15)}:00",
                "end_time": f"{random.randint(9, 16)}:00",
                "duration_minutes": random.choice([45, 50, 60, 90])
            }
            
            class_record = {
                'name': f"Class {i+1}",
                'description': f"Educational class for {random.choice(subjects)} - {random.choice(class_types)} level",
                'grade_level': str(random.randint(1, 12)),  # Convert to string as it's VARCHAR
                'max_students': random.randint(15, 35),
                'schedule': json.dumps(schedule_metadata),
                'location': random.choice(locations),
                'class_type': random.choice(class_types),
                'instructor_id': random.choice(teacher_ids),
                'start_date': datetime.now() + timedelta(days=random.randint(1, 30)),
                'end_date': datetime.now() + timedelta(days=random.randint(60, 180)),
                'status': random.choice(statuses),
                'is_active': random.choice([True, False]),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now(),
                'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'archived_at': None,
                'deleted_at': None,
                'scheduled_deletion_at': None,
                'retention_period': random.randint(30, 365)
            }
            classes.append(class_record)
        
        # Insert classes
        session.execute(text("""
            INSERT INTO educational_classes (name, description, grade_level, max_students, schedule, 
                                           location, class_type, instructor_id, start_date, end_date, 
                                           status, is_active, created_at, updated_at, last_accessed_at, 
                                           archived_at, deleted_at, scheduled_deletion_at, retention_period)
            VALUES (:name, :description, :grade_level, :max_students, :schedule, :location, 
                    :class_type, :instructor_id, :start_date, :end_date, :status, :is_active, 
                    :created_at, :updated_at, :last_accessed_at, :archived_at, :deleted_at, 
                    :scheduled_deletion_at, :retention_period)
        """), classes)
        
        session.commit()
        print(f"  ✅ Successfully created {len(classes)} educational classes")
        return len(classes)
        
    except Exception as e:
        print(f"  ❌ Error seeding educational_classes: {e}")
        import traceback
        traceback.print_exc()
        return 0

def seed_educational_class_students(session: Session) -> int:
    """Seed educational class students table"""
    try:
        # Check if table exists and has data
        result = session.execute(text("SELECT COUNT(*) FROM educational_class_students"))
        existing_count = result.scalar()
        
        # In development, skip if data already exists (additive only after CASCADE DROP)
        if existing_count > 0:
            print(f"  ⚠️  educational_class_students already has {existing_count} records, skipping...")
            return existing_count
        
        # Get actual class IDs and student IDs from the database
        class_result = session.execute(text("SELECT id FROM educational_classes ORDER BY id"))
        class_ids = [row[0] for row in class_result.fetchall()]
        
        # Get actual student IDs from the database - try multiple sources for flexibility
        student_ids = []
        possible_student_tables = ['students', 'dashboard_users', 'users']
        
        for table_name in possible_student_tables:
            try:
                student_result = session.execute(text(f"SELECT id FROM {table_name} ORDER BY id"))
                student_ids = [row[0] for row in student_result.fetchall()]
                if student_ids:
                    print(f"  📋 Found {len(student_ids)} student records in {table_name}")
                    break
            except Exception as e:
                continue
        
        if not student_ids:
            print("  ⚠️  No students found in any table, creating fallback student IDs...")
            student_ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]  # Fallback IDs for development
        
        if not class_ids:
            print("  ⚠️  No classes found, skipping enrollments...")
            return 0
        
        # Create realistic class student enrollments
        enrollments = []
        statuses = ['Active', 'Dropped', 'Completed', 'On Hold']
        
        # Calculate realistic number of enrollments
        # Each student should be in 2-4 classes, with 20-30 students per class
        # Use the smaller of: (students * 3) or (classes * 25)
        num_enrollments = min(len(student_ids) * 3, len(class_ids) * 25)
        print(f"  📝 Creating {num_enrollments} class enrollments for {len(student_ids)} students across {len(class_ids)} classes...")
        
        for i in range(num_enrollments):
            # Create performance and attendance data as JSON
            performance_data = {
                "overall_score": random.randint(60, 100),
                "participation": random.randint(70, 100),
                "assignments_completed": random.randint(5, 20),
                "last_assessment_score": random.randint(50, 100)
            }
            
            attendance_record = {
                "total_classes": random.randint(15, 30),
                "attended": random.randint(10, 25),
                "absences": random.randint(0, 5),
                "tardies": random.randint(0, 3)
            }
            
            enrollment = {
                'class_id': random.choice(class_ids),
                'student_id': random.choice(student_ids),
                'enrollment_date': datetime.now() - timedelta(days=random.randint(1, 365)),
                'status': random.choice(statuses),
                'performance_data': json.dumps(performance_data),
                'attendance_record': json.dumps(attendance_record),
                'notes': f'Student enrollment notes for class {i+1}',
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now(),
                'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'archived_at': None,
                'deleted_at': None,
                'scheduled_deletion_at': None,
                'retention_period': random.randint(30, 365)
            }
            enrollments.append(enrollment)
        
        # Insert enrollments
        session.execute(text("""
            INSERT INTO educational_class_students (class_id, student_id, enrollment_date, status,
                                                  performance_data, attendance_record, notes,
                                                  created_at, updated_at, last_accessed_at,
                                                  archived_at, deleted_at, scheduled_deletion_at, retention_period)
            VALUES (:class_id, :student_id, :enrollment_date, :status, :performance_data, 
                    :attendance_record, :notes, :created_at, :updated_at, :last_accessed_at,
                    :archived_at, :deleted_at, :scheduled_deletion_at, :retention_period)
        """), enrollments)
        
        session.commit()
        return len(enrollments)
        
    except Exception as e:
        print(f"  ❌ Error seeding educational_class_students: {e}")
        return 0

def seed_educational_teachers(session: Session) -> int:
    """Migrate existing users to educational teachers table"""
    try:
        print(f"  🔍 Checking educational_teachers table...")
        # Check if table exists and has data
        result = session.execute(text("SELECT COUNT(*) FROM educational_teachers"))
        existing_count = result.scalar()
        print(f"  📊 Found {existing_count} existing records in educational_teachers table")
        
        # Additive approach - work with existing data
        if existing_count > 0:
            print(f"  📊 educational_teachers already has {existing_count} records, continuing with migration...")
            # Continue with migration instead of skipping
        
        print(f"  🔍 Querying users table...")
        # Get user data from users table (not dashboard_users)
        user_result = session.execute(text("""
            SELECT id, first_name, last_name, email 
            FROM users 
            ORDER BY id 
            LIMIT 32
        """))
        users = user_result.fetchall()
        print(f"  📊 Found {len(users)} users in users table")
        
        if not users:
            print("  ⚠️  No users found, skipping educational teachers...")
            return 0
        
        print(f"  🔄 Migrating {len(users)} users to educational teachers...")
        
        # Migrate users to educational teachers
        teachers = []
        for i, user in enumerate(users):
            teachers.append({
                'user_id': user[0],
                'name': f"{user[1]} {user[2]}" if user[1] and user[2] else f"Teacher {i + 1}",
                'school': random.choice(['Lincoln Elementary', 'Roosevelt Middle', 'Kennedy High', 'Washington Elementary', 'Jefferson Middle']),
                'department': random.choice(['Mathematics', 'Science', 'English', 'History', 'Physical Education']),
                'subjects': json.dumps([random.choice(['Math', 'Science', 'English', 'History', 'PE'])]),
                'grade_levels': json.dumps([random.choice(['K-5', '6-8', '9-12'])]),
                'certifications': json.dumps([random.choice(['Teaching License', 'Subject Certification', 'Special Education'])]),
                'specialties': json.dumps([random.choice(['Gifted Education', 'Special Needs', 'ESL', 'STEM'])]),
                'bio': f"Experienced educator with {random.randint(1, 20)} years of teaching experience",
                'last_login': datetime.now() - timedelta(days=random.randint(1, 30)),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 7)),
                'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 7)),
                'archived_at': None,
                'deleted_at': None,
                'scheduled_deletion_at': None,
                'retention_period': 365,
                'status': 'ACTIVE',
                'is_active': True
            })
        
        # Use upsert logic to handle existing records
        migrated_count = 0
        for teacher in teachers:
            # Check if teacher already exists
            existing_result = session.execute(text("""
                SELECT id FROM educational_teachers WHERE user_id = :user_id
            """), {'user_id': teacher['user_id']})
            existing_teacher = existing_result.fetchone()
            
            if existing_teacher:
                # Update existing teacher
                session.execute(text("""
                    UPDATE educational_teachers SET
                        name = :name,
                        school = :school,
                        department = :department,
                        subjects = :subjects,
                        grade_levels = :grade_levels,
                        certifications = :certifications,
                        specialties = :specialties,
                        bio = :bio,
                        last_login = :last_login,
                        updated_at = :updated_at,
                        last_accessed_at = :last_accessed_at,
                        retention_period = :retention_period,
                        status = :status,
                        is_active = :is_active
                    WHERE user_id = :user_id
                """), teacher)
            else:
                # Insert new teacher
                session.execute(text("""
                    INSERT INTO educational_teachers (user_id, name, school, department, subjects, grade_levels, 
                                                   certifications, specialties, bio, last_login, created_at, updated_at,
                                                   last_accessed_at, archived_at, deleted_at, scheduled_deletion_at,
                                                   retention_period, status, is_active)
                    VALUES (:user_id, :name, :school, :department, :subjects, :grade_levels, 
                           :certifications, :specialties, :bio, :last_login, :created_at, :updated_at,
                           :last_accessed_at, :archived_at, :deleted_at, :scheduled_deletion_at,
                           :retention_period, :status, :is_active)
                """), teacher)
            migrated_count += 1
        
        session.commit()
        print(f"  ✅ Migrated {migrated_count} educational teachers (updated existing + inserted new)")
        return migrated_count
        
    except Exception as e:
        print(f"  ❌ Error migrating educational_teachers: {e}")
        import traceback
        traceback.print_exc()
        session.rollback()
        return 0

def seed_educational_teacher_availability(session: Session) -> int:
    """Seed educational teacher availability table"""
    try:
        # Check if table exists and has data
        result = session.execute(text("SELECT COUNT(*) FROM educational_teacher_availability"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  ⚠️  educational_teacher_availability already has {existing_count} records, skipping...")
            return existing_count
        
        # Get actual teacher IDs from the database
        teacher_result = session.execute(text("SELECT id FROM educational_teachers ORDER BY id"))
        teacher_ids = [row[0] for row in teacher_result.fetchall()]
        
        if not teacher_ids:
            print("  ⚠️  No teachers found, skipping educational teacher availability...")
            return 0
        
        # Create sample educational teacher availability records
        availability_records = []
        days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        for i in range(100):
            availability = {
                'teacher_id': random.choice(teacher_ids),
                'day_of_week': random.choice(days_of_week),
                'start_time': datetime.now() + timedelta(hours=random.randint(8, 17)),
                'end_time': datetime.now() + timedelta(hours=random.randint(18, 22)),
                'is_available': random.choice([True, False]),
                'notes': f"Educational availability notes for teacher {i+1}",
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now(),
                'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'archived_at': None,
                'deleted_at': None,
                'scheduled_deletion_at': None,
                'retention_period': random.randint(30, 365)
            }
            availability_records.append(availability)
        
        # Insert availability records
        session.execute(text("""
            INSERT INTO educational_teacher_availability (teacher_id, day_of_week, start_time, end_time,
                                                        is_available, notes, created_at, updated_at,
                                                        last_accessed_at, archived_at, deleted_at,
                                                        scheduled_deletion_at, retention_period)
            VALUES (:teacher_id, :day_of_week, :start_time, :end_time, :is_available, :notes,
                    :created_at, :updated_at, :last_accessed_at, :archived_at, :deleted_at,
                    :scheduled_deletion_at, :retention_period)
        """), availability_records)
        
        session.commit()
        return len(availability_records)
        
    except Exception as e:
        print(f"  ❌ Error seeding educational_teacher_availability: {e}")
        return 0

def seed_educational_teacher_certifications(session: Session) -> int:
    """Seed educational teacher certifications table"""
    try:
        # Check if table exists and has data
        result = session.execute(text("SELECT COUNT(*) FROM educational_teacher_certifications"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  ⚠️  educational_teacher_certifications already has {existing_count} records, skipping...")
            return existing_count
        
        # Get actual teacher IDs from the database
        teacher_result = session.execute(text("SELECT id FROM educational_teachers ORDER BY id"))
        teacher_ids = [row[0] for row in teacher_result.fetchall()]
        
        if not teacher_ids:
            print("  ⚠️  No teachers found, skipping educational teacher certifications...")
            return 0
        
        # Create sample educational teacher certifications
        certifications = []
        cert_names = ['Teaching License', 'PE Certification', 'Health Certification', 'First Aid', 'CPR', 'Sports Medicine', 'Nutrition Certification']
        organizations = ['State Education Board', 'American Red Cross', 'National Board of Education', 'Sports Medicine Institute', 'Health Education Council']
        
        for i in range(80):
            certification = {
                'teacher_id': random.choice(teacher_ids),
                'certification_name': random.choice(cert_names),
                'issuing_organization': random.choice(organizations),
                'issue_date': datetime.now() - timedelta(days=random.randint(1, 1825)),  # Up to 5 years ago
                'expiry_date': datetime.now() + timedelta(days=random.randint(1, 1825)),  # Up to 5 years in future
                'certification_number': f"EDU-CERT-{random.randint(10000, 99999)}",
                'verification_url': f"https://verify.education.gov/cert/{random.randint(100000, 999999)}",
                'notes': f"Certification notes for teacher {i+1}",
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now(),
                'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'archived_at': None,
                'deleted_at': None,
                'scheduled_deletion_at': None,
                'retention_period': random.randint(30, 365)
            }
            certifications.append(certification)
        
        # Insert certifications
        session.execute(text("""
            INSERT INTO educational_teacher_certifications (teacher_id, certification_name, issuing_organization,
                                                          issue_date, expiry_date, certification_number, verification_url,
                                                          notes, created_at, updated_at, last_accessed_at,
                                                          archived_at, deleted_at, scheduled_deletion_at, retention_period)
            VALUES (:teacher_id, :certification_name, :issuing_organization, :issue_date, :expiry_date,
                    :certification_number, :verification_url, :notes, :created_at, :updated_at, :last_accessed_at,
                    :archived_at, :deleted_at, :scheduled_deletion_at, :retention_period)
        """), certifications)
        
        session.commit()
        return len(certifications)
        
    except Exception as e:
        print(f"  ❌ Error seeding educational_teacher_certifications: {e}")
        return 0

def seed_class_attendance(session: Session) -> int:
    """Seed class attendance table"""
    try:
        # Check if table exists and has data
        result = session.execute(text("SELECT COUNT(*) FROM class_attendance"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  ⚠️  class_attendance already has {existing_count} records, skipping...")
            return existing_count
        
        # Get actual class IDs and student IDs from the database
        class_result = session.execute(text("SELECT id FROM educational_classes ORDER BY id"))
        class_ids = [row[0] for row in class_result.fetchall()]
        
        # Get actual student IDs from the database - try multiple sources for flexibility
        student_ids = []
        possible_student_tables = ['students', 'dashboard_users', 'users']
        
        for table_name in possible_student_tables:
            try:
                student_result = session.execute(text(f"SELECT id FROM {table_name} ORDER BY id"))
                student_ids = [row[0] for row in student_result.fetchall()]
                if student_ids:
                    print(f"  📋 Found {len(student_ids)} student records in {table_name}")
                    break
            except Exception as e:
                continue
        
        if not student_ids:
            print("  ⚠️  No students found in any table, creating fallback student IDs...")
            student_ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]  # Fallback IDs for development
        
        if not class_ids:
            print("  ⚠️  No classes found, skipping class attendance...")
            return 0
        
        # Create realistic class attendance records
        attendance_records = []
        
        # Calculate realistic number of attendance records
        # Each student should have multiple attendance records per class
        # Use: (students * classes * 2) for multiple attendance records per student per class
        num_attendance = min(len(student_ids) * len(class_ids) * 2, 10000)  # Cap at 10k for performance
        print(f"  📝 Creating {num_attendance} attendance records for {len(student_ids)} students across {len(class_ids)} classes...")
        
        for i in range(num_attendance):
            attendance = {
                'class_id': random.choice(class_ids),
                'student_id': random.choice(student_ids),
                'date': datetime.now() - timedelta(days=random.randint(1, 30)),
                'present': random.choice([True, False]),
                'notes': f"Attendance notes for record {i+1}",
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now(),
                'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'archived_at': None,
                'deleted_at': None,
                'scheduled_deletion_at': None,
                'retention_period': random.randint(30, 365)
            }
            attendance_records.append(attendance)
        
        # Insert attendance records
        session.execute(text("""
            INSERT INTO class_attendance (class_id, student_id, date, present, notes,
                                        created_at, updated_at, last_accessed_at,
                                        archived_at, deleted_at, scheduled_deletion_at, retention_period)
            VALUES (:class_id, :student_id, :date, :present, :notes, :created_at, :updated_at,
                    :last_accessed_at, :archived_at, :deleted_at, :scheduled_deletion_at, :retention_period)
        """), attendance_records)
        
        session.commit()
        return len(attendance_records)
        
    except Exception as e:
        print(f"  ❌ Error seeding class_attendance: {e}")
        return 0

def seed_class_plans(session: Session) -> int:
    """Seed class plans table"""
    try:
        # Check if table exists and has data
        result = session.execute(text("SELECT COUNT(*) FROM class_plans"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  ⚠️  class_plans already has {existing_count} records, skipping...")
            return existing_count
        
        # Get actual class IDs and plan IDs from the database
        class_result = session.execute(text("SELECT id FROM physical_education_classes ORDER BY id"))
        class_ids = [row[0] for row in class_result.fetchall()]

        plan_result = session.execute(text("SELECT id FROM activity_plans ORDER BY id"))
        plan_ids = [row[0] for row in plan_result.fetchall()]
        
        if not class_ids or not plan_ids:
            print("  ⚠️  No classes or plans found, skipping class plans...")
            return 0
        
        # Create sample class plans
        plans = []
        statuses = ['PLANNED', 'ACTIVE', 'COMPLETED', 'CANCELLED', 'ON_HOLD']
        
        for i in range(150):
            plan = {
                'class_id': random.choice(class_ids),
                'plan_id': random.choice(plan_ids),
                'scheduled_date': datetime.now() + timedelta(days=random.randint(1, 365)),
                'status': random.choice(statuses),
                'class_plan_metadata': json.dumps({
                    'title': f"Class Plan {i+1}",
                    'description': f"Description for class plan {i+1}",
                    'plan_type': random.choice(['Daily', 'Weekly', 'Monthly', 'Unit', 'Semester']),
                    'is_active': random.choice([True, False])
                }),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now(),
                'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'archived_at': None,
                'deleted_at': None,
                'scheduled_deletion_at': None,
                'retention_period': random.randint(30, 365)
            }
            plans.append(plan)
        
        # Insert plans
        session.execute(text("""
            INSERT INTO class_plans (class_id, plan_id, scheduled_date, status, class_plan_metadata,
                                   created_at, updated_at, last_accessed_at, archived_at,
                                   deleted_at, scheduled_deletion_at, retention_period)
            VALUES (:class_id, :plan_id, :scheduled_date, :status, :class_plan_metadata,
                    :created_at, :updated_at, :last_accessed_at, :archived_at,
                    :deleted_at, :scheduled_deletion_at, :retention_period)
        """), plans)
        
        session.commit()
        return len(plans)
        
    except Exception as e:
        print(f"  ❌ Error seeding class_plans: {e}")
        return 0

def seed_class_schedules(session: Session) -> int:
    """Seed class schedules table"""
    try:
        # Check if table exists and has data
        result = session.execute(text("SELECT COUNT(*) FROM class_schedules"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  ⚠️  class_schedules already has {existing_count} records, skipping...")
            return existing_count
        
        # Get actual class IDs from the database
        class_result = session.execute(text("SELECT id FROM educational_classes ORDER BY id"))
        class_ids = [row[0] for row in class_result.fetchall()]
        
        if not class_ids:
            print("  ⚠️  No classes found, skipping class schedules...")
            return 0
        
        # Create sample class schedules
        schedules = []
        days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        for i in range(200):
            schedule = {
                'class_id': random.choice(class_ids),
                'day_of_week': random.choice(days_of_week),
                'start_time': datetime.now() + timedelta(hours=random.randint(7, 17)),  # 7 AM to 5 PM
                'end_time': datetime.now() + timedelta(hours=random.randint(8, 18)),   # 8 AM to 6 PM
                'location': f"Room {random.randint(100, 999)}",
                'recurring': random.choice([True, False]),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now(),
                'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'archived_at': None,
                'deleted_at': None,
                'scheduled_deletion_at': None,
                'retention_period': random.randint(30, 365)
            }
            schedules.append(schedule)
        
        # Insert schedules
        session.execute(text("""
            INSERT INTO class_schedules (class_id, day_of_week, start_time, end_time, location,
                                       recurring, created_at, updated_at, last_accessed_at,
                                       archived_at, deleted_at, scheduled_deletion_at, retention_period)
            VALUES (:class_id, :day_of_week, :start_time, :end_time, :location, :recurring,
                    :created_at, :updated_at, :last_accessed_at, :archived_at, :deleted_at,
                    :scheduled_deletion_at, :retention_period)
        """), schedules)
        
        session.commit()
        return len(schedules)
        
    except Exception as e:
        print(f"  ❌ Error seeding class_schedules: {e}")
        return 0

# ============================================================================
# SECTION 2.3: DEPARTMENT & ORGANIZATION SEEDING FUNCTIONS
# ============================================================================

def seed_departments(session: Session) -> int:
    """Seed departments table"""
    try:
        # Check if table exists and has data
        result = session.execute(text("SELECT COUNT(*) FROM departments"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  🔄 departments already has {existing_count} records, continuing with migration...")
            # Continue with seeding - let ON CONFLICT clauses handle duplicates
        
        # Create sample departments
        departments = []
        statuses = ['ACTIVE', 'INACTIVE', 'PENDING', 'SCHEDULED', 'COMPLETED', 'CANCELLED', 'ON_HOLD']
        
        for i in range(8):
            department = {
                'organization_id': 1,  # Use the only existing organization
                'name': f"Department {i+1}",
                'description': f"Description for department {i+1}",
                'settings': json.dumps({
                    'department_type': random.choice(['Academic', 'Administrative', 'Support', 'Research', 'Student Services']),
                    'head_teacher_id': random.randint(1, 50),
                    'budget': random.randint(10000, 100000),
                    'location': f"Building {random.randint(1, 5)}"
                }),
                'status': random.choice(statuses),
                'is_active': random.choice([True, False]),
                'metadata': json.dumps({
                    'founded_date': (datetime.now() - timedelta(days=random.randint(365, 3650))).isoformat(),
                    'contact_email': f"dept{i+1}@school.edu",
                    'phone': f"555-{random.randint(1000, 9999)}"
                }),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now(),
                'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'archived_at': None,
                'deleted_at': None,
                'scheduled_deletion_at': None,
                'retention_period': random.randint(30, 365)
            }
            departments.append(department)
        
        # Insert departments
        session.execute(text("""
            INSERT INTO departments (organization_id, name, description, settings, status, is_active,
                                   metadata, created_at, updated_at, last_accessed_at, archived_at,
                                   deleted_at, scheduled_deletion_at, retention_period)
            VALUES (:organization_id, :name, :description, :settings, :status, :is_active,
                    :metadata, :created_at, :updated_at, :last_accessed_at, :archived_at,
                    :deleted_at, :scheduled_deletion_at, :retention_period)
        """), departments)
        
        session.commit()
        return len(departments)
        
    except Exception as e:
        print(f"  ❌ Error seeding departments: {e}")
        return 0

def seed_department_members(session: Session) -> int:
    """Seed department members table"""
    try:
        # Check if table exists and has data
        result = session.execute(text("SELECT COUNT(*) FROM department_members"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  ⚠️  department_members already has {existing_count} records, skipping...")
            return existing_count
        
        # Create sample department members
        members = []
        member_roles = ['Member', 'Senior Member', 'Lead', 'Coordinator']
        statuses = ['ACTIVE', 'INACTIVE', 'PENDING', 'SCHEDULED', 'COMPLETED', 'CANCELLED', 'ON_HOLD']
        
        # Get actual department IDs and user IDs from database
        result = session.execute(text("SELECT id FROM departments"))
        department_ids = [row[0] for row in result.fetchall()]
        
        result = session.execute(text("SELECT id FROM dashboard_users"))
        user_ids = [row[0] for row in result.fetchall()]
        
        for i in range(40):
            member = {
                'department_id': random.choice(department_ids),   # Use actual department IDs
                'user_id': random.choice(user_ids),               # Use actual user IDs
                'role': random.choice(member_roles),
                'permissions': json.dumps({
                    'can_edit': random.choice([True, False]),
                    'can_delete': random.choice([True, False]),
                    'can_manage_members': random.choice([True, False]),
                    'access_level': random.choice(['read', 'write', 'admin'])
                }),
                'status': random.choice(statuses),
                'is_active': random.choice([True, False]),
                'metadata': json.dumps({
                    'join_date': (datetime.now() - timedelta(days=random.randint(1, 1825))).isoformat(),
                    'notes': f'Department member {i+1}',
                    'department_notes': f'Notes for member {i+1}'
                }),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now(),
                'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'archived_at': None,
                'deleted_at': None,
                'scheduled_deletion_at': None,
                'retention_period': random.randint(30, 365)
            }
            members.append(member)
        
        # Insert members
        session.execute(text("""
            INSERT INTO department_members (department_id, user_id, role, permissions, status, is_active,
                                          metadata, created_at, updated_at, last_accessed_at, archived_at,
                                          deleted_at, scheduled_deletion_at, retention_period)
            VALUES (:department_id, :user_id, :role, :permissions, :status, :is_active,
                    :metadata, :created_at, :updated_at, :last_accessed_at, :archived_at,
                    :deleted_at, :scheduled_deletion_at, :retention_period)
        """), members)
        
        session.commit()
        return len(members)
        
    except Exception as e:
        print(f"  ❌ Error seeding department_members: {e}")
        return 0

def seed_organization_roles(session: Session) -> int:
    """Seed organization roles table"""
    try:
        # Check if table exists and has data
        result = session.execute(text("SELECT COUNT(*) FROM organization_roles"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  ⚠️  organization_roles already has {existing_count} records, skipping...")
            return existing_count
        
        # Create sample organization roles
        roles = []
        statuses = ['ACTIVE', 'INACTIVE', 'PENDING', 'SCHEDULED', 'COMPLETED', 'CANCELLED', 'ON_HOLD']
        
        for i in range(15):
            role = {
                'organization_id': 1,  # Use the only existing organization
                'name': f"Role {i+1}",
                'description': f"Description for role {i+1}",
                'permissions': json.dumps({
                    'can_manage_users': random.choice([True, False]),
                    'can_manage_roles': random.choice([True, False]),
                    'can_view_reports': random.choice([True, False]),
                    'can_edit_settings': random.choice([True, False]),
                    'access_level': random.choice(['read', 'write', 'admin'])
                }),
                'is_system_role': random.choice([True, False]),
                'settings': json.dumps({
                    'role_type': random.choice(['Administrative', 'Academic', 'Support', 'Leadership', 'Staff']),
                    'priority': random.randint(1, 10),
                    'department_access': random.choice(['all', 'specific', 'none'])
                }),
                'status': random.choice(statuses),
                'is_active': random.choice([True, False]),
                'metadata': json.dumps({
                    'created_by': f"admin_{i+1}",
                    'notes': f'Organization role {i+1}',
                    'last_modified': (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat()
                }),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now(),
                'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'archived_at': None,
                'deleted_at': None,
                'scheduled_deletion_at': None,
                'retention_period': random.randint(30, 365)
            }
            roles.append(role)
        
        # Insert roles
        session.execute(text("""
            INSERT INTO organization_roles (organization_id, name, description, permissions, is_system_role,
                                          settings, status, is_active, metadata, created_at, updated_at,
                                          last_accessed_at, archived_at, deleted_at, scheduled_deletion_at, retention_period)
            VALUES (:organization_id, :name, :description, :permissions, :is_system_role,
                    :settings, :status, :is_active, :metadata, :created_at, :updated_at,
                    :last_accessed_at, :archived_at, :deleted_at, :scheduled_deletion_at, :retention_period)
        """), roles)
        
        session.commit()
        return len(roles)
        
    except Exception as e:
        print(f"  ❌ Error seeding organization_roles: {e}")
        return 0

def seed_organization_members(session: Session) -> int:
    """Seed organization members table"""
    try:
        # Check if table exists and has data
        result = session.execute(text("SELECT COUNT(*) FROM organization_members"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  ⚠️  organization_members already has {existing_count} records, skipping...")
            return existing_count
        
        # Get actual organization_ids and user_ids from database
        org_result = session.execute(text("SELECT id FROM organizations LIMIT 5"))
        organization_ids = [row[0] for row in org_result.fetchall()]
        
        user_result = session.execute(text("SELECT id FROM dashboard_users "))
        user_ids = [row[0] for row in user_result.fetchall()]
        
        role_result = session.execute(text("SELECT id FROM organization_roles LIMIT 15"))
        role_ids = [row[0] for row in role_result.fetchall()]
        
        if not organization_ids or not user_ids or not role_ids:
            print("  ⚠️  No organizations, users, or roles found, skipping organization_members...")
            return 0
        
        # Create sample organization members
        members = []
        statuses = ['ACTIVE', 'INACTIVE', 'PENDING', 'SCHEDULED', 'COMPLETED', 'CANCELLED', 'ON_HOLD']
        
        for i in range(60):
            member = {
                'organization_id': random.choice(organization_ids),
                'user_id': random.choice(user_ids),
                'role_id': random.choice(role_ids),
                'permissions': json.dumps({
                    'can_read': random.choice([True, False]),
                    'can_write': random.choice([True, False]),
                    'can_delete': random.choice([True, False])
                }),
                'status': random.choice(statuses),
                'is_active': random.choice([True, False]),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now(),
                'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'archived_at': None,
                'deleted_at': None,
                'scheduled_deletion_at': None,
                'retention_period': random.randint(30, 365),
                'metadata': json.dumps({
                    'department': f'Department {random.randint(1, 10)}',
                    'notes': f'Member notes {i+1}'
                })
            }
            members.append(member)
        
        # Insert members
        session.execute(text("""
            INSERT INTO organization_members (organization_id, user_id, role_id, permissions, status, is_active,
                                            created_at, updated_at, last_accessed_at, archived_at, deleted_at,
                                            scheduled_deletion_at, retention_period, metadata)
            VALUES (:organization_id, :user_id, :role_id, :permissions, :status, :is_active,
                    :created_at, :updated_at, :last_accessed_at, :archived_at, :deleted_at,
                    :scheduled_deletion_at, :retention_period, :metadata)
        """), members)
        
        session.commit()
        return len(members)
        
    except Exception as e:
        print(f"  ❌ Error seeding organization_members: {e}")
        return 0

def seed_organization_collaborations(session: Session) -> int:
    """Seed organization collaborations table"""
    try:
        # Check if table exists and has data
        result = session.execute(text("SELECT COUNT(*) FROM organization_collaborations"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  ⚠️  organization_collaborations already has {existing_count} records, skipping...")
            return existing_count
        
        # Get actual organization_ids from database
        org_result = session.execute(text("SELECT id FROM organizations LIMIT 5"))
        organization_ids = [row[0] for row in org_result.fetchall()]
        
        if not organization_ids:
            print("  ⚠️  No organizations found, skipping organization_collaborations...")
            return 0
        
        # Create sample organization collaborations
        collaborations = []
        collaboration_types = ['Partnership', 'Joint Project', 'Resource Sharing', 'Training', 'Research', 'Development']
        statuses = ['ACTIVE', 'INACTIVE', 'PENDING', 'SCHEDULED', 'COMPLETED', 'CANCELLED', 'ON_HOLD']
        
        for i in range(25):
            collaboration = {
                'source_org_id': random.choice(organization_ids),
                'target_org_id': random.choice(organization_ids),
                'type': random.choice(collaboration_types),
                'settings': json.dumps({
                    'duration_months': random.randint(1, 24),
                    'budget': random.randint(1000, 100000),
                    'priority': random.choice(['High', 'Medium', 'Low'])
                }),
                'status': random.choice(statuses),
                'is_active': random.choice([True, False]),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now(),
                'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'archived_at': None,
                'deleted_at': None,
                'scheduled_deletion_at': None,
                'retention_period': random.randint(30, 365),
                'metadata': json.dumps({
                    'description': f"Collaboration description {i+1}",
                    'contact_person': f"Contact {i+1}",
                    'notes': f"Collaboration notes {i+1}"
                })
            }
            collaborations.append(collaboration)
        
        # Insert collaborations
        session.execute(text("""
            INSERT INTO organization_collaborations (source_org_id, target_org_id, type, settings, status, is_active,
                                                  created_at, updated_at, last_accessed_at, archived_at, deleted_at,
                                                  scheduled_deletion_at, retention_period, metadata)
            VALUES (:source_org_id, :target_org_id, :type, :settings, :status, :is_active,
                    :created_at, :updated_at, :last_accessed_at, :archived_at, :deleted_at,
                    :scheduled_deletion_at, :retention_period, :metadata)
        """), collaborations)
        
        session.commit()
        return len(collaborations)
        
    except Exception as e:
        print(f"  ❌ Error seeding organization_collaborations: {e}")
        return 0

def seed_organization_projects(session: Session) -> int:
    """Seed organization projects table"""
    try:
        # Check if table exists and has data
        result = session.execute(text("SELECT COUNT(*) FROM organization_projects"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  🔄 organization_projects already has {existing_count} records, continuing with migration...")
            # Continue with seeding - let ON CONFLICT clauses handle duplicates
        
        # Get actual user_ids and team_ids from database
        user_result = session.execute(text("SELECT id FROM dashboard_users LIMIT 50"))
        user_ids = [row[0] for row in user_result.fetchall()]
        
        team_result = session.execute(text("SELECT id FROM teams ORDER BY id"))
        team_ids = [row[0] for row in team_result.fetchall()]
        
        if not user_ids:
            print("  ⚠️  No users found, skipping organization_projects...")
            return 0
        
        # Create sample organization projects
        projects = []
        statuses = ['ACTIVE', 'INACTIVE', 'PENDING', 'SCHEDULED', 'COMPLETED', 'CANCELLED', 'ON_HOLD']
        
        for i in range(20):
            project = {
                'name': f"Project {i+1}",
                'description': f"Description for project {i+1}",
                'active_gpt_id': f"gpt-{random.randint(1000, 9999)}" if random.choice([True, False]) else None,
                'configuration': json.dumps({
                    'project_type': random.choice(['Research', 'Development', 'Implementation', 'Training', 'Assessment']),
                    'budget': random.randint(1000, 100000),
                    'priority': random.choice(['High', 'Medium', 'Low']),
                    'team_size': random.randint(2, 20)
                }),
                'is_template': random.choice([True, False]),
                'user_id': random.choice(user_ids),
                'team_id': random.choice(team_ids) if team_ids else None,
                'status': random.choice(statuses),
                'is_active': random.choice([True, False]),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now(),
                'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'archived_at': None,
                'deleted_at': None,
                'scheduled_deletion_at': None,
                'retention_period': random.randint(30, 365),
                'metadata': json.dumps({
                    'start_date': (datetime.now() - timedelta(days=random.randint(1, 365))).isoformat(),
                    'end_date': (datetime.now() + timedelta(days=random.randint(1, 365))).isoformat(),
                    'notes': f"Project notes {i+1}"
                })
            }
            projects.append(project)
        
        # Insert projects
        session.execute(text("""
            INSERT INTO organization_projects (name, description, active_gpt_id, configuration, is_template,
                                            user_id, team_id, status, is_active, created_at, updated_at,
                                            last_accessed_at, archived_at, deleted_at, scheduled_deletion_at,
                                            retention_period, metadata)
            VALUES (:name, :description, :active_gpt_id, :configuration, :is_template,
                    :user_id, :team_id, :status, :is_active, :created_at, :updated_at,
                    :last_accessed_at, :archived_at, :deleted_at, :scheduled_deletion_at,
                    :retention_period, :metadata)
        """), projects)
        
        session.commit()
        return len(projects)
        
    except Exception as e:
        print(f"  ❌ Error seeding organization_projects: {e}")
        return 0

def seed_organization_resources(session: Session) -> int:
    """Seed organization resources table"""
    try:
        # Check if table exists and has data
        result = session.execute(text("SELECT COUNT(*) FROM organization_resources"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  ⚠️  organization_resources already has {existing_count} records, skipping...")
            return existing_count
        
        # Get actual organization_ids from database
        org_result = session.execute(text("SELECT id FROM organizations LIMIT 5"))
        organization_ids = [row[0] for row in org_result.fetchall()]
        
        if not organization_ids:
            print("  ⚠️  No organizations found, skipping organization_resources...")
            return 0
        
        # Create sample organization resources
        resources = []
        resource_types = ['Equipment', 'Software', 'Facilities', 'Materials', 'Personnel', 'Technology', 'Training']
        statuses = ['ACTIVE', 'INACTIVE', 'PENDING', 'SCHEDULED', 'COMPLETED', 'CANCELLED', 'ON_HOLD']
        
        for i in range(30):
            resource = {
                'organization_id': random.choice(organization_ids),
                'name': f"Resource {i+1}",
                'type': random.choice(resource_types),
                'settings': json.dumps({
                    'quantity': random.randint(1, 100),
                    'unit_cost': random.randint(10, 1000),
                    'location': f"Location {random.randint(1, 10)}",
                    'condition': random.choice(['New', 'Good', 'Fair', 'Poor'])
                }),
                'status': random.choice(statuses),
                'is_active': random.choice([True, False]),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now(),
                'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'archived_at': None,
                'deleted_at': None,
                'scheduled_deletion_at': None,
                'retention_period': random.randint(30, 365),
                'metadata': json.dumps({
                    'description': f"Description for resource {i+1}",
                    'notes': f"Resource notes {i+1}"
                })
            }
            resources.append(resource)
        
        # Insert resources
        session.execute(text("""
            INSERT INTO organization_resources (organization_id, name, type, settings, status, is_active,
                                             created_at, updated_at, last_accessed_at, archived_at, deleted_at,
                                             scheduled_deletion_at, retention_period, metadata)
            VALUES (:organization_id, :name, :type, :settings, :status, :is_active,
                    :created_at, :updated_at, :last_accessed_at, :archived_at, :deleted_at,
                    :scheduled_deletion_at, :retention_period, :metadata)
        """), resources)
        
        session.commit()
        
        return len(resources)
        
    except Exception as e:
        print(f"  ❌ Error seeding organization_resources: {e}")
        return 0

def seed_organization_settings(session: Session) -> int:
    """Seed organization settings table"""
    try:
        # Check if table exists and has data
        result = session.execute(text("SELECT COUNT(*) FROM organization_settings"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  🔄 organization_settings already has {existing_count} records, continuing with migration...")
            # Continue with seeding - let ON CONFLICT clauses handle duplicates
        
        # Get actual organization_ids from database
        org_result = session.execute(text("SELECT id FROM organizations LIMIT 5"))
        organization_ids = [row[0] for row in org_result.fetchall()]
        
        if not organization_ids:
            print("  ⚠️  No organizations found, skipping organization_settings...")
            return 0
        
        # Check which organizations already have settings
        existing_settings_result = session.execute(text("SELECT organization_id FROM organization_settings"))
        existing_org_ids = {row[0] for row in existing_settings_result.fetchall()}
        
        # Filter out organizations that already have settings
        new_organization_ids = [org_id for org_id in organization_ids if org_id not in existing_org_ids]
        
        if not new_organization_ids:
            print("  ✅ All organizations already have settings, skipping...")
            return len(organization_ids)
        
        # Create sample organization settings (one per organization)
        settings = []
        statuses = ['ACTIVE', 'INACTIVE', 'PENDING', 'SCHEDULED', 'COMPLETED', 'CANCELLED', 'ON_HOLD']
        
        for i, org_id in enumerate(new_organization_ids):
            setting = {
                'organization_id': org_id,
                'theme': random.choice(['light', 'dark', 'auto']),
                'language': random.choice(['en', 'es', 'fr', 'de']),
                'timezone': random.choice(['UTC', 'EST', 'PST', 'CST']),
                'features': json.dumps({
                    'feature_1': random.choice([True, False]),
                    'feature_2': random.choice([True, False]),
                    'feature_3': random.choice([True, False])
                }),
                'enabled_modules': json.dumps(['module1', 'module2', 'module3']),
                'experimental_features': json.dumps({
                    'exp_feature_1': False,
                    'exp_feature_2': True
                }),
                'integrations': json.dumps({
                    'slack': True,
                    'email': True,
                    'calendar': False
                }),
                'api_keys': json.dumps({
                    'key1': 'encrypted_key_value',
                    'key2': 'encrypted_key_value'
                }),
                'webhooks': json.dumps({
                    'webhook1': 'https://example.com/webhook1',
                    'webhook2': 'https://example.com/webhook2'
                }),
                'notification_preferences': json.dumps({
                    'email': True,
                    'sms': False,
                    'push': True
                }),
                'email_settings': json.dumps({
                    'smtp_server': 'smtp.example.com',
                    'port': 587,
                    'ssl': True
                }),
                'alert_settings': json.dumps({
                    'critical': True,
                    'warning': True,
                    'info': False
                }),
                'security_policies': json.dumps({
                    'password_policy': 'strong',
                    '2fa_required': True,
                    'session_timeout': 3600
                }),
                'access_controls': json.dumps({
                    'ip_whitelist': ['192.168.1.0/24'],
                    'time_restrictions': 'business_hours'
                }),
                'audit_settings': json.dumps({
                    'log_level': 'info',
                    'retention_days': 90
                }),
                'custom_settings': json.dumps({
                    'custom_setting_1': 'value1',
                    'custom_setting_2': 'value2'
                }),
                'status': random.choice(statuses),
                'is_active': random.choice([True, False]),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now(),
                'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'archived_at': None,
                'deleted_at': None,
                'scheduled_deletion_at': None,
                'retention_period': random.randint(30, 365),
                'metadata': json.dumps({
                    'description': f"Organization settings {i+1}",
                    'notes': f"Settings notes {i+1}"
                })
            }
            settings.append(setting)
        
        # Insert settings
        session.execute(text("""
            INSERT INTO organization_settings (organization_id, theme, language, timezone, features,
                                            enabled_modules, experimental_features, integrations, api_keys,
                                            webhooks, notification_preferences, email_settings, alert_settings,
                                            security_policies, access_controls, audit_settings, custom_settings,
                                            status, is_active, created_at, updated_at, last_accessed_at,
                                            archived_at, deleted_at, scheduled_deletion_at, retention_period, metadata)
            VALUES (:organization_id, :theme, :language, :timezone, :features, :enabled_modules,
                    :experimental_features, :integrations, :api_keys, :webhooks, :notification_preferences,
                    :email_settings, :alert_settings, :security_policies, :access_controls, :audit_settings,
                    :custom_settings, :status, :is_active, :created_at, :updated_at, :last_accessed_at,
                    :archived_at, :deleted_at, :scheduled_deletion_at, :retention_period, :metadata)
        """), settings)
        
        session.commit()
        
        return len(settings)
        
    except Exception as e:
        print(f"  ❌ Error seeding organization_settings: {e}")
        recover_transaction(session)
        return 0

def seed_organization_feedback(session: Session) -> int:
    """Seed organization feedback table"""
    try:
        # Check if table exists and has data
        result = session.execute(text("SELECT COUNT(*) FROM organization_feedback"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  ⚠️  organization_feedback already has {existing_count} records, skipping...")
            return existing_count
        
        # Get actual user_ids, project_ids, gpt_ids, and category_ids from database
        user_result = session.execute(text("SELECT id FROM dashboard_users "))
        user_ids = [row[0] for row in user_result.fetchall()]
        
        project_result = session.execute(text("SELECT id FROM feedback_projects ORDER BY id"))
        project_ids = [row[0] for row in project_result.fetchall()]
        
        gpt_result = session.execute(text("SELECT id FROM core_gpt_definitions ORDER BY id"))
        gpt_ids = [row[0] for row in gpt_result.fetchall()]
        
        category_result = session.execute(text("SELECT id FROM feedback_categories ORDER BY id"))
        category_ids = [row[0] for row in category_result.fetchall()]
        
        if not user_ids:
            print("  ⚠️  No users found, skipping organization_feedback...")
            return 0
        
        # Create sample organization feedback
        feedback_records = []
        feedback_types = ['BUG', 'FEATURE', 'IMPROVEMENT', 'QUESTION', 'COMPLAINT', 'PRAISE', 'SUGGESTION', 'OTHER']
        statuses = ['OPEN', 'IN_PROGRESS', 'RESOLVED', 'CLOSED', 'REOPENED', 'DUPLICATE', 'WONT_FIX']
        priorities = ['LOW', 'MEDIUM', 'HIGH', 'URGENT', 'CRITICAL']
        
        for i in range(40):
            feedback = {
                'user_id': random.choice(user_ids),
                'project_id': random.choice(project_ids) if project_ids and random.choice([True, False]) else None,
                'gpt_id': random.choice(gpt_ids) if gpt_ids and random.choice([True, False]) else None,
                'category_id': random.choice(category_ids) if category_ids and random.choice([True, False]) else None,
                'feedback_type': random.choice(feedback_types),
                'status': random.choice(statuses),
                'priority': random.choice(priorities),
                'title': f"Feedback {i+1}",
                'content': f"Description for feedback {i+1}",
                'rating': random.randint(1, 5) if random.choice([True, False]) else None,
                'tags': json.dumps([f'tag{i+1}', f'category{i+1}']),
                'source': random.choice(['web', 'mobile', 'api', 'email']),
                'browser_info': json.dumps({
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'browser': 'Chrome',
                    'version': '91.0.4472.124'
                }),
                'device_info': json.dumps({
                    'platform': 'Windows',
                    'device_type': 'desktop',
                    'screen_resolution': '1920x1080'
                }),
                'resolved_at': datetime.now() - timedelta(days=random.randint(1, 30)) if random.choice([True, False]) else None,
                'closed_at': datetime.now() - timedelta(days=random.randint(1, 10)) if random.choice([True, False]) else None,
                'is_active': random.choice([True, False]),
                'metadata': json.dumps({
                    'department': f'Department {random.randint(1, 10)}',
                    'notes': f'Feedback notes {i+1}'
                })
            }
            feedback_records.append(feedback)
        
        # Insert feedback
        session.execute(text("""
            INSERT INTO organization_feedback (user_id, project_id, gpt_id, category_id, feedback_type, status, priority,
                                            title, content, rating, tags, source, browser_info, device_info,
                                            resolved_at, closed_at, is_active, metadata)
            VALUES (:user_id, :project_id, :gpt_id, :category_id, :feedback_type, :status, :priority,
                    :title, :content, :rating, :tags, :source, :browser_info, :device_info,
                    :resolved_at, :closed_at, :is_active, :metadata)
        """), feedback_records)
        
        session.commit()
        
        return len(feedback_records)
        
    except Exception as e:
        print(f"  ❌ Error seeding organization_feedback: {e}")
        return 0

def seed_teams(session: Session) -> int:
    """Seed teams table"""
    try:
        # Check if table exists and has data
        result = session.execute(text("SELECT COUNT(*) FROM teams"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  ⚠️  teams already has {existing_count} records, skipping...")
            return existing_count
        
        # Create sample teams
        teams = []
        statuses = ['ACTIVE', 'INACTIVE', 'PENDING', 'SCHEDULED', 'COMPLETED', 'CANCELLED', 'ON_HOLD']
        
        for i in range(12):
            team = {
                'name': f"Team {i+1}",
                'description': f"Description for team {i+1}",
                'settings': json.dumps({
                    'max_members': random.randint(5, 20),
                    'meeting_frequency': random.choice(['weekly', 'bi-weekly', 'monthly']),
                    'communication_channel': random.choice(['slack', 'email', 'teams'])
                }),
                'is_active': random.choice([True, False]),
                'status': random.choice(statuses),
                'metadata': json.dumps({
                    'department': f'Department {random.randint(1, 10)}',
                    'notes': f'Team notes {i+1}'
                })
            }
            teams.append(team)
        
        # Insert teams
        session.execute(text("""
            INSERT INTO teams (name, description, settings, is_active, status, metadata)
            VALUES (:name, :description, :settings, :is_active, :status, :metadata)
        """), teams)
        
        session.commit()
        
        return len(teams)
        
    except Exception as e:
        print(f"  ❌ Error seeding teams: {e}")
        return 0

def seed_team_members(session: Session) -> int:
    """Seed team members table"""
    try:
        # Check if table exists and has data
        result = session.execute(text("SELECT COUNT(*) FROM team_members"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  ⚠️  team_members already has {existing_count} records, skipping...")
            return existing_count
        
        # Get actual team_ids and user_ids from database
        team_result = session.execute(text("SELECT id FROM teams LIMIT 12"))
        team_ids = [row[0] for row in team_result.fetchall()]
        
        user_result = session.execute(text("SELECT id FROM dashboard_users "))
        user_ids = [row[0] for row in user_result.fetchall()]
        
        if not team_ids or not user_ids:
            print("  ⚠️  No teams or users found, skipping team_members...")
            return 0
        
        # Create sample team members
        members = []
        member_roles = ['Member', 'Senior Member', 'Lead', 'Coordinator', 'Contributor', 'Manager', 'Admin']
        statuses = ['ACTIVE', 'INACTIVE', 'PENDING', 'SCHEDULED', 'COMPLETED', 'CANCELLED', 'ON_HOLD']
        
        for i in range(60):
            member = {
                'team_id': random.choice(team_ids),
                'user_id': random.choice(user_ids),
                'role': random.choice(member_roles),
                'permissions': json.dumps({
                    'can_read': random.choice([True, False]),
                    'can_write': random.choice([True, False]),
                    'can_delete': random.choice([True, False]),
                    'can_manage': random.choice([True, False])
                }),
                'joined_at': datetime.now() - timedelta(days=random.randint(1, 1825)),  # Up to 5 years ago
                'last_active': datetime.now() - timedelta(days=random.randint(1, 30)),
                'status': random.choice(statuses),
                'is_active': random.choice([True, False]),
                'metadata': json.dumps({
                    'department': f'Department {random.randint(1, 10)}',
                    'notes': f'Member notes {i+1}'
                })
            }
            members.append(member)
        
        # Insert members
        session.execute(text("""
            INSERT INTO team_members (team_id, user_id, role, permissions, joined_at, last_active, 
                                     status, is_active, metadata)
            VALUES (:team_id, :user_id, :role, :permissions, :joined_at, :last_active, 
                    :status, :is_active, :metadata)
        """), members)
        
        session.commit()
        
        return len(members)
        
    except Exception as e:
        print(f"  ❌ Error seeding team_members: {e}")
        return 0

# ============================================================================
# MAIN SEEDING FUNCTION
# ============================================================================

def recover_transaction(session):
    """Recover from failed transaction by rolling back and starting fresh"""
    try:
        session.rollback()
        print("  🔄 Transaction rolled back, continuing...")
        return True
    except Exception as e:
        print(f"  ❌ Failed to rollback transaction: {e}")
        return False

def seed_phase2_educational_system(session: Session) -> Dict[str, int]:
    """
    Seed Phase 2: Educational System Enhancement
    Returns a dictionary with counts of records created for each table
    """
    print("\n" + "="*60)
    print("🚀 PHASE 2: EDUCATIONAL SYSTEM ENHANCEMENT")
    print("="*60)
    print("📚 Seeding 38 tables for advanced educational features")
    print("👨‍🏫 Teacher & class management")
    print("🏢 Department & organization structure")
    print("="*60)
    
    results = {}
    
    try:
        # Section 2.1: Advanced Educational Features (12 tables)
        print("\n📚 SECTION 2.1: ADVANCED EDUCATIONAL FEATURES")
        print("-" * 50)
        
        # Seed physical education teachers first (needed for foreign keys)
        print("Seeding physical education teachers...")
        results['physical_education_teachers'] = seed_physical_education_teachers(session)
        
        # Seed physical education classes (needed for foreign keys)
        print("Seeding physical education classes...")
        results['physical_education_classes'] = seed_physical_education_classes(session)
        
        # Seed activity plans (needed for foreign keys)
        print("Seeding activity plans...")
        results['activity_plans'] = seed_activity_plans(session)
        
        # Seed activity plans planning
        print("Seeding activity plans planning...")
        results['activity_plans_planning'] = seed_activity_plans_planning(session)
        
        # Seed PE lesson plans
        print("Seeding PE lesson plans...")
        pe_lesson_plans_count = seed_pe_lesson_plans(session)
        results['pe_lesson_plans'] = pe_lesson_plans_count
        print(f"✅ Created {pe_lesson_plans_count} PE lesson plans")
        
        # Seed lesson plan activities
        print("Seeding lesson plan activities...")
        lesson_plan_activities_count = seed_lesson_plan_activities(session)
        results['lesson_plan_activities'] = lesson_plan_activities_count
        print(f"✅ Created {lesson_plan_activities_count} lesson plan activities")
        
        # Seed lesson plan objectives
        print("Seeding lesson plan objectives...")
        lesson_plan_objectives_count = seed_lesson_plan_objectives(session)
        results['lesson_plan_objectives'] = lesson_plan_objectives_count
        print(f"✅ Created {lesson_plan_objectives_count} lesson plan objectives")
        
        # Seed curriculum FIRST (needed for lessons and standards)
        print("Seeding curriculum...")
        curriculum_count = seed_curriculum(session)
        results['curriculum'] = curriculum_count
        print(f"✅ Created {curriculum_count} curriculum records")
        
        # Commit curriculum to ensure it persists for dependent tables
        session.commit()
        print("🔒 Curriculum data committed - ensuring persistence for dependent tables")
        
        # Seed curriculum lessons
        print("Seeding curriculum lessons...")
        curriculum_lessons_count = seed_curriculum_lessons(session)
        results['curriculum_lessons'] = curriculum_lessons_count
        print(f"✅ Created {curriculum_lessons_count} curriculum lessons")
        
        # Seed curriculum standards
        print("Seeding curriculum standards...")
        curriculum_standards_count = seed_curriculum_standards(session)
        results['curriculum_standards'] = curriculum_standards_count
        print(f"✅ Created {curriculum_standards_count} curriculum standards")
        
        # Seed curriculum standard associations
        print("Seeding curriculum standard associations...")
        print("🔍 About to call seed_curriculum_standard_associations...")
        standard_associations_count = seed_curriculum_standard_associations(session)
        print(f"🔍 seed_curriculum_standard_associations returned: {standard_associations_count}")
        results['curriculum_standard_association'] = standard_associations_count
        print(f"✅ Created {standard_associations_count} standard associations")
        
        # Seed courses
        print("Seeding courses...")
        print("🔍 About to call seed_courses...")
        courses_count = seed_courses(session)
        print(f"🔍 seed_courses returned: {courses_count}")
        results['courses'] = courses_count
        print(f"✅ Created {courses_count} courses")
        
        # Commit courses to protect from rollbacks
        session.commit()
        print("🔒 Courses committed - protecting from rollbacks")
        
        # Seed course enrollments
        print("Seeding course enrollments...")
        print("🔍 About to call seed_course_enrollments...")
        enrollments_count = seed_course_enrollments(session)
        print(f"🔍 seed_course_enrollments returned: {enrollments_count}")
        results['course_enrollments'] = enrollments_count
        print(f"✅ Created {enrollments_count} course enrollments")
        
        # Commit course enrollments to protect from rollbacks
        session.commit()
        print("🔒 Course enrollments committed - protecting from rollbacks")
        
        # Seed assignments
        print("Seeding assignments...")
        print("🔍 About to call seed_assignments...")
        assignments_count = seed_assignments(session)
        print(f"🔍 seed_assignments returned: {assignments_count}")
        results['assignments'] = assignments_count
        print(f"✅ Created {assignments_count} assignments")
        
        # Commit assignments to protect from rollbacks
        session.commit()
        print("🔒 Assignments committed - protecting from rollbacks")
        
        # Seed grades
        print("Seeding grades...")
        print("🔍 About to call seed_grades...")
        grades_count = seed_grades(session)
        print(f"🔍 seed_grades returned: {grades_count}")
        results['grades'] = grades_count
        print(f"✅ Created {grades_count} grades")
        
        # Commit grades to protect from rollbacks
        session.commit()
        print("🔒 Grades committed - protecting from rollbacks")
        
        # Seed rubrics
        print("Seeding rubrics...")
        rubrics_count = seed_rubrics(session)
        results['rubrics'] = rubrics_count
        print(f"✅ Created {rubrics_count} rubrics")
        
        # Commit course-related tables to protect from rollbacks
        session.commit()
        print("🔒 Course-related tables committed - protecting from rollbacks")
        
        # Section 2.2: Teacher & Class Management (12 tables)
        print("\n👨‍🏫 SECTION 2.2: TEACHER & CLASS MANAGEMENT")
        print("-" * 50)
        
        # Seed teacher availability
        print("Seeding teacher availability...")
        teacher_availability_count = seed_teacher_availability(session)
        results['teacher_availability'] = teacher_availability_count
        print(f"✅ Created {teacher_availability_count} teacher availability records")
        
        # Seed teacher certifications
        print("Seeding teacher certifications...")
        teacher_certifications_count = seed_teacher_certifications(session)
        results['teacher_certifications'] = teacher_certifications_count
        print(f"✅ Created {teacher_certifications_count} teacher certifications")
        
        # Seed teacher preferences
        print("Seeding teacher preferences...")
        teacher_preferences_count = seed_teacher_preferences(session)
        results['teacher_preferences'] = teacher_preferences_count
        print(f"✅ Created {teacher_preferences_count} teacher preferences")
        
        # Seed teacher qualifications
        print("Seeding teacher qualifications...")
        teacher_qualifications_count = seed_teacher_qualifications(session)
        results['teacher_qualifications'] = teacher_qualifications_count
        print(f"✅ Created {teacher_qualifications_count} teacher qualifications")
        
        # Seed teacher schedules
        print("Seeding teacher schedules...")
        teacher_schedules_count = seed_teacher_schedules(session)
        results['teacher_schedules'] = teacher_schedules_count
        print(f"✅ Created {teacher_schedules_count} teacher schedules")
        
        # Seed teacher specializations
        print("Seeding teacher specializations...")
        teacher_specializations_count = seed_teacher_specializations(session)
        results['teacher_specializations'] = teacher_specializations_count
        print(f"✅ Created {teacher_specializations_count} teacher specializations")
        
        # Seed educational teachers first (needed for educational classes foreign key)
        print("Seeding educational teachers...")
        educational_teachers_count = seed_educational_teachers(session)
        results['educational_teachers'] = educational_teachers_count
        print(f"✅ Created {educational_teachers_count} educational teachers")
        
        # Seed educational classes
        print("Seeding educational classes...")
        educational_classes_count = seed_educational_classes(session)
        results['educational_classes'] = educational_classes_count
        print(f"✅ Created {educational_classes_count} educational classes")
        
        # Seed educational class students
        print("Seeding educational class students...")
        class_students_count = seed_educational_class_students(session)
        results['educational_class_students'] = class_students_count
        print(f"✅ Created {class_students_count} class student enrollments")
        
        # Commit educational classes to protect from rollbacks
        session.commit()
        print("🔒 Educational classes committed - protecting from rollbacks")
        
        # Seed educational teacher availability
        print("Seeding educational teacher availability...")
        edu_teacher_availability_count = seed_educational_teacher_availability(session)
        results['educational_teacher_availability'] = edu_teacher_availability_count
        print(f"✅ Created {edu_teacher_availability_count} educational teacher availability records")
        
        # Seed educational teacher certifications
        print("Seeding educational teacher certifications...")
        edu_teacher_certifications_count = seed_educational_teacher_certifications(session)
        results['educational_teacher_certifications'] = edu_teacher_certifications_count
        print(f"✅ Created {edu_teacher_certifications_count} educational teacher certifications")
        
        # Seed class attendance
        print("Seeding class attendance...")
        class_attendance_count = seed_class_attendance(session)
        results['class_attendance'] = class_attendance_count
        print(f"✅ Created {class_attendance_count} class attendance records")
        
        # Seed class plans
        print("Seeding class plans...")
        class_plans_count = seed_class_plans(session)
        results['class_plans'] = class_plans_count
        print(f"✅ Created {class_plans_count} class plans")
        
        # Seed class schedules
        print("Seeding class schedules...")
        class_schedules_count = seed_class_schedules(session)
        results['class_schedules'] = class_schedules_count
        print(f"✅ Created {class_schedules_count} class schedules")
        
        # Section 2.3: Department & Organization (14 tables)
        print("\n🏢 SECTION 2.3: DEPARTMENT & ORGANIZATION")
        print("-" * 50)
        
        # Seed departments
        print("Seeding departments...")
        departments_count = seed_departments(session)
        results['departments'] = departments_count
        print(f"✅ Created {departments_count} departments")
        
        # Seed department members
        print("Seeding department members...")
        department_members_count = seed_department_members(session)
        results['department_members'] = department_members_count
        print(f"✅ Created {department_members_count} department members")
        
        # Seed organization roles
        print("Seeding organization roles...")
        organization_roles_count = seed_organization_roles(session)
        results['organization_roles'] = organization_roles_count
        print(f"✅ Created {organization_roles_count} organization roles")
        
        # Seed organization members
        print("Seeding organization members...")
        organization_members_count = seed_organization_members(session)
        results['organization_members'] = organization_members_count
        print(f"✅ Created {organization_members_count} organization members")
        
        # Seed organization collaborations
        print("Seeding organization collaborations...")
        collaborations_count = seed_organization_collaborations(session)
        results['organization_collaborations'] = collaborations_count
        print(f"✅ Created {collaborations_count} organization collaborations")
        
        # Seed organization projects
        print("Seeding organization projects...")
        projects_count = seed_organization_projects(session)
        results['organization_projects'] = projects_count
        print(f"✅ Created {projects_count} organization projects")
        
        # Seed organization resources
        print("Seeding organization resources...")
        resources_count = seed_organization_resources(session)
        results['organization_resources'] = resources_count
        print(f"✅ Created {resources_count} organization resources")
        
        # Seed organization settings
        print("Seeding organization settings...")
        settings_count = seed_organization_settings(session)
        results['organization_settings'] = settings_count
        print(f"✅ Created {settings_count} organization settings")
        
        # Seed organization feedback
        print("Seeding organization feedback...")
        feedback_count = seed_organization_feedback(session)
        results['organization_feedback'] = feedback_count
        print(f"✅ Created {feedback_count} organization feedback records")
        
        # Seed teams
        print("Seeding teams...")
        teams_count = seed_teams(session)
        results['teams'] = teams_count
        print(f"✅ Created {teams_count} teams")
        
        # Seed team members
        print("Seeding team members...")
        team_members_count = seed_team_members(session)
        results['team_members'] = team_members_count
        print(f"✅ Created {team_members_count} team members")
        
        print("\n" + "="*60)
        print("🎉 PHASE 2 SEEDING COMPLETE!")
        print("="*60)
        
        total_records = sum(results.values())
        print(f"📊 Total records created: {total_records:,}")
        print(f"📋 Tables populated: {len(results)}")
        
        for table_name, count in results.items():
            print(f"  {table_name}: {count:,} records")
        
        print("="*60)
        
        return results
        
    except Exception as e:
        print(f"❌ Error during Phase 2 seeding: {e}")
        logger.error(f"Phase 2 seeding failed: {e}")
        session.rollback()
        raise

if __name__ == "__main__":
    # Create a session and run the seeding
    session = SessionLocal()
    try:
        results = seed_phase2_educational_system(session)
        session.commit()
        print("✅ Phase 2 seeding completed successfully!")
    except Exception as e:
        print(f"❌ Phase 2 seeding failed: {e}")
        session.rollback()
    finally:
        session.close() 

