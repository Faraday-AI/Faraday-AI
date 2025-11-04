#!/usr/bin/env python3
"""
Comprehensive Health Curriculum Seeding Script
Creates a complete health education curriculum for both teacher and district versions.
Available for grades K-12 with age-appropriate content and standards alignment.
"""

import os
from datetime import datetime, timedelta
from uuid import UUID
from faker import Faker
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Initialize Faker for realistic data
fake = Faker()

# Database connection details (must be provided via environment)
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL must be set in the environment")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- Helper Functions ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_first_teacher_id(session):
    """Fetches the ID of the first teacher from teacher_registrations."""
    result = session.execute(text("SELECT id FROM teacher_registrations LIMIT 1")).fetchone()
    if result:
        return str(result[0])
    return None

def create_health_curriculum_units(session):
    """Creates comprehensive health curriculum units for K-12."""
    print("1️⃣ Creating health curriculum database tables...")
    
    # Run the health curriculum migration first
    migration_path = '/app/migrations/add_health_curriculum_tables.sql'
    if os.path.exists(migration_path):
        with open(migration_path, 'r') as f:
            migration_sql = f.read()
            session.execute(text(migration_sql))
        session.commit()
        print("   ✅ Health curriculum tables created")
    else:
        print("   ⚠️  Migration file not found, skipping table creation")
    
    print("3️⃣ Creating health curriculum units...")
    
    # Comprehensive K-12 Health Curriculum Units
    units_data = [
        # Elementary School (K-5)
        {
            "unit_number": 1,
            "unit_title": "Personal Health and Hygiene",
            "description": "Basic personal hygiene, handwashing, dental care, and healthy habits.",
            "grade_level": "K-2",
            "duration_weeks": 2,
            "prerequisites": [],
            "learning_outcomes": ["Practice proper handwashing", "Understand dental hygiene", "Develop healthy habits"],
            "state_standards": ["HE.1.1", "HE.1.2", "HE.1.3"],
            "national_standards": ["NHES.1", "NHES.2"],
            "is_core_unit": True,
        },
        {
            "unit_number": 2,
            "unit_title": "Nutrition and Healthy Eating",
            "description": "Introduction to healthy foods, food groups, and making healthy choices.",
            "grade_level": "K-2",
            "duration_weeks": 3,
            "prerequisites": ["Unit 1"],
            "learning_outcomes": ["Identify food groups", "Make healthy food choices", "Understand portion sizes"],
            "state_standards": ["HE.2.1", "HE.2.2"],
            "national_standards": ["NHES.3", "NHES.4"],
            "is_core_unit": True,
        },
        {
            "unit_number": 3,
            "unit_title": "Physical Activity and Exercise",
            "description": "Importance of physical activity, different types of exercise, and staying active.",
            "grade_level": "K-2",
            "duration_weeks": 2,
            "prerequisites": ["Unit 1"],
            "learning_outcomes": ["Understand benefits of exercise", "Participate in physical activities", "Develop active lifestyle"],
            "state_standards": ["HE.3.1", "HE.3.2"],
            "national_standards": ["NHES.5", "NHES.6"],
            "is_core_unit": True,
        },
        {
            "unit_number": 4,
            "unit_title": "Safety and Injury Prevention",
            "description": "Basic safety rules, stranger danger, and injury prevention strategies.",
            "grade_level": "K-2",
            "duration_weeks": 2,
            "prerequisites": ["Unit 1"],
            "learning_outcomes": ["Follow safety rules", "Identify safe behaviors", "Prevent common injuries"],
            "state_standards": ["HE.4.1", "HE.4.2"],
            "national_standards": ["NHES.7", "NHES.8"],
            "is_core_unit": True,
        },
        
        # Upper Elementary (3-5)
        {
            "unit_number": 5,
            "unit_title": "Mental Health and Emotions",
            "description": "Understanding emotions, stress management, and building resilience.",
            "grade_level": "3-5",
            "duration_weeks": 3,
            "prerequisites": ["Unit 1", "Unit 2"],
            "learning_outcomes": ["Identify emotions", "Manage stress", "Build resilience"],
            "state_standards": ["HE.5.1", "HE.5.2", "HE.5.3"],
            "national_standards": ["NHES.1", "NHES.2", "NHES.3"],
            "is_core_unit": True,
        },
        {
            "unit_number": 6,
            "unit_title": "Substance Abuse Prevention",
            "description": "Understanding harmful substances, peer pressure, and refusal skills.",
            "grade_level": "3-5",
            "duration_weeks": 2,
            "prerequisites": ["Unit 5"],
            "learning_outcomes": ["Identify harmful substances", "Resist peer pressure", "Practice refusal skills"],
            "state_standards": ["HE.6.1", "HE.6.2"],
            "national_standards": ["NHES.4", "NHES.5"],
            "is_core_unit": True,
        },
        {
            "unit_number": 7,
            "unit_title": "Growth and Development",
            "description": "Understanding body changes, puberty, and healthy development.",
            "grade_level": "3-5",
            "duration_weeks": 2,
            "prerequisites": ["Unit 1"],
            "learning_outcomes": ["Understand body changes", "Develop positive body image", "Practice self-care"],
            "state_standards": ["HE.7.1", "HE.7.2"],
            "national_standards": ["NHES.6", "NHES.7"],
            "is_core_unit": True,
        },
        
        # Middle School (6-8)
        {
            "unit_number": 8,
            "unit_title": "Adolescent Health",
            "description": "Comprehensive adolescent health including physical, mental, and social aspects.",
            "grade_level": "6-8",
            "duration_weeks": 4,
            "prerequisites": ["Unit 5", "Unit 6", "Unit 7"],
            "learning_outcomes": ["Understand adolescent development", "Make healthy decisions", "Build positive relationships"],
            "state_standards": ["HE.8.1", "HE.8.2", "HE.8.3"],
            "national_standards": ["NHES.1", "NHES.2", "NHES.3", "NHES.4"],
            "is_core_unit": True,
        },
        {
            "unit_number": 9,
            "unit_title": "Sexual Health Education",
            "description": "Age-appropriate sexual health education including anatomy, reproduction, and relationships.",
            "grade_level": "6-8",
            "duration_weeks": 3,
            "prerequisites": ["Unit 8"],
            "learning_outcomes": ["Understand reproductive health", "Build healthy relationships", "Practice consent"],
            "state_standards": ["HE.9.1", "HE.9.2"],
            "national_standards": ["NHES.5", "NHES.6"],
            "is_core_unit": True,
        },
        {
            "unit_number": 10,
            "unit_title": "Mental Health and Wellness",
            "description": "Advanced mental health topics including depression, anxiety, and coping strategies.",
            "grade_level": "6-8",
            "duration_weeks": 3,
            "prerequisites": ["Unit 5", "Unit 8"],
            "learning_outcomes": ["Recognize mental health issues", "Develop coping strategies", "Seek help when needed"],
            "state_standards": ["HE.10.1", "HE.10.2"],
            "national_standards": ["NHES.7", "NHES.8"],
            "is_core_unit": True,
        },
        
        # High School (9-12)
        {
            "unit_number": 11,
            "unit_title": "Advanced Nutrition and Wellness",
            "description": "Advanced nutrition science, meal planning, and wellness strategies.",
            "grade_level": "9-12",
            "duration_weeks": 4,
            "prerequisites": ["Unit 2", "Unit 5"],
            "learning_outcomes": ["Understand nutrition science", "Plan balanced meals", "Develop wellness strategies"],
            "state_standards": ["HE.11.1", "HE.11.2", "HE.11.3"],
            "national_standards": ["NHES.1", "NHES.2", "NHES.3"],
            "is_core_unit": True,
        },
        {
            "unit_number": 12,
            "unit_title": "Substance Abuse and Addiction",
            "description": "Comprehensive study of substance abuse, addiction, and prevention strategies.",
            "grade_level": "9-12",
            "duration_weeks": 3,
            "prerequisites": ["Unit 6", "Unit 8"],
            "learning_outcomes": ["Understand addiction", "Recognize risk factors", "Develop prevention strategies"],
            "state_standards": ["HE.12.1", "HE.12.2"],
            "national_standards": ["NHES.4", "NHES.5"],
            "is_core_unit": True,
        },
        {
            "unit_number": 13,
            "unit_title": "Sexual and Reproductive Health",
            "description": "Comprehensive sexual health education including STIs, contraception, and healthy relationships.",
            "grade_level": "9-12",
            "duration_weeks": 4,
            "prerequisites": ["Unit 9", "Unit 8"],
            "learning_outcomes": ["Understand reproductive health", "Prevent STIs", "Make informed decisions"],
            "state_standards": ["HE.13.1", "HE.13.2", "HE.13.3"],
            "national_standards": ["NHES.6", "NHES.7"],
            "is_core_unit": True,
        },
        {
            "unit_number": 14,
            "unit_title": "Mental Health and Crisis Intervention",
            "description": "Advanced mental health topics including crisis intervention and suicide prevention.",
            "grade_level": "9-12",
            "duration_weeks": 3,
            "prerequisites": ["Unit 10", "Unit 8"],
            "learning_outcomes": ["Recognize mental health crises", "Intervene appropriately", "Prevent suicide"],
            "state_standards": ["HE.14.1", "HE.14.2"],
            "national_standards": ["NHES.8", "NHES.9"],
            "is_core_unit": True,
        },
        {
            "unit_number": 15,
            "unit_title": "Health Advocacy and Community Health",
            "description": "Health advocacy, community health issues, and public health policy.",
            "grade_level": "9-12",
            "duration_weeks": 3,
            "prerequisites": ["Unit 11", "Unit 12", "Unit 13", "Unit 14"],
            "learning_outcomes": ["Advocate for health", "Understand community health", "Engage in public health"],
            "state_standards": ["HE.15.1", "HE.15.2"],
            "national_standards": ["NHES.10"],
            "is_core_unit": True,
        }
    ]

    for unit_data in units_data:
        session.execute(
            text(
                """
                INSERT INTO health_curriculum_units (
                    unit_number, unit_title, description, grade_level, duration_weeks,
                    prerequisites, learning_outcomes, state_standards, national_standards,
                    is_core_unit
                ) VALUES (
                    :unit_number, :unit_title, :description, :grade_level, :duration_weeks,
                    :prerequisites, :learning_outcomes, :state_standards, :national_standards,
                    :is_core_unit
                )
                """
            ),
            unit_data,
        )
    session.commit()
    print(f"   ✅ Created {len(units_data)} health curriculum units")

def create_lesson_plans_for_unit(session, teacher_id: UUID, unit_number: int, num_lessons: int):
    """Generates and inserts lesson plans for a specific health curriculum unit."""
    unit = session.execute(
        text("SELECT id, unit_title, grade_level FROM health_curriculum_units WHERE unit_number = :unit_number"),
        {"unit_number": unit_number},
    ).fetchone()

    if not unit:
        print(f"   ⚠️  Unit {unit_number} not found, skipping lesson plan creation.")
        return

    unit_id, unit_title, grade_level = unit

    lesson_types = ["classroom", "laboratory", "discussion", "project", "assessment"]
    difficulty_levels = ["beginner", "intermediate", "advanced"]

    for i in range(1, num_lessons + 1):
        title = f"{unit_title} - Lesson {i}: {fake.sentence(nb_words=4).replace('.', '')}"
        description = fake.paragraph(nb_sentences=3)
        duration = fake.random_int(min=30, max=90)
        lesson_type = fake.random_element(lesson_types)
        difficulty = fake.random_element(difficulty_levels)
        objectives = [fake.sentence(nb_words=6) for _ in range(3)]
        materials = [fake.word() for _ in range(3)]
        equipment = [fake.word() for _ in range(2)]
        health_considerations = [fake.sentence(nb_words=5)]
        assessment_methods = [fake.word() for _ in range(2)]
        state_standards = [f"HE.{unit_number}.{fake.random_int(min=1, max=3)}"]
        national_standards = [f"NHES.{fake.random_int(min=1, max=10)}"]

        session.execute(
            text(
                """
                INSERT INTO health_lesson_plans (
                    teacher_id, curriculum_unit_id, lesson_number, title, description,
                    grade_level, duration_minutes, lesson_type, difficulty_level,
                    learning_objectives, materials_needed, equipment_needed,
                    health_considerations, assessment_methods, state_standards,
                    national_standards, is_template, is_public
                ) VALUES (
                    :teacher_id, :curriculum_unit_id, :lesson_number, :title, :description,
                    :grade_level, :duration_minutes, :lesson_type, :difficulty_level,
                    :learning_objectives, :materials_needed, :equipment_needed,
                    :health_considerations, :assessment_methods, :state_standards,
                    :national_standards, TRUE, TRUE
                )
                """
            ),
            {
                "teacher_id": teacher_id,
                "curriculum_unit_id": unit_id,
                "lesson_number": i,
                "title": title,
                "description": description,
                "grade_level": grade_level,
                "duration_minutes": duration,
                "lesson_type": lesson_type,
                "difficulty_level": difficulty,
                "learning_objectives": objectives,
                "materials_needed": materials,
                "equipment_needed": equipment,
                "health_considerations": health_considerations,
                "assessment_methods": assessment_methods,
                "state_standards": state_standards,
                "national_standards": national_standards,
            },
        )
    session.commit()
    print(f"   ✅ Created {num_lessons} lesson plans for Unit {unit_number}")

def create_health_safety_protocols(session):
    """Creates health education safety protocols."""
    print("5️⃣ Creating health safety protocols...")
    protocols_data = [
        {
            "protocol_name": "Laboratory Safety Procedures",
            "protocol_type": "laboratory_safety",
            "description": "Safety procedures for health education laboratory activities.",
            "steps": ["Wear safety equipment", "Follow instructions", "Clean up properly", "Report incidents"],
            "safety_checklist": ["Safety goggles", "Lab coats", "First aid kit", "Emergency contacts"],
            "required_equipment": ["Safety goggles", "Lab coats", "First aid kit"],
            "applicable_lesson_types": ["laboratory"],
            "grade_levels": ["6-12"],
        },
        {
            "protocol_name": "Food Safety Guidelines",
            "protocol_type": "food_safety",
            "description": "Guidelines for safe food handling and preparation activities.",
            "steps": ["Wash hands", "Clean surfaces", "Check expiration dates", "Store properly"],
            "safety_checklist": ["Hand washing", "Surface cleaning", "Temperature checks"],
            "required_equipment": ["Hand sanitizer", "Cleaning supplies", "Thermometer"],
            "applicable_lesson_types": ["laboratory", "classroom"],
            "grade_levels": ["K-12"],
        },
        {
            "protocol_name": "Field Trip Safety",
            "protocol_type": "field_trip",
            "description": "Safety procedures for health education field trips.",
            "steps": ["Obtain permissions", "Prepare emergency contacts", "Conduct safety briefing", "Maintain supervision"],
            "safety_checklist": ["Permission slips", "Emergency contacts", "First aid kit", "Student lists"],
            "required_equipment": ["First aid kit", "Emergency contacts", "Student lists"],
            "applicable_lesson_types": ["field_trip"],
            "grade_levels": ["K-12"],
        },
        {
            "protocol_name": "Mental Health Crisis Response",
            "protocol_type": "emergency",
            "description": "Procedures for responding to mental health crises in the classroom.",
            "steps": ["Assess situation", "Ensure safety", "Contact support", "Follow up"],
            "safety_checklist": ["Crisis contacts", "Support resources", "Documentation"],
            "required_equipment": ["Crisis hotline numbers", "Support resources"],
            "applicable_lesson_types": ["classroom", "discussion"],
            "grade_levels": ["6-12"],
        }
    ]
    
    for protocol_data in protocols_data:
        session.execute(
            text(
                """
                INSERT INTO health_safety_protocols (
                    protocol_name, protocol_type, description, steps,
                    safety_checklist, required_equipment, applicable_lesson_types,
                    grade_levels
                ) VALUES (
                    :protocol_name, :protocol_type, :description, :steps,
                    :safety_checklist, :required_equipment, :applicable_lesson_types,
                    :grade_levels
                )
                """
            ),
            protocol_data,
        )
    session.commit()
    print(f"   ✅ Created {len(protocols_data)} health safety protocols")

def create_health_assessment_rubrics(session):
    """Creates health education assessment rubrics."""
    print("6️⃣ Creating health assessment rubrics...")
    rubrics_data = [
        {
            "rubric_name": "Health Knowledge Assessment",
            "assessment_type": "written_test",
            "grade_level": "K-12",
            "description": "Assessment of health knowledge and understanding.",
            "criteria": ["Knowledge accuracy", "Understanding depth", "Application ability"],
            "scoring_scale": "percentage",
            "passing_score": 80.0,
            "time_limit_minutes": 45,
        },
        {
            "rubric_name": "Health Project Evaluation",
            "assessment_type": "project",
            "grade_level": "3-12",
            "description": "Evaluation of health-related projects and presentations.",
            "criteria": ["Content accuracy", "Creativity", "Presentation quality", "Research depth"],
            "scoring_scale": "1-4",
            "passing_score": 2.5,
            "time_limit_minutes": 0,
        },
        {
            "rubric_name": "Health Behavior Assessment",
            "assessment_type": "portfolio",
            "grade_level": "6-12",
            "description": "Assessment of health behavior changes and goal achievement.",
            "criteria": ["Goal setting", "Progress tracking", "Behavior change", "Reflection quality"],
            "scoring_scale": "1-5",
            "passing_score": 3.0,
            "time_limit_minutes": 0,
        },
        {
            "rubric_name": "Peer Health Education Assessment",
            "assessment_type": "peer_assessment",
            "grade_level": "9-12",
            "description": "Peer evaluation of health education presentations and teaching.",
            "criteria": ["Teaching effectiveness", "Content accuracy", "Engagement", "Communication"],
            "scoring_scale": "1-4",
            "passing_score": 2.5,
            "time_limit_minutes": 0,
        }
    ]
    
    for rubric_data in rubrics_data:
        session.execute(
            text(
                """
                INSERT INTO health_assessment_rubrics (
                    rubric_name, assessment_type, grade_level, description,
                    criteria, scoring_scale, passing_score, time_limit_minutes
                ) VALUES (
                    :rubric_name, :assessment_type, :grade_level, :description,
                    :criteria, :scoring_scale, :passing_score, :time_limit_minutes
                )
                """
            ),
            rubric_data,
        )
    session.commit()
    print(f"   ✅ Created {len(rubrics_data)} health assessment rubrics")

def create_sample_health_equipment(session):
    """Creates sample health education equipment and supplies."""
    print("7️⃣ Creating sample health equipment...")
    equipment_data = [
        {
            "equipment_name": "Anatomy Models",
            "equipment_type": "Educational Models",
            "category": "educational",
            "description": "Human anatomy models for health education",
            "manufacturer": "Educational Supply Co",
            "model_number": "ANAT-001",
            "purchase_date": "2023-01-15",
            "warranty_expiry": "2025-01-15",
            "maintenance_due_date": "2024-07-15",
            "last_maintenance_date": "2024-01-15",
            "location": "Health Lab A",
        },
        {
            "equipment_name": "First Aid Kit",
            "equipment_type": "Safety Equipment",
            "category": "safety",
            "description": "Comprehensive first aid kit for health education",
            "manufacturer": "Safety First",
            "model_number": "FAK-100",
            "purchase_date": "2023-08-20",
            "warranty_expiry": "2024-08-20",
            "maintenance_due_date": "2024-02-20",
            "last_maintenance_date": "2024-02-20",
            "location": "Health Classroom",
        },
        {
            "equipment_name": "Digital Scale",
            "equipment_type": "Measurement Equipment",
            "category": "laboratory",
            "description": "Digital scale for nutrition and health measurements",
            "manufacturer": "Precision Scales",
            "model_number": "DS-500",
            "purchase_date": "2023-03-10",
            "warranty_expiry": "2025-03-10",
            "maintenance_due_date": "2024-09-10",
            "last_maintenance_date": "2024-03-10",
            "location": "Health Lab B",
        },
        {
            "equipment_name": "Interactive Health Software",
            "equipment_type": "Educational Software",
            "category": "technology",
            "description": "Interactive software for health education activities",
            "manufacturer": "EduTech Solutions",
            "model_number": "IHS-2024",
            "purchase_date": "2024-01-05",
            "warranty_expiry": "2025-01-05",
            "maintenance_due_date": "2024-07-05",
            "last_maintenance_date": "2024-01-05",
            "location": "Computer Lab",
        }
    ]
    
    for equipment_item in equipment_data:
        session.execute(
            text(
                """
                INSERT INTO health_equipment (
                    equipment_name, equipment_type, category, description,
                    manufacturer, model_number, purchase_date, warranty_expiry,
                    maintenance_due_date, last_maintenance_date, location
                ) VALUES (
                    :equipment_name, :equipment_type, :category, :description,
                    :manufacturer, :model_number, :purchase_date, :warranty_expiry,
                    :maintenance_due_date, :last_maintenance_date, :location
                )
                """
            ),
            equipment_item,
        )
    session.commit()
    print(f"   ✅ Created {len(equipment_data)} sample health equipment items")

def verify_health_curriculum(session):
    """Verifies the created health curriculum by counting records."""
    print("\n6️⃣ Verifying health curriculum...")
    units_count = session.execute(text("SELECT COUNT(*) FROM health_curriculum_units")).scalar()
    lessons_count = session.execute(text("SELECT COUNT(*) FROM health_lesson_plans")).scalar()
    protocols_count = session.execute(text("SELECT COUNT(*) FROM health_safety_protocols")).scalar()
    rubrics_count = session.execute(text("SELECT COUNT(*) FROM health_assessment_rubrics")).scalar()
    equipment_count = session.execute(text("SELECT COUNT(*) FROM health_equipment")).scalar()

    print(f"   📊 Curriculum Units: {units_count}")
    print(f"   📊 Lesson Plans: {lessons_count}")
    print(f"   📊 Safety Protocols: {protocols_count}")
    print(f"   📊 Assessment Rubrics: {rubrics_count}")
    print(f"   📊 Equipment Items: {equipment_count}")

    print("\n7️⃣ Lesson distribution by unit:")
    unit_lessons = session.execute(
        text(
            """
            SELECT hcu.unit_number, hcu.unit_title, COUNT(hlp.id) AS lesson_count
            FROM health_curriculum_units hcu
            LEFT JOIN health_lesson_plans hlp ON hcu.id = hlp.curriculum_unit_id
            GROUP BY hcu.unit_number, hcu.unit_title
            ORDER BY hcu.unit_number
            """
        )
    ).fetchall()
    for unit_num, unit_title, count in unit_lessons:
        print(f"   Unit {unit_num}: {unit_title} - {count} lessons")

def create_health_curriculum():
    """Main function to create the comprehensive health curriculum."""
    print("🏥 Creating Comprehensive Health Curriculum...")
    print("=" * 80)

    session = next(get_db())
    try:
        print("1️⃣ Checking Phase 1 teachers...")
        teacher_id = get_first_teacher_id(session)
        if not teacher_id:
            print("❌ No teachers found in Phase 1. Please ensure Phase 1 seeding is run first.")
            return
        print(f"   ✅ Using teacher: {teacher_id}")

        create_health_curriculum_units(session)
        
        # Get all curriculum units
        units = session.execute(text("SELECT id, unit_number FROM health_curriculum_units ORDER BY unit_number")).fetchall()
        unit_map = {unit.unit_number: unit.id for unit in units}
        print(f"   ✅ Found {len(units)} curriculum units")

        print("\n4️⃣ Creating comprehensive lesson plans for all units...")
        # Define how many lessons per unit based on grade level and complexity
        lessons_per_unit = {
            1: 4,   # Personal Health and Hygiene (K-2)
            2: 5,   # Nutrition and Healthy Eating (K-2)
            3: 4,   # Physical Activity and Exercise (K-2)
            4: 4,   # Safety and Injury Prevention (K-2)
            5: 6,   # Mental Health and Emotions (3-5)
            6: 4,   # Substance Abuse Prevention (3-5)
            7: 4,   # Growth and Development (3-5)
            8: 8,   # Adolescent Health (6-8)
            9: 6,   # Sexual Health Education (6-8)
            10: 6,  # Mental Health and Wellness (6-8)
            11: 8,  # Advanced Nutrition and Wellness (9-12)
            12: 6,  # Substance Abuse and Addiction (9-12)
            13: 8,  # Sexual and Reproductive Health (9-12)
            14: 6,  # Mental Health and Crisis Intervention (9-12)
            15: 6,  # Health Advocacy and Community Health (9-12)
        }

        for unit_num, num_lessons in lessons_per_unit.items():
            print(f"   Creating {num_lessons} lesson plans for Unit {unit_num}...")
            create_lesson_plans_for_unit(session, UUID(teacher_id), unit_num, num_lessons)
            print(f"   ✅ Created {num_lessons} lesson plans for Unit {unit_num}")

        create_health_safety_protocols(session)
        create_health_assessment_rubrics(session)
        create_sample_health_equipment(session)

        verify_health_curriculum(session)

        print("\n🎉 Comprehensive Health Curriculum Complete!")
        print("=" * 80)

    except Exception as e:
        print(f"❌ Error creating health curriculum: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    create_health_curriculum()
