from sqlalchemy import text
from app.core.database import async_session
import asyncio

async def check_enums():
    """Check the enum values in the database."""
    async with async_session() as session:
        # Check activity_type enum
        result = await session.execute(text("""
            SELECT enum_range(NULL::activitytype);
        """))
        activity_types = result.scalar()
        print("\nActivity Types:", activity_types)

        # Check difficulty_level enum
        result = await session.execute(text("""
            SELECT enum_range(NULL::difficultylevel);
        """))
        difficulty_levels = result.scalar()
        print("\nDifficulty Levels:", difficulty_levels)

        # Check equipment_requirement enum
        result = await session.execute(text("""
            SELECT enum_range(NULL::equipmentrequirement);
        """))
        equipment_requirements = result.scalar()
        print("\nEquipment Requirements:", equipment_requirements)

if __name__ == "__main__":
    asyncio.run(check_enums()) 