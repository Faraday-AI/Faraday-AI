from datetime import datetime, timedelta
import random
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.physical_education.routine.routine_performance_models import RoutinePerformanceMetrics, RoutinePerformanceMetric
from app.models.physical_education.pe_enums.pe_types import (
    MetricType,
    MetricLevel,
    MetricStatus,
    MetricTrigger
)

def seed_performance_metrics(session):
    """Seed the performance_metrics table with initial data."""
    # First, get some routines and students to create performance metrics
    from app.models.physical_education.routine.models import Routine
    from app.models.physical_education.student.models import Student
    
    routines_result = session.execute(select(Routine.id))
    routine_ids = [row[0] for row in routines_result.fetchall()]
    
    students_result = session.execute(select(Student.id))
    student_ids = [row[0] for row in students_result.fetchall()]
    
    if not routine_ids or not student_ids:
        print("No routines or students found in the database. Please seed routines and students first.")
        return
    
    # Create some performance metrics records first
    performance_metrics_records = []
    for i in range(min(3, len(routine_ids))):
        for j in range(min(2, len(student_ids))):
            performance_record = RoutinePerformanceMetrics(
                routine_id=routine_ids[i],
                student_id=student_ids[j],
                performance_data={
                    "completion_rate": random.uniform(0.7, 1.0),
                    "energy_level": random.randint(1, 10),
                    "difficulty_rating": random.randint(1, 10)
                },
                completion_time=random.uniform(15.0, 45.0),
                accuracy_score=random.uniform(0.6, 1.0),
                effort_score=random.uniform(0.7, 1.0),
                notes=f"Performance record {i+1}-{j+1}",
                is_completed=random.choice([True, False])
            )
            session.add(performance_record)
            performance_metrics_records.append(performance_record)
    
    session.flush()
    
    # Get the IDs of the created performance records
    performance_ids = [record.id for record in performance_metrics_records]

    # Use the existing RoutinePerformanceMetric model

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
        metric = RoutinePerformanceMetric(**metric_data)
        session.add(metric)

    session.flush()
    print("Performance metrics seeded successfully!") 