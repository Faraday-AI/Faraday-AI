from datetime import datetime, timedelta
from app.services.physical_education.models.movement import MovementInsight

async def seed_movement_insights(session):
    """Seed the movement_insights table with initial data."""
    movement_insights = [
        {
            "student_id": 1,
            "movement_type": "jump_rope",
            "insight_data": {
                "key_insights": [
                    {
                        "title": "Endurance Breakthrough",
                        "description": "Student shows significant improvement in endurance, maintaining consistent rhythm for longer periods",
                        "impact": "high",
                        "evidence": {
                            "metrics": ["endurance_score", "consistency_score"],
                            "trend": "45% improvement over 30 days"
                        }
                    },
                    {
                        "title": "Form Consistency",
                        "description": "Landing technique has improved but still needs work during fatigue",
                        "impact": "medium",
                        "evidence": {
                            "metrics": ["landing_score", "fatigue_impact"],
                            "trend": "15% improvement, 10% drop during fatigue"
                        }
                    }
                ],
                "recommendations": [
                    {
                        "priority": "high",
                        "action": "Focus on fatigue management",
                        "rationale": "Performance drops significantly after 3 minutes",
                        "expected_impact": "Improve consistency during longer sessions"
                    },
                    {
                        "priority": "medium",
                        "action": "Work on landing technique",
                        "rationale": "Soft landings improve endurance and reduce injury risk",
                        "expected_impact": "Increase session duration and consistency"
                    }
                ],
                "correlations": {
                    "practice_frequency": "Strong positive correlation with improvement",
                    "rest_periods": "Optimal rest period identified at 30 seconds",
                    "time_of_day": "Better performance in morning sessions"
                }
            },
            "confidence_score": 0.92
        },
        {
            "student_id": 1,
            "movement_type": "basketball_dribbling",
            "insight_data": {
                "key_insights": [
                    {
                        "title": "Weak Hand Development",
                        "description": "Significant progress in weak hand control, now approaching strong hand proficiency",
                        "impact": "high",
                        "evidence": {
                            "metrics": ["weak_hand_score", "control_balance"],
                            "trend": "30% improvement in weak hand over 30 days"
                        }
                    },
                    {
                        "title": "Head Position Awareness",
                        "description": "Student tends to look down during complex moves",
                        "impact": "medium",
                        "evidence": {
                            "metrics": ["head_position_score", "complex_move_accuracy"],
                            "trend": "20% accuracy drop during complex moves"
                        }
                    }
                ],
                "recommendations": [
                    {
                        "priority": "high",
                        "action": "Continue weak hand development",
                        "rationale": "Current progress shows strong potential",
                        "expected_impact": "Achieve equal proficiency in both hands"
                    },
                    {
                        "priority": "medium",
                        "action": "Practice looking up during drills",
                        "rationale": "Improves game awareness and control",
                        "expected_impact": "Better performance in game situations"
                    }
                ],
                "correlations": {
                    "drill_complexity": "Performance drops with increased complexity",
                    "practice_duration": "Optimal session length is 45 minutes",
                    "rest_frequency": "Better results with more frequent short breaks"
                }
            },
            "confidence_score": 0.88
        },
        {
            "student_id": 2,
            "movement_type": "soccer_passing",
            "insight_data": {
                "key_insights": [
                    {
                        "title": "Power Generation",
                        "description": "Student shows good technique but needs to develop more power",
                        "impact": "high",
                        "evidence": {
                            "metrics": ["power_rating", "technique_score"],
                            "trend": "Technique at 90%, power at 75%"
                        }
                    },
                    {
                        "title": "Follow-through Consistency",
                        "description": "Incomplete follow-through affects long pass accuracy",
                        "impact": "medium",
                        "evidence": {
                            "metrics": ["follow_through_score", "long_pass_accuracy"],
                            "trend": "20% accuracy difference between short and long passes"
                        }
                    }
                ],
                "recommendations": [
                    {
                        "priority": "high",
                        "action": "Focus on leg drive and power generation",
                        "rationale": "Good technique foundation needs power development",
                        "expected_impact": "Improve pass distance and accuracy"
                    },
                    {
                        "priority": "medium",
                        "action": "Work on complete follow-through",
                        "rationale": "Affects both power and accuracy",
                        "expected_impact": "More consistent long passes"
                    }
                ],
                "correlations": {
                    "power_vs_accuracy": "Strong correlation between power and accuracy",
                    "practice_frequency": "Better results with daily practice",
                    "rest_duration": "Optimal rest period is 1 minute between sets"
                }
            },
            "confidence_score": 0.90
        },
        {
            "student_id": 2,
            "movement_type": "dynamic_warmup",
            "insight_data": {
                "key_insights": [
                    {
                        "title": "Breathing Pattern",
                        "description": "Student shows inconsistent breathing during transitions",
                        "impact": "medium",
                        "evidence": {
                            "metrics": ["breathing_consistency", "transition_smoothness"],
                            "trend": "Breathing affects movement fluidity"
                        }
                    },
                    {
                        "title": "Range of Motion",
                        "description": "Good flexibility but could improve in certain movements",
                        "impact": "high",
                        "evidence": {
                            "metrics": ["range_of_motion", "movement_quality"],
                            "trend": "15% improvement in range, 10% in quality"
                        }
                    }
                ],
                "recommendations": [
                    {
                        "priority": "high",
                        "action": "Focus on rhythmic breathing",
                        "rationale": "Improves movement quality and endurance",
                        "expected_impact": "Better exercise execution"
                    },
                    {
                        "priority": "medium",
                        "action": "Work on specific movement ranges",
                        "rationale": "Targeted improvement needed in certain areas",
                        "expected_impact": "More complete warm-up routine"
                    }
                ],
                "correlations": {
                    "breathing_vs_quality": "Strong correlation between breathing and movement quality",
                    "time_of_day": "Better performance in afternoon sessions",
                    "warmup_duration": "Optimal duration is 15-20 minutes"
                }
            },
            "confidence_score": 0.85
        }
    ]

    for insight_data in movement_insights:
        insight = MovementInsight(**insight_data)
        session.add(insight)

    await session.flush()
    print("Movement insights seeded successfully!") 