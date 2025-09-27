from datetime import datetime, timedelta
import random
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.physical_education.safety import SafetyIncident
from app.models.physical_education.pe_enums.pe_types import (
    IncidentType,
    IncidentLevel,
    IncidentStatus,
    IncidentTrigger
)

def seed_safety_incidents(session):
    """Seed the safety_incidents table with initial data."""
    # First, get the actual activity IDs from the database
    result = session.execute(text("SELECT id, name FROM activities ORDER BY name"))
    activities = {row.name: row.id for row in result.fetchall()}
    
    # Get the actual student IDs from the database
    result = session.execute(text("SELECT id, first_name, last_name FROM students ORDER BY id"))
    students = {f"{row.first_name} {row.last_name}": row.id for row in result.fetchall()}
    
    # Get a teacher for the teacher_id field
    result = session.execute(text("SELECT id FROM users WHERE role = 'teacher' LIMIT 1"))
    teacher = result.fetchone()
    if not teacher:
        print("Warning: No teacher found for safety incidents")
        return
    teacher_id = teacher[0]
    
    # Generate realistic safety incidents for multiple students
    safety_incidents = []
    
    # Get a sample of students and activities for variety
    student_ids = list(students.values())
    activity_names = list(activities.keys())
    
    # Create incidents for a realistic district level (1 per 20 students)
    num_incidents = max(200, len(student_ids) // 20)
    
    # Define incident templates
    incident_templates = [
        {
            "incident_type": "injury",
            "severity": "low",
            "description": "Twisted ankle during {activity}",
            "action_taken": "Applied ice and provided rest",
            "preventive_measures": "Added proper landing technique training"
        },
        {
            "incident_type": "near_miss",
            "severity": "low",
            "description": "Almost collided with another student during {activity}",
            "action_taken": "Reorganized drill spacing",
            "preventive_measures": "Added visual markers for personal space"
        },
        {
            "incident_type": "equipment_failure",
            "severity": "low",
            "description": "Equipment issue during {activity}",
            "action_taken": "Replaced equipment with properly maintained version",
            "preventive_measures": "Added equipment check before each session"
        },
        {
            "incident_type": "behavioral_issue",
            "severity": "low",
            "description": "Student performing {activity} with improper form",
            "action_taken": "Provided immediate form correction",
            "preventive_measures": "Added more detailed form demonstration"
        },
        {
            "incident_type": "environmental",
            "severity": "low",
            "description": "Wet floor conditions during {activity}",
            "action_taken": "Immediately stopped activity and dried floor",
            "preventive_measures": "Added floor condition check before activities"
        }
    ]
    
    for _ in range(num_incidents):
        # Randomly select student and activity
        student_id = random.choice(student_ids)
        activity_name = random.choice(activity_names)
        activity_id = activities[activity_name]
        
        # Randomly select incident template
        template = random.choice(incident_templates)
        
        # Random date within last 30 days
        incident_date = datetime.now() - timedelta(days=random.randint(1, 30))
        
        # Random severity (mostly low, some medium)
        severity = random.choice(["low", "low", "low", "medium"])
        
        # Generate description and action based on template
        description = template["description"].format(activity=activity_name.lower())
        action_taken = template["action_taken"]
        preventive_measures = template["preventive_measures"]
        
        incident_data = {
            "student_id": student_id,
            "activity_id": activity_id,
            "incident_date": incident_date,
            "teacher_id": teacher_id,
            "incident_type": template["incident_type"],
            "severity": severity,
            "description": description,
            "action_taken": action_taken,
            "incident_metadata": {
                "preventive_measures": preventive_measures,
                "reported_by": f"TEACH{random.randint(1, 32):03d}"
            }
        }
        
        safety_incidents.append(incident_data)

    for incident_data in safety_incidents:
        incident = SafetyIncident(**incident_data)
        session.add(incident)
    
    session.commit()
    print("Safety incidents seeded successfully!") 