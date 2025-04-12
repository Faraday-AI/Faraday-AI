from datetime import datetime, timedelta
from app.services.physical_education.models.movement import MovementChallenge

async def seed_movement_challenges(session):
    """Seed the movement_challenges table with initial data."""
    movement_challenges = [
        {
            "student_id": 1,
            "movement_type": "jump_rope",
            "challenge_data": {
                "challenge_type": "endurance",
                "target_metrics": {
                    "duration": "5 minutes",
                    "jump_count": 1000,
                    "consistency_score": 0.85
                },
                "timeframe": {
                    "start_date": datetime.now(),
                    "end_date": datetime.now() + timedelta(days=14),
                    "checkpoints": [
                        {
                            "date": datetime.now() + timedelta(days=7),
                            "target": {
                                "duration": "3 minutes",
                                "jump_count": 600,
                                "consistency_score": 0.80
                            }
                        }
                    ]
                },
                "rewards": {
                    "completion": "Advanced jump rope badge",
                    "milestone": "Endurance achievement badge"
                }
            },
            "confidence_score": 0.92
        },
        {
            "student_id": 1,
            "movement_type": "basketball_dribbling",
            "challenge_data": {
                "challenge_type": "skill_mastery",
                "target_metrics": {
                    "weak_hand_score": 0.85,
                    "speed_rating": "high",
                    "control_score": 0.90
                },
                "timeframe": {
                    "start_date": datetime.now(),
                    "end_date": datetime.now() + timedelta(days=21),
                    "checkpoints": [
                        {
                            "date": datetime.now() + timedelta(days=7),
                            "target": {
                                "weak_hand_score": 0.75,
                                "speed_rating": "medium_high",
                                "control_score": 0.85
                            }
                        },
                        {
                            "date": datetime.now() + timedelta(days=14),
                            "target": {
                                "weak_hand_score": 0.80,
                                "speed_rating": "high",
                                "control_score": 0.88
                            }
                        }
                    ]
                },
                "rewards": {
                    "completion": "Dribbling master badge",
                    "milestone": "Weak hand proficiency badge"
                }
            },
            "confidence_score": 0.88
        },
        {
            "student_id": 2,
            "movement_type": "soccer_passing",
            "challenge_data": {
                "challenge_type": "accuracy",
                "target_metrics": {
                    "pass_accuracy": 0.90,
                    "power_rating": "high",
                    "technique_score": 0.95
                },
                "timeframe": {
                    "start_date": datetime.now(),
                    "end_date": datetime.now() + timedelta(days=28),
                    "checkpoints": [
                        {
                            "date": datetime.now() + timedelta(days=14),
                            "target": {
                                "pass_accuracy": 0.85,
                                "power_rating": "medium_high",
                                "technique_score": 0.90
                            }
                        }
                    ]
                },
                "rewards": {
                    "completion": "Passing accuracy badge",
                    "milestone": "Power passing badge"
                }
            },
            "confidence_score": 0.90
        },
        {
            "student_id": 2,
            "movement_type": "dynamic_warmup",
            "challenge_data": {
                "challenge_type": "form_perfection",
                "target_metrics": {
                    "range_of_motion": 0.95,
                    "form_score": 0.95,
                    "consistency_score": 0.90
                },
                "timeframe": {
                    "start_date": datetime.now(),
                    "end_date": datetime.now() + timedelta(days=14),
                    "checkpoints": [
                        {
                            "date": datetime.now() + timedelta(days=7),
                            "target": {
                                "range_of_motion": 0.90,
                                "form_score": 0.90,
                                "consistency_score": 0.85
                            }
                        }
                    ]
                },
                "rewards": {
                    "completion": "Form mastery badge",
                    "milestone": "Flexibility achievement badge"
                }
            },
            "confidence_score": 0.85
        }
    ]

    for challenge_data in movement_challenges:
        challenge = MovementChallenge(**challenge_data)
        session.add(challenge)

    await session.flush()
    print("Movement challenges seeded successfully!") 