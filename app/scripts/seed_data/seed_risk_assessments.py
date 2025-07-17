from datetime import datetime, timedelta
import random
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.physical_education.safety import RiskAssessment
from app.models.activity import Activity
from app.models.physical_education.class_ import PhysicalEducationClass
from app.models.core.user import User
from app.models.physical_education.pe_enums.pe_types import (
    RiskType,
    RiskLevel,
    RiskStatus,
    RiskTrigger,
    ActivityType,
    ClassType
)

def seed_risk_assessments(session):
    """Seed the risk_assessments table with initial data."""
    # First, get the activity IDs by name
    activity_names = ["Jump Rope Basics", "Basketball Dribbling", "Soccer Passing", "Dynamic Warm-up"]
    activities = {}
    
    for name in activity_names:
        result = session.execute(select(Activity).where(Activity.name == name))
        activity = result.scalar_one_or_none()
        if activity:
            activities[name] = activity.id
        else:
            print(f"Warning: Activity '{name}' not found in database")

    # Get the class IDs by specific class IDs (501, 502, 601, 602)
    class_ids = [501, 502, 601, 602]  # Using integers
    classes = {}
    
    for class_id in class_ids:
        result = session.execute(select(PhysicalEducationClass).where(PhysicalEducationClass.id == class_id)).unique()
        class_ = result.scalar_one_or_none()
        if class_:
            classes[str(class_id)] = class_.id  # Store the actual database ID
        else:
            print(f"Warning: Class with ID '{class_id}' not found in database")

    # Create risk assessments
    risk_assessments = []
    
    # Get a teacher user for the assessed_by field
    teacher_result = session.execute(select(User).where(User.role == "teacher")).unique()
    teacher = teacher_result.scalar()
    if not teacher:
        print("Warning: No teacher found for risk assessments")
        return
    
    if "501" in classes and "Jump Rope Basics" in activities:
        risk_assessments.append({
            "class_id": classes["501"],  # Using the actual database ID
            "activity_id": activities["Jump Rope Basics"],
            "activity_type": "Jump Rope",
            "environment": "indoor",
            "assessment_date": datetime.now() - timedelta(days=1),
            "assessed_by": teacher.id,
            "risk_level": RiskLevel.LOW,
            "environmental_risks": ["floor surface", "space"],
            "student_risks": ["coordination", "fatigue"],
            "activity_risks": ["rope length", "speed"],
            "mitigation_strategies": [
                "Check floor condition",
                "Ensure adequate space",
                "Proper warm-up",
                "Regular breaks",
                "Adjust rope length",
                "Monitor speed"
            ],
            "mitigation_plan": "Comprehensive safety plan for jump rope activities",
            "follow_up_date": datetime.now() + timedelta(days=7)
        })
    
    if "601" in classes and "Basketball Dribbling" in activities:
        risk_assessments.append({
            "class_id": classes["601"],  # Using the actual database ID
            "activity_id": activities["Basketball Dribbling"],
            "activity_type": "Basketball",
            "environment": "indoor",
            "assessment_date": datetime.now() - timedelta(days=2),
            "assessed_by": teacher.id,
            "risk_level": RiskLevel.LOW,
            "environmental_risks": ["court condition", "lighting"],
            "student_risks": ["ball control", "collisions"],
            "activity_risks": ["ball pressure", "spacing"],
            "mitigation_strategies": [
                "Check court condition",
                "Ensure proper lighting",
                "Teach ball control",
                "Maintain spacing",
                "Check equipment",
                "Clear instructions"
            ],
            "mitigation_plan": "Comprehensive safety plan for basketball activities",
            "follow_up_date": datetime.now() + timedelta(days=7)
        })
    
    if "502" in classes and "Soccer Passing" in activities:
        risk_assessments.append({
            "class_id": classes["502"],  # Using the actual database ID
            "activity_id": activities["Soccer Passing"],
            "activity_type": "Soccer Passing",
            "environment": "outdoor",
            "assessment_date": datetime.now() - timedelta(days=3),
            "assessed_by": teacher.id,
            "risk_level": RiskLevel.MEDIUM,
            "environmental_risks": ["field condition", "weather"],
            "student_risks": ["passing technique", "spacing"],
            "activity_risks": ["ball pressure", "goal posts"],
            "mitigation_strategies": [
                "Check field condition",
                "Monitor weather",
                "Teach proper technique",
                "Maintain safe spacing",
                "Check ball pressure",
                "Secure goal posts"
            ],
            "mitigation_plan": "Comprehensive safety plan for soccer activities",
            "follow_up_date": datetime.now() + timedelta(days=7)
        })
    
    if "602" in classes and "Dynamic Warm-up" in activities:
        risk_assessments.append({
            "class_id": classes["602"],  # Using the actual database ID
            "activity_id": activities["Dynamic Warm-up"],
            "activity_type": "Dynamic Warm-up",
            "environment": "indoor",
            "assessment_date": datetime.now() - timedelta(days=4),
            "assessed_by": teacher.id,
            "risk_level": RiskLevel.LOW,
            "environmental_risks": ["floor surface", "room temperature"],
            "student_risks": ["form", "range of motion"],
            "activity_risks": ["mats", "space"],
            "mitigation_strategies": [
                "Check floor condition",
                "Maintain comfortable temperature",
                "Demonstrate proper form",
                "Monitor range of motion",
                "Provide mats",
                "Ensure adequate space"
            ],
            "mitigation_plan": "Comprehensive safety plan for warm-up activities",
            "follow_up_date": datetime.now() + timedelta(days=7)
        })

    # Add risk assessments to session
    for assessment_data in risk_assessments:
        assessment = RiskAssessment(**assessment_data)
        session.add(assessment)

    session.flush()
    print("Risk assessments seeded successfully!") 