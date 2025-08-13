"""Seed environmental checks data."""
from datetime import datetime, timedelta
import random
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.physical_education.safety import EnvironmentalCheck
from app.models.physical_education.pe_enums.pe_types import (
    SafetyType,
    CheckType
)

def seed_environmental_checks(session: Session) -> None:
    """Seed environmental checks data."""
    print("Seeding environmental checks...")
    
    # Delete existing records
    session.execute(text("DELETE FROM physical_education_environmental_checks"))
    session.commit()
    
    # Get all class IDs from the database
    result = session.execute(text("SELECT id FROM physical_education_classes"))
    class_ids = [row[0] for row in result.fetchall()]
    
    if not class_ids:
        print("No classes found in the database. Skipping environmental checks seeding.")
        return
    
    # Create environmental checks for each class
    environmental_checks = []
    for class_id in class_ids:
        # Create multiple checks per class with different dates
        for days_ago in [1, 3, 7]:
            check_date = datetime.now() - timedelta(days=days_ago)
            
            # Get a teacher for the checked_by field
            teacher_result = session.execute(text("SELECT id FROM users LIMIT 1"))
            teacher_id = teacher_result.fetchone()[0]
            
            environmental_check = EnvironmentalCheck(
                class_id=class_id,
                check_date=check_date,
                checked_by=teacher_id,
                temperature=21.5,  # Celsius
                humidity=45.0,  # Percentage
                air_quality="good",  # String value
                lighting_conditions="adequate",  # String value
                surface_condition="good",  # String value
                weather_conditions="indoor",  # String value
                status="PASS",
                notes="Regular environmental check completed"
            )
            environmental_checks.append(environmental_check)
    
    # Add all environmental checks to the session
    session.add_all(environmental_checks)
    session.flush()
    
    # Count and display the actual number of environmental checks seeded
    environmental_check_count = session.query(EnvironmentalCheck).count()
    print(f"Seeded {len(environmental_checks)} environmental checks. Total environmental checks in database: {environmental_check_count}") 