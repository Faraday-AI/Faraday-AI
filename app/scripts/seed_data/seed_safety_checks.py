"""Seed data for safety checks."""
from datetime import datetime, timedelta
import random
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.physical_education.safety import SafetyCheck
from app.models.physical_education.pe_enums.pe_types import (
    SafetyType,
    CheckType,
    AlertType,
    SafetyCheckType,
    SafetyCheckLevel,
    SafetyCheckStatus,
    SafetyCheckTrigger
)

def seed_safety_checks(session: Session) -> None:
    """Seed safety checks data."""
    print("Seeding safety checks...")
    
    # Get all class IDs from the database
    result = session.execute(text("SELECT id FROM physical_education_classes"))
    class_ids = [row[0] for row in result.fetchall()]  # Keep as string
    if not class_ids:
        print("No classes found in the database. Skipping safety checks seeding.")
        return
    
    # Get a teacher for the checked_by field
    result = session.execute(text("SELECT id FROM users WHERE role = 'teacher' LIMIT 1"))
    teacher = result.fetchone()
    if not teacher:
        print("Warning: No teacher found for safety checks")
        return
    teacher_id = teacher[0]
    
    # Define check types
    check_types = [
        "equipment_inspection",
        "environmental_assessment",
        "student_health_check",
        "emergency_procedures_review",
        "activity_specific_safety"
    ]
    
    # Define status options
    statuses = ["pending", "completed", "failed", "requires_attention"]
    
    # Create safety checks for each class
    safety_checks = []
    for class_id in class_ids:
        # Create checks for each type
        for check_type in check_types:
            check_date = datetime.now() - timedelta(days=7)  # One week ago
            
            safety_check = SafetyCheck(
                class_id=class_id,  # Already a string, no conversion needed
                check_type=check_type,
                check_date=check_date,
                checked_by=teacher_id,
                results={
                    "items_checked": 5,
                    "issues_found": 0,
                    "notes": "All safety measures in place"
                },
                status="completed",
                check_metadata={
                    "checked_by": "Safety Officer",
                    "location": "Gymnasium",
                    "follow_up_required": False
                }
            )
            safety_checks.append(safety_check)
    
    # Add all safety checks to the session
    session.add_all(safety_checks)
    session.commit()
    
    print(f"Seeded {len(safety_checks)} safety checks.") 