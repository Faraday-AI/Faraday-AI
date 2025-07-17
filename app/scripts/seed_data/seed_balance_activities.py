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

async def seed_balance_activities():
    """Seed additional activities to balance category distribution."""
    async with async_session() as session:
        # Additional Running Activities
        running_activities = [
            {
                "name": "Interval Running Technique",
                "description": "Progressive running technique development with intervals",
                "activity_type": ActivityType.SKILL_DEVELOPMENT,
                "difficulty": DifficultyLevel.INTERMEDIATE,
                "equipment_required": EquipmentRequirement.MINIMAL,
                "duration_minutes": 25,
                "instructions": "1. Form running drills\n2. Stride length practice\n3. Cadence training\n4. Speed variations\n5. Recovery intervals",
                "safety_guidelines": "Proper footwear, gradual progression, surface awareness",
                "variations": "Adjust intervals, modify terrain, change speeds",
                "benefits": "Running efficiency, form improvement, endurance development",
                "categories": ["Cardio", "Running"]
            },
            {
                "name": "Endurance Running Program",
                "description": "Structured running program for endurance building",
                "activity_type": ActivityType.FITNESS_TRAINING,
                "difficulty": DifficultyLevel.INTERMEDIATE,
                "equipment_required": EquipmentRequirement.MINIMAL,
                "duration_minutes": 30,
                "instructions": "1. Progressive warm-up\n2. Distance running\n3. Pace variations\n4. Hill training\n5. Cool-down jog",
                "safety_guidelines": "Heart rate monitoring, hydration, proper pacing",
                "variations": "Distance adjustments, terrain changes, pace modifications",
                "benefits": "Cardiovascular fitness, stamina, mental endurance",
                "categories": ["Cardio", "Running"]
            }
        ]

        # Additional Volleyball Activities
        volleyball_activities = [
            {
                "name": "Volleyball Defense Training",
                "description": "Defensive skills and positioning practice",
                "activity_type": ActivityType.SKILL_DEVELOPMENT,
                "difficulty": DifficultyLevel.INTERMEDIATE,
                "equipment_required": EquipmentRequirement.MINIMAL,
                "duration_minutes": 30,
                "instructions": "1. Defensive stance practice\n2. Digging drills\n3. Position movement\n4. Block footwork\n5. Game scenarios",
                "safety_guidelines": "Proper landing technique, court awareness, communication",
                "variations": "Add attack variations, modify speed, include combinations",
                "benefits": "Defensive skills, reaction time, court awareness",
                "categories": ["Team Sports", "Volleyball"]
            },
            {
                "name": "Volleyball Team Tactics",
                "description": "Team-based volleyball strategy training",
                "activity_type": ActivityType.SKILL_DEVELOPMENT,
                "difficulty": DifficultyLevel.ADVANCED,
                "equipment_required": EquipmentRequirement.MODERATE,
                "duration_minutes": 35,
                "instructions": "1. Formation practice\n2. Rotation drills\n3. Play calling\n4. Team communication\n5. Strategy implementation",
                "safety_guidelines": "Clear communication, proper spacing, role understanding",
                "variations": "Different formations, offensive/defensive focus, game situations",
                "benefits": "Team coordination, strategic thinking, game awareness",
                "categories": ["Team Sports", "Volleyball"]
            }
        ]

        # Additional Light Cardio Activities
        light_cardio_activities = [
            {
                "name": "Rhythmic Movement Circuit",
                "description": "Light cardio workout with rhythmic movements",
                "activity_type": ActivityType.WARM_UP,
                "difficulty": DifficultyLevel.BEGINNER,
                "equipment_required": EquipmentRequirement.NONE,
                "duration_minutes": 20,
                "instructions": "1. Marching patterns\n2. Arm circles\n3. Step touches\n4. Knee lifts\n5. Gentle bouncing",
                "safety_guidelines": "Maintain control, proper posture, steady breathing",
                "variations": "Add arm movements, change rhythm, modify intensity",
                "benefits": "Cardiovascular warm-up, coordination, rhythm development",
                "categories": ["Warm-up", "Light Cardio"]
            },
            {
                "name": "Active Movement Preparation",
                "description": "Progressive cardio preparation routine",
                "activity_type": ActivityType.WARM_UP,
                "difficulty": DifficultyLevel.INTERMEDIATE,
                "equipment_required": EquipmentRequirement.NONE,
                "duration_minutes": 15,
                "instructions": "1. Walking variations\n2. Skip patterns\n3. Lateral movements\n4. Direction changes\n5. Movement combinations",
                "safety_guidelines": "Start slow, increase gradually, maintain control",
                "variations": "Speed adjustments, pattern changes, movement complexity",
                "benefits": "Movement preparation, light cardiovascular work, coordination",
                "categories": ["Warm-up", "Light Cardio"]
            }
        ]

        # Additional Balance Activity
        balance_activities = [
            {
                "name": "Dynamic Balance Flow",
                "description": "Flowing balance challenges with movement transitions",
                "activity_type": ActivityType.SKILL_DEVELOPMENT,
                "difficulty": DifficultyLevel.INTERMEDIATE,
                "equipment_required": EquipmentRequirement.MINIMAL,
                "duration_minutes": 25,
                "instructions": "1. Single leg sequences\n2. Balance transitions\n3. Movement combinations\n4. Direction changes\n5. Flow patterns",
                "safety_guidelines": "Clear space, proper progression, spotting when needed",
                "variations": "Eyes open/closed, surface changes, movement speed",
                "benefits": "Balance control, proprioception, movement confidence",
                "categories": ["Individual Skills", "Balance"]
            }
        ]

        # Additional Breathing Activity
        breathing_activities = [
            {
                "name": "Athletic Breathing Integration",
                "description": "Sport-specific breathing techniques and patterns",
                "activity_type": ActivityType.COOL_DOWN,
                "difficulty": DifficultyLevel.INTERMEDIATE,
                "equipment_required": EquipmentRequirement.NONE,
                "duration_minutes": 20,
                "instructions": "1. Activity-specific patterns\n2. Rhythm development\n3. Movement integration\n4. Recovery breathing\n5. Performance patterns",
                "safety_guidelines": "Natural progression, avoid strain, maintain focus",
                "variations": "Pattern changes, movement integration, duration adjustments",
                "benefits": "Performance breathing, recovery enhancement, stress management",
                "categories": ["Cool-down", "Breathing"]
            }
        ]

        # Additional Joint Mobility Activity
        joint_mobility_activities = [
            {
                "name": "Sport Mobility Preparation",
                "description": "Sport-specific joint mobility routine",
                "activity_type": ActivityType.WARM_UP,
                "difficulty": DifficultyLevel.INTERMEDIATE,
                "equipment_required": EquipmentRequirement.MINIMAL,
                "duration_minutes": 20,
                "instructions": "1. Sport-specific patterns\n2. Movement preparation\n3. Joint integration\n4. Dynamic mobility\n5. Activity preparation",
                "safety_guidelines": "Controlled movement, proper progression, joint awareness",
                "variations": "Sport focus, movement complexity, time adjustments",
                "benefits": "Sport readiness, joint preparation, movement quality",
                "categories": ["Warm-up", "Joint Mobility"]
            }
        ]

        # Add all activities to the database
        for activity_group in [running_activities, volleyball_activities, light_cardio_activities,
                             balance_activities, breathing_activities, joint_mobility_activities]:
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
        print("Balance activities seeded successfully!")

if __name__ == "__main__":
    asyncio.run(seed_balance_activities()) 