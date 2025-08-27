#!/usr/bin/env python3
"""
Recreate Comprehensive Lesson Planning System
This script recreates all essential components in the correct order:
1. Grade Levels
2. Subjects  
3. Educational Teachers
4. Comprehensive Lesson Plans
5. Curriculum Structure
"""

import json
import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import SessionLocal


def recreate_comprehensive_system(session: Session) -> None:
    """Recreate the entire comprehensive lesson planning system."""
    print("🔄 RECREATING COMPREHENSIVE LESSON PLANNING SYSTEM")
    print("=" * 60)
    
    try:
        # STEP 0: CLEAN UP EXISTING DATA (in correct order)
        print("\n🧹 STEP 0: Cleaning up existing data...")
        print("  📝 Deleting existing lesson plans...")
        session.execute(text("DELETE FROM lesson_plans"))
        print("  ✅ Lesson plans deleted")
        
        print("  👨‍🏫 Deleting existing educational teachers...")
        session.execute(text("DELETE FROM educational_teachers"))
        print("  ✅ Educational teachers deleted")
        
        print("  📖 Deleting existing subjects...")
        session.execute(text("DELETE FROM subjects"))
        print("  ✅ Subjects deleted")
        
        print("  📚 Deleting existing grade levels...")
        session.execute(text("DELETE FROM grade_levels"))
        print("  ✅ Grade levels deleted")
        
        print("  🏗️  Deleting existing curriculum structure...")
        session.execute(text("DELETE FROM curriculum_units"))
        session.execute(text("DELETE FROM curricula"))
        print("  ✅ Curriculum structure deleted")
        
        session.commit()
        print("  ✅ All existing data cleaned up successfully")
        
        # STEP 1: RECREATE GRADE LEVELS
        print("\n📚 STEP 1: Recreating Grade Levels...")
        
        grade_levels_data = [
            {"name": "K", "description": "Kindergarten"},
            {"name": "1ST", "description": "First Grade"},
            {"name": "2ND", "description": "Second Grade"},
            {"name": "3RD", "description": "Third Grade"},
            {"name": "4TH", "description": "Fourth Grade"},
            {"name": "5TH", "description": "Fifth Grade"},
            {"name": "6TH", "description": "Sixth Grade"},
            {"name": "7TH", "description": "Seventh Grade"},
            {"name": "8TH", "description": "Eighth Grade"},
            {"name": "9TH", "description": "Ninth Grade"},
            {"name": "10TH", "description": "Tenth Grade"},
            {"name": "11TH", "description": "Eleventh Grade"},
            {"name": "12TH", "description": "Twelfth Grade"}
        ]
        
        for grade_data in grade_levels_data:
            session.execute(
                text("""
                    INSERT INTO grade_levels (name, description, created_at, updated_at)
                    VALUES (:name, :description, :created_at, :updated_at)
                """),
                {
                    "name": grade_data["name"],
                    "description": grade_data["description"],
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            )
        
        session.commit()
        print(f"  ✅ Created {len(grade_levels_data)} grade levels")
        
        # STEP 2: RECREATE SUBJECTS
        print("\n📖 STEP 2: Recreating Subjects...")
        session.execute(text("DELETE FROM subjects"))
        
        subjects_data = [
            {"name": "Physical Education", "description": "Physical education and fitness curriculum"},
            {"name": "Health Education", "description": "Comprehensive health education including nutrition, mental health, and wellness"},
            {"name": "Drivers Education", "description": "Driver safety, traffic laws, and vehicle operation skills"}
        ]
        
        for subject_data in subjects_data:
            session.execute(
                text("""
                    INSERT INTO subjects (name, description, created_at, updated_at)
                    VALUES (:name, :description, :created_at, :updated_at)
                """),
                {
                    **subject_data,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            )
        
        session.commit()
        print(f"  ✅ Created {len(subjects_data)} subjects")
        
        # STEP 3: RECREATE EDUCATIONAL TEACHERS
        print("\n👨‍🏫 STEP 3: Recreating Educational Teachers...")
        session.execute(text("DELETE FROM educational_teachers"))
        
        # Get existing dashboard users
        dashboard_users = session.execute(text("SELECT id, full_name FROM dashboard_users WHERE role = 'TEACHER' ORDER BY id")).fetchall()
        if not dashboard_users:
            print("  ❌ No TEACHER users found in dashboard_users table.")
            return
        
        print(f"  📋 Found {len(dashboard_users)} TEACHER users to reference...")
        
        teachers_data = [
            {
                "name": "Sarah Johnson",
                "school": "Lincoln Elementary",
                "department": "Physical Education",
                "subjects": json.dumps(["Physical Education", "Health"]),
                "grade_levels": json.dumps(["K", "1ST", "2ND", "3RD", "4TH", "5TH"]),
                "certifications": json.dumps(["PE Teacher Certification", "First Aid"]),
                "specialties": json.dumps(["Elementary PE", "Adaptive PE"]),
                "bio": "Experienced elementary PE teacher with 8 years of experience.",
                "status": "ACTIVE",
                "is_active": True
            },
            {
                "name": "Michael Chen",
                "school": "Riverside Middle School",
                "department": "Physical Education",
                "subjects": json.dumps(["Physical Education", "Sports"]),
                "grade_levels": json.dumps(["6TH", "7TH", "8TH"]),
                "certifications": json.dumps(["PE Teacher Certification", "Coaching License"]),
                "specialties": json.dumps(["Team Sports", "Fitness"]),
                "bio": "Middle school PE teacher and basketball coach.",
                "status": "ACTIVE",
                "is_active": True
            },
            {
                "name": "Emily Rodriguez",
                "school": "Central High School",
                "department": "Physical Education",
                "subjects": json.dumps(["Physical Education", "Health Science"]),
                "grade_levels": json.dumps(["9TH", "10TH", "11TH", "12TH"]),
                "certifications": json.dumps(["PE Teacher Certification", "Health Education"]),
                "specialties": json.dumps(["High School PE", "Health Education"]),
                "bio": "High school PE teacher with focus on health and wellness.",
                "status": "ACTIVE",
                "is_active": True
            },
            {
                "name": "David Thompson",
                "school": "Oakwood Elementary",
                "department": "Physical Education",
                "subjects": json.dumps(["Physical Education"]),
                "grade_levels": json.dumps(["K", "1ST", "2ND", "3RD", "4TH", "5TH"]),
                "certifications": json.dumps(["PE Teacher Certification"]),
                "specialties": json.dumps(["Elementary PE", "Movement Education"]),
                "bio": "Elementary PE teacher specializing in fundamental movement skills.",
                "status": "ACTIVE",
                "is_active": True
            },
            {
                "name": "Lisa Park",
                "school": "Maple Middle School",
                "department": "Physical Education",
                "subjects": json.dumps(["Physical Education", "Dance"]),
                "grade_levels": json.dumps(["6TH", "7TH", "8TH"]),
                "certifications": json.dumps(["PE Teacher Certification", "Dance Instruction"]),
                "specialties": json.dumps(["Dance", "Creative Movement"]),
                "bio": "Middle school PE teacher with dance and creative movement expertise.",
                "status": "ACTIVE",
                "is_active": True
            }
        ]
        
        # Create educational teachers, referencing existing dashboard users
        for i, teacher_data in enumerate(teachers_data):
            try:
                user_id = dashboard_users[i % len(dashboard_users)][0]  # Cycle through available users
                
                insert_query = text("""
                    INSERT INTO educational_teachers (
                        user_id, name, school, department, subjects, grade_levels, certifications,
                        specialties, bio, status, is_active, created_at, updated_at
                    ) VALUES (
                        :user_id, :name, :school, :department, :subjects, :grade_levels, :certifications,
                        :specialties, :bio, :status, :is_active, :created_at, :updated_at
                    ) RETURNING id
                """)
                
                result = session.execute(insert_query, {
                    **teacher_data,
                    "user_id": user_id,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                })
                
                teacher_id = result.scalar()
                print(f"  ✅ Created teacher {i+1}/5: {teacher_data['name']} (ID: {teacher_id})")
                
            except Exception as e:
                print(f"  ❌ Error creating teacher {teacher_data['name']}: {e}")
                continue
        
        session.commit()
        print(f"  ✅ Successfully created {len(teachers_data)} educational teachers!")
        
        # STEP 4: RECREATE COMPREHENSIVE LESSON PLANS
        print("\n📝 STEP 4: Recreating Comprehensive Lesson Plans...")
        session.execute(text("DELETE FROM lesson_plans"))
        
        # Get the data we just created
        educational_teachers = session.execute(text("SELECT id FROM educational_teachers")).fetchall()
        subjects = session.execute(text("SELECT id, name FROM subjects")).fetchall()
        grade_levels = session.execute(text("SELECT id FROM grade_levels")).fetchall()
        
        if not educational_teachers or not subjects or not grade_levels:
            print("  ❌ Missing required data: teachers, subjects, or grade levels")
            return
        
        teacher_ids = [row[0] for row in educational_teachers]
        subject_ids = [row[0] for row in subjects]
        grade_level_ids = [row[0] for row in grade_levels]
        
        print(f"  📋 Found {len(teacher_ids)} teachers, {len(subjects)} subjects, {len(grade_level_ids)} grade levels")
        
        # Create comprehensive lesson plan templates for all subjects
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
                }
            ]
        }
        
        # Calculate lesson plans needed per subject
        plans_per_subject = 400  # 400 plans per subject for comprehensive coverage
        total_lesson_plans = plans_per_subject * len(subjects)
        
        print(f"  🎯 Creating {total_lesson_plans} comprehensive lesson plans...")
        
        # Generate lesson plans for each subject
        successful_inserts = 0
        for subject_name, templates in lesson_templates.items():
            print(f"    📚 Creating lesson plans for {subject_name}...")
            
            # Get subject ID
            subject_id = next((row[0] for row in subjects if row[1] == subject_name), None)
            if not subject_id:
                print(f"      ❌ Subject {subject_name} not found, skipping...")
                continue
            
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
                        print(f"      ✅ Created {i + 1}/{plans_per_subject} {subject_name} lesson plans...")
                        session.commit()  # Commit in batches
                    
                except Exception as e:
                    print(f"      ❌ Error creating {subject_name} lesson plan {i+1}: {e}")
                    session.rollback()
                    continue
            
            # Final commit for this subject
            session.commit()
            print(f"      ✅ Successfully created {plans_per_subject} {subject_name} lesson plans!")
        
        # STEP 5: SEED CURRICULUM STRUCTURE
        print("\n🏗️  STEP 5: Seeding Curriculum Structure...")
        
        # Create curricula
        curricula_data = []
        for subject in subjects:
            for grade_level_id in grade_level_ids[:5]:  # Limit to first 5 grade levels per subject
                # Get grade level name for display
                grade_level_name = session.execute(
                    text("SELECT name FROM grade_levels WHERE id = :id"), 
                    {"id": grade_level_id}
                ).scalar()
                
                curriculum = {
                    "name": f"{subject[1]} Curriculum - {grade_level_name}",
                    "description": f"Comprehensive {subject[1]} curriculum for {grade_level_name}",
                    "grade_level": grade_level_name,
                    "academic_year": "2024-2025",
                    "learning_standards": json.dumps(["Standard 1", "Standard 2", "Standard 3"]),
                    "learning_objectives": json.dumps(["Objective 1", "Objective 2", "Objective 3"]),
                    "core_competencies": json.dumps(["Competency 1", "Competency 2"]),
                    "unit_data": json.dumps({"units": 5, "duration_weeks": 18}),
                    "progression_path": json.dumps({"beginner": "Basic skills", "intermediate": "Advanced skills", "expert": "Mastery"}),
                    "time_allocation": json.dumps({"weekly_hours": 2, "total_hours": 36}),
                    "assessment_criteria": json.dumps(["Participation", "Skill demonstration", "Knowledge assessment"]),
                    "evaluation_methods": json.dumps(["Observation", "Performance tasks", "Written assessments"]),
                    "version": 1,
                    "is_valid": True,
                    "is_active": True,
                    "status": "ACTIVE",
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                curricula_data.append(curriculum)
        
        # Insert curricula
        for curriculum in curricula_data:
            try:
                insert_query = text("""
                    INSERT INTO curricula (
                        name, description, grade_level, academic_year, learning_standards,
                        learning_objectives, core_competencies, unit_data, progression_path,
                        time_allocation, assessment_criteria, evaluation_methods, version,
                        is_valid, is_active, status, created_at, updated_at
                    ) VALUES (
                        :name, :description, :grade_level, :academic_year, :learning_standards,
                        :learning_objectives, :core_competencies, :unit_data, :progression_path,
                        :time_allocation, :assessment_criteria, :evaluation_methods, :version,
                        :is_valid, :is_active, :status, :created_at, :updated_at
                    ) RETURNING id
                """)
                result = session.execute(insert_query, curriculum)
                curriculum_id = result.scalar()
                print(f"  ✅ Created curriculum: {curriculum['name'][:50]}... (ID: {curriculum_id})")
            except Exception as e:
                print(f"  ❌ Error creating curriculum: {e}")
                continue
        
        session.commit()
        
        # Create curriculum units
        created_curricula = session.execute(text("SELECT id, name FROM curricula")).fetchall()
        curriculum_units_data = []
        
        unit_templates = [
            "Introduction and Fundamentals",
            "Core Skills Development", 
            "Advanced Applications",
            "Assessment and Review",
            "Enrichment Activities"
        ]
        
        for curriculum in created_curricula:
            for i, unit_name in enumerate(unit_templates):
                unit = {
                    "name": f"{unit_name} - Unit {i+1}",
                    "description": f"{unit_name} unit for {curriculum[1]}",
                    "curriculum_id": curriculum[0],
                    "sequence_number": i + 1,
                    "duration_weeks": random.randint(2, 6),
                    "learning_objectives": json.dumps([f"Objective {j+1} for {unit_name}" for j in range(3)]),
                    "key_concepts": json.dumps([f"Concept {j+1} for {unit_name}" for j in range(3)]),
                    "skill_focus": json.dumps([f"Skill {j+1} for {unit_name}" for j in range(2)]),
                    "core_activities": json.dumps([f"Activity {j+1} for {unit_name}" for j in range(3)]),
                    "completion_criteria": json.dumps([f"Criterion {j+1} for {unit_name}" for j in range(2)]),
                    "version": 1,
                    "is_valid": True,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                curriculum_units_data.append(unit)
        
        # Insert curriculum units
        for unit in curriculum_units_data:
            try:
                insert_query = text("""
                    INSERT INTO curriculum_units (
                        name, description, curriculum_id, sequence_number, duration_weeks,
                        learning_objectives, key_concepts, skill_focus, core_activities,
                        completion_criteria, version, is_valid, created_at, updated_at
                    ) VALUES (
                        :name, :description, :curriculum_id, :sequence_number, :duration_weeks,
                        :learning_objectives, :key_concepts, :skill_focus, :core_activities,
                        :completion_criteria, :version, :is_valid, :created_at, :updated_at
                    ) RETURNING id
                """)
                result = session.execute(insert_query, unit)
                unit_id = result.scalar()
                print(f"  ✅ Created unit: {unit['name']} (ID: {unit_id})")
            except Exception as e:
                print(f"  ❌ Error creating unit: {e}")
                continue
        
        session.commit()
        
        # FINAL VERIFICATION
        print(f"\n🎉 COMPREHENSIVE SYSTEM RECREATION COMPLETE!")
        print("=" * 60)
        
        # Show final results
        grade_levels_count = session.execute(text("SELECT COUNT(*) FROM grade_levels")).scalar()
        subjects_count = session.execute(text("SELECT COUNT(*) FROM subjects")).scalar()
        educational_teachers_count = session.execute(text("SELECT COUNT(*) FROM educational_teachers")).scalar()
        lesson_plans_count = session.execute(text("SELECT COUNT(*) FROM lesson_plans")).scalar()
        curricula_count = session.execute(text("SELECT COUNT(*) FROM curricula")).scalar()
        curriculum_units_count = session.execute(text("SELECT COUNT(*) FROM curriculum_units")).scalar()
        
        print(f"📊 FINAL RESULTS:")
        print(f"  - Grade Levels: {grade_levels_count} records")
        print(f"  - Subjects: {subjects_count} records")
        print(f"  - Educational Teachers: {educational_teachers_count} records")
        print(f"  - Lesson Plans: {lesson_plans_count} records")
        print(f"  - Curricula: {curricula_count} records")
        print(f"  - Curriculum Units: {curriculum_units_count} records")
        
        # Show lesson plans breakdown by subject
        subject_breakdown = session.execute(text("""
            SELECT s.name as subject_name, COUNT(*) as count 
            FROM lesson_plans lp
            JOIN subjects s ON lp.subject_id = s.id
            GROUP BY s.name, s.id
            ORDER BY count DESC
        """)).fetchall()
        
        print(f"\n📋 Lesson Plans by Subject:")
        for subject in subject_breakdown:
            print(f"  - {subject[0]}: {subject[1]} plans")
        
        print(f"\n🎯 Total Lesson Plans: {lesson_plans_count} records")
        print(f"✅ District coverage: COMPREHENSIVE!")
        
    except Exception as e:
        print(f"❌ Error during system recreation: {e}")
        session.rollback()


def main():
    """Main function to run the recreation."""
    session = SessionLocal()
    try:
        recreate_comprehensive_system(session)
    finally:
        session.close()


if __name__ == "__main__":
    main() 