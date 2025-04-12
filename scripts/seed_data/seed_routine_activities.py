from datetime import datetime
from app.services.physical_education.models.activity import RoutineActivity

async def seed_routine_activities(session):
    """Seed the routine_activities table with initial data."""
    routine_activities = [
        # Grade 5 Warm-up Routine (R001)
        {
            "routine_id": "R001",
            "activity_id": 4,  # Dynamic Warm-up
            "order": 1,
            "duration_minutes": 10,
            "notes": "Full-body dynamic warm-up"
        },
        {
            "routine_id": "R001",
            "activity_id": 1,  # Jump Rope Basics
            "order": 2,
            "duration_minutes": 5,
            "notes": "Basic jump rope to increase heart rate"
        },
        
        # Grade 6 Warm-up Routine (R002)
        {
            "routine_id": "R002",
            "activity_id": 4,  # Dynamic Warm-up
            "order": 1,
            "duration_minutes": 10,
            "notes": "Full-body dynamic warm-up"
        },
        {
            "routine_id": "R002",
            "activity_id": 1,  # Jump Rope Basics
            "order": 2,
            "duration_minutes": 5,
            "notes": "Basic jump rope to increase heart rate"
        },
        
        # Basketball Skills Circuit (R003)
        {
            "routine_id": "R003",
            "activity_id": 2,  # Basketball Dribbling
            "order": 1,
            "duration_minutes": 10,
            "notes": "Dribbling drills"
        },
        {
            "routine_id": "R003",
            "activity_id": 6,  # Circuit Training
            "order": 2,
            "duration_minutes": 20,
            "notes": "Basketball-specific circuit"
        },
        
        # Soccer Skills Circuit (R004)
        {
            "routine_id": "R004",
            "activity_id": 3,  # Soccer Passing
            "order": 1,
            "duration_minutes": 10,
            "notes": "Passing drills"
        },
        {
            "routine_id": "R004",
            "activity_id": 6,  # Circuit Training
            "order": 2,
            "duration_minutes": 20,
            "notes": "Soccer-specific circuit"
        },
        
        # Fitness Challenge Circuit (R005)
        {
            "routine_id": "R005",
            "activity_id": 6,  # Circuit Training
            "order": 1,
            "duration_minutes": 25,
            "notes": "High-intensity fitness circuit"
        },
        
        # Advanced Fitness Circuit (R006)
        {
            "routine_id": "R006",
            "activity_id": 6,  # Circuit Training
            "order": 1,
            "duration_minutes": 25,
            "notes": "Advanced fitness circuit"
        }
    ]

    for routine_activity_data in routine_activities:
        routine_activity = RoutineActivity(**routine_activity_data)
        session.add(routine_activity)

    await session.flush()
    print("Routine activities seeded successfully!") 