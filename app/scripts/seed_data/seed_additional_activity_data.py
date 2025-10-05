from datetime import datetime, timedelta
import random
import json
from typing import List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import select, text
from app.models.physical_education.activity.models import Activity
from app.models.physical_education.student.models import Student

def seed_additional_activity_data(session):
    """Seed additional activity-related data for empty tables."""
    print("  Seeding additional activity data...")
    
    # Get some activities and students
    activities = session.execute(select(Activity.id).limit(10)).fetchall()
    students = session.execute(select(Student.id).limit(20)).fetchall()
    
    if not activities or not students:
        print("    No activities or students found, skipping")
        return {"total": 0}
    
    activity_ids = [row[0] for row in activities]
    student_ids = [row[0] for row in students]
    
    total_records = {}
    
    # Seed activity performances (if table exists)
    try:
        from app.models.physical_education.activity.models import StudentActivityPerformance
        
        # Don't clear existing data - append instead
        # session.execute(StudentActivityPerformance.__table__.delete())
        
        # Create new activity performances
        for i in range(1000):
            performance = StudentActivityPerformance(
                student_id=random.choice(student_ids),
                activity_id=random.choice(activity_ids),
                performance_level=random.choice(["EXCELLENT", "GOOD", "SATISFACTORY", "NEEDS_IMPROVEMENT"]),
                score=random.uniform(60, 95),
                recorded_at=datetime.now() - timedelta(days=random.randint(1, 30)),
                notes=f"Additional performance record {i+1}"
            )
            session.add(performance)
        
        total_records["activity_performances"] = 1000
        print(f"    Created {1000} activity performances")
        
    except Exception as e:
        print(f"    Could not seed activity performances: {e}")
    
    # Seed activity assessments (if table exists)
    try:
        from app.models.physical_education.activity.models import ActivityAssessment
        from app.models.physical_education.pe_enums.pe_types import PerformanceLevel
        
        # Get users (teachers) for assessors
        try:
            users = session.execute(select("SELECT id FROM users LIMIT 20")).fetchall()
            user_ids = [u[0] for u in users] if users else [1]
        except:
            user_ids = [1]  # Default fallback
        
        # Don't clear existing data - append instead
        # session.execute(ActivityAssessment.__table__.delete())
        
        # Create new activity assessments
        for i in range(20):
            # Get random performance level and convert to uppercase string for database compatibility
            performance_level_enum = random.choice([PerformanceLevel.EXCELLENT, PerformanceLevel.GOOD, PerformanceLevel.SATISFACTORY, PerformanceLevel.NEEDS_IMPROVEMENT])
            performance_level_str = performance_level_enum.value.upper()
            
            assessment = ActivityAssessment(
                activity_id=random.choice(activity_ids),
                assessment_type=random.choice(["SKILL_EVALUATION", "SAFETY_ASSESSMENT", "PERFORMANCE_REVIEW", "PROGRESS_CHECK"]),
                assessment_date=datetime.now() - timedelta(days=random.randint(1, 30)),
                assessor_id=random.choice(user_ids),  # Using teachers as assessors
                performance_level=performance_level_str,  # Use the correct field name
                feedback=f"Additional assessment record {i+1}",
                recommendations=f"Recommendations for assessment {i+1}"
            )
            session.add(assessment)
        
        total_records["activity_assessments"] = 20
        print(f"    Created {20} activity assessments")
        
    except Exception as e:
        print(f"    Could not seed activity assessments: {e}")
    
    # Seed adapted activities (if table exists)
    try:
        from app.models.activity_adaptation.activity.activity import AdaptedActivity
        
        # Check if table exists and has data
        existing_count = session.execute(text("SELECT COUNT(*) FROM adapted_activities")).scalar()
        if existing_count > 0:
            print(f"    Adapted activities already exist ({existing_count} records), skipping...")
        else:
            # Create some adapted activities
            adapted_activities = []
            for i in range(50):  # Create 50 adapted activities
                adapted_activities.append({
                    'name': f'Adapted Activity {i+1}',
                    'description': f'Specialized activity adapted for students with specific needs {i+1}',
                    'activity_id': random.choice(activity_ids) if activity_ids else None,
                    'type': random.choice(['COORDINATION', 'BALANCE', 'FLEXIBILITY', 'STRETCHING', 'MOBILITY', 'STABILITY']),
                    'difficulty_level': random.choice(['BEGINNER', 'INTERMEDIATE', 'ADVANCED', 'EXPERT']),
                    'equipment_requirements': random.choice(['NONE', 'MINIMAL', 'STANDARD', 'SPECIALIZED', 'EXTENSIVE']),
                    'duration_minutes': random.randint(15, 60),
                    'instructions': json.dumps({'steps': [f'Step 1 for activity {i+1}', f'Step 2 for activity {i+1}']}),
                    'adaptations': json.dumps(['Wheelchair accessible', 'Visual aids available', 'Simplified movements']),
                    'activity_metadata': json.dumps({'target_audience': 'Special needs students', 'safety_level': 'High'}),
                    'status': 'ACTIVE',
                    'is_active': True,
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                    'updated_at': datetime.now()
                })
            
            # Insert adapted activities
            for activity_data in adapted_activities:
                session.execute(text("""
                    INSERT INTO adapted_activities 
                    (name, description, activity_id, type, difficulty_level, equipment_requirements, 
                     duration_minutes, instructions, adaptations, activity_metadata, status, is_active, created_at, updated_at)
                    VALUES (:name, :description, :activity_id, :type, :difficulty_level, :equipment_requirements, 
                            :duration_minutes, :instructions, :adaptations, :activity_metadata, :status, :is_active, :created_at, :updated_at)
                """), activity_data)
            
            session.commit()
            print(f"    Created {len(adapted_activities)} adapted activities")
            total_records["adapted_activities"] = len(adapted_activities)
        
    except Exception as e:
        print(f"    Could not seed adapted activities: {e}")
        total_records["adapted_activities"] = 0
    
    print(f"  Total additional activity records created: {total_records}")
    return total_records 