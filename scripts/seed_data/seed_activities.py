from datetime import datetime
from app.services.physical_education.models.activity import Activity

async def seed_activities(session):
    """Seed the activities table with initial data."""
    activities = [
        {
            "name": "Jump Rope Basics",
            "description": "Basic jump rope techniques for beginners",
            "activity_type": "skill_development",
            "difficulty": "beginner",
            "equipment_required": "minimal",
            "duration_minutes": 15
        },
        {
            "name": "Basketball Dribbling",
            "description": "Basic basketball dribbling skills",
            "activity_type": "skill_development",
            "difficulty": "beginner",
            "equipment_required": "moderate",
            "duration_minutes": 20
        },
        {
            "name": "Soccer Passing",
            "description": "Basic soccer passing techniques",
            "activity_type": "skill_development",
            "difficulty": "beginner",
            "equipment_required": "moderate",
            "duration_minutes": 25
        },
        {
            "name": "Dynamic Warm-up",
            "description": "Full-body dynamic warm-up routine",
            "activity_type": "warm_up",
            "difficulty": "beginner",
            "equipment_required": "none",
            "duration_minutes": 10
        },
        {
            "name": "Cool Down Stretches",
            "description": "Post-activity stretching routine",
            "activity_type": "cool_down",
            "difficulty": "beginner",
            "equipment_required": "none",
            "duration_minutes": 10
        },
        {
            "name": "Circuit Training",
            "description": "Full-body circuit training workout",
            "activity_type": "fitness_training",
            "difficulty": "intermediate",
            "equipment_required": "moderate",
            "duration_minutes": 30
        },
        {
            "name": "Basketball Game",
            "description": "5v5 basketball game",
            "activity_type": "game",
            "difficulty": "intermediate",
            "equipment_required": "moderate",
            "duration_minutes": 40
        },
        {
            "name": "Advanced Jump Rope",
            "description": "Advanced jump rope techniques and combinations",
            "activity_type": "skill_development",
            "difficulty": "advanced",
            "equipment_required": "minimal",
            "duration_minutes": 20
        }
    ]

    for activity_data in activities:
        activity = Activity(**activity_data)
        session.add(activity)

    await session.flush()
    print("Activities seeded successfully!") 