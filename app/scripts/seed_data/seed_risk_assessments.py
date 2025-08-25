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

    # Get actual classes from the database dynamically
    from sqlalchemy import text
    class_result = session.execute(text("SELECT id, name, grade_level FROM physical_education_classes LIMIT 10"))
    classes = {}
    
    for class_row in class_result:
        class_id = class_row.id
        class_name = class_row.name
        grade_level = class_row.grade_level
        classes[str(class_id)] = {
            'id': class_id,
            'name': class_name,
            'grade_level': grade_level
        }
    
    if not classes:
        print("Warning: No classes found in database")
        return
    
    print(f"Found {len(classes)} classes for risk assessments")

    # Create risk assessments
    risk_assessments = []
    
    # Get a teacher user for the assessed_by field
    teacher_result = session.execute(select(User).where(User.role == "teacher")).unique()
    teacher = teacher_result.scalar()
    if not teacher:
        print("Warning: No teacher found for risk assessments")
        return
    
    # Create risk assessments for available classes and activities
    for class_key, class_info in classes.items():
        if "Jump Rope Basics" in activities:
            risk_assessments.append({
                "class_id": class_info['id'],
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
            break  # Only create one jump rope assessment
        
        if "Basketball Dribbling" in activities:
            risk_assessments.append({
                "class_id": class_info['id'],
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
            break  # Only create one basketball assessment
    
    # Create additional risk assessments for other activities
    for class_key, class_info in classes.items():
        if "Soccer Passing" in activities and len(risk_assessments) < 2:
            risk_assessments.append({
                "class_id": class_info['id'],
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
            break
        
        if "Dynamic Warm-up" in activities and len(risk_assessments) < 3:
            risk_assessments.append({
                "class_id": class_info['id'],
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
            break

    # Add risk assessments to session
    for assessment_data in risk_assessments:
        assessment = RiskAssessment(**assessment_data)
        session.add(assessment)

    session.flush()
    print("Risk assessments seeded successfully!") 