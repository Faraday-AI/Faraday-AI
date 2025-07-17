from sqlalchemy import text
from app.core.database import async_session
import asyncio

async def seed_final_balance():
    """Seed final balancing activities to ensure all categories have at least 3 activities."""
    async with async_session() as session:
        # Single Activity Categories Updates
        dynamic_stretching_activities = [
            {
                "name": "Dynamic Movement Sequence",
                "description": "Progressive dynamic stretching routine focusing on full-body movement patterns",
                "activity_type": "WARM_UP",
                "difficulty": "INTERMEDIATE",
                "equipment_required": "NONE",
                "duration_minutes": 15,
                "instructions": "1. Upper body mobility sequence (3 min)\n2. Lower body dynamic patterns (3 min)\n3. Multi-directional movements (3 min)\n4. Sport-specific preparation (3 min)\n5. Movement flow integration (3 min)",
                "safety_guidelines": "1. Start slowly\n2. Progress gradually\n3. Maintain control\n4. Stay within range\n5. Monitor breathing\n6. Adapt as needed",
                "variations": "1. Speed adjustments\n2. Range modifications\n3. Pattern complexity\n4. Movement combinations\n5. Direction changes\n6. Equipment integration",
                "benefits": "1. Improved mobility\n2. Better movement quality\n3. Enhanced warm-up\n4. Injury prevention\n5. Performance preparation\n6. Movement awareness",
                "categories": ["Warm-up", "Dynamic Stretching"]
            },
            {
                "name": "Sport Dynamic Preparation",
                "description": "Sport-specific dynamic stretching routine for athletic preparation",
                "activity_type": "WARM_UP",
                "difficulty": "ADVANCED",
                "equipment_required": "MINIMAL",
                "duration_minutes": 20,
                "instructions": "1. Sport movement analysis (4 min)\n2. Dynamic pattern progression (4 min)\n3. Movement complexity building (4 min)\n4. Speed development (4 min)\n5. Integration and flow (4 min)",
                "safety_guidelines": "1. Proper progression\n2. Movement quality\n3. Appropriate intensity\n4. Recovery periods\n5. Technique focus\n6. Individual adaptation",
                "variations": "1. Sport specificity\n2. Movement complexity\n3. Speed variations\n4. Pattern combinations\n5. Equipment use\n6. Partner work",
                "benefits": "1. Sport readiness\n2. Movement efficiency\n3. Performance enhancement\n4. Injury prevention\n5. Coordination improvement\n6. Better warm-up quality",
                "categories": ["Warm-up", "Dynamic Stretching"]
            }
        ]

        high_intensity_activities = [
            {
                "name": "Advanced HIIT Circuit",
                "description": "High-intensity interval training focusing on full-body conditioning",
                "activity_type": "FITNESS_TRAINING",
                "difficulty": "ADVANCED",
                "equipment_required": "MINIMAL",
                "duration_minutes": 25,
                "instructions": "1. Dynamic warm-up (5 min)\n2. HIIT circuit explanation (2 min)\n3. Work intervals (12 min)\n4. Active recovery (3 min)\n5. Cool-down (3 min)",
                "safety_guidelines": "1. Proper form priority\n2. Intensity management\n3. Rest intervals\n4. Hydration focus\n5. Movement control\n6. Recovery monitoring",
                "variations": "1. Work-rest ratios\n2. Exercise selection\n3. Equipment use\n4. Complexity levels\n5. Target focus\n6. Circuit structure",
                "benefits": "1. Cardiovascular fitness\n2. Strength development\n3. Metabolic enhancement\n4. Endurance improvement\n5. Power development\n6. Recovery capacity",
                "categories": ["Cardio", "High-Intensity"]
            },
            {
                "name": "Power Conditioning Series",
                "description": "Progressive high-intensity power development workout",
                "activity_type": "FITNESS_TRAINING",
                "difficulty": "ADVANCED",
                "equipment_required": "MODERATE",
                "duration_minutes": 30,
                "instructions": "1. Power preparation (5 min)\n2. Technique review (5 min)\n3. Power development (10 min)\n4. Complex combinations (5 min)\n5. Power endurance (5 min)",
                "safety_guidelines": "1. Technical excellence\n2. Progressive loading\n3. Recovery emphasis\n4. Movement quality\n5. Fatigue management\n6. Adaptation monitoring",
                "variations": "1. Movement selection\n2. Load progression\n3. Volume adjustment\n4. Rest periods\n5. Complex design\n6. Integration methods",
                "benefits": "1. Power development\n2. Strength enhancement\n3. Athletic performance\n4. Movement efficiency\n5. Work capacity\n6. Recovery ability",
                "categories": ["Cardio", "High-Intensity"]
            }
        ]

        soccer_activities = [
            {
                "name": "Soccer Ball Control",
                "description": "Technical soccer skills focusing on ball control and manipulation",
                "activity_type": "SKILL_DEVELOPMENT",
                "difficulty": "INTERMEDIATE",
                "equipment_required": "MINIMAL",
                "duration_minutes": 20,
                "instructions": "1. Basic control drills (4 min)\n2. Movement patterns (4 min)\n3. Technical progression (4 min)\n4. Speed development (4 min)\n5. Skill integration (4 min)",
                "safety_guidelines": "1. Proper footwear\n2. Surface check\n3. Progressive difficulty\n4. Technical focus\n5. Rest periods\n6. Individual pace",
                "variations": "1. Ball techniques\n2. Movement patterns\n3. Speed variations\n4. Skill combinations\n5. Direction changes\n6. Pressure situations",
                "benefits": "1. Ball control\n2. Technical skills\n3. Movement quality\n4. Game readiness\n5. Confidence building\n6. Performance enhancement",
                "categories": ["Team Sports", "Soccer"]
            },
            {
                "name": "Soccer Game Skills",
                "description": "Game-based soccer skills and tactical development",
                "activity_type": "GAME",
                "difficulty": "INTERMEDIATE",
                "equipment_required": "MINIMAL",
                "duration_minutes": 25,
                "instructions": "1. Skill warm-up (5 min)\n2. Technical practice (5 min)\n3. Game situations (5 min)\n4. Small-sided games (5 min)\n5. Skill application (5 min)",
                "safety_guidelines": "1. Field awareness\n2. Communication\n3. Fair play\n4. Hydration breaks\n5. Equipment check\n6. Safety spacing",
                "variations": "1. Game formats\n2. Team sizes\n3. Field dimensions\n4. Rule modifications\n5. Scoring systems\n6. Time variations",
                "benefits": "1. Game understanding\n2. Tactical awareness\n3. Team play\n4. Decision making\n5. Skill application\n6. Game fitness",
                "categories": ["Team Sports", "Soccer"]
            }
        ]

        static_stretching_activities = [
            {
                "name": "Complete Flexibility Program",
                "description": "Comprehensive static stretching routine for full-body flexibility",
                "activity_type": "COOL_DOWN",
                "difficulty": "INTERMEDIATE",
                "equipment_required": "MINIMAL",
                "duration_minutes": 20,
                "instructions": "1. Breathing preparation (3 min)\n2. Upper body focus (4 min)\n3. Lower body focus (4 min)\n4. Core integration (4 min)\n5. Final relaxation (5 min)",
                "safety_guidelines": "1. No bouncing\n2. Gentle progression\n3. Breathing focus\n4. Position awareness\n5. Time monitoring\n6. Comfort priority",
                "variations": "1. Hold durations\n2. Position modifications\n3. Sequence changes\n4. Partner work\n5. Props usage\n6. Focus areas",
                "benefits": "1. Flexibility improvement\n2. Muscle recovery\n3. Tension release\n4. Posture enhancement\n5. Range increase\n6. Relaxation promotion",
                "categories": ["Cool-down", "Static Stretching"]
            },
            {
                "name": "Advanced Flexibility Flow",
                "description": "Progressive static stretching sequence for advanced flexibility development",
                "activity_type": "COOL_DOWN",
                "difficulty": "ADVANCED",
                "equipment_required": "MINIMAL",
                "duration_minutes": 25,
                "instructions": "1. Mindful preparation (5 min)\n2. Progressive stretching (5 min)\n3. Deep holds (5 min)\n4. Position flows (5 min)\n5. Recovery phase (5 min)",
                "safety_guidelines": "1. Proper alignment\n2. Breathing technique\n3. Edge awareness\n4. Time management\n5. Body feedback\n6. Recovery focus",
                "variations": "1. Position complexity\n2. Hold duration\n3. Movement integration\n4. Props utilization\n5. Focus variation\n6. Sequence modification",
                "benefits": "1. Advanced flexibility\n2. Body awareness\n3. Recovery enhancement\n4. Range optimization\n5. Movement quality\n6. Mental focus",
                "categories": ["Cool-down", "Static Stretching"]
            }
        ]

        # Two Activity Categories Updates
        agility_activities = [
            {
                "name": "Advanced Agility Development",
                "description": "Complex agility training for advanced movement capability",
                "activity_type": "SKILL_DEVELOPMENT",
                "difficulty": "ADVANCED",
                "equipment_required": "MODERATE",
                "duration_minutes": 25,
                "instructions": "1. Movement preparation (5 min)\n2. Pattern progression (5 min)\n3. Speed development (5 min)\n4. Complex combinations (5 min)\n5. Integration phase (5 min)",
                "safety_guidelines": "1. Surface check\n2. Proper footwear\n3. Progressive loading\n4. Recovery periods\n5. Form priority\n6. Fatigue monitoring",
                "variations": "1. Pattern complexity\n2. Speed variations\n3. Direction changes\n4. Equipment use\n5. Rest intervals\n6. Combination types",
                "benefits": "1. Movement efficiency\n2. Reaction speed\n3. Coordination enhancement\n4. Athletic performance\n5. Body control\n6. Sport readiness",
                "categories": ["Individual Skills", "Agility"]
            }
        ]

        basketball_activities = [
            {
                "name": "Basketball Skill Integration",
                "description": "Advanced basketball skills combining multiple techniques",
                "activity_type": "SKILL_DEVELOPMENT",
                "difficulty": "ADVANCED",
                "equipment_required": "MINIMAL",
                "duration_minutes": 30,
                "instructions": "1. Skill warm-up (5 min)\n2. Technical progression (5 min)\n3. Combination drills (10 min)\n4. Game application (5 min)\n5. Skill refinement (5 min)",
                "safety_guidelines": "1. Court awareness\n2. Proper technique\n3. Progressive intensity\n4. Rest periods\n5. Equipment check\n6. Safety spacing",
                "variations": "1. Drill complexity\n2. Speed variations\n3. Defensive pressure\n4. Skill combinations\n5. Game situations\n6. Team integration",
                "benefits": "1. Skill mastery\n2. Game understanding\n3. Decision making\n4. Performance enhancement\n5. Team integration\n6. Competitive readiness",
                "categories": ["Team Sports", "Basketball"]
            }
        ]

        jumping_activities = [
            {
                "name": "Advanced Jump Training",
                "description": "Progressive jumping program for advanced power development",
                "activity_type": "FITNESS_TRAINING",
                "difficulty": "ADVANCED",
                "equipment_required": "MODERATE",
                "duration_minutes": 25,
                "instructions": "1. Jump preparation (5 min)\n2. Technique work (5 min)\n3. Power development (5 min)\n4. Complex jumps (5 min)\n5. Integration phase (5 min)",
                "safety_guidelines": "1. Landing mechanics\n2. Progressive loading\n3. Surface check\n4. Recovery time\n5. Form priority\n6. Fatigue monitoring",
                "variations": "1. Jump types\n2. Height progression\n3. Combination work\n4. Equipment use\n5. Rest periods\n6. Complex patterns",
                "benefits": "1. Power development\n2. Jump height\n3. Landing mechanics\n4. Athletic performance\n5. Body control\n6. Explosive strength",
                "categories": ["Cardio", "Jumping"]
            }
        ]

        light_movement_activities = [
            {
                "name": "Recovery Movement Integration",
                "description": "Comprehensive light movement program for active recovery",
                "activity_type": "COOL_DOWN",
                "difficulty": "INTERMEDIATE",
                "equipment_required": "NONE",
                "duration_minutes": 20,
                "instructions": "1. Movement assessment (4 min)\n2. Flow patterns (4 min)\n3. Integration work (4 min)\n4. Recovery focus (4 min)\n5. Cool-down phase (4 min)",
                "safety_guidelines": "1. Movement quality\n2. Breathing focus\n3. Body awareness\n4. Proper progression\n5. Individual pace\n6. Recovery priority",
                "variations": "1. Movement patterns\n2. Speed adjustments\n3. Focus areas\n4. Time variations\n5. Position changes\n6. Flow sequences",
                "benefits": "1. Active recovery\n2. Movement quality\n3. Body awareness\n4. Tension release\n5. Recovery enhancement\n6. Mental relaxation",
                "categories": ["Cool-down", "Light Movement"]
            }
        ]

        volleyball_activities = [
            {
                "name": "Volleyball Skill Progression",
                "description": "Advanced volleyball skills and technical development",
                "activity_type": "SKILL_DEVELOPMENT",
                "difficulty": "ADVANCED",
                "equipment_required": "MINIMAL",
                "duration_minutes": 30,
                "instructions": "1. Skill warm-up (5 min)\n2. Technical work (5 min)\n3. Combination drills (10 min)\n4. Game situations (5 min)\n5. Skill integration (5 min)",
                "safety_guidelines": "1. Court awareness\n2. Proper technique\n3. Landing mechanics\n4. Communication\n5. Progressive loading\n6. Safety spacing",
                "variations": "1. Skill focus\n2. Drill complexity\n3. Game situations\n4. Position specific\n5. Team integration\n6. Pressure scenarios",
                "benefits": "1. Skill mastery\n2. Game understanding\n3. Team coordination\n4. Performance enhancement\n5. Decision making\n6. Competitive readiness",
                "categories": ["Team Sports", "Volleyball"]
            }
        ]

        # Combine all activities
        all_activities = (
            dynamic_stretching_activities +
            high_intensity_activities +
            soccer_activities +
            static_stretching_activities +
            agility_activities +
            basketball_activities +
            jumping_activities +
            light_movement_activities +
            volleyball_activities
        )

        # Add all activities to database
        for activity in all_activities:
            # Check if activity exists
            result = await session.execute(
                text("SELECT id FROM activities WHERE name = :name"),
                {"name": activity["name"]}
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
                        "name": activity["name"],
                        "description": activity["description"],
                        "activity_type": activity["activity_type"],
                        "difficulty": activity["difficulty"],
                        "equipment_required": activity["equipment_required"],
                        "duration_minutes": activity["duration_minutes"],
                        "instructions": activity["instructions"],
                        "safety_guidelines": activity["safety_guidelines"],
                        "variations": activity["variations"],
                        "benefits": activity["benefits"]
                    }
                )
                activity_id = str(result.scalar())
                
                # Add category associations
                for category_name in activity["categories"]:
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
        print("Final balance activities seeded successfully!")

if __name__ == "__main__":
    asyncio.run(seed_final_balance()) 