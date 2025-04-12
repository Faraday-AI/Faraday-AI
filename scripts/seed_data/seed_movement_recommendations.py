from datetime import datetime
from app.services.physical_education.models.movement import MovementRecommendation

async def seed_movement_recommendations(session):
    """Seed the movement_recommendations table with initial data."""
    movement_recommendations = [
        {
            "analysis_id": 1,  # Jump Rope Analysis
            "recommendation_type": "progression",
            "recommendation_data": {
                "current_level": "intermediate",
                "target_level": "advanced",
                "recommended_actions": [
                    {
                        "action": "Increase jump complexity",
                        "details": "Introduce double-unders",
                        "timeline": "2 weeks",
                        "prerequisites": ["Consistent single jumps", "Good rhythm"]
                    },
                    {
                        "action": "Enhance endurance",
                        "details": "Add interval training",
                        "timeline": "3 weeks",
                        "prerequisites": ["Basic stamina", "Proper form"]
                    }
                ],
                "success_metrics": {
                    "double_unders": "5 consecutive",
                    "endurance": "5 minutes continuous"
                }
            },
            "confidence_score": 0.92
        },
        {
            "analysis_id": 2,  # Basketball Dribbling Analysis
            "recommendation_type": "skill_development",
            "recommendation_data": {
                "current_skills": ["Basic dribble", "Stationary control"],
                "target_skills": ["Advanced dribble moves", "Game-speed control"],
                "recommended_actions": [
                    {
                        "action": "Master crossover",
                        "details": "Practice stationary then moving",
                        "timeline": "2 weeks",
                        "prerequisites": ["Basic ball control", "Proper stance"]
                    },
                    {
                        "action": "Develop weak hand",
                        "details": "Dedicated weak hand drills",
                        "timeline": "4 weeks",
                        "prerequisites": ["Strong hand proficiency"]
                    }
                ],
                "success_metrics": {
                    "crossover": "Clean execution at game speed",
                    "weak_hand": "Equal control both hands"
                }
            },
            "confidence_score": 0.88
        },
        {
            "analysis_id": 3,  # Soccer Passing Analysis
            "recommendation_type": "technique_refinement",
            "recommendation_data": {
                "current_technique": "Basic passing",
                "target_technique": "Advanced passing",
                "recommended_actions": [
                    {
                        "action": "Improve long passes",
                        "details": "Focus on power and accuracy",
                        "timeline": "3 weeks",
                        "prerequisites": ["Proper form", "Basic accuracy"]
                    },
                    {
                        "action": "Develop weighted passes",
                        "details": "Practice different pass types",
                        "timeline": "4 weeks",
                        "prerequisites": ["Consistent technique"]
                    }
                ],
                "success_metrics": {
                    "long_passes": "30m accuracy 80%",
                    "weighted_passes": "3 different types mastered"
                }
            },
            "confidence_score": 0.90
        },
        {
            "analysis_id": 4,  # Dynamic Warm-up Analysis
            "recommendation_type": "routine_enhancement",
            "recommendation_data": {
                "current_routine": "Basic dynamic stretches",
                "target_routine": "Advanced dynamic preparation",
                "recommended_actions": [
                    {
                        "action": "Add resistance training",
                        "details": "Incorporate bands and weights",
                        "timeline": "2 weeks",
                        "prerequisites": ["Proper form", "Basic mobility"]
                    },
                    {
                        "action": "Enhance mobility",
                        "details": "Advanced range of motion exercises",
                        "timeline": "3 weeks",
                        "prerequisites": ["Good flexibility"]
                    }
                ],
                "success_metrics": {
                    "resistance": "Proper form with added weight",
                    "mobility": "Increased range of motion"
                }
            },
            "confidence_score": 0.85
        }
    ]

    for recommendation_data in movement_recommendations:
        recommendation = MovementRecommendation(**recommendation_data)
        session.add(recommendation)

    await session.flush()
    print("Movement recommendations seeded successfully!") 