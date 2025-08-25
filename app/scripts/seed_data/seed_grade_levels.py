"""
Seed grade levels table with standard K-12 grade levels.

This script populates the grade_levels table with the standard grade levels
that other seeding scripts expect to reference.
"""

from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime

def seed_grade_levels(session: Session) -> None:
    """Seed the grade_levels table with standard K-12 grade levels."""
    print("Seeding grade levels...")
    
    # Check if grade_levels table exists and has data
    try:
        result = session.execute(text("SELECT COUNT(*) FROM grade_levels")).scalar()
        if result > 0:
            print(f"Grade levels table already has {result} records. Skipping seeding.")
            return
    except Exception as e:
        print(f"Error checking grade_levels table: {e}")
        return
    
    # Standard K-12 grade levels
    grade_levels = [
        {"name": "K", "description": "Kindergarten"},
        {"name": "1", "description": "First Grade"},
        {"name": "2", "description": "Second Grade"},
        {"name": "3", "description": "Third Grade"},
        {"name": "4", "description": "Fourth Grade"},
        {"name": "5", "description": "Fifth Grade"},
        {"name": "6", "description": "Sixth Grade"},
        {"name": "7", "description": "Seventh Grade"},
        {"name": "8", "description": "Eighth Grade"},
        {"name": "9", "description": "Ninth Grade"},
        {"name": "10", "description": "Tenth Grade"},
        {"name": "11", "description": "Eleventh Grade"},
        {"name": "12", "description": "Twelfth Grade"}
    ]
    
    # Insert grade levels
    for grade_data in grade_levels:
        try:
            session.execute(
                text("""
                    INSERT INTO grade_levels (name, description, created_at, updated_at)
                    VALUES (:name, :description, :created_at, :updated_at)
                    ON CONFLICT (name) DO NOTHING
                """),
                {
                    "name": grade_data["name"],
                    "description": grade_data["description"],
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            )
        except Exception as e:
            print(f"Error inserting grade level {grade_data['name']}: {e}")
    
    # Commit the changes
    session.commit()
    
    # Verify the seeding
    try:
        result = session.execute(text("SELECT COUNT(*) FROM grade_levels")).scalar()
        print(f"✅ Grade levels seeded successfully: {result} records")
        
        # Show the inserted data
        grades = session.execute(text("SELECT name, description FROM grade_levels ORDER BY name")).fetchall()
        print("Inserted grade levels:")
        for grade in grades:
            print(f"  - {grade[0]}: {grade[1]}")
            
    except Exception as e:
        print(f"Error verifying grade levels: {e}")

if __name__ == "__main__":
    from app.core.database import SessionLocal
    
    session = SessionLocal()
    try:
        seed_grade_levels(session)
    finally:
        session.close() 