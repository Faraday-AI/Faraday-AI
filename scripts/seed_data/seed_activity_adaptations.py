from datetime import datetime
from app.services.physical_education.models.movement import ActivityAdaptation

async def seed_activity_adaptations(session):
    """Seed the activity_adaptations table with initial data."""
    activity_adaptations = [
        {
            "analysis_id": 1,  # Jump Rope Analysis
            "adaptation_type": "intensity",
            "adaptation_data": {
                "current_level": "moderate",
                "recommended_level": "high",
                "reason": "Student shows good form and endurance",
                "implementation_guidelines": {
                    "duration_increase": "5 minutes",
                    "intensity_increase": "20%",
                    "rest_periods": "30 seconds between sets"
                }
            },
            "confidence_score": 0.88
        },
        {
            "analysis_id": 1,  # Jump Rope Analysis
            "adaptation_type": "technique",
            "adaptation_data": {
                "current_technique": "basic_jump",
                "recommended_technique": "alternating_foot",
                "reason": "Student has mastered basic jumps",
                "implementation_guidelines": {
                    "progression_steps": [
                        "Practice single-leg hops",
                        "Introduce alternating foot pattern",
                        "Gradually increase speed"
                    ],
                    "safety_considerations": [
                        "Maintain proper form",
                        "Start with slow tempo",
                        "Focus on landing technique"
                    ]
                }
            },
            "confidence_score": 0.92
        },
        {
            "analysis_id": 2,  # Basketball Dribbling Analysis
            "adaptation_type": "complexity",
            "adaptation_data": {
                "current_complexity": "basic_dribble",
                "recommended_complexity": "crossover_dribble",
                "reason": "Student shows good ball control",
                "implementation_guidelines": {
                    "progression_steps": [
                        "Practice stationary crossovers",
                        "Add movement with crossovers",
                        "Incorporate speed changes"
                    ],
                    "drill_suggestions": [
                        "Figure-8 dribble",
                        "Two-ball dribble",
                        "Defensive pressure drills"
                    ]
                }
            },
            "confidence_score": 0.85
        },
        {
            "analysis_id": 3,  # Soccer Passing Analysis
            "adaptation_type": "technique",
            "adaptation_data": {
                "current_technique": "short_pass",
                "recommended_technique": "long_pass",
                "reason": "Student has mastered short passes",
                "implementation_guidelines": {
                    "progression_steps": [
                        "Practice weight transfer",
                        "Focus on follow-through",
                        "Gradually increase distance"
                    ],
                    "drill_suggestions": [
                        "Target passing",
                        "Moving target practice",
                        "Pressure passing drills"
                    ]
                }
            },
            "confidence_score": 0.90
        },
        {
            "analysis_id": 4,  # Dynamic Warm-up Analysis
            "adaptation_type": "progression",
            "adaptation_data": {
                "current_level": "beginner",
                "recommended_level": "intermediate",
                "reason": "Student shows good mobility and control",
                "implementation_guidelines": {
                    "exercise_progressions": {
                        "arm_circles": "Add resistance bands",
                        "leg_swings": "Increase range of motion",
                        "lunges": "Add dynamic movement"
                    },
                    "intensity_guidelines": {
                        "repetitions": "Increase by 25%",
                        "hold_time": "Increase by 5 seconds",
                        "rest_periods": "Decrease by 10 seconds"
                    }
                }
            },
            "confidence_score": 0.87
        }
    ]

    for adaptation_data in activity_adaptations:
        adaptation = ActivityAdaptation(**adaptation_data)
        session.add(adaptation)

    await session.flush()
    print("Activity adaptations seeded successfully!") 