from .seed_database import seed_database
from app.core.database import async_session
from app.scripts.seed_data.seed_activities import seed_activities
from app.scripts.seed_data.seed_students import seed_students
from app.scripts.seed_data.seed_classes import seed_classes
from app.scripts.seed_data.seed_routines import seed_routines
from app.scripts.seed_data.seed_exercises import seed_exercises
from app.scripts.seed_data.seed_safety_checks import seed_safety_checks
from app.scripts.seed_data.seed_movement_analysis import seed_movement_analysis
from app.scripts.seed_data.seed_activity_adaptations import seed_activity_adaptations
from app.scripts.seed_data.seed_user_preferences import seed_user_preferences
from app.scripts.seed_data.seed_assistant_profiles import seed_assistant_profiles
from app.scripts.seed_data.seed_memories import seed_memories

if __name__ == "__main__":
    import asyncio
    asyncio.run(seed_database())

async def main():
    """Main function to seed all data."""
    async with async_session() as session:
        try:
            # First seed base data
            await seed_activities(session)
            await seed_students(session)
            await seed_classes(session)
            await seed_routines(session)
            await seed_exercises(session)
            await seed_safety_checks(session)
            await seed_movement_analysis(session)
            await seed_activity_adaptations(session)
            
            # Then seed user-related data
            await seed_user_preferences(session)
            await seed_assistant_profiles(session)
            await seed_memories(session)
            
            await session.commit()
            print("All data seeded successfully!")
        except Exception as e:
            await session.rollback()
            print(f"Error seeding data: {e}")
            raise 