from datetime import datetime, timedelta
from app.services.physical_education.models.movement import MovementProgress

async def seed_movement_progress(session):
    """Seed the movement_progress table with initial data."""
    movement_progress = [
        {
            "student_id": 1,
            "movement_type": "jump_rope",
            "progress_data": {
                "baseline": {
                    "date": datetime.now() - timedelta(days=30),
                    "metrics": {
                        "total_jumps": 300,
                        "consistency_score": 0.70,
                        "endurance_level": "fair"
                    }
                },
                "current": {
                    "date": datetime.now(),
                    "metrics": {
                        "total_jumps": 500,
                        "consistency_score": 0.85,
                        "endurance_level": "good"
                    }
                },
                "improvement": {
                    "jump_count": "+200 jumps",
                    "consistency": "+15%",
                    "endurance": "fair → good"
                }
            },
            "confidence_score": 0.92
        },
        {
            "student_id": 1,
            "movement_type": "basketball_dribbling",
            "progress_data": {
                "baseline": {
                    "date": datetime.now() - timedelta(days=30),
                    "metrics": {
                        "ball_control_score": 0.75,
                        "weak_hand_proficiency": 0.60,
                        "speed_rating": "low"
                    }
                },
                "current": {
                    "date": datetime.now(),
                    "metrics": {
                        "ball_control_score": 0.88,
                        "weak_hand_proficiency": 0.75,
                        "speed_rating": "medium"
                    }
                },
                "improvement": {
                    "control": "+13%",
                    "weak_hand": "+15%",
                    "speed": "low → medium"
                }
            },
            "confidence_score": 0.88
        },
        {
            "student_id": 2,
            "movement_type": "soccer_passing",
            "progress_data": {
                "baseline": {
                    "date": datetime.now() - timedelta(days=30),
                    "metrics": {
                        "pass_accuracy": 0.65,
                        "power_rating": "low",
                        "technique_score": 0.70
                    }
                },
                "current": {
                    "date": datetime.now(),
                    "metrics": {
                        "pass_accuracy": 0.78,
                        "power_rating": "medium",
                        "technique_score": 0.85
                    }
                },
                "improvement": {
                    "accuracy": "+13%",
                    "power": "low → medium",
                    "technique": "+15%"
                }
            },
            "confidence_score": 0.90
        },
        {
            "student_id": 2,
            "movement_type": "dynamic_warmup",
            "progress_data": {
                "baseline": {
                    "date": datetime.now() - timedelta(days=30),
                    "metrics": {
                        "range_of_motion": 0.80,
                        "form_score": 0.75,
                        "endurance_level": "fair"
                    }
                },
                "current": {
                    "date": datetime.now(),
                    "metrics": {
                        "range_of_motion": 0.90,
                        "form_score": 0.88,
                        "endurance_level": "good"
                    }
                },
                "improvement": {
                    "mobility": "+10%",
                    "form": "+13%",
                    "endurance": "fair → good"
                }
            },
            "confidence_score": 0.85
        }
    ]

    for progress_data in movement_progress:
        progress = MovementProgress(**progress_data)
        session.add(progress)

    await session.flush()
    print("Movement progress seeded successfully!") 