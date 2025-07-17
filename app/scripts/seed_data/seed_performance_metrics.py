from datetime import datetime, timedelta
import random
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.routine import RoutinePerformance
from app.models.physical_education.pe_enums.pe_types import (
    MetricType,
    MetricLevel,
    MetricStatus,
    MetricTrigger
)

def seed_performance_metrics(session):
    """Seed the performance_metrics table with initial data."""
    # First, get the actual performance IDs from the database
    result = session.execute(select(RoutinePerformance.id))
    performance_ids = [row[0] for row in result.fetchall()]
    
    if not performance_ids:
        print("No routine performances found in the database. Please seed routine performances first.")
        return

    # Create a simple PerformanceMetrics model for seeding
    from sqlalchemy import Column, Integer, String, Float, JSON, ForeignKey, DateTime
    from app.models.shared_base import SharedBase
    
    class SeedPerformanceMetrics(SharedBase):
        """Model for seeding performance metrics."""
        __tablename__ = "seed_performance_metrics"
        __table_args__ = {'extend_existing': True}

        id = Column(Integer, primary_key=True, index=True)
        performance_id = Column(Integer, ForeignKey("routine_performances.id", ondelete='CASCADE'), nullable=False)
        metric_type = Column(String(50), nullable=False)
        metric_value = Column(Float, nullable=False)
        metric_data = Column(JSON, nullable=True)
        created_at = Column(DateTime, default=datetime.utcnow)

    performance_metrics = [
        {
            "performance_id": performance_ids[0],  # First performance
            "metric_type": "endurance",
            "metric_value": 0.80,
            "metric_data": {
                "unit": "score",
                "notes": "Good endurance for basic jumps",
                "timestamp": (datetime.now() - timedelta(days=1)).isoformat()
            }
        },
        {
            "performance_id": performance_ids[0],  # First performance
            "metric_type": "accuracy",
            "metric_value": 0.85,
            "metric_data": {
                "unit": "score",
                "notes": "Consistent rhythm and timing",
                "timestamp": (datetime.now() - timedelta(days=1)).isoformat()
            }
        },
        {
            "performance_id": performance_ids[1],  # Second performance
            "metric_type": "ball_control",
            "metric_value": 0.88,
            "metric_data": {
                "unit": "score",
                "notes": "Excellent ball handling skills",
                "timestamp": (datetime.now() - timedelta(days=2)).isoformat()
            }
        },
        {
            "performance_id": performance_ids[1],  # Second performance
            "metric_type": "speed",
            "metric_value": 0.75,
            "metric_data": {
                "unit": "score",
                "notes": "Needs improvement in fast dribbling",
                "timestamp": (datetime.now() - timedelta(days=2)).isoformat()
            }
        },
        {
            "performance_id": performance_ids[2],  # Third performance
            "metric_type": "accuracy",
            "metric_value": 0.75,
            "metric_data": {
                "unit": "score",
                "notes": "Good short pass accuracy",
                "timestamp": (datetime.now() - timedelta(days=3)).isoformat()
            }
        },
        {
            "performance_id": performance_ids[2],  # Third performance
            "metric_type": "power",
            "metric_value": 0.70,
            "metric_data": {
                "unit": "score",
                "notes": "Needs more power in long passes",
                "timestamp": (datetime.now() - timedelta(days=3)).isoformat()
            }
        }
    ]

    for metric_data in performance_metrics:
        metric = SeedPerformanceMetrics(**metric_data)
        session.add(metric)

    session.flush()
    print("Performance metrics seeded successfully!") 