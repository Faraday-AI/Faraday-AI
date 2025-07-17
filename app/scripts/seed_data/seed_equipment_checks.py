from datetime import datetime, timedelta
import random
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.physical_education.safety import EquipmentCheck
from app.models.physical_education.pe_enums.pe_types import (
    SafetyType,
    CheckType,
    EquipmentType
)

def seed_equipment_checks(session: Session):
    """Seed equipment checks data."""
    print("Seeding equipment checks...")
    
    # Get all class IDs
    result = session.execute(text("SELECT id FROM physical_education_classes"))
    class_ids = [row[0] for row in result.fetchall()]
    
    if not class_ids:
        print("No classes found to seed equipment checks for")
        return
    
    # Common equipment types
    equipment_types = [
        "Basketball", "Soccer Ball", "Jump Rope", "Cones", "Hula Hoop",
        "Tennis Ball", "Volleyball", "Baseball", "Frisbee", "Yoga Mat"
    ]
    
    # Generate equipment checks
    equipment_checks = []
    for class_id in class_ids:
        # Generate 2-4 equipment checks per class
        num_checks = random.randint(2, 4)
        for _ in range(num_checks):
            equipment_type = random.choice(equipment_types)
            check_date = datetime.utcnow() - timedelta(days=random.randint(0, 30))
            last_maintenance = check_date - timedelta(days=random.randint(0, 90))
            purchase_date = last_maintenance - timedelta(days=random.randint(180, 365))
            
            # Create equipment check without specifying id
            equipment_check = EquipmentCheck(
                class_id=class_id,
                equipment_id=f"{equipment_type}-{random.randint(1000, 9999)}",
                check_date=check_date,
                maintenance_status=random.choice([True, False]),
                damage_status=random.choice([True, False]),
                age_status=random.choice([True, False]),
                last_maintenance=last_maintenance,
                purchase_date=purchase_date,
                max_age_years=random.uniform(1.0, 5.0),
                equipment_metadata={
                    "type": equipment_type,
                    "condition": random.choice(["Good", "Fair", "Poor"]),
                    "notes": random.choice([
                        "Regular wear and tear",
                        "Needs replacement soon",
                        "In good condition",
                        "Requires maintenance"
                    ])
                }
            )
            equipment_checks.append(equipment_check)
    
    # Add all equipment checks to the session
    session.add_all(equipment_checks)
    session.flush()
    
    print(f"Seeded {len(equipment_checks)} equipment checks.") 