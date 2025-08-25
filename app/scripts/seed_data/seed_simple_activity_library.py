from datetime import datetime, timedelta
import random
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.physical_education.activity.models import Activity

def seed_simple_activity_library(session):
    """Seed the activities table with a simple library of 1,000 activities using basic values."""
    print("Seeding simple activity library...")
    
    activities = []
    
    # ============================================================================
    # SIMPLE ACTIVITY GENERATION - BASIC ACTIVITIES (150 activities)
    # ============================================================================
    
    print("Creating basic activity library...")
    
    # Basic activity types
    basic_activities = [
        "Running", "Walking", "Jumping", "Skipping", "Hopping", "Galloping", "Sliding",
        "Cycling", "Swimming", "Rowing", "Stair Climbing", "Mountain Climbing", 
        "Burpees", "Mountain Climbers", "High Knees", "Butt Kicks", "Jumping Jacks",
        "Push-ups", "Pull-ups", "Dips", "Squats", "Lunges", "Planks", "Bear Crawls",
        "Basketball", "Soccer", "Football", "Baseball", "Softball", "Volleyball",
        "Tennis", "Badminton", "Table Tennis", "Golf", "Hockey", "Lacrosse",
        "Dance", "Yoga", "Pilates", "Martial Arts", "Hiking", "Rock Climbing",
        "Skating", "Skiing", "Snowboarding", "Surfing", "Bowling", "Archery"
    ]
    
    # Activity variations
    variations = [
        "Basic", "Advanced", "Modified", "Interval", "Endurance", "Speed", "Agility",
        "Recovery", "Power", "Explosive", "Steady State", "Mixed", "Progressive"
    ]
    
    # Activity modifiers
    modifiers = [
        "with Resistance", "with Weights", "with Bands", "with Medicine Ball",
        "with Partner", "with Music", "with Timer", "Indoor", "Outdoor", "on Track",
        "on Field", "in Gym", "in Pool", "with Equipment", "without Equipment"
    ]
    
    # Generate activities systematically (expanded combinations for 1,000 activities)
    for base in basic_activities:
        for variation in variations:  # Use all variations
            for modifier in modifiers:  # Use all modifiers
                for difficulty in ["BEGINNER", "INTERMEDIATE", "ADVANCED"]:
                    if len(activities) >= 1000:  # Stop at 1000
                        break
                    
                    # Determine category and type based on activity using correct database enum values
                    # Distribute activities evenly across all types and categories
                    
                    # First, determine the type based on the activity index to ensure even distribution
                    type_options = ["CARDIO", "STRENGTH_TRAINING", "SKILL_DEVELOPMENT", "DANCE", "GAMES", "FLEXIBILITY", "HIIT", "WARM_UP", "COOL_DOWN"]
                    activity_type = type_options[len(activities) % len(type_options)]
                    
                    # Then determine category based on the type and activity index
                    if activity_type == "CARDIO":
                        # Distribute cardio activities across different categories
                        category_options = ["INDIVIDUAL", "TEAM", "GROUP", "COMPETITIVE"]
                        category = category_options[len(activities) % len(category_options)]
                    elif activity_type == "STRENGTH_TRAINING":
                        # Distribute strength activities across different categories
                        category_options = ["INDIVIDUAL", "GROUP", "COMPETITIVE"]
                        category = category_options[len(activities) % len(category_options)]
                    elif activity_type == "SKILL_DEVELOPMENT":
                        # Distribute skill development activities across different categories
                        category_options = ["TEAM", "COMPETITIVE", "GROUP"]
                        category = category_options[len(activities) % len(category_options)]
                    elif activity_type == "DANCE":
                        # Distribute dance activities across different categories
                        category_options = ["GROUP", "INDIVIDUAL", "COMPETITIVE"]
                        category = category_options[len(activities) % len(category_options)]
                    elif activity_type == "GAMES":
                        # Distribute game activities across different categories
                        category_options = ["INDIVIDUAL", "GROUP"]
                        category = category_options[len(activities) % len(category_options)]
                    else:
                        # Distribute other activities across different categories
                        category_options = ["INDIVIDUAL", "TEAM", "GROUP", "COMPETITIVE"]
                        category = category_options[len(activities) % len(category_options)]
                    
                    activity = {
                        "name": f"{variation} {base} {modifier}",
                        "description": f"{variation.lower()} {base.lower()} activity {modifier.lower()} for fitness development",
                        "duration": random.randint(15, 60),
                        "difficulty_level": difficulty,
                        "category": category,
                        "type": activity_type,
                        "equipment_needed": "Equipment as needed",
                        "safety_notes": "Warm up properly, maintain form, stay hydrated",
                        "calories_burn_rate": random.uniform(3.0, 15.0),
                        "target_muscle_groups": "full body, fitness development",
                        "format": ["INDIVIDUAL", "SMALL_GROUP", "LARGE_GROUP", "CLASS", "TEAM"][len(activities) % 5], # Distribute evenly
                        "goal": ["SKILL_DEVELOPMENT", "HEALTH", "COORDINATION", "WELLNESS", "COMPETITION", "ENJOYMENT", "TEAMWORK", "FITNESS"][len(activities) % 8], # Distribute evenly
                        "status": "ACTIVE"
                    }
                    activities.append(activity)
                if len(activities) >= 1000:
                    break
            if len(activities) >= 1000:
                break
        if len(activities) >= 1000:
            break
    
    # ============================================================================
    # CREATE ALL ACTIVITIES
    # ============================================================================
    
    print(f"Creating {len(activities)} activities...")
    
    for activity_data in activities:
        activity = Activity(**activity_data)
        session.add(activity)

    session.commit()
    print(f"Successfully seeded {len(activities)} comprehensive activities!")
    print(f"Massive activity library now includes:")
    print(f"  - Individual activities: {len([a for a in activities if a['category'] == 'INDIVIDUAL'])}")
    print(f"  - Team activities: {len([a for a in activities if a['category'] == 'TEAM'])}")
    print(f"  - Group activities: {len([a for a in activities if a['category'] == 'GROUP'])}")
    print(f"  - Competitive activities: {len([a for a in activities if a['category'] == 'COMPETITIVE'])}")
    print(f"  - Cardio activities: {len([a for a in activities if a['type'] == 'CARDIO'])}")
    print(f"  - Strength activities: {len([a for a in activities if a['type'] == 'STRENGTH_TRAINING'])}")
    print(f"  - Skill development activities: {len([a for a in activities if a['type'] == 'SKILL_DEVELOPMENT'])}")
    print(f"  - Dance activities: {len([a for a in activities if a['type'] == 'DANCE'])}")
    print(f"  - Game activities: {len([a for a in activities if a['type'] == 'GAMES'])}")
    print(f"Total activities created: {len(activities)}")

if __name__ == "__main__":
    from app.core.database import get_db
    session = next(get_db())
    seed_simple_activity_library(session) 