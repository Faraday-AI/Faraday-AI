from sqlalchemy import create_engine, inspect
import os
from app.core.database import engine
from sqlalchemy import text

# Get database URL from environment
db_url = os.getenv('DATABASE_URL', 'postgresql://faraday_admin:CodaMoeLuna31@faraday-ai-db.postgres.database.azure.com:5432/postgres?sslmode=require')

# Create engine and inspector
engine = create_engine(db_url)
inspector = inspect(engine)

# Check if exercises table exists
if 'exercises' in inspector.get_table_names():
    print('Columns in exercises table:')
    for column in inspector.get_columns('exercises'):
        print(f"- {column['name']}: {column['type']} (nullable: {column['nullable']})")
else:
    print('exercises table does not exist')

# Check alembic version
result = engine.execute("SELECT version_num FROM alembic_version")
print("\nCurrent alembic version:", result.scalar())

def check_table():
    with engine.connect() as conn:
        result = conn.execute(text('SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = \'assessment_criteria\')'))
        print(f"assessment_criteria table exists: {result.scalar()}")
        
        # Check other related tables
        tables = ['skill_assessments', 'assessment_results', 'assessment_history', 'skill_progress']
        for table in tables:
            result = conn.execute(text(f'SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = \'{table}\')'))
            print(f"{table} table exists: {result.scalar()}")

if __name__ == "__main__":
    check_table() 