from datetime import datetime, timedelta
import random
from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.physical_education.activity_adaptation.activity_adaptation import ActivityAdaptation, AdaptationHistory
from app.models.activity import Activity
from app.models.student import Student
from app.models.core.core_models import AdaptationType, AdaptationLevel, AdaptationStatus, AdaptationTrigger

async def seed_activity_adaptations(session: AsyncSession) -> None:
    """Seed activity adaptations data."""
    print("Seeding activity adaptations...")

    # Get all students and activities
    students = (await session.execute(select(Student))).scalars().all()
    activities = (await session.execute(select(Activity))).scalars().all()

    adaptation_types = [AdaptationType.DIFFICULTY, AdaptationType.EQUIPMENT, AdaptationType.DURATION, AdaptationType.INTENSITY, AdaptationType.MODIFICATION]

    # Create sample adaptations for each student-activity pair
    for student in students[:5]:  # Limit to first 5 students for sample data
        for activity in activities[:3]:  # Limit to first 3 activities
            # Create activity adaptation
            adaptation = ActivityAdaptation(
                student_id=student.id,
                activity_id=activity.id,
                adaptation_type=random.choice(adaptation_types),
                adaptation_level=AdaptationLevel.MODERATE,
                status=AdaptationStatus.ACTIVE,
                trigger=AdaptationTrigger.TEACHER_INITIATED,
                description="Sample adaptation for demonstration",
                modifications={
                    'intensity': {
                        'level': 'moderate',
                        'rest_periods': 3,
                        'target_heart_rate': 140
                    },
                    'equipment': 'lighter weights',
                    'movement': 'reduced range of motion',
                    'support': 'moderate assistance'
                }
            )
            session.add(adaptation)
            await session.flush()

            # Create adaptation history entries
            history_entries = [
                AdaptationHistory(
                    adaptation_id=adaptation.id,
                    previous_type=None,
                    previous_level=None,
                    previous_status=None,
                    previous_modifications=None,
                    reason="Initial setup based on student assessment"
                ),
                AdaptationHistory(
                    adaptation_id=adaptation.id,
                    previous_type=AdaptationType.DIFFICULTY,
                    previous_level=AdaptationLevel.MINOR,
                    previous_status=AdaptationStatus.PENDING,
                    previous_modifications={
                        'intensity': {
                            'level': 'low',
                            'rest_periods': 4,
                            'target_heart_rate': 130
                        }
                    },
                    reason="Student showing good progress"
                )
            ]
            for entry in history_entries:
                session.add(entry)

    print("Activity adaptations seeded successfully!") 