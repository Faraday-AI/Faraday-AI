from datetime import datetime, timedelta
import random
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.activity import Activity
from app.models.physical_education.pe_enums.pe_types import (
    ActivityType,
    ActivityLevel,
    ActivityStatus
)

def seed_activities(session: Session):
    """Seed the activities table with initial data."""
    activities = [
        {
            "name": "Jump Rope Basics",
            "description": "Basic jump rope techniques for beginners",
            "type": ActivityType.SKILL_DEVELOPMENT,
            "difficulty_level": "BEGINNER",
            "equipment_needed": "Jump rope",
            "duration": 15
        },
        {
            "name": "Basketball Dribbling",
            "description": "Basic basketball dribbling skills",
            "type": ActivityType.SKILL_DEVELOPMENT,
            "difficulty_level": "BEGINNER",
            "equipment_needed": "Basketball",
            "duration": 20
        },
        {
            "name": "Soccer Passing",
            "description": "Basic soccer passing techniques",
            "type": ActivityType.SKILL_DEVELOPMENT,
            "difficulty_level": "BEGINNER",
            "equipment_needed": "Soccer ball",
            "duration": 25
        },
        {
            "name": "Dynamic Warm-up",
            "description": "Full-body dynamic warm-up routine",
            "type": ActivityType.WARM_UP,
            "difficulty_level": "BEGINNER",
            "equipment_needed": "None",
            "duration": 10
        },
        {
            "name": "Cool Down Stretches",
            "description": "Post-activity stretching routine",
            "type": ActivityType.COOL_DOWN,
            "difficulty_level": "BEGINNER",
            "equipment_needed": "None",
            "duration": 10
        },
        {
            "name": "Circuit Training",
            "description": "Full-body circuit training workout",
            "type": ActivityType.CARDIO,
            "difficulty_level": "INTERMEDIATE",
            "equipment_needed": "Weights, mats",
            "duration": 30
        },
        {
            "name": "Basketball Game",
            "description": "5v5 basketball game",
            "type": ActivityType.GAMES,
            "difficulty_level": "INTERMEDIATE",
            "equipment_needed": "Basketball, hoops",
            "duration": 40
        },
        {
            "name": "Advanced Jump Rope",
            "description": "Advanced jump rope techniques and combinations",
            "type": ActivityType.SKILL_DEVELOPMENT,
            "difficulty_level": "ADVANCED",
            "equipment_needed": "Jump rope",
            "duration": 20
        }
    ]

    for activity_data in activities:
        activity = Activity(**activity_data)
        session.add(activity)

    session.commit()  # Commit the activities to ensure they are in the database
    
    # Verify activities were created
    result = session.execute(text("SELECT id, name FROM activities ORDER BY id"))
    activities = result.fetchall()
    print("\nActivities in database:")
    for activity in activities:
        print(f"ID: {activity.id}, Name: {activity.name}")
    
    # Check for gaps in IDs
    ids = [activity.id for activity in activities]
    if len(ids) > 1:
        gaps = []
        for i in range(1, len(ids)):
            if ids[i] - ids[i-1] > 1:
                gaps.append((ids[i-1], ids[i]))
        if gaps:
            print("\nGaps in activity IDs:")
            for start, end in gaps:
                print(f"Gap between {start} and {end}")
        else:
            print("\nNo gaps in activity IDs")
    
    print("Activities seeded successfully!") 