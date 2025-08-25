#!/usr/bin/env python3

from app.core.database import SessionLocal
from sqlalchemy import text

def check_distribution():
    session = SessionLocal()
    
    try:
        print("=== EXERCISE DISTRIBUTION ===")
        result = session.execute(text('SELECT type, COUNT(*) FROM exercises GROUP BY type ORDER BY COUNT(*) DESC'))
        for row in result:
            print(f"{row[0]}: {row[1]}")
        
        print("\n=== ACTIVITY DISTRIBUTION ===")
        result = session.execute(text('SELECT type, COUNT(*) FROM activities GROUP BY type ORDER BY COUNT(*) DESC'))
        for row in result:
            print(f"{row[0]}: {row[1]}")
            
        print("\n=== ACTIVITY CATEGORY DISTRIBUTION ===")
        result = session.execute(text('SELECT category, COUNT(*) FROM activities GROUP BY category ORDER BY COUNT(*) DESC'))
        for row in result:
            print(f"{row[0]}: {row[1]}")
            
        print("\n=== ACTIVITY FORMAT DISTRIBUTION ===")
        result = session.execute(text('SELECT format, COUNT(*) FROM activities GROUP BY format ORDER BY COUNT(*) DESC'))
        for row in result:
            print(f"{row[0]}: {row[1]}")
            
        print("\n=== ACTIVITY GOAL DISTRIBUTION ===")
        result = session.execute(text('SELECT goal, COUNT(*) FROM activities GROUP BY goal ORDER BY COUNT(*) DESC'))
        for row in result:
            print(f"{row[0]}: {row[1]}")
            
    finally:
        session.close()

if __name__ == "__main__":
    check_distribution() 