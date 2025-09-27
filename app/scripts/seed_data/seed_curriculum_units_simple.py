#!/usr/bin/env python3
"""
Simple curriculum units seeding that migrates from existing PE lesson plans.
"""

import json
import random
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text


def seed_curriculum_units_simple(session: Session) -> int:
    """Seed curriculum_units table by migrating from existing PE lesson plans."""
    print("Seeding curriculum units from existing PE lesson plans...")
    
    try:
        # Check if curriculum_units already has data
        existing_count = session.execute(text("SELECT COUNT(*) FROM curriculum_units")).scalar()
        if existing_count > 0:
            print(f"  ⚠️  curriculum_units already has {existing_count} records, skipping...")
            return existing_count
        
        # Get existing data for foreign keys
        subjects = session.execute(text("SELECT id, name FROM subjects")).fetchall()
        grade_levels = session.execute(text("SELECT id FROM grade_levels")).fetchall()
        curriculum_records = session.execute(text("SELECT id, name FROM curriculum LIMIT 10")).fetchall()
        pe_lesson_plans = session.execute(text("""
            SELECT id, title, description, grade_level, duration
            FROM pe_lesson_plans
            LIMIT 100
        """)).fetchall()
        
        if not subjects or not grade_levels:
            print("Missing required data: subjects or grade levels")
            return 0
        
        subject_ids = [row[0] for row in subjects]
        grade_level_ids = [row[0] for row in grade_levels]
        curriculum_ids = [row[0] for row in curriculum_records]
        
        print(f"Found {len(subjects)} subjects, {len(grade_levels)} grade levels, {len(curriculum_records)} curriculum records, {len(pe_lesson_plans)} PE lesson plans")
        print(f"Curriculum IDs available: {curriculum_ids}")
        print(f"Subject IDs available: {subject_ids}")
        
        # Create curriculum units
        curriculum_units_data = []
        
        if pe_lesson_plans:
            print("  📋 Creating curriculum units from PE lesson plans...")
            
            # Group PE lesson plans by grade level and create units
            grade_groups = {}
            for plan in pe_lesson_plans:
                grade = plan[3] if plan[3] else 1  # Default to grade 1 if no grade level
                if grade not in grade_groups:
                    grade_groups[grade] = []
                grade_groups[grade].append(plan)
            
            unit_number = 1
            for grade_level, plans in grade_groups.items():
                # Create units based on PE lesson plans
                for i, plan in enumerate(plans[:10]):  # Limit to 10 units per grade
                    unit = {
                        "curriculum_id": random.choice(curriculum_ids) if curriculum_ids else random.choice(subject_ids),  # Use curriculum ID if available, otherwise subject ID
                        "name": f"Unit {unit_number}: {plan[1][:30]}",
                        "description": plan[2] if plan[2] else f"Unit based on {plan[1]}",
                        "sequence_number": unit_number,
                        "duration_weeks": random.randint(2, 6),
                        "learning_objectives": json.dumps([f"Learn {plan[1][:30]}", "Practice skills", "Apply knowledge"]),
                        "key_concepts": json.dumps(["Movement", "Coordination", "Teamwork"]),
                        "skill_focus": json.dumps(["Physical fitness", "Motor skills", "Social skills"]),
                        "core_activities": json.dumps([f"Activity based on {plan[1][:30]}"]),
                        "extension_activities": json.dumps(["Advanced variations"]),
                        "assessment_activities": json.dumps(["Skill demonstration", "Participation"]),
                        "equipment_needed": json.dumps(["Basic equipment"]),
                        "teaching_resources": json.dumps(["Lesson plans", "Visual aids"]),
                        "support_materials": json.dumps(["Handouts", "Videos"]),
                        "teaching_points": json.dumps(["Safety first", "Encourage participation"]),
                        "safety_considerations": json.dumps(["Proper warm-up", "Supervision"]),
                        "differentiation": json.dumps(["Adapt for different skill levels"]),
                        "completion_criteria": json.dumps(["Demonstrate skills", "Participate actively", "Show improvement"]),
                        "progress_indicators": json.dumps(["Skill demonstration", "Participation level"]),
                        "assessment_methods": json.dumps(["Observation", "Skill tests"]),
                        "version": 1,
                        "is_valid": True,
                        "created_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                    curriculum_units_data.append(unit)
                    unit_number += 1
        else:
            print("  📋 No PE lesson plans found, creating basic curriculum units...")
            # Create basic curriculum units without lesson plan references
            unit_number = 1
            for subject in subjects[:3]:  # Limit to first 3 subjects
                for grade_level_id in grade_level_ids[:5]:  # Limit to first 5 grade levels
                    unit = {
                        "curriculum_id": random.choice(curriculum_ids) if curriculum_ids else subject[0],  # Use curriculum ID if available, otherwise subject ID
                        "name": f"Unit {unit_number}: {subject[1]} - Grade {grade_level_id}",
                        "description": f"Comprehensive {subject[1]} unit for grade level {grade_level_id}",
                        "sequence_number": unit_number,
                        "duration_weeks": random.randint(2, 8),
                        "learning_objectives": json.dumps([f"Master {subject[1]} concepts", "Develop skills", "Apply knowledge"]),
                        "key_concepts": json.dumps(["Core concepts", "Practical applications"]),
                        "skill_focus": json.dumps(["Knowledge", "Understanding", "Application"]),
                        "core_activities": json.dumps([f"{subject[1]} activities"]),
                        "extension_activities": json.dumps(["Advanced projects"]),
                        "assessment_activities": json.dumps(["Tests", "Projects", "Presentations"]),
                        "equipment_needed": json.dumps(["Basic materials"]),
                        "teaching_resources": json.dumps(["Textbooks", "Digital resources"]),
                        "support_materials": json.dumps(["Worksheets", "Handouts"]),
                        "teaching_points": json.dumps(["Clear explanations", "Active learning"]),
                        "safety_considerations": json.dumps(["Classroom safety"]),
                        "differentiation": json.dumps(["Adapt for different learning styles"]),
                        "completion_criteria": json.dumps(["Complete assignments", "Demonstrate understanding", "Participate in discussions"]),
                        "progress_indicators": json.dumps(["Assignment completion", "Test scores"]),
                        "assessment_methods": json.dumps(["Tests", "Projects", "Participation"]),
                        "version": 1,
                        "is_valid": True,
                        "created_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                    curriculum_units_data.append(unit)
                    unit_number += 1
        
        # Insert curriculum units
        created_count = 0
        for i, unit in enumerate(curriculum_units_data):
            try:
                print(f"  🔍 Attempting to insert unit {i+1}/{len(curriculum_units_data)} with curriculum_id: {unit['curriculum_id']}")
                insert_query = text("""
                    INSERT INTO curriculum_units (curriculum_id, name, description, sequence_number, duration_weeks,
                                                learning_objectives, key_concepts, skill_focus, core_activities,
                                                extension_activities, assessment_activities, equipment_needed,
                                                teaching_resources, support_materials, teaching_points,
                                                safety_considerations, differentiation, completion_criteria,
                                                progress_indicators, assessment_methods, version, is_valid,
                                                created_at, updated_at)
                    VALUES (:curriculum_id, :name, :description, :sequence_number, :duration_weeks,
                           :learning_objectives, :key_concepts, :skill_focus, :core_activities,
                           :extension_activities, :assessment_activities, :equipment_needed,
                           :teaching_resources, :support_materials, :teaching_points,
                           :safety_considerations, :differentiation, :completion_criteria,
                           :progress_indicators, :assessment_methods, :version, :is_valid,
                           :created_at, :updated_at)
                    RETURNING id
                """)
                result = session.execute(insert_query, unit)
                unit_id = result.scalar()
                created_count += 1
                print(f"  ✅ Created curriculum unit: {unit['description'][:50]}... (ID: {unit_id})")
            except Exception as e:
                print(f"  ❌ Error creating curriculum unit {i+1}: {e}")
                print(f"  🔍 Unit data: curriculum_id={unit['curriculum_id']}, description={unit['description'][:50]}...")
                # Don't continue after first error to see what's wrong
                break
        
        print(f"  📊 Created {created_count} curriculum units")
        return created_count
        
    except Exception as e:
        print(f"  ❌ Error seeding curriculum units: {e}")
        import traceback
        print(f"  🔍 Full traceback: {traceback.format_exc()}")
        return 0
