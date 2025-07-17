from app.core.database import get_async_db
import asyncio

async def check_tables():
    async with get_async_db() as db:
        # Check assessment_criteria table
        result = await db.execute(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'assessment_criteria')"
        )
        print(f"assessment_criteria table exists: {result.scalar()}")
        
        # Check other related tables
        tables = ['skill_assessments', 'assessment_results', 'assessment_history', 'skill_progress']
        for table in tables:
            result = await db.execute(
                f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table}')"
            )
            print(f"{table} table exists: {result.scalar()}")

if __name__ == "__main__":
    asyncio.run(check_tables()) 