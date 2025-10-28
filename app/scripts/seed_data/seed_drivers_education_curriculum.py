#!/usr/bin/env python3
"""
Comprehensive Drivers Education Curriculum Seeder
Creates a complete drivers education curriculum for both beta teachers and district versions
"""

import os
import sys
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Add the app directory to the Python path
sys.path.append('/app')

from app.core.database import SessionLocal
from sqlalchemy import text

def create_drivers_ed_curriculum():
    """Create comprehensive drivers education curriculum"""
    
    print("🚗 Creating Comprehensive Drivers Education Curriculum...")
    print("=" * 80)
    
    # Get database session
    session = SessionLocal()
    
    try:
        # First, create the database tables
        print("1️⃣ Creating drivers education database tables...")
        
        with open('/app/migrations/add_drivers_education_tables.sql', 'r') as f:
            migration_sql = f.read()
        
        session.execute(text(migration_sql))
        session.commit()
        print("   ✅ Drivers education tables created")
        
        # Create curriculum units
        print("\n2️⃣ Creating curriculum units...")
        
        curriculum_units = [
            {
                "unit_number": 1,
                "unit_title": "Introduction to Driver Education",
                "description": "Basic concepts, rules of the road, and driver responsibilities",
                "grade_level": "9-12",
                "duration_weeks": 2,
                "prerequisites": [],
                "learning_outcomes": [
                    "Understand the importance of driver education",
                    "Identify key traffic laws and regulations",
                    "Recognize driver responsibilities and rights",
                    "Demonstrate knowledge of vehicle controls"
                ],
                "state_standards": ["DE.1.1", "DE.1.2", "DE.1.3"],
                "national_standards": ["NHTSA.1", "NHTSA.2"],
                "is_core_unit": True
            },
            {
                "unit_number": 2,
                "unit_title": "Vehicle Operation and Controls",
                "description": "Understanding vehicle systems, controls, and basic operation",
                "grade_level": "9-12",
                "duration_weeks": 3,
                "prerequisites": ["Unit 1"],
                "learning_outcomes": [
                    "Identify and operate all vehicle controls",
                    "Understand vehicle systems and maintenance",
                    "Perform pre-drive safety checks",
                    "Demonstrate proper vehicle positioning"
                ],
                "state_standards": ["DE.2.1", "DE.2.2", "DE.2.3", "DE.2.4"],
                "national_standards": ["NHTSA.3", "NHTSA.4"],
                "is_core_unit": True
            },
            {
                "unit_number": 3,
                "unit_title": "Traffic Laws and Regulations",
                "description": "Comprehensive study of traffic laws, signs, signals, and right-of-way",
                "grade_level": "9-12",
                "duration_weeks": 4,
                "prerequisites": ["Unit 1", "Unit 2"],
                "learning_outcomes": [
                    "Interpret traffic signs, signals, and pavement markings",
                    "Apply right-of-way rules in various situations",
                    "Understand speed limits and traffic violations",
                    "Navigate intersections and traffic control devices"
                ],
                "state_standards": ["DE.3.1", "DE.3.2", "DE.3.3", "DE.3.4"],
                "national_standards": ["NHTSA.5", "NHTSA.6"],
                "is_core_unit": True
            },
            {
                "unit_number": 4,
                "unit_title": "Defensive Driving Techniques",
                "description": "Advanced driving skills, hazard recognition, and collision avoidance",
                "grade_level": "10-12",
                "duration_weeks": 3,
                "prerequisites": ["Unit 1", "Unit 2", "Unit 3"],
                "learning_outcomes": [
                    "Identify and respond to potential hazards",
                    "Apply defensive driving strategies",
                    "Maintain safe following distances",
                    "Handle emergency situations safely"
                ],
                "state_standards": ["DE.4.1", "DE.4.2", "DE.4.3"],
                "national_standards": ["NHTSA.7", "NHTSA.8"],
                "is_core_unit": True
            },
            {
                "unit_number": 5,
                "unit_title": "Highway and Freeway Driving",
                "description": "High-speed driving, merging, lane changes, and highway safety",
                "grade_level": "11-12",
                "duration_weeks": 2,
                "prerequisites": ["Unit 1", "Unit 2", "Unit 3", "Unit 4"],
                "learning_outcomes": [
                    "Safely enter and exit highways",
                    "Perform lane changes and merging maneuvers",
                    "Navigate highway interchanges",
                    "Handle high-speed driving situations"
                ],
                "state_standards": ["DE.5.1", "DE.5.2", "DE.5.3"],
                "national_standards": ["NHTSA.9", "NHTSA.10"],
                "is_core_unit": True
            },
            {
                "unit_number": 6,
                "unit_title": "Special Driving Conditions",
                "description": "Weather conditions, night driving, and challenging road conditions",
                "grade_level": "11-12",
                "duration_weeks": 2,
                "prerequisites": ["Unit 1", "Unit 2", "Unit 3", "Unit 4"],
                "learning_outcomes": [
                    "Drive safely in various weather conditions",
                    "Navigate night driving situations",
                    "Handle construction zones and work areas",
                    "Drive in rural and urban environments"
                ],
                "state_standards": ["DE.6.1", "DE.6.2", "DE.6.3"],
                "national_standards": ["NHTSA.11", "NHTSA.12"],
                "is_core_unit": True
            },
            {
                "unit_number": 7,
                "unit_title": "Impaired Driving and Substance Abuse",
                "description": "Effects of alcohol, drugs, and fatigue on driving performance",
                "grade_level": "9-12",
                "duration_weeks": 2,
                "prerequisites": ["Unit 1"],
                "learning_outcomes": [
                    "Understand effects of alcohol and drugs on driving",
                    "Recognize signs of impaired driving",
                    "Learn about DUI laws and consequences",
                    "Develop strategies for responsible decision-making"
                ],
                "state_standards": ["DE.7.1", "DE.7.2", "DE.7.3"],
                "national_standards": ["NHTSA.13", "NHTSA.14"],
                "is_core_unit": True
            },
            {
                "unit_number": 8,
                "unit_title": "Vehicle Maintenance and Safety",
                "description": "Basic vehicle maintenance, safety equipment, and emergency procedures",
                "grade_level": "9-12",
                "duration_weeks": 1,
                "prerequisites": ["Unit 2"],
                "learning_outcomes": [
                    "Perform basic vehicle maintenance checks",
                    "Understand safety equipment and its use",
                    "Handle vehicle emergencies and breakdowns",
                    "Maintain vehicle safety systems"
                ],
                "state_standards": ["DE.8.1", "DE.8.2", "DE.8.3"],
                "national_standards": ["NHTSA.15", "NHTSA.16"],
                "is_core_unit": True
            }
        ]
        
        # Insert curriculum units
        print(f"   📊 Found {len(curriculum_units)} curriculum units to insert")
        for i, unit in enumerate(curriculum_units):
            print(f"   📝 Processing unit {i+1}: {unit.get('unit_title', 'Unknown')}")
            print(f"   🔍 Unit keys: {list(unit.keys()) if isinstance(unit, dict) else 'Not a dict'}")
            print(f"   🔍 Unit type: {type(unit)}")
            if not isinstance(unit, dict) or 'unit_number' not in unit:
                print(f"   ❌ Skipping invalid unit: {unit}")
                continue
            session.execute(text("""
                INSERT INTO drivers_ed_curriculum_units (
                    unit_number, unit_title, description, grade_level, duration_weeks,
                    prerequisites, learning_outcomes, state_standards, national_standards,
                    is_core_unit, is_elective
                ) VALUES (
                    :unit_number, :unit_title, :description, :grade_level, :duration_weeks,
                    :prerequisites, :learning_outcomes, :state_standards, :national_standards,
                    :is_core_unit, :is_elective
                )
            """), {
                'unit_number': unit['unit_number'],
                'unit_title': unit['unit_title'],
                'description': unit['description'],
                'grade_level': unit['grade_level'],
                'duration_weeks': unit['duration_weeks'],
                'prerequisites': unit['prerequisites'],
                'learning_outcomes': unit['learning_outcomes'],
                'state_standards': unit['state_standards'],
                'national_standards': unit['national_standards'],
                'is_core_unit': unit['is_core_unit'],
                'is_elective': unit.get('is_elective', False)
            })
        
        session.commit()
        print(f"   ✅ Created {len(curriculum_units)} curriculum units")
        
        # Create comprehensive lesson plans
        print("\n3️⃣ Creating comprehensive lesson plans...")
        
        # Get the first teacher for lesson plan creation
        teacher_result = session.execute(text("SELECT id FROM teacher_registrations LIMIT 1")).fetchone()
        if not teacher_result:
            # Create a default teacher for drivers ed
            default_teacher_id = '00000000-0000-0000-0000-000000000002'
            session.execute(text("""
                INSERT INTO teacher_registrations (
                    id, email, password_hash, first_name, last_name, 
                    is_verified, is_active
                ) VALUES (
                    :id, :email, :password_hash, :first_name, :last_name,
                    TRUE, TRUE
                )
            """), {
                'id': default_teacher_id,
                'email': 'driversed@faraday-ai.com',
                'password_hash': 'driversed_hash',
                'first_name': 'Drivers',
                'last_name': 'Education'
            })
            session.commit()
        else:
            default_teacher_id = str(teacher_result[0])
        
        # Get curriculum unit IDs
        unit_ids = {}
        units_result = session.execute(text("SELECT id, unit_number FROM drivers_ed_curriculum_units ORDER BY unit_number")).fetchall()
        for unit_id, unit_number in units_result:
            unit_ids[unit_number] = unit_id
        
        # Create lesson plans for each unit
        lesson_plans = create_lesson_plans()
        
        created_lessons = 0
        for lesson in lesson_plans:
            try:
                session.execute(text("""
                    INSERT INTO drivers_ed_lesson_plans (
                        teacher_id, curriculum_unit_id, lesson_number, title, description,
                        grade_level, duration_minutes, lesson_type, difficulty_level,
                        learning_objectives, key_vocabulary, safety_focus_areas,
                        warm_up_activities, main_activities, cool_down_activities,
                        materials_needed, equipment_needed, technology_required, handouts_needed,
                        safety_considerations, assessment_methods, evaluation_criteria,
                        state_standards, national_standards, dmv_requirements,
                        tags, is_template, is_public
                    ) VALUES (
                        :teacher_id, :curriculum_unit_id, :lesson_number, :title, :description,
                        :grade_level, :duration_minutes, :lesson_type, :difficulty_level,
                        :learning_objectives, :key_vocabulary, :safety_focus_areas,
                        :warm_up_activities, :main_activities, :cool_down_activities,
                        :materials_needed, :equipment_needed, :technology_required, :handouts_needed,
                        :safety_considerations, :assessment_methods, :evaluation_criteria,
                        :state_standards, :national_standards, :dmv_requirements,
                        :tags, :is_template, :is_public
                    )
                """), {
                    'teacher_id': default_teacher_id,
                    'curriculum_unit_id': unit_ids[lesson['unit_number']],
                    'lesson_number': lesson['lesson_number'],
                    'title': lesson['title'],
                    'description': lesson['description'],
                    'grade_level': lesson['grade_level'],
                    'duration_minutes': lesson['duration_minutes'],
                    'lesson_type': lesson['lesson_type'],
                    'difficulty_level': lesson['difficulty_level'],
                    'learning_objectives': lesson['learning_objectives'],
                    'key_vocabulary': lesson['key_vocabulary'],
                    'safety_focus_areas': lesson['safety_focus_areas'],
                    'warm_up_activities': lesson['warm_up_activities'],
                    'main_activities': lesson['main_activities'],
                    'cool_down_activities': lesson['cool_down_activities'],
                    'materials_needed': lesson['materials_needed'],
                    'equipment_needed': lesson['equipment_needed'],
                    'technology_required': lesson['technology_required'],
                    'handouts_needed': lesson['handouts_needed'],
                    'safety_considerations': lesson['safety_considerations'],
                    'assessment_methods': lesson['assessment_methods'],
                    'evaluation_criteria': lesson['evaluation_criteria'],
                    'state_standards': lesson['state_standards'],
                    'national_standards': lesson['national_standards'],
                    'dmv_requirements': lesson['dmv_requirements'],
                    'tags': lesson['tags'],
                    'is_template': True,
                    'is_public': True
                })
                created_lessons += 1
                
            except Exception as e:
                print(f"   ⚠️  Error creating lesson {lesson['title']}: {e}")
                continue
        
        session.commit()
        print(f"   ✅ Created {created_lessons} lesson plans")
        
        # Create safety protocols
        print("\n4️⃣ Creating safety protocols...")
        
        safety_protocols = create_safety_protocols()
        
        for protocol in safety_protocols:
            session.execute(text("""
                INSERT INTO drivers_ed_safety_protocols (
                    protocol_name, protocol_type, description, steps, safety_checklist,
                    required_equipment, applicable_lesson_types, grade_levels, is_mandatory
                ) VALUES (
                    :protocol_name, :protocol_type, :description, :steps, :safety_checklist,
                    :required_equipment, :applicable_lesson_types, :grade_levels, :is_mandatory
                )
            """), protocol)
        
        session.commit()
        print(f"   ✅ Created {len(safety_protocols)} safety protocols")
        
        # Create assessment rubrics
        print("\n5️⃣ Creating assessment rubrics...")
        
        assessment_rubrics = create_assessment_rubrics()
        
        for rubric in assessment_rubrics:
            session.execute(text("""
                INSERT INTO drivers_ed_assessment_rubrics (
                    rubric_name, assessment_type, grade_level, description, criteria,
                    scoring_scale, passing_score, time_limit_minutes, is_standardized
                ) VALUES (
                    :rubric_name, :assessment_type, :grade_level, :description, :criteria,
                    :scoring_scale, :passing_score, :time_limit_minutes, :is_standardized
                )
            """), rubric)
        
        session.commit()
        print(f"   ✅ Created {len(assessment_rubrics)} assessment rubrics")
        
        # Create sample vehicles
        print("\n6️⃣ Creating sample vehicle fleet...")
        
        vehicles = create_sample_vehicles()
        
        for vehicle in vehicles:
            session.execute(text("""
                INSERT INTO drivers_ed_vehicles (
                    vehicle_make, vehicle_model, year, license_plate, vin,
                    vehicle_type, transmission_type, safety_equipment,
                    inspection_due_date, last_inspection_date, insurance_expiry, registration_expiry
                ) VALUES (
                    :vehicle_make, :vehicle_model, :year, :license_plate, :vin,
                    :vehicle_type, :transmission_type, :safety_equipment,
                    :inspection_due_date, :last_inspection_date, :insurance_expiry, :registration_expiry
                ) ON CONFLICT (license_plate) DO NOTHING
            """), vehicle)
        
        session.commit()
        print(f"   ✅ Created {len(vehicles)} sample vehicles")
        
        # Final verification
        print("\n7️⃣ Verifying drivers education curriculum...")
        
        units_count = session.execute(text("SELECT COUNT(*) FROM drivers_ed_curriculum_units")).fetchone()[0]
        lessons_count = session.execute(text("SELECT COUNT(*) FROM drivers_ed_lesson_plans")).fetchone()[0]
        protocols_count = session.execute(text("SELECT COUNT(*) FROM drivers_ed_safety_protocols")).fetchone()[0]
        rubrics_count = session.execute(text("SELECT COUNT(*) FROM drivers_ed_assessment_rubrics")).fetchone()[0]
        vehicles_count = session.execute(text("SELECT COUNT(*) FROM drivers_ed_vehicles")).fetchone()[0]
        
        print(f"   📊 Curriculum Units: {units_count}")
        print(f"   📊 Lesson Plans: {lessons_count}")
        print(f"   📊 Safety Protocols: {protocols_count}")
        print(f"   📊 Assessment Rubrics: {rubrics_count}")
        print(f"   📊 Vehicles: {vehicles_count}")
        
        print("\n🎉 Drivers Education Curriculum Creation Complete!")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ Error creating drivers education curriculum: {e}")
        session.rollback()
        raise
    finally:
        session.close()

def create_lesson_plans() -> List[Dict[str, Any]]:
    """Create comprehensive lesson plans for drivers education"""
    
    lesson_plans = []
    
    # Unit 1: Introduction to Driver Education
    lesson_plans.extend([
        {
            "unit_number": 1,
            "lesson_number": 1,
            "title": "Welcome to Driver Education",
            "description": "Introduction to driver education program, expectations, and safety rules",
            "grade_level": "9-12",
            "duration_minutes": 50,
            "lesson_type": "classroom",
            "difficulty_level": "beginner",
            "learning_objectives": [
                "Understand the importance of driver education",
                "Identify program expectations and requirements",
                "Recognize basic safety rules and procedures",
                "Complete necessary paperwork and forms"
            ],
            "key_vocabulary": ["Driver Education", "Safety", "Responsibility", "Laws", "Regulations"],
            "safety_focus_areas": ["Classroom Safety", "Program Rules", "Emergency Procedures"],
            "warm_up_activities": [
                "Welcome and introductions",
                "Ice breaker: 'Why do you want to learn to drive?'",
                "Review of course syllabus and expectations"
            ],
            "main_activities": [
                "Presentation: Importance of driver education",
                "Discussion: Driver responsibilities and rights",
                "Activity: Safety rules and procedures",
                "Handout: Course requirements and paperwork"
            ],
            "cool_down_activities": [
                "Q&A session",
                "Preview of next lesson",
                "Assignment: Read Chapter 1 in driver manual"
            ],
            "materials_needed": ["Course syllabus", "Driver manual", "Safety rules handout", "Registration forms"],
            "equipment_needed": ["Projector", "Whiteboard", "Markers"],
            "technology_required": ["Computer", "Presentation software"],
            "handouts_needed": ["Course syllabus", "Safety rules", "Registration forms"],
            "safety_considerations": [
                "Ensure all students understand safety procedures",
                "Review emergency evacuation routes",
                "Check for any medical conditions that may affect participation"
            ],
            "assessment_methods": ["Participation", "Completion of forms", "Oral questioning"],
            "evaluation_criteria": [
                "Active participation in discussions",
                "Completion of required paperwork",
                "Demonstration of understanding of safety rules"
            ],
            "state_standards": ["DE.1.1", "DE.1.2"],
            "national_standards": ["NHTSA.1"],
            "dmv_requirements": ["Completion of 30 hours classroom instruction"],
            "tags": ["introduction", "safety", "orientation"]
        },
        {
            "unit_number": 1,
            "lesson_number": 2,
            "title": "Traffic Laws and Regulations",
            "description": "Introduction to basic traffic laws, signs, and regulations",
            "grade_level": "9-12",
            "duration_minutes": 50,
            "lesson_type": "classroom",
            "difficulty_level": "beginner",
            "learning_objectives": [
                "Identify basic traffic signs and their meanings",
                "Understand fundamental traffic laws",
                "Recognize right-of-way rules",
                "Apply traffic laws to common driving situations"
            ],
            "key_vocabulary": ["Traffic Signs", "Right of Way", "Speed Limit", "Stop Sign", "Yield"],
            "safety_focus_areas": ["Traffic Sign Recognition", "Right of Way Rules", "Speed Limits"],
            "warm_up_activities": [
                "Review of previous lesson",
                "Quick quiz on safety rules",
                "Introduction to traffic signs"
            ],
            "main_activities": [
                "Presentation: Types of traffic signs",
                "Activity: Traffic sign identification game",
                "Discussion: Right-of-way rules",
                "Practice: Applying laws to scenarios"
            ],
            "cool_down_activities": [
                "Review of key concepts",
                "Assignment: Study traffic signs",
                "Preview of next lesson"
            ],
            "materials_needed": ["Traffic sign flashcards", "Driver manual", "Scenarios worksheet"],
            "equipment_needed": ["Projector", "Traffic sign images", "Whiteboard"],
            "technology_required": ["Computer", "Traffic sign software"],
            "handouts_needed": ["Traffic sign study guide", "Right-of-way rules", "Practice scenarios"],
            "safety_considerations": [
                "Ensure students understand the importance of following traffic laws",
                "Emphasize the consequences of traffic violations",
                "Review emergency procedures for classroom"
            ],
            "assessment_methods": ["Traffic sign quiz", "Scenario analysis", "Participation"],
            "evaluation_criteria": [
                "Accuracy in identifying traffic signs",
                "Correct application of right-of-way rules",
                "Active participation in discussions"
            ],
            "state_standards": ["DE.1.3", "DE.3.1"],
            "national_standards": ["NHTSA.5"],
            "dmv_requirements": ["Knowledge of traffic signs and laws"],
            "tags": ["traffic laws", "signs", "regulations", "right of way"]
        }
    ])
    
    # Unit 2: Vehicle Operation and Controls
    lesson_plans.extend([
        {
            "unit_number": 2,
            "lesson_number": 1,
            "title": "Vehicle Controls and Instruments",
            "description": "Understanding and operating vehicle controls, gauges, and instruments",
            "grade_level": "9-12",
            "duration_minutes": 60,
            "lesson_type": "classroom",
            "difficulty_level": "beginner",
            "learning_objectives": [
                "Identify all vehicle controls and their functions",
                "Understand dashboard instruments and warning lights",
                "Demonstrate proper operation of vehicle controls",
                "Recognize safety features and their operation"
            ],
            "key_vocabulary": ["Steering Wheel", "Brake Pedal", "Accelerator", "Dashboard", "Warning Lights"],
            "safety_focus_areas": ["Control Operation", "Warning Systems", "Safety Features"],
            "warm_up_activities": [
                "Review of traffic laws",
                "Introduction to vehicle controls",
                "Discussion of personal vehicle experience"
            ],
            "main_activities": [
                "Presentation: Vehicle control systems",
                "Demonstration: Control operation",
                "Activity: Control identification practice",
                "Discussion: Safety features and warning systems"
            ],
            "cool_down_activities": [
                "Review of key controls",
                "Assignment: Study control functions",
                "Preview of hands-on practice"
            ],
            "materials_needed": ["Vehicle control diagrams", "Dashboard layout", "Safety feature guide"],
            "equipment_needed": ["Vehicle simulator", "Control models", "Projector"],
            "technology_required": ["Driving simulator software", "Interactive displays"],
            "handouts_needed": ["Control identification guide", "Dashboard layout", "Safety features list"],
            "safety_considerations": [
                "Ensure students understand the importance of proper control operation",
                "Review safety procedures for hands-on practice",
                "Check for any physical limitations that may affect control operation"
            ],
            "assessment_methods": ["Control identification test", "Simulator practice", "Oral questioning"],
            "evaluation_criteria": [
                "Accuracy in identifying controls",
                "Proper operation of controls",
                "Understanding of safety features"
            ],
            "state_standards": ["DE.2.1", "DE.2.2"],
            "national_standards": ["NHTSA.3"],
            "dmv_requirements": ["Knowledge of vehicle controls"],
            "tags": ["vehicle controls", "dashboard", "safety features", "instruments"]
        },
        {
            "unit_number": 2,
            "lesson_number": 2,
            "title": "Pre-Drive Safety Inspection",
            "description": "Learning to perform comprehensive pre-drive safety checks",
            "grade_level": "9-12",
            "duration_minutes": 45,
            "lesson_type": "behind_wheel",
            "difficulty_level": "beginner",
            "learning_objectives": [
                "Perform complete pre-drive safety inspection",
                "Identify potential safety hazards",
                "Check vehicle systems and equipment",
                "Document inspection findings"
            ],
            "key_vocabulary": ["Pre-Drive Check", "Safety Inspection", "Tire Pressure", "Fluid Levels", "Lights"],
            "safety_focus_areas": ["Vehicle Inspection", "Safety Checks", "Hazard Identification"],
            "warm_up_activities": [
                "Review of vehicle controls",
                "Discussion of safety importance",
                "Introduction to inspection procedures"
            ],
            "main_activities": [
                "Demonstration: Pre-drive inspection",
                "Practice: Hands-on inspection",
                "Discussion: Common safety issues",
                "Activity: Inspection checklist completion"
            ],
            "cool_down_activities": [
                "Review of inspection procedures",
                "Assignment: Practice inspection at home",
                "Preview of driving practice"
            ],
            "materials_needed": ["Inspection checklist", "Safety equipment", "Vehicle"],
            "equipment_needed": ["Vehicle", "Safety equipment", "Inspection tools"],
            "technology_required": ["Inspection app", "Digital checklist"],
            "handouts_needed": ["Inspection checklist", "Safety procedures", "Common issues guide"],
            "safety_considerations": [
                "Ensure students understand the importance of pre-drive checks",
                "Review safety procedures for vehicle inspection",
                "Check for any physical limitations that may affect inspection"
            ],
            "assessment_methods": ["Inspection demonstration", "Checklist completion", "Safety knowledge test"],
            "evaluation_criteria": [
                "Completeness of inspection",
                "Accuracy in identifying issues",
                "Understanding of safety procedures"
            ],
            "state_standards": ["DE.2.3", "DE.2.4"],
            "national_standards": ["NHTSA.4"],
            "dmv_requirements": ["Pre-drive safety inspection"],
            "tags": ["safety inspection", "pre-drive check", "vehicle maintenance", "hazard identification"]
        }
    ])
    
    # Unit 3: Traffic Laws and Regulations - Additional lessons
    lesson_plans.extend([
        {
            "unit_number": 3,
            "lesson_number": 1,
            "title": "Understanding Traffic Signs and Signals",
            "description": "Comprehensive guide to traffic signs, signals, and markings",
            "grade_level": "9-12",
            "duration_minutes": 50,
            "lesson_type": "classroom",
            "difficulty_level": "intermediate",
            "learning_objectives": ["Identify all types of traffic signs", "Understand traffic signal meanings", "Recognize road markings"],
            "key_vocabulary": ["Stop Sign", "Yield", "No Entry", "Speed Limit", "Right Turn Only"],
            "safety_focus_areas": ["Sign Recognition", "Traffic Signals", "Road Markings"],
            "warm_up_activities": ["Sign identification quiz", "Review previous traffic laws"],
            "main_activities": ["Interactive sign game", "Signal demonstration", "Road marking exercises"],
            "cool_down_activities": ["Q&A", "Practice test"],
            "materials_needed": ["Sign flashcards", "Traffic diagrams"],
            "equipment_needed": ["Projector", "Whiteboard"],
            "technology_required": ["Computer"],
            "handouts_needed": ["Sign study guide"],
            "safety_considerations": ["Emphasize importance of following signs"],
            "assessment_methods": ["Written test", "Oral questioning"],
            "evaluation_criteria": ["Sign recognition accuracy"],
            "state_standards": ["DE.3.1"],
            "national_standards": ["NHTSA.5"],
            "dmv_requirements": ["Traffic sign knowledge"],
            "tags": ["traffic signs", "signals", "regulations"]
        },
        {
            "unit_number": 3,
            "lesson_number": 2,
            "title": "Right-of-Way Rules and Intersections",
            "description": "Mastering right-of-way rules and safe intersection navigation",
            "grade_level": "9-12",
            "duration_minutes": 50,
            "lesson_type": "classroom",
            "difficulty_level": "intermediate",
            "learning_objectives": ["Apply right-of-way rules", "Navigate intersections safely", "Handle complex scenarios"],
            "key_vocabulary": ["Right of Way", "Yield", "Stop", "Intersection", "Four-Way Stop"],
            "safety_focus_areas": ["Intersection Safety", "Right of Way", "Defensive Driving"],
            "warm_up_activities": ["Scenario review", "Right-of-way quiz"],
            "main_activities": ["Interactive scenarios", "Video analysis", "Practice problems"],
            "cool_down_activities": ["Review", "Preview next lesson"],
            "materials_needed": ["Scenario cards", "Video clips"],
            "equipment_needed": ["Projector"],
            "technology_required": ["Computer", "Video player"],
            "handouts_needed": ["Right-of-way rules"],
            "safety_considerations": ["Emphasize defensive driving"],
            "assessment_methods": ["Written test", "Scenario evaluation"],
            "evaluation_criteria": ["Correct application of rules"],
            "state_standards": ["DE.3.2"],
            "national_standards": ["NHTSA.5"],
            "dmv_requirements": ["Intersection knowledge"],
            "tags": ["right of way", "intersections", "safety"]
        }
    ])
    
    # Unit 4: Defensive Driving Techniques
    lesson_plans.extend([
        {
            "unit_number": 4,
            "lesson_number": 1,
            "title": "Maintaining Safe Following Distance",
            "description": "Understanding and applying the 3-second rule and safe following distances",
            "grade_level": "9-12",
            "duration_minutes": 45,
            "lesson_type": "behind_wheel",
            "difficulty_level": "intermediate",
            "learning_objectives": ["Apply 3-second rule", "Adjust for weather conditions", "Identify unsafe distances"],
            "key_vocabulary": ["Following Distance", "3-Second Rule", "Safe Distance", "Braking Distance"],
            "safety_focus_areas": ["Safe Following", "Weather Adaptation", "Collision Prevention"],
            "warm_up_activities": ["Distance estimation", "Review previous lesson"],
            "main_activities": ["On-road practice", "Distance calculation", "Weather simulation"],
            "cool_down_activities": ["Debrief", "Review techniques"],
            "materials_needed": ["Vehicle", "Safe distance guide"],
            "equipment_needed": ["Vehicle", "Safety equipment"],
            "technology_required": ["Vehicle telemetry"],
            "handouts_needed": ["Following distance guide"],
            "safety_considerations": ["Supervised practice only", "Safe speeds"],
            "assessment_methods": ["Driving observation", "Distance measurement"],
            "evaluation_criteria": ["Consistent safe distance"],
            "state_standards": ["DE.4.1"],
            "national_standards": ["NHTSA.6"],
            "dmv_requirements": ["Safe following"],
            "tags": ["defensive driving", "following distance", "safety"]
        }
    ])
    
    # Unit 5: Highway and Freeway Driving
    lesson_plans.extend([
        {
            "unit_number": 5,
            "lesson_number": 1,
            "title": "Entering and Exiting Freeways Safely",
            "description": "Mastering freeway entry, lane changes, and exits",
            "grade_level": "9-12",
            "duration_minutes": 60,
            "lesson_type": "behind_wheel",
            "difficulty_level": "advanced",
            "learning_objectives": ["Enter freeway safely", "Change lanes properly", "Exit smoothly"],
            "key_vocabulary": ["Acceleration Lane", "Merge", "Exit Ramp", "Lane Change"],
            "safety_focus_areas": ["Freeway Entry", "Lane Changes", "Exits"],
            "warm_up_activities": ["Freeway rules review", "Safety briefing"],
            "main_activities": ["Freeway practice", "Lane change practice", "Exit practice"],
            "cool_down_activities": ["Debrief", "Review techniques"],
            "materials_needed": ["Vehicle", "Route plan"],
            "equipment_needed": ["Vehicle", "Safety equipment"],
            "technology_required": ["GPS"],
            "handouts_needed": ["Freeway guide"],
            "safety_considerations": ["Supervised only", "Begin with light traffic"],
            "assessment_methods": ["Driving observation"],
            "evaluation_criteria": ["Safe entry/exit", "Proper signaling"],
            "state_standards": ["DE.5.1"],
            "national_standards": ["NHTSA.7"],
            "dmv_requirements": ["Freeway proficiency"],
            "tags": ["highway", "freeway", "advanced"]
        }
    ])
    
    # Unit 6: Special Driving Conditions
    lesson_plans.extend([
        {
            "unit_number": 6,
            "lesson_number": 1,
            "title": "Driving in Adverse Weather Conditions",
            "description": "Safe driving techniques for rain, snow, fog, and other weather conditions",
            "grade_level": "9-12",
            "duration_minutes": 50,
            "lesson_type": "classroom",
            "difficulty_level": "intermediate",
            "learning_objectives": ["Adapt to weather conditions", "Reduce speed appropriately", "Increase following distance"],
            "key_vocabulary": ["Hydroplaning", "Black Ice", "Fog Lights", "Weather Conditions"],
            "safety_focus_areas": ["Weather Adaptation", "Speed Reduction", "Visibility"],
            "warm_up_activities": ["Weather scenario review", "Discussion of experiences"],
            "main_activities": ["Video analysis", "Weather simulation", "Safety techniques"],
            "cool_down_activities": ["Review", "Safety reminders"],
            "materials_needed": ["Weather safety guide", "Video clips"],
            "equipment_needed": ["Projector"],
            "technology_required": ["Computer", "Video"],
            "handouts_needed": ["Weather safety guide"],
            "safety_considerations": ["Emphasize caution", "Practice avoidance"],
            "assessment_methods": ["Written test", "Scenario analysis"],
            "evaluation_criteria": ["Understanding of safety techniques"],
            "state_standards": ["DE.6.1"],
            "national_standards": ["NHTSA.8"],
            "dmv_requirements": ["Weather awareness"],
            "tags": ["weather", "safety", "conditions"]
        }
    ])
    
    # Unit 7: Impaired Driving and Substance Abuse
    lesson_plans.extend([
        {
            "unit_number": 7,
            "lesson_number": 1,
            "title": "Understanding Impaired Driving Risks",
            "description": "Comprehensive education on DUI, distracted driving, and substance abuse",
            "grade_level": "9-12",
            "duration_minutes": 50,
            "lesson_type": "classroom",
            "difficulty_level": "intermediate",
            "learning_objectives": ["Recognize impairment signs", "Understand legal consequences", "Avoid impaired driving"],
            "key_vocabulary": ["DUI", "Distracted Driving", "BAC", "Impaired"],
            "safety_focus_areas": ["Substance Awareness", "Legal Consequences", "Safety"],
            "warm_up_activities": ["Discussion starter", "Statistics presentation"],
            "main_activities": ["Guest speaker", "Video presentation", "Discussion"],
            "cool_down_activities": ["Commitment activity", "Review"],
            "materials_needed": ["Educational materials", "Statistics"],
            "equipment_needed": ["Projector"],
            "technology_required": ["Computer"],
            "handouts_needed": ["Substance abuse guide"],
            "safety_considerations": ["Sensitive topic", "Professional presentation"],
            "assessment_methods": ["Reflection essay", "Participation"],
            "evaluation_criteria": ["Understanding of risks"],
            "state_standards": ["DE.7.1"],
            "national_standards": ["NHTSA.9"],
            "dmv_requirements": ["Substance awareness"],
            "tags": ["impaired", "substance abuse", "safety"]
        }
    ])
    
    # Unit 8: Vehicle Maintenance and Safety
    lesson_plans.extend([
        {
            "unit_number": 8,
            "lesson_number": 1,
            "title": "Basic Vehicle Maintenance for Drivers",
            "description": "Essential maintenance checks every driver should know",
            "grade_level": "9-12",
            "duration_minutes": 50,
            "lesson_type": "classroom",
            "difficulty_level": "beginner",
            "learning_objectives": ["Perform basic checks", "Identify maintenance needs", "Understand vehicle systems"],
            "key_vocabulary": ["Oil Level", "Tire Pressure", "Brake Fluid", "Coolant"],
            "safety_focus_areas": ["Vehicle Safety", "Prevention", "Maintenance"],
            "warm_up_activities": ["Vehicle walk-around", "Discussion"],
            "main_activities": ["Hands-on demonstration", "Practice checks", "Discussion"],
            "cool_down_activities": ["Review checklist", "Assignment"],
            "materials_needed": ["Vehicle", "Maintenance guide"],
            "equipment_needed": ["Vehicle", "Tools"],
            "technology_required": ["Computer"],
            "handouts_needed": ["Maintenance checklist"],
            "safety_considerations": ["Safe vehicle handling", "Supervision"],
            "assessment_methods": ["Practical demonstration"],
            "evaluation_criteria": ["Proper technique"],
            "state_standards": ["DE.8.1"],
            "national_standards": ["NHTSA.10"],
            "dmv_requirements": ["Vehicle knowledge"],
            "tags": ["maintenance", "vehicle", "safety"]
        }
    ])
    
    return lesson_plans

def create_safety_protocols() -> List[Dict[str, Any]]:
    """Create comprehensive safety protocols for drivers education"""
    
    return [
        {
            "protocol_name": "Pre-Drive Safety Inspection",
            "protocol_type": "pre_drive",
            "description": "Comprehensive safety inspection before driving",
            "steps": [
                "Check vehicle exterior for damage",
                "Inspect tires for wear and pressure",
                "Check all lights and signals",
                "Verify mirrors are properly adjusted",
                "Check seat belts and safety equipment",
                "Test brakes and steering",
                "Check fluid levels",
                "Verify registration and insurance"
            ],
            "safety_checklist": [
                "Tires properly inflated",
                "All lights working",
                "Mirrors adjusted",
                "Seat belts functional",
                "Brakes responsive",
                "Steering smooth",
                "Fluid levels adequate",
                "Documents current"
            ],
            "required_equipment": ["Tire pressure gauge", "Flashlight", "Safety vest", "Inspection checklist"],
            "applicable_lesson_types": ["behind_wheel", "simulator"],
            "grade_levels": ["9-12"],
            "is_mandatory": True
        },
        {
            "protocol_name": "Emergency Procedures",
            "protocol_type": "emergency",
            "description": "Procedures for handling driving emergencies",
            "steps": [
                "Assess the situation safely",
                "Signal and move to safe location",
                "Turn on hazard lights",
                "Call emergency services if needed",
                "Exit vehicle if safe to do so",
                "Wait for help in safe location",
                "Document incident if required"
            ],
            "safety_checklist": [
                "Vehicle in safe location",
                "Hazard lights on",
                "Emergency services contacted",
                "All occupants safe",
                "Incident documented"
            ],
            "required_equipment": ["Emergency kit", "Phone", "Hazard triangle", "First aid kit"],
            "applicable_lesson_types": ["behind_wheel", "simulator", "classroom"],
            "grade_levels": ["9-12"],
            "is_mandatory": True
        }
    ]

def create_assessment_rubrics() -> List[Dict[str, Any]]:
    """Create comprehensive assessment rubrics for drivers education"""
    
    return [
        {
            "rubric_name": "Behind-the-Wheel Driving Assessment",
            "assessment_type": "behind_wheel",
            "grade_level": "9-12",
            "description": "Comprehensive assessment of driving skills and safety",
            "criteria": [
                "Vehicle control and operation",
                "Traffic law compliance",
                "Safety awareness and procedures",
                "Defensive driving techniques",
                "Communication and signaling",
                "Speed and space management",
                "Hazard recognition and response",
                "Overall driving competence"
            ],
            "scoring_scale": "1-4",
            "passing_score": 3.0,
            "time_limit_minutes": 30,
            "is_standardized": True
        },
        {
            "rubric_name": "Written Knowledge Test",
            "assessment_type": "written_test",
            "grade_level": "9-12",
            "description": "Assessment of traffic laws, signs, and regulations knowledge",
            "criteria": [
                "Traffic sign recognition",
                "Traffic law knowledge",
                "Right-of-way rules",
                "Safety procedures",
                "Vehicle operation",
                "Emergency procedures",
                "Impaired driving awareness",
                "Overall knowledge comprehension"
            ],
            "scoring_scale": "percentage",
            "passing_score": 80.0,
            "time_limit_minutes": 60,
            "is_standardized": True
        }
    ]

def create_sample_vehicles() -> List[Dict[str, Any]]:
    """Create sample vehicle fleet for drivers education"""
    
    return [
        {
            "vehicle_make": "Toyota",
            "vehicle_model": "Camry",
            "year": 2022,
            "license_plate": "DE-001",
            "vin": "1HGBH41JXMN109186",
            "vehicle_type": "sedan",
            "transmission_type": "automatic",
            "safety_equipment": ["Airbags", "ABS", "Traction Control", "Backup Camera", "Blind Spot Monitor"],
            "inspection_due_date": "2024-12-01",
            "last_inspection_date": "2024-06-01",
            "insurance_expiry": "2024-12-31",
            "registration_expiry": "2024-12-31"
        },
        {
            "vehicle_make": "Honda",
            "vehicle_model": "Civic",
            "year": 2021,
            "license_plate": "DE-002",
            "vin": "2HGBH41JXMN109187",
            "vehicle_type": "sedan",
            "transmission_type": "automatic",
            "safety_equipment": ["Airbags", "ABS", "Traction Control", "Backup Camera"],
            "inspection_due_date": "2024-11-15",
            "last_inspection_date": "2024-05-15",
            "insurance_expiry": "2024-11-30",
            "registration_expiry": "2024-11-30"
        }
    ]

if __name__ == "__main__":
    create_drivers_ed_curriculum()
