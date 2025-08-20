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
    
    # Create realistic activity plans for multiple students
    activity_plans = []
    
    # Get a sample of students for variety
    student_ids = list(students.values())
    
    # Create plans for a subset of students (about 50-100 plans)
    num_plans = min(75, len(student_ids) // 2)
    
    # Define plan templates for different activities
    plan_templates = [
        {
            "name": "Jump Rope Mastery Plan",
            "description": "A comprehensive plan to master jump rope techniques",
            "duration": 45,
            "difficulty": "intermediate",
            "objectives": {
                "primary": "Master basic and intermediate jump rope techniques",
                "secondary": ["Improve endurance", "Develop rhythm"]
            },
            "assessment_criteria": {
                "technique": ["Proper form", "Consistent rhythm"],
                "endurance": ["Duration", "Consistency"]
            }
        },
        {
            "name": "Basketball Fundamentals Plan",
            "description": "Develop core basketball skills",
            "duration": 60,
            "difficulty": "beginner",
            "objectives": {
                "primary": "Master dribbling and shooting techniques",
                "secondary": ["Improve ball control", "Develop accuracy"]
            },
            "assessment_criteria": {
                "dribbling": ["Control", "Speed"],
                "shooting": ["Accuracy", "Form"]
            }
        },
        {
            "name": "Soccer Skills Development",
            "description": "Build foundational soccer abilities",
            "duration": 50,
            "difficulty": "beginner",
            "objectives": {
                "primary": "Master passing and dribbling",
                "secondary": ["Improve coordination", "Build stamina"]
            },
            "assessment_criteria": {
                "passing": ["Accuracy", "Power"],
                "dribbling": ["Control", "Speed"]
            }
        },
        {
            "name": "Fitness Foundation Plan",
            "description": "Establish basic fitness and strength",
            "duration": 40,
            "difficulty": "beginner",
            "objectives": {
                "primary": "Build core strength and endurance",
                "secondary": ["Improve flexibility", "Develop coordination"]
            },
            "assessment_criteria": {
                "strength": ["Repetitions", "Form"],
                "endurance": ["Duration", "Consistency"]
            }
        }
    ]
    
    for _ in range(num_plans):
        # Randomly select student and plan template
        student_id = random.choice(student_ids)
        template = random.choice(plan_templates)
        
        # Generate grade level (K-12)
        grade_levels = ["K", "1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th", "9th", "10th", "11th", "12th"]
        grade_level = random.choice(grade_levels)
        
        # Random duration variation
        duration = template["duration"] + random.randint(-10, 10)
        duration = max(30, min(90, duration))  # Keep between 30-90 minutes
        
        # Random difficulty
        difficulties = ["beginner", "intermediate", "advanced"]
        difficulty = random.choice(difficulties)
        
        # Random dates
        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=random.randint(14, 60))
        
        plan_data = {
            "name": template["name"],
            "description": template["description"],
            "student_id": student_id,
            "grade_level": grade_level,
            "duration": duration,
            "difficulty": difficulty,
            "plan_metadata": {
                "objectives": template["objectives"],
                "assessment_criteria": template["assessment_criteria"],
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "status": "active"
            }
        }
        
        activity_plans.append(plan_data)
    
    # Create plan activities
    plan_activities = []
    
    for plan_data in activity_plans:
        plan = ActivityPlan(**plan_data)
        session.add(plan)
        session.flush()  # Get the plan ID
        
        # Add activities to the plan based on plan type
        if "Jump Rope" in plan.name:
            # Add jump rope activities
            plan_activities.extend([
                {
                    "plan_id": plan.id,
                    "activity_id": activities.get("Jump Rope Basics", list(activities.values())[0]),
                    "sequence": 1,
                    "duration": 20,
                    "activity_metadata": {
                        "scheduled_date": (datetime.now() + timedelta(days=7)).date().isoformat(),
                        "status": "scheduled"
                    }
                },
                {
                    "plan_id": plan.id,
                    "activity_id": activities.get("Advanced Jump Rope", list(activities.values())[0]),
                    "sequence": 2,
                    "duration": 25,
                    "activity_metadata": {
                        "scheduled_date": (datetime.now() + timedelta(days=14)).date().isoformat(),
                        "status": "scheduled"
                    }
                }
            ])
        elif "Basketball" in plan.name:
            # Add basketball activities
            plan_activities.extend([
                {
                    "plan_id": plan.id,
                    "activity_id": activities.get("Basketball Dribbling", list(activities.values())[0]),
                    "sequence": 1,
                    "duration": 30,
                    "activity_metadata": {
                        "scheduled_date": (datetime.now() + timedelta(days=7)).date().isoformat(),
                        "status": "scheduled"
                    }
                },
                {
                    "plan_id": plan.id,
                    "activity_id": activities.get("Basketball Game", list(activities.values())[0]),
                    "sequence": 2,
                    "duration": 30,
                    "activity_metadata": {
                        "scheduled_date": (datetime.now() + timedelta(days=14)).date().isoformat(),
                        "status": "scheduled"
                    }
                }
            ])
        elif "Soccer" in plan.name:
            # Add soccer activities
            plan_activities.extend([
                {
                    "plan_id": plan.id,
                    "activity_id": activities.get("Soccer Passing", list(activities.values())[0]),
                    "sequence": 1,
                    "duration": 25,
                    "activity_metadata": {
                        "scheduled_date": (datetime.now() + timedelta(days=7)).date().isoformat(),
                        "status": "scheduled"
                    }
                },
                {
                    "plan_id": plan.id,
                    "activity_id": activities.get("Soccer Scrimmage", list(activities.values())[0]),
                    "sequence": 2,
                    "duration": 25,
                    "activity_metadata": {
                        "scheduled_date": (datetime.now() + timedelta(days=14)).date().isoformat(),
                        "status": "scheduled"
                    }
                }
            ])
        else:
            # Add general fitness activities for other plans
            available_activities = list(activities.values())
            plan_activities.extend([
                {
                    "plan_id": plan.id,
                    "activity_id": random.choice(available_activities),
                    "sequence": 1,
                    "duration": 25,
                    "activity_metadata": {
                        "scheduled_date": (datetime.now() + timedelta(days=7)).date().isoformat(),
                        "status": "scheduled"
                    }
                },
                {
                    "plan_id": plan.id,
                    "activity_id": random.choice(available_activities),
                    "sequence": 2,
                    "duration": 25,
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