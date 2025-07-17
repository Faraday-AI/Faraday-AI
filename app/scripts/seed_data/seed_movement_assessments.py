from datetime import datetime, timedelta
from app.services.physical_education.models.movement import MovementAssessment

async def seed_movement_assessments(session):
    """Seed the movement_assessments table with initial data."""
    movement_assessments = [
        {
            "student_id": 1,
            "movement_type": "jump_rope",
            "assessment_data": {
                "form_analysis": {
                    "posture": {
                        "score": 0.85,
                        "notes": "Good upright posture, slight forward lean during fatigue"
                    },
                    "arm_position": {
                        "score": 0.90,
                        "notes": "Consistent elbow position, good wrist movement"
                    },
                    "landing": {
                        "score": 0.80,
                        "notes": "Mostly soft landings, occasional heavy impact"
                    }
                },
                "performance_metrics": {
                    "rhythm_consistency": 0.88,
                    "jump_height_consistency": 0.82,
                    "endurance_score": 0.85
                },
                "recommendations": [
                    "Focus on softer landings",
                    "Maintain posture during fatigue",
                    "Work on jump height consistency"
                ]
            },
            "confidence_score": 0.92
        },
        {
            "student_id": 1,
            "movement_type": "basketball_dribbling",
            "assessment_data": {
                "form_analysis": {
                    "stance": {
                        "score": 0.88,
                        "notes": "Good athletic stance, needs to stay lower"
                    },
                    "hand_control": {
                        "score": 0.85,
                        "notes": "Strong hand excellent, weak hand needs work"
                    },
                    "head_position": {
                        "score": 0.75,
                        "notes": "Often looking at ball, needs to keep head up"
                    }
                },
                "performance_metrics": {
                    "ball_control_score": 0.82,
                    "speed_rating": "medium",
                    "weak_hand_proficiency": 0.70
                },
                "recommendations": [
                    "Practice keeping head up",
                    "Focus on weak hand development",
                    "Maintain lower stance"
                ]
            },
            "confidence_score": 0.88
        },
        {
            "student_id": 2,
            "movement_type": "soccer_passing",
            "assessment_data": {
                "form_analysis": {
                    "plant_foot": {
                        "score": 0.90,
                        "notes": "Good placement, consistent positioning"
                    },
                    "striking_foot": {
                        "score": 0.85,
                        "notes": "Good technique, needs more power"
                    },
                    "follow_through": {
                        "score": 0.80,
                        "notes": "Incomplete follow-through on long passes"
                    }
                },
                "performance_metrics": {
                    "pass_accuracy": 0.78,
                    "power_rating": "medium",
                    "technique_score": 0.82
                },
                "recommendations": [
                    "Work on complete follow-through",
                    "Develop more power in passes",
                    "Maintain accuracy with increased power"
                ]
            },
            "confidence_score": 0.90
        },
        {
            "student_id": 2,
            "movement_type": "dynamic_warmup",
            "assessment_data": {
                "form_analysis": {
                    "range_of_motion": {
                        "score": 0.88,
                        "notes": "Good flexibility, could increase range"
                    },
                    "control": {
                        "score": 0.85,
                        "notes": "Good control, needs smoother transitions"
                    },
                    "breathing": {
                        "score": 0.80,
                        "notes": "Inconsistent breathing pattern"
                    }
                },
                "performance_metrics": {
                    "mobility_score": 0.85,
                    "form_consistency": 0.82,
                    "endurance_rating": "good"
                },
                "recommendations": [
                    "Focus on breathing patterns",
                    "Work on smoother transitions",
                    "Increase range of motion gradually"
                ]
            },
            "confidence_score": 0.85
        }
    ]

    for assessment_data in movement_assessments:
        assessment = MovementAssessment(**assessment_data)
        session.add(assessment)

    await session.flush()
    print("Movement assessments seeded successfully!") 