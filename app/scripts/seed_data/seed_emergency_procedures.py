from datetime import datetime, timedelta
import random
import json
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import text, select
from app.models.physical_education.safety import EmergencyProcedure
from app.models.physical_education.class_ import PhysicalEducationClass
from app.models.core.user import User

def seed_emergency_procedures(session):
    """Seed the emergency_procedures table with initial data."""
    # Check if emergency_procedures already has data
    result = session.execute(text("SELECT COUNT(*) FROM emergency_procedures"))
    if result.scalar() > 0:
        print("Emergency procedures already seeded, skipping...")
        return
    
    # Get actual classes from the database dynamically
    class_result = session.execute(text("SELECT id, name FROM physical_education_classes LIMIT 20"))
    classes = {row.id: row.name for row in class_result.fetchall()}
    
    if not classes:
        print("Warning: No classes found for emergency procedures")
        return
    
    # Get teacher users for the created_by field
    teacher_result = session.execute(select(User).where(User.role == "teacher"))
    teachers = [teacher.id for teacher in teacher_result.scalars().all()]
    
    if not teachers:
        print("Warning: No teachers found for emergency procedures")
        return
    
    # Define procedure types
    procedure_types = ["fire", "medical", "weather", "security", "other"]
    
    # Define procedure templates
    procedure_templates = {
        "fire": {
            "name": "Fire Evacuation Procedure",
            "description": "Comprehensive fire evacuation procedure for physical education facilities",
            "steps": [
                "Sound alarm and alert all staff",
                "Evacuate students immediately through designated exits",
                "Account for all students at designated assembly point",
                "Contact emergency services (911)",
                "Wait for all-clear from fire department before re-entry"
            ],
            "contact_info": {
                "fire_department": "911",
                "school_security": "Extension 1111",
                "principal": "Extension 1000"
            }
        },
        "medical": {
            "name": "Medical Emergency Procedure",
            "description": "Standard procedure for handling medical emergencies during physical education",
            "steps": [
                "Assess situation and call for help",
                "Administer first aid if trained",
                "Contact school nurse immediately",
                "Call 911 if condition is serious",
                "Notify parents/guardians",
                "Document incident in detail"
            ],
            "contact_info": {
                "emergency_services": "911",
                "school_nurse": "Extension 2222",
                "administrator": "Extension 1000"
            }
        },
        "weather": {
            "name": "Severe Weather Procedure",
            "description": "Procedure for handling severe weather conditions during outdoor activities",
            "steps": [
                "Monitor weather conditions continuously",
                "Move indoors immediately when severe weather is detected",
                "Account for all students",
                "Stay away from windows and doors",
                "Wait for all-clear from administration"
            ],
            "contact_info": {
                "weather_service": "Local weather line",
                "administration": "Extension 1000"
            }
        },
        "security": {
            "name": "Security Lockdown Procedure",
            "description": "Lockdown procedure for security threats during physical education",
            "steps": [
                "Lock all doors and windows",
                "Move students to secure location",
                "Turn off lights and remain quiet",
                "Account for all students",
                "Wait for official all-clear signal"
            ],
            "contact_info": {
                "security": "Extension 1111",
                "police": "911",
                "administration": "Extension 1000"
            }
        },
        "other": {
            "name": "General Emergency Procedure",
            "description": "General emergency response procedure for various situations",
            "steps": [
                "Assess the situation",
                "Ensure student safety first",
                "Contact appropriate authorities",
                "Follow established protocols",
                "Document the incident"
            ],
            "contact_info": {
                "emergency": "911",
                "administration": "Extension 1000"
            }
        }
    }
    
    emergency_procedures = []
    
    # Create procedures for each class (at least one per class)
    class_ids = list(classes.keys())
    
    # Create 2-3 procedures per class on average
    num_procedures = max(50, len(class_ids) * 2)
    
    for i in range(num_procedures):
        # Randomly select class (can be None for general procedures)
        class_id = random.choice(class_ids) if random.random() > 0.2 else None
        
        # Select procedure type
        procedure_type = random.choice(procedure_types)
        template = procedure_templates[procedure_type]
        
        # Generate procedure name with variation
        if class_id:
            procedure_name = f"{template['name']} - {classes[class_id]}"
        else:
            procedure_name = f"{template['name']} - General"
        
        # Random dates for drills
        last_drill_date = datetime.now() - timedelta(days=random.randint(30, 365))
        next_drill_date = datetime.now() + timedelta(days=random.randint(30, 180))
        
        # Create procedure data
        procedure_data = {
            "name": procedure_name,
            "description": template["description"],
            "procedure_type": procedure_type,
            "class_id": class_id,
            "steps": json.dumps(template["steps"]),
            "contact_info": json.dumps(template["contact_info"]),
            "is_active": True,
            "last_drill_date": last_drill_date,
            "next_drill_date": next_drill_date,
            "created_by": random.choice(teachers)
        }
        
        emergency_procedures.append(procedure_data)
    
    # Add procedures to session
    for procedure_data in emergency_procedures:
        procedure = EmergencyProcedure(**procedure_data)
        session.add(procedure)
    
    session.flush()
    print(f"Emergency procedures seeded successfully! ({len(emergency_procedures)} records)")

