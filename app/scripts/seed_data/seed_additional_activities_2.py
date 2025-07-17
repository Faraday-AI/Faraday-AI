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

async def seed_additional_activities_2():
    """Seed additional activities focusing on soccer and underrepresented categories."""
    async with async_session() as session:
        # Soccer Activities
        soccer_activities = [
            {
                "name": "Soccer Dribbling Skills",
                "description": "Progressive drills to develop soccer ball control and dribbling",
                "activity_type": ActivityType.SKILL_DEVELOPMENT,
                "difficulty": DifficultyLevel.INTERMEDIATE,
                "equipment_required": EquipmentRequirement.MINIMAL,
                "duration_minutes": 25,
                "instructions": "1. Cone weaving dribbling\n2. Figure-8 dribbling\n3. Speed dribbling\n4. Close control practice\n5. Direction change drills",
                "safety_guidelines": "Maintain proper spacing, watch for obstacles, use appropriate ball pressure",
                "variations": "Adjust cone spacing, vary speed, add defensive pressure",
                "benefits": "Improves ball control, footwork, and coordination",
                "categories": ["Team Sports", "Soccer", "Coordination"]
            },
            {
                "name": "Soccer Shooting Practice",
                "description": "Focused practice on different types of soccer shots",
                "activity_type": ActivityType.SKILL_DEVELOPMENT,
                "difficulty": DifficultyLevel.INTERMEDIATE,
                "equipment_required": EquipmentRequirement.MODERATE,
                "duration_minutes": 30,
                "instructions": "1. Basic shot technique\n2. Power shots\n3. Placement shots\n4. Volleys\n5. Shot scenarios",
                "safety_guidelines": "Proper shooting technique, clear shooting area, rotate positions",
                "variations": "Vary distance, add goalkeeper, moving shots",
                "benefits": "Develops shooting accuracy, power, and decision-making",
                "categories": ["Team Sports", "Soccer"]
            },
            {
                "name": "Small-Sided Soccer Game",
                "description": "Modified soccer game with fewer players and smaller field",
                "activity_type": ActivityType.GAME,
                "difficulty": DifficultyLevel.INTERMEDIATE,
                "equipment_required": EquipmentRequirement.MINIMAL,
                "duration_minutes": 25,
                "instructions": "1. 3v3 or 4v4 format\n2. Small field setup\n3. Modified rules\n4. Continuous play\n5. Quick restarts",
                "safety_guidelines": "Clear boundaries, fair play rules, appropriate contact",
                "variations": "Adjust team size, field size, scoring rules",
                "benefits": "Game awareness, teamwork, quick decision-making",
                "categories": ["Team Sports", "Soccer"]
            }
        ]

        # Additional Balance Activities
        balance_activities = [
            {
                "name": "Advanced Balance Course",
                "description": "Challenging balance course with multiple elements",
                "activity_type": ActivityType.SKILL_DEVELOPMENT,
                "difficulty": DifficultyLevel.ADVANCED,
                "equipment_required": EquipmentRequirement.MODERATE,
                "duration_minutes": 25,
                "instructions": "1. Single-leg balance sequence\n2. Balance beam exercises\n3. Unstable surface challenges\n4. Dynamic balance moves\n5. Partner balance activities",
                "safety_guidelines": "Use spotters when needed, proper equipment setup, progressive difficulty",
                "variations": "Add movement patterns, eyes closed variations, time challenges",
                "benefits": "Advanced balance control, proprioception, core strength",
                "categories": ["Individual Skills", "Balance"]
            }
        ]

        # Additional Agility Activities
        agility_activities = [
            {
                "name": "Advanced Agility Circuit",
                "description": "Complex agility drills combining multiple movement patterns",
                "activity_type": ActivityType.FITNESS_TRAINING,
                "difficulty": DifficultyLevel.ADVANCED,
                "equipment_required": EquipmentRequirement.MODERATE,
                "duration_minutes": 30,
                "instructions": "1. Multi-directional sprints\n2. Reactive agility drills\n3. Complex cone patterns\n4. Speed ladder combinations\n5. Agility game scenarios",
                "safety_guidelines": "Proper warm-up, clear pathways, adequate rest periods",
                "variations": "Add balls/equipment, time challenges, competitive elements",
                "benefits": "Enhanced agility, reaction time, and movement efficiency",
                "categories": ["Individual Skills", "Agility"]
            }
        ]

        # Additional Joint Mobility Activities
        joint_mobility_activities = [
            {
                "name": "Advanced Joint Preparation",
                "description": "Comprehensive joint mobility routine for advanced athletes",
                "activity_type": ActivityType.WARM_UP,
                "difficulty": DifficultyLevel.ADVANCED,
                "equipment_required": EquipmentRequirement.MINIMAL,
                "duration_minutes": 20,
                "instructions": "1. Advanced shoulder mobility\n2. Hip complex mobility\n3. Spine articulation\n4. Ankle mobility flow\n5. Wrist/elbow preparation",
                "safety_guidelines": "Progress gradually, respect joint ranges, maintain control",
                "variations": "Add resistance bands, increase complexity, flow combinations",
                "benefits": "Enhanced joint range of motion, injury prevention, movement quality",
                "categories": ["Warm-up", "Joint Mobility"]
            }
        ]

        # Additional Light Cardio Activities
        light_cardio_activities = [
            {
                "name": "Progressive Cardio Flow",
                "description": "Flowing cardio routine with gradual intensity progression",
                "activity_type": ActivityType.WARM_UP,
                "difficulty": DifficultyLevel.INTERMEDIATE,
                "equipment_required": EquipmentRequirement.NONE,
                "duration_minutes": 20,
                "instructions": "1. Walking patterns\n2. Light jogging variations\n3. Dynamic movement combinations\n4. Rhythmic stepping\n5. Cool-down progression",
                "safety_guidelines": "Monitor intensity, maintain proper form, progress gradually",
                "variations": "Add arm movements, directional changes, rhythm variations",
                "benefits": "Cardiovascular warm-up, movement preparation, coordination",
                "categories": ["Warm-up", "Light Cardio"]
            }
        ]

        # Add all activities to the database
        for activity_group in [soccer_activities, balance_activities, agility_activities, 
                             joint_mobility_activities, light_cardio_activities]:
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
        print("Additional soccer and underrepresented category activities seeded successfully!")

if __name__ == "__main__":
    asyncio.run(seed_additional_activities_2()) 