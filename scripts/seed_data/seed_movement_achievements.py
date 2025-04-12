from datetime import datetime, timedelta
from app.services.physical_education.models.movement import MovementAchievement

async def seed_movement_achievements(session):
    """Seed the movement_achievements table with initial data."""
    movement_achievements = [
        {
            "student_id": 1,
            "movement_type": "jump_rope",
            "achievement_data": {
                "achievement_type": "endurance_mastery",
                "metrics": {
                    "duration": "5 minutes",
                    "total_jumps": 1000,
                    "consistency_score": 0.90
                },
                "milestones": [
                    {
                        "date": datetime.now() - timedelta(days=30),
                        "achievement": "First 100 consecutive jumps"
                    },
                    {
                        "date": datetime.now() - timedelta(days=15),
                        "achievement": "3 minutes continuous jumping"
                    },
                    {
                        "date": datetime.now(),
                        "achievement": "5 minutes with 90% consistency"
                    }
                ],
                "badges": [
                    "Endurance Master",
                    "Consistency Expert",
                    "Jump Rope Pro"
                ]
            },
            "confidence_score": 0.92
        },
        {
            "student_id": 1,
            "movement_type": "basketball_dribbling",
            "achievement_data": {
                "achievement_type": "skill_mastery",
                "metrics": {
                    "weak_hand_score": 0.85,
                    "speed_rating": "high",
                    "control_score": 0.90
                },
                "milestones": [
                    {
                        "date": datetime.now() - timedelta(days=45),
                        "achievement": "Basic dribble control"
                    },
                    {
                        "date": datetime.now() - timedelta(days=30),
                        "achievement": "Crossover mastered"
                    },
                    {
                        "date": datetime.now(),
                        "achievement": "Advanced dribble combinations"
                    }
                ],
                "badges": [
                    "Dribble Master",
                    "Weak Hand Expert",
                    "Ball Control Pro"
                ]
            },
            "confidence_score": 0.88
        },
        {
            "student_id": 2,
            "movement_type": "soccer_passing",
            "achievement_data": {
                "achievement_type": "accuracy_mastery",
                "metrics": {
                    "pass_accuracy": 0.90,
                    "power_rating": "high",
                    "technique_score": 0.95
                },
                "milestones": [
                    {
                        "date": datetime.now() - timedelta(days=60),
                        "achievement": "Basic passing technique"
                    },
                    {
                        "date": datetime.now() - timedelta(days=30),
                        "achievement": "Accurate short passes"
                    },
                    {
                        "date": datetime.now(),
                        "achievement": "Precision long passes"
                    }
                ],
                "badges": [
                    "Passing Master",
                    "Accuracy Expert",
                    "Technique Pro"
                ]
            },
            "confidence_score": 0.90
        },
        {
            "student_id": 2,
            "movement_type": "dynamic_warmup",
            "achievement_data": {
                "achievement_type": "form_mastery",
                "metrics": {
                    "range_of_motion": 0.95,
                    "form_score": 0.95,
                    "consistency_score": 0.90
                },
                "milestones": [
                    {
                        "date": datetime.now() - timedelta(days=30),
                        "achievement": "Basic form established"
                    },
                    {
                        "date": datetime.now() - timedelta(days=15),
                        "achievement": "Improved flexibility"
                    },
                    {
                        "date": datetime.now(),
                        "achievement": "Perfect form execution"
                    }
                ],
                "badges": [
                    "Form Master",
                    "Flexibility Expert",
                    "Movement Pro"
                ]
            },
            "confidence_score": 0.85
        }
    ]

    for achievement_data in movement_achievements:
        achievement = MovementAchievement(**achievement_data)
        session.add(achievement)

    await session.flush()
    print("Movement achievements seeded successfully!") 