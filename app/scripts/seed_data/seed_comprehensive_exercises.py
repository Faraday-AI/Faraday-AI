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

def seed_comprehensive_exercises(session):
    """Seed the exercises table with comprehensive exercise data."""
    # Get all activities
    activities = session.execute(text("SELECT id, name FROM activities"))
    activity_map = {row.name: row.id for row in activities}
    
    exercises = [
        # CARDIO EXERCISES
        {
            "name": "Basic Jump Rope",
            "description": "Basic jump rope technique with two feet",
            "exercise_type": ExerciseType.CARDIO.value,
            "difficulty": ExerciseDifficulty.BEGINNER.value,
            "category": "cardio",
            "equipment_needed": ["Jump rope"],
            "target_muscle_groups": ["legs", "core"],
            "instructions": "Keep knees slightly bent, land softly on balls of feet. Focus on maintaining a steady rhythm.",
            "exercise_metadata": {
                "duration_minutes": 10,
                "sets": 4,
                "reps": 20,
                "rest_time_seconds": 60,
                "intensity": "MEDIUM"
            }
        },
        {
            "name": "Advanced Jump Rope Techniques",
            "description": "Advanced jump rope combinations and footwork",
            "exercise_type": ExerciseType.CARDIO.value,
            "difficulty": ExerciseDifficulty.ADVANCED.value,
            "category": "cardio",
            "equipment_needed": ["Jump rope"],
            "target_muscle_groups": ["legs", "core", "arms"],
            "instructions": "Master basic jumps before attempting advanced moves. Progress gradually to more complex moves.",
            "exercise_metadata": {
                "duration_minutes": 20,
                "sets": 5,
                "reps": 30,
                "rest_time_seconds": 60,
                "intensity": "HIGH"
            }
        },
        {
            "name": "High-Intensity Interval Training (HIIT)",
            "description": "Alternating high and low intensity cardio intervals",
            "exercise_type": ExerciseType.HIIT.value,
            "difficulty": ExerciseDifficulty.INTERMEDIATE.value,
            "category": "cardio",
            "equipment_needed": ["Stopwatch", "Cones"],
            "target_muscle_groups": ["full_body"],
            "instructions": "30 seconds high intensity, 30 seconds rest. Repeat for 10-15 rounds.",
            "exercise_metadata": {
                "duration_minutes": 25,
                "sets": 10,
                "reps": 1,
                "rest_time_seconds": 30,
                "intensity": "HIGH"
            }
        },
        {
            "name": "Mountain Climbers",
            "description": "Dynamic cardio exercise targeting core and legs",
            "exercise_type": ExerciseType.CARDIO.value,
            "difficulty": ExerciseDifficulty.INTERMEDIATE.value,
            "category": "cardio",
            "equipment_needed": [],
            "target_muscle_groups": ["core", "legs", "shoulders"],
            "instructions": "Start in plank position, alternate bringing knees to chest rapidly.",
            "exercise_metadata": {
                "duration_minutes": 15,
                "sets": 4,
                "reps": 30,
                "rest_time_seconds": 45,
                "intensity": "HIGH"
            }
        },
        {
            "name": "Burpees",
            "description": "Full-body cardio exercise combining multiple movements",
            "exercise_type": ExerciseType.CARDIO.value,
            "difficulty": ExerciseDifficulty.INTERMEDIATE.value,
            "category": "cardio",
            "equipment_needed": [],
            "target_muscle_groups": ["full_body"],
            "instructions": "Squat, jump back to plank, do push-up, jump forward, jump up.",
            "exercise_metadata": {
                "duration_minutes": 20,
                "sets": 5,
                "reps": 15,
                "rest_time_seconds": 60,
                "intensity": "HIGH"
            }
        },
        
        # STRENGTH EXERCISES
        {
            "name": "Push-ups",
            "description": "Classic upper body strength exercise",
            "exercise_type": ExerciseType.STRENGTH.value,
            "difficulty": ExerciseDifficulty.BEGINNER.value,
            "category": "strength_training",
            "equipment_needed": [],
            "target_muscle_groups": ["chest", "shoulders", "triceps"],
            "instructions": "Maintain straight body line, lower chest to ground, push back up.",
            "exercise_metadata": {
                "duration_minutes": 15,
                "sets": 3,
                "reps": 10,
                "rest_time_seconds": 60,
                "intensity": "MEDIUM"
            }
        },
        {
            "name": "Modified Push-ups",
            "description": "Easier version of push-ups for beginners",
            "exercise_type": ExerciseType.STRENGTH.value,
            "difficulty": ExerciseDifficulty.BEGINNER.value,
            "category": "strength_training",
            "equipment_needed": [],
            "target_muscle_groups": ["chest", "shoulders", "triceps"],
            "instructions": "Knees on ground, maintain straight upper body, perform push-up motion.",
            "exercise_metadata": {
                "duration_minutes": 15,
                "sets": 3,
                "reps": 12,
                "rest_time_seconds": 60,
                "intensity": "LOW"
            }
        },
        {
            "name": "Squats",
            "description": "Fundamental lower body strength exercise",
            "exercise_type": ExerciseType.STRENGTH.value,
            "difficulty": ExerciseDifficulty.BEGINNER.value,
            "category": "strength_training",
            "equipment_needed": [],
            "target_muscle_groups": ["legs", "glutes", "core"],
            "instructions": "Feet shoulder-width apart, lower hips back and down, keep chest up.",
            "exercise_metadata": {
                "duration_minutes": 15,
                "sets": 3,
                "reps": 15,
                "rest_time_seconds": 60,
                "intensity": "MEDIUM"
            }
        },
        {
            "name": "Lunges",
            "description": "Dynamic lower body exercise for balance and strength",
            "exercise_type": ExerciseType.STRENGTH.value,
            "difficulty": ExerciseDifficulty.INTERMEDIATE.value,
            "category": "strength_training",
            "equipment_needed": [],
            "target_muscle_groups": ["legs", "glutes", "core"],
            "instructions": "Step forward, lower back knee toward ground, push back to start.",
            "exercise_metadata": {
                "duration_minutes": 20,
                "sets": 3,
                "reps": 20,
                "rest_time_seconds": 60,
                "intensity": "MEDIUM"
            }
        },
        {
            "name": "Plank",
            "description": "Core stability and endurance exercise",
            "exercise_type": ExerciseType.STRENGTH.value,
            "difficulty": ExerciseDifficulty.BEGINNER.value,
            "category": "strength_training",
            "equipment_needed": [],
            "target_muscle_groups": ["core", "shoulders"],
            "instructions": "Hold body in straight line from head to heels, engage core muscles.",
            "exercise_metadata": {
                "duration_minutes": 10,
                "sets": 3,
                "reps": 1,
                "rest_time_seconds": 60,
                "intensity": "MEDIUM"
            }
        },
        
        # FLEXIBILITY EXERCISES
        {
            "name": "Static Stretching Routine",
            "description": "Post-activity static stretching for all major muscle groups",
            "exercise_type": ExerciseType.FLEXIBILITY.value,
            "difficulty": ExerciseDifficulty.BEGINNER.value,
            "category": "cool_down",
            "equipment_needed": ["Yoga mat"],
            "target_muscle_groups": ["full_body"],
            "instructions": "Hold each stretch for 20-30 seconds, breathe deeply. Don't bounce.",
            "exercise_metadata": {
                "duration_minutes": 15,
                "sets": 1,
                "reps": 1,
                "rest_time_seconds": 0,
                "intensity": "LOW"
            }
        },
        {
            "name": "Dynamic Warm-up Circuit",
            "description": "Full-body dynamic warm-up exercises",
            "exercise_type": ExerciseType.WARM_UP.value,
            "difficulty": ExerciseDifficulty.BEGINNER.value,
            "category": "warm_up",
            "equipment_needed": [],
            "target_muscle_groups": ["full_body"],
            "instructions": "Move through full range of motion, maintain control. Focus on proper form.",
            "exercise_metadata": {
                "duration_minutes": 10,
                "sets": 3,
                "reps": 15,
                "rest_time_seconds": 30,
                "intensity": "LOW"
            }
        },
        {
            "name": "Yoga Flow Sequence",
            "description": "Flowing yoga poses for flexibility and mindfulness",
            "exercise_type": ExerciseType.YOGA.value,
            "difficulty": ExerciseDifficulty.INTERMEDIATE.value,
            "category": "flexibility",
            "equipment_needed": ["Yoga mat"],
            "target_muscle_groups": ["full_body"],
            "instructions": "Flow smoothly between poses, focus on breath and alignment.",
            "exercise_metadata": {
                "duration_minutes": 30,
                "sets": 1,
                "reps": 1,
                "rest_time_seconds": 0,
                "intensity": "LOW"
            }
        },
        
        # BALANCE EXERCISES
        {
            "name": "Single Leg Balance",
            "description": "Basic balance exercise on one leg",
            "exercise_type": ExerciseType.BALANCE.value,
            "difficulty": ExerciseDifficulty.BEGINNER.value,
            "category": "balance",
            "equipment_needed": [],
            "target_muscle_groups": ["legs", "core"],
            "instructions": "Stand on one leg, maintain balance for 30 seconds, switch legs.",
            "exercise_metadata": {
                "duration_minutes": 10,
                "sets": 3,
                "reps": 1,
                "rest_time_seconds": 30,
                "intensity": "LOW"
            }
        },
        {
            "name": "Balance Beam Walking",
            "description": "Walking on narrow surface to improve balance",
            "exercise_type": ExerciseType.BALANCE.value,
            "difficulty": ExerciseDifficulty.INTERMEDIATE.value,
            "category": "balance",
            "equipment_needed": ["Balance beam", "Cones"],
            "target_muscle_groups": ["legs", "core"],
            "instructions": "Walk forward and backward on beam, maintain steady pace.",
            "exercise_metadata": {
                "duration_minutes": 15,
                "sets": 4,
                "reps": 1,
                "rest_time_seconds": 45,
                "intensity": "MEDIUM"
            }
        },
        
        # COORDINATION EXERCISES
        {
            "name": "Agility Ladder Drills",
            "description": "Footwork patterns through agility ladder",
            "exercise_type": ExerciseType.COORDINATION.value,
            "difficulty": ExerciseDifficulty.INTERMEDIATE.value,
            "category": "coordination",
            "equipment_needed": ["Agility ladder"],
            "target_muscle_groups": ["legs", "core"],
            "instructions": "Practice various footwork patterns through ladder rungs.",
            "exercise_metadata": {
                "duration_minutes": 20,
                "sets": 5,
                "reps": 1,
                "rest_time_seconds": 60,
                "intensity": "MEDIUM"
            }
        },
        {
            "name": "Ball Tossing Drills",
            "description": "Coordination exercises with ball tossing",
            "exercise_type": ExerciseType.COORDINATION.value,
            "difficulty": ExerciseDifficulty.BEGINNER.value,
            "category": "coordination",
            "equipment_needed": ["Tennis balls", "Bean bags"],
            "target_muscle_groups": ["arms", "core"],
            "instructions": "Toss ball in air, catch with opposite hand, progress to juggling.",
            "exercise_metadata": {
                "duration_minutes": 15,
                "sets": 4,
                "reps": 20,
                "rest_time_seconds": 45,
                "intensity": "LOW"
            }
        },
        
        # SPORTS SKILLS
        {
            "name": "Basketball Dribble Drills",
            "description": "Basic basketball dribbling techniques",
            "exercise_type": ExerciseType.SKILL.value,
            "difficulty": ExerciseDifficulty.BEGINNER.value,
            "category": "skill_development",
            "equipment_needed": ["Basketball"],
            "target_muscle_groups": ["arms", "shoulders", "core"],
            "instructions": "Keep eyes up, use fingertips, maintain low stance. Practice with both hands.",
            "exercise_metadata": {
                "duration_minutes": 20,
                "sets": 4,
                "reps": 30,
                "rest_time_seconds": 45,
                "intensity": "MEDIUM"
            }
        },
        {
            "name": "Basketball Shooting Practice",
            "description": "Basketball shooting technique and accuracy",
            "exercise_type": ExerciseType.SKILL.value,
            "difficulty": ExerciseDifficulty.INTERMEDIATE.value,
            "category": "skill_development",
            "equipment_needed": ["Basketball", "Basketball hoop"],
            "target_muscle_groups": ["arms", "shoulders", "core", "legs"],
            "instructions": "Focus on proper form: BEEF (Balance, Eyes, Elbow, Follow-through).",
            "exercise_metadata": {
                "duration_minutes": 25,
                "sets": 5,
                "reps": 20,
                "rest_time_seconds": 60,
                "intensity": "MEDIUM"
            }
        },
        {
            "name": "Soccer Passing Drills",
            "description": "Basic soccer passing techniques",
            "exercise_type": ExerciseType.SKILL.value,
            "difficulty": ExerciseDifficulty.BEGINNER.value,
            "category": "skill_development",
            "equipment_needed": ["Soccer ball", "Cones"],
            "target_muscle_groups": ["legs", "core"],
            "instructions": "Plant foot next to ball, strike with inside of foot. Practice with both feet.",
            "exercise_metadata": {
                "duration_minutes": 20,
                "sets": 4,
                "reps": 25,
                "rest_time_seconds": 45,
                "intensity": "MEDIUM"
            }
        },
        {
            "name": "Soccer Dribbling Skills",
            "description": "Soccer ball control and dribbling techniques",
            "exercise_type": ExerciseType.SKILL.value,
            "difficulty": ExerciseDifficulty.INTERMEDIATE.value,
            "category": "skill_development",
            "equipment_needed": ["Soccer ball", "Cones"],
            "target_muscle_groups": ["legs", "core"],
            "instructions": "Keep ball close, use both feet, practice various moves and turns.",
            "exercise_metadata": {
                "duration_minutes": 25,
                "sets": 5,
                "reps": 30,
                "rest_time_seconds": 60,
                "intensity": "MEDIUM"
            }
        },
        {
            "name": "Tennis Forehand Practice",
            "description": "Basic tennis forehand stroke technique",
            "exercise_type": ExerciseType.SKILL.value,
            "difficulty": ExerciseDifficulty.BEGINNER.value,
            "category": "skill_development",
            "equipment_needed": ["Tennis racket", "Tennis balls"],
            "target_muscle_groups": ["arms", "shoulders", "core"],
            "instructions": "Proper grip, step into shot, follow through across body.",
            "exercise_metadata": {
                "duration_minutes": 20,
                "sets": 4,
                "reps": 25,
                "rest_time_seconds": 60,
                "intensity": "MEDIUM"
            }
        },
        
        # TEAM SPORTS
        {
            "name": "Basketball Game Drills",
            "description": "5v5 basketball game preparation",
            "exercise_type": ExerciseType.SPORTS.value,
            "difficulty": ExerciseDifficulty.INTERMEDIATE.value,
            "category": "team_sports",
            "equipment_needed": ["Basketball", "Court"],
            "target_muscle_groups": ["full_body"],
            "instructions": "Focus on team play, communication, and strategy. Rotate positions regularly.",
            "exercise_metadata": {
                "duration_minutes": 40,
                "sets": 5,
                "reps": 1,
                "rest_time_seconds": 120,
                "intensity": "HIGH"
            }
        },
        {
            "name": "Soccer Small-Sided Games",
            "description": "3v3 or 4v4 soccer games for skill development",
            "exercise_type": ExerciseType.SPORTS.value,
            "difficulty": ExerciseDifficulty.INTERMEDIATE.value,
            "category": "team_sports",
            "equipment_needed": ["Soccer ball", "Cones", "Goals"],
            "target_muscle_groups": ["full_body"],
            "instructions": "Focus on ball control, passing, and team coordination in small groups.",
            "exercise_metadata": {
                "duration_minutes": 30,
                "sets": 4,
                "reps": 1,
                "rest_time_seconds": 90,
                "intensity": "HIGH"
            }
        },
        
        # FITNESS TRAINING
        {
            "name": "Circuit Training Workout",
            "description": "Full-body circuit training exercises",
            "exercise_type": ExerciseType.STRENGTH.value,
            "difficulty": ExerciseDifficulty.INTERMEDIATE.value,
            "category": "strength_training",
            "equipment_needed": ["Various fitness equipment"],
            "target_muscle_groups": ["full_body"],
            "instructions": "Maintain proper form, control movement speed. Adjust weights as needed.",
            "exercise_metadata": {
                "duration_minutes": 30,
                "sets": 5,
                "reps": 15,
                "rest_time_seconds": 60,
                "intensity": "HIGH"
            }
        },
        {
            "name": "Tabata Training",
            "description": "High-intensity interval training with 20/10 work/rest ratio",
            "exercise_type": ExerciseType.HIIT.value,
            "difficulty": ExerciseDifficulty.ADVANCED.value,
            "category": "cardio",
            "equipment_needed": ["Stopwatch"],
            "target_muscle_groups": ["full_body"],
            "instructions": "20 seconds work, 10 seconds rest, repeat 8 times for one round.",
            "exercise_metadata": {
                "duration_minutes": 20,
                "sets": 4,
                "reps": 1,
                "rest_time_seconds": 60,
                "intensity": "HIGH"
            }
        },
        
        # RECREATIONAL ACTIVITIES
        {
            "name": "Dance Fitness",
            "description": "Cardio dance workout combining fitness and fun",
            "exercise_type": ExerciseType.DANCE.value,
            "difficulty": ExerciseDifficulty.BEGINNER.value,
            "category": "recreational",
            "equipment_needed": ["Music player", "Dance space"],
            "target_muscle_groups": ["full_body"],
            "instructions": "Follow dance moves, keep moving, have fun while getting fit.",
            "exercise_metadata": {
                "duration_minutes": 30,
                "sets": 1,
                "reps": 1,
                "rest_time_seconds": 0,
                "intensity": "MEDIUM"
            }
        },
        {
            "name": "Hula Hoop Workout",
            "description": "Full-body workout using hula hoops",
            "exercise_type": ExerciseType.RECREATIONAL.value,
            "difficulty": ExerciseDifficulty.BEGINNER.value,
            "category": "recreational",
            "equipment_needed": ["Hula hoops"],
            "target_muscle_groups": ["core", "legs"],
            "instructions": "Keep hoop moving around waist, add arm movements for variety.",
            "exercise_metadata": {
                "duration_minutes": 20,
                "sets": 3,
                "reps": 1,
                "rest_time_seconds": 60,
                "intensity": "MEDIUM"
            }
        },
        
        # MOBILITY AND RECOVERY
        {
            "name": "Foam Rolling Routine",
            "description": "Self-myofascial release using foam roller",
            "exercise_type": ExerciseType.RECOVERY.value,
            "difficulty": ExerciseDifficulty.BEGINNER.value,
            "category": "recovery",
            "equipment_needed": ["Foam roller"],
            "target_muscle_groups": ["full_body"],
            "instructions": "Roll slowly over tight areas, pause on tender spots, breathe deeply.",
            "exercise_metadata": {
                "duration_minutes": 15,
                "sets": 1,
                "reps": 1,
                "rest_time_seconds": 0,
                "intensity": "LOW"
            }
        },
        {
            "name": "Mobility Flow",
            "description": "Dynamic mobility exercises for joint health",
            "exercise_type": ExerciseType.MOBILITY.value,
            "difficulty": ExerciseDifficulty.INTERMEDIATE.value,
            "category": "mobility",
            "equipment_needed": [],
            "target_muscle_groups": ["full_body"],
            "instructions": "Move joints through full range of motion, maintain control and breathing.",
            "exercise_metadata": {
                "duration_minutes": 20,
                "sets": 1,
                "reps": 1,
                "rest_time_seconds": 0,
                "intensity": "LOW"
            }
        },
        
        # SPECIALIZED TRAINING
        {
            "name": "Plyometric Training",
            "description": "Explosive jumping and bounding exercises",
            "exercise_type": ExerciseType.PLYOMETRIC.value,
            "difficulty": ExerciseDifficulty.ADVANCED.value,
            "category": "strength_training",
            "equipment_needed": ["Boxes", "Cones"],
            "target_muscle_groups": ["legs", "core"],
            "instructions": "Land softly, absorb impact, explode upward. Focus on quality over quantity.",
            "exercise_metadata": {
                "duration_minutes": 25,
                "sets": 4,
                "reps": 8,
                "rest_time_seconds": 90,
                "intensity": "HIGH"
            }
        },
        {
            "name": "Resistance Band Workout",
            "description": "Strength training using resistance bands",
            "exercise_type": ExerciseType.RESISTANCE.value,
            "difficulty": ExerciseDifficulty.INTERMEDIATE.value,
            "category": "strength_training",
            "equipment_needed": ["Resistance bands"],
            "target_muscle_groups": ["full_body"],
            "instructions": "Maintain tension on bands, control movement speed, focus on form.",
            "exercise_metadata": {
                "duration_minutes": 30,
                "sets": 4,
                "reps": 15,
                "rest_time_seconds": 60,
                "intensity": "MEDIUM"
            }
        },
        
        # ADAPTIVE EXERCISES
        {
            "name": "Seated Exercise Routine",
            "description": "Chair-based exercises for limited mobility",
            "exercise_type": ExerciseType.THERAPEUTIC.value,
            "difficulty": ExerciseDifficulty.BEGINNER.value,
            "category": "therapeutic",
            "equipment_needed": ["Chair", "Light weights"],
            "target_muscle_groups": ["arms", "core", "legs"],
            "instructions": "Perform exercises while seated, maintain good posture, breathe normally.",
            "exercise_metadata": {
                "duration_minutes": 20,
                "sets": 3,
                "reps": 12,
                "rest_time_seconds": 60,
                "intensity": "LOW"
            }
        },
        {
            "name": "Low-Impact Cardio",
            "description": "Gentle cardio exercises for joint health",
            "exercise_type": ExerciseType.CARDIO.value,
            "difficulty": ExerciseDifficulty.BEGINNER.value,
            "category": "therapeutic",
            "equipment_needed": [],
            "target_muscle_groups": ["full_body"],
            "instructions": "Keep movements low-impact, maintain steady pace, listen to your body.",
            "exercise_metadata": {
                "duration_minutes": 25,
                "sets": 1,
                "reps": 1,
                "rest_time_seconds": 0,
                "intensity": "LOW"
            }
        }
    ]

    for exercise_data in exercises:
        exercise = Exercise(**exercise_data)
        session.add(exercise)

    session.commit()
    print(f"Successfully seeded {len(exercises)} comprehensive exercises!")

if __name__ == "__main__":
    from app.core.database import get_db
    session = next(get_db())
    seed_comprehensive_exercises(session) 