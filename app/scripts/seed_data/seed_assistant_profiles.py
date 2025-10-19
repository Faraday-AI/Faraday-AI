"""Seed assistant profiles and capabilities data."""
from datetime import datetime, timedelta
from app.models.core.assistant import AssistantProfile, AssistantCapability
from sqlalchemy.orm import Session
from sqlalchemy import text

def seed_assistant_profiles(session: Session) -> None:
    """Seed assistant profiles and their capabilities."""
    print("Seeding assistant profiles...")
    try:
        # Check for existing profiles
        existing_profiles = session.execute(
            text("SELECT name FROM assistant_profiles WHERE name IN ('PE Coach', 'Health Advisor')")
        ).fetchall()
        existing_names = {row[0] for row in existing_profiles}
        
        profiles_to_create = []
        
        if "PE Coach" not in existing_names:
            profiles_to_create.append(AssistantProfile(
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
            ))
        else:
            print("PE Coach profile already exists, skipping...")
            
        if "Health Advisor" not in existing_names:
            profiles_to_create.append(AssistantProfile(
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
            ))
        else:
            print("Health Advisor profile already exists, skipping...")
        
        # Add profiles only if there are new ones to create
        if profiles_to_create:
            session.add_all(profiles_to_create)
            session.commit()
            print(f"Assistant profiles seeded successfully! Created {len(profiles_to_create)} new profiles.")
        else:
            print("All assistant profiles already exist, skipping creation.")
        
        # Create capabilities for each profile
        print("Seeding assistant capabilities...")
        capabilities_to_create = []
        
        # Get the profiles (both existing and newly created)
        db_profiles = session.execute(AssistantProfile.__table__.select()).fetchall()
        
        for profile in db_profiles:
            if profile.name == "PE Coach":
                # Check for existing capabilities for PE Coach
                existing_caps = session.execute(
                    text("SELECT name FROM assistant_capabilities WHERE assistant_profile_id = :profile_id AND name IN ('movement_analysis', 'exercise_planning')"),
                    {"profile_id": profile.id}
                ).fetchall()
                existing_cap_names = {row[0] for row in existing_caps}
                
                if "movement_analysis" not in existing_cap_names:
                    capabilities_to_create.append(AssistantCapability(
                        name="movement_analysis",
                        description="Analyze and provide feedback on movement patterns",
                        assistant_profile_id=profile.id,
                        parameters={"accuracy_threshold": 0.8, "feedback_detail": "high"},
                        is_enabled=True,
                        priority=1
                    ))
                if "exercise_planning" not in existing_cap_names:
                    capabilities_to_create.append(AssistantCapability(
                        name="exercise_planning",
                        description="Create and adapt exercise routines",
                        assistant_profile_id=profile.id,
                        parameters={"difficulty_levels": ["beginner", "intermediate", "advanced"]},
                        is_enabled=True,
                        priority=2
                    ))
                    
            elif profile.name == "Health Advisor":
                # Check for existing capabilities for Health Advisor
                existing_caps = session.execute(
                    text("SELECT name FROM assistant_capabilities WHERE assistant_profile_id = :profile_id AND name IN ('health_assessment', 'safety_guidance')"),
                    {"profile_id": profile.id}
                ).fetchall()
                existing_cap_names = {row[0] for row in existing_caps}
                
                if "health_assessment" not in existing_cap_names:
                    capabilities_to_create.append(AssistantCapability(
                        name="health_assessment",
                        description="Assess health status and provide recommendations",
                        assistant_profile_id=profile.id,
                        parameters={"assessment_types": ["general", "fitness", "nutrition"]},
                        is_enabled=True,
                        priority=1
                    ))
                if "safety_guidance" not in existing_cap_names:
                    capabilities_to_create.append(AssistantCapability(
                        name="safety_guidance",
                        description="Provide safety guidelines and precautions",
                        assistant_profile_id=profile.id,
                        parameters={"risk_levels": ["low", "medium", "high"]},
                        is_enabled=True,
                        priority=2
                    ))
        
        # Add capabilities only if there are new ones to create
        if capabilities_to_create:
            session.add_all(capabilities_to_create)
            session.commit()
            print(f"Assistant capabilities seeded successfully! Created {len(capabilities_to_create)} new capabilities.")
        else:
            print("All assistant capabilities already exist, skipping creation.")
        
    except Exception as e:
        print(f"Error seeding assistant profiles and capabilities: {e}")
        session.rollback()
        raise 