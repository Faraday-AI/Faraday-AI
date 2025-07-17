from sqlalchemy import text
from app.core.database import async_session
import asyncio

# Define enum values as they exist in the database
class ActivityType:
    WARM_UP = "WARM_UP"
    SKILL_DEVELOPMENT = "SKILL_DEVELOPMENT"
    FITNESS_TRAINING = "FITNESS_TRAINING"
    GAME = "GAME"
    COOL_DOWN = "COOL_DOWN"

class DifficultyLevel:
    BEGINNER = "BEGINNER"
    INTERMEDIATE = "INTERMEDIATE"
    ADVANCED = "ADVANCED"

class EquipmentRequirement:
    NONE = "NONE"
    MINIMAL = "MINIMAL"
    MODERATE = "MODERATE"
    EXTENSIVE = "EXTENSIVE"

async def seed_additional_activities_3():
    """Seed additional activities for categories with only 2 activities."""
    async with async_session() as session:
        # Basketball Activities
        basketball_activities = [
            {
                "name": "Advanced Basketball Skills",
                "description": "Complex basketball drills combining multiple skills",
                "activity_type": ActivityType.SKILL_DEVELOPMENT,
                "difficulty": DifficultyLevel.ADVANCED,
                "equipment_required": EquipmentRequirement.MINIMAL,
                "duration_minutes": 35,
                "instructions": "1. Advanced ball handling series\n2. Shooting combinations\n3. Drive and kick drills\n4. Pick and roll practice\n5. Fast break scenarios",
                "safety_guidelines": "Maintain court awareness, proper footwear, adequate spacing",
                "variations": "Add defenders, modify speed, create game situations",
                "benefits": "Advanced skill development, decision making, game readiness",
                "categories": ["Team Sports", "Basketball", "Coordination"]
            }
        ]

        # Breathing Activities
        breathing_activities = [
            {
                "name": "Performance Breathing Routine",
                "description": "Advanced breathing techniques for athletic performance",
                "activity_type": ActivityType.COOL_DOWN,
                "difficulty": DifficultyLevel.INTERMEDIATE,
                "equipment_required": EquipmentRequirement.NONE,
                "duration_minutes": 15,
                "instructions": "1. Box breathing technique\n2. Performance breathing patterns\n3. Recovery breathing\n4. Energy management\n5. Focus enhancement",
                "safety_guidelines": "Maintain proper posture, avoid hyperventilation, stay focused",
                "variations": "Adjust breathing ratios, combine with movement, use different positions",
                "benefits": "Enhanced recovery, stress management, performance optimization",
                "categories": ["Cool-down", "Breathing"]
            }
        ]

        # Jumping Activities
        jumping_activities = [
            {
                "name": "Plyometric Jump Training",
                "description": "Advanced jumping exercises for power development",
                "activity_type": ActivityType.FITNESS_TRAINING,
                "difficulty": DifficultyLevel.ADVANCED,
                "equipment_required": EquipmentRequirement.MODERATE,
                "duration_minutes": 25,
                "instructions": "1. Box jumps progression\n2. Depth jumps\n3. Bounding exercises\n4. Reactive jumps\n5. Power development series",
                "safety_guidelines": "Proper landing technique, adequate rest, appropriate surfaces",
                "variations": "Adjust heights, add movements, modify intensity",
                "benefits": "Power development, explosive strength, athletic performance",
                "categories": ["Cardio", "Jumping"]
            }
        ]

        # Light Movement Activities
        light_movement_activities = [
            {
                "name": "Movement Flow Sequence",
                "description": "Flowing sequence of gentle movements for recovery",
                "activity_type": ActivityType.COOL_DOWN,
                "difficulty": DifficultyLevel.INTERMEDIATE,
                "equipment_required": EquipmentRequirement.NONE,
                "duration_minutes": 20,
                "instructions": "1. Joint circles flow\n2. Walking patterns\n3. Gentle mobility sequence\n4. Balance transitions\n5. Coordination patterns",
                "safety_guidelines": "Move within comfort, maintain control, focus on quality",
                "variations": "Modify tempo, add breathing focus, change patterns",
                "benefits": "Active recovery, movement quality, body awareness",
                "categories": ["Cool-down", "Light Movement"]
            }
        ]

        # Running Activities
        running_activities = [
            {
                "name": "Speed Development Drills",
                "description": "Advanced running drills for speed and technique",
                "activity_type": ActivityType.FITNESS_TRAINING,
                "difficulty": DifficultyLevel.ADVANCED,
                "equipment_required": EquipmentRequirement.MINIMAL,
                "duration_minutes": 30,
                "instructions": "1. Sprint technique drills\n2. Acceleration practice\n3. Speed endurance work\n4. Form running\n5. Sprint mechanics",
                "safety_guidelines": "Proper warm-up, technique focus, adequate recovery",
                "variations": "Adjust distances, add resistance, modify rest periods",
                "benefits": "Speed development, running efficiency, athletic performance",
                "categories": ["Cardio", "Running"]
            }
        ]

        # Add all activities to the database
        for activity_group in [basketball_activities, breathing_activities, jumping_activities,
                             light_movement_activities, running_activities]:
            for activity_data in activity_group:
                # Check if activity already exists
                result = await session.execute(
                    text("SELECT id FROM activities WHERE name = :name"),
                    {"name": activity_data["name"]}
                )
                existing = result.scalar()
                
                if not existing:
                    # Create activity
                    result = await session.execute(
                        text("""
                            INSERT INTO activities (
                                name, description, activity_type, difficulty,
                                equipment_required, duration_minutes, instructions,
                                safety_guidelines, variations, benefits,
                                created_at, updated_at
                            ) VALUES (
                                :name, :description, :activity_type, :difficulty,
                                :equipment_required, :duration_minutes, :instructions,
                                :safety_guidelines, :variations, :benefits,
                                NOW(), NOW()
                            ) RETURNING id
                        """),
                        {
                            "name": activity_data["name"],
                            "description": activity_data["description"],
                            "activity_type": activity_data["activity_type"],
                            "difficulty": activity_data["difficulty"],
                            "equipment_required": activity_data["equipment_required"],
                            "duration_minutes": activity_data["duration_minutes"],
                            "instructions": activity_data["instructions"],
                            "safety_guidelines": activity_data["safety_guidelines"],
                            "variations": activity_data["variations"],
                            "benefits": activity_data["benefits"]
                        }
                    )
                    activity_id = str(result.scalar())
                    
                    # Add category associations
                    for category_name in activity_data["categories"]:
                        # Get category ID
                        result = await session.execute(
                            text("SELECT id FROM activity_categories WHERE name = :name"),
                            {"name": category_name}
                        )
                        category_id = str(result.scalar())
                        
                        if category_id:
                            # Create association
                            await session.execute(
                                text("""
                                    INSERT INTO activity_category_associations (
                                        activity_id, category_id, created_at, updated_at
                                    ) VALUES (
                                        :activity_id, :category_id, NOW(), NOW()
                                    )
                                """),
                                {
                                    "activity_id": activity_id,
                                    "category_id": category_id
                                }
                            )
        
        await session.commit()
        print("Additional activities for remaining categories seeded successfully!")

if __name__ == "__main__":
    asyncio.run(seed_additional_activities_3()) 