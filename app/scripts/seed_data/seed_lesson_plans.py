"""
Seed lesson plans table with comprehensive lesson plan data.

This script populates the lesson_plans table with structured lesson plans
that reference existing lessons, grade levels, and teachers.
"""

from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, timedelta
import random
import json

def seed_lesson_plans(session: Session) -> None:
    """Seed the lesson_plans table with comprehensive lesson plan data."""
    print("Seeding lesson plans...")
    
    # Check if lesson_plans table exists and has data
    try:
        result = session.execute(text("SELECT COUNT(*) FROM lesson_plans")).scalar()
        if result > 0:
            print(f"Lesson plans table already has {result} records. Skipping seeding.")
            return
    except Exception as e:
        print(f"Error checking lesson_plans table: {e}")
        return
    
    # Get existing data for references
    try:
        # Get teachers
        teachers = session.execute(text("SELECT id FROM users WHERE role = 'teacher' LIMIT 10")).fetchall()
        teacher_ids = [t[0] for t in teachers] if teachers else [1]
        
        # Get subjects
        subjects = session.execute(text("SELECT id FROM subjects LIMIT 5")).fetchall()
        subject_ids = [s[0] for s in subjects] if subjects else [1]
        
        # Get grade levels
        grade_levels = session.execute(text("SELECT id FROM grade_levels LIMIT 13")).fetchall()
        grade_level_ids = [g[0] for g in grade_levels] if grade_levels else [1]
        
        print(f"Found {len(teacher_ids)} teachers, {len(subject_ids)} subjects, {len(grade_level_ids)} grade levels")
        
    except Exception as e:
        print(f"Error getting reference data: {e}")
        return
    
    # Create comprehensive lesson plans
    lesson_plans = []
    
    # Lesson plan templates for different grade levels
    plan_templates = [
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
        }
    ]
    
    # Create lesson plans for different grade levels and subjects
    for i in range(50):  # Create 50 lesson plans
        template = random.choice(plan_templates)
        teacher_id = random.choice(teacher_ids)
        subject_id = random.choice(subject_ids)
        grade_level_id = random.choice(grade_level_ids)
        
        # Generate dates for the school year
        start_date = datetime(2024, 9, 1) + timedelta(days=random.randint(0, 180))
        
        lesson_plan = {
            "teacher_id": teacher_id,
            "subject_id": subject_id,
            "grade_level_id": grade_level_id,
            "unit_title": template["unit_title"],
            "lesson_title": f"{template['lesson_title']} - Lesson {i+1}",
            "date": start_date,
            "period": random.choice(["1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th"]),
            "duration": random.choice([30, 45, 60, 90]),
            "essential_question": template["essential_question"],
            "do_now": template["do_now"],
            "objectives": json.dumps(template["objectives"], ensure_ascii=False),  # Convert list to JSON string
            "anticipatory_set": template["anticipatory_set"],
            "direct_instruction": template["direct_instruction"],
            "guided_practice": json.dumps(template["guided_practice"], ensure_ascii=False),  # Convert list to JSON string
            "independent_practice": json.dumps(template["independent_practice"], ensure_ascii=False),  # Convert list to JSON string
            "closure": template["closure"],
            "assessment": template["assessment"],
            "materials": json.dumps(template["materials"], ensure_ascii=False),  # Convert list to JSON string
            "homework": template["homework"],
            "notes": template["notes"],
            "reflection": f"Lesson {i+1} reflection notes",
            "next_steps": template["next_steps"],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        lesson_plans.append(lesson_plan)
    
    # Insert lesson plans
    for plan_data in lesson_plans:
        try:
            session.execute(
                text("""
                    INSERT INTO lesson_plans (
                        teacher_id, subject_id, grade_level_id, unit_title, lesson_title, 
                        date, period, duration, essential_question, do_now, objectives, 
                        anticipatory_set, direct_instruction, guided_practice, independent_practice,
                        closure, assessment, materials, homework, notes, reflection, next_steps,
                        created_at, updated_at
                    )
                    VALUES (
                        :teacher_id, :subject_id, :grade_level_id, :unit_title, :lesson_title,
                        :date, :period, :duration, :essential_question, :do_now, :objectives,
                        :anticipatory_set, :direct_instruction, :guided_practice, :independent_practice,
                        :closure, :assessment, :materials, :homework, :notes, :reflection, :next_steps,
                        :created_at, :updated_at
                    )
                """),
                plan_data
            )
        except Exception as e:
            print(f"Error inserting lesson plan {plan_data['lesson_title']}: {e}")
            continue
    
    # Commit the changes
    session.commit()
    
    # Verify the seeding
    try:
        result = session.execute(text("SELECT COUNT(*) FROM lesson_plans")).scalar()
        print(f"✅ Lesson plans seeded successfully: {result} records")
        
        # Show sample of inserted data
        sample_plans = session.execute(text("SELECT lesson_title, unit_title, duration FROM lesson_plans LIMIT 5")).fetchall()
        print("Sample lesson plans:")
        for plan in sample_plans:
            print(f"  - {plan[0]} ({plan[1]}) - {plan[2]} minutes")
            
    except Exception as e:
        print(f"Error verifying lesson plans: {e}")

if __name__ == "__main__":
    from app.core.database import SessionLocal
    
    session = SessionLocal()
    try:
        seed_lesson_plans(session)
    finally:
        session.close() 