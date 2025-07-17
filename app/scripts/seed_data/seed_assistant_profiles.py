"""Seed assistant profiles and capabilities data."""
from datetime import datetime, timedelta
from app.models.core.assistant import AssistantProfile, AssistantCapability
from sqlalchemy.orm import Session

def seed_assistant_profiles(session: Session) -> None:
    """Seed assistant profiles and their capabilities."""
    print("Seeding assistant profiles...")
    try:
        # Create assistant profiles
        profiles = [
            AssistantProfile(
                name="PE Coach",
                description="Physical Education teaching assistant",
                model_version="gpt-4",
                configuration={
                    "specialization": "physical_education",
                    "teaching_style": "encouraging",
                    "focus_areas": ["movement", "fitness", "sports"]
                },
                is_active=True,
                max_context_length=4096,
                temperature=0.7,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0,
                stop_sequences=None,
                assistant_metadata={"created_by": "system", "version": "1.0"}
            ),
            AssistantProfile(
                name="Health Advisor",
                description="Health and wellness assistant",
                model_version="gpt-4",
                configuration={
                    "specialization": "health_education",
                    "teaching_style": "informative",
                    "focus_areas": ["wellness", "nutrition", "safety"]
                },
                is_active=True,
                max_context_length=4096,
                temperature=0.7,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0,
                stop_sequences=None,
                assistant_metadata={"created_by": "system", "version": "1.0"}
            )
        ]
        
        # Add profiles
        session.add_all(profiles)
        session.commit()
        print("Assistant profiles seeded successfully!")
        
        # Create capabilities for each profile
        print("Seeding assistant capabilities...")
        capabilities = []
        
        # Get the created profiles
        db_profiles = session.execute(AssistantProfile.__table__.select()).fetchall()
        
        for profile in db_profiles:
            if profile.name == "PE Coach":
                capabilities.extend([
                    AssistantCapability(
                        name="movement_analysis",
                        description="Analyze and provide feedback on movement patterns",
                        assistant_profile_id=profile.id,
                        parameters={"accuracy_threshold": 0.8, "feedback_detail": "high"},
                        is_enabled=True,
                        priority=1
                    ),
                    AssistantCapability(
                        name="exercise_planning",
                        description="Create and adapt exercise routines",
                        assistant_profile_id=profile.id,
                        parameters={"difficulty_levels": ["beginner", "intermediate", "advanced"]},
                        is_enabled=True,
                        priority=2
                    )
                ])
            elif profile.name == "Health Advisor":
                capabilities.extend([
                    AssistantCapability(
                        name="health_assessment",
                        description="Assess health status and provide recommendations",
                        assistant_profile_id=profile.id,
                        parameters={"assessment_types": ["general", "fitness", "nutrition"]},
                        is_enabled=True,
                        priority=1
                    ),
                    AssistantCapability(
                        name="safety_guidance",
                        description="Provide safety guidelines and precautions",
                        assistant_profile_id=profile.id,
                        parameters={"risk_levels": ["low", "medium", "high"]},
                        is_enabled=True,
                        priority=2
                    )
                ])
        
        # Add capabilities
        session.add_all(capabilities)
        session.commit()
        print("Assistant capabilities seeded successfully!")
        
    except Exception as e:
        print(f"Error seeding assistant profiles and capabilities: {e}")
        session.rollback()
        raise 