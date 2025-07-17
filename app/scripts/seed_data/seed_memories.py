"""Seed user memories and memory interactions data."""
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.core.memory import UserMemory, MemoryInteraction
from app.models.core.user import User
from app.models.core.assistant import AssistantProfile
from datetime import datetime, timedelta

async def seed_memories(session: AsyncSession) -> None:
    """Seed user memories and their interactions."""
    print("Seeding user memories...")
    try:
        # Get users and assistant profiles
        users = (await session.execute(User.__table__.select())).fetchall()
        profiles = (await session.execute(AssistantProfile.__table__.select())).fetchall()
        
        if not users or not profiles:
            print("No users or assistant profiles found. Skipping memory seeding.")
            return
        
        # Create memories for each user
        memories = []
        for user in users:
            for profile in profiles:
                # Create a memory for PE-related content
                if profile.name == "PE Coach":
                    memory = UserMemory(
                        user_id=user.id,
                        assistant_profile_id=profile.id,
                        content="Student shows strong interest in basketball and team sports",
                        context={
                            "activity_type": "team_sports",
                            "skill_level": "intermediate",
                            "preferred_activities": ["basketball", "soccer"]
                        },
                        importance=0.8,
                        last_accessed=datetime.utcnow(),
                        category="preferences",
                        tags=["sports", "basketball", "team_activities"],
                        source="activity_history",
                        confidence=0.9,
                        version="1.0"
                    )
                    memories.append(memory)
                
                # Create a memory for health-related content
                elif profile.name == "Health Advisor":
                    memory = UserMemory(
                        user_id=user.id,
                        assistant_profile_id=profile.id,
                        content="Student maintains regular exercise routine with focus on cardio",
                        context={
                            "exercise_type": "cardio",
                            "frequency": "3x_week",
                            "duration": "30_minutes"
                        },
                        importance=0.7,
                        last_accessed=datetime.utcnow(),
                        category="health_habits",
                        tags=["exercise", "cardio", "routine"],
                        source="health_tracking",
                        confidence=0.85,
                        version="1.0"
                    )
                    memories.append(memory)
        
        # Add memories
        session.add_all(memories)
        await session.commit()
        print("User memories seeded successfully!")
        
        # Create memory interactions
        print("Seeding memory interactions...")
        interactions = []
        
        # Get the created memories
        db_memories = (await session.execute(UserMemory.__table__.select())).fetchall()
        
        for memory in db_memories:
            # Create a read interaction
            read_interaction = MemoryInteraction(
                memory_id=memory.id,
                user_id=memory.user_id,
                interaction_type="read",
                timestamp=datetime.utcnow() - timedelta(days=1),
                context={"action": "lesson_planning"},
                feedback={"relevance": 0.9}
            )
            interactions.append(read_interaction)
            
            # Create an update interaction
            update_interaction = MemoryInteraction(
                memory_id=memory.id,
                user_id=memory.user_id,
                interaction_type="update",
                timestamp=datetime.utcnow(),
                context={"action": "performance_tracking"},
                feedback={"accuracy": 0.95}
            )
            interactions.append(update_interaction)
        
        # Add interactions
        session.add_all(interactions)
        await session.commit()
        print("Memory interactions seeded successfully!")
        
    except Exception as e:
        print(f"Error seeding memories and interactions: {e}")
        await session.rollback()
        raise 