from sqlalchemy import text
from app.core.database import async_session
import asyncio

async def drop_tables():
    async with async_session() as session:
        await session.execute(text('DROP TABLE IF EXISTS adaptation_history CASCADE'))
        await session.execute(text('DROP TABLE IF EXISTS activity_adaptations CASCADE'))
        await session.commit()
        print("Tables dropped successfully!")

if __name__ == "__main__":
    asyncio.run(drop_tables()) 