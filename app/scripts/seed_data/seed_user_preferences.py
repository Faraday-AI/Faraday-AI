"""Seed user preferences data."""
from sqlalchemy.orm import Session
from app.dashboard.models.user_preferences import UserPreferences
from app.dashboard.models import DashboardUser as User

def seed_user_preferences(session: Session) -> None:
    """Seed user preferences data."""
    print("Seeding user preferences...")
    try:
        # Get all users
        users = session.execute(User.__table__.select()).fetchall()
        
        # Create preferences for each user
        preferences = []
        for user in users:
            preference = UserPreferences(
                user_id=user.id,
                theme="light",
                notifications={"email": True, "push": True, "in_app": True},
                language="en",
                timezone="America/New_York"
            )
            preferences.append(preference)
        
        # Add all preferences
        session.add_all(preferences)
        session.commit()
        print("User preferences seeded successfully!")
        
    except Exception as e:
        print(f"Error seeding user preferences: {e}")
        session.rollback()
        raise 