from datetime import datetime, timedelta
import random
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select, text
from app.models.physical_education.activity.models import (
    Activity,
    StudentActivityPerformance,
    StudentActivityPreference,
    ActivityAssessment,
    ActivityProgression
)
from app.models.physical_education.student.models import Student
from app.models.physical_education.pe_enums.pe_types import (
    PerformanceLevel,
    ProgressionLevel
)

def seed_student_activity_data(session):
    """Seed the student activity performances and preferences tables with initial data."""
    print("  Starting comprehensive student activity data seeding...")
    
    # First, get the actual student IDs from the database
    result = session.execute(select(Student.id))
    student_ids = [row[0] for row in result.fetchall()]
    
    if not student_ids:
        print("No students found in the database. Please seed students first.")
        return

    # Get the actual activity IDs from the database
    result = session.execute(select(Activity.id))
    activity_ids = [row[0] for row in result.fetchall()]
    
    if not activity_ids:
        print("No activities found in the database. Please seed activities first.")
        return

    print(f"    Found {len(student_ids)} students and {len(activity_ids)} activities")

    # Seed student activity performances
    activity_performances = [
        {
            "student_id": student_ids[0],  # First student
            "activity_id": activity_ids[0],  # First activity
            "performance_level": "EXCELLENT",  # Converted to uppercase string for database compatibility
            "score": 0.85,
            "recorded_at": datetime.now() - timedelta(days=1),
            "notes": "Good performance with room for improvement in technique"
        },
        {
            "student_id": student_ids[0],  # First student
            "activity_id": activity_ids[1],  # Second activity
            "performance_level": "EXCELLENT",  # Converted to uppercase string for database compatibility
            "score": 0.90,
            "recorded_at": datetime.now() - timedelta(days=2),
            "notes": "Excellent performance, showing good progress"
        },
        {
            "student_id": student_ids[1],  # Second student
            "activity_id": activity_ids[0],  # First activity
            "performance_level": "SATISFACTORY",  # Converted to uppercase string for database compatibility
            "score": 0.75,
            "recorded_at": datetime.now() - timedelta(days=1),
            "notes": "Needs more practice with basic movements"
        },
        {
            "student_id": student_ids[1],  # Second student
            "activity_id": activity_ids[1],  # Second activity
            "performance_level": "GOOD",  # Converted to uppercase string for database compatibility
            "score": 0.80,
            "recorded_at": datetime.now() - timedelta(days=2),
            "notes": "Showing improvement in coordination"
        }
    ]

    for performance_data in activity_performances:
        performance = StudentActivityPerformance(**performance_data)
        session.add(performance)

    # Seed student activity preferences
    activity_preferences = [
        {
            "student_id": student_ids[0],  # First student
            "activity_id": activity_ids[0],  # First activity
            "preference_level": 4,
            "preference_score": 0.85,
            "last_updated": datetime.now() - timedelta(days=1)
        },
        {
            "student_id": student_ids[0],  # First student
            "activity_id": activity_ids[1],  # Second activity
            "preference_level": 5,
            "preference_score": 0.90,
            "last_updated": datetime.now() - timedelta(days=1)
        },
        {
            "student_id": student_ids[1],  # Second student
            "activity_id": activity_ids[0],  # First activity
            "preference_level": 3,
            "preference_score": 0.75,
            "last_updated": datetime.now() - timedelta(days=2)
        },
        {
            "student_id": student_ids[1],  # Second student
            "activity_id": activity_ids[1],  # Second activity
            "preference_level": 4,
            "preference_score": 0.80,
            "last_updated": datetime.now() - timedelta(days=2)
        }
    ]

    for preference_data in activity_preferences:
        preference = StudentActivityPreference(**preference_data)
        session.add(preference)

    # ADDITIONAL: Create comprehensive student activity performances for more data
    print("  Creating additional comprehensive activity performances...")
    additional_performances = []
    
    # Create 1000+ additional performance records (100 students × 10+ activities)
    num_students = min(100, len(student_ids))
    num_activities = min(10, len(activity_ids))
    
    for i in range(num_students):
        for j in range(num_activities):
            # Create multiple performance records per student-activity pair
            for performance_idx in range(random.randint(1, 3)):  # 1-3 performances per pair
                additional_performance = StudentActivityPerformance(
                    student_id=student_ids[i],
                    activity_id=activity_ids[j],
                    performance_level=random.choice(["EXCELLENT", "GOOD", "SATISFACTORY", "NEEDS_IMPROVEMENT"]),
                    score=random.uniform(60, 100),
                    completion_time=random.randint(15, 60),
                    attempts=random.randint(1, 5),
                    recorded_at=datetime.now() - timedelta(days=random.randint(1, 90)),
                    notes=f"Additional performance record {performance_idx + 1} for student {i+1} in activity {j+1}",
                    feedback={"teacher_notes": f"Good effort, keep practicing", "peer_feedback": "Great teamwork!"},
                    performance_metadata={"location": "gym", "weather": "indoor", "equipment_used": "standard"}
                )
                session.add(additional_performance)
                additional_performances.append(additional_performance)
                
                # Flush every 100 records to manage memory
                if len(additional_performances) % 100 == 0:
                    session.flush()
                    print(f"    Created {len(additional_performances)} additional performance records...")
    
    session.flush()
    print(f"  Created {len(additional_performances)} additional comprehensive performance records")

    # ADDITIONAL: Create comprehensive student activity preferences for more data
    print("  Creating additional comprehensive activity preferences...")
    additional_preferences = []
    
    # Create 1000+ additional preference records (100 students × 10+ activities)
    for i in range(num_students):
        for j in range(num_activities):
            additional_preference = StudentActivityPreference(
                student_id=student_ids[i],
                activity_id=activity_ids[j],
                preference_level=random.randint(1, 5),  # 1-5 scale
                preference_score=random.uniform(0.3, 1.0),  # 0.3-1.0 score
                last_updated=datetime.now() - timedelta(days=random.randint(1, 30)),
                notes=f"Additional preference record for student {i+1} in activity {j+1}",
                preference_metadata={"reason": random.choice(["enjoyment", "skill_level", "social_aspect", "challenge"]), "frequency": random.randint(1, 5)}
            )
            session.add(additional_preference)
            additional_preferences.append(additional_preference)
            
            # Flush every 100 records to manage memory
            if len(additional_preferences) % 100 == 0:
                session.flush()
                print(f"    Created {len(additional_preferences)} additional preference records...")
    
    session.flush()
    print(f"  Created {len(additional_preferences)} additional comprehensive preference records")

    # ADDITIONAL: Create comprehensive activity assessments
    print("  Creating comprehensive activity assessments...")
    activity_assessments = []
    
    # Get users (teachers) for assessors
    try:
        users = session.execute(text("SELECT id FROM users LIMIT 50")).fetchall()
        user_ids = [u[0] for u in users] if users else [1]
    except:
        user_ids = [1]  # Default fallback
    
    # Create 500+ activity assessments (50 activities × 10+ assessors)
    num_assessors = min(10, len(user_ids))  # Using teachers as assessors
    
    for i in range(min(50, len(activity_ids))):
        for j in range(num_assessors):
            # Get random performance level and convert to uppercase string for database compatibility
            performance_level_enum = random.choice([PerformanceLevel.EXCELLENT, PerformanceLevel.GOOD, PerformanceLevel.SATISFACTORY, PerformanceLevel.NEEDS_IMPROVEMENT, PerformanceLevel.POOR])
            performance_level_str = performance_level_enum.value.upper()
            
            assessment = ActivityAssessment(
                activity_id=activity_ids[i],
                assessment_type=random.choice(["SKILL_EVALUATION", "SAFETY_ASSESSMENT", "PERFORMANCE_REVIEW", "PROGRESS_CHECK"]),
                assessment_date=datetime.now() - timedelta(days=random.randint(1, 180)),
                assessor_id=user_ids[j],  # Using teachers as assessors
                performance_level=performance_level_str, # Fixed enum usage with uppercase conversion
                feedback=f"Comprehensive assessment for activity {i+1} by assessor {j+1}",
                recommendations=f"Focus on improving technique and consistency for activity {i+1}"
            )
            session.add(assessment)
            activity_assessments.append(assessment)
            
            if len(activity_assessments) % 100 == 0:
                session.flush()
                print(f"    Created {len(activity_assessments)} activity assessments...")
    
    session.flush()
    print(f"  Created {len(activity_assessments)} comprehensive activity assessments")

    # ADDITIONAL: Create comprehensive activity progressions
    print("  Creating comprehensive activity progressions...")
    activity_progressions = []
    
    # Create 500+ activity progressions (50 students × 10+ activities)
    for i in range(min(50, len(student_ids))):
        for j in range(min(10, len(activity_ids))):
            # Get random progression levels and convert to lowercase strings for database compatibility
            level_enum = random.choice([ProgressionLevel.NOVICE, ProgressionLevel.DEVELOPING, ProgressionLevel.PROFICIENT, ProgressionLevel.ADVANCED, ProgressionLevel.EXPERT])
            current_level_enum = random.choice([ProgressionLevel.NOVICE, ProgressionLevel.DEVELOPING, ProgressionLevel.PROFICIENT, ProgressionLevel.ADVANCED, ProgressionLevel.EXPERT])
            level_str = level_enum.value  # ProgressionLevel uses lowercase values
            current_level_str = current_level_enum.value  # ProgressionLevel uses lowercase values
            
            progression = ActivityProgression(
                activity_id=activity_ids[j],
                student_id=student_ids[i],
                level=level_str,  # Fixed enum usage with lowercase conversion
                current_level=current_level_str,  # Fixed enum usage with lowercase conversion
                requirements=f"Student {i+1} must demonstrate mastery of basic skills for activity {j+1}",
                improvement_rate=random.uniform(0.1, 0.9),
                last_assessment_date=datetime.now() - timedelta(days=random.randint(1, 30)),
                next_assessment_date=datetime.now() + timedelta(days=random.randint(7, 90)),
                progression_metadata={"focus_areas": ["technique", "endurance", "coordination"], "goals": ["improve accuracy", "increase speed"]}
            )
            session.add(progression)
            activity_progressions.append(progression)
            
            if len(activity_progressions) % 100 == 0:
                session.flush()
                print(f"    Created {len(activity_progressions)} activity progressions...")
    
    session.flush()
    print(f"  Created {len(activity_progressions)} comprehensive activity progressions")

    session.flush()
    print("Student activity performances and preferences seeded successfully!")
    
    # Return count of created records
    performance_count = len(activity_performances) + len(additional_performances)
    preference_count = len(activity_preferences) + len(additional_preferences)
    assessment_count = len(activity_assessments)
    progression_count = len(activity_progressions)
    
    print(f"    Total records created:")
    print(f"      - Activity Performances: {performance_count}")
    print(f"      - Activity Preferences: {preference_count}")
    print(f"      - Activity Assessments: {assessment_count}")
    print(f"      - Activity Progressions: {progression_count}")
    
    return performance_count, preference_count, assessment_count, progression_count