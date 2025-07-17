"""Seed data for activity plans and plan activities."""
from datetime import datetime, timedelta
import random
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from sqlalchemy.orm import Session
from app.models.activity import Activity
from app.models.student import Student
from app.models.physical_education.class_ import PhysicalEducationClass
from app.models.core.core_models import (
    ActivityType,
    DifficultyLevel,
    EquipmentRequirement,
    SafetyType,
    AssessmentType
)
from app.models.physical_education.activity_plan.models import ActivityPlan, ActivityPlanActivity

async def seed_activity_plans(session: AsyncSession) -> None:
    """Seed activity plans and plan activities data."""
    print("Seeding activity plans...")
    
    # Delete existing records
    await session.execute(text("DELETE FROM activity_plan_activities"))
    await session.execute(text("DELETE FROM activity_plans"))
    await session.commit()
    
    # Get all students and classes
    result = await session.execute(select(Student.id, Student.first_name, Student.last_name))
    students = {f"{row.first_name} {row.last_name}": row.id for row in result.fetchall()}
    
    result = await session.execute(select(PhysicalEducationClass.id, PhysicalEducationClass.name))
    classes = {row.name: row.id for row in result.fetchall()}
    
    # Get all activities
    result = await session.execute(select(Activity.id, Activity.name))
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
            "class_id": 501,  # Using integer ID for Grade 5 Physical Education
            "start_date": datetime.now().date(),
            "end_date": (datetime.now() + timedelta(days=30)).date(),
            "status": "active",
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
            "student_id": students["Emily Johnson"],
            "class_id": 601,  # Using integer ID for Grade 6 Physical Education
            "start_date": datetime.now().date(),
            "end_date": (datetime.now() + timedelta(days=45)).date(),
            "status": "active",
            "objectives": {
                "primary": "Master dribbling and shooting techniques",
                "secondary": ["Improve ball control", "Develop accuracy"]
            },
            "assessment_criteria": {
                "dribbling": ["Control", "Speed"],
                "shooting": ["Accuracy", "Form"]
            }
        }
    ]
    
    # Create plan activities
    plan_activities = []
    
    for plan_data in activity_plans:
        plan = ActivityPlan(**plan_data)
        session.add(plan)
        await session.flush()  # Get the plan ID
        
        # Add activities to the plan
        if plan.name == "Jump Rope Mastery Plan":
            plan_activities.extend([
                {
                    "plan_id": plan.id,
                    "activity_id": activities["Jump Rope Basics"],
                    "scheduled_date": plan.start_date + timedelta(days=7),
                    "status": "scheduled"
                },
                {
                    "plan_id": plan.id,
                    "activity_id": activities["Advanced Jump Rope"],
                    "scheduled_date": plan.start_date + timedelta(days=14),
                    "status": "scheduled"
                }
            ])
        elif plan.name == "Basketball Fundamentals Plan":
            plan_activities.extend([
                {
                    "plan_id": plan.id,
                    "activity_id": activities["Basketball Dribbling"],
                    "scheduled_date": plan.start_date + timedelta(days=7),
                    "status": "scheduled"
                },
                {
                    "plan_id": plan.id,
                    "activity_id": activities["Basketball Game"],
                    "scheduled_date": plan.start_date + timedelta(days=14),
                    "status": "scheduled"
                }
            ])
    
    # Add all plan activities
    for activity_data in plan_activities:
        plan_activity = ActivityPlanActivity(**activity_data)
        session.add(plan_activity)
    
    await session.commit()
    print("Activity plans and plan activities seeded successfully!") 