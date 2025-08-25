"""Seed user preferences data."""
from sqlalchemy.orm import Session
from app.dashboard.models.user_preferences import UserPreferences
from app.models.core.user import User

def seed_user_preferences(session: Session) -> None:
    """Seed user preferences data."""
    print("Seeding user preferences...")
    try:
        # Get all users from the core users table
        from sqlalchemy import text
        users = session.execute(text("SELECT id FROM users")).fetchall()
        
        if not users:
            print("No users found, skipping user preferences creation")
            return
        
        print(f"Found {len(users)} users, creating preferences...")
        
        # Create preferences for each user
        preferences = []
        for user in users:
            preference = UserPreferences(
                user_id=user.id,
                theme="light",
                email_notifications=True,
                push_notifications=True,
                in_app_notifications=True,
                language="en",
                timezone="America/New_York"
            )
            preferences.append(preference)
        
        # Add all preferences
        session.add_all(preferences)
        session.commit()
        print(f"User preferences seeded successfully! Created {len(preferences)} preferences")
        
    except Exception as e:
        print(f"Error seeding user preferences: {e}")
        session.rollback()
        raise 