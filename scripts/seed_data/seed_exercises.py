from datetime import datetime
from app.services.physical_education.models.activity import Exercise

async def seed_exercises(session):
    """Seed the exercises table with initial data."""
    exercises = [
        {
            "name": "Basic Jump Rope",
            "description": "Basic jump rope technique with two feet",
            "activity_id": 1,  # Jump Rope Basics
            "sets": 3,
            "reps": 30,
            "rest_time_seconds": 60,
            "technique_notes": "Keep elbows close to body, jump on balls of feet",
            "progression_steps": [
                "Start with single jumps",
                "Progress to double jumps",
                "Add cross-overs"
            ],
            "regression_steps": [
                "Use a longer rope",
                "Practice without rope",
                "Use a hula hoop instead"
            ]
        },
        {
            "name": "Basketball Dribble Drills",
            "description": "Basic basketball dribbling techniques",
            "activity_id": 2,  # Basketball Dribbling
            "sets": 4,
            "reps": 20,
            "rest_time_seconds": 45,
            "technique_notes": "Keep head up, use fingertips, control the ball",
            "progression_steps": [
                "Stationary dribbling",
                "Walking dribble",
                "Running dribble",
                "Crossover dribble"
            ],
            "regression_steps": [
                "Use a larger ball",
                "Practice without movement",
                "Use two hands"
            ]
        },
        {
            "name": "Soccer Passing Drills",
            "description": "Basic soccer passing techniques",
            "activity_id": 3,  # Soccer Passing
            "sets": 3,
            "reps": 15,
            "rest_time_seconds": 60,
            "technique_notes": "Use inside of foot, follow through, maintain balance",
            "progression_steps": [
                "Stationary passing",
                "Moving passing",
                "One-touch passing",
                "Long passing"
            ],
            "regression_steps": [
                "Use a larger ball",
                "Reduce distance",
                "Allow multiple touches"
            ]
        },
        {
            "name": "Dynamic Warm-up Circuit",
            "description": "Full-body dynamic warm-up exercises",
            "activity_id": 4,  # Dynamic Warm-up
            "sets": 1,
            "reps": 10,
            "rest_time_seconds": 30,
            "technique_notes": "Move through full range of motion, maintain control",
            "progression_steps": [
                "Increase range of motion",
                "Add resistance",
                "Increase speed"
            ],
            "regression_steps": [
                "Reduce range of motion",
                "Decrease speed",
                "Use support if needed"
            ]
        },
        {
            "name": "Static Stretching Routine",
            "description": "Post-activity static stretching",
            "activity_id": 5,  # Cool Down Stretches
            "sets": 1,
            "reps": 3,
            "rest_time_seconds": 0,
            "technique_notes": "Hold each stretch for 20-30 seconds, breathe deeply",
            "progression_steps": [
                "Increase hold time",
                "Add more stretches",
                "Increase intensity"
            ],
            "regression_steps": [
                "Reduce hold time",
                "Use support",
                "Focus on major muscle groups only"
            ]
        }
    ]

    for exercise_data in exercises:
        exercise = Exercise(**exercise_data)
        session.add(exercise)

    await session.flush()
    print("Exercises seeded successfully!") 