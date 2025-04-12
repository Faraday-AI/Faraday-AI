from datetime import datetime, timedelta
from app.services.physical_education.models.movement import MovementGoal

async def seed_movement_goals(session):
    """Seed the movement_goals table with initial data."""
    movement_goals = [
        {
            "student_id": 1,
            "movement_type": "jump_rope",
            "goal_data": {
                "target_metrics": {
                    "total_jumps": 800,
                    "consistency_score": 0.90,
                    "endurance_level": "excellent"
                },
                "timeline": {
                    "start_date": datetime.now(),
                    "target_date": datetime.now() + timedelta(days=30),
                    "milestones": [
                        {
                            "date": datetime.now() + timedelta(days=10),
                            "target": {
                                "total_jumps": 600,
                                "consistency_score": 0.85,
                                "endurance_level": "good"
                            }
                        },
                        {
                            "date": datetime.now() + timedelta(days=20),
                            "target": {
                                "total_jumps": 700,
                                "consistency_score": 0.88,
                                "endurance_level": "very_good"
                            }
                        }
                    ]
                },
                "progress_tracking": {
                    "frequency": "weekly",
                    "metrics_to_track": ["total_jumps", "consistency_score", "endurance_level"]
                }
            },
            "confidence_score": 0.92
        },
        {
            "student_id": 1,
            "movement_type": "basketball_dribbling",
            "goal_data": {
                "target_metrics": {
                    "ball_control_score": 0.95,
                    "weak_hand_proficiency": 0.90,
                    "speed_rating": "high"
                },
                "timeline": {
                    "start_date": datetime.now(),
                    "target_date": datetime.now() + timedelta(days=45),
                    "milestones": [
                        {
                            "date": datetime.now() + timedelta(days=15),
                            "target": {
                                "ball_control_score": 0.90,
                                "weak_hand_proficiency": 0.80,
                                "speed_rating": "medium"
                            }
                        },
                        {
                            "date": datetime.now() + timedelta(days=30),
                            "target": {
                                "ball_control_score": 0.93,
                                "weak_hand_proficiency": 0.85,
                                "speed_rating": "medium_high"
                            }
                        }
                    ]
                },
                "progress_tracking": {
                    "frequency": "bi-weekly",
                    "metrics_to_track": ["ball_control_score", "weak_hand_proficiency", "speed_rating"]
                }
            },
            "confidence_score": 0.88
        },
        {
            "student_id": 2,
            "movement_type": "soccer_passing",
            "goal_data": {
                "target_metrics": {
                    "pass_accuracy": 0.90,
                    "power_rating": "high",
                    "technique_score": 0.95
                },
                "timeline": {
                    "start_date": datetime.now(),
                    "target_date": datetime.now() + timedelta(days=60),
                    "milestones": [
                        {
                            "date": datetime.now() + timedelta(days=20),
                            "target": {
                                "pass_accuracy": 0.85,
                                "power_rating": "medium_high",
                                "technique_score": 0.90
                            }
                        },
                        {
                            "date": datetime.now() + timedelta(days=40),
                            "target": {
                                "pass_accuracy": 0.88,
                                "power_rating": "high",
                                "technique_score": 0.93
                            }
                        }
                    ]
                },
                "progress_tracking": {
                    "frequency": "weekly",
                    "metrics_to_track": ["pass_accuracy", "power_rating", "technique_score"]
                }
            },
            "confidence_score": 0.90
        },
        {
            "student_id": 2,
            "movement_type": "dynamic_warmup",
            "goal_data": {
                "target_metrics": {
                    "range_of_motion": 0.95,
                    "form_score": 0.95,
                    "endurance_level": "excellent"
                },
                "timeline": {
                    "start_date": datetime.now(),
                    "target_date": datetime.now() + timedelta(days=30),
                    "milestones": [
                        {
                            "date": datetime.now() + timedelta(days=10),
                            "target": {
                                "range_of_motion": 0.92,
                                "form_score": 0.90,
                                "endurance_level": "very_good"
                            }
                        },
                        {
                            "date": datetime.now() + timedelta(days=20),
                            "target": {
                                "range_of_motion": 0.93,
                                "form_score": 0.93,
                                "endurance_level": "very_good"
                            }
                        }
                    ]
                },
                "progress_tracking": {
                    "frequency": "weekly",
                    "metrics_to_track": ["range_of_motion", "form_score", "endurance_level"]
                }
            },
            "confidence_score": 0.85
        }
    ]

    for goal_data in movement_goals:
        goal = MovementGoal(**goal_data)
        session.add(goal)

    await session.flush()
    print("Movement goals seeded successfully!") 