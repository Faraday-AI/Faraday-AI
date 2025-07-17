"""Seed data for activity plans and plan activities."""
from datetime import datetime, timedelta
import random
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select, text
from app.models.activity import Activity
from app.models.physical_education.student.models import Student
from app.models.physical_education.class_ import PhysicalEducationClass
from app.models.core.core_models import (
    ActivityType,
    DifficultyLevel,
    EquipmentRequirement,
    SafetyType,
    AssessmentType
)
from app.models.physical_education.activity_plan.models import ActivityPlan, ActivityPlanActivity

def seed_activity_plans(session: Session) -> None:
    """Seed activity plans and plan activities data."""
    print("Seeding activity plans...")
    
    # Delete existing records
    session.execute(text("DELETE FROM activity_plan_activities"))
    session.execute(text("DELETE FROM activity_plans"))
    session.commit()
    
    # Get all students and classes
    result = session.execute(select(Student.id, Student.first_name, Student.last_name))
    students = {f"{row.first_name} {row.last_name}": row.id for row in result.fetchall()}
    
    result = session.execute(select(PhysicalEducationClass.id, PhysicalEducationClass.name))
    classes = {row.name: row.id for row in result.fetchall()}
    
    # Get all activities
    result = session.execute(select(Activity.id, Activity.name))
    activities = {row.name: row.id for row in result.fetchall()}
    
    if not students or not classes or not activities:
        print("Missing required data. Please seed students, classes, and activities first.")
        return
    
    # Create activity plans
    activity_plans = [
        {
            "name": "Jump Rope Mastery Plan",
            "description": "A comprehensive plan to master jump rope techniques",
            "student_id": students["John Smith"],
            "grade_level": "5th",
            "duration": 45,
            "difficulty": "intermediate",
            "plan_metadata": {
                "objectives": {
                    "primary": "Master basic and intermediate jump rope techniques",
                    "secondary": ["Improve endurance", "Develop rhythm"]
                },
                "assessment_criteria": {
                    "technique": ["Proper form", "Consistent rhythm"],
                    "endurance": ["Duration", "Consistency"]
                },
                "start_date": datetime.now().date().isoformat(),
                "end_date": (datetime.now() + timedelta(days=30)).date().isoformat(),
                "status": "active"
            }
        },
        {
            "name": "Basketball Fundamentals Plan",
            "description": "Develop core basketball skills",
            "student_id": students["Emily Johnson"],
            "grade_level": "6th",
            "duration": 60,
            "difficulty": "beginner",
            "plan_metadata": {
                "objectives": {
                    "primary": "Master dribbling and shooting techniques",
                    "secondary": ["Improve ball control", "Develop accuracy"]
                },
                "assessment_criteria": {
                    "dribbling": ["Control", "Speed"],
                    "shooting": ["Accuracy", "Form"]
                },
                "start_date": datetime.now().date().isoformat(),
                "end_date": (datetime.now() + timedelta(days=45)).date().isoformat(),
                "status": "active"
            }
        }
    ]
    
    # Create plan activities
    plan_activities = []
    
    for plan_data in activity_plans:
        plan = ActivityPlan(**plan_data)
        session.add(plan)
        session.flush()  # Get the plan ID
        
        # Add activities to the plan
        if plan.name == "Jump Rope Mastery Plan":
            plan_activities.extend([
                {
                    "plan_id": plan.id,
                    "activity_id": activities["Jump Rope Basics"],
                    "sequence": 1,
                    "duration": 20,
                    "activity_metadata": {
                        "scheduled_date": (datetime.now() + timedelta(days=7)).date().isoformat(),
                        "status": "scheduled"
                    }
                },
                {
                    "plan_id": plan.id,
                    "activity_id": activities["Advanced Jump Rope"],
                    "sequence": 2,
                    "duration": 25,
                    "activity_metadata": {
                        "scheduled_date": (datetime.now() + timedelta(days=14)).date().isoformat(),
                        "status": "scheduled"
                    }
                }
            ])
        elif plan.name == "Basketball Fundamentals Plan":
            plan_activities.extend([
                {
                    "plan_id": plan.id,
                    "activity_id": activities["Basketball Dribbling"],
                    "sequence": 1,
                    "duration": 30,
                    "activity_metadata": {
                        "scheduled_date": (datetime.now() + timedelta(days=7)).date().isoformat(),
                        "status": "scheduled"
                    }
                },
                {
                    "plan_id": plan.id,
                    "activity_id": activities["Basketball Game"],
                    "sequence": 2,
                    "duration": 30,
                    "activity_metadata": {
                        "scheduled_date": (datetime.now() + timedelta(days=14)).date().isoformat(),
                        "status": "scheduled"
                    }
                }
            ])
    
    # Add all plan activities
    for activity_data in plan_activities:
        plan_activity = ActivityPlanActivity(**activity_data)
        session.add(plan_activity)
    
    session.commit()
    print("Activity plans and plan activities seeded successfully!") 