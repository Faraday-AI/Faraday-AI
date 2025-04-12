import os
import sys
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any
import json

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.core.database import async_session
from app.core.config import settings
from app.services.physical_education.models.activity import Activity, Exercise, Routine, RoutineActivity
from app.services.physical_education.models.student import Student
from app.services.physical_education.models.class_ import Class, ClassStudent
from app.services.physical_education.models.safety import SafetyIncident, RiskAssessment
from app.services.physical_education.models.movement import (
    MovementAnalysis, MovementPattern, MovementInsight, MovementMetric,
    MovementSession, MovementProgress, MovementGoal, MovementAssessment,
    MovementChallenge, MovementAchievement, MovementAnalytic,
    MovementRecommendation, MovementFeedback
)
from app.services.physical_education.models.adaptation import ActivityAdaptation, AdaptationHistory
from app.services.physical_education.models.assessment import SkillAssessment, SkillProgress
from app.services.physical_education.models.performance import RoutinePerformance, PerformanceMetric

async def seed_database():
    """Main function to seed the database with initial data."""
    try:
        async with async_session() as session:
            # Seed in order of dependencies
            await seed_activities(session)
            await seed_students(session)
            await seed_classes(session)
            await seed_class_students(session)
            await seed_exercises(session)
            await seed_routines(session)
            await seed_routine_activities(session)
            
            # Seed movement-related data
            await seed_movement_analysis(session)
            await seed_movement_patterns(session)
            await seed_movement_insights(session)
            await seed_movement_metrics(session)
            await seed_movement_sessions(session)
            await seed_movement_progress(session)
            await seed_movement_goals(session)
            await seed_movement_assessments(session)
            await seed_movement_challenges(session)
            await seed_movement_achievements(session)
            await seed_movement_analytics(session)
            await seed_movement_recommendations(session)
            await seed_movement_feedback(session)
            
            # Seed adaptation and assessment data
            await seed_activity_adaptations(session)
            await seed_adaptation_history(session)
            await seed_skill_assessments(session)
            await seed_skill_progress(session)
            await seed_routine_performance(session)
            await seed_performance_metrics(session)
            await seed_safety_incidents(session)
            await seed_risk_assessments(session)
            
            await session.commit()
            print("Database seeding completed successfully!")
    except Exception as e:
        print(f"Error seeding database: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(seed_database()) 