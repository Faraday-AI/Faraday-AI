"""Seed environmental checks data."""
from datetime import datetime, timedelta
import random
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.models.physical_education.safety import EnvironmentalCheck
from app.models.physical_education.pe_enums.pe_types import (
    SafetyType,
    CheckType
)

async def seed_environmental_checks(session: AsyncSession) -> None:
    """Seed environmental checks data."""
    print("Seeding environmental checks...")
    
    # Delete existing records
    await session.execute(text("DELETE FROM environmental_checks"))
    await session.commit()
    
    # Get all class IDs from the database
    result = await session.execute(text("SELECT id FROM classes"))
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
            
            environmental_check = EnvironmentalCheck(
                class_id=class_id,
                check_date=check_date,
                temperature=21.5,  # Celsius
                humidity=45.0,  # Percentage
                air_quality=95.0,  # AQI
                surface_conditions={
                    "floor_type": "hardwood",
                    "cleanliness": "good",
                    "hazards": [],
                    "maintenance_needed": False
                },
                lighting=800.0,  # Lux
                equipment_condition={
                    "storage": "organized",
                    "maintenance": "up-to-date",
                    "issues": []
                },
                environmental_metadata={
                    "checked_by": "Environmental Officer",
                    "location": "Main Gymnasium",
                    "weather": "indoor",
                    "ventilation": "operational"
                }
            )
            environmental_checks.append(environmental_check)
    
    # Add all environmental checks to the session
    session.add_all(environmental_checks)
    await session.flush()
    
    print(f"Seeded {len(environmental_checks)} environmental checks.") 