import os
import sys
from sqlalchemy import inspect, create_engine
from sqlalchemy.orm import sessionmaker

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from app.core.config import settings

def check_schema():
    # Create engine
    engine = create_engine(settings.DATABASE_URL)
    
    # Create inspector
    inspector = inspect(engine)
    
    # Get all tables
    tables = inspector.get_table_names()
    print("Tables in database:", tables)
    
    # Get columns in users table
    if 'users' in tables:
        columns = inspector.get_columns('users')
        print("\nColumns in users table:")
        for column in columns:
            print(f"- {column['name']} ({column['type']})")
    else:
        print("\nUsers table not found in database")

if __name__ == "__main__":
    check_schema() 