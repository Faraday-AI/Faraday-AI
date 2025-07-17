import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def check_tables():
    engine = create_async_engine(
        'postgresql+asyncpg://faraday_admin:CodaMoeLuna31@faraday-ai.postgres.database.azure.com:5432/postgres?ssl=require'
    )
    
    async with engine.connect() as conn:
        # Check movement_analysis table
        print("\nMovement Analysis Table:")
        result = await conn.execute(text('SELECT * FROM movement_analysis LIMIT 1'))
        row = result.fetchone()
        print(f"Sample row: {row}")
        
        # Check movement_patterns table
        print("\nMovement Patterns Table:")
        result = await conn.execute(text('SELECT * FROM movement_patterns LIMIT 1'))
        row = result.fetchone()
        print(f"Sample row: {row}")

if __name__ == "__main__":
    asyncio.run(check_tables()) 