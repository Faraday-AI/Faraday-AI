import os
import sys
from datetime import datetime
from typing import List, Dict, Any
import json
from sqlalchemy.orm import Session
from pathlib import Path
from sqlalchemy import text

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.core.database import get_db
from app.core.config import settings
from app.models.core.subject import SubjectCategory

def seed_subject_categories(session: Session) -> None:
    """Seed the database with initial subject category data."""
    print("Seeding subject categories...")
    
    # Sample subject category data with hierarchical structure
    categories_data = [
        {
            "name": "Physical Education",
            "description": "Core physical education curriculum",
            "level": 1,
            "path": "1",
            "category_data": {
                "color": "#4CAF50",
                "icon": "sports_soccer"
            }
        },
        {
            "name": "Team Sports",
            "description": "Team-based sports and activities",
            "level": 2,
            "path": "1.1",
            "category_data": {
                "color": "#2196F3",
                "icon": "groups"
            }
        },
        {
            "name": "Individual Sports",
            "description": "Individual sports and activities",
            "level": 2,
            "path": "1.2",
            "category_data": {
                "color": "#FF9800",
                "icon": "person"
            }
        },
        {
            "name": "Fitness",
            "description": "Physical fitness and wellness",
            "level": 2,
            "path": "1.3",
            "category_data": {
                "color": "#F44336",
                "icon": "fitness_center"
            }
        },
        {
            "name": "Health Education",
            "description": "Health and wellness education",
            "level": 1,
            "path": "2",
            "category_data": {
                "color": "#9C27B0",
                "icon": "health_and_safety"
            }
        }
    ]
    
    # Create categories
    for category_data in categories_data:
        # Check if category already exists
        existing_category = session.execute(
            text("SELECT id FROM subject_categories WHERE name = :name"),
            {"name": category_data["name"]}
        )
        if existing_category.scalar():
            print(f"Category {category_data['name']} already exists, skipping...")
            continue
            
        category = SubjectCategory(**category_data)
        session.add(category)
    
    session.commit()
    print("Subject categories seeded successfully!")

if __name__ == "__main__":
    session = next(get_db())
    seed_subject_categories(session) 