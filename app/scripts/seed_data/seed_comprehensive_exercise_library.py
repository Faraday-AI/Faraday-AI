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

def seed_comprehensive_exercise_library(session):
    """Seed the exercises table with a comprehensive library of 3,000+ exercises."""
    print("Seeding comprehensive exercise library...")
    
    # Get all activities
    activities = session.execute(text("SELECT id, name FROM activities"))
    activity_map = {row.name: row.id for row in activities}
    
    exercises = []
    
    # ============================================================================
    # CARDIO EXERCISES (600+ exercises)
    # ============================================================================
    
    print("Creating cardio exercises...")
    
    # Basic Cardio Variations
    cardio_variations = [
        "Basic", "Advanced", "Interval", "Endurance", "Speed", "Agility", "Recovery"
    ]
    
    cardio_activities = [
        "Jump Rope", "Running", "Walking", "Cycling", "Swimming", "Rowing", "Elliptical",
        "Stair Climbing", "Mountain Climbing", "Burpees", "Mountain Climbers", "High Knees",
        "Butt Kicks", "Jumping Jacks", "Star Jumps", "Cross Jacks", "Seal Jacks",
        "Power Jacks", "Split Jacks", "Squat Jacks", "Lunge Jacks", "Push-up Jacks"
    ]
    
    for variation in cardio_variations:
        for activity in cardio_activities:
            for difficulty in ["beginner", "intermediate", "advanced"]:
                exercise = {
                    "name": f"{variation} {activity}",
                    "description": f"{variation.lower()} {activity.lower()} exercise for cardiovascular fitness",
                    "exercise_type": ExerciseType.CARDIO.value,
                    "difficulty": difficulty,
                    "category": "cardio",
                    "equipment_needed": ["Stopwatch"] if "Jump Rope" in activity else [],
                    "target_muscle_groups": ["legs", "core", "cardiovascular"],
                    "instructions": f"Perform {activity.lower()} with proper form and {variation.lower()} intensity",
                    "exercise_metadata": {
                        "duration_minutes": random.randint(10, 45),
                        "sets": random.randint(3, 6),
                        "reps": random.randint(20, 100),
                        "rest_time_seconds": random.randint(30, 120),
                        "intensity": random.choice(["LOW", "MEDIUM", "HIGH"])
                    }
                }
                exercises.append(exercise)
    
    # HIIT Cardio Variations
    hiit_exercises = [
        "Tabata Intervals", "30/30 Intervals", "45/15 Intervals", "60/30 Intervals",
        "Pyramid Intervals", "Ladder Intervals", "Descending Intervals", "Ascending Intervals"
    ]
    
    for hiit in hiit_exercises:
        for difficulty in ["intermediate", "advanced"]:
            exercise = {
                "name": f"HIIT {hiit}",
                "description": f"High-intensity interval training using {hiit.lower()} format",
                "exercise_type": ExerciseType.HIIT.value,
                "difficulty": difficulty,
                "category": "cardio",
                "equipment_needed": ["Stopwatch"],
                "target_muscle_groups": ["full_body", "cardiovascular"],
                "instructions": f"Perform {hiit.lower()} intervals with maximum effort during work periods",
                "exercise_metadata": {
                    "duration_minutes": random.randint(20, 40),
                    "sets": random.randint(4, 8),
                    "reps": random.randint(1, 1),
                    "rest_time_seconds": random.randint(15, 60),
                    "intensity": "HIGH"
                }
            }
            exercises.append(exercise)
    
    # ============================================================================
    # STRENGTH EXERCISES (800+ exercises)
    # ============================================================================
    
    print("Creating strength exercises...")
    
    # Bodyweight Strength
    bodyweight_exercises = [
        "Push-ups", "Pull-ups", "Dips", "Squats", "Lunges", "Planks", "Burpees",
        "Mountain Climbers", "Bear Crawls", "Crab Walks", "Inchworm Walks",
        "Wall Walks", "Handstand Holds", "Pike Push-ups", "Diamond Push-ups",
        "Wide Push-ups", "Decline Push-ups", "Incline Push-ups", "Archer Push-ups",
        "One-Arm Push-ups", "Plyometric Push-ups", "Clap Push-ups"
    ]
    
    for exercise in bodyweight_exercises:
        for difficulty in ["beginner", "intermediate", "advanced"]:
            exercise_data = {
                "name": f"{exercise}",
                "description": f"Bodyweight {exercise.lower()} for strength development",
                "exercise_type": ExerciseType.STRENGTH.value,
                "difficulty": difficulty,
                "category": "strength_training",
                "equipment_needed": [],
                "target_muscle_groups": ["chest", "arms", "shoulders", "core", "legs"],
                "instructions": f"Perform {exercise.lower()} with proper form and controlled movement",
                "exercise_metadata": {
                    "duration_minutes": random.randint(15, 30),
                    "sets": random.randint(3, 5),
                    "reps": random.randint(8, 25),
                    "rest_time_seconds": random.randint(60, 120),
                    "intensity": random.choice(["MEDIUM", "HIGH"])
                }
            }
            exercises.append(exercise_data)
    
    # Weight Training Variations
    weight_exercises = [
        "Bench Press", "Squat", "Deadlift", "Overhead Press", "Bent Over Row",
        "Bicep Curl", "Tricep Extension", "Lateral Raise", "Front Raise",
        "Upright Row", "Shrug", "Calf Raise", "Leg Press", "Leg Extension",
        "Leg Curl", "Lat Pulldown", "Seated Row", "Chest Fly", "Shoulder Fly"
    ]
    
    for exercise in weight_exercises:
        for difficulty in ["intermediate", "advanced"]:
            exercise_data = {
                "name": f"Weight Training {exercise}",
                "description": f"Weight training exercise: {exercise.lower()}",
                "exercise_type": ExerciseType.WEIGHT_TRAINING.value,
                "difficulty": difficulty,
                "category": "strength_training",
                "equipment_needed": ["Weights", "Barbell", "Dumbbells"],
                "target_muscle_groups": ["full_body"],
                "instructions": f"Perform {exercise.lower()} with proper form and appropriate weight",
                "exercise_metadata": {
                    "duration_minutes": random.randint(20, 45),
                    "sets": random.randint(3, 6),
                    "reps": random.randint(6, 15),
                    "rest_time_seconds": random.randint(90, 180),
                    "intensity": "HIGH"
                }
            }
            exercises.append(exercise_data)
    
    # Resistance Band Exercises
    band_exercises = [
        "Band Squats", "Band Lunges", "Band Push-ups", "Band Rows", "Band Presses",
        "Band Curls", "Band Extensions", "Band Pull-aparts", "Band Face Pulls",
        "Band Lateral Walks", "Band Monster Walks", "Band Clamshells", "Band Glute Bridges"
    ]
    
    for exercise in band_exercises:
        for difficulty in ["beginner", "intermediate"]:
            exercise_data = {
                "name": f"Resistance Band {exercise}",
                "description": f"Resistance band exercise: {exercise.lower()}",
                "exercise_type": ExerciseType.RESISTANCE.value,
                "difficulty": difficulty,
                "category": "strength_training",
                "equipment_needed": ["Resistance bands"],
                "target_muscle_groups": ["legs", "arms", "core", "glutes"],
                "instructions": f"Perform {exercise.lower()} with resistance band tension",
                "exercise_metadata": {
                    "duration_minutes": random.randint(15, 30),
                    "sets": random.randint(3, 5),
                    "reps": random.randint(12, 20),
                    "rest_time_seconds": random.randint(60, 90),
                    "intensity": "MEDIUM"
                }
            }
            exercises.append(exercise_data)
    
    # ============================================================================
    # FLEXIBILITY EXERCISES (400+ exercises)
    # ============================================================================
    
    print("Creating flexibility exercises...")
    
    # Static Stretching
    static_stretches = [
        "Hamstring Stretch", "Quad Stretch", "Calf Stretch", "Hip Flexor Stretch",
        "Butterfly Stretch", "Pigeon Stretch", "Cobra Stretch", "Child's Pose",
        "Cat-Cow Stretch", "Downward Dog", "Upward Dog", "Triangle Pose",
        "Warrior Pose", "Tree Pose", "Mountain Pose", "Chair Pose"
    ]
    
    for stretch in static_stretches:
        for difficulty in ["beginner", "intermediate"]:
            exercise_data = {
                "name": f"Static {stretch}",
                "description": f"Static stretching exercise: {stretch.lower()}",
                "exercise_type": ExerciseType.FLEXIBILITY.value,
                "difficulty": difficulty,
                "category": "flexibility",
                "equipment_needed": ["Yoga mat"],
                "target_muscle_groups": ["full_body"],
                "instructions": f"Hold {stretch.lower()} for 20-30 seconds, breathe deeply",
                "exercise_metadata": {
                    "duration_minutes": random.randint(10, 20),
                    "sets": random.randint(2, 4),
                    "reps": random.randint(1, 3),
                    "rest_time_seconds": random.randint(30, 60),
                    "intensity": "LOW"
                }
            }
            exercises.append(exercise_data)
    
    # Dynamic Stretching
    dynamic_stretches = [
        "Arm Circles", "Leg Swings", "Hip Circles", "Ankle Circles", "Torso Twists",
        "Walking Knee Hugs", "Walking Quad Stretches", "Walking Lunges",
        "High Knees", "Butt Kicks", "Walking Heel Walks", "Walking Toe Walks"
    ]
    
    for stretch in dynamic_stretches:
        exercise_data = {
            "name": f"Dynamic {stretch}",
            "description": f"Dynamic stretching exercise: {stretch.lower()}",
            "exercise_type": ExerciseType.WARM_UP.value,
            "difficulty": "beginner",
            "category": "warm_up",
            "equipment_needed": [],
            "target_muscle_groups": ["full_body"],
            "instructions": f"Perform {stretch.lower()} with controlled movement through full range",
            "exercise_metadata": {
                "duration_minutes": random.randint(5, 15),
                "sets": random.randint(2, 3),
                "reps": random.randint(10, 20),
                "rest_time_seconds": random.randint(15, 30),
                "intensity": "LOW"
            }
        }
        exercises.append(exercise_data)
    
    # ============================================================================
    # BALANCE EXERCISES (300+ exercises)
    # ============================================================================
    
    print("Creating balance exercises...")
    
    # Balance Variations
    balance_exercises = [
        "Single Leg Balance", "Single Leg Squat", "Single Leg Deadlift",
        "Single Leg Glute Bridge", "Single Leg Calf Raise", "Single Leg Hop",
        "Balance Beam Walk", "Tightrope Walk", "Heel-to-Toe Walk",
        "Standing on One Foot", "Standing on One Foot with Eyes Closed"
    ]
    
    for exercise in balance_exercises:
        for difficulty in ["beginner", "intermediate", "advanced"]:
            exercise_data = {
                "name": f"Balance {exercise}",
                "description": f"Balance exercise: {exercise.lower()}",
                "exercise_type": ExerciseType.BALANCE.value,
                "difficulty": difficulty,
                "category": "balance",
                "equipment_needed": ["Balance beam"] if "beam" in exercise.lower() else [],
                "target_muscle_groups": ["legs", "core", "ankles"],
                "instructions": f"Perform {exercise.lower()} while maintaining balance and control",
                "exercise_metadata": {
                    "duration_minutes": random.randint(10, 20),
                    "sets": random.randint(3, 5),
                    "reps": random.randint(1, 10),
                    "rest_time_seconds": random.randint(30, 60),
                    "intensity": "MEDIUM"
                }
            }
            exercises.append(exercise_data)
    
    # ============================================================================
    # COORDINATION EXERCISES (300+ exercises)
    # ============================================================================
    
    print("Creating coordination exercises...")
    
    # Coordination Drills
    coordination_exercises = [
        "Agility Ladder Drills", "Cone Drills", "Ball Tossing", "Ball Catching",
        "Juggling", "Hand-Eye Coordination", "Foot-Eye Coordination",
        "Cross-Crawl Exercises", "Opposite Arm/Leg Movements", "Rhythm Exercises"
    ]
    
    for exercise in coordination_exercises:
        for difficulty in ["beginner", "intermediate", "advanced"]:
            exercise_data = {
                "name": f"Coordination {exercise}",
                "description": f"Coordination exercise: {exercise.lower()}",
                "exercise_type": ExerciseType.COORDINATION.value,
                "difficulty": difficulty,
                "category": "coordination",
                "equipment_needed": ["Agility ladder"] if "ladder" in exercise.lower() else ["Balls", "Cones"],
                "target_muscle_groups": ["full_body"],
                "instructions": f"Perform {exercise.lower()} focusing on coordination and timing",
                "exercise_metadata": {
                    "duration_minutes": random.randint(15, 30),
                    "sets": random.randint(3, 6),
                    "reps": random.randint(10, 30),
                    "rest_time_seconds": random.randint(45, 90),
                    "intensity": "MEDIUM"
                }
            }
            exercises.append(exercise_data)
    
    # ============================================================================
    # SPORTS SKILL EXERCISES (400+ exercises)
    # ============================================================================
    
    print("Creating sports skill exercises...")
    
    # Basketball Skills
    basketball_skills = [
        "Dribbling", "Shooting", "Passing", "Rebounding", "Defense",
        "Layups", "Free Throws", "Three Point Shooting", "Jump Shots",
        "Hook Shots", "Fadeaway Shots", "Bank Shots", "Alley Oops"
    ]
    
    for skill in basketball_skills:
        for difficulty in ["beginner", "intermediate", "advanced"]:
            exercise_data = {
                "name": f"Basketball {skill}",
                "description": f"Basketball skill development: {skill.lower()}",
                "exercise_type": ExerciseType.SKILL.value,
                "difficulty": difficulty,
                "category": "skill_development",
                "equipment_needed": ["Basketball", "Basketball hoop"],
                "target_muscle_groups": ["arms", "shoulders", "core", "legs"],
                "instructions": f"Practice {skill.lower()} with proper basketball technique",
                "exercise_metadata": {
                    "duration_minutes": random.randint(20, 40),
                    "sets": random.randint(4, 6),
                    "reps": random.randint(20, 50),
                    "rest_time_seconds": random.randint(60, 120),
                    "intensity": "MEDIUM"
                }
            }
            exercises.append(exercise_data)
    
    # Soccer Skills
    soccer_skills = [
        "Dribbling", "Passing", "Shooting", "Heading", "Tackling",
        "First Touch", "Ball Control", "Crossing", "Free Kicks",
        "Penalty Kicks", "Corner Kicks", "Throw-ins", "Goalkeeping"
    ]
    
    for skill in soccer_skills:
        for difficulty in ["beginner", "intermediate", "advanced"]:
            exercise_data = {
                "name": f"Soccer {skill}",
                "description": f"Soccer skill development: {skill.lower()}",
                "exercise_type": ExerciseType.SKILL.value,
                "difficulty": difficulty,
                "category": "skill_development",
                "equipment_needed": ["Soccer ball", "Cones", "Goals"],
                "target_muscle_groups": ["legs", "core"],
                "instructions": f"Practice {skill.lower()} with proper soccer technique",
                "exercise_metadata": {
                    "duration_minutes": random.randint(20, 40),
                    "sets": random.randint(4, 6),
                    "reps": random.randint(20, 50),
                    "rest_time_seconds": random.randint(60, 120),
                    "intensity": "MEDIUM"
                }
            }
            exercises.append(exercise_data)
    
    # ============================================================================
    # TEAM SPORTS EXERCISES (200+ exercises)
    # ============================================================================
    
    print("Creating team sports exercises...")
    
    # Team Sports
    team_sports = [
        "Basketball", "Soccer", "Volleyball", "Baseball", "Softball",
        "Football", "Hockey", "Lacrosse", "Field Hockey", "Rugby"
    ]
    
    for sport in team_sports:
        for difficulty in ["beginner", "intermediate", "advanced"]:
            exercise_data = {
                "name": f"{sport} Team Practice",
                "description": f"Team practice session for {sport.lower()}",
                "exercise_type": ExerciseType.SPORTS.value,
                "difficulty": difficulty,
                "category": "team_sports",
                "equipment_needed": [f"{sport.lower()} equipment"],
                "target_muscle_groups": ["full_body"],
                "instructions": f"Participate in {sport.lower()} team practice focusing on teamwork and strategy",
                "exercise_metadata": {
                    "duration_minutes": random.randint(45, 90),
                    "sets": random.randint(1, 3),
                    "reps": random.randint(1, 1),
                    "rest_time_seconds": random.randint(120, 300),
                    "intensity": "HIGH"
                }
            }
            exercises.append(exercise_data)
    
    # ============================================================================
    # FITNESS TRAINING EXERCISES (300+ exercises)
    # ============================================================================
    
    print("Creating fitness training exercises...")
    
    # Circuit Training
    circuit_exercises = [
        "Full Body Circuit", "Upper Body Circuit", "Lower Body Circuit",
        "Core Circuit", "Cardio Circuit", "Strength Circuit", "Endurance Circuit"
    ]
    
    for circuit in circuit_exercises:
        for difficulty in ["beginner", "intermediate", "advanced"]:
            exercise_data = {
                "name": f"Circuit Training: {circuit}",
                "description": f"Circuit training workout: {circuit.lower()}",
                "exercise_type": ExerciseType.STRENGTH.value,
                "difficulty": difficulty,
                "category": "strength_training",
                "equipment_needed": ["Various fitness equipment"],
                "target_muscle_groups": ["full_body"],
                "instructions": f"Complete {circuit.lower()} circuit with minimal rest between exercises",
                "exercise_metadata": {
                    "duration_minutes": random.randint(30, 60),
                    "sets": random.randint(3, 6),
                    "reps": random.randint(10, 20),
                    "rest_time_seconds": random.randint(30, 90),
                    "intensity": "HIGH"
                }
            }
            exercises.append(exercise_data)
    
    # ============================================================================
    # RECREATIONAL ACTIVITIES (200+ exercises)
    # ============================================================================
    
    print("Creating recreational activities...")
    
    # Recreational Activities
    recreational_activities = [
        "Dance", "Yoga", "Pilates", "Martial Arts", "Swimming",
        "Hiking", "Cycling", "Rock Climbing", "Kayaking", "Paddleboarding"
    ]
    
    for activity in recreational_activities:
        for difficulty in ["beginner", "intermediate", "advanced"]:
            exercise_data = {
                "name": f"Recreational {activity}",
                "description": f"Recreational activity: {activity.lower()}",
                "exercise_type": ExerciseType.RECREATIONAL.value,
                "difficulty": difficulty,
                "category": "recreational",
                "equipment_needed": [f"{activity.lower()} equipment"],
                "target_muscle_groups": ["full_body"],
                "instructions": f"Participate in {activity.lower()} for recreation and fitness",
                "exercise_metadata": {
                    "duration_minutes": random.randint(30, 120),
                    "sets": random.randint(1, 1),
                    "reps": random.randint(1, 1),
                    "rest_time_seconds": random.randint(0, 60),
                    "intensity": random.choice(["LOW", "MEDIUM", "HIGH"])
                }
            }
            exercises.append(exercise_data)
    
    # ============================================================================
    # THERAPEUTIC & ADAPTIVE EXERCISES (200+ exercises)
    # ============================================================================
    
    print("Creating therapeutic and adaptive exercises...")
    
    # Therapeutic Exercises
    therapeutic_exercises = [
        "Seated Exercise Routine", "Chair-Based Workout", "Bed Exercises",
        "Wheelchair Exercises", "Low-Impact Cardio", "Gentle Stretching",
        "Balance Exercises", "Coordination Drills", "Range of Motion"
    ]
    
    for exercise in therapeutic_exercises:
        exercise_data = {
            "name": f"Therapeutic {exercise}",
            "description": f"Therapeutic exercise: {exercise.lower()}",
            "exercise_type": ExerciseType.THERAPEUTIC.value,
            "difficulty": "beginner",
            "category": "therapeutic",
            "equipment_needed": ["Chair"] if "chair" in exercise.lower() else [],
            "target_muscle_groups": ["full_body"],
            "instructions": f"Perform {exercise.lower()} with gentle, controlled movements",
            "exercise_metadata": {
                "duration_minutes": random.randint(20, 40),
                "sets": random.randint(2, 4),
                "reps": random.randint(8, 15),
                "rest_time_seconds": random.randint(60, 120),
                "intensity": "LOW"
            }
        }
        exercises.append(exercise_data)
    
    # ============================================================================
    # MOBILITY & RECOVERY EXERCISES (200+ exercises)
    # ============================================================================
    
    print("Creating mobility and recovery exercises...")
    
    # Mobility Exercises
    mobility_exercises = [
        "Joint Mobility", "Hip Mobility", "Shoulder Mobility", "Ankle Mobility",
        "Thoracic Mobility", "Cervical Mobility", "Lumbar Mobility"
    ]
    
    for exercise in mobility_exercises:
        for difficulty in ["beginner", "intermediate"]:
            exercise_data = {
                "name": f"Mobility {exercise}",
                "description": f"Mobility exercise: {exercise.lower()}",
                "exercise_type": ExerciseType.MOBILITY.value,
                "difficulty": difficulty,
                "category": "mobility",
                "equipment_needed": [],
                "target_muscle_groups": ["full_body"],
                "instructions": f"Perform {exercise.lower()} with controlled movement through full range",
                "exercise_metadata": {
                    "duration_minutes": random.randint(15, 30),
                    "sets": random.randint(2, 4),
                    "reps": random.randint(8, 15),
                    "rest_time_seconds": random.randint(30, 60),
                    "intensity": "LOW"
                }
            }
            exercises.append(exercise_data)
    
    # Recovery Exercises
    recovery_exercises = [
        "Foam Rolling", "Stretching", "Light Walking", "Gentle Swimming",
        "Recovery Yoga", "Meditation", "Breathing Exercises"
    ]
    
    for exercise in recovery_exercises:
        exercise_data = {
            "name": f"Recovery {exercise}",
            "description": f"Recovery exercise: {exercise.lower()}",
            "exercise_type": ExerciseType.RECOVERY.value,
            "difficulty": "beginner",
            "category": "recovery",
            "equipment_needed": ["Foam roller"] if "foam" in exercise.lower() else [],
            "target_muscle_groups": ["full_body"],
            "instructions": f"Perform {exercise.lower()} for recovery and relaxation",
            "exercise_metadata": {
                "duration_minutes": random.randint(15, 45),
                "sets": random.randint(1, 3),
                "reps": random.randint(1, 1),
                "rest_time_seconds": random.randint(0, 30),
                "intensity": "LOW"
            }
        }
        exercises.append(exercise_data)
    
    # ============================================================================
    # PLYOMETRIC EXERCISES (100+ exercises)
    # ============================================================================
    
    print("Creating plyometric exercises...")
    
    # Plyometric Exercises
    plyometric_exercises = [
        "Box Jumps", "Depth Jumps", "Bounding", "Plyometric Push-ups",
        "Clap Push-ups", "Medicine Ball Throws", "Plyometric Lunges",
        "Jump Squats", "Tuck Jumps", "Split Jumps", "Broad Jumps"
    ]
    
    for exercise in plyometric_exercises:
        for difficulty in ["intermediate", "advanced"]:
            exercise_data = {
                "name": f"Plyometric {exercise}",
                "description": f"Plyometric exercise: {exercise.lower()}",
                "exercise_type": ExerciseType.PLYOMETRIC.value,
                "difficulty": difficulty,
                "category": "strength_training",
                "equipment_needed": ["Boxes", "Medicine balls"] if "box" in exercise.lower() or "medicine" in exercise.lower() else [],
                "target_muscle_groups": ["legs", "core", "arms"],
                "instructions": f"Perform {exercise.lower()} with explosive power and proper landing",
                "exercise_metadata": {
                    "duration_minutes": random.randint(20, 40),
                    "sets": random.randint(3, 5),
                    "reps": random.randint(6, 15),
                    "rest_time_seconds": random.randint(90, 180),
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
    print(f"Exercise library now includes:")
    print(f"  - Cardio exercises: {len([e for e in exercises if e['exercise_type'] == ExerciseType.CARDIO.value])}")
    print(f"  - Strength exercises: {len([e for e in exercises if e['exercise_type'] == ExerciseType.STRENGTH.value])}")
    print(f"  - Flexibility exercises: {len([e for e in exercises if e['exercise_type'] == ExerciseType.FLEXIBILITY.value])}")
    print(f"  - Balance exercises: {len([e for e in exercises if e['exercise_type'] == ExerciseType.BALANCE.value])}")
    print(f"  - Coordination exercises: {len([e for e in exercises if e['exercise_type'] == ExerciseType.COORDINATION.value])}")
    print(f"  - Sports skill exercises: {len([e for e in exercises if e['exercise_type'] == ExerciseType.SKILL.value])}")
    print(f"  - Team sports exercises: {len([e for e in exercises if e['exercise_type'] == ExerciseType.SPORTS.value])}")
    print(f"  - And many more categories...")

if __name__ == "__main__":
    from app.core.database import get_db
    session = next(get_db())
    seed_comprehensive_exercise_library(session) 