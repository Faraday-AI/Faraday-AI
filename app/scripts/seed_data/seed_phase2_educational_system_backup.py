#!/usr/bin/env python3
"""
Phase 2: Educational System Enhancement Seeding Script
Seeds 38 tables for advanced educational features, teacher management, and organization structure
"""

import os
import sys
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
from app.models.educational.curriculum.assignment import Assignment
from app.models.educational.curriculum.grade import Grade
from app.models.educational.curriculum.rubric import Rubric
from app.models.educational.teacher.teacher_management import (
    TeacherAvailability, TeacherCertification, TeacherPreference,
    TeacherQualification, TeacherSchedule, TeacherSpecialization
)
from app.models.educational.class_.class_management import (
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
        
        for i in range(400):
            lesson_plan = {
                'title': f"PE Lesson Plan {i+1}",
                'subject': random.choice(pe_subjects),
                'grade_level': random.choice(grade_levels),
                'duration_minutes': random.randint(30, 90),
                'objectives': f"Learning objectives for lesson {i+1}",
                'materials_needed': f"Equipment and materials for lesson {i+1}",
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now()
            }
            lesson_plans.append(lesson_plan)
        
        # Insert lesson plans
        session.execute(text("""
            INSERT INTO pe_lesson_plans (title, subject, grade_level, duration_minutes, 
                                       objectives, materials_needed, created_at, updated_at)
            VALUES (:title, :subject, :grade_level, :duration_minutes, 
                    :objectives, :materials_needed, :created_at, :updated_at)
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
        
        # Create sample lesson plan activities
        activities = []
        activity_types = ['Warm-up', 'Main Activity', 'Cool-down', 'Assessment', 'Game']
        
        for i in range(1200):
            activity = {
                'lesson_plan_id': random.randint(1, 400),  # Assuming 400 lesson plans exist
                'activity_type': random.choice(activity_types),
                'title': f"Activity {i+1}",
                'description': f"Description for activity {i+1}",
                'duration_minutes': random.randint(5, 30),
                'sequence_order': random.randint(1, 10),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now()
            }
            activities.append(activity)
        
        # Insert activities
        session.execute(text("""
            INSERT INTO lesson_plan_activities (lesson_plan_id, activity_type, title, 
                                              description, duration_minutes, sequence_order, 
                                              created_at, updated_at)
            VALUES (:lesson_plan_id, :activity_type, :title, :description, 
                    :duration_minutes, :sequence_order, :created_at, :updated_at)
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
        
        # Create sample lesson plan objectives
        objectives = []
        objective_types = ['Knowledge', 'Skill', 'Attitude', 'Behavior']
        
        for i in range(2400):
            objective = {
                'lesson_plan_id': random.randint(1, 400),  # Assuming 400 lesson plans exist
                'objective_type': random.choice(objective_types),
                'description': f"Objective {i+1} for lesson plan",
                'is_measurable': random.choice([True, False]),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now()
            }
            objectives.append(objective)
        
        # Insert objectives
        session.execute(text("""
            INSERT INTO lesson_plan_objectives (lesson_plan_id, objective_type, description, 
                                              is_measurable, created_at, updated_at)
            VALUES (:lesson_plan_id, :objective_type, :description, 
                    :is_measurable, :created_at, :updated_at)
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
        
        # Create sample curriculum lessons
        lessons = []
        subjects = ['Physical Education', 'Health Education', 'Sports Science', 'Nutrition']
        grade_levels = ['K-2', '3-5', '6-8', '9-12']
        
        for i in range(600):
            lesson = {
                'curriculum_id': random.randint(1, 30),  # Assuming 30 curriculum records exist
                'title': f"Curriculum Lesson {i+1}",
                'subject': random.choice(subjects),
                'grade_level': random.choice(grade_levels),
                'sequence_order': random.randint(1, 50),
                'estimated_duration': random.randint(30, 120),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now()
            }
            lessons.append(lesson)
        
        # Insert lessons
        session.execute(text("""
            INSERT INTO curriculum_lessons (curriculum_id, title, subject, grade_level, 
                                          sequence_order, estimated_duration, created_at, updated_at)
            VALUES (:curriculum_id, :title, :subject, :grade_level, :sequence_order, 
                    :estimated_duration, :created_at, :updated_at)
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
        
        # Create sample curriculum standards
        standards = []
        standard_types = ['National', 'State', 'District', 'School']
        subjects = ['Physical Education', 'Health Education', 'Sports Science']
        
        for i in range(50):
            standard = {
                'standard_code': f"PE.{random.randint(1, 12)}.{random.randint(1, 5)}",
                'title': f"Standard {i+1}",
                'description': f"Description for standard {i+1}",
                'standard_type': random.choice(standard_types),
                'subject': random.choice(subjects),
                'grade_level': f"{random.randint(1, 12)}",
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now()
            }
            standards.append(standard)
        
        # Insert standards
        session.execute(text("""
            INSERT INTO curriculum_standards (standard_code, title, description, standard_type, 
                                            subject, grade_level, created_at, updated_at)
            VALUES (:standard_code, :title, :description, :standard_type, 
                    :subject, :grade_level, :created_at, :updated_at)
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
        
        # Create sample associations
        associations = []
        
        for i in range(200):
            association = {
                'curriculum_id': random.randint(1, 30),  # Assuming 30 curriculum records exist
                'standard_id': random.randint(1, 50),    # Assuming 50 standards exist
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now()
            }
            associations.append(association)
        
        # Insert associations
        session.execute(text("""
            INSERT INTO curriculum_standard_association (curriculum_id, standard_id, 
                                                       created_at, updated_at)
            VALUES (:curriculum_id, :standard_id, :created_at, :updated_at)
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
        
        # Create sample courses
        courses = []
        course_types = ['Required', 'Elective', 'Honors', 'AP']
        subjects = ['Physical Education', 'Health Education', 'Sports Science', 'Nutrition']
        
        for i in range(25):
            course = {
                'course_code': f"PE{random.randint(100, 999)}",
                'title': f"Course {i+1}",
                'description': f"Description for course {i+1}",
                'course_type': random.choice(course_types),
                'subject': random.choice(subjects),
                'credits': random.randint(1, 4),
                'grade_level': random.randint(9, 12),
                'is_active': random.choice([True, False]),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now()
            }
            courses.append(course)
        
        # Insert courses
        session.execute(text("""
            INSERT INTO courses (course_code, title, description, course_type, subject, 
                               credits, grade_level, is_active, created_at, updated_at)
            VALUES (:course_code, :title, :description, :course_type, :subject, 
                    :credits, :grade_level, :is_active, :created_at, :updated_at)
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
        
        # Create sample enrollments
        enrollments = []
        enrollment_statuses = ['Active', 'Completed', 'Dropped', 'In Progress']
        
        for i in range(500):
            enrollment = {
                'course_id': random.randint(1, 25),      # Assuming 25 courses exist
                'student_id': random.randint(1, 100),    # Assuming 100 students exist
                'enrollment_date': datetime.now() - timedelta(days=random.randint(1, 365)),
                'enrollment_status': random.choice(enrollment_statuses),
                'grade': random.choice(['A', 'B', 'C', 'D', 'F', None]),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now()
            }
            enrollments.append(enrollment)
        
        # Insert enrollments
        session.execute(text("""
            INSERT INTO course_enrollments (course_id, student_id, enrollment_date, 
                                          enrollment_status, grade, created_at, updated_at)
            VALUES (:course_id, :student_id, :enrollment_date, :enrollment_status, 
                    :grade, :created_at, :updated_at)
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
        
        # Create sample assignments
        assignments = []
        assignment_types = ['Homework', 'Project', 'Quiz', 'Test', 'Presentation']
        
        for i in range(800):
            assignment = {
                'course_id': random.randint(1, 25),      # Assuming 25 courses exist
                'title': f"Assignment {i+1}",
                'description': f"Description for assignment {i+1}",
                'assignment_type': random.choice(assignment_types),
                'due_date': datetime.now() + timedelta(days=random.randint(1, 30)),
                'max_points': random.randint(10, 100),
                'is_active': random.choice([True, False]),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now()
            }
            assignments.append(assignment)
        
        # Insert assignments
        session.execute(text("""
            INSERT INTO assignments (course_id, title, description, assignment_type, 
                                   due_date, max_points, is_active, created_at, updated_at)
            VALUES (:course_id, :title, :description, :assignment_type, 
                    :due_date, :max_points, :is_active, :created_at, :updated_at)
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
        
        # Create sample grades
        grades = []
        letter_grades = ['A', 'B', 'C', 'D', 'F']
        
        for i in range(1200):
            grade = {
                'assignment_id': random.randint(1, 800),  # Assuming 800 assignments exist
                'student_id': random.randint(1, 100),     # Assuming 100 students exist
                'letter_grade': random.choice(letter_grades),
                'numeric_score': random.randint(60, 100),
                'feedback': f"Feedback for assignment {i+1}",
                'graded_date': datetime.now() - timedelta(days=random.randint(1, 30)),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now()
            }
            grades.append(grade)
        
        # Insert grades
        session.execute(text("""
            INSERT INTO grades (assignment_id, student_id, letter_grade, numeric_score, 
                               feedback, graded_date, created_at, updated_at)
            VALUES (:assignment_id, :student_id, :letter_grade, :numeric_score, 
                    :feedback, :graded_date, :created_at, :updated_at)
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
        
        # Create sample rubrics
        rubrics = []
        rubric_types = ['Analytic', 'Holistic', 'Single-Point']
        
        for i in range(40):
            rubric = {
                'title': f"Rubric {i+1}",
                'description': f"Description for rubric {i+1}",
                'rubric_type': random.choice(rubric_types),
                'max_score': random.randint(10, 100),
                'is_active': random.choice([True, False]),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now()
            }
            rubrics.append(rubric)
        
        # Insert rubrics
        session.execute(text("""
            INSERT INTO rubrics (title, description, rubric_type, max_score, 
                               is_active, created_at, updated_at)
            VALUES (:title, :description, :rubric_type, :max_score, 
                    :is_active, :created_at, :updated_at)
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
        
        # Create sample teacher availability records
        availability_records = []
        availability_types = ['Available', 'Busy', 'Out of Office', 'On Leave']
        
        for i in range(100):
            availability = {
                'teacher_id': random.randint(1, 50),  # Assuming 50 teachers exist
                'availability_type': random.choice(availability_types),
                'start_time': datetime.now() + timedelta(hours=random.randint(0, 24)),
                'end_time': datetime.now() + timedelta(hours=random.randint(1, 8)),
                'notes': f"Availability notes for teacher {i+1}",
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now()
            }
            availability_records.append(availability)
        
        # Insert availability records
        session.execute(text("""
            INSERT INTO teacher_availability (teacher_id, availability_type, start_time, 
                                            end_time, notes, created_at, updated_at)
            VALUES (:teacher_id, :availability_type, :start_time, :end_time, 
                    :notes, :created_at, :updated_at)
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
        
        # Create sample teacher certifications
        certifications = []
        cert_types = ['Teaching License', 'PE Certification', 'Health Certification', 'First Aid', 'CPR']
        
        for i in range(80):
            certification = {
                'teacher_id': random.randint(1, 50),  # Assuming 50 teachers exist
                'certification_type': random.choice(cert_types),
                'certification_number': f"CERT-{random.randint(10000, 99999)}",
                'issue_date': datetime.now() - timedelta(days=random.randint(1, 1825)),  # Up to 5 years ago
                'expiry_date': datetime.now() + timedelta(days=random.randint(1, 1825)),  # Up to 5 years in future
                'issuing_authority': f"Authority {random.randint(1, 10)}",
                'is_active': random.choice([True, False]),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now()
            }
            certifications.append(certification)
        
        # Insert certifications
        session.execute(text("""
            INSERT INTO teacher_certifications (teacher_id, certification_type, certification_number, 
                                              issue_date, expiry_date, issuing_authority, is_active, 
                                              created_at, updated_at)
            VALUES (:teacher_id, :certification_type, :certification_number, :issue_date, 
                    :expiry_date, :issuing_authority, :is_active, :created_at, :updated_at)
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
        
        # Create sample teacher preferences
        preferences = []
        preference_types = ['Class Size', 'Teaching Style', 'Assessment Method', 'Technology Usage']
        
        for i in range(50):
            preference = {
                'teacher_id': random.randint(1, 50),  # Assuming 50 teachers exist
                'preference_type': random.choice(preference_types),
                'preference_value': f"Preference value {i+1}",
                'priority': random.randint(1, 5),
                'is_active': random.choice([True, False]),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now()
            }
            preferences.append(preference)
        
        # Insert preferences
        session.execute(text("""
            INSERT INTO teacher_preferences (teacher_id, preference_type, preference_value, 
                                           priority, is_active, created_at, updated_at)
            VALUES (:teacher_id, :preference_type, :preference_value, :priority, 
                    :is_active, :created_at, :updated_at)
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
        
        # Create sample teacher qualifications
        qualifications = []
        degree_types = ['Bachelor', 'Master', 'PhD', 'Associate']
        subjects = ['Physical Education', 'Health Education', 'Sports Science', 'Education']
        
        for i in range(60):
            qualification = {
                'teacher_id': random.randint(1, 50),  # Assuming 50 teachers exist
                'degree_type': random.choice(degree_types),
                'subject': random.choice(subjects),
                'institution': f"University {random.randint(1, 20)}",
                'graduation_year': random.randint(1990, 2024),
                'gpa': round(random.uniform(2.5, 4.0), 2),
                'is_verified': random.choice([True, False]),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now()
            }
            qualifications.append(qualification)
        
        # Insert qualifications
        session.execute(text("""
            INSERT INTO teacher_qualifications (teacher_id, degree_type, subject, institution, 
                                              graduation_year, gpa, is_verified, created_at, updated_at)
            VALUES (:teacher_id, :degree_type, :subject, :institution, :graduation_year, 
                    :gpa, :is_verified, :created_at, :updated_at)
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
        
        # Create sample teacher schedules
        schedules = []
        schedule_types = ['Regular', 'Substitute', 'Special Event', 'Professional Development']
        
        for i in range(100):
            schedule = {
                'teacher_id': random.randint(1, 50),  # Assuming 50 teachers exist
                'schedule_type': random.choice(schedule_types),
                'start_time': datetime.now() + timedelta(hours=random.randint(7, 17)),  # 7 AM to 5 PM
                'end_time': datetime.now() + timedelta(hours=random.randint(8, 18)),   # 8 AM to 6 PM
                'day_of_week': random.randint(1, 7),  # Monday = 1, Sunday = 7
                'is_recurring': random.choice([True, False]),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now()
            }
            schedules.append(schedule)
        
        # Insert schedules
        session.execute(text("""
            INSERT INTO teacher_schedules (teacher_id, schedule_type, start_time, end_time, 
                                         day_of_week, is_recurring, created_at, updated_at)
            VALUES (:teacher_id, :schedule_type, :start_time, :end_time, :day_of_week, 
                    :is_recurring, :created_at, :updated_at)
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
        
        # Create sample teacher specializations
        specializations = []
        spec_areas = ['Elementary PE', 'Secondary PE', 'Adaptive PE', 'Health Education', 'Sports Coaching']
        
        for i in range(75):
            specialization = {
                'teacher_id': random.randint(1, 50),  # Assuming 50 teachers exist
                'specialization_area': random.choice(spec_areas),
                'years_experience': random.randint(1, 20),
                'certification_level': random.choice(['Basic', 'Intermediate', 'Advanced', 'Expert']),
                'is_primary': random.choice([True, False]),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now()
            }
            specializations.append(specialization)
        
        # Insert specializations
        session.execute(text("""
            INSERT INTO teacher_specializations (teacher_id, specialization_area, years_experience, 
                                               certification_level, is_primary, created_at, updated_at)
            VALUES (:teacher_id, :specialization_area, :years_experience, :certification_level, 
                    :is_primary, :created_at, :updated_at)
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
        
        # Create sample educational classes
        classes = []
        class_types = ['Regular', 'Honors', 'AP', 'Remedial', 'Enrichment']
        subjects = ['Physical Education', 'Health Education', 'Sports Science']
        
        for i in range(50):
            class_record = {
                'class_name': f"Class {i+1}",
                'class_type': random.choice(class_types),
                'subject': random.choice(subjects),
                'grade_level': random.randint(1, 12),
                'max_students': random.randint(15, 35),
                'teacher_id': random.randint(1, 50),  # Assuming 50 teachers exist
                'is_active': random.choice([True, False]),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now()
            }
            classes.append(class_record)
        
        # Insert classes
        session.execute(text("""
            INSERT INTO educational_classes (class_name, class_type, subject, grade_level, 
                                           max_students, teacher_id, is_active, created_at, updated_at)
            VALUES (:class_name, :class_type, :subject, :grade_level, :max_students, 
                    :teacher_id, :is_active, :created_at, :updated_at)
        """), classes)
        
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
        
        # Create sample class student enrollments
        enrollments = []
        enrollment_statuses = ['Active', 'Dropped', 'Completed', 'On Hold']
        
        for i in range(200):
            enrollment = {
                'class_id': random.randint(1, 50),      # Assuming 50 classes exist
                'student_id': random.randint(1, 100),   # Assuming 100 students exist
                'enrollment_date': datetime.now() - timedelta(days=random.randint(1, 365)),
                'enrollment_status': random.choice(enrollment_statuses),
                'grade': random.choice(['A', 'B', 'C', 'D', 'F', None]),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now()
            }
            enrollments.append(enrollment)
        
        # Insert enrollments
        session.execute(text("""
            INSERT INTO educational_class_students (class_id, student_id, enrollment_date, 
                                                  enrollment_status, grade, created_at, updated_at)
            VALUES (:class_id, :student_id, :enrollment_date, :enrollment_status, 
                    :grade, :created_at, :updated_at)
        """), enrollments)
        
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
        
        # Create sample educational teacher availability records
        availability_records = []
        availability_types = ['Available', 'Busy', 'Out of Office', 'On Leave']
        
        for i in range(100):
            availability = {
                'teacher_id': random.randint(1, 50),  # Assuming 50 teachers exist
                'availability_type': random.choice(availability_types),
                'start_time': datetime.now() + timedelta(hours=random.randint(0, 24)),
                'end_time': datetime.now() + timedelta(hours=random.randint(1, 8)),
                'notes': f"Educational availability notes for teacher {i+1}",
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now()
            }
            availability_records.append(availability)
        
        # Insert availability records
        session.execute(text("""
            INSERT INTO educational_teacher_availability (teacher_id, availability_type, start_time, 
                                                        end_time, notes, created_at, updated_at)
            VALUES (:teacher_id, :availability_type, :start_time, :end_time, 
                    :notes, :created_at, :updated_at)
        """), availability_records)
        
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
        
        # Create sample educational teacher certifications
        certifications = []
        cert_types = ['Teaching License', 'PE Certification', 'Health Certification', 'First Aid', 'CPR']
        
        for i in range(80):
            certification = {
                'teacher_id': random.randint(1, 50),  # Assuming 50 teachers exist
                'certification_type': random.choice(cert_types),
                'certification_number': f"EDU-CERT-{random.randint(10000, 99999)}",
                'issue_date': datetime.now() - timedelta(days=random.randint(1, 1825)),  # Up to 5 years ago
                'expiry_date': datetime.now() + timedelta(days=random.randint(1, 1825)),  # Up to 5 years in future
                'issuing_authority': f"Educational Authority {random.randint(1, 10)}",
                'is_active': random.choice([True, False]),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now()
            }
            certifications.append(certification)
        
        # Insert certifications
        session.execute(text("""
            INSERT INTO educational_teacher_certifications (teacher_id, certification_type, certification_number, 
                                                          issue_date, expiry_date, issuing_authority, is_active, 
                                                          created_at, updated_at)
            VALUES (:teacher_id, :certification_type, :certification_number, :issue_date, 
                    :expiry_date, :issuing_authority, :is_active, :created_at, :updated_at)
        """), certifications)
        
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
        
        # Create sample class attendance records
        attendance_records = []
        attendance_statuses = ['Present', 'Absent', 'Late', 'Excused', 'Tardy']
        
        for i in range(1000):
            attendance = {
                'class_id': random.randint(1, 50),      # Assuming 50 classes exist
                'student_id': random.randint(1, 100),   # Assuming 100 students exist
                'attendance_date': datetime.now() - timedelta(days=random.randint(1, 30)),
                'attendance_status': random.choice(attendance_statuses),
                'notes': f"Attendance notes for record {i+1}",
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now()
            }
            attendance_records.append(attendance)
        
        # Insert attendance records
        session.execute(text("""
            INSERT INTO class_attendance (class_id, student_id, attendance_date, attendance_status, 
                                        notes, created_at, updated_at)
            VALUES (:class_id, :student_id, :attendance_date, :attendance_status, 
                    :notes, :created_at, :updated_at)
        """), attendance_records)
        
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
        
        # Create sample class plans
        plans = []
        plan_types = ['Daily', 'Weekly', 'Monthly', 'Unit', 'Semester']
        
        for i in range(150):
            plan = {
                'class_id': random.randint(1, 50),  # Assuming 50 classes exist
                'plan_type': random.choice(plan_types),
                'title': f"Class Plan {i+1}",
                'description': f"Description for class plan {i+1}",
                'start_date': datetime.now() - timedelta(days=random.randint(1, 365)),
                'end_date': datetime.now() + timedelta(days=random.randint(1, 365)),
                'is_active': random.choice([True, False]),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now()
            }
            plans.append(plan)
        
        # Insert plans
        session.execute(text("""
            INSERT INTO class_plans (class_id, plan_type, title, description, start_date, 
                                   end_date, is_active, created_at, updated_at)
            VALUES (:class_id, :plan_type, :title, :description, :start_date, 
                    :end_date, :is_active, :created_at, :updated_at)
        """), plans)
        
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
        
        # Create sample class schedules
        schedules = []
        schedule_types = ['Regular', 'Special Event', 'Field Trip', 'Assembly']
        
        for i in range(200):
            schedule = {
                'class_id': random.randint(1, 50),  # Assuming 50 classes exist
                'schedule_type': random.choice(schedule_types),
                'start_time': datetime.now() + timedelta(hours=random.randint(7, 17)),  # 7 AM to 5 PM
                'end_time': datetime.now() + timedelta(hours=random.randint(8, 18)),   # 8 AM to 6 PM
                'day_of_week': random.randint(1, 7),  # Monday = 1, Sunday = 7
                'room_number': f"Room {random.randint(100, 999)}",
                'is_recurring': random.choice([True, False]),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now()
            }
            schedules.append(schedule)
        
        # Insert schedules
        session.execute(text("""
            INSERT INTO class_schedules (class_id, schedule_type, start_time, end_time, 
                                       day_of_week, room_number, is_recurring, created_at, updated_at)
            VALUES (:class_id, :schedule_type, :start_time, :end_time, :day_of_week, 
                    :room_number, :is_recurring, :created_at, :updated_at)
        """), schedules)
        
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
        dept_types = ['Academic', 'Administrative', 'Support', 'Research', 'Student Services']
        
        for i in range(8):
            department = {
                'name': f"Department {i+1}",
                'description': f"Description for department {i+1}",
                'department_type': random.choice(dept_types),
                'head_teacher_id': random.randint(1, 50),  # Assuming 50 teachers exist
                'is_active': random.choice([True, False]),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now()
            }
            departments.append(department)
        
        # Insert departments
        session.execute(text("""
            INSERT INTO departments (name, description, department_type, head_teacher_id, 
                                   is_active, created_at, updated_at)
            VALUES (:name, :description, :department_type, :head_teacher_id, 
                    :is_active, :created_at, :updated_at)
        """), departments)
        
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
        
        for i in range(40):
            member = {
                'department_id': random.randint(1, 8),   # Assuming 8 departments exist
                'teacher_id': random.randint(1, 50),     # Assuming 50 teachers exist
                'role': random.choice(member_roles),
                'join_date': datetime.now() - timedelta(days=random.randint(1, 1825)),  # Up to 5 years ago
                'is_active': random.choice([True, False]),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now()
            }
            members.append(member)
        
        # Insert members
        session.execute(text("""
            INSERT INTO department_members (department_id, teacher_id, role, join_date, 
                                          is_active, created_at, updated_at)
            VALUES (:department_id, :teacher_id, :role, :join_date, 
                    :is_active, :created_at, :updated_at)
        """), members)
        
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
        role_types = ['Administrative', 'Academic', 'Support', 'Leadership', 'Staff']
        
        for i in range(15):
            role = {
                'role_name': f"Role {i+1}",
                'description': f"Description for role {i+1}",
                'role_type': random.choice(role_types),
                'permissions': f"Permissions for role {i+1}",
                'is_active': random.choice([True, False]),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now()
            }
            roles.append(role)
        
        # Insert roles
        session.execute(text("""
            INSERT INTO organization_roles (role_name, description, role_type, permissions, 
                                          is_active, created_at, updated_at)
            VALUES (:role_name, :description, :role_type, :permissions, 
                    :is_active, :created_at, :updated_at)
        """), roles)
        
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
        
        # Create sample organization members
        members = []
        member_statuses = ['Active', 'Inactive', 'Pending', 'Suspended']
        
        for i in range(60):
            member = {
                'organization_id': random.randint(1, 5),  # Assuming 5 organizations exist
                'user_id': random.randint(1, 100),        # Assuming 100 users exist
                'role_id': random.randint(1, 15),         # Assuming 15 roles exist
                'member_status': random.choice(member_statuses),
                'join_date': datetime.now() - timedelta(days=random.randint(1, 1825)),  # Up to 5 years ago
                'is_active': random.choice([True, False]),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now()
            }
            members.append(member)
        
        # Insert members
        session.execute(text("""
            INSERT INTO organization_members (organization_id, user_id, role_id, member_status, 
                                            join_date, is_active, created_at, updated_at)
            VALUES (:organization_id, :user_id, :role_id, :member_status, 
                    :join_date, :is_active, :created_at, :updated_at)
        """), members)
        
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
        
        # Create sample organization collaborations
        collaborations = []
        collaboration_types = ['Partnership', 'Joint Project', 'Resource Sharing', 'Training']
        
        for i in range(25):
            collaboration = {
                'organization_id_1': random.randint(1, 5),  # Assuming 5 organizations exist
                'organization_id_2': random.randint(1, 5),  # Assuming 5 organizations exist
                'collaboration_type': random.choice(collaboration_types),
                'description': f"Description for collaboration {i+1}",
                'start_date': datetime.now() - timedelta(days=random.randint(1, 365)),
                'end_date': datetime.now() + timedelta(days=random.randint(1, 365)),
                'status': random.choice(['Active', 'Completed', 'Planned', 'On Hold']),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now()
            }
            collaborations.append(collaboration)
        
        # Insert collaborations
        session.execute(text("""
            INSERT INTO organization_collaborations (organization_id_1, organization_id_2, 
                                                   collaboration_type, description, start_date, 
                                                   end_date, status, created_at, updated_at)
            VALUES (:organization_id_1, :organization_id_2, :collaboration_type, :description, 
                    :start_date, :end_date, :status, :created_at, :updated_at)
        """), collaborations)
        
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
        
        # Create sample organization projects
        projects = []
        project_types = ['Research', 'Development', 'Implementation', 'Training', 'Assessment']
        project_statuses = ['Planning', 'Active', 'On Hold', 'Completed', 'Cancelled']
        
        for i in range(20):
            project = {
                'organization_id': random.randint(1, 5),  # Assuming 5 organizations exist
                'project_name': f"Project {i+1}",
                'description': f"Description for project {i+1}",
                'project_type': random.choice(project_types),
                'start_date': datetime.now() - timedelta(days=random.randint(1, 365)),
                'end_date': datetime.now() + timedelta(days=random.randint(1, 365)),
                'status': random.choice(project_statuses),
                'budget': random.randint(1000, 100000),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now()
            }
            projects.append(project)
        
        # Insert projects
        session.execute(text("""
            INSERT INTO organization_projects (organization_id, project_name, description, 
                                             project_type, start_date, end_date, status, 
                                             budget, created_at, updated_at)
            VALUES (:organization_id, :project_name, :description, :project_type, 
                    :start_date, :end_date, :status, :budget, :created_at, :updated_at)
        """), projects)
        
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
        
        # Create sample organization resources
        resources = []
        resource_types = ['Equipment', 'Software', 'Facilities', 'Materials', 'Personnel']
        
        for i in range(30):
            resource = {
                'organization_id': random.randint(1, 5),  # Assuming 5 organizations exist
                'resource_name': f"Resource {i+1}",
                'description': f"Description for resource {i+1}",
                'resource_type': random.choice(resource_types),
                'quantity': random.randint(1, 100),
                'unit_cost': random.randint(10, 1000),
                'is_available': random.choice([True, False]),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now()
            }
            resources.append(resource)
        
        # Insert resources
        session.execute(text("""
            INSERT INTO organization_resources (organization_id, resource_name, description, 
                                              resource_type, quantity, unit_cost, is_available, 
                                              created_at, updated_at)
            VALUES (:organization_id, :resource_name, :description, :resource_type, 
                    :quantity, :unit_cost, :is_available, :created_at, :updated_at)
        """), resources)
        
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
        
        # Create sample organization settings
        settings = []
        setting_types = ['General', 'Security', 'Notification', 'Integration', 'Custom']
        
        for i in range(12):
            setting = {
                'organization_id': random.randint(1, 5),  # Assuming 5 organizations exist
                'setting_key': f"setting_key_{i+1}",
                'setting_value': f"setting_value_{i+1}",
                'setting_type': random.choice(setting_types),
                'description': f"Description for setting {i+1}",
                'is_active': random.choice([True, False]),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now()
            }
            settings.append(setting)
        
        # Insert settings
        session.execute(text("""
            INSERT INTO organization_settings (organization_id, setting_key, setting_value, 
                                             setting_type, description, is_active, created_at, updated_at)
            VALUES (:organization_id, :setting_key, :setting_value, :setting_type, 
                    :description, :is_active, :created_at, :updated_at)
        """), settings)
        
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
        
        # Create sample organization feedback
        feedback_records = []
        feedback_types = ['Suggestion', 'Complaint', 'Compliment', 'Question', 'Report']
        
        for i in range(40):
            feedback = {
                'organization_id': random.randint(1, 5),  # Assuming 5 organizations exist
                'user_id': random.randint(1, 100),        # Assuming 100 users exist
                'feedback_type': random.choice(feedback_types),
                'title': f"Feedback {i+1}",
                'description': f"Description for feedback {i+1}",
                'rating': random.randint(1, 5),
                'is_resolved': random.choice([True, False]),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now()
            }
            feedback_records.append(feedback)
        
        # Insert feedback
        session.execute(text("""
            INSERT INTO organization_feedback (organization_id, user_id, feedback_type, title, 
                                             description, rating, is_resolved, created_at, updated_at)
            VALUES (:organization_id, :user_id, :feedback_type, :title, :description, 
                    :rating, :is_resolved, :created_at, :updated_at)
        """), feedback_records)
        
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
        team_types = ['Department', 'Project', 'Committee', 'Working Group', 'Advisory']
        
        for i in range(12):
            team = {
                'team_name': f"Team {i+1}",
                'description': f"Description for team {i+1}",
                'team_type': random.choice(team_types),
                'leader_id': random.randint(1, 50),  # Assuming 50 teachers exist
                'max_members': random.randint(5, 20),
                'is_active': random.choice([True, False]),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now()
            }
            teams.append(team)
        
        # Insert teams
        session.execute(text("""
            INSERT INTO teams (team_name, description, team_type, leader_id, max_members, 
                              is_active, created_at, updated_at)
            VALUES (:team_name, :description, :team_type, :leader_id, :max_members, 
                    :is_active, :created_at, :updated_at)
        """), teams)
        
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
        
        # Create sample team members
        members = []
        member_roles = ['Member', 'Senior Member', 'Lead', 'Coordinator', 'Contributor']
        
        for i in range(60):
            member = {
                'team_id': random.randint(1, 12),      # Assuming 12 teams exist
                'user_id': random.randint(1, 100),     # Assuming 100 users exist
                'role': random.choice(member_roles),
                'join_date': datetime.now() - timedelta(days=random.randint(1, 1825)),  # Up to 5 years ago
                'is_active': random.choice([True, False]),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now()
            }
            members.append(member)
        
        # Insert members
        session.execute(text("""
            INSERT INTO team_members (team_id, user_id, role, join_date, is_active, 
                                     created_at, updated_at)
            VALUES (:team_id, :user_id, :role, :join_date, :is_active, 
                    :created_at, :updated_at)
        """), members)
        
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