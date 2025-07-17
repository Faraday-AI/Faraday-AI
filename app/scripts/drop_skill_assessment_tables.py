from sqlalchemy import text
from app.core.database import async_session
import asyncio

async def drop_tables():
    async with async_session() as session:
        # Drop tables in correct order (reverse dependency order)
        await session.execute(text('DROP TABLE IF EXISTS skill_progress CASCADE'))
        print("Dropped skill_progress table")
        await session.execute(text('DROP TABLE IF EXISTS assessment_history CASCADE'))
        print("Dropped assessment_history table")
        await session.execute(text('DROP TABLE IF EXISTS assessment_results CASCADE'))
        print("Dropped assessment_results table")
        await session.execute(text('DROP TABLE IF EXISTS skill_assessments CASCADE'))
        print("Dropped skill_assessments table")
        await session.execute(text('DROP TABLE IF EXISTS assessment_criteria CASCADE'))
        print("Dropped assessment_criteria table")
        await session.commit()
        print("All skill assessment tables dropped successfully!")

if __name__ == "__main__":
    asyncio.run(drop_tables()) 