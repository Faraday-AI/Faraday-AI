from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from app.models.movement_analysis.analysis.movement_analysis import MovementPattern

async def seed_movement_patterns(session):
    """Seed the movement_patterns table with initial data."""
    movement_patterns = [
        {
            "analysis_id": 1,  # Jump Rope Analysis
            "pattern_type": "jump_sequence",
            "pattern_data": {
                "sequence": ["single_jump", "single_jump", "double_jump"],
                "timing": [0.5, 0.5, 0.8],
                "consistency": 0.85,
                "variations": {
                    "height_variation": 0.1,
                    "timing_variation": 0.05
                }
            },
            "confidence_score": 0.92
        },
        {
            "analysis_id": 1,  # Jump Rope Analysis
            "pattern_type": "landing_pattern",
            "pattern_data": {
                "landing_type": "ball_of_foot",
                "force_distribution": {
                    "left_foot": 0.52,
                    "right_foot": 0.48
                },
                "stability_score": 0.88
            },
            "confidence_score": 0.90
        },
        {
            "analysis_id": 2,  # Basketball Dribbling Analysis
            "pattern_type": "dribble_sequence",
            "pattern_data": {
                "hand_usage": {
                    "right_hand": 0.55,
                    "left_hand": 0.45
                },
                "rhythm_consistency": 0.82,
                "control_patterns": {
                    "height_consistency": 0.85,
                    "speed_variation": 0.15
                }
            },
            "confidence_score": 0.88
        },
        {
            "analysis_id": 3,  # Soccer Passing Analysis
            "pattern_type": "passing_technique",
            "pattern_data": {
                "foot_placement": {
                    "plant_foot": "correct",
                    "striking_foot": "inside"
                },
                "follow_through": {
                    "direction": "target",
                    "completion": 0.75
                },
                "weight_transfer": {
                    "efficiency": 0.80,
                    "balance": 0.85
                }
            },
            "confidence_score": 0.85
        },
        {
            "analysis_id": 4,  # Dynamic Warm-up Analysis
            "pattern_type": "movement_sequence",
            "pattern_data": {
                "exercise_sequence": [
                    "arm_circles",
                    "leg_swings",
                    "torso_twists",
                    "lunges"
                ],
                "transition_smoothness": 0.90,
                "range_of_motion": {
                    "upper_body": 0.92,
                    "lower_body": 0.88,
                    "core": 0.85
                }
            },
            "confidence_score": 0.93
        }
    ]

    for pattern_data in movement_patterns:
        pattern = MovementPattern(**pattern_data)
        session.add(pattern)

    await session.flush()
    print("Movement patterns seeded successfully!") 