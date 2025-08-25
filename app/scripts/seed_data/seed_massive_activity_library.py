from datetime import datetime, timedelta
import random
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.physical_education.activity.models import Activity
from app.models.physical_education.pe_enums.pe_types import ActivityDifficulty, ActivityType, ActivityCategory

def seed_massive_activity_library(session):
    """Seed the activities table with exactly 1,000 diverse activities."""
    print("Seeding massive activity library...")
    
    activities = []
    
    # ============================================================================
    # SYSTEMATIC ACTIVITY GENERATION - CARDIO ACTIVITIES (300 activities)
    # ============================================================================
    
    print("Creating cardio activity library...")
    
    # Base cardio activities
    cardio_bases = [
        "Running", "Walking", "Jumping", "Skipping", "Hopping", "Galloping", "Sliding",
        "Cycling", "Swimming", "Rowing", "Elliptical Training", "Stair Climbing",
        "Mountain Climbing", "Burpees", "Mountain Climbers", "High Knees", "Butt Kicks",
        "Jumping Jacks", "Star Jumps", "Cross Jacks", "Seal Jacks", "Power Jacks"
    ]
    
    # Cardio variations
    cardio_variations = [
        "Basic", "Advanced", "Interval", "Endurance", "Speed", "Agility", "Recovery",
        "Power", "Explosive", "Steady State", "Mixed", "Progressive", "Regressive"
    ]
    
    # Cardio modifiers
    cardio_modifiers = [
        "with Resistance", "with Weights", "with Bands", "with Medicine Ball",
        "with Partner", "with Music", "with Timer", "Indoor", "Outdoor", "on Track"
    ]
    
    # Generate cardio activities systematically (limited combinations)
    for base in cardio_bases:
        for variation in cardio_variations[:8]:  # Limit variations
            for modifier in cardio_modifiers[:6]:  # Limit modifiers
                for difficulty in ["BEGINNER", "INTERMEDIATE", "ADVANCED"]:
                    if len(activities) >= 300:  # Stop at 300 cardio
                        break
                    activity = {
                        "name": f"{variation} {base} {modifier}",
                        "description": f"{variation.lower()} {base.lower()} activity {modifier.lower()} for cardiovascular fitness development",
                        "duration": random.randint(15, 60),
                        "difficulty_level": difficulty,
                        "category": ActivityCategory.CARDIO,
                        "type": ActivityType.CARDIO,
                        "equipment_needed": "Stopwatch, Equipment",
                        "safety_notes": "Warm up properly, maintain form, stay hydrated",
                        "calories_burn_rate": random.uniform(5.0, 15.0),
                        "target_muscle_groups": "legs, core, cardiovascular",
                        "format": random.choice(["INDIVIDUAL", "PARTNER", "GROUP"]),
                        "goal": random.choice(["FITNESS", "ENDURANCE", "PERFORMANCE"]),
                        "status": "ACTIVE"
                    }
                    activities.append(activity)
                if len(activities) >= 300:
                    break
            if len(activities) >= 300:
                break
        if len(activities) >= 300:
            break
    
    # ============================================================================
    # SYSTEMATIC ACTIVITY GENERATION - STRENGTH ACTIVITIES (250 activities)
    # ============================================================================
    
    print("Creating strength activity library...")
    
    # Base strength movements
    strength_bases = [
        "Push-ups", "Pull-ups", "Dips", "Squats", "Lunges", "Planks", "Burpees",
        "Mountain Climbers", "Bear Crawls", "Crab Walks", "Inchworm Walks",
        "Wall Walks", "Handstand Holds", "Pike Push-ups", "Diamond Push-ups"
    ]
    
    # Strength variations
    strength_variations = [
        "Basic", "Advanced", "Modified", "Weighted", "Resistance Band", "Plyometric",
        "Isometric", "Eccentric", "Concentric", "Dynamic", "Static", "Explosive"
    ]
    
    # Strength modifiers
    strength_modifiers = [
        "with Weight", "with Resistance Band", "with Medicine Ball", "with Partner",
        "on Stability Ball", "on TRX", "on Rings", "with Tempo", "with Pause"
    ]
    
    # Generate strength activities systematically
    for base in strength_bases:
        for variation in strength_variations[:8]:  # Limit variations
            for modifier in strength_modifiers[:6]:  # Limit modifiers
                for difficulty in ["BEGINNER", "INTERMEDIATE", "ADVANCED"]:
                    if len(activities) >= 550:  # Stop at 550 total
                        break
                    activity = {
                        "name": f"{variation} {base} {modifier}",
                        "description": f"{variation.lower()} {base.lower()} activity {modifier.lower()} for strength development",
                        "duration": random.randint(20, 45),
                        "difficulty_level": difficulty,
                        "category": ActivityCategory.STRENGTH_TRAINING,
                        "type": ActivityType.STRENGTH_TRAINING,
                        "equipment_needed": "Weights, Resistance bands, Equipment",
                        "safety_notes": "Maintain proper form, start with appropriate resistance, allow rest between sets",
                        "calories_burn_rate": random.uniform(3.0, 12.0),
                        "target_muscle_groups": "chest, arms, shoulders, core, legs",
                        "format": random.choice(["INDIVIDUAL", "PARTNER", "GROUP"]),
                        "goal": random.choice(["STRENGTH", "POWER", "MUSCLE_ENDURANCE"]),
                        "status": "ACTIVE"
                    }
                    activities.append(activity)
                if len(activities) >= 550:
                    break
            if len(activities) >= 550:
                break
        if len(activities) >= 550:
            break
    
    # ============================================================================
    # SYSTEMATIC ACTIVITY GENERATION - SPORTS ACTIVITIES (200 activities)
    # ============================================================================
    
    print("Creating sports activity library...")
    
    # Sports
    sports = [
        "Basketball", "Soccer", "Football", "Baseball", "Softball", "Volleyball",
        "Tennis", "Badminton", "Table Tennis", "Golf", "Hockey", "Lacrosse"
    ]
    
    # Sports skills
    sports_skills = [
        "Dribbling", "Shooting", "Passing", "Receiving", "Catching", "Throwing",
        "Kicking", "Heading", "Tackling", "Blocking", "Serving", "Volleying"
    ]
    
    # Sports variations
    sports_variations = [
        "Basic", "Advanced", "Modified", "with Speed", "with Accuracy",
        "with Power", "with Control", "with Movement", "with Partner", "Team-based"
    ]
    
    # Generate sports activities systematically
    for sport in sports:
        for skill in sports_skills[:8]:  # Limit skills
            for variation in sports_variations[:6]:  # Limit variations
                for difficulty in ["BEGINNER", "INTERMEDIATE", "ADVANCED"]:
                    if len(activities) >= 750:  # Stop at 750 total
                        break
                    activity = {
                        "name": f"{variation} {sport} {skill}",
                        "description": f"{variation.lower()} {sport.lower()} {skill.lower()} for skill development",
                        "duration": random.randint(25, 50),
                        "difficulty_level": difficulty,
                        "category": ActivityCategory.SKILL_DEVELOPMENT,
                        "type": ActivityType.SKILL_DEVELOPMENT,
                        "equipment_needed": f"{sport.lower()} equipment",
                        "safety_notes": "Use appropriate protective equipment, follow sport-specific safety rules",
                        "calories_burn_rate": random.uniform(4.0, 14.0),
                        "target_muscle_groups": "full body, sport-specific",
                        "format": random.choice(["INDIVIDUAL", "PARTNER", "GROUP"]),
                        "goal": random.choice(["SKILL_DEVELOPMENT", "PERFORMANCE", "COMPETITION"]),
                        "status": "ACTIVE"
                    }
                    activities.append(activity)
                if len(activities) >= 750:
                    break
            if len(activities) >= 750:
                break
        if len(activities) >= 750:
            break
    
    # ============================================================================
    # SYSTEMATIC ACTIVITY GENERATION - FITNESS TRAINING (150 activities)
    # ============================================================================
    
    print("Creating fitness training activity library...")
    
    # Fitness training types
    fitness_types = [
        "Circuit Training", "HIIT", "Tabata", "CrossFit", "Functional Training",
        "Core Training", "Upper Body Training", "Lower Body Training", "Full Body Training",
        "Agility Training", "Speed Training", "Power Training", "Endurance Training"
    ]
    
    # Fitness variations
    fitness_variations = [
        "Basic", "Advanced", "Modified", "with Equipment", "without Equipment",
        "with Weights", "with Resistance Bands", "with Bodyweight", "Partner-based"
    ]
    
    # Fitness modifiers
    fitness_modifiers = [
        "for Beginners", "for Intermediates", "for Advanced", "for Athletes",
        "for Seniors", "for Youth", "for Rehabilitation", "for Performance"
    ]
    
    # Generate fitness training activities systematically
    for fitness_type in fitness_types:
        for variation in fitness_variations[:6]:  # Limit variations
            for modifier in fitness_modifiers[:6]:  # Limit modifiers
                if len(activities) >= 900:  # Stop at 900 total
                    break
                activity = {
                    "name": f"{variation} {fitness_type} {modifier}",
                    "description": f"{variation.lower()} {fitness_type.lower()} {modifier.lower()}",
                    "duration": random.randint(30, 90),
                    "difficulty_level": random.choice(["BEGINNER", "INTERMEDIATE", "ADVANCED"]),
                                            "category": ActivityCategory.FITNESS_TRAINING,
                                            "type": ActivityType.EXERCISES,
                    "equipment_needed": "Fitness equipment, Weights, Bands",
                    "safety_notes": "Warm up thoroughly, maintain proper form, progress gradually",
                    "calories_burn_rate": random.uniform(6.0, 16.0),
                    "target_muscle_groups": "full body, overall fitness",
                    "format": random.choice(["INDIVIDUAL", "PARTNER", "GROUP"]),
                    "goal": random.choice(["FITNESS", "STRENGTH", "ENDURANCE"]),
                    "status": "ACTIVE"
                }
                activities.append(activity)
            if len(activities) >= 900:
                break
        if len(activities) >= 900:
            break
    
    # ============================================================================
    # SYSTEMATIC ACTIVITY GENERATION - RECREATIONAL ACTIVITIES (100 activities)
    # ============================================================================
    
    print("Creating recreational activities library...")
    
    # Recreational activities
    recreational_activities = [
        "Dance", "Yoga", "Pilates", "Martial Arts", "Swimming",
        "Hiking", "Cycling", "Rock Climbing", "Kayaking", "Paddleboarding",
        "Skating", "Skiing", "Snowboarding", "Surfing", "Tennis"
    ]
    
    # Activity variations
    activity_variations = [
        "Basic", "Advanced", "Modified", "with Instruction", "with Partner",
        "with Group", "with Equipment", "without Equipment", "Competitive"
    ]
    
    # Activity modifiers
    activity_modifiers = [
        "for Beginners", "for Intermediates", "for Advanced", "for Fun",
        "for Competition", "for Recreation", "for Fitness", "for Skill"
    ]
    
    # Generate recreational activities systematically
    for activity in recreational_activities:
        for variation in activity_variations[:5]:  # Limit variations
            for modifier in activity_modifiers[:5]:  # Limit modifiers
                if len(activities) >= 1000:  # Stop at exactly 1000
                    break
                activity_data = {
                    "name": f"{variation} {activity} {modifier}",
                    "description": f"{variation.lower()} {activity.lower()} {modifier.lower()}",
                    "duration": random.randint(30, 150),
                    "difficulty_level": random.choice(["BEGINNER", "INTERMEDIATE", "ADVANCED"]),
                                            "category": ActivityCategory.GAME,
                    "type": ActivityType.RECREATIONAL,
                    "equipment_needed": f"{activity.lower()} equipment",
                    "safety_notes": "Use appropriate safety equipment, follow activity-specific guidelines",
                    "calories_burn_rate": random.uniform(3.0, 12.0),
                    "target_muscle_groups": "full body, recreational skills",
                    "format": random.choice(["INDIVIDUAL", "PARTNER", "GROUP"]),
                    "goal": random.choice(["ENJOYMENT", "SKILL_DEVELOPMENT", "FITNESS"]),
                    "status": "ACTIVE"
                }
                activities.append(activity_data)
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
    print(f"  - Cardio activities: {len([a for a in activities if a['category'] == ActivityCategory.CARDIO])}")
    print(f"  - Strength activities: {len([a for a in activities if a['category'] == ActivityCategory.STRENGTH_TRAINING])}")
    print(f"  - Sports activities: {len([a for a in activities if a['category'] == ActivityCategory.SKILL_DEVELOPMENT])}")
    print(f"  - Fitness training activities: {len([a for a in activities if a['category'] == ActivityCategory.FITNESS_TRAINING])}")
    print(f"  - Recreational activities: {len([a for a in activities if a['category'] == ActivityCategory.GAME])}")
    print(f"Total activities created: {len(activities)}")

if __name__ == "__main__":
    from app.core.database import get_db
    session = next(get_db())
    seed_massive_activity_library(session) 