from sqlalchemy import text
from app.core.database import async_session
import asyncio

async def update_activities_comprehensive():
    """Update activities with more comprehensive details."""
    async with async_session() as session:
        # Enhanced Running Activities Updates
        running_updates = {
            "Interval Running Technique": {
                "description": "Comprehensive running technique development focusing on form, efficiency, and interval training principles",
                "instructions": "1. Dynamic warm-up (5 min)\n2. Form running drills: high knees, butt kicks, skips (5 min)\n3. Stride length analysis and adjustment (5 min)\n4. Interval pattern: 2 min run, 1 min recovery x 4 (12 min)\n5. Form assessment and correction (3 min)\n6. Cool-down and technique review (5 min)",
                "safety_guidelines": "1. Proper running shoes required\n2. Start with form before speed\n3. Maintain proper hydration\n4. Monitor heart rate\n5. Run on appropriate surfaces\n6. Stop if experiencing pain",
                "variations": "1. Adjust interval ratios (1:1, 2:1, 1:2)\n2. Incorporate hills or terrain changes\n3. Modify speeds within intervals\n4. Add resistance (weighted vest)\n5. Include backward running\n6. Integrate lateral movements",
                "benefits": "1. Improved running economy\n2. Enhanced cardiovascular fitness\n3. Better running form\n4. Increased speed and power\n5. Reduced injury risk\n6. Greater endurance capacity"
            },
            "Endurance Running Program": {
                "description": "Structured endurance development program incorporating progressive distance and intensity",
                "instructions": "1. Pre-run mobility routine (5 min)\n2. Progressive warm-up jog (5 min)\n3. Distance running with pace changes (15 min)\n4. Hill or terrain challenge (5 min)\n5. Steady-state endurance segment (10 min)\n6. Form maintenance drills (5 min)",
                "safety_guidelines": "1. Complete health screening\n2. Use heart rate zones\n3. Progressive distance increase\n4. Regular hydration breaks\n5. Weather-appropriate gear\n6. Post-run recovery protocol",
                "variations": "1. Fartlek training integration\n2. Progressive distance increases\n3. Terrain variation challenges\n4. Pace manipulation sets\n5. Recovery run modifications\n6. Cross-training elements",
                "benefits": "1. Improved aerobic capacity\n2. Enhanced stamina\n3. Better pace management\n4. Increased mental toughness\n5. Improved recovery ability\n6. Greater running efficiency"
            }
        }

        # Enhanced Volleyball Activities Updates
        volleyball_updates = {
            "Volleyball Defense Training": {
                "description": "Comprehensive defensive skills program focusing on positioning, movement, and reaction training",
                "instructions": "1. Defensive stance practice (5 min)\n2. Movement pattern drills (5 min)\n3. Dig technique progression (10 min)\n4. Block footwork series (5 min)\n5. Defensive scenarios (10 min)\n6. Position-specific training (5 min)",
                "safety_guidelines": "1. Proper knee protection\n2. Correct landing technique\n3. Court awareness training\n4. Communication protocols\n5. Progressive intensity\n6. Regular rest intervals",
                "variations": "1. Add attack variations\n2. Modify ball speeds\n3. Include combination plays\n4. Vary court positions\n5. Integrate team scenarios\n6. Add competitive elements",
                "benefits": "1. Improved reaction time\n2. Better court coverage\n3. Enhanced defensive technique\n4. Increased agility\n5. Better team coordination\n6. Improved game awareness"
            },
            "Volleyball Team Tactics": {
                "description": "Advanced team-based volleyball strategy training incorporating offensive and defensive systems",
                "instructions": "1. Team formation review (5 min)\n2. Rotation practice (5 min)\n3. Offensive system drills (10 min)\n4. Defensive coverage patterns (10 min)\n5. Game situation scenarios (10 min)\n6. Team communication exercises (5 min)",
                "safety_guidelines": "1. Clear communication system\n2. Proper spacing protocols\n3. Role understanding\n4. Progressive complexity\n5. Regular feedback sessions\n6. Injury prevention focus",
                "variations": "1. Different offensive systems\n2. Various defensive formations\n3. Serve receive patterns\n4. Attack combinations\n5. Blocking schemes\n6. Transition play focus",
                "benefits": "1. Enhanced team coordination\n2. Improved strategic thinking\n3. Better game management\n4. Increased tactical awareness\n5. Improved team communication\n6. Greater competitive success"
            }
        }

        # Enhanced Light Cardio Activities Updates
        light_cardio_updates = {
            "Rhythmic Movement Circuit": {
                "description": "Progressive rhythmic movement sequence designed for cardiovascular development and coordination",
                "instructions": "1. Basic rhythm establishment (3 min)\n2. Upper body patterns (4 min)\n3. Lower body sequences (4 min)\n4. Combination movements (4 min)\n5. Intensity progression (3 min)\n6. Cool-down sequence (2 min)",
                "safety_guidelines": "1. Maintain proper form\n2. Progressive intensity\n3. Regular breathing pattern\n4. Appropriate footwear\n5. Spatial awareness\n6. Modified options available",
                "variations": "1. Tempo changes\n2. Movement complexity\n3. Direction variations\n4. Equipment integration\n5. Partner patterns\n6. Music tempo matching",
                "benefits": "1. Improved coordination\n2. Enhanced rhythm\n3. Better cardiovascular fitness\n4. Increased movement awareness\n5. Enhanced agility\n6. Greater movement confidence"
            }
        }

        # Enhanced Balance Activities Updates
        balance_updates = {
            "Dynamic Balance Flow": {
                "description": "Progressive balance training incorporating dynamic movements and stability challenges",
                "instructions": "1. Static balance foundation (5 min)\n2. Single leg progressions (5 min)\n3. Dynamic movement patterns (5 min)\n4. Balance flow sequences (5 min)\n5. Challenge combinations (5 min)\n6. Stability tests (5 min)",
                "safety_guidelines": "1. Clear space requirement\n2. Proper progression\n3. Spotter when needed\n4. Surface assessment\n5. Equipment check\n6. Modified options available",
                "variations": "1. Surface changes\n2. Visual input modification\n3. Movement speed adjustments\n4. Equipment integration\n5. Partner challenges\n6. Direction variations",
                "benefits": "1. Improved balance control\n2. Enhanced proprioception\n3. Better stability\n4. Increased core strength\n5. Greater movement confidence\n6. Injury prevention"
            }
        }

        # Enhanced Breathing Activities Updates
        breathing_updates = {
            "Athletic Breathing Integration": {
                "description": "Comprehensive breathing technique program designed for athletic performance enhancement",
                "instructions": "1. Breathing assessment (3 min)\n2. Diaphragmatic breathing practice (5 min)\n3. Movement integration (5 min)\n4. Performance patterns (5 min)\n5. Recovery breathing (5 min)\n6. Sport-specific application (7 min)",
                "safety_guidelines": "1. Proper posture maintenance\n2. Progressive complexity\n3. Regular assessment\n4. Modified options\n5. Recovery periods\n6. Individual adaptation",
                "variations": "1. Breathing patterns\n2. Movement complexity\n3. Position changes\n4. Sport specificity\n5. Intensity levels\n6. Recovery focus",
                "benefits": "1. Improved oxygen efficiency\n2. Better performance\n3. Enhanced recovery\n4. Reduced fatigue\n5. Increased focus\n6. Better stress management"
            }
        }

        # Enhanced Joint Mobility Activities Updates
        joint_mobility_updates = {
            "Sport Mobility Preparation": {
                "description": "Comprehensive joint mobility program designed for sport-specific movement preparation",
                "instructions": "1. Joint assessment (3 min)\n2. Progressive mobility sequence (5 min)\n3. Sport-specific patterns (5 min)\n4. Dynamic integration (5 min)\n5. Movement flow (5 min)\n6. Performance preparation (7 min)",
                "safety_guidelines": "1. Individual assessment\n2. Progressive loading\n3. Range monitoring\n4. Proper warm-up\n5. Movement control\n6. Modified options",
                "variations": "1. Sport-specific focus\n2. Movement complexity\n3. Speed variations\n4. Equipment integration\n5. Partner drills\n6. Environmental adaptation",
                "benefits": "1. Improved joint range\n2. Better movement quality\n3. Enhanced performance\n4. Injury prevention\n5. Increased body awareness\n6. Greater movement efficiency"
            }
        }

        # Update all activities
        all_updates = {**running_updates, **volleyball_updates, **light_cardio_updates,
                      **balance_updates, **breathing_updates, **joint_mobility_updates}

        for activity_name, updates in all_updates.items():
            await session.execute(
                text("""
                    UPDATE activities
                    SET description = :description,
                        instructions = :instructions,
                        safety_guidelines = :safety_guidelines,
                        variations = :variations,
                        benefits = :benefits,
                        updated_at = NOW()
                    WHERE name = :name
                """),
                {
                    "name": activity_name,
                    **updates
                }
            )

        await session.commit()
        print("Activities updated with comprehensive details successfully!")

if __name__ == "__main__":
    asyncio.run(update_activities_comprehensive()) 