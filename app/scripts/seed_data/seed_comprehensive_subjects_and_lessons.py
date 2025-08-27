#!/usr/bin/env python3
"""
Seed comprehensive subjects and lesson plans for the entire district.
This adds Drivers Ed and Health subjects, then creates lesson plans for all three subjects.
"""

import json
import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import SessionLocal


def seed_comprehensive_subjects_and_lessons(session: Session) -> None:
    """Seed comprehensive subjects and lesson plans for the entire district."""
    print("Seeding comprehensive subjects and lesson plans...")
    
    # First, add missing subjects
    print("📚 Adding missing subjects...")
    
    # Check existing subjects
    existing_subjects = session.execute(text("SELECT name FROM subjects")).fetchall()
    existing_subject_names = [row[0] for row in existing_subjects]
    print(f"Existing subjects: {existing_subject_names}")
    
    # Add missing subjects
    subjects_to_add = [
        {
            "name": "Health Education",
            "description": "Comprehensive health education including nutrition, mental health, and wellness"
        },
        {
            "name": "Drivers Education",
            "description": "Driver safety, traffic laws, and vehicle operation skills"
        }
    ]
    
    for subject in subjects_to_add:
        if subject["name"] not in existing_subject_names:
            try:
                session.execute(text("""
                    INSERT INTO subjects (name, description) 
                    VALUES (:name, :description)
                """), subject)
                print(f"  ✅ Added subject: {subject['name']}")
            except Exception as e:
                print(f"  ❌ Error adding subject {subject['name']}: {e}")
                continue
    
    session.commit()
    
    # Get all subjects including newly added ones
    all_subjects = session.execute(text("SELECT id, name FROM subjects ORDER BY id")).fetchall()
    print(f"📚 All subjects available: {[row[1] for row in all_subjects]}")
    
    # Get other required data
    educational_teachers = session.execute(text("SELECT id FROM educational_teachers")).fetchall()
    grade_levels = session.execute(text("SELECT id FROM grade_levels")).fetchall()
    
    if not educational_teachers or not grade_levels:
        print("Missing required data: teachers or grade levels")
        return
    
    teacher_ids = [row[0] for row in educational_teachers]
    subject_ids = [row[0] for row in all_subjects]
    grade_level_ids = [row[0] for row in grade_levels]
    
    print(f"Found {len(teacher_ids)} teachers, {len(subject_ids)} subjects, {len(grade_level_ids)} grade levels")
    
    # Create comprehensive lesson templates for all subjects
    lesson_templates = {
        "Physical Education": [
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
        ],
        "Health Education": [
            {
                "unit_title": "Nutrition and Wellness",
                "lesson_title": "Healthy Eating Habits",
                "essential_question": "How do our food choices affect our health?",
                "do_now": "List your favorite foods and categorize them",
                "objectives": ["Understand food groups", "Learn about balanced nutrition", "Plan healthy meals"],
                "anticipatory_set": "Show pictures of different food groups",
                "direct_instruction": "Explain the food pyramid and nutrition basics",
                "guided_practice": ["Food group sorting activity", "Meal planning exercises", "Nutrition label reading"],
                "independent_practice": ["Create a healthy meal plan", "Analyze food labels"],
                "closure": "Share healthy meal ideas",
                "assessment": "Meal planning assignment and participation",
                "materials": ["Food group charts", "Nutrition labels", "Meal planning worksheets"],
                "homework": "Plan a healthy dinner for your family",
                "notes": "Emphasize balance and moderation",
                "next_steps": "Introduce portion control concepts"
            },
            {
                "unit_title": "Mental Health and Wellness",
                "lesson_title": "Stress Management",
                "essential_question": "How can we manage stress in healthy ways?",
                "do_now": "Rate your stress level 1-10 and write one stressor",
                "objectives": ["Identify stress triggers", "Learn coping strategies", "Practice relaxation techniques"],
                "anticipatory_set": "Discuss what stress feels like",
                "direct_instruction": "Teach stress management techniques",
                "guided_practice": ["Deep breathing exercises", "Progressive muscle relaxation", "Mindfulness activities"],
                "independent_practice": ["Create stress management plan", "Practice techniques daily"],
                "closure": "Share which techniques worked best",
                "assessment": "Stress management plan and participation",
                "materials": ["Stress management worksheets", "Relaxation music", "Breathing guides"],
                "homework": "Practice one stress management technique daily",
                "notes": "Create a supportive environment",
                "next_steps": "Introduce time management skills"
            },
            {
                "unit_title": "Substance Abuse Prevention",
                "lesson_title": "Making Healthy Choices",
                "essential_question": "How do we make healthy choices about substances?",
                "do_now": "List substances that can affect health",
                "objectives": ["Understand substance effects", "Learn refusal skills", "Practice decision making"],
                "anticipatory_set": "Discuss peer pressure scenarios",
                "direct_instruction": "Teach about substance effects and refusal skills",
                "guided_practice": ["Role-play refusal scenarios", "Decision-making exercises", "Peer pressure situations"],
                "independent_practice": ["Create refusal strategy", "Practice with partners"],
                "closure": "Share refusal strategies",
                "assessment": "Role-play participation and strategy creation",
                "materials": ["Role-play scenarios", "Decision-making worksheets", "Refusal skill guides"],
                "homework": "Practice refusal skills with family",
                "notes": "Focus on empowerment and skills",
                "next_steps": "Introduce goal setting for healthy living"
            }
        ],
        "Drivers Education": [
            {
                "unit_title": "Traffic Laws and Safety",
                "lesson_title": "Understanding Traffic Signs",
                "essential_question": "How do traffic signs help keep us safe?",
                "do_now": "Draw a traffic sign you know",
                "objectives": ["Identify common traffic signs", "Understand sign meanings", "Practice sign recognition"],
                "anticipatory_set": "Show various traffic signs",
                "direct_instruction": "Explain traffic sign categories and meanings",
                "guided_practice": ["Sign identification games", "Matching signs to meanings", "Road scenario practice"],
                "independent_practice": ["Create traffic sign flashcards", "Practice with partners"],
                "closure": "Review key traffic signs",
                "assessment": "Sign identification quiz and participation",
                "materials": ["Traffic sign charts", "Flashcards", "Road scenario pictures"],
                "homework": "Identify 10 traffic signs on your way home",
                "notes": "Emphasize safety and following rules",
                "next_steps": "Introduce traffic signal meanings"
            },
            {
                "unit_title": "Vehicle Operation",
                "lesson_title": "Basic Vehicle Controls",
                "essential_question": "How do we safely operate a vehicle?",
                "do_now": "List vehicle controls you know",
                "objectives": ["Identify vehicle controls", "Understand control functions", "Practice safe operation"],
                "anticipatory_set": "Show vehicle control panel",
                "direct_instruction": "Explain vehicle control functions and safety",
                "guided_practice": ["Control identification", "Simulated operation", "Safety checklist practice"],
                "independent_practice": ["Create control diagram", "Practice with simulation"],
                "closure": "Review safety procedures",
                "assessment": "Control identification and safety knowledge",
                "materials": ["Vehicle control diagrams", "Safety checklists", "Simulation equipment"],
                "homework": "Study vehicle manual for your family car",
                "notes": "Always emphasize safety first",
                "next_steps": "Introduce pre-driving checks"
            },
            {
                "unit_title": "Defensive Driving",
                "lesson_title": "Hazard Recognition",
                "essential_question": "How can we identify and avoid driving hazards?",
                "do_now": "List potential driving hazards",
                "objectives": ["Identify common hazards", "Learn defensive strategies", "Practice hazard response"],
                "anticipatory_set": "Show hazard scenario videos",
                "direct_instruction": "Teach hazard recognition and response",
                "guided_practice": ["Hazard identification games", "Response strategy practice", "Scenario analysis"],
                "independent_practice": ["Create hazard response plan", "Practice with scenarios"],
                "closure": "Share hazard recognition strategies",
                "assessment": "Hazard identification and response planning",
                "materials": ["Hazard scenario videos", "Response strategy guides", "Practice worksheets"],
                "homework": "Practice hazard recognition while riding in car",
                "notes": "Focus on prevention and awareness",
                "next_steps": "Introduce emergency response procedures"
            }
        ]
    }
    
    # Calculate lesson plans needed per subject
    # Total: 1,200 plans across all subjects
    plans_per_subject = 400  # 400 plans per subject for comprehensive coverage
    
    print(f"🎯 Creating {plans_per_subject} lesson plans per subject...")
    
    # Generate lesson plans for each subject
    for subject_name, templates in lesson_templates.items():
        print(f"\n📚 Creating lesson plans for {subject_name}...")
        
        # Get subject ID
        subject_id = next((row[0] for row in all_subjects if row[1] == subject_name), None)
        if not subject_id:
            print(f"  ❌ Subject {subject_name} not found, skipping...")
            continue
        
        successful_inserts = 0
        for i in range(plans_per_subject):
            try:
                # Select random template for this subject
                template = random.choice(templates)
                # IMPORTANT: Teachers can teach ANY subject - they're not restricted to one subject area
                # This allows PE teachers to teach Health and Drivers Ed as well
                teacher_id = random.choice(teacher_ids)
                grade_level_id = random.choice(grade_level_ids)
                
                # Generate random date within school year
                start_date = datetime(2024, 9, 1)
                end_date = datetime(2025, 6, 15)
                date_range = (end_date - start_date).days
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
                    "reflection": f"{subject_name} Lesson {i+1} reflection notes",
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
                    print(f"  ✅ Created {i + 1}/{plans_per_subject} {subject_name} lesson plans...")
                    session.commit()  # Commit in batches
                
            except Exception as e:
                print(f"  ❌ Error creating {subject_name} lesson plan {i+1}: {e}")
                session.rollback()
                continue
        
        # Final commit for this subject
        session.commit()
        print(f"  ✅ Successfully created {successful_inserts} {subject_name} lesson plans!")
    
    # Final verification
    print(f"\n🎉 COMPREHENSIVE SEEDING COMPLETE!")
    
    # Show final results
    total_plans = session.execute(text("SELECT COUNT(*) FROM lesson_plans")).scalar()
    print(f"📊 Total lesson plans in database: {total_plans} records")
    
    # Show breakdown by subject
    subject_breakdown = session.execute(text("""
        SELECT s.name as subject_name, COUNT(*) as count 
        FROM lesson_plans lp
        JOIN subjects s ON lp.subject_id = s.id
        GROUP BY s.name, s.id
        ORDER BY count DESC
    """)).fetchall()
    
    print("📋 Lesson plans by subject:")
    for subject in subject_breakdown:
        print(f"  - {subject[0]}: {subject[1]} plans")
    
    # Show breakdown by unit
    unit_breakdown = session.execute(text("""
        SELECT unit_title, COUNT(*) as count 
        FROM lesson_plans 
        GROUP BY unit_title 
        ORDER BY count DESC
    """)).fetchall()
    
    print("\n📋 Lesson plans by unit:")
    for unit in unit_breakdown:
        print(f"  - {unit[0]}: {unit[1]} plans")


def main():
    """Main function to run the seeding."""
    session = SessionLocal()
    try:
        seed_comprehensive_subjects_and_lessons(session)
    finally:
        session.close()


if __name__ == "__main__":
    main() 