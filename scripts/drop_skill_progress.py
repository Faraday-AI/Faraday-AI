from sqlalchemy import create_engine, text
import os

# Get database URL from environment
db_url = os.getenv('DATABASE_URL', 'postgresql://faraday_admin:CodaMoeLuna31@faraday-ai-db.postgres.database.azure.com:5432/postgres?sslmode=require')

# Create engine
engine = create_engine(db_url)

def drop_skill_progress():
    with engine.connect() as conn:
        # Drop constraints first
        conn.execute(text("""
            DO $$ 
            BEGIN
                -- Drop foreign key constraints
                ALTER TABLE IF EXISTS skill_progress 
                DROP CONSTRAINT IF EXISTS skill_progress_student_id_fkey,
                DROP CONSTRAINT IF EXISTS skill_progress_activity_id_fkey;
                
                -- Drop check constraints
                ALTER TABLE IF EXISTS skill_progress 
                DROP CONSTRAINT IF EXISTS valid_skill_level;
            EXCEPTION WHEN OTHERS THEN
                -- If any error occurs, just continue
                NULL;
            END $$;
        """))
        conn.commit()
        
        # Drop the table
        conn.execute(text("DROP TABLE IF EXISTS skill_progress CASCADE;"))
        conn.commit()
        
        print("Successfully dropped skill_progress table and its constraints")

if __name__ == "__main__":
    drop_skill_progress() 