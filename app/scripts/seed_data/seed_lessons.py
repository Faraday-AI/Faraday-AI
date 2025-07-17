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
from app.services.education.models.lesson import Lesson
from app.models.core.subject import SubjectCategory
from app.dashboard.models import DashboardUser as User

def seed_lessons(session: Session) -> None:
    """Seed the database with initial lesson data."""
    print("Seeding lessons...")
    
    # Get existing users and subject categories
    users = session.execute(text("SELECT id FROM users WHERE is_teacher = true"))
    user_ids = [user[0] for user in users.fetchall()]
    
    subject_categories = session.execute(text("SELECT id FROM subject_categories"))
    subject_category_ids = [category[0] for category in subject_categories.fetchall()]
    
    if not user_ids or not subject_category_ids:
        print("Warning: No teachers or subject categories found. Skipping lesson seeding.")
        return
    
    # Sample lesson data
    lessons_data = [
        {
            "title": "Introduction to Physical Education",
            "content": "Basic principles and importance of physical education",
            "grade_level": "9",
            "week_number": 1,
            "content_area": "Physical Education",
            "lesson_data": {
                "objectives": ["Understand basic PE principles", "Learn safety guidelines"],
                "materials": ["Cones", "Balls", "Whistle"],
                "activities": ["Warm-up exercises", "Basic movement patterns"],
                "assessment": "Observation and participation"
            },
            "status": "published",
            "version": 1
        },
        {
            "title": "Team Sports Fundamentals",
            "content": "Introduction to team sports and cooperation",
            "grade_level": "10",
            "week_number": 2,
            "content_area": "Team Sports",
            "lesson_data": {
                "objectives": ["Learn team sports basics", "Develop cooperation skills"],
                "materials": ["Soccer balls", "Basketballs", "Nets"],
                "activities": ["Passing drills", "Team coordination exercises"],
                "assessment": "Skill demonstration and teamwork evaluation"
            },
            "status": "published",
            "version": 1
        },
        {
            "title": "Fitness and Wellness",
            "content": "Understanding fitness components and wellness",
            "grade_level": "11",
            "week_number": 3,
            "content_area": "Health and Fitness",
            "lesson_data": {
                "objectives": ["Understand fitness components", "Learn wellness principles"],
                "materials": ["Heart rate monitors", "Fitness trackers"],
                "activities": ["Cardio exercises", "Strength training basics"],
                "assessment": "Fitness testing and wellness journal"
            },
            "status": "draft",
            "version": 1
        }
    ]
    
    # Create lessons
    for lesson_data in lessons_data:
        # Randomly assign user and subject category
        import random
        user_id = random.choice(user_ids)
        subject_category_id = random.choice(subject_category_ids)
        
        lesson = Lesson(
            user_id=user_id,
            subject_category_id=subject_category_id,
            **lesson_data
        )
        session.add(lesson)
    
    session.commit()
    print("Lessons seeded successfully!")

if __name__ == "__main__":
    session = next(get_db())
    seed_lessons(session) 