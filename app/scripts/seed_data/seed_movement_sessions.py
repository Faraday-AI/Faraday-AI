from datetime import datetime, timedelta
from app.services.physical_education.models.movement import MovementSession

async def seed_movement_sessions(session):
    """Seed the movement_sessions table with initial data."""
    movement_sessions = [
        {
            "student_id": 1,
            "session_type": "jump_rope",
            "start_time": datetime.now() - timedelta(days=1),
            "end_time": datetime.now() - timedelta(days=1) + timedelta(minutes=30),
            "session_data": {
                "warmup": {
                    "duration": "5 minutes",
                    "exercises": ["arm_circles", "leg_swings", "light_jumps"]
                },
                "main_activity": {
                    "duration": "20 minutes",
                    "exercises": [
                        {
                            "name": "basic_jumps",
                            "duration": "5 minutes",
                            "sets": 3,
                            "rest": "30 seconds"
                        },
                        {
                            "name": "alternating_foot",
                            "duration": "5 minutes",
                            "sets": 3,
                            "rest": "30 seconds"
                        }
                    ]
                },
                "cooldown": {
                    "duration": "5 minutes",
                    "exercises": ["walking", "stretching"]
                }
            },
            "performance_metrics": {
                "total_jumps": 500,
                "average_height": 0.15,
                "consistency_score": 0.85,
                "endurance_level": "good"
            }
        },
        {
            "student_id": 1,
            "session_type": "basketball_dribbling",
            "start_time": datetime.now() - timedelta(days=2),
            "end_time": datetime.now() - timedelta(days=2) + timedelta(minutes=45),
            "session_data": {
                "warmup": {
                    "duration": "10 minutes",
                    "exercises": ["ball_handling", "stationary_dribble"]
                },
                "main_activity": {
                    "duration": "30 minutes",
                    "exercises": [
                        {
                            "name": "crossover_dribble",
                            "duration": "10 minutes",
                            "sets": 3,
                            "rest": "1 minute"
                        },
                        {
                            "name": "speed_dribble",
                            "duration": "10 minutes",
                            "sets": 3,
                            "rest": "1 minute"
                        }
                    ]
                },
                "cooldown": {
                    "duration": "5 minutes",
                    "exercises": ["light_dribble", "stretching"]
                }
            },
            "performance_metrics": {
                "ball_control_score": 0.88,
                "speed_rating": "medium",
                "consistency_score": 0.82,
                "weak_hand_proficiency": 0.75
            }
        },
        {
            "student_id": 2,
            "session_type": "soccer_passing",
            "start_time": datetime.now() - timedelta(days=3),
            "end_time": datetime.now() - timedelta(days=3) + timedelta(minutes=40),
            "session_data": {
                "warmup": {
                    "duration": "8 minutes",
                    "exercises": ["ball_taps", "light_jogging"]
                },
                "main_activity": {
                    "duration": "25 minutes",
                    "exercises": [
                        {
                            "name": "short_passes",
                            "duration": "10 minutes",
                            "sets": 3,
                            "rest": "1 minute"
                        },
                        {
                            "name": "long_passes",
                            "duration": "10 minutes",
                            "sets": 3,
                            "rest": "1 minute"
                        }
                    ]
                },
                "cooldown": {
                    "duration": "7 minutes",
                    "exercises": ["walking", "stretching"]
                }
            },
            "performance_metrics": {
                "pass_accuracy": 0.78,
                "power_rating": "medium",
                "technique_score": 0.85,
                "consistency_score": 0.80
            }
        },
        {
            "student_id": 2,
            "session_type": "dynamic_warmup",
            "start_time": datetime.now() - timedelta(days=4),
            "end_time": datetime.now() - timedelta(days=4) + timedelta(minutes=25),
            "session_data": {
                "warmup": {
                    "duration": "5 minutes",
                    "exercises": ["light_jogging", "arm_circles"]
                },
                "main_activity": {
                    "duration": "15 minutes",
                    "exercises": [
                        {
                            "name": "dynamic_stretches",
                            "duration": "7 minutes",
                            "sets": 2,
                            "rest": "30 seconds"
                        },
                        {
                            "name": "mobility_drills",
                            "duration": "7 minutes",
                            "sets": 2,
                            "rest": "30 seconds"
                        }
                    ]
                },
                "cooldown": {
                    "duration": "5 minutes",
                    "exercises": ["walking", "static_stretches"]
                }
            },
            "performance_metrics": {
                "range_of_motion": 0.90,
                "form_score": 0.88,
                "consistency_score": 0.85,
                "endurance_level": "good"
            }
        }
    ]

    for session_data in movement_sessions:
        movement_session = MovementSession(**session_data)
        session.add(movement_session)

    await session.flush()
    print("Movement sessions seeded successfully!") 