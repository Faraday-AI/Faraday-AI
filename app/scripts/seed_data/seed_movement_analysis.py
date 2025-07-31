from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.models.physical_education.movement_analysis.movement_models import MovementAnalysisRecord, MovementPattern
from app.models.student import Student
from app.models.activity import Activity
import json
import random

async def seed_movement_analysis(session: AsyncSession):
    """Seed movement analysis data."""
    print("Seeding movement analysis data...")
    
    # Delete existing data
    await session.execute(text("DELETE FROM movement_patterns"))
    await session.execute(text("DELETE FROM movement_analysis"))
    print("Deleted existing movement analysis data")
    
    # Get students and activities
    students = (await session.execute(text("SELECT id FROM students"))).scalars().all()
    activities = (await session.execute(text("SELECT id FROM activities"))).scalars().all()
    
    if not students or not activities:
        print("No students or activities found. Skipping movement analysis seeding.")
        return
    
    # Create movement analysis records
    movement_analyses = []
    for student_id in students:
        for activity_id in activities:
            # Create movement data
            movement_data = {
                "key_points": {
                    "shoulder": [
                        {"x": 0.5, "y": 0.6, "z": 0.0, "visibility": 0.9},
                        {"x": 0.6, "y": 0.6, "z": 0.0, "visibility": 0.9}
                    ],
                    "hip": [
                        {"x": 0.5, "y": 0.7, "z": 0.0, "visibility": 0.9},
                        {"x": 0.6, "y": 0.7, "z": 0.0, "visibility": 0.9}
                    ],
                    "knee": [
                        {"x": 0.5, "y": 0.8, "z": 0.0, "visibility": 0.9},
                        {"x": 0.6, "y": 0.8, "z": 0.0, "visibility": 0.9}
                    ],
                    "ankle": [
                        {"x": 0.5, "y": 0.9, "z": 0.0, "visibility": 0.9},
                        {"x": 0.6, "y": 0.9, "z": 0.0, "visibility": 0.9}
                    ]
                },
                "metrics": {
                    "smoothness": random.uniform(0.6, 1.0),
                    "consistency": random.uniform(0.6, 1.0),
                    "speed": random.uniform(0.6, 1.0),
                    "range_of_motion": random.uniform(0.6, 1.0)
                }
            }
            
            # Create analysis results
            analysis_results = {
                "form_score": random.uniform(0.6, 1.0),
                "alignment_score": random.uniform(0.6, 1.0),
                "stability_score": random.uniform(0.6, 1.0),
                "recommendations": ["Focus on knee alignment", "Improve shoulder stability"]
            }
            
            # Create movement analysis record
            analysis = MovementAnalysisRecord(
                student_id=student_id,
                activity_id=activity_id,
                timestamp=datetime.utcnow(),
                movement_data=movement_data,
                analysis_results=analysis_results,
                confidence_score=random.uniform(0.7, 1.0),
                is_completed=True
            )
            movement_analyses.append(analysis)
    
    # Add all movement analyses to session
    session.add_all(movement_analyses)
    await session.flush()  # Flush to get IDs
    
    # Create movement patterns for each analysis
    movement_patterns = []
    for analysis in movement_analyses:
        # Create pattern data
        pattern_data = {
            "sequence": [
                {"frame": 1, "key_points": analysis.movement_data["key_points"]["shoulder"][0]},
                {"frame": 5, "key_points": analysis.movement_data["key_points"]["hip"][0]},
                {"frame": 10, "key_points": analysis.movement_data["key_points"]["knee"][0]},
                {"frame": 15, "key_points": analysis.movement_data["key_points"]["ankle"][0]}
            ],
            "metrics": {
                "average_speed": random.uniform(0.5, 2.0),
                "peak_force": random.uniform(0.5, 1.0),
                "efficiency": random.uniform(0.6, 1.0)
            }
        }
        
        # Create movement pattern record
        pattern = MovementPattern(
            analysis_id=analysis.id,
            pattern_type=random.choice(["jumping", "running", "throwing", "catching"]),
            confidence_score=random.uniform(0.7, 1.0),
            pattern_data=pattern_data,
            duration=random.uniform(2.0, 10.0),
            repetitions=random.randint(5, 20),
            quality_score=random.uniform(0.6, 1.0),
            notes="Good form overall, needs improvement in landing technique"
        )
        movement_patterns.append(pattern)
    
    # Add all movement patterns to session
    session.add_all(movement_patterns)
    
    print("Movement analysis data seeded successfully!") 