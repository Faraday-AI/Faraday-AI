from datetime import datetime, timedelta
import random
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.physical_education.exercise.models import Exercise
from app.models.physical_education.pe_enums.pe_types import (
    ExerciseType,
    ExerciseDifficulty
)

def seed_massive_exercise_library(session):
    """Seed the exercises table with a massive library of 3,000+ exercises."""
    print("Seeding massive exercise library...")
    
    # Get all activities
    activities = session.execute(text("SELECT id, name FROM activities"))
    activity_map = {row.name: row.id for row in activities}
    
    exercises = []
    
    # ============================================================================
    # SYSTEMATIC EXERCISE GENERATION - CARDIO (800+ exercises)
    # ============================================================================
    
    print("Creating massive cardio exercise library...")
    
    # Base cardio activities
    cardio_bases = [
        "Jump Rope", "Running", "Walking", "Cycling", "Swimming", "Rowing", "Elliptical",
        "Stair Climbing", "Mountain Climbing", "Burpees", "Mountain Climbers", "High Knees",
        "Butt Kicks", "Jumping Jacks", "Star Jumps", "Cross Jacks", "Seal Jacks",
        "Power Jacks", "Split Jacks", "Squat Jacks", "Lunge Jacks", "Push-up Jacks",
        "Sprint", "Jog", "March", "Skip", "Gallop", "Slide", "Leap", "Hop", "Jump"
    ]
    
    # Cardio variations
    cardio_variations = [
        "Basic", "Advanced", "Interval", "Endurance", "Speed", "Agility", "Recovery",
        "Power", "Explosive", "Steady State", "Fartlek", "Tempo", "Threshold",
        "Aerobic", "Anaerobic", "Mixed", "Progressive", "Regressive", "Alternating"
    ]
    
    # Cardio modifiers
    cardio_modifiers = [
        "with Resistance", "with Weights", "with Bands", "with Medicine Ball",
        "with Partner", "with Music", "with Timer", "with Distance", "with Time",
        "with Intensity", "with Speed", "with Power", "with Endurance"
    ]
    
    # Generate cardio exercises systematically
    for base in cardio_bases:
        for variation in cardio_variations:
            for modifier in cardio_modifiers:
                for difficulty in ["beginner", "intermediate", "advanced"]:
                    exercise = {
                        "name": f"{variation} {base} {modifier}",
                        "description": f"{variation.lower()} {base.lower()} exercise {modifier.lower()} for cardiovascular fitness",
                        "exercise_type": ExerciseType.CARDIO.value,
                        "difficulty": difficulty,
                        "category": "cardio",
                        "equipment_needed": ["Stopwatch", "Equipment"],
                        "target_muscle_groups": ["legs", "core", "cardiovascular"],
                        "instructions": f"Perform {base.lower()} with {variation.lower()} intensity {modifier.lower()}",
                        "exercise_metadata": {
                            "duration_minutes": random.randint(10, 60),
                            "sets": random.randint(3, 8),
                            "reps": random.randint(20, 150),
                            "rest_time_seconds": random.randint(30, 180),
                            "intensity": random.choice(["LOW", "MEDIUM", "HIGH"])
                        }
                    }
                    exercises.append(exercise)
    
    # ============================================================================
    # SYSTEMATIC EXERCISE GENERATION - STRENGTH (1000+ exercises)
    # ============================================================================
    
    print("Creating massive strength exercise library...")
    
    # Base strength movements
    strength_bases = [
        "Push-up", "Pull-up", "Dip", "Squat", "Lunge", "Plank", "Burpee",
        "Mountain Climber", "Bear Crawl", "Crab Walk", "Inchworm Walk",
        "Wall Walk", "Handstand Hold", "Pike Push-up", "Diamond Push-up",
        "Wide Push-up", "Decline Push-up", "Incline Push-up", "Archer Push-up",
        "One-Arm Push-up", "Plyometric Push-up", "Clap Push-up", "Spiderman Push-up",
        "T Push-up", "Pike Push-up", "Dive Bomber Push-up", "Hindu Push-up"
    ]
    
    # Strength variations
    strength_variations = [
        "Basic", "Advanced", "Modified", "Weighted", "Resistance Band", "Plyometric",
        "Isometric", "Eccentric", "Concentric", "Isokinetic", "Isotonic",
        "Dynamic", "Static", "Explosive", "Slow", "Fast", "Controlled"
    ]
    
    # Strength modifiers
    strength_modifiers = [
        "with Weight", "with Resistance Band", "with Medicine Ball", "with Partner",
        "on Stability Ball", "on TRX", "on Rings", "on Parallel Bars",
        "with Tempo", "with Pause", "with Hold", "with Pulse", "with Twist"
    ]
    
    # Generate strength exercises systematically
    for base in strength_bases:
        for variation in strength_variations:
            for modifier in strength_modifiers:
                for difficulty in ["beginner", "intermediate", "advanced"]:
                    exercise = {
                        "name": f"{variation} {base} {modifier}",
                        "description": f"{variation.lower()} {base.lower()} exercise {modifier.lower()} for strength development",
                        "exercise_type": ExerciseType.STRENGTH.value,
                        "difficulty": difficulty,
                        "category": "strength_training",
                        "equipment_needed": ["Weights", "Resistance bands", "Equipment"],
                        "target_muscle_groups": ["chest", "arms", "shoulders", "core", "legs"],
                        "instructions": f"Perform {base.lower()} with {variation.lower()} technique {modifier.lower()}",
                        "exercise_metadata": {
                            "duration_minutes": random.randint(15, 45),
                            "sets": random.randint(3, 6),
                            "reps": random.randint(8, 30),
                            "rest_time_seconds": random.randint(60, 180),
                            "intensity": random.choice(["MEDIUM", "HIGH"])
                        }
                    }
                    exercises.append(exercise)
    
    # ============================================================================
    # SYSTEMATIC EXERCISE GENERATION - FLEXIBILITY (400+ exercises)
    # ============================================================================
    
    print("Creating massive flexibility exercise library...")
    
    # Base flexibility movements
    flexibility_bases = [
        "Hamstring Stretch", "Quad Stretch", "Calf Stretch", "Hip Flexor Stretch",
        "Butterfly Stretch", "Pigeon Stretch", "Cobra Stretch", "Child's Pose",
        "Cat-Cow Stretch", "Downward Dog", "Upward Dog", "Triangle Pose",
        "Warrior Pose", "Tree Pose", "Mountain Pose", "Chair Pose", "Bridge Pose",
        "Fish Pose", "Locust Pose", "Bow Pose", "Camel Pose", "Eagle Pose"
    ]
    
    # Flexibility variations
    flexibility_variations = [
        "Static", "Dynamic", "PNF", "Active", "Passive", "Assisted", "Resisted",
        "Ballistic", "Slow", "Fast", "Hold", "Pulse", "Bounce", "Flow"
    ]
    
    # Flexibility modifiers
    flexibility_modifiers = [
        "with Partner", "with Strap", "with Block", "with Wall", "with Chair",
        "Seated", "Standing", "Lying", "Kneeling", "with Twist", "with Rotation"
    ]
    
    # Generate flexibility exercises systematically
    for base in flexibility_bases:
        for variation in flexibility_variations:
            for modifier in flexibility_modifiers:
                exercise = {
                    "name": f"{variation} {base} {modifier}",
                    "description": f"{variation.lower()} {base.lower()} {modifier.lower()} for flexibility",
                    "exercise_type": ExerciseType.FLEXIBILITY.value,
                    "difficulty": random.choice(["beginner", "intermediate"]),
                    "category": "flexibility",
                    "equipment_needed": ["Yoga mat", "Strap", "Block"],
                    "target_muscle_groups": ["full_body"],
                    "instructions": f"Perform {base.lower()} with {variation.lower()} technique {modifier.lower()}",
                    "exercise_metadata": {
                        "duration_minutes": random.randint(10, 30),
                        "sets": random.randint(2, 5),
                        "reps": random.randint(1, 5),
                        "rest_time_seconds": random.randint(30, 90),
                        "intensity": "LOW"
                    }
                }
                exercises.append(exercise)
    
    # ============================================================================
    # SYSTEMATIC EXERCISE GENERATION - BALANCE (300+ exercises)
    # ============================================================================
    
    print("Creating massive balance exercise library...")
    
    # Base balance movements
    balance_bases = [
        "Single Leg Balance", "Single Leg Squat", "Single Leg Deadlift",
        "Single Leg Glute Bridge", "Single Leg Calf Raise", "Single Leg Hop",
        "Balance Beam Walk", "Tightrope Walk", "Heel-to-Toe Walk",
        "Standing on One Foot", "Standing on One Foot with Eyes Closed"
    ]
    
    # Balance variations
    balance_variations = [
        "Basic", "Advanced", "Modified", "with Movement", "with Rotation",
        "with Arm Movement", "with Leg Movement", "with Head Movement",
        "with Eyes Closed", "with Distraction", "with Partner"
    ]
    
    # Balance modifiers
    balance_modifiers = [
        "on Stable Surface", "on Unstable Surface", "on Balance Board", "on Bosu Ball",
        "on Stability Ball", "on Foam Roller", "with Weight", "with Movement"
    ]
    
    # Generate balance exercises systematically
    for base in balance_bases:
        for variation in balance_variations:
            for modifier in balance_modifiers:
                exercise = {
                    "name": f"{variation} {base} {modifier}",
                    "description": f"{variation.lower()} {base.lower()} {modifier.lower()} for balance development",
                    "exercise_type": ExerciseType.BALANCE.value,
                    "difficulty": random.choice(["beginner", "intermediate", "advanced"]),
                    "category": "balance",
                    "equipment_needed": ["Balance equipment", "Stability tools"],
                    "target_muscle_groups": ["legs", "core", "ankles"],
                    "instructions": f"Perform {base.lower()} with {variation.lower()} technique {modifier.lower()}",
                    "exercise_metadata": {
                        "duration_minutes": random.randint(10, 25),
                        "sets": random.randint(3, 6),
                        "reps": random.randint(1, 15),
                        "rest_time_seconds": random.randint(30, 90),
                        "intensity": "MEDIUM"
                    }
                }
                exercises.append(exercise)
    
    # ============================================================================
    # SYSTEMATIC EXERCISE GENERATION - COORDINATION (300+ exercises)
    # ============================================================================
    
    print("Creating massive coordination exercise library...")
    
    # Base coordination movements
    coordination_bases = [
        "Agility Ladder Drills", "Cone Drills", "Ball Tossing", "Ball Catching",
        "Juggling", "Hand-Eye Coordination", "Foot-Eye Coordination",
        "Cross-Crawl Exercises", "Opposite Arm/Leg Movements", "Rhythm Exercises"
    ]
    
    # Coordination variations
    coordination_variations = [
        "Basic", "Advanced", "Modified", "with Speed", "with Accuracy",
        "with Rhythm", "with Partner", "with Equipment", "with Music"
    ]
    
    # Coordination modifiers
    coordination_modifiers = [
        "Forward", "Backward", "Sideways", "Diagonal", "Circular",
        "with Direction Change", "with Speed Change", "with Rhythm Change"
    ]
    
    # Generate coordination exercises systematically
    for base in coordination_bases:
        for variation in coordination_variations:
            for modifier in coordination_modifiers:
                exercise = {
                    "name": f"{variation} {base} {modifier}",
                    "description": f"{variation.lower()} {base.lower()} {modifier.lower()} for coordination",
                    "exercise_type": ExerciseType.COORDINATION.value,
                    "difficulty": random.choice(["beginner", "intermediate", "advanced"]),
                    "category": "coordination",
                    "equipment_needed": ["Agility equipment", "Balls", "Cones"],
                    "target_muscle_groups": ["full_body"],
                    "instructions": f"Perform {base.lower()} with {variation.lower()} technique {modifier.lower()}",
                    "exercise_metadata": {
                        "duration_minutes": random.randint(15, 35),
                        "sets": random.randint(3, 7),
                        "reps": random.randint(10, 40),
                        "rest_time_seconds": random.randint(45, 120),
                        "intensity": "MEDIUM"
                    }
                }
                exercises.append(exercise)
    
    # ============================================================================
    # SYSTEMATIC EXERCISE GENERATION - SPORTS SKILLS (500+ exercises)
    # ============================================================================
    
    print("Creating massive sports skill exercise library...")
    
    # Sports
    sports = [
        "Basketball", "Soccer", "Football", "Baseball", "Softball", "Volleyball",
        "Tennis", "Badminton", "Table Tennis", "Golf", "Hockey", "Lacrosse",
        "Field Hockey", "Rugby", "Cricket", "Rowing", "Swimming", "Track & Field"
    ]
    
    # Sports skills
    sports_skills = [
        "Dribbling", "Shooting", "Passing", "Receiving", "Catching", "Throwing",
        "Kicking", "Heading", "Tackling", "Blocking", "Serving", "Volleying",
        "Swinging", "Putting", "Pitching", "Batting", "Fielding", "Running"
    ]
    
    # Skill variations
    skill_variations = [
        "Basic", "Advanced", "Modified", "with Speed", "with Accuracy",
        "with Power", "with Control", "with Movement", "with Partner"
    ]
    
    # Generate sports skill exercises systematically
    for sport in sports:
        for skill in sports_skills:
            for variation in skill_variations:
                for difficulty in ["beginner", "intermediate", "advanced"]:
                    exercise = {
                        "name": f"{variation} {sport} {skill}",
                        "description": f"{variation.lower()} {sport.lower()} {skill.lower()} for skill development",
                        "exercise_type": ExerciseType.SKILL.value,
                        "difficulty": difficulty,
                        "category": "skill_development",
                        "equipment_needed": [f"{sport.lower()} equipment"],
                        "target_muscle_groups": ["full_body"],
                        "instructions": f"Practice {sport.lower()} {skill.lower()} with {variation.lower()} technique",
                        "exercise_metadata": {
                            "duration_minutes": random.randint(20, 50),
                            "sets": random.randint(4, 8),
                            "reps": random.randint(20, 60),
                            "rest_time_seconds": random.randint(60, 150),
                            "intensity": "MEDIUM"
                        }
                    }
                    exercises.append(exercise)
    
    # ============================================================================
    # SYSTEMATIC EXERCISE GENERATION - TEAM SPORTS (200+ exercises)
    # ============================================================================
    
    print("Creating massive team sports exercise library...")
    
    # Team sports
    team_sports = [
        "Basketball", "Soccer", "Volleyball", "Baseball", "Softball",
        "Football", "Hockey", "Lacrosse", "Field Hockey", "Rugby"
    ]
    
    # Team activities
    team_activities = [
        "Team Practice", "Scrimmage", "Game", "Drill", "Strategy Session",
        "Team Building", "Communication Exercise", "Leadership Development"
    ]
    
    # Team variations
    team_variations = [
        "Basic", "Advanced", "Modified", "with Focus", "with Pressure",
        "with Time Limit", "with Scoring", "with Competition"
    ]
    
    # Generate team sports exercises systematically
    for sport in team_sports:
        for activity in team_activities:
            for variation in team_variations:
                exercise = {
                    "name": f"{variation} {sport} {activity}",
                    "description": f"{variation.lower()} {sport.lower()} {activity.lower()} for team development",
                    "exercise_type": ExerciseType.SPORTS.value,
                    "difficulty": random.choice(["beginner", "intermediate", "advanced"]),
                    "category": "team_sports",
                    "equipment_needed": [f"{sport.lower()} equipment"],
                    "target_muscle_groups": ["full_body"],
                    "instructions": f"Participate in {sport.lower()} {activity.lower()} with {variation.lower()} approach",
                    "exercise_metadata": {
                        "duration_minutes": random.randint(45, 120),
                        "sets": random.randint(1, 4),
                        "reps": random.randint(1, 1),
                        "rest_time_seconds": random.randint(120, 300),
                        "intensity": "HIGH"
                    }
                }
                exercises.append(exercise)
    
    # ============================================================================
    # SYSTEMATIC EXERCISE GENERATION - FITNESS TRAINING (400+ exercises)
    # ============================================================================
    
    print("Creating massive fitness training exercise library...")
    
    # Fitness training types
    fitness_types = [
        "Circuit Training", "HIIT", "Tabata", "CrossFit", "Functional Training",
        "Core Training", "Upper Body Training", "Lower Body Training", "Full Body Training"
    ]
    
    # Fitness variations
    fitness_variations = [
        "Basic", "Advanced", "Modified", "with Equipment", "without Equipment",
        "with Weights", "with Resistance Bands", "with Bodyweight"
    ]
    
    # Fitness modifiers
    fitness_modifiers = [
        "for Beginners", "for Intermediates", "for Advanced", "for Athletes",
        "for Seniors", "for Youth", "for Rehabilitation", "for Performance"
    ]
    
    # Generate fitness training exercises systematically
    for fitness_type in fitness_types:
        for variation in fitness_variations:
            for modifier in fitness_modifiers:
                exercise = {
                    "name": f"{variation} {fitness_type} {modifier}",
                    "description": f"{variation.lower()} {fitness_type.lower()} {modifier.lower()}",
                    "exercise_type": ExerciseType.STRENGTH.value,
                    "difficulty": random.choice(["beginner", "intermediate", "advanced"]),
                    "category": "strength_training",
                    "equipment_needed": ["Fitness equipment", "Weights", "Bands"],
                    "target_muscle_groups": ["full_body"],
                    "instructions": f"Complete {fitness_type.lower()} with {variation.lower()} approach {modifier.lower()}",
                    "exercise_metadata": {
                        "duration_minutes": random.randint(30, 90),
                        "sets": random.randint(3, 8),
                        "reps": random.randint(10, 30),
                        "rest_time_seconds": random.randint(30, 120),
                        "intensity": random.choice(["MEDIUM", "HIGH"])
                    }
                }
                exercises.append(exercise)
    
    # ============================================================================
    # SYSTEMATIC EXERCISE GENERATION - RECREATIONAL ACTIVITIES (200+ exercises)
    # ============================================================================
    
    print("Creating massive recreational activities library...")
    
    # Recreational activities
    recreational_activities = [
        "Dance", "Yoga", "Pilates", "Martial Arts", "Swimming",
        "Hiking", "Cycling", "Rock Climbing", "Kayaking", "Paddleboarding",
        "Skating", "Skiing", "Snowboarding", "Surfing", "Tennis",
        "Golf", "Bowling", "Archery", "Fencing", "Boxing"
    ]
    
    # Activity variations
    activity_variations = [
        "Basic", "Advanced", "Modified", "with Instruction", "with Partner",
        "with Group", "with Equipment", "without Equipment"
    ]
    
    # Activity modifiers
    activity_modifiers = [
        "for Beginners", "for Intermediates", "for Advanced", "for Fun",
        "for Competition", "for Recreation", "for Fitness", "for Skill"
    ]
    
    # Generate recreational activities systematically
    for activity in recreational_activities:
        for variation in activity_variations:
            for modifier in activity_modifiers:
                exercise = {
                    "name": f"{variation} {activity} {modifier}",
                    "description": f"{variation.lower()} {activity.lower()} {modifier.lower()}",
                    "exercise_type": ExerciseType.RECREATIONAL.value,
                    "difficulty": random.choice(["beginner", "intermediate", "advanced"]),
                    "category": "recreational",
                    "equipment_needed": [f"{activity.lower()} equipment"],
                    "target_muscle_groups": ["full_body"],
                    "instructions": f"Participate in {activity.lower()} with {variation.lower()} approach {modifier.lower()}",
                    "exercise_metadata": {
                        "duration_minutes": random.randint(30, 150),
                        "sets": random.randint(1, 3),
                        "reps": random.randint(1, 1),
                        "rest_time_seconds": random.randint(0, 90),
                        "intensity": random.choice(["LOW", "MEDIUM", "HIGH"])
                    }
                }
                exercises.append(exercise)
    
    # ============================================================================
    # SYSTEMATIC EXERCISE GENERATION - THERAPEUTIC & ADAPTIVE (300+ exercises)
    # ============================================================================
    
    print("Creating massive therapeutic and adaptive exercise library...")
    
    # Therapeutic exercises
    therapeutic_exercises = [
        "Seated Exercise Routine", "Chair-Based Workout", "Bed Exercises",
        "Wheelchair Exercises", "Low-Impact Cardio", "Gentle Stretching",
        "Balance Exercises", "Coordination Drills", "Range of Motion",
        "Strength Building", "Endurance Training", "Flexibility Work"
    ]
    
    # Therapeutic variations
    therapeutic_variations = [
        "Basic", "Modified", "Assisted", "Independent", "with Support",
        "with Equipment", "without Equipment", "with Partner", "Solo"
    ]
    
    # Therapeutic modifiers
    therapeutic_modifiers = [
        "for Rehabilitation", "for Seniors", "for Youth", "for Special Needs",
        "for Recovery", "for Maintenance", "for Improvement", "for Prevention"
    ]
    
    # Generate therapeutic exercises systematically
    for exercise in therapeutic_exercises:
        for variation in therapeutic_variations:
            for modifier in therapeutic_modifiers:
                exercise_data = {
                    "name": f"{variation} {exercise} {modifier}",
                    "description": f"{variation.lower()} {exercise.lower()} {modifier.lower()}",
                    "exercise_type": ExerciseType.THERAPEUTIC.value,
                    "difficulty": "beginner",
                    "category": "therapeutic",
                    "equipment_needed": ["Chair", "Support equipment"],
                    "target_muscle_groups": ["full_body"],
                    "instructions": f"Perform {exercise.lower()} with {variation.lower()} approach {modifier.lower()}",
                    "exercise_metadata": {
                        "duration_minutes": random.randint(20, 50),
                        "sets": random.randint(2, 5),
                        "reps": random.randint(8, 20),
                        "rest_time_seconds": random.randint(60, 150),
                        "intensity": "LOW"
                    }
                }
                exercises.append(exercise_data)
    
    # ============================================================================
    # SYSTEMATIC EXERCISE GENERATION - MOBILITY & RECOVERY (200+ exercises)
    # ============================================================================
    
    print("Creating massive mobility and recovery exercise library...")
    
    # Mobility exercises
    mobility_exercises = [
        "Joint Mobility", "Hip Mobility", "Shoulder Mobility", "Ankle Mobility",
        "Thoracic Mobility", "Cervical Mobility", "Lumbar Mobility",
        "Wrist Mobility", "Elbow Mobility", "Knee Mobility"
    ]
    
    # Recovery exercises
    recovery_exercises = [
        "Foam Rolling", "Stretching", "Light Walking", "Gentle Swimming",
        "Recovery Yoga", "Meditation", "Breathing Exercises", "Light Cycling"
    ]
    
    # Mobility variations
    mobility_variations = [
        "Basic", "Advanced", "Modified", "with Movement", "with Hold",
        "with Flow", "with Control", "with Range", "with Strength"
    ]
    
    # Generate mobility and recovery exercises systematically
    for exercise in mobility_exercises + recovery_exercises:
        for variation in mobility_variations:
            exercise_data = {
                "name": f"{variation} {exercise}",
                "description": f"{variation.lower()} {exercise.lower()} for mobility and recovery",
                "exercise_type": ExerciseType.MOBILITY.value if "Mobility" in exercise else ExerciseType.RECOVERY.value,
                "difficulty": random.choice(["beginner", "intermediate"]),
                "category": "mobility" if "Mobility" in exercise else "recovery",
                "equipment_needed": ["Foam roller"] if "Foam Rolling" in exercise else [],
                "target_muscle_groups": ["full_body"],
                "instructions": f"Perform {exercise.lower()} with {variation.lower()} approach",
                "exercise_metadata": {
                    "duration_minutes": random.randint(15, 40),
                    "sets": random.randint(2, 4),
                    "reps": random.randint(8, 20),
                    "rest_time_seconds": random.randint(30, 90),
                    "intensity": "LOW"
                }
            }
            exercises.append(exercise_data)
    
    # ============================================================================
    # SYSTEMATIC EXERCISE GENERATION - PLYOMETRIC (150+ exercises)
    # ============================================================================
    
    print("Creating massive plyometric exercise library...")
    
    # Plyometric exercises
    plyometric_exercises = [
        "Box Jumps", "Depth Jumps", "Bounding", "Plyometric Push-ups",
        "Clap Push-ups", "Medicine Ball Throws", "Plyometric Lunges",
        "Jump Squats", "Tuck Jumps", "Split Jumps", "Broad Jumps",
        "Plyometric Pull-ups", "Plyometric Dips", "Plyometric Burpees"
    ]
    
    # Plyometric variations
    plyometric_variations = [
        "Basic", "Advanced", "Modified", "with Height", "with Distance",
        "with Speed", "with Power", "with Control", "with Landing"
    ]
    
    # Plyometric modifiers
    plyometric_modifiers = [
        "Single Leg", "Double Leg", "Alternating", "with Rotation",
        "with Direction Change", "with Landing Control", "with Recovery"
    ]
    
    # Generate plyometric exercises systematically
    for exercise in plyometric_exercises:
        for variation in plyometric_variations:
            for modifier in plyometric_modifiers:
                exercise_data = {
                    "name": f"{variation} {exercise} {modifier}",
                    "description": f"{variation.lower()} {exercise.lower()} {modifier.lower()} for power development",
                    "exercise_type": ExerciseType.PLYOMETRIC.value,
                    "difficulty": random.choice(["intermediate", "advanced"]),
                    "category": "strength_training",
                    "equipment_needed": ["Boxes", "Medicine balls", "Equipment"],
                    "target_muscle_groups": ["legs", "core", "arms"],
                    "instructions": f"Perform {exercise.lower()} with {variation.lower()} technique {modifier.lower()}",
                    "exercise_metadata": {
                        "duration_minutes": random.randint(20, 45),
                        "sets": random.randint(3, 6),
                        "reps": random.randint(6, 20),
                        "rest_time_seconds": random.randint(90, 240),
                        "intensity": "HIGH"
                    }
                }
                exercises.append(exercise_data)
    
    # ============================================================================
    # CREATE ALL EXERCISES
    # ============================================================================
    
    print(f"Creating {len(exercises)} exercises...")
    
    for exercise_data in exercises:
        exercise = Exercise(**exercise_data)
        session.add(exercise)

    session.commit()
    print(f"Successfully seeded {len(exercises)} comprehensive exercises!")
    print(f"Massive exercise library now includes:")
    print(f"  - Cardio exercises: {len([e for e in exercises if e['exercise_type'] == ExerciseType.CARDIO.value])}")
    print(f"  - Strength exercises: {len([e for e in exercises if e['exercise_type'] == ExerciseType.STRENGTH.value])}")
    print(f"  - Flexibility exercises: {len([e for e in exercises if e['exercise_type'] == ExerciseType.FLEXIBILITY.value])}")
    print(f"  - Balance exercises: {len([e for e in exercises if e['exercise_type'] == ExerciseType.BALANCE.value])}")
    print(f"  - Coordination exercises: {len([e for e in exercises if e['exercise_type'] == ExerciseType.COORDINATION.value])}")
    print(f"  - Sports skill exercises: {len([e for e in exercises if e['exercise_type'] == ExerciseType.SKILL.value])}")
    print(f"  - Team sports exercises: {len([e for e in exercises if e['exercise_type'] == ExerciseType.SPORTS.value])}")
    print(f"  - And many more categories...")
    print(f"Total exercises created: {len(exercises)}")

if __name__ == "__main__":
    from app.core.database import get_db
    session = next(get_db())
    seed_massive_exercise_library(session) 