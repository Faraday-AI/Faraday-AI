from datetime import datetime, timedelta
from app.services.physical_education.models.movement import MovementAnalytics

async def seed_movement_analytics(session):
    """Seed the movement_analytics table with initial data."""
    movement_analytics = [
        {
            "student_id": 1,
            "movement_type": "jump_rope",
            "analytics_data": {
                "performance_trends": {
                    "jump_count": {
                        "daily_average": 750,
                        "weekly_trend": "+15%",
                        "monthly_trend": "+45%"
                    },
                    "consistency": {
                        "daily_average": 0.85,
                        "weekly_trend": "+5%",
                        "monthly_trend": "+20%"
                    },
                    "endurance": {
                        "daily_average": "4 minutes",
                        "weekly_trend": "+10%",
                        "monthly_trend": "+50%"
                    }
                },
                "improvement_areas": {
                    "landing_technique": {
                        "current_score": 0.80,
                        "trend": "improving",
                        "recommendation": "Focus on soft landings"
                    },
                    "rhythm_consistency": {
                        "current_score": 0.85,
                        "trend": "stable",
                        "recommendation": "Maintain current practice"
                    }
                },
                "correlation_analysis": {
                    "endurance_vs_consistency": 0.75,
                    "practice_frequency_vs_improvement": 0.82,
                    "form_vs_performance": 0.88
                }
            },
            "confidence_score": 0.92
        },
        {
            "student_id": 1,
            "movement_type": "basketball_dribbling",
            "analytics_data": {
                "performance_trends": {
                    "ball_control": {
                        "daily_average": 0.85,
                        "weekly_trend": "+8%",
                        "monthly_trend": "+25%"
                    },
                    "weak_hand": {
                        "daily_average": 0.75,
                        "weekly_trend": "+10%",
                        "monthly_trend": "+30%"
                    },
                    "speed_rating": {
                        "daily_average": "medium_high",
                        "weekly_trend": "improving",
                        "monthly_trend": "low → medium_high"
                    }
                },
                "improvement_areas": {
                    "head_position": {
                        "current_score": 0.75,
                        "trend": "improving",
                        "recommendation": "Practice looking up"
                    },
                    "weak_hand_control": {
                        "current_score": 0.75,
                        "trend": "improving",
                        "recommendation": "Continue weak hand drills"
                    }
                },
                "correlation_analysis": {
                    "practice_time_vs_control": 0.78,
                    "weak_hand_vs_overall": 0.85,
                    "speed_vs_accuracy": 0.72
                }
            },
            "confidence_score": 0.88
        },
        {
            "student_id": 2,
            "movement_type": "soccer_passing",
            "analytics_data": {
                "performance_trends": {
                    "accuracy": {
                        "daily_average": 0.78,
                        "weekly_trend": "+7%",
                        "monthly_trend": "+25%"
                    },
                    "power": {
                        "daily_average": "medium",
                        "weekly_trend": "improving",
                        "monthly_trend": "low → medium"
                    },
                    "technique": {
                        "daily_average": 0.82,
                        "weekly_trend": "+5%",
                        "monthly_trend": "+20%"
                    }
                },
                "improvement_areas": {
                    "follow_through": {
                        "current_score": 0.80,
                        "trend": "improving",
                        "recommendation": "Focus on complete motion"
                    },
                    "power_generation": {
                        "current_score": 0.75,
                        "trend": "improving",
                        "recommendation": "Work on leg drive"
                    }
                },
                "correlation_analysis": {
                    "power_vs_accuracy": 0.68,
                    "technique_vs_consistency": 0.82,
                    "practice_frequency_vs_improvement": 0.75
                }
            },
            "confidence_score": 0.90
        },
        {
            "student_id": 2,
            "movement_type": "dynamic_warmup",
            "analytics_data": {
                "performance_trends": {
                    "range_of_motion": {
                        "daily_average": 0.88,
                        "weekly_trend": "+5%",
                        "monthly_trend": "+15%"
                    },
                    "form_consistency": {
                        "daily_average": 0.85,
                        "weekly_trend": "+4%",
                        "monthly_trend": "+12%"
                    },
                    "endurance": {
                        "daily_average": "good",
                        "weekly_trend": "improving",
                        "monthly_trend": "fair → good"
                    }
                },
                "improvement_areas": {
                    "breathing_pattern": {
                        "current_score": 0.80,
                        "trend": "improving",
                        "recommendation": "Focus on rhythmic breathing"
                    },
                    "transition_smoothness": {
                        "current_score": 0.82,
                        "trend": "stable",
                        "recommendation": "Practice fluid movements"
                    }
                },
                "correlation_analysis": {
                    "flexibility_vs_form": 0.85,
                    "breathing_vs_endurance": 0.78,
                    "practice_consistency_vs_improvement": 0.82
                }
            },
            "confidence_score": 0.85
        }
    ]

    for analytics_data in movement_analytics:
        analytics = MovementAnalytics(**analytics_data)
        session.add(analytics)

    await session.flush()
    print("Movement analytics seeded successfully!") 