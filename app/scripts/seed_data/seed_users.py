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

from app.core.database import SessionLocal
from app.core.config import settings
from app.models.core.user import User
from app.models.mixins.status import BaseStatus

def seed_users(session: Session) -> None:
    """Seed the database with initial user data."""
    print("Seeding users...")
    
    # Sample user data
    users_data = [
        {
            "email": "teacher1@example.com",
            "password_hash": "hashed_password_1",  # In production, use proper password hashing
            "first_name": "John",
            "last_name": "Smith",
            "role": "teacher",
            "is_active": True,
            "user_type": "teacher",
            "preferences": {
                "school": "Springfield High School",
                "department": "Physical Education",
                "subjects": ["Physical Education", "Health"],
                "grade_levels": ["9", "10", "11", "12"]
            }
        },
        {
            "email": "teacher2@example.com",
            "password_hash": "hashed_password_2",
            "first_name": "Sarah",
            "last_name": "Johnson",
            "role": "teacher",
            "is_active": True,
            "user_type": "teacher",
            "preferences": {
                "school": "Springfield High School",
                "department": "Physical Education",
                "subjects": ["Physical Education", "Sports Science"],
                "grade_levels": ["9", "10"]
            }
        },
        {
            "email": "teacher3@example.com",
            "password_hash": "hashed_password_3",
            "first_name": "Michael",
            "last_name": "Brown",
            "role": "teacher",
            "is_active": True,
            "user_type": "teacher",
            "preferences": {
                "school": "Lincoln High School",
                "department": "Physical Education",
                "subjects": ["Physical Education", "Fitness"],
                "grade_levels": ["11", "12"]
            }
        }
    ]
    
    # Create users using SQLAlchemy ORM
    for user_data in users_data:
        # Check if user already exists
        existing_user = session.query(User).filter(User.email == user_data["email"]).first()
        if existing_user:
            print(f"User {user_data['email']} already exists, skipping...")
            continue
            
        # Create user using ORM
        user = User(
            email=user_data["email"],
            password_hash=user_data["password_hash"],
            first_name=user_data["first_name"],
            last_name=user_data["last_name"],
            role=user_data["role"],
            is_active=user_data["is_active"],
            user_type=user_data["user_type"],
            preferences=user_data["preferences"],
            status=BaseStatus.ACTIVE
        )
        
        session.add(user)
    
    session.commit()
    print("Users seeded successfully!")

if __name__ == "__main__":
    seed_users(SessionLocal()) 