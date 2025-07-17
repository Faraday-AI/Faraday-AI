from datetime import datetime
from app.services.physical_education.models.movement import MovementFeedback

async def seed_movement_feedback(session):
    """Seed the movement_feedback table with initial data."""
    movement_feedback = [
        {
            "analysis_id": 1,  # Jump Rope Analysis
            "feedback_type": "form",
            "feedback_data": {
                "strengths": [
                    "Good knee bend during jumps",
                    "Consistent rhythm",
                    "Proper arm positioning"
                ],
                "areas_for_improvement": [
                    "Landing could be softer",
                    "Need to maintain consistent jump height",
                    "Focus on core engagement"
                ],
                "suggestions": [
                    "Practice landing on balls of feet",
                    "Use a mirror for height consistency",
                    "Add core exercises to routine"
                ]
            },
            "confidence_score": 0.90
        },
        {
            "analysis_id": 1,  # Jump Rope Analysis
            "feedback_type": "performance",
            "feedback_data": {
                "metrics_summary": {
                    "jump_height": "Consistent",
                    "rhythm": "Excellent",
                    "endurance": "Good"
                },
                "progress_indicators": {
                    "improvement": "15% increase in consistency",
                    "consistency": "85% of jumps within target range",
                    "endurance": "Can maintain form for 3 minutes"
                },
                "recommendations": [
                    "Increase session duration by 2 minutes",
                    "Add interval training",
                    "Incorporate double-unders"
                ]
            },
            "confidence_score": 0.88
        },
        {
            "analysis_id": 2,  # Basketball Dribbling Analysis
            "feedback_type": "technique",
            "feedback_data": {
                "strengths": [
                    "Good ball control",
                    "Proper hand positioning",
                    "Effective use of fingertips"
                ],
                "areas_for_improvement": [
                    "Need to keep head up more",
                    "Could improve weak hand dribbling",
                    "Speed control needs work"
                ],
                "drill_suggestions": [
                    "Practice dribbling while looking at target",
                    "Spend more time on weak hand",
                    "Work on speed variation drills"
                ]
            },
            "confidence_score": 0.92
        },
        {
            "analysis_id": 3,  # Soccer Passing Analysis
            "feedback_type": "form",
            "feedback_data": {
                "strengths": [
                    "Good follow-through",
                    "Proper plant foot placement",
                    "Accurate short passes"
                ],
                "areas_for_improvement": [
                    "Need more power in long passes",
                    "Weight transfer could be improved",
                    "Timing of passes needs work"
                ],
                "practice_focus": [
                    "Work on power generation",
                    "Practice weight transfer drills",
                    "Focus on timing with moving targets"
                ]
            },
            "confidence_score": 0.85
        },
        {
            "analysis_id": 4,  # Dynamic Warm-up Analysis
            "feedback_type": "execution",
            "feedback_data": {
                "strengths": [
                    "Good range of motion",
                    "Proper form in exercises",
                    "Effective warm-up routine"
                ],
                "areas_for_improvement": [
                    "Could increase intensity gradually",
                    "Need to focus on breathing",
                    "Should add more dynamic stretches"
                ],
                "routine_enhancements": [
                    "Add resistance bands to arm circles",
                    "Incorporate breathing exercises",
                    "Include more dynamic movements"
                ]
            },
            "confidence_score": 0.87
        }
    ]

    for feedback_data in movement_feedback:
        feedback = MovementFeedback(**feedback_data)
        session.add(feedback)

    await session.flush()
    print("Movement feedback seeded successfully!") 