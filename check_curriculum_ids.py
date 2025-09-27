#!/usr/bin/env python3
"""Check curriculum IDs"""

import sys
sys.path.insert(0, '/app')

from sqlalchemy import text
from app.db.session import get_db

def check_curriculum_ids():
    session = next(get_db())
    
    # Check curriculum table
    result = session.execute(text("SELECT id, name FROM curriculum LIMIT 10"))
    print("Existing curriculum records:")
    for row in result:
        print(f"  ID: {row[0]}, Name: {row[1]}")
    
    # Check subjects table
    result = session.execute(text("SELECT id, name FROM subjects LIMIT 10"))
    print("\nExisting subjects records:")
    for row in result:
        print(f"  ID: {row[0]}, Name: {row[1]}")
    
    session.close()

if __name__ == "__main__":
    check_curriculum_ids()
