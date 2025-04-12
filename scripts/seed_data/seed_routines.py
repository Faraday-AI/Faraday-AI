from datetime import datetime
from app.services.physical_education.models.activity import Routine

async def seed_routines(session):
    """Seed the routines table with initial data."""
    routines = [
        {
            "id": "R001",
            "name": "Grade 5 Warm-up Routine",
            "description": "Standard warm-up routine for 5th grade students",
            "class_id": "PE501",
            "duration_minutes": 15,
            "focus_areas": ["cardiovascular", "flexibility", "coordination"]
        },
        {
            "id": "R002",
            "name": "Grade 6 Warm-up Routine",
            "description": "Standard warm-up routine for 6th grade students",
            "class_id": "PE601",
            "duration_minutes": 15,
            "focus_areas": ["cardiovascular", "flexibility", "coordination"]
        },
        {
            "id": "R003",
            "name": "Basketball Skills Circuit",
            "description": "Circuit training for basketball skills",
            "class_id": "PE502",
            "duration_minutes": 30,
            "focus_areas": ["dribbling", "shooting", "passing", "defense"]
        },
        {
            "id": "R004",
            "name": "Soccer Skills Circuit",
            "description": "Circuit training for soccer skills",
            "class_id": "PE602",
            "duration_minutes": 30,
            "focus_areas": ["dribbling", "passing", "shooting", "defense"]
        },
        {
            "id": "R005",
            "name": "Fitness Challenge Circuit",
            "description": "High-intensity fitness circuit",
            "class_id": "PE502",
            "duration_minutes": 25,
            "focus_areas": ["strength", "endurance", "agility", "speed"]
        },
        {
            "id": "R006",
            "name": "Advanced Fitness Circuit",
            "description": "Advanced fitness circuit for 6th grade",
            "class_id": "PE602",
            "duration_minutes": 25,
            "focus_areas": ["strength", "endurance", "agility", "speed"]
        }
    ]

    for routine_data in routines:
        routine = Routine(**routine_data)
        session.add(routine)

    await session.flush()
    print("Routines seeded successfully!") 