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

async def seed_additional_activities_1():
    """Seed additional stretching and high-intensity activities."""
    async with async_session() as session:
        # Dynamic Stretching Activities
        dynamic_stretching_activities = [
            {
                "name": "Dynamic Movement Flow",
                "description": "Flowing sequence of dynamic stretches for full-body mobility",
                "activity_type": ActivityType.WARM_UP,
                "difficulty": DifficultyLevel.INTERMEDIATE,
                "equipment_required": EquipmentRequirement.NONE,
                "duration_minutes": 15,
                "instructions": "1. Leg swings (front/back, side/side)\n2. Arm circles and shoulder rolls\n3. Hip circles and rotations\n4. Walking knee pulls\n5. Dynamic lunges with rotation",
                "safety_guidelines": "Keep movements controlled, avoid jerky motions, maintain proper form",
                "variations": "Can be modified for different fitness levels, add resistance bands",
                "benefits": "Improves dynamic flexibility, prepares muscles for activity, enhances movement patterns",
                "categories": ["Warm-up", "Dynamic Stretching"]
            },
            {
                "name": "Sport-Specific Dynamic Preparation",
                "description": "Dynamic stretching routine tailored for sports performance",
                "activity_type": ActivityType.WARM_UP,
                "difficulty": DifficultyLevel.INTERMEDIATE,
                "equipment_required": EquipmentRequirement.NONE,
                "duration_minutes": 20,
                "instructions": "1. High knees and butt kicks\n2. Lateral shuffles with arm swings\n3. Carioca steps\n4. Dynamic leg kicks\n5. Multi-directional lunges",
                "safety_guidelines": "Progress gradually in range of motion, maintain core stability",
                "variations": "Adjust speed and range of motion based on sport requirements",
                "benefits": "Sport-specific mobility, improved coordination, injury prevention",
                "categories": ["Warm-up", "Dynamic Stretching"]
            }
        ]

        # Static Stretching Activities
        static_stretching_activities = [
            {
                "name": "Full-Body Flexibility Routine",
                "description": "Comprehensive static stretching sequence for all major muscle groups",
                "activity_type": ActivityType.COOL_DOWN,
                "difficulty": DifficultyLevel.BEGINNER,
                "equipment_required": EquipmentRequirement.MINIMAL,
                "duration_minutes": 20,
                "instructions": "1. Standing forward fold (hamstrings)\n2. Butterfly stretch (groin)\n3. Figure-4 stretch (glutes)\n4. Cat-cow stretch (spine)\n5. Child's pose (back and shoulders)",
                "safety_guidelines": "Hold stretches 15-30 seconds, avoid bouncing, breathe steadily",
                "variations": "Use props for support, modify positions for comfort",
                "benefits": "Improves flexibility, reduces muscle tension, promotes recovery",
                "categories": ["Cool-down", "Static Stretching"]
            },
            {
                "name": "Advanced Flexibility Training",
                "description": "Advanced static stretching routine for enhanced flexibility",
                "activity_type": ActivityType.COOL_DOWN,
                "difficulty": DifficultyLevel.ADVANCED,
                "equipment_required": EquipmentRequirement.MINIMAL,
                "duration_minutes": 25,
                "instructions": "1. Split stretches\n2. Advanced hip openers\n3. Shoulder and chest stretches\n4. Deep back bends\n5. Advanced twists",
                "safety_guidelines": "Warm up properly, respect current flexibility limits, avoid forcing stretches",
                "variations": "Use blocks or straps for assistance, progress gradually",
                "benefits": "Increases range of motion, improves posture, enhances recovery",
                "categories": ["Cool-down", "Static Stretching"]
            }
        ]

        # High-Intensity Activities
        high_intensity_activities = [
            {
                "name": "HIIT Cardio Blast",
                "description": "High-intensity interval training focusing on cardio exercises",
                "activity_type": ActivityType.FITNESS_TRAINING,
                "difficulty": DifficultyLevel.INTERMEDIATE,
                "equipment_required": EquipmentRequirement.MINIMAL,
                "duration_minutes": 25,
                "instructions": "1. Warm-up (5 min)\n2. 30s high knees / 30s rest\n3. 30s mountain climbers / 30s rest\n4. 30s burpees / 30s rest\n5. 30s jump squats / 30s rest\n6. Repeat 3x",
                "safety_guidelines": "Monitor heart rate, maintain form during fatigue, stay hydrated",
                "variations": "Adjust work/rest ratios, modify exercises for different levels",
                "benefits": "Improves cardiovascular fitness, burns calories, increases endurance",
                "categories": ["Cardio", "High-Intensity"]
            },
            {
                "name": "Tabata Strength Challenge",
                "description": "High-intensity interval training with strength focus",
                "activity_type": ActivityType.FITNESS_TRAINING,
                "difficulty": DifficultyLevel.ADVANCED,
                "equipment_required": EquipmentRequirement.MODERATE,
                "duration_minutes": 30,
                "instructions": "1. Warm-up (5 min)\n2. 20s push-ups / 10s rest\n3. 20s squats / 10s rest\n4. 20s rows / 10s rest\n5. 20s lunges / 10s rest\n6. Repeat 4x",
                "safety_guidelines": "Use appropriate weights, maintain strict form, rest when needed",
                "variations": "Bodyweight options, adjust intensity with weights",
                "benefits": "Builds strength and endurance, improves power output",
                "categories": ["Cardio", "High-Intensity"]
            },
            {
                "name": "Power Endurance Circuit",
                "description": "High-intensity circuit combining power and endurance exercises",
                "activity_type": ActivityType.FITNESS_TRAINING,
                "difficulty": DifficultyLevel.ADVANCED,
                "equipment_required": EquipmentRequirement.MODERATE,
                "duration_minutes": 35,
                "instructions": "1. Box jumps (45s work/15s rest)\n2. Kettlebell swings (45s/15s)\n3. Battle rope waves (45s/15s)\n4. Medicine ball slams (45s/15s)\n5. Rest 1 min, repeat 3x",
                "safety_guidelines": "Proper equipment handling, maintain power output safely",
                "variations": "Scale movements to ability, adjust work periods",
                "benefits": "Develops power endurance, improves work capacity",
                "categories": ["Cardio", "High-Intensity"]
            }
        ]

        # Add all activities to the database
        for activity_group in [dynamic_stretching_activities, static_stretching_activities, high_intensity_activities]:
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
        print("Additional stretching and high-intensity activities seeded successfully!")

if __name__ == "__main__":
    asyncio.run(seed_additional_activities_1()) 