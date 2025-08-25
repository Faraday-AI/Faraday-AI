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
    users = session.execute(text("SELECT id FROM users WHERE role = 'teacher'"))
    user_ids = [user[0] for user in users.fetchall()]
    
    subject_categories = session.execute(text("SELECT id FROM subject_categories"))
    subject_category_ids = [category[0] for category in subject_categories.fetchall()]
    
    if not user_ids or not subject_category_ids:
        print("Warning: No teachers or subject categories found. Skipping lesson seeding.")
        return
    
    # Comprehensive lesson data aligned with our 6-school district structure
    lessons_data = []
    
    # Elementary School Lessons (K-5) - Fundamental Movement Skills
    elementary_lessons = [
        {
            "title": "Kindergarten Movement Basics",
            "content": "Introduction to fundamental movement patterns for young learners",
            "grade_level": "K",
            "week_of": datetime(2024, 1, 8),
            "content_area": "Fundamental Movement",
            "objectives": ["Develop basic locomotor skills", "Learn spatial awareness", "Practice following directions"],
            "materials": ["Cones", "Bean bags", "Music player"],
            "activities": ["Walking, running, jumping games", "Animal movement imitation", "Follow the leader"],
            "assessment_criteria": "Observation of participation and basic skill demonstration",
            "status": "published",
            "version": 1
        },
        {
            "title": "Grade 1-2 Team Building",
            "content": "Cooperative games and basic team sports introduction",
            "grade_level": "1-2",
            "week_of": datetime(2024, 1, 15),
            "content_area": "Team Sports",
            "objectives": ["Learn cooperation skills", "Practice basic throwing/catching", "Understand fair play"],
            "materials": ["Soft balls", "Hula hoops", "Cones"],
            "activities": ["Partner toss games", "Hula hoop challenges", "Simple relay races"],
            "assessment_criteria": "Participation, cooperation, and basic skill demonstration",
            "status": "published",
            "version": 1
        },
        {
            "title": "Grade 3-5 Sports Fundamentals",
            "content": "Introduction to organized sports and fitness activities",
            "grade_level": "3-5",
            "week_of": datetime(2024, 1, 22),
            "content_area": "Sports Skills",
            "objectives": ["Master basic sports skills", "Learn game rules", "Develop fitness habits"],
            "materials": ["Basketballs", "Soccer balls", "Jump ropes", "Stopwatch"],
            "activities": ["Basketball dribbling", "Soccer passing", "Jump rope challenges", "Fitness stations"],
            "assessment_criteria": "Skill demonstration, game participation, and fitness improvement",
            "status": "published",
            "version": 1
        }
    ]
    
    # Middle School Lessons (6-8) - Advanced Skills and Fitness
    middle_school_lessons = [
        {
            "title": "Grade 6-8 Advanced Sports Skills",
            "content": "Intermediate level sports training and fitness development",
            "grade_level": "6-8",
            "week_of": datetime(2024, 2, 5),
            "content_area": "Advanced Sports",
            "objectives": ["Refine sports techniques", "Build endurance", "Learn strategy"],
            "materials": ["Sports equipment", "Fitness trackers", "Video analysis tools"],
            "activities": ["Skill drills", "Scrimmage games", "Fitness testing", "Strategy sessions"],
            "assessment_criteria": "Skill improvement, game performance, and fitness metrics",
            "status": "published",
            "version": 1
        },
        {
            "title": "Middle School Fitness Program",
            "content": "Comprehensive fitness training for adolescent development",
            "grade_level": "6-8",
            "week_of": datetime(2024, 2, 12),
            "content_area": "Fitness Training",
            "objectives": ["Improve cardiovascular fitness", "Build strength", "Enhance flexibility"],
            "materials": ["Resistance bands", "Medicine balls", "Fitness equipment"],
            "activities": ["Circuit training", "Strength exercises", "Flexibility work", "Cardio intervals"],
            "assessment_criteria": "Fitness test results, strength gains, and endurance improvement",
            "status": "published",
            "version": 1
        }
    ]
    
    # High School Lessons (9-12) - Specialized Training and Leadership
    high_school_lessons = [
        {
            "title": "High School Sports Specialization",
            "content": "Advanced training in specific sports and leadership development",
            "grade_level": "9-12",
            "week_of": datetime(2024, 3, 1),
            "content_area": "Sports Specialization",
            "objectives": ["Master advanced techniques", "Develop leadership skills", "Prepare for competition"],
            "materials": ["Advanced equipment", "Performance analysis tools", "Training facilities"],
            "activities": ["Advanced skill work", "Tactical training", "Leadership exercises", "Competition prep"],
            "assessment_criteria": "Performance metrics, leadership demonstration, and competitive readiness",
            "status": "published",
            "version": 1
        },
        {
            "title": "High School Fitness and Wellness",
            "content": "Comprehensive fitness programming and health education",
            "grade_level": "9-12",
            "week_of": datetime(2024, 3, 8),
            "content_area": "Health and Fitness",
            "objectives": ["Achieve fitness goals", "Learn health principles", "Develop lifelong habits"],
            "materials": ["Fitness equipment", "Health resources", "Assessment tools"],
            "activities": ["Personalized training", "Health education", "Goal setting", "Progress tracking"],
            "assessment_criteria": "Goal achievement, health knowledge, and habit formation",
            "status": "published",
            "version": 1
        }
    ]
    
    # Combine all lessons
    lessons_data = elementary_lessons + middle_school_lessons + high_school_lessons
    
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