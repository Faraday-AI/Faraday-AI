#!/usr/bin/env python3
"""
Seed curriculum structure tables using the same successful migration pattern.
This creates comprehensive curriculum data that references existing records.
"""

import json
import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import SessionLocal


def seed_curriculum_structure(session: Session) -> None:
    """Seed comprehensive curriculum structure data."""
    print("Seeding curriculum structure tables...")
    
    try:
        # Check existing data for foreign keys
        subjects = session.execute(text("SELECT id, name FROM subjects")).fetchall()
        grade_levels = session.execute(text("SELECT id FROM grade_levels")).fetchall()
        
        # Check if we have lesson_plans or pe_lesson_plans
        lesson_plans = session.execute(text("SELECT id, unit_title FROM lesson_plans LIMIT 100")).fetchall()
        pe_lesson_plans = session.execute(text("SELECT id, title FROM pe_lesson_plans LIMIT 100")).fetchall()
        
        if not subjects or not grade_levels:
            print("Missing required data: subjects or grade levels")
            return
        
        # Use lesson_plans if available, otherwise use pe_lesson_plans
        if lesson_plans:
            lesson_plan_ids = [row[0] for row in lesson_plans]
            lesson_plan_titles = [row[1] for row in lesson_plans]
            print(f"Found {len(subjects)} subjects, {len(grade_levels)} grade levels, {len(lesson_plans)} lesson plans")
        elif pe_lesson_plans:
            lesson_plan_ids = [row[0] for row in pe_lesson_plans]
            lesson_plan_titles = [row[1] for row in pe_lesson_plans]
            print(f"Found {len(subjects)} subjects, {len(grade_levels)} grade levels, {len(pe_lesson_plans)} PE lesson plans")
        else:
            print("Missing required data: lesson plans or PE lesson plans")
            return
        
        subject_ids = [row[0] for row in subjects]
        grade_level_ids = [row[0] for row in grade_levels]
        
        # 1. SEED CURRICULA TABLE
        print("\n📚 Seeding curriculum table...")
        curriculum_data = []
        for subject in subjects:
            for grade_level_id in grade_level_ids[:5]:  # Limit to first 5 grade levels per subject
                curriculum = {
                    "name": f"{subject[1]} Curriculum - Grade Level {grade_level_id}",
                    "description": f"Comprehensive {subject[1]} curriculum for grade level {grade_level_id}",
                    "subject_id": subject[0],
                    "grade_level_id": grade_level_id,
                    "academic_year": "2024-2025",
                    "is_active": True,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                curriculum_data.append(curriculum)
        
        # Insert curriculum
        for curriculum in curriculum_data:
            try:
                insert_query = text("""
                    INSERT INTO curriculum (name, description, subject_id, grade_level_id, 
                                        academic_year, is_active, created_at, updated_at)
                    VALUES (:name, :description, :subject_id, :grade_level_id, 
                           :academic_year, :is_active, :created_at, :updated_at)
                    RETURNING id
                """)
                result = session.execute(insert_query, curriculum)
                curriculum_id = result.scalar()
                print(f"  ✅ Created curriculum: {curriculum['name']} (ID: {curriculum_id})")
            except Exception as e:
                print(f"  ❌ Error creating curriculum: {e}")
                continue
        
        session.commit()
        
        # 2. SEED CURRICULUM UNITS TABLE
        print("\n📖 Seeding curriculum units table...")
        curriculum_units_data = []
        
        # Get created curriculum
        created_curriculum = session.execute(text("SELECT id, name FROM curriculum")).fetchall()
        
        unit_templates = [
            "Introduction and Fundamentals",
            "Core Skills Development", 
            "Advanced Applications",
            "Assessment and Review",
            "Enrichment Activities"
        ]
        
        for curriculum in created_curriculum:
            for i, unit_name in enumerate(unit_templates):
                unit = {
                    "name": f"{unit_name} - Unit {i+1}",
                    "description": f"{unit_name} unit for {curriculum[1]}",
                    "curriculum_id": curriculum[0],
                    "unit_number": i + 1,
                    "duration_weeks": random.randint(2, 6),
                    "is_active": True,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                curriculum_units_data.append(unit)
        
        # Insert curriculum units
        for unit in curriculum_units_data:
            try:
                insert_query = text("""
                    INSERT INTO curriculum_units (name, description, curriculum_id, unit_number,
                                                duration_weeks, is_active, created_at, updated_at)
                    VALUES (:name, :description, :curriculum_id, :unit_number,
                           :duration_weeks, :is_active, :created_at, :updated_at)
                    RETURNING id
                """)
                result = session.execute(insert_query, unit)
                unit_id = result.scalar()
                print(f"  ✅ Created unit: {unit['name']} (ID: {unit_id})")
            except Exception as e:
                print(f"  ❌ Error creating unit: {e}")
                continue
        
        session.commit()
        
        # 3. SEED LESSON PLAN ACTIVITIES TABLE
        print("\n🎯 Seeding lesson plan activities table...")
        
        # Check if lesson_plan_activities already has data
        existing_activities = session.execute(text("SELECT COUNT(*) FROM lesson_plan_activities")).scalar()
        if existing_activities > 0:
            print(f"  ⚠️  lesson_plan_activities already has {existing_activities} records, skipping...")
        else:
            lesson_plan_activities_data = []
            
            activity_templates = [
            {
                "name": "Warm-up Activity",
                "description": "Pre-lesson warm-up to prepare students",
                "duration_minutes": 10,
                "activity_type": "warm_up"
            },
            {
                "name": "Main Skill Practice",
                "description": "Core skill development activity",
                "duration_minutes": 25,
                "activity_type": "skill_practice"
            },
            {
                "name": "Group Activity",
                "description": "Collaborative learning activity",
                "duration_minutes": 20,
                "activity_type": "group_work"
            },
            {
                "name": "Cool-down Activity",
                "description": "Post-lesson cool-down and reflection",
                "duration_minutes": 5,
                "activity_type": "cool_down"
            }
        ]
        
            for lesson_plan_id in lesson_plan_ids[:50]:  # Limit to first 50 lesson plans
                for template in activity_templates:
                    activity = {
                        "lesson_plan_id": lesson_plan_id,
                        "name": template["name"],
                        "description": template["description"],
                        "duration_minutes": template["duration_minutes"],
                        "activity_type": template["activity_type"],
                        "materials_needed": json.dumps(["Equipment", "Space", "Instructions"]),
                        "instructions": f"Detailed instructions for {template['name']}",
                        "is_active": True,
                        "created_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                    lesson_plan_activities_data.append(activity)
            
            # Insert lesson plan activities
            for activity in lesson_plan_activities_data:
                try:
                    insert_query = text("""
                        INSERT INTO lesson_plan_activities (lesson_plan_id, name, description, 
                                                          duration_minutes, activity_type, materials_needed,
                                                          instructions, is_active, created_at, updated_at)
                        VALUES (:lesson_plan_id, :name, :description, :duration_minutes, :activity_type,
                               :materials_needed, :instructions, :is_active, :created_at, :updated_at)
                        RETURNING id
                    """)
                    result = session.execute(insert_query, activity)
                    activity_id = result.scalar()
                    print(f"  ✅ Created activity: {activity['name']} (ID: {activity_id})")
                except Exception as e:
                    print(f"  ❌ Error creating activity: {e}")
                    continue
        
        session.commit()
        
        # 4. SEED LESSON PLAN OBJECTIVES TABLE
        print("\n🎯 Seeding lesson plan objectives table...")
        
        # Check if lesson_plan_objectives already has data
        existing_objectives = session.execute(text("SELECT COUNT(*) FROM lesson_plan_objectives")).scalar()
        if existing_objectives > 0:
            print(f"  ⚠️  lesson_plan_objectives already has {existing_objectives} records, skipping...")
        else:
            lesson_plan_objectives_data = []
        
        objective_templates = [
            "Students will demonstrate understanding of key concepts",
            "Students will practice and improve specific skills",
            "Students will collaborate effectively with peers",
            "Students will apply knowledge in practical situations",
            "Students will reflect on their learning progress"
        ]
        
        for lesson_plan_id in lesson_plan_ids[:50]:  # Limit to first 50 lesson plans
            for i, objective_text in enumerate(objective_templates[:3]):  # 3 objectives per lesson
                objective = {
                    "lesson_plan_id": lesson_plan_id,
                    "objective_text": objective_text,
                    "objective_number": i + 1,
                    "is_measurable": True,
                    "assessment_criteria": f"Assessment criteria for objective {i+1}",
                    "is_active": True,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                lesson_plan_objectives_data.append(objective)
        
        # Insert lesson plan objectives
        for objective in lesson_plan_objectives_data:
            try:
                insert_query = text("""
                    INSERT INTO lesson_plan_objectives (lesson_plan_id, objective_text, objective_number,
                                                      is_measurable, assessment_criteria, is_active,
                                                      created_at, updated_at)
                    VALUES (:lesson_plan_id, :objective_text, :objective_number, :is_measurable,
                           :assessment_criteria, :is_active, :created_at, :updated_at)
                    RETURNING id
                """)
                result = session.execute(insert_query, objective)
                objective_id = result.scalar()
                print(f"  ✅ Created objective: {objective['objective_text'][:50]}... (ID: {objective_id})")
            except Exception as e:
                print(f"  ❌ Error creating objective: {e}")
                continue
        
        session.commit()
        
        # 5. SEED PE LESSON PLANS TABLE
        print("\n🏃 Seeding PE lesson plans table...")
        pe_lesson_plans_data = []
        
        # Get PE-specific lesson plans
        pe_lesson_plans = session.execute(text("""
            SELECT lp.id, lp.lesson_title, lp.unit_title, lp.grade_level_id
            FROM lesson_plans lp
            JOIN subjects s ON lp.subject_id = s.id
            WHERE s.name = 'Physical Education'
            LIMIT 100
        """)).fetchall()
        
        for pe_plan in pe_lesson_plans:
            pe_lesson_plan = {
                "lesson_plan_id": pe_plan[0],
                "pe_specific_title": f"PE: {pe_plan[1]}",
                "activity_focus": random.choice(["Cardiovascular", "Strength", "Flexibility", "Coordination", "Team Sports"]),
                "equipment_needed": json.dumps(["Cones", "Balls", "Mats", "Stopwatch"]),
                "safety_considerations": "Ensure proper warm-up and supervision",
                "modifications": "Provide modifications for different ability levels",
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            pe_lesson_plans_data.append(pe_lesson_plan)
        
        # Insert PE lesson plans
        for pe_plan in pe_lesson_plans_data:
            try:
                insert_query = text("""
                    INSERT INTO pe_lesson_plans (lesson_plan_id, pe_specific_title, activity_focus,
                                               equipment_needed, safety_considerations, modifications,
                                               is_active, created_at, updated_at)
                    VALUES (:lesson_plan_id, :pe_specific_title, :activity_focus, :equipment_needed,
                           :safety_considerations, :modifications, :is_active, :created_at, :updated_at)
                    RETURNING id
                """)
                result = session.execute(insert_query, pe_plan)
                pe_plan_id = result.scalar()
                print(f"  ✅ Created PE lesson plan: {pe_plan['pe_specific_title'][:50]}... (ID: {pe_plan_id})")
            except Exception as e:
                print(f"  ❌ Error creating PE lesson plan: {e}")
                continue
        
        session.commit()
        
        # Final verification
        print(f"\n🎉 CURRICULUM STRUCTURE SEEDING COMPLETE!")
        
        # Show results
        curriculum_count = session.execute(text("SELECT COUNT(*) FROM curriculum")).scalar()
        curriculum_units_count = session.execute(text("SELECT COUNT(*) FROM curriculum_units")).scalar()
        lesson_plan_activities_count = session.execute(text("SELECT COUNT(*) FROM lesson_plan_activities")).scalar()
        lesson_plan_objectives_count = session.execute(text("SELECT COUNT(*) FROM lesson_plan_objectives")).scalar()
        pe_lesson_plans_count = session.execute(text("SELECT COUNT(*) FROM pe_lesson_plans")).scalar()
        
        print(f"📊 Results:")
        print(f"  - Curriculum: {curriculum_count} records")
        print(f"  - Curriculum Units: {curriculum_units_count} records")
        print(f"  - Lesson Plan Activities: {lesson_plan_activities_count} records")
        print(f"  - Lesson Plan Objectives: {lesson_plan_objectives_count} records")
        print(f"  - PE Lesson Plans: {pe_lesson_plans_count} records")
        
    except Exception as e:
        print(f"❌ Error seeding curriculum structure: {e}")
        session.rollback()


def main():
    """Main function to run the seeding."""
    session = SessionLocal()
    try:
        seed_curriculum_structure(session)
    finally:
        session.close()


if __name__ == "__main__":
    main() 