from datetime import datetime
from app.services.physical_education.models.movement import MovementMetric

async def seed_movement_metrics(session):
    """Seed the movement_metrics table with initial data."""
    movement_metrics = [
        {
            "analysis_id": 1,  # Jump Rope Analysis
            "metric_type": "jump_height",
            "value": 0.15,
            "unit": "meters",
            "timestamp": datetime.now(),
            "confidence_score": 0.92
        },
        {
            "analysis_id": 1,  # Jump Rope Analysis
            "metric_type": "landing_force",
            "value": 1.2,
            "unit": "body_weight",
            "timestamp": datetime.now(),
            "confidence_score": 0.90
        },
        {
            "analysis_id": 1,  # Jump Rope Analysis
            "metric_type": "rhythm_consistency",
            "value": 0.85,
            "unit": "percentage",
            "timestamp": datetime.now(),
            "confidence_score": 0.88
        },
        {
            "analysis_id": 2,  # Basketball Dribbling Analysis
            "metric_type": "dribble_height",
            "value": 0.3,
            "unit": "meters",
            "timestamp": datetime.now(),
            "confidence_score": 0.89
        },
        {
            "analysis_id": 2,  # Basketball Dribbling Analysis
            "metric_type": "control_score",
            "value": 0.88,
            "unit": "percentage",
            "timestamp": datetime.now(),
            "confidence_score": 0.91
        },
        {
            "analysis_id": 2,  # Basketball Dribbling Analysis
            "metric_type": "average_speed",
            "value": 2.5,
            "unit": "meters_per_second",
            "timestamp": datetime.now(),
            "confidence_score": 0.87
        },
        {
            "analysis_id": 3,  # Soccer Passing Analysis
            "metric_type": "pass_accuracy",
            "value": 0.75,
            "unit": "percentage",
            "timestamp": datetime.now(),
            "confidence_score": 0.85
        },
        {
            "analysis_id": 3,  # Soccer Passing Analysis
            "metric_type": "power_score",
            "value": 0.68,
            "unit": "percentage",
            "timestamp": datetime.now(),
            "confidence_score": 0.82
        },
        {
            "analysis_id": 4,  # Dynamic Warm-up Analysis
            "metric_type": "range_of_motion",
            "value": 0.92,
            "unit": "percentage",
            "timestamp": datetime.now(),
            "confidence_score": 0.94
        },
        {
            "analysis_id": 4,  # Dynamic Warm-up Analysis
            "metric_type": "form_score",
            "value": 0.88,
            "unit": "percentage",
            "timestamp": datetime.now(),
            "confidence_score": 0.90
        }
    ]

    for metric_data in movement_metrics:
        metric = MovementMetric(**metric_data)
        session.add(metric)

    await session.flush()
    print("Movement metrics seeded successfully!") 