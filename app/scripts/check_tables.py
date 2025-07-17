from sqlalchemy import text
from app.core.database import async_session
import asyncio

async def check_tables():
    async with async_session() as session:
        result1 = await session.execute(text('SELECT COUNT(*) FROM activity_adaptations'))
        result2 = await session.execute(text('SELECT COUNT(*) FROM adaptation_history'))
        count1 = result1.scalar()
        count2 = result2.scalar()
        print(f'activity_adaptations count: {count1}')
        print(f'adaptation_history count: {count2}')

if __name__ == "__main__":
    asyncio.run(check_tables()) 