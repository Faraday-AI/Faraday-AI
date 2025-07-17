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

async def seed_recovery_activities():
    """Seed recovery and basic fitness activities."""
    async with async_session() as session:
        # Second Priority Activities

        # 1. Breathing Activities (Cool-down)
        breathing_activities = [
            {
                "name": "Deep Breathing Exercise",
                "description": "Focused deep breathing exercises for recovery",
                "activity_type": ActivityType.COOL_DOWN,
                "difficulty": DifficultyLevel.BEGINNER,
                "equipment_required": EquipmentRequirement.NONE,
                "duration_minutes": 5,
                "instructions": "1. Sit or stand comfortably\n2. Inhale slowly through nose (4 counts)\n3. Hold breath (4 counts)\n4. Exhale slowly through mouth (4 counts)\n5. Repeat for duration",
                "safety_guidelines": "Stop if feeling lightheaded, maintain good posture",
                "variations": "Can be done lying down, can adjust breath counts",
                "benefits": "Reduces heart rate, promotes relaxation, improves recovery",
                "categories": ["Cool-down", "Breathing"]
            },
            {
                "name": "Mindful Breathing Flow",
                "description": "Combination of breathing exercises with gentle movement",
                "activity_type": ActivityType.COOL_DOWN,
                "difficulty": DifficultyLevel.BEGINNER,
                "equipment_required": EquipmentRequirement.NONE,
                "duration_minutes": 8,
                "instructions": "1. Start with normal breathing (1 min)\n2. Progress to diaphragmatic breathing\n3. Add arm raises with breath\n4. Practice breath focus\n5. End with relaxation breathing",
                "safety_guidelines": "Keep movements gentle, focus on breath quality",
                "variations": "Can be modified for different positions",
                "benefits": "Enhances mind-body connection, promotes relaxation, improves breathing patterns",
                "categories": ["Cool-down", "Breathing"]
            }
        ]

        # 2. Light Movement Activities (Cool-down)
        light_movement_activities = [
            {
                "name": "Gentle Walking Cool-down",
                "description": "Progressive reduction in activity intensity through walking",
                "activity_type": ActivityType.COOL_DOWN,
                "difficulty": DifficultyLevel.BEGINNER,
                "equipment_required": EquipmentRequirement.NONE,
                "duration_minutes": 10,
                "instructions": "1. Start with normal walking pace\n2. Gradually reduce speed\n3. Add arm swings\n4. Include gentle stretches\n5. End with slow walking",
                "safety_guidelines": "Maintain good posture, stay hydrated",
                "variations": "Can be done in place if space limited",
                "benefits": "Promotes active recovery, prevents blood pooling, reduces muscle soreness",
                "categories": ["Cool-down", "Light Movement"]
            },
            {
                "name": "Recovery Movement Flow",
                "description": "Sequence of gentle movements for cool-down",
                "activity_type": ActivityType.COOL_DOWN,
                "difficulty": DifficultyLevel.BEGINNER,
                "equipment_required": EquipmentRequirement.NONE,
                "duration_minutes": 12,
                "instructions": "1. Gentle arm circles\n2. Hip circles\n3. Knee lifts\n4. Ankle rotations\n5. Shoulder rolls\n6. Light twisting",
                "safety_guidelines": "Keep movements controlled and gentle",
                "variations": "Can be done seated for lower intensity",
                "benefits": "Improves circulation, reduces muscle tension, promotes recovery",
                "categories": ["Cool-down", "Light Movement"]
            }
        ]

        # 3. Running Activities
        running_activities = [
            {
                "name": "Basic Running Form",
                "description": "Introduction to proper running technique",
                "activity_type": ActivityType.SKILL_DEVELOPMENT,
                "difficulty": DifficultyLevel.BEGINNER,
                "equipment_required": EquipmentRequirement.MINIMAL,
                "duration_minutes": 20,
                "instructions": "1. Posture check\n2. Arm movement practice\n3. Foot strike drills\n4. Walking to running transitions\n5. Form maintenance practice",
                "safety_guidelines": "Start slow, focus on form over speed",
                "variations": "Can be done in place or moving",
                "benefits": "Develops proper running technique, improves efficiency, reduces injury risk",
                "categories": ["Cardio", "Running"]
            },
            {
                "name": "Progressive Running Intervals",
                "description": "Structured intervals for running development",
                "activity_type": ActivityType.FITNESS_TRAINING,
                "difficulty": DifficultyLevel.INTERMEDIATE,
                "equipment_required": EquipmentRequirement.MINIMAL,
                "duration_minutes": 25,
                "instructions": "1. Warm-up walk/jog (5 min)\n2. Run 1 min, walk 2 min x3\n3. Run 2 min, walk 1 min x3\n4. Cool-down walk (5 min)",
                "safety_guidelines": "Maintain consistent pace, stay hydrated",
                "variations": "Adjust intervals based on fitness level",
                "benefits": "Builds running endurance, improves cardiovascular fitness",
                "categories": ["Cardio", "Running"]
            }
        ]

        # Add all activities to the database
        for activity_group in [breathing_activities, light_movement_activities, running_activities]:
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
        print("Recovery and basic fitness activities seeded successfully!")

if __name__ == "__main__":
    asyncio.run(seed_recovery_activities()) 