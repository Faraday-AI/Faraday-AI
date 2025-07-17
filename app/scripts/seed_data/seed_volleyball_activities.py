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

async def seed_volleyball_activities():
    """Seed volleyball-specific activities."""
    async with async_session() as session:
        # Volleyball Activities
        volleyball_activities = [
            {
                "name": "Volleyball Bumping Basics",
                "description": "Introduction to fundamental volleyball bumping technique",
                "activity_type": ActivityType.SKILL_DEVELOPMENT,
                "difficulty": DifficultyLevel.BEGINNER,
                "equipment_required": EquipmentRequirement.MINIMAL,
                "duration_minutes": 20,
                "instructions": "1. Proper stance and ready position\n2. Hand position for bumping\n3. Contact point practice\n4. Partner bumping drills\n5. Moving and bumping practice",
                "safety_guidelines": "Keep eyes on the ball, maintain proper form to prevent wrist injury",
                "variations": "Can be done with balloon for beginners, adjust height and speed",
                "benefits": "Develops basic volleyball skills, improves hand-eye coordination",
                "categories": ["Team Sports", "Volleyball"]
            },
            {
                "name": "Volleyball Setting Skills",
                "description": "Development of volleyball setting technique",
                "activity_type": ActivityType.SKILL_DEVELOPMENT,
                "difficulty": DifficultyLevel.INTERMEDIATE,
                "equipment_required": EquipmentRequirement.MINIMAL,
                "duration_minutes": 25,
                "instructions": "1. Hand positioning for setting\n2. Overhead pass technique\n3. Setting accuracy drills\n4. Moving and setting practice\n5. Back setting introduction",
                "safety_guidelines": "Maintain proper finger strength, avoid overextension",
                "variations": "Practice against wall, partner drills, group drills",
                "benefits": "Improves ball control, develops finger strength and coordination",
                "categories": ["Team Sports", "Volleyball"]
            },
            {
                "name": "Volleyball Serving Practice",
                "description": "Learning and practicing different volleyball serves",
                "activity_type": ActivityType.SKILL_DEVELOPMENT,
                "difficulty": DifficultyLevel.INTERMEDIATE,
                "equipment_required": EquipmentRequirement.MINIMAL,
                "duration_minutes": 30,
                "instructions": "1. Underhand serve technique\n2. Overhand serve basics\n3. Service line practice\n4. Target serving drills\n5. Service consistency practice",
                "safety_guidelines": "Proper shoulder warm-up, maintain good form",
                "variations": "Short serve, deep serve, different serve types",
                "benefits": "Develops serving accuracy, builds shoulder strength",
                "categories": ["Team Sports", "Volleyball"]
            },
            {
                "name": "Volleyball Spiking Fundamentals",
                "description": "Basic volleyball attacking and spiking skills",
                "activity_type": ActivityType.SKILL_DEVELOPMENT,
                "difficulty": DifficultyLevel.INTERMEDIATE,
                "equipment_required": EquipmentRequirement.MODERATE,
                "duration_minutes": 35,
                "instructions": "1. Approach steps practice\n2. Arm swing technique\n3. Timing drills\n4. Spike approach practice\n5. Target hitting practice",
                "safety_guidelines": "Proper landing technique, shoulder protection",
                "variations": "Different approach angles, tip practice, roll shots",
                "benefits": "Improves attacking skills, develops jumping and timing",
                "categories": ["Team Sports", "Volleyball"]
            },
            {
                "name": "Modified Volleyball Game",
                "description": "Simplified volleyball game format for skill development",
                "activity_type": ActivityType.GAME,
                "difficulty": DifficultyLevel.BEGINNER,
                "equipment_required": EquipmentRequirement.MODERATE,
                "duration_minutes": 30,
                "instructions": "1. Teams of 3-4 players\n2. Modified scoring system\n3. Catch and throw allowed\n4. Three touches required\n5. Rotation practice",
                "safety_guidelines": "Clear communication, maintain court spacing",
                "variations": "Different court sizes, modified rules for beginners",
                "benefits": "Develops game understanding, team cooperation",
                "categories": ["Team Sports", "Volleyball"]
            },
            {
                "name": "Competitive Volleyball Match",
                "description": "Full volleyball game with standard rules",
                "activity_type": ActivityType.GAME,
                "difficulty": DifficultyLevel.ADVANCED,
                "equipment_required": EquipmentRequirement.MODERATE,
                "duration_minutes": 45,
                "instructions": "1. Standard 6v6 format\n2. Official scoring system\n3. Proper rotation rules\n4. Position responsibilities\n5. Game strategy application",
                "safety_guidelines": "Proper warm-up, clear communication, court awareness",
                "variations": "Different scoring systems, specialized positions",
                "benefits": "Applies all volleyball skills, develops team strategy",
                "categories": ["Team Sports", "Volleyball"]
            }
        ]

        # Add activities to the database
        for activity_data in volleyball_activities:
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
        print("Volleyball activities seeded successfully!")

if __name__ == "__main__":
    asyncio.run(seed_volleyball_activities()) 