from datetime import datetime, timedelta
from app.services.physical_education.models.movement import MovementAnalysis

async def seed_movement_analysis(session):
    """Seed the movement_analysis table with initial data."""
    movement_analyses = [
        {
            "student_id": "STU001",
            "activity_id": 1,  # Jump Rope Basics
            "timestamp": datetime.now() - timedelta(days=1),
            "movement_data": {
                "jump_height": 0.15,
                "landing_force": 1.2,
                "rhythm_score": 0.85,
                "form_metrics": {
                    "elbow_position": "good",
                    "wrist_movement": "excellent",
                    "posture": "good"
                }
            },
            "analysis_results": {
                "overall_score": 0.82,
                "strengths": ["good rhythm", "proper form"],
                "areas_for_improvement": ["increase jump height", "reduce landing force"],
                "recommendations": ["practice higher jumps", "focus on soft landings"]
            },
            "confidence_score": 0.95,
            "is_completed": True
        },
        {
            "student_id": "STU002",
            "activity_id": 2,  # Basketball Dribbling
            "timestamp": datetime.now() - timedelta(days=2),
            "movement_data": {
                "dribble_height": 0.3,
                "control_score": 0.88,
                "speed_metrics": {
                    "average_speed": 2.5,
                    "max_speed": 3.2,
                    "acceleration": 1.8
                },
                "hand_placement": "correct"
            },
            "analysis_results": {
                "overall_score": 0.85,
                "strengths": ["good control", "proper hand placement"],
                "areas_for_improvement": ["increase speed", "maintain consistency"],
                "recommendations": ["practice speed drills", "focus on rhythm"]
            },
            "confidence_score": 0.92,
            "is_completed": True
        },
        {
            "student_id": "STU003",
            "activity_id": 3,  # Soccer Passing
            "timestamp": datetime.now() - timedelta(days=3),
            "movement_data": {
                "pass_accuracy": 0.75,
                "power_score": 0.68,
                "technique_metrics": {
                    "foot_placement": "good",
                    "follow_through": "needs_improvement",
                    "balance": "good"
                }
            },
            "analysis_results": {
                "overall_score": 0.70,
                "strengths": ["good foot placement", "maintains balance"],
                "areas_for_improvement": ["increase accuracy", "improve follow-through"],
                "recommendations": ["practice accuracy drills", "focus on technique"]
            },
            "confidence_score": 0.88,
            "is_completed": True
        },
        {
            "student_id": "STU004",
            "activity_id": 4,  # Dynamic Warm-up
            "timestamp": datetime.now() - timedelta(days=1),
            "movement_data": {
                "range_of_motion": 0.92,
                "form_score": 0.88,
                "movement_metrics": {
                    "smoothness": "excellent",
                    "control": "good",
                    "coordination": "excellent"
                }
            },
            "analysis_results": {
                "overall_score": 0.90,
                "strengths": ["excellent range of motion", "good control"],
                "areas_for_improvement": ["maintain form throughout"],
                "recommendations": ["continue current practice", "focus on consistency"]
            },
            "confidence_score": 0.94,
            "is_completed": True
        }
    ]

    for analysis_data in movement_analyses:
        analysis = MovementAnalysis(**analysis_data)
        session.add(analysis)

    await session.flush()
    print("Movement analyses seeded successfully!") 