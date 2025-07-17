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

async def seed_priority_activities():
    """Seed high-priority activities for fundamental categories."""
    async with async_session() as session:
        # First Priority Activities

        # 1. Joint Mobility Activities (Warm-up)
        joint_mobility_activities = [
            {
                "name": "Joint Circles Warm-up",
                "description": "Systematic warm-up of all major joints through circular movements",
                "activity_type": ActivityType.WARM_UP,
                "difficulty": DifficultyLevel.BEGINNER,
                "equipment_required": EquipmentRequirement.NONE,
                "duration_minutes": 10,
                "instructions": "1. Start with neck circles\n2. Move to shoulder circles\n3. Progress to wrist circles\n4. Hip circles\n5. Knee circles\n6. Ankle circles",
                "safety_guidelines": "Move slowly and controlled, avoid jerky movements",
                "variations": "Can be done seated for modified version",
                "benefits": "Improves joint mobility, prevents injury, prepares body for exercise",
                "categories": ["Warm-up", "Joint Mobility"]
            },
            {
                "name": "Dynamic Joint Mobility Flow",
                "description": "Flowing sequence of joint mobility exercises",
                "activity_type": ActivityType.WARM_UP,
                "difficulty": DifficultyLevel.INTERMEDIATE,
                "equipment_required": EquipmentRequirement.NONE,
                "duration_minutes": 15,
                "instructions": "1. Arm circles forward and back\n2. Leg swings front and side\n3. Hip openers\n4. Thoracic rotations\n5. Ankle mobility work",
                "safety_guidelines": "Maintain control throughout movements, stay within comfortable range",
                "variations": "Can be modified for different fitness levels",
                "benefits": "Enhanced joint mobility, improved movement patterns, injury prevention",
                "categories": ["Warm-up", "Joint Mobility"]
            }
        ]

        # 2. Light Cardio Activities (Warm-up)
        light_cardio_activities = [
            {
                "name": "Walking Warm-up Circuit",
                "description": "Progressive walking-based warm-up routine",
                "activity_type": ActivityType.WARM_UP,
                "difficulty": DifficultyLevel.BEGINNER,
                "equipment_required": EquipmentRequirement.MINIMAL,
                "duration_minutes": 10,
                "instructions": "1. Regular walking (2 min)\n2. High knee walking (2 min)\n3. Heel-to-toe walking (2 min)\n4. Side stepping (2 min)\n5. Light jogging (2 min)",
                "safety_guidelines": "Start slow and increase intensity gradually",
                "variations": "Can be done indoors or outdoors",
                "benefits": "Gradually increases heart rate, warms up muscles, improves circulation",
                "categories": ["Warm-up", "Light Cardio"]
            },
            {
                "name": "Light Jogging Patterns",
                "description": "Various light jogging patterns and movements",
                "activity_type": ActivityType.WARM_UP,
                "difficulty": DifficultyLevel.BEGINNER,
                "equipment_required": EquipmentRequirement.MINIMAL,
                "duration_minutes": 12,
                "instructions": "1. Forward jogging\n2. Backward jogging\n3. Side shuffling\n4. Diagonal jogging\n5. Figure-8 patterns",
                "safety_guidelines": "Maintain proper form, stay at conversational pace",
                "variations": "Can be done with or without directional cues",
                "benefits": "Improves coordination, raises heart rate gradually, prepares for more intense activity",
                "categories": ["Warm-up", "Light Cardio"]
            }
        ]

        # 3. Agility Activities
        agility_activities = [
            {
                "name": "Agility Ladder Fundamentals",
                "description": "Basic agility ladder drills for footwork and coordination",
                "activity_type": ActivityType.SKILL_DEVELOPMENT,
                "difficulty": DifficultyLevel.BEGINNER,
                "equipment_required": EquipmentRequirement.MINIMAL,
                "duration_minutes": 15,
                "instructions": "1. Single step through\n2. Double step through\n3. In-and-out steps\n4. Lateral steps\n5. High knees through ladder",
                "safety_guidelines": "Focus on precision before speed, maintain good posture",
                "variations": "Can be done with or without actual ladder using floor markers",
                "benefits": "Improves footwork, coordination, and agility",
                "categories": ["Individual Skills", "Agility"]
            },
            {
                "name": "Cone Weaving Patterns",
                "description": "Various cone weaving drills for agility development",
                "activity_type": ActivityType.SKILL_DEVELOPMENT,
                "difficulty": DifficultyLevel.BEGINNER,
                "equipment_required": EquipmentRequirement.MINIMAL,
                "duration_minutes": 20,
                "instructions": "1. Forward weaving\n2. Backward weaving\n3. Side shuffle weaving\n4. Sprint-backpedal combination\n5. Figure-8 patterns",
                "safety_guidelines": "Start slow and focus on form before increasing speed",
                "variations": "Adjust cone spacing and patterns for different challenges",
                "benefits": "Develops change of direction skills, spatial awareness, and coordination",
                "categories": ["Individual Skills", "Agility"]
            }
        ]

        # 4. Balance Activities
        balance_activities = [
            {
                "name": "Static Balance Progressions",
                "description": "Progressive static balance exercises",
                "activity_type": ActivityType.SKILL_DEVELOPMENT,
                "difficulty": DifficultyLevel.BEGINNER,
                "equipment_required": EquipmentRequirement.NONE,
                "duration_minutes": 15,
                "instructions": "1. Two-foot balance\n2. One-foot balance\n3. One-foot balance with arm movements\n4. One-foot balance with eyes closed\n5. One-foot balance on unstable surface",
                "safety_guidelines": "Have support nearby if needed, progress gradually",
                "variations": "Can be modified for different skill levels",
                "benefits": "Improves balance, stability, and body awareness",
                "categories": ["Individual Skills", "Balance"]
            },
            {
                "name": "Dynamic Balance Challenges",
                "description": "Moving balance exercises and challenges",
                "activity_type": ActivityType.SKILL_DEVELOPMENT,
                "difficulty": DifficultyLevel.INTERMEDIATE,
                "equipment_required": EquipmentRequirement.MINIMAL,
                "duration_minutes": 20,
                "instructions": "1. Walking heel-to-toe\n2. Walking on imaginary line\n3. Walking with knee raises\n4. Lateral stepping with balance holds\n5. Walking with arm patterns",
                "safety_guidelines": "Ensure clear space, have support nearby if needed",
                "variations": "Add cognitive tasks for additional challenge",
                "benefits": "Enhances dynamic balance, coordination, and movement control",
                "categories": ["Individual Skills", "Balance"]
            }
        ]

        # Add all activities to the database
        for activity_group in [joint_mobility_activities, light_cardio_activities, agility_activities, balance_activities]:
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
        print("Priority activities seeded successfully!")

if __name__ == "__main__":
    asyncio.run(seed_priority_activities()) 