from app.core.database import async_session
import asyncio
from sqlalchemy import text

async def check_table_schema():
    async with async_session() as session:
        result = await session.execute(text("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'movement_analysis'
            ORDER BY ordinal_position;
        """))
        print('Columns in movement_analysis table:')
        for row in result:
            print(f"Column: {row[0]}, Type: {row[1]}, Nullable: {row[2]}")

if __name__ == '__main__':
    asyncio.run(check_table_schema()) 