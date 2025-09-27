"""Seed data for activity category associations."""
from datetime import datetime, timedelta
import random
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select, text
from sqlalchemy.orm import Session
from app.models.activity import Activity
from app.models.activity_adaptation.categories.activity_categories import ActivityCategory
from app.models.activity_adaptation.categories.associations import ActivityCategoryAssociation
from app.models.physical_education.pe_enums.pe_types import (
    ActivityType,
    ActivityCategoryType
)

def seed_activity_category_associations(session: Session) -> None:
    """Seed activity category associations data."""
    print("Seeding activity category associations...")
    
    # Note: No need to delete existing data - initial cascade drop cleared everything
    
    # Get all activities and categories
    result = session.execute(select(Activity.id, Activity.name))
    activities = {row.name: row.id for row in result.fetchall()}
    
    result = session.execute(select(ActivityCategory.id, ActivityCategory.name))
    categories = {row.name: row.id for row in result.fetchall()}
    
    if not activities or not categories:
        print("Missing required data. Please seed activities and categories first.")
        return
    
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
    for activity_name, category_names in activity_categories.items():
        if activity_name in activities:
            activity_id = activities[activity_name]
            # First category is primary
            for i, category_name in enumerate(category_names):
                if category_name in categories:
                    assoc = ActivityCategoryAssociation(
                        activity_id=activity_id,
                        category_id=categories[category_name],
                        primary_category=(i == 0)
                    )
                    session.add(assoc)
    
    session.flush()
    print("Activity category associations seeded successfully!") 