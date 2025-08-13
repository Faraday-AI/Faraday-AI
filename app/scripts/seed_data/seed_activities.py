from datetime import datetime, timedelta
import random
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.activity import Activity
from app.models.physical_education.pe_enums.pe_types import (
    ActivityType,
    ActivityLevel,
    ActivityStatus,
    ActivityCategoryType,
    ActivityFormat,
    ActivityGoal
)

def seed_activities(session: Session):
    """Seed the activities table with comprehensive and diverse initial data."""
    
    # First delete existing activities
    session.execute(Activity.__table__.delete())
    
    activities = [
        # BEGINNER LEVEL ACTIVITIES
        {
            "name": "Jump Rope Basics",
            "description": "Basic jump rope techniques for beginners including single jumps, double jumps, and basic footwork patterns",
            "type": ActivityType.SKILL_DEVELOPMENT,
            "difficulty_level": "BEGINNER",
            "equipment_needed": "Jump rope",
            "duration": 15,
            "calories_burn_rate": 8.0,
            "target_muscle_groups": "Legs, cardiovascular",
            "safety_notes": "Ensure proper rope length, clear space around student",
            "category": ActivityCategoryType.INDIVIDUAL,
            "format": ActivityFormat.INDIVIDUAL,
            "goal": ActivityGoal.SKILL_DEVELOPMENT,
            "status": ActivityStatus.ACTIVE
        },
        {
            "name": "Basketball Dribbling",
            "description": "Basic basketball dribbling skills with both hands, stationary and moving drills",
            "type": ActivityType.SKILL_DEVELOPMENT,
            "difficulty_level": "BEGINNER",
            "equipment_needed": "Basketball",
            "duration": 20,
            "calories_burn_rate": 6.0,
            "target_muscle_groups": "Arms, shoulders, coordination",
            "safety_notes": "Use appropriate ball size for age group",
            "category": ActivityCategoryType.INDIVIDUAL,
            "format": ActivityFormat.INDIVIDUAL,
            "goal": ActivityGoal.SKILL_DEVELOPMENT,
            "status": ActivityStatus.ACTIVE
        },
        {
            "name": "Soccer Passing",
            "description": "Basic soccer passing techniques including inside foot, outside foot, and short passes",
            "type": ActivityType.SKILL_DEVELOPMENT,
            "difficulty_level": "BEGINNER",
            "equipment_needed": "Soccer ball",
            "duration": 25,
            "calories_burn_rate": 7.0,
            "target_muscle_groups": "Legs, coordination",
            "safety_notes": "Ensure proper ball inflation, clear space",
            "category": ActivityCategoryType.INDIVIDUAL,
            "format": ActivityFormat.INDIVIDUAL,
            "goal": ActivityGoal.SKILL_DEVELOPMENT,
            "status": ActivityStatus.ACTIVE
        },
        {
            "name": "Dynamic Warm-up",
            "description": "Full-body dynamic warm-up routine including arm circles, leg swings, and light jogging",
            "type": ActivityType.WARM_UP,
            "difficulty_level": "BEGINNER",
            "equipment_needed": "None",
            "duration": 10,
            "calories_burn_rate": 4.0,
            "target_muscle_groups": "Full body",
            "safety_notes": "Start slow, increase intensity gradually",
            "category": ActivityCategoryType.INDIVIDUAL,
            "format": ActivityFormat.INDIVIDUAL,
            "goal": ActivityGoal.FITNESS,
            "status": ActivityStatus.ACTIVE
        },
        {
            "name": "Cool Down Stretches",
            "description": "Post-activity stretching routine focusing on major muscle groups used during activity",
            "type": ActivityType.COOL_DOWN,
            "difficulty_level": "BEGINNER",
            "equipment_needed": "None",
            "duration": 10,
            "calories_burn_rate": 2.0,
            "target_muscle_groups": "Full body flexibility",
            "safety_notes": "Hold stretches gently, no bouncing",
            "category": ActivityCategoryType.INDIVIDUAL,
            "format": ActivityFormat.INDIVIDUAL,
            "goal": ActivityGoal.HEALTH,
            "status": ActivityStatus.ACTIVE
        },
        {
            "name": "Basic Yoga Poses",
            "description": "Simple yoga poses for beginners including mountain pose, child's pose, and cat-cow",
            "type": ActivityType.FLEXIBILITY,
            "difficulty_level": "BEGINNER",
            "equipment_needed": "Yoga mat (optional)",
            "duration": 20,
            "calories_burn_rate": 3.0,
            "target_muscle_groups": "Full body flexibility",
            "safety_notes": "Focus on breathing, don't force poses",
            "category": ActivityCategoryType.INDIVIDUAL,
            "format": ActivityFormat.INDIVIDUAL,
            "goal": ActivityGoal.WELLNESS,
            "status": ActivityStatus.ACTIVE
        },
        {
            "name": "Walking Drills",
            "description": "Various walking patterns including heel-to-toe, side stepping, and backward walking",
            "type": ActivityType.CARDIO,
            "difficulty_level": "BEGINNER",
            "equipment_needed": "None",
            "duration": 15,
            "calories_burn_rate": 5.0,
            "target_muscle_groups": "Legs, coordination",
            "safety_notes": "Ensure clear path, maintain balance",
            "category": ActivityCategoryType.INDIVIDUAL,
            "format": ActivityFormat.INDIVIDUAL,
            "goal": ActivityGoal.FITNESS,
            "status": ActivityStatus.ACTIVE
        },
        {
            "name": "Basic Throwing",
            "description": "Fundamental throwing techniques using soft balls or bean bags",
            "type": ActivityType.SKILL_DEVELOPMENT,
            "difficulty_level": "BEGINNER",
            "equipment_needed": "Soft balls or bean bags",
            "duration": 20,
            "calories_burn_rate": 4.0,
            "target_muscle_groups": "Arms, shoulders, coordination",
            "safety_notes": "Use soft equipment, clear throwing area",
            "category": ActivityCategoryType.INDIVIDUAL,
            "format": ActivityFormat.INDIVIDUAL,
            "goal": ActivityGoal.SKILL_DEVELOPMENT,
            "status": ActivityStatus.ACTIVE
        },
        
        # INTERMEDIATE LEVEL ACTIVITIES
        {
            "name": "Circuit Training",
            "description": "Full-body circuit training workout with stations for different muscle groups",
            "type": ActivityType.CARDIO,
            "difficulty_level": "INTERMEDIATE",
            "equipment_needed": "Weights, mats, cones",
            "duration": 30,
            "calories_burn_rate": 12.0,
            "target_muscle_groups": "Full body strength and cardio",
            "safety_notes": "Proper form over speed, rest between stations",
            "category": ActivityCategoryType.GROUP,
            "format": ActivityFormat.SMALL_GROUP,
            "goal": ActivityGoal.FITNESS,
            "status": ActivityStatus.ACTIVE
        },
        {
            "name": "Basketball Game",
            "description": "5v5 basketball game with modified rules for physical education setting",
            "type": ActivityType.GAMES,
            "difficulty_level": "INTERMEDIATE",
            "equipment_needed": "Basketball, hoops, court",
            "duration": 40,
            "calories_burn_rate": 15.0,
            "target_muscle_groups": "Full body, cardiovascular",
            "safety_notes": "Emphasize teamwork, fair play, proper warm-up",
            "category": ActivityCategoryType.TEAM,
            "format": ActivityFormat.TEAM,
            "goal": ActivityGoal.COMPETITION,
            "status": ActivityStatus.ACTIVE
        },
        {
            "name": "Soccer Scrimmage",
            "description": "Small-sided soccer games focusing on skill application and teamwork",
            "type": ActivityType.GAMES,
            "difficulty_level": "INTERMEDIATE",
            "equipment_needed": "Soccer balls, goals, cones",
            "duration": 35,
            "calories_burn_rate": 14.0,
            "target_muscle_groups": "Legs, cardiovascular, coordination",
            "safety_notes": "Use appropriate field size, emphasize control",
            "category": ActivityCategoryType.TEAM,
            "format": ActivityFormat.SMALL_GROUP,
            "goal": ActivityGoal.TEAMWORK,
            "status": ActivityStatus.ACTIVE
        },
        {
            "name": "Interval Running",
            "description": "Alternating periods of running and walking to build endurance",
            "type": ActivityType.CARDIO,
            "difficulty_level": "INTERMEDIATE",
            "equipment_needed": "None",
            "duration": 25,
            "calories_burn_rate": 13.0,
            "target_muscle_groups": "Legs, cardiovascular",
            "safety_notes": "Start with short intervals, build gradually",
            "category": ActivityCategoryType.INDIVIDUAL,
            "format": ActivityFormat.INDIVIDUAL,
            "goal": ActivityGoal.FITNESS,
            "status": ActivityStatus.ACTIVE
        },
        {
            "name": "Strength Training Basics",
            "description": "Basic strength exercises using body weight and light resistance",
            "type": ActivityType.STRENGTH_TRAINING,
            "difficulty_level": "INTERMEDIATE",
            "equipment_needed": "Light weights, resistance bands",
            "duration": 30,
            "calories_burn_rate": 8.0,
            "target_muscle_groups": "Major muscle groups",
            "safety_notes": "Focus on form, start with lighter weights",
            "category": ActivityCategoryType.INDIVIDUAL,
            "format": ActivityFormat.INDIVIDUAL,
            "goal": ActivityGoal.FITNESS,
            "status": ActivityStatus.ACTIVE
        },
        {
            "name": "Agility Drills",
            "description": "Ladder drills, cone drills, and other agility exercises",
            "type": ActivityType.SKILL_DEVELOPMENT,
            "difficulty_level": "INTERMEDIATE",
            "equipment_needed": "Agility ladder, cones",
            "duration": 20,
            "calories_burn_rate": 10.0,
            "target_muscle_groups": "Legs, coordination, agility",
            "safety_notes": "Clear space, proper footwear, start slow",
            "category": ActivityCategoryType.INDIVIDUAL,
            "format": ActivityFormat.INDIVIDUAL,
            "goal": ActivityGoal.COORDINATION,
            "status": ActivityStatus.ACTIVE
        },
        {
            "name": "Team Building Games",
            "description": "Cooperative games that build teamwork and communication skills",
            "type": ActivityType.GAMES,
            "difficulty_level": "INTERMEDIATE",
            "equipment_needed": "Various equipment based on game",
            "duration": 30,
            "calories_burn_rate": 6.0,
            "target_muscle_groups": "Full body, social skills",
            "safety_notes": "Emphasize cooperation over competition",
            "category": ActivityCategoryType.GROUP,
            "format": ActivityFormat.LARGE_GROUP,
            "goal": ActivityGoal.TEAMWORK,
            "status": ActivityStatus.ACTIVE
        },
        {
            "name": "Dance Basics",
            "description": "Basic dance moves and simple choreography for physical education",
            "type": ActivityType.DANCE,
            "difficulty_level": "INTERMEDIATE",
            "equipment_needed": "Music player, open space",
            "duration": 25,
            "calories_burn_rate": 9.0,
            "target_muscle_groups": "Full body, coordination",
            "safety_notes": "Clear space, appropriate music selection",
            "category": ActivityCategoryType.GROUP,
            "format": ActivityFormat.CLASS,
            "goal": ActivityGoal.ENJOYMENT,
            "status": ActivityStatus.ACTIVE
        },
        
        # ADVANCED LEVEL ACTIVITIES
        {
            "name": "Advanced Jump Rope",
            "description": "Advanced jump rope techniques including crossovers, double unders, and complex footwork",
            "type": ActivityType.SKILL_DEVELOPMENT,
            "difficulty_level": "ADVANCED",
            "equipment_needed": "Jump rope",
            "duration": 20,
            "calories_burn_rate": 15.0,
            "target_muscle_groups": "Legs, cardiovascular, coordination",
            "safety_notes": "Master basics first, clear space, proper rope",
            "category": ActivityCategoryType.INDIVIDUAL,
            "format": ActivityFormat.INDIVIDUAL,
            "goal": ActivityGoal.SKILL_DEVELOPMENT,
            "status": ActivityStatus.ACTIVE
        },
        {
            "name": "High-Intensity Interval Training",
            "description": "Advanced HIIT workout with short, intense exercise periods followed by recovery",
            "type": ActivityType.HIIT,
            "difficulty_level": "ADVANCED",
            "equipment_needed": "Timer, various equipment",
            "duration": 35,
            "calories_burn_rate": 18.0,
            "target_muscle_groups": "Full body, cardiovascular",
            "safety_notes": "Proper warm-up, monitor intensity, rest periods",
            "category": ActivityCategoryType.INDIVIDUAL,
            "format": ActivityFormat.INDIVIDUAL,
            "goal": ActivityGoal.FITNESS,
            "status": ActivityStatus.ACTIVE
        },
        {
            "name": "Advanced Basketball Skills",
            "description": "Complex basketball moves including crossovers, spin moves, and advanced shooting",
            "type": ActivityType.SKILL_DEVELOPMENT,
            "difficulty_level": "ADVANCED",
            "equipment_needed": "Basketball, hoops, court",
            "duration": 30,
            "calories_burn_rate": 12.0,
            "target_muscle_groups": "Full body, coordination",
            "safety_notes": "Master basics first, proper court space",
            "category": ActivityCategoryType.INDIVIDUAL,
            "format": ActivityFormat.INDIVIDUAL,
            "goal": ActivityGoal.SKILL_DEVELOPMENT,
            "status": ActivityStatus.ACTIVE
        },
        {
            "name": "Advanced Soccer Skills",
            "description": "Complex soccer techniques including juggling, advanced dribbling, and shooting",
            "type": ActivityType.SKILL_DEVELOPMENT,
            "difficulty_level": "ADVANCED",
            "equipment_needed": "Soccer balls, goals, cones",
            "duration": 30,
            "calories_burn_rate": 13.0,
            "target_muscle_groups": "Legs, coordination, cardiovascular",
            "safety_notes": "Master basics first, clear practice area",
            "category": ActivityCategoryType.INDIVIDUAL,
            "format": ActivityFormat.INDIVIDUAL,
            "goal": ActivityGoal.SKILL_DEVELOPMENT,
            "status": ActivityStatus.ACTIVE
        },
        {
            "name": "Competitive Games",
            "description": "Advanced competitive games with complex rules and strategies",
            "type": ActivityType.GAMES,
            "difficulty_level": "ADVANCED",
            "equipment_needed": "Various equipment based on game",
            "duration": 45,
            "calories_burn_rate": 16.0,
            "target_muscle_groups": "Full body, strategic thinking",
            "safety_notes": "Emphasize fair play, proper warm-up, clear rules",
            "category": ActivityCategoryType.COMPETITIVE,
            "format": ActivityFormat.TEAM,
            "goal": ActivityGoal.COMPETITION,
            "status": ActivityStatus.ACTIVE
        },
        {
            "name": "Advanced Strength Training",
            "description": "Complex strength exercises with increased resistance and advanced techniques",
            "type": ActivityType.STRENGTH_TRAINING,
            "difficulty_level": "ADVANCED",
            "equipment_needed": "Weights, resistance equipment",
            "duration": 40,
            "calories_burn_rate": 10.0,
            "target_muscle_groups": "Major muscle groups, core",
            "safety_notes": "Spotter recommended, proper form essential",
            "category": ActivityCategoryType.INDIVIDUAL,
            "format": ActivityFormat.INDIVIDUAL,
            "goal": ActivityGoal.FITNESS,
            "status": ActivityStatus.ACTIVE
        },
        {
            "name": "Advanced Agility and Speed",
            "description": "Complex agility drills and speed training exercises",
            "type": ActivityType.SKILL_DEVELOPMENT,
            "difficulty_level": "ADVANCED",
            "equipment_needed": "Agility equipment, timing devices",
            "duration": 25,
            "calories_burn_rate": 14.0,
            "target_muscle_groups": "Legs, coordination, speed",
            "safety_notes": "Proper warm-up, clear space, gradual progression",
            "category": ActivityCategoryType.INDIVIDUAL,
            "format": ActivityFormat.INDIVIDUAL,
            "goal": ActivityGoal.COORDINATION,
            "status": ActivityStatus.ACTIVE
        },
        {
            "name": "Advanced Dance and Movement",
            "description": "Complex dance routines and advanced movement patterns",
            "type": ActivityType.DANCE,
            "difficulty_level": "ADVANCED",
            "equipment_needed": "Music player, open space",
            "duration": 30,
            "calories_burn_rate": 12.0,
            "target_muscle_groups": "Full body, coordination, flexibility",
            "safety_notes": "Master basics first, clear space, appropriate music",
            "category": ActivityCategoryType.INDIVIDUAL,
            "format": ActivityFormat.INDIVIDUAL,
            "goal": ActivityGoal.ENJOYMENT,
            "status": ActivityStatus.ACTIVE
        }
    ]

    # Create and add activities
    for activity_data in activities:
        activity = Activity(**activity_data)
        session.add(activity)

    session.commit()
    
    # Verify activities were created
    result = session.execute(text("SELECT id, name, difficulty_level, duration FROM activities ORDER BY id"))
    activities = result.fetchall()
    print(f"\nActivities seeded successfully! Total activities in database: {len(activities)}")
    
    # Print activities by difficulty level
    print("\nActivities by difficulty level:")
    difficulty_groups = {}
    for activity in activities:
        level = activity.difficulty_level
        if level not in difficulty_groups:
            difficulty_groups[level] = []
        difficulty_groups[level].append(activity)
    
    for level, acts in difficulty_groups.items():
        print(f"\n{level} ({len(acts)} activities):")
        for act in acts:
            print(f"  - {act.name} ({act.duration} min)")
    
    # Check for gaps in IDs
    ids = [activity.id for activity in activities]
    if len(ids) > 1:
        gaps = []
        for i in range(1, len(ids)):
            if ids[i] - ids[i-1] > 1:
                gaps.append(f"{ids[i-1]} to {ids[i]}")
        if gaps:
            print(f"\nGaps in activity IDs: {', '.join(gaps)}")
        else:
            print("\nNo gaps in activity IDs") 