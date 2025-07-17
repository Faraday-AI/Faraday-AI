from datetime import datetime, timedelta
import random
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select, delete
from app.models.activity import Activity
from app.models.activity_adaptation.categories.activity_categories import ActivityCategory
from app.models.activity_adaptation.categories.associations import ActivityCategoryAssociation
from app.models.physical_education.pe_enums.pe_types import ActivityCategoryType

def seed_activity_categories(session):
    """Seed activity categories and their associations."""
    print("Seeding activity categories...")
    
    # Delete existing records
    session.execute(delete(ActivityCategoryAssociation))
    session.execute(delete(ActivityCategory))
    
    # Define main categories
    categories = [
        {
            "name": "Warm-up",
            "description": "Activities to prepare the body for exercise",
            "subcategories": [
                {"name": "Dynamic Stretching", "description": "Movement-based stretching exercises"},
                {"name": "Light Cardio", "description": "Low-intensity cardiovascular activities"},
                {"name": "Joint Mobility", "description": "Exercises to improve joint range of motion"}
            ]
        },
        {
            "name": "Cardio",
            "description": "Cardiovascular fitness activities",
            "subcategories": [
                {"name": "Running", "description": "Running-based activities"},
                {"name": "Jumping", "description": "Jumping-based exercises"},
                {"name": "High-Intensity", "description": "High-intensity cardio activities"}
            ]
        },
        {
            "name": "Team Sports",
            "description": "Group-based sporting activities",
            "subcategories": [
                {"name": "Basketball", "description": "Basketball-related activities"},
                {"name": "Soccer", "description": "Soccer-related activities"},
                {"name": "Volleyball", "description": "Volleyball-related activities"}
            ]
        },
        {
            "name": "Individual Skills",
            "description": "Personal skill development activities",
            "subcategories": [
                {"name": "Balance", "description": "Balance improvement exercises"},
                {"name": "Coordination", "description": "Coordination development activities"},
                {"name": "Agility", "description": "Agility training exercises"}
            ]
        },
        {
            "name": "Cool-down",
            "description": "Post-exercise recovery activities",
            "subcategories": [
                {"name": "Static Stretching", "description": "Held stretching positions"},
                {"name": "Light Movement", "description": "Gentle cool-down activities"},
                {"name": "Breathing", "description": "Breathing and relaxation exercises"}
            ]
        }
    ]
    
    # Create categories and store them
    category_map = {}
    for cat_data in categories:
        # Create main category
        main_cat = ActivityCategory(
            name=cat_data["name"],
            description=cat_data["description"],
            category_type=ActivityCategoryType.GROUP
        )
        session.add(main_cat)
        session.flush()
        category_map[cat_data["name"]] = main_cat
        
        # Create subcategories
        for sub_data in cat_data["subcategories"]:
            sub_cat = ActivityCategory(
                name=sub_data["name"],
                description=sub_data["description"],
                parent_id=main_cat.id,
                category_type=ActivityCategoryType.INDIVIDUAL
            )
            session.add(sub_cat)
            session.flush()
            category_map[sub_data["name"]] = sub_cat
    
    # Get all activities
    activities = session.execute(select(Activity)).scalars().all()
    
    # Define activity-category mappings
    activity_categories = {
        "Jump Rope Basics": ["Cardio", "Jumping"],
        "Basketball Dribbling": ["Team Sports", "Basketball", "Coordination"],
        "Soccer Passing": ["Team Sports", "Soccer", "Coordination"],
        "Dynamic Warm-up": ["Warm-up", "Dynamic Stretching"],
        "Cool Down Stretches": ["Cool-down", "Static Stretching"],
        "Circuit Training": ["Cardio", "High-Intensity"],
        "Basketball Game": ["Team Sports", "Basketball"],
        "Advanced Jump Rope": ["Cardio", "Jumping", "Coordination"]
    }
    
    # Create associations
    for activity in activities:
        if activity.name in activity_categories:
            categories = activity_categories[activity.name]
            # First category is primary
            for i, cat_name in enumerate(categories):
                if cat_name in category_map:
                    assoc = ActivityCategoryAssociation(
                        activity_id=activity.id,
                        category_id=category_map[cat_name].id,
                        primary_category=(i == 0)
                    )
                    session.add(assoc)
    
    session.flush()
    print("Activity categories and associations seeded successfully!") 