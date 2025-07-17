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

async def seed_combination_activities():
    """Seed combination activities that integrate multiple categories."""
    async with async_session() as session:
        # Sport-Specific Conditioning Activities
        sport_conditioning_activities = [
            {
                "name": "Basketball Conditioning Circuit",
                "description": "High-intensity basketball-specific conditioning drills",
                "activity_type": ActivityType.FITNESS_TRAINING,
                "difficulty": DifficultyLevel.ADVANCED,
                "equipment_required": EquipmentRequirement.MODERATE,
                "duration_minutes": 40,
                "instructions": "1. Full-court dribbling sprints\n2. Defensive slide intervals\n3. Shooting conditioning drills\n4. Rebound and sprint series\n5. Game situation cardio",
                "safety_guidelines": "Proper warm-up, hydration breaks, monitor fatigue",
                "variations": "Adjust work/rest ratios, modify drill complexity",
                "benefits": "Sport-specific endurance, skill maintenance under fatigue",
                "categories": ["Team Sports", "Basketball", "High-Intensity", "Cardio"]
            },
            {
                "name": "Volleyball Power Training",
                "description": "Combined power and skill development for volleyball",
                "activity_type": ActivityType.FITNESS_TRAINING,
                "difficulty": DifficultyLevel.ADVANCED,
                "equipment_required": EquipmentRequirement.MODERATE,
                "duration_minutes": 45,
                "instructions": "1. Jump training with ball control\n2. Explosive approach practice\n3. Quick reaction drills\n4. Power hitting circuit\n5. Defensive agility work",
                "safety_guidelines": "Progressive loading, proper technique focus, adequate rest",
                "variations": "Modify jump intensity, adjust skill complexity",
                "benefits": "Volleyball-specific power, skill integration, game endurance",
                "categories": ["Team Sports", "Volleyball", "Jumping", "Agility"]
            }
        ]

        # Skill-Based Circuit Activities
        skill_circuit_activities = [
            {
                "name": "Agility and Balance Circuit",
                "description": "Comprehensive circuit combining agility and balance skills",
                "activity_type": ActivityType.SKILL_DEVELOPMENT,
                "difficulty": DifficultyLevel.INTERMEDIATE,
                "equipment_required": EquipmentRequirement.MODERATE,
                "duration_minutes": 35,
                "instructions": "1. Balance beam with agility tasks\n2. Single-leg stability work\n3. Quick direction changes\n4. Coordination challenges\n5. Reactive balance drills",
                "safety_guidelines": "Proper progression, surface awareness, spotter when needed",
                "variations": "Add cognitive tasks, modify speed, change surfaces",
                "benefits": "Improved proprioception, multi-skill development",
                "categories": ["Individual Skills", "Balance", "Agility", "Coordination"]
            },
            {
                "name": "Cardio Skill Integration",
                "description": "Cardio workout incorporating various skill elements",
                "activity_type": ActivityType.FITNESS_TRAINING,
                "difficulty": DifficultyLevel.INTERMEDIATE,
                "equipment_required": EquipmentRequirement.MINIMAL,
                "duration_minutes": 30,
                "instructions": "1. Agility ladder cardio\n2. Coordination running patterns\n3. Balance challenges with movement\n4. Skill-based intervals\n5. Movement pattern circuits",
                "safety_guidelines": "Maintain form during fatigue, appropriate progression",
                "variations": "Adjust work periods, modify skill complexity",
                "benefits": "Endurance with skill development, movement efficiency",
                "categories": ["Cardio", "Individual Skills", "Coordination", "Agility"]
            }
        ]

        # Recovery Combination Activities
        recovery_activities = [
            {
                "name": "Active Recovery Flow",
                "description": "Combined breathing and movement recovery session",
                "activity_type": ActivityType.COOL_DOWN,
                "difficulty": DifficultyLevel.INTERMEDIATE,
                "equipment_required": EquipmentRequirement.MINIMAL,
                "duration_minutes": 25,
                "instructions": "1. Breathing with gentle movement\n2. Mobility flow with breath focus\n3. Recovery stretching\n4. Mind-body integration\n5. Progressive relaxation",
                "safety_guidelines": "Listen to body, maintain breath awareness, gentle progression",
                "variations": "Modify movement complexity, adjust breath patterns",
                "benefits": "Enhanced recovery, stress reduction, body awareness",
                "categories": ["Cool-down", "Breathing", "Light Movement", "Static Stretching"]
            },
            {
                "name": "Dynamic Recovery Session",
                "description": "Active recovery combining multiple recovery elements",
                "activity_type": ActivityType.COOL_DOWN,
                "difficulty": DifficultyLevel.INTERMEDIATE,
                "equipment_required": EquipmentRequirement.MINIMAL,
                "duration_minutes": 30,
                "instructions": "1. Light cardio with breathing\n2. Joint mobility work\n3. Dynamic flexibility\n4. Balance recovery\n5. Relaxation techniques",
                "safety_guidelines": "Keep intensity low, focus on quality, maintain control",
                "variations": "Adjust movement selection, modify duration, change focus",
                "benefits": "Comprehensive recovery, movement restoration, relaxation",
                "categories": ["Cool-down", "Light Movement", "Joint Mobility", "Dynamic Stretching"]
            }
        ]

        # Add all activities to the database
        for activity_group in [sport_conditioning_activities, skill_circuit_activities, 
                             recovery_activities]:
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
        print("Combination activities seeded successfully!")

if __name__ == "__main__":
    asyncio.run(seed_combination_activities()) 