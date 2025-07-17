from datetime import datetime, timedelta
import random
from typing import List
from sqlalchemy.orm import Session
from app.models.activity import Activity
from app.models.physical_education.student.models import Student
from app.models.skill_assessment.assessment.assessment import SkillProgress
from app.models.physical_education.pe_enums.pe_types import (
    SkillLevel, ProgressType, ProgressStatus
)
from app.models.core.core_models import (
    DifficultyLevel, AssessmentType, AssessmentStatus,
    ActivityType, StudentType
)

def seed_skill_progress(session):
    """Seed the skill_progress table with initial data."""
    print("Seeding skill progress...")
    try:
        # Get the first two students from the database
        students = session.execute(Student.__table__.select().limit(2)).fetchall()
        
        if not students or len(students) < 2:
            print("Not enough students found. Skipping skill progress seeding.")
            return

        student1_id = students[0].id
        student2_id = students[1].id

        # Get activities by name
        activities = session.execute(
            Activity.__table__.select().where(
                Activity.__table__.c.name.in_([
                    'Jump Rope Basics',
                    'Basketball Dribbling',
                    'Soccer Passing',
                    'Dynamic Warm-up'
                ])
            )
        ).fetchall()

        if len(activities) < 4:
            print("Not all required activities found. Skipping skill progress seeding.")
            return

        # Create a mapping of activity names to IDs
        activity_map = {activity.name: activity.id for activity in activities}

        skill_progress = [
            {
                "student_id": student1_id,  # First student
                "activity_id": activity_map['Jump Rope Basics'],
                "skill_level": "intermediate",
                "progress_data": {
                    "rhythm_improvement": 0.15,
                    "form_improvement": 0.10,
                    "endurance_improvement": 0.20,
                    "technique_improvements": {
                        "basic_jumps": 0.05,
                        "alternating_foot": 0.25,
                        "double_unders": 0.30
                    }
                },
                "last_assessment_date": datetime.now() - timedelta(days=1),
                "next_assessment_date": datetime.now() + timedelta(days=30),
                "goals": {
                    "short_term": "Master double unders",
                    "long_term": "Achieve advanced jump rope combinations"
                }
            },
            {
                "student_id": student1_id,  # Same student
                "activity_id": activity_map['Basketball Dribbling'],
                "skill_level": "beginner",
                "progress_data": {
                    "ball_control_improvement": 0.12,
                    "speed_improvement": 0.15,
                    "hand_usage_improvements": {
                        "right_hand": 0.05,
                        "left_hand": 0.10
                    },
                    "technique_improvements": {
                        "stationary": 0.05,
                        "moving": 0.15,
                        "crossover": 0.20
                    }
                },
                "last_assessment_date": datetime.now() - timedelta(days=2),
                "next_assessment_date": datetime.now() + timedelta(days=28),
                "goals": {
                    "short_term": "Improve left hand dribbling",
                    "long_term": "Master crossover dribble"
                }
            },
            {
                "student_id": student2_id,  # Second student
                "activity_id": activity_map['Soccer Passing'],
                "skill_level": "beginner",
                "progress_data": {
                    "accuracy_improvement": 0.15,
                    "power_improvement": 0.20,
                    "technique_improvements": {
                        "short_pass": 0.10,
                        "long_pass": 0.25,
                        "receive": 0.15
                    }
                },
                "last_assessment_date": datetime.now() - timedelta(days=3),
                "next_assessment_date": datetime.now() + timedelta(days=27),
                "goals": {
                    "short_term": "Improve passing accuracy",
                    "long_term": "Master long-distance passing"
                }
            },
            {
                "student_id": student2_id,  # Same student
                "activity_id": activity_map['Dynamic Warm-up'],
                "skill_level": "intermediate",
                "progress_data": {
                    "form_improvement": 0.10,
                    "range_of_motion_improvement": 0.15,
                    "technique_improvements": {
                        "arm_circles": 0.05,
                        "leg_swings": 0.10,
                        "lunges": 0.15
                    }
                },
                "last_assessment_date": datetime.now() - timedelta(days=4),
                "next_assessment_date": datetime.now() + timedelta(days=26),
                "goals": {
                    "short_term": "Perfect form in all warm-up exercises",
                    "long_term": "Develop personalized warm-up routine"
                }
            }
        ]

        for progress_data in skill_progress:
            progress = SkillProgress(**progress_data)
            session.add(progress)

        session.flush()
        print("Skill progress seeded successfully!")
        
    except Exception as e:
        print(f"Error seeding skill progress: {e}")
        session.rollback()
        raise 