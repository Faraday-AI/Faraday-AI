from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.physical_education.activity_adaptation.activity_adaptation import AdaptationHistory
from app.models.core.core_models import AdaptationType, AdaptationLevel, AdaptationStatus

async def seed_adaptation_history(session):
    """Seed the adaptation_history table with initial data."""
    adaptation_history = [
        {
            "adaptation_id": 1,  # Jump Rope Intensity Adaptation
            "previous_type": AdaptationType.INTENSITY,
            "previous_level": AdaptationLevel.MINOR,
            "previous_status": AdaptationStatus.PENDING,
            "previous_modifications": {"intensity": "low"},
            "reason": "Student responded well to increased intensity"
        },
        {
            "adaptation_id": 2,  # Jump Rope Technique Adaptation
            "previous_type": AdaptationType.MODIFICATION,
            "previous_level": AdaptationLevel.MODERATE,
            "previous_status": AdaptationStatus.IN_PROGRESS,
            "previous_modifications": {"technique": "basic"},
            "reason": "Student is learning alternating foot pattern"
        },
        {
            "adaptation_id": 3,  # Basketball Dribbling Adaptation
            "previous_type": AdaptationType.DIFFICULTY,
            "previous_level": AdaptationLevel.MAJOR,
            "previous_status": AdaptationStatus.ACTIVE,
            "previous_modifications": {"difficulty": "advanced"},
            "reason": "Student mastered crossover dribble"
        },
        {
            "adaptation_id": 4,  # Soccer Passing Adaptation
            "previous_type": AdaptationType.EQUIPMENT,
            "previous_level": AdaptationLevel.MINOR,
            "previous_status": AdaptationStatus.IN_PROGRESS,
            "previous_modifications": {"equipment": "standard ball"},
            "reason": "Working on long pass technique"
        },
        {
            "adaptation_id": 5,  # Dynamic Warm-up Adaptation
            "previous_type": AdaptationType.DURATION,
            "previous_level": AdaptationLevel.MODERATE,
            "previous_status": AdaptationStatus.ACTIVE,
            "previous_modifications": {"duration": "extended"},
            "reason": "Student progressing well with intermediate exercises"
        }
    ]

    for history_data in adaptation_history:
        history = AdaptationHistory(**history_data)
        session.add(history)

    await session.flush()
    print("Adaptation history seeded successfully!") 