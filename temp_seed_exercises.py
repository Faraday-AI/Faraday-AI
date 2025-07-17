from datetime import datetime
from sqlalchemy import text
from app.services.physical_education.models.exercise import Exercise

async def seed_exercises(session):
    """Seed the exercises table with initial data."""
    # Get all activities
    activities = await session.execute(text("SELECT id, name FROM activities"))
    activity_map = {row.name: row.id for row in activities}
    
    exercises = [
        {
            "name": "Basic Jump Rope",
            "description": "Basic jump rope technique with two feet",
            "activity_id": activity_map["Jump Rope Basics"],
            "duration_minutes": 10,
            "intensity": "medium",
            "equipment_needed": "Jump rope",
            "sets": 4
        },
        {
            "name": "Basketball Dribble Drills",
            "description": "Basic basketball dribbling techniques",
            "activity_id": activity_map["Basketball Dribbling"],
            "duration_minutes": 15,
            "intensity": "medium",
            "equipment_needed": "Basketball",
            "sets": 4
        },
        {
            "name": "Soccer Passing Drills",
            "description": "Basic soccer passing techniques",
            "activity_id": activity_map["Soccer Passing"],
            "duration_minutes": 20,
            "intensity": "medium",
            "equipment_needed": "Soccer ball",
            "sets": 4
        },
        {
            "name": "Dynamic Warm-up Circuit",
            "description": "Full-body dynamic warm-up exercises",
            "activity_id": activity_map["Dynamic Warm-up"],
            "duration_minutes": 10,
            "intensity": "low",
            "equipment_needed": "None",
            "sets": 3
        },
        {
            "name": "Static Stretching Routine",
            "description": "Post-activity static stretching",
            "activity_id": activity_map["Cool Down Stretches"],
            "duration_minutes": 10,
            "intensity": "low",
            "equipment_needed": "Yoga mat (optional)",
            "sets": 3
        },
        {
            "name": "Circuit Training Workout",
            "description": "Full-body circuit training exercises",
            "activity_id": activity_map["Circuit Training"],
            "duration_minutes": 30,
            "intensity": "high",
            "equipment_needed": "Various fitness equipment",
            "sets": 5
        },
        {
            "name": "Basketball Game Drills",
            "description": "5v5 basketball game preparation",
            "activity_id": activity_map["Basketball Game"],
            "duration_minutes": 40,
            "intensity": "high",
            "equipment_needed": "Basketball, court",
            "sets": 5
        },
        {
            "name": "Advanced Jump Rope Techniques",
            "description": "Advanced jump rope combinations",
            "activity_id": activity_map["Advanced Jump Rope"],
            "duration_minutes": 20,
            "intensity": "high",
            "equipment_needed": "Jump rope",
            "sets": 5
        }
    ]

    for exercise_data in exercises:
        exercise = Exercise(**exercise_data)
        session.add(exercise)

    await session.flush()
    print("Exercises seeded successfully!") 