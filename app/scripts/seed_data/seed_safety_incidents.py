from datetime import datetime, timedelta
import random
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.physical_education.safety import SafetyIncident
from app.models.physical_education.pe_enums.pe_types import (
    IncidentType,
    IncidentLevel,
    IncidentStatus,
    IncidentTrigger
)

async def seed_safety_incidents(session):
    """Seed the safety_incidents table with initial data."""
    # First, get the actual activity IDs from the database
    result = await session.execute(text("SELECT id, name FROM activities ORDER BY name"))
    activities = {row.name: row.id for row in result.fetchall()}
    
    # Get the actual student IDs from the database
    result = await session.execute(text("SELECT id, first_name, last_name FROM students ORDER BY id"))
    students = {f"{row.first_name} {row.last_name}": row.id for row in result.fetchall()}
    
    safety_incidents = [
        {
            "student_id": students["John Smith"],  # Using actual student ID
            "activity_id": activities["Jump Rope Basics"],
            "incident_type": "injury",
            "severity": "low",
            "description": "Twisted ankle during double under attempt",
            "action_taken": "Applied ice and provided rest",
            "incident_metadata": {
                "preventive_measures": "Added proper landing technique training",
                "reported_by": "TEACH001"
            }
        },
        {
            "student_id": students["Emily Johnson"],
            "activity_id": activities["Basketball Dribbling"],
            "incident_type": "near_miss",
            "severity": "low",
            "description": "Almost collided with another student during fast dribble drill",
            "action_taken": "Reorganized drill spacing",
            "incident_metadata": {
                "preventive_measures": "Added visual markers for personal space",
                "reported_by": "TEACH001"
            }
        },
        {
            "student_id": students["Michael Brown"],
            "activity_id": activities["Soccer Passing"],
            "incident_type": "equipment_failure",
            "severity": "low",
            "description": "Soccer ball was overinflated and too hard",
            "action_taken": "Replaced ball with properly inflated one",
            "incident_metadata": {
                "preventive_measures": "Added ball pressure check before each session",
                "reported_by": "TEACH002"
            }
        },
        {
            "student_id": students["Sarah Davis"],
            "activity_id": activities["Circuit Training"],
            "incident_type": "behavioral_issue",
            "severity": "low",
            "description": "Student performing lunges with improper knee alignment",
            "action_taken": "Provided immediate form correction",
            "incident_metadata": {
                "preventive_measures": "Added more detailed form demonstration",
                "reported_by": "TEACH002"
            }
        }
    ]

    for incident_data in safety_incidents:
        incident = SafetyIncident(**incident_data)
        session.add(incident)
    
    await session.commit()
    print("Safety incidents seeded successfully!") 