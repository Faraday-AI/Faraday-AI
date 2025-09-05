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
            print(f"  ⚠️  physical_education_teachers already has {existing_count} records, skipping...")
            return existing_count
        
        # Create sample physical education teachers
        teachers = []
        for i in range(5):  # Create 5 teachers
            teacher = {
                'user_id': i + 1,  # Simple user ID
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
        
        # Insert teachers
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
        """), teachers)
        
        session.commit()
        print(f"  ✅ Created {len(teachers)} physical education teachers")
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
            print(f"  ⚠️  physical_education_classes already has {existing_count} records, skipping...")
            return existing_count
        
        # Get actual teacher IDs from physical_education_teachers table
        teacher_result = session.execute(text("SELECT id FROM physical_education_teachers ORDER BY id"))
        teacher_ids = [row[0] for row in teacher_result.fetchall()]
        
        if not teacher_ids:
            print("  ⚠️  No teachers found, skipping physical education classes...")
            return 0
        
        # Create sample physical education classes
        classes = []
        for i in range(50):  # Create 50 classes
            class_data = {
                'instructor_id': random.choice(teacher_ids),
                'class_name': f'PE Class {i + 1}',
                'class_code': f'PE{i + 1:03d}',
                'description': f'Physical Education class focusing on {random.choice(["fitness", "team sports", "individual sports", "recreation"])}',
                'max_students': random.randint(15, 30),
                'current_students': random.randint(5, 25),
                'class_type': random.choice(['Regular', 'Advanced', 'Beginner', 'Special Needs']),
                'grade_level': random.choice(['K-2', '3-5', '6-8', '9-12']),
                'is_active': random.choice([True, False]),
                'class_metadata': json.dumps({
                    "equipment_needed": random.choice(["balls", "mats", "cones", "jump ropes"]),
                    "location": f"Gym {random.randint(1, 5)}",
                    "schedule": "Monday, Wednesday, Friday"
                }),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now(),
                'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'archived_at': None,
                'deleted_at': None,
                'scheduled_deletion_at': None,
                'retention_period': random.randint(30, 365)
            }
            classes.append(class_data)
        
        # Insert classes
        session.execute(text("""
            INSERT INTO physical_education_classes (instructor_id, class_name, class_code, description, 
                                                  max_students, current_students, class_type, grade_level,
                                                  is_active, class_metadata, created_at, updated_at,
                                                  last_accessed_at, archived_at, deleted_at, 
                                                  scheduled_deletion_at, retention_period)
            VALUES (:instructor_id, :class_name, :class_code, :description, :max_students, 
                   :current_students, :class_type, :grade_level, :is_active, :class_metadata, 
                   :created_at, :updated_at, :last_accessed_at, :archived_at, :deleted_at, 
                   :scheduled_deletion_at, :retention_period)
        """), classes)
        
        session.commit()
        print(f"  ✅ Created {len(classes)} physical education classes")
        return len(classes)
        
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
            print(f"  ⚠️  activity_plans already has {existing_count} records, skipping...")
            return existing_count
        
        # Create sample activity plans
        plans = []
        for i in range(400):  # Create 400 activity plans
            plan = {
                'plan_name': f'Activity Plan {i + 1}',
                'description': f'Physical activity plan focusing on {random.choice(["cardiovascular fitness", "strength training", "flexibility", "coordination", "team building"])}',
                'activity_type': random.choice(['Cardio', 'Strength', 'Flexibility', 'Sports', 'Games', 'Dance', 'Yoga']),
                'duration_minutes': random.randint(30, 120),
                'difficulty_level': random.choice(['Beginner', 'Intermediate', 'Advanced']),
                'equipment_needed': json.dumps(random.sample(['balls', 'mats', 'cones', 'jump ropes', 'weights', 'resistance bands'], random.randint(1, 3))),
                'instructions': f'Step-by-step instructions for activity plan {i + 1}',
                'safety_notes': f'Safety considerations for activity plan {i + 1}',
                'is_active': random.choice([True, False]),
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
            INSERT INTO activity_plans (plan_name, description, activity_type, duration_minutes, 
                                      difficulty_level, equipment_needed, instructions, safety_notes,
                                      is_active, created_at, updated_at, last_accessed_at, 
                                      archived_at, deleted_at, scheduled_deletion_at, retention_period)
            VALUES (:plan_name, :description, :activity_type, :duration_minutes, :difficulty_level, 
                   :equipment_needed, :instructions, :safety_notes, :is_active, :created_at, 
                   :updated_at, :last_accessed_at, :archived_at, :deleted_at, 
                   :scheduled_deletion_at, :retention_period)
        """), plans)
        
        session.commit()
        print(f"  ✅ Created {len(plans)} activity plans")
        return len(plans)
        
    except Exception as e:
        print(f"  ❌ Error seeding activity_plans: {e}")
        session.rollback()
        return 0

def seed_pe_lesson_plans(session: Session) -> int:
    """Seed PE lesson plans table"""
    try:
        # Check if table exists and has data
        result = session.execute(text("SELECT COUNT(*) FROM pe_lesson_plans"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  ⚠️  pe_lesson_plans already has {existing_count} records, skipping...")
            return existing_count
        
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
            print(f"  ⚠️  lesson_plan_activities already has {existing_count} records, skipping...")
            return existing_count
        
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
        
        # Check if physical_education_curriculum_units has any records
        result = session.execute(text("SELECT COUNT(*) FROM physical_education_curriculum_units"))
        units_count = result.scalar()
        
        if units_count == 0:
            print(f"  📝 Creating curriculum first...")
            # First create some curriculum records
            curriculums = []
            academic_years = ['2023-2024', '2024-2025', '2025-2026']
            for i in range(5):
                curriculum = {
                    'name': f"PE Curriculum {i+1}",
                    'description': f"Physical Education Curriculum {i+1} for comprehensive PE education",
                    'grade_level': random.choice(['K-2', '3-5', '6-8', '9-12']),
                    'academic_year': random.choice(academic_years),
                    'curriculum_metadata': f'{{"subject": "Physical Education", "focus": "Comprehensive PE Education", "standards": "National PE Standards"}}',
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                    'updated_at': datetime.now()
                }
                curriculums.append(curriculum)
            
            # Insert curriculum records
            session.execute(text("""
                INSERT INTO curriculum (name, description, grade_level, academic_year, curriculum_metadata, created_at, updated_at)
                VALUES (:name, :description, :grade_level, :academic_year, :curriculum_metadata, :created_at, :updated_at)
            """), curriculums)
            print(f"  ✅ Created {len(curriculums)} curriculum records")
            
            # Get the curriculum IDs
            curriculum_result = session.execute(text("SELECT id FROM curriculum ORDER BY id"))
            curriculum_ids = [row[0] for row in curriculum_result.fetchall()]
            
            print(f"  📝 Creating curriculum units...")
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
            print(f"  ✅ Created {len(units)} curriculum units")
        
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
        
        # Get actual unit IDs from the database
        unit_result = session.execute(text("SELECT id FROM physical_education_curriculum_units ORDER BY id"))
        unit_ids = [row[0] for row in unit_result.fetchall()]
        
        if not unit_ids:
            print("  ⚠️  No curriculum units found, skipping standards...")
            return 0
        
        # Create sample curriculum standards
        standards = []
        categories = ['Motor Skills', 'Fitness', 'Knowledge', 'Behavior', 'Social']
        levels = ['Beginner', 'Intermediate', 'Advanced', 'Expert']
        grade_levels = ['K-2', '3-5', '6-8', '9-12']
        
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
        
        # Get actual curriculum and standard IDs from the database
        curriculum_result = session.execute(text("SELECT id FROM curricula ORDER BY id"))
        curriculum_ids = [row[0] for row in curriculum_result.fetchall()]
        
        standard_result = session.execute(text("SELECT id FROM curriculum_standards ORDER BY id"))
        standard_ids = [row[0] for row in standard_result.fetchall()]
        
        if not curriculum_ids or not standard_ids:
            print("  ⚠️  No curricula or standards found, skipping associations...")
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
        
        return len(associations)
        
    except Exception as e:
        print(f"  ❌ Error seeding curriculum_standard_association: {e}")
        return 0

def seed_curriculum(session: Session) -> int:
    """Seed curriculum table"""
    try:
        # Check if table exists and has data
        result = session.execute(text("SELECT COUNT(*) FROM curriculum"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  ⚠️  curriculum already has {existing_count} records, skipping...")
            return existing_count
        
        # Create sample curriculum records
        curricula = []
        curriculum_types = ['Standard', 'Advanced', 'Remedial', 'Enrichment']
        subjects = ['Physical Education', 'Health Education', 'Sports Science']
        
        for i in range(30):
            curriculum = {
                'name': f"Curriculum {i+1}",
                'description': f"Description for curriculum {i+1}",
                'curriculum_type': random.choice(curriculum_types),
                'subject': random.choice(subjects),
                'grade_level_start': random.randint(1, 12),
                'grade_level_end': random.randint(1, 12),
                'is_active': random.choice([True, False]),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now()
            }
            curricula.append(curriculum)
        
        # Insert curricula
        session.execute(text("""
            INSERT INTO curriculum (name, description, curriculum_type, subject, 
                                  grade_level_start, grade_level_end, is_active, 
                                  created_at, updated_at)
            VALUES (:name, :description, :curriculum_type, :subject, 
                    :grade_level_start, :grade_level_end, :is_active, 
                    :created_at, :updated_at)
        """), curricula)
        
        return len(curricula)
        
    except Exception as e:
        print(f"  ❌ Error seeding curriculum: {e}")
        return 0

def seed_courses(session: Session) -> int:
    """Seed courses table"""
    try:
        # Check if table exists and has data
        result = session.execute(text("SELECT COUNT(*) FROM courses"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  ⚠️  courses already has {existing_count} records, skipping...")
            return existing_count
        
        # Create sample courses with unique codes
        courses = []
        course_names = ['Physical Education Fundamentals', 'Health and Wellness', 'Sports Science', 'Nutrition Basics', 'Fitness Training', 'Team Sports', 'Individual Sports', 'Outdoor Education']
        used_codes = set()
        
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
                'created_by': 1,  # Assuming user ID 1 exists
                'is_active': random.choice([True, False]),
                'start_date': datetime.now() - timedelta(days=random.randint(1, 365)),
                'end_date': datetime.now() + timedelta(days=random.randint(30, 365)),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now()
            }
            courses.append(course)
        
        # Insert courses
        session.execute(text("""
            INSERT INTO courses (name, code, description, created_by, is_active, 
                               start_date, end_date, created_at, updated_at)
            VALUES (:name, :code, :description, :created_by, :is_active, 
                    :start_date, :end_date, :created_at, :updated_at)
        """), courses)
        
        return len(courses)
        
    except Exception as e:
        print(f"  ❌ Error seeding courses: {e}")
        return 0

def seed_course_enrollments(session: Session) -> int:
    """Seed course enrollments table"""
    try:
        # Check if table exists and has data
        result = session.execute(text("SELECT COUNT(*) FROM course_enrollments"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  ⚠️  course_enrollments already has {existing_count} records, skipping...")
            return existing_count
        
        # Get actual course IDs and user IDs from the database
        course_result = session.execute(text("SELECT id FROM courses ORDER BY id"))
        course_ids = [row[0] for row in course_result.fetchall()]
        
        user_result = session.execute(text("SELECT id FROM dashboard_users ORDER BY id"))
        user_ids = [row[0] for row in user_result.fetchall()]
        
        if not course_ids or not user_ids:
            print("  ⚠️  No courses or users found, skipping enrollments...")
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
        
        return len(enrollments)
        
    except Exception as e:
        print(f"  ❌ Error seeding course_enrollments: {e}")
        return 0

def seed_assignments(session: Session) -> int:
    """Seed assignments table"""
    try:
        # Check if table exists and has data
        result = session.execute(text("SELECT COUNT(*) FROM assignments"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  ⚠️  assignments already has {existing_count} records, skipping...")
            return existing_count
        
        # Get actual course IDs from the database
        course_result = session.execute(text("SELECT id FROM courses ORDER BY id"))
        course_ids = [row[0] for row in course_result.fetchall()]
        
        if not course_ids:
            print("  ⚠️  No courses found, skipping assignments...")
            return 0
        
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
        
        # Insert assignments using only existing columns
        session.execute(text("""
            INSERT INTO assignments (course_id, title, description, due_date, 
                                   created_by, rubric_id, status, created_at, updated_at)
            VALUES (:course_id, :title, :description, :due_date, 
                    :created_by, :rubric_id, :status, :created_at, :updated_at)
        """), assignments)
        
        return len(assignments)
        
    except Exception as e:
        print(f"  ❌ Error seeding assignments: {e}")
        return 0

def seed_grades(session: Session) -> int:
    """Seed grades table"""
    try:
        # Check if table exists and has data
        result = session.execute(text("SELECT COUNT(*) FROM grades"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  ⚠️  grades already has {existing_count} records, skipping...")
            return existing_count
        
        # Get actual assignment and student IDs from the database
        assignment_result = session.execute(text("SELECT id FROM assignments ORDER BY id"))
        assignment_ids = [row[0] for row in assignment_result.fetchall()]
        
        user_result = session.execute(text("SELECT id FROM dashboard_users ORDER BY id"))
        user_ids = [row[0] for row in user_result.fetchall()]
        
        if not assignment_ids or not user_ids:
            print("  ⚠️  No assignments or users found, skipping grades...")
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
        # Check if table exists and has data
        result = session.execute(text("SELECT COUNT(*) FROM educational_classes"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  ⚠️  educational_classes already has {existing_count} records, skipping...")
            return existing_count
        
        # Get actual teacher IDs from physical_education_teachers table
        teacher_result = session.execute(text("SELECT id FROM physical_education_teachers ORDER BY id"))
        teacher_ids = [row[0] for row in teacher_result.fetchall()]
        
        if not teacher_ids:
            print("  ⚠️  No teachers found, skipping educational classes...")
            return 0
        
        # Create sample educational classes
        classes = []
        class_types = ['REGULAR', 'SPECIAL_NEEDS', 'ATHLETIC', 'RECREATIONAL', 'COMPETITIVE', 'ADVANCED', 'BEGINNER']
        subjects = ['Physical Education', 'Health Education', 'Sports Science']
        statuses = ['PLANNED', 'ACTIVE', 'COMPLETED', 'CANCELLED', 'ON_HOLD']
        locations = ['Gymnasium A', 'Gymnasium B', 'Outdoor Field', 'Classroom 101', 'Classroom 102']
        
        for i in range(50):
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
        return len(classes)
        
    except Exception as e:
        print(f"  ❌ Error seeding educational_classes: {e}")
        return 0

def seed_educational_class_students(session: Session) -> int:
    """Seed educational class students table"""
    try:
        # Check if table exists and has data
        result = session.execute(text("SELECT COUNT(*) FROM educational_class_students"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"  ⚠️  educational_class_students already has {existing_count} records, skipping...")
            return existing_count
        
        # Get actual class IDs and student IDs from the database
        class_result = session.execute(text("SELECT id FROM educational_classes ORDER BY id"))
        class_ids = [row[0] for row in class_result.fetchall()]
        
        student_result = session.execute(text("SELECT id FROM dashboard_users ORDER BY id"))
        student_ids = [row[0] for row in student_result.fetchall()]
        
        if not class_ids or not student_ids:
            print("  ⚠️  No classes or students found, skipping enrollments...")
            return 0
        
        # Create sample class student enrollments
        enrollments = []
        statuses = ['Active', 'Dropped', 'Completed', 'On Hold']
        
        for i in range(200):
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
        teacher_result = session.execute(text("SELECT id FROM physical_education_teachers ORDER BY id"))
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
        teacher_result = session.execute(text("SELECT id FROM physical_education_teachers ORDER BY id"))
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
        
        student_result = session.execute(text("SELECT id FROM dashboard_users ORDER BY id"))
        student_ids = [row[0] for row in student_result.fetchall()]
        
        if not class_ids or not student_ids:
            print("  ⚠️  No classes or students found, skipping class attendance...")
            return 0
        
        # Create sample class attendance records
        attendance_records = []
        
        for i in range(1000):
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
            print(f"  ⚠️  departments already has {existing_count} records, skipping...")
            return existing_count
        
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
        
        user_result = session.execute(text("SELECT id FROM dashboard_users LIMIT 100"))
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
            print(f"  ⚠️  organization_projects already has {existing_count} records, skipping...")
            return existing_count
        
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
            print(f"  ⚠️  organization_settings already has {existing_count} records, skipping...")
            return existing_count
        
        # Get actual organization_ids from database
        org_result = session.execute(text("SELECT id FROM organizations LIMIT 5"))
        organization_ids = [row[0] for row in org_result.fetchall()]
        
        if not organization_ids:
            print("  ⚠️  No organizations found, skipping organization_settings...")
            return 0
        
        # Create sample organization settings (one per organization)
        settings = []
        statuses = ['ACTIVE', 'INACTIVE', 'PENDING', 'SCHEDULED', 'COMPLETED', 'CANCELLED', 'ON_HOLD']
        
        for i, org_id in enumerate(organization_ids):
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
        user_result = session.execute(text("SELECT id FROM dashboard_users LIMIT 100"))
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
        
        user_result = session.execute(text("SELECT id FROM dashboard_users LIMIT 100"))
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
        standard_associations_count = seed_curriculum_standard_associations(session)
        results['curriculum_standard_association'] = standard_associations_count
        print(f"✅ Created {standard_associations_count} standard associations")
        
        # Seed curriculum
        print("Seeding curriculum...")
        curriculum_count = seed_curriculum(session)
        results['curriculum'] = curriculum_count
        print(f"✅ Created {curriculum_count} curriculum records")
        
        # Seed courses
        print("Seeding courses...")
        courses_count = seed_courses(session)
        results['courses'] = courses_count
        print(f"✅ Created {courses_count} courses")
        
        # Seed course enrollments
        print("Seeding course enrollments...")
        enrollments_count = seed_course_enrollments(session)
        results['course_enrollments'] = enrollments_count
        print(f"✅ Created {enrollments_count} course enrollments")
        
        # Seed assignments
        print("Seeding assignments...")
        assignments_count = seed_assignments(session)
        results['assignments'] = assignments_count
        print(f"✅ Created {assignments_count} assignments")
        
        # Seed grades
        print("Seeding grades...")
        grades_count = seed_grades(session)
        results['grades'] = grades_count
        print(f"✅ Created {grades_count} grades")
        
        # Seed rubrics
        print("Seeding rubrics...")
        rubrics_count = seed_rubrics(session)
        results['rubrics'] = rubrics_count
        print(f"✅ Created {rubrics_count} rubrics")
        
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

