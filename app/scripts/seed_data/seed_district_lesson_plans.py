#!/usr/bin/env python3
"""
Seed comprehensive lesson plans for the entire district.
This creates detailed lesson plans based on existing lessons data to cover the school year.
"""

import json
import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import SessionLocal


def seed_district_lesson_plans(session: Session) -> None:
    """Seed comprehensive lesson plans for the entire district."""
    print("Seeding comprehensive district lesson plans...")
    
    try:
        # Check if we already have comprehensive lesson plans
        result = session.execute(text("SELECT COUNT(*) FROM lesson_plans")).scalar()
        if result > 100:  # If we already have substantial lesson plans
            print(f"Lesson plans table already has {result} records. This may be sufficient.")
            return
        
        # Get existing data for foreign keys
        educational_teachers = session.execute(text("SELECT id FROM educational_teachers")).fetchall()
        subjects = session.execute(text("SELECT id FROM subjects")).fetchall()
        grade_levels = session.execute(text("SELECT id FROM grade_levels")).fetchall()
        
        if not educational_teachers or not subjects or not grade_levels:
            print("Missing required data: teachers, subjects, or grade levels")
            return
        
        teacher_ids = [row[0] for row in educational_teachers]
        subject_ids = [row[0] for row in subjects]
        grade_level_ids = [row[0] for row in grade_levels]
        
        print(f"Found {len(teacher_ids)} teachers, {len(subject_ids)} subjects, {len(grade_level_ids)} grade levels")
        
        # Calculate how many lesson plans we need for the district
        # 6 schools × 180 school days = 1,080 minimum lesson plans needed
        target_lesson_plans = 1200  # Slightly more than minimum to account for different subjects/grade levels
        
        # Create comprehensive lesson plan templates
        lesson_templates = [
            {
                "unit_title": "Fundamental Movement Skills",
                "lesson_title": "Basic Locomotor Movements",
                "essential_question": "How do we move our bodies safely and efficiently?",
                "do_now": "Practice walking, running, and jumping in place",
                "objectives": ["Demonstrate basic locomotor skills", "Understand spatial awareness", "Practice following directions"],
                "anticipatory_set": "Show pictures of different animals and their movements",
                "direct_instruction": "Demonstrate proper form for walking, running, and jumping",
                "guided_practice": ["Walking in different directions", "Running with control", "Jumping in place"],
                "independent_practice": ["Create movement sequences", "Practice with partners"],
                "closure": "Review what we learned about movement",
                "assessment": "Observation of skill demonstration",
                "materials": ["Cones", "Bean bags", "Music player"],
                "homework": "Practice movements at home",
                "notes": "Focus on safety and proper form",
                "next_steps": "Introduce more complex movements"
            },
            {
                "unit_title": "Team Sports Fundamentals",
                "lesson_title": "Introduction to Teamwork",
                "essential_question": "How do we work together as a team?",
                "do_now": "Find a partner and practice throwing and catching",
                "objectives": ["Learn cooperation skills", "Practice basic throwing/catching", "Understand fair play"],
                "anticipatory_set": "Discuss what makes a good team player",
                "direct_instruction": "Demonstrate proper throwing and catching technique",
                "guided_practice": ["Partner toss games", "Group circle activities", "Simple relay races"],
                "independent_practice": ["Create team challenges", "Practice with different partners"],
                "closure": "Share what we learned about teamwork",
                "assessment": "Participation and cooperation observation",
                "materials": ["Soft balls", "Hula hoops", "Cones"],
                "homework": "Practice throwing and catching at home",
                "notes": "Emphasize cooperation over competition",
                "next_steps": "Introduce team sports rules"
            },
            {
                "unit_title": "Fitness and Wellness",
                "lesson_title": "Cardiovascular Health",
                "essential_question": "Why is cardiovascular fitness important?",
                "do_now": "Light jogging and stretching",
                "objectives": ["Understand cardiovascular fitness", "Practice aerobic activities", "Learn about heart health"],
                "anticipatory_set": "Discuss how the heart works during exercise",
                "direct_instruction": "Explain different types of aerobic activities",
                "guided_practice": ["Walking", "Jogging", "Jumping jacks", "Dancing"],
                "independent_practice": ["Create fitness routines", "Monitor heart rate"],
                "closure": "Reflect on how exercise makes us feel",
                "assessment": "Participation and understanding of concepts",
                "materials": ["Stopwatch", "Heart rate monitors", "Music"],
                "homework": "Exercise for 20 minutes at home",
                "notes": "Monitor students for fatigue",
                "next_steps": "Introduce strength training"
            },
            {
                "unit_title": "Strength and Conditioning",
                "lesson_title": "Basic Strength Training",
                "essential_question": "How can we build strength safely?",
                "do_now": "Light warm-up exercises",
                "objectives": ["Learn proper form for basic exercises", "Understand muscle groups", "Practice safety techniques"],
                "anticipatory_set": "Discuss why strength training is important",
                "direct_instruction": "Demonstrate proper form for push-ups, squats, and planks",
                "guided_practice": ["Modified push-ups", "Body weight squats", "Plank holds"],
                "independent_practice": ["Create exercise circuits", "Practice with partners"],
                "closure": "Review safety guidelines",
                "assessment": "Form assessment and participation",
                "materials": ["Exercise mats", "Resistance bands", "Stopwatch"],
                "homework": "Practice exercises at home",
                "notes": "Emphasize proper form over quantity",
                "next_steps": "Introduce more advanced exercises"
            },
            {
                "unit_title": "Dance and Creative Movement",
                "lesson_title": "Creative Expression Through Movement",
                "essential_question": "How can we express ourselves through movement?",
                "do_now": "Free dance to music",
                "objectives": ["Express creativity through movement", "Learn basic dance steps", "Work with rhythm"],
                "anticipatory_set": "Show examples of creative movement",
                "direct_instruction": "Teach basic dance steps and combinations",
                "guided_practice": ["Follow the leader", "Mirror movements", "Group choreography"],
                "independent_practice": ["Create dance sequences", "Perform for partners"],
                "closure": "Share creative movements",
                "assessment": "Creativity and participation",
                "materials": ["Music player", "Open space", "Props"],
                "homework": "Practice dance moves at home",
                "notes": "Encourage creativity and self-expression",
                "next_steps": "Introduce cultural dance forms"
            }
        ]
        
        # Generate comprehensive lesson plans
        print(f"Creating {target_lesson_plans} comprehensive lesson plans...")
        
        # School year dates (September to June)
        start_date = datetime(2024, 9, 1)
        end_date = datetime(2025, 6, 15)
        date_range = (end_date - start_date).days
        
        successful_inserts = 0
        for i in range(target_lesson_plans):
            try:
                # Select random template and data
                template = random.choice(lesson_templates)
                teacher_id = random.choice(teacher_ids)
                subject_id = random.choice(subject_ids)
                grade_level_id = random.choice(grade_level_ids)
                
                # Generate random date within school year
                random_days = random.randint(0, date_range)
                lesson_date = start_date + timedelta(days=random_days)
                
                # Create lesson plan
                lesson_plan = {
                    "teacher_id": teacher_id,
                    "subject_id": subject_id,
                    "grade_level_id": grade_level_id,
                    "unit_title": template["unit_title"],
                    "lesson_title": f"{template['lesson_title']} - Lesson {i+1}",
                    "date": lesson_date,
                    "period": random.choice(["1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th"]),
                    "duration": random.choice([30, 45, 60, 90]),
                    "essential_question": template["essential_question"],
                    "do_now": template["do_now"],
                    "objectives": json.dumps(template["objectives"]),
                    "anticipatory_set": template["anticipatory_set"],
                    "direct_instruction": template["direct_instruction"],
                    "guided_practice": json.dumps(template["guided_practice"]),
                    "independent_practice": json.dumps(template["independent_practice"]),
                    "closure": template["closure"],
                    "assessment": json.dumps([template["assessment"]]),
                    "materials": json.dumps(template["materials"]),
                    "homework": template["homework"],
                    "notes": template["notes"],
                    "reflection": f"Lesson {i+1} reflection notes",
                    "next_steps": template["next_steps"],
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                
                # Insert lesson plan
                insert_query = text("""
                    INSERT INTO lesson_plans (
                        teacher_id, subject_id, grade_level_id, unit_title, lesson_title, 
                        date, period, duration, essential_question, do_now, objectives, 
                        anticipatory_set, direct_instruction, guided_practice, independent_practice,
                        closure, assessment, materials, homework, notes, reflection, next_steps,
                        created_at, updated_at
                    ) VALUES (
                        :teacher_id, :subject_id, :grade_level_id, :unit_title, :lesson_title,
                        :date, :period, :duration, :essential_question, :do_now, :objectives,
                        :anticipatory_set, :direct_instruction, :guided_practice, :independent_practice,
                        :closure, :assessment, :materials, :homework, :notes, :reflection, :next_steps,
                        :created_at, :updated_at
                    )
                """)
                
                session.execute(insert_query, lesson_plan)
                successful_inserts += 1
                
                # Progress update every 100 plans
                if (i + 1) % 100 == 0:
                    print(f"  ✅ Created {i + 1}/{target_lesson_plans} lesson plans...")
                    session.commit()  # Commit in batches
                
            except Exception as e:
                print(f"  ❌ Error creating lesson plan {i+1}: {e}")
                session.rollback()
                continue
        
        # Final commit
        session.commit()
        
        print(f"✅ Successfully created {successful_inserts} comprehensive lesson plans!")
        
        # Verify the results
        total_plans = session.execute(text("SELECT COUNT(*) FROM lesson_plans")).scalar()
        print(f"📊 Total lesson plans in database: {total_plans} records")
        
        # Show breakdown by unit
        unit_breakdown = session.execute(text("""
            SELECT unit_title, COUNT(*) as count 
            FROM lesson_plans 
            GROUP BY unit_title 
            ORDER BY count DESC
        """)).fetchall()
        
        print("📋 Lesson plans by unit:")
        for unit in unit_breakdown:
            print(f"  - {unit[0]}: {unit[1]} plans")
        
    except Exception as e:
        print(f"❌ Error seeding district lesson plans: {e}")
        session.rollback()


def main():
    """Main function to run the seeding."""
    session = SessionLocal()
    try:
        seed_district_lesson_plans(session)
    finally:
        session.close()


if __name__ == "__main__":
    main() 