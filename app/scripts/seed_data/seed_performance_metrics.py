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
    print("  Starting comprehensive performance metrics seeding...")
    
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
    
    print(f"    Found {len(routine_ids)} routines and {len(student_ids)} students")
    
    # Create some performance metrics records first
    performance_metrics_records = []
    for i in range(min(10, len(routine_ids))):
        for j in range(min(20, len(student_ids))):
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
    print(f"    Created {len(performance_metrics_records)} initial performance records")
    
    # ADDITIONAL: Create comprehensive performance metrics records for more data
    print("  Creating additional comprehensive performance metrics...")
    additional_records = []
    
    # Create 1000+ additional performance records (50 routines × 20+ students)
    for i in range(min(50, len(routine_ids))):
        for j in range(min(20, len(student_ids))):
            additional_record = RoutinePerformanceMetrics(
                routine_id=routine_ids[i],
                student_id=student_ids[j],
                performance_data={
                    "completion_rate": random.uniform(0.7, 1.0),
                    "energy_level": random.randint(1, 10),
                    "difficulty_rating": random.randint(1, 10),
                    "heart_rate": random.randint(120, 180),
                    "calories_burned": random.uniform(50, 300),
                    "steps_taken": random.randint(500, 2000)
                },
                completion_time=random.uniform(15.0, 45.0),
                accuracy_score=random.uniform(0.6, 1.0),
                effort_score=random.uniform(0.7, 1.0),
                notes=f"Additional comprehensive performance record for routine {i+1} by student {j+1}",
                is_completed=random.choice([True, False])
            )
            session.add(additional_record)
            additional_records.append(additional_record)
            
            # Flush every 100 records to manage memory
            if len(additional_records) % 100 == 0:
                session.flush()
                print(f"      Created {len(additional_records)} additional performance records...")
    
    # Combine all records
    all_performance_records = performance_metrics_records + additional_records
    print(f"  Total performance records created: {len(all_performance_records)}")
    
    session.flush()
    
    # Get the IDs of the created performance records
    performance_ids = [record.id for record in performance_metrics_records]
    
    # ADDITIONAL: Get IDs from additional records too
    additional_performance_ids = [record.id for record in additional_records]
    all_performance_ids = performance_ids + additional_performance_ids

    # Create initial individual metrics
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
    print(f"    Created {len(performance_metrics)} initial individual metrics")

    # ADDITIONAL: Create comprehensive individual metrics for each performance record
    print("    Creating additional comprehensive individual metrics...")
    metric_types = ["endurance", "accuracy", "speed", "power", "coordination", "flexibility", "strength", "balance", "agility", "reaction_time", "stamina", "technique"]
    
    additional_individual_metrics_created = 0
    
    # Create 5-8 metrics per performance record for comprehensive coverage
    for performance_id in all_performance_ids:
        num_metrics = random.randint(5, 8)
        for metric_idx in range(num_metrics):
            metric_type = random.choice(metric_types)
            metric = RoutinePerformanceMetric(
                performance_id=performance_id,
                metric_type=metric_type,
                metric_value=random.uniform(0.6, 1.0),
                metric_data={
                    "unit": "score",
                    "notes": f"Additional metric {metric_idx + 1} for {metric_type}",
                    "timestamp": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat(),
                    "assessment_method": random.choice(["teacher_observation", "peer_assessment", "self_assessment", "technology_tracking", "video_analysis", "sensor_data"]),
                    "context": random.choice(["practice_session", "assessment", "competition", "training", "evaluation"]),
                    "environment": random.choice(["indoor", "outdoor", "gym", "field", "court", "track"]),
                    "equipment_used": random.choice(["none", "basic", "advanced", "specialized"]),
                    "weather_conditions": random.choice(["clear", "rainy", "windy", "hot", "cold", "indoor"]),
                    "time_of_day": random.choice(["morning", "afternoon", "evening", "night"]),
                    "student_mood": random.choice(["motivated", "tired", "excited", "focused", "distracted"]),
                    "difficulty_level": random.choice(["easy", "moderate", "challenging", "difficult"]),
                    "improvement_trend": random.choice(["improving", "stable", "declining", "variable"]),
                    "recommendations": f"Focus on improving {metric_type} through targeted practice and feedback"
                }
            )
            session.add(metric)
            additional_individual_metrics_created += 1
            
            # Flush every 200 metrics to manage memory
            if additional_individual_metrics_created % 200 == 0:
                session.flush()
                print(f"      Created {additional_individual_metrics_created} additional individual metrics...")
    
    session.flush()
    print(f"    Created {additional_individual_metrics_created} additional comprehensive individual metrics")
    
    # ADDITIONAL: Create specialized metric categories for better data distribution
    print("    Creating specialized metric categories...")
    specialized_metrics_created = 0
    
    # Create specialized metrics for different performance aspects
    specialized_types = {
        "cardiovascular": ["heart_rate", "blood_pressure", "oxygen_saturation", "recovery_rate"],
        "muscular": ["strength_upper", "strength_lower", "endurance_upper", "endurance_lower", "power_output"],
        "flexibility": ["range_of_motion", "joint_mobility", "muscle_length", "stretching_capacity"],
        "coordination": ["balance", "agility", "reaction_time", "hand_eye_coordination", "foot_eye_coordination"],
        "cognitive": ["focus", "decision_making", "strategy_execution", "adaptability", "learning_rate"],
        "social": ["teamwork", "leadership", "communication", "sportsmanship", "motivation"]
    }
    
    for performance_id in all_performance_ids[:min(100, len(all_performance_ids))]:  # Limit to first 100 for specialized metrics
        for category, metric_types in specialized_types.items():
            for metric_type in metric_types:
                if random.random() < 0.3:  # 30% chance for each specialized metric
                    metric = RoutinePerformanceMetric(
                        performance_id=performance_id,
                        metric_type=metric_type,
                        metric_value=random.uniform(0.5, 1.0),
                        metric_data={
                            "unit": "score",
                            "category": category,
                            "notes": f"Specialized {category} metric for {metric_type}",
                            "timestamp": (datetime.now() - timedelta(days=random.randint(1, 60))).isoformat(),
                            "assessment_method": "specialized_testing",
                            "context": "comprehensive_evaluation",
                            "significance": random.choice(["high", "medium", "low"]),
                            "trend_analysis": random.choice(["positive", "stable", "negative", "improving"]),
                            "recommendations": f"Focus on {category} development through targeted training"
                        }
                    )
                    session.add(metric)
                    specialized_metrics_created += 1
                    
                    if specialized_metrics_created % 100 == 0:
                        session.flush()
                        print(f"      Created {specialized_metrics_created} specialized metrics...")
    
    session.flush()
    print(f"    Created {specialized_metrics_created} specialized category metrics")
    
    print("Performance metrics seeded successfully!")
    
    # Return count of created records
    performance_metrics_count = len(all_performance_records)
    total_metrics_count = len(performance_metrics) + additional_individual_metrics_created + specialized_metrics_created
    
    print(f"    Final counts:")
    print(f"      - Performance Records: {performance_metrics_count}")
    print(f"      - Total Individual Metrics: {total_metrics_count}")
    print(f"      - Initial Metrics: {len(performance_metrics)}")
    print(f"      - Additional Metrics: {additional_individual_metrics_created}")
    print(f"      - Specialized Metrics: {specialized_metrics_created}")
    
    return performance_metrics_count, total_metrics_count