#!/usr/bin/env python3
"""
Data Consistency Fix Script
Fixes data scaling and consistency issues for the mock school district
"""

import random
from datetime import datetime, timedelta
from sqlalchemy import text
from app.db.session import get_db

def fix_health_data_consistency(session):
    """Scale up health records to match student population"""
    print("🏥 Fixing health data consistency...")
    
    # Get current counts
    total_students = session.execute(text("SELECT COUNT(*) FROM students")).scalar()
    current_health_records = session.execute(text("SELECT COUNT(*) FROM student_health")).scalar()
    current_health_checks = session.execute(text("SELECT COUNT(*) FROM health_checks")).scalar()
    
    print(f"  Current: {current_health_records} health records, {current_health_checks} health checks")
    print(f"  Target: {total_students} students need health records")
    
    # Get all students without health records
    students_without_health = session.execute(text("""
        SELECT s.id, s.first_name, s.last_name, s.date_of_birth, s.gender
        FROM students s
        LEFT JOIN student_health sh ON s.id = sh.student_id
        WHERE sh.student_id IS NULL
        LIMIT 4000
    """)).fetchall()
    
    print(f"  Found {len(students_without_health)} students without health records")
    
    # Create health records for students
    health_conditions = [
        "None", "Asthma", "Diabetes", "Allergies", "ADHD", "Anxiety", 
        "Depression", "Learning Disability", "Physical Disability", "Other"
    ]
    
    for student in students_without_health:
        try:
            # Create student health record
            session.execute(text("""
                INSERT INTO student_health (
                    student_id, has_medical_conditions, medical_conditions,
                    emergency_contact_name, emergency_contact_phone,
                    insurance_provider, insurance_number, created_at, updated_at
                ) VALUES (
                    :student_id, :has_conditions, :conditions,
                    :emergency_name, :emergency_phone, :insurance_provider,
                    :insurance_number, :created_at, :updated_at
                )
            """), {
                'student_id': student[0],
                'has_conditions': random.choice([True, False]),
                'conditions': random.choice(health_conditions),
                'emergency_name': f"Emergency Contact for {student[1]} {student[2]}",
                'emergency_phone': f"555-{random.randint(1000, 9999)}",
                'insurance_provider': random.choice(["Blue Cross", "Aetna", "Cigna", "UnitedHealth", "None"]),
                'insurance_number': f"INS{random.randint(100000, 999999)}",
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            })
            
            # Create health check record
            session.execute(text("""
                INSERT INTO health_checks (
                    student_id, check_date, height_cm, weight_kg, bmi,
                    blood_pressure_systolic, blood_pressure_diastolic,
                    heart_rate, vision_left, vision_right, hearing_left, hearing_right,
                    notes, created_at, updated_at
                ) VALUES (
                    :student_id, :check_date, :height, :weight, :bmi,
                    :bp_systolic, :bp_diastolic, :heart_rate, :vision_l, :vision_r,
                    :hearing_l, :hearing_r, :notes, :created_at, :updated_at
                )
            """), {
                'student_id': student[0],
                'check_date': datetime.now() - timedelta(days=random.randint(1, 365)),
                'height': random.uniform(120, 190),  # cm
                'weight': random.uniform(25, 100),   # kg
                'bmi': random.uniform(15, 35),
                'bp_systolic': random.randint(90, 140),
                'bp_diastolic': random.randint(60, 90),
                'heart_rate': random.randint(60, 100),
                'vision_l': random.uniform(0.5, 1.2),
                'vision_r': random.uniform(0.5, 1.2),
                'hearing_l': random.choice(["Normal", "Mild Loss", "Moderate Loss"]),
                'hearing_r': random.choice(["Normal", "Mild Loss", "Moderate Loss"]),
                'notes': f"Health check for {student[1]} {student[2]}",
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            })
            
        except Exception as e:
            print(f"    Error creating health record for student {student[0]}: {e}")
            continue
    
    session.commit()
    print(f"  ✅ Created health records for {len(students_without_health)} students")

def fix_nutrition_data_consistency(session):
    """Scale up nutrition logs to realistic daily levels"""
    print("🍽️ Fixing nutrition data consistency...")
    
    # Get current counts
    total_students = session.execute(text("SELECT COUNT(*) FROM students")).scalar()
    current_nutrition_logs = session.execute(text("SELECT COUNT(*) FROM nutrition_logs")).scalar()
    
    print(f"  Current: {current_nutrition_logs} nutrition logs")
    print(f"  Target: ~{total_students * 3} nutrition logs (3 per student)")
    
    # Get sample students
    students = session.execute(text("SELECT id FROM students LIMIT 4000")).fetchall()
    
    # Create nutrition logs
    meals = ["Breakfast", "Lunch", "Dinner", "Snack"]
    food_items = [
        "Apple", "Banana", "Sandwich", "Salad", "Pizza", "Chicken", "Rice",
        "Pasta", "Vegetables", "Milk", "Water", "Juice", "Crackers", "Yogurt"
    ]
    
    for student in students:
        # Create 3 nutrition logs per student
        for _ in range(3):
            try:
                session.execute(text("""
                    INSERT INTO nutrition_logs (
                        student_id, log_date, meal_type, food_items,
                        calories, protein_g, carbs_g, fat_g, fiber_g,
                        sugar_g, sodium_mg, notes, created_at, updated_at
                    ) VALUES (
                        :student_id, :log_date, :meal_type, :food_items,
                        :calories, :protein, :carbs, :fat, :fiber,
                        :sugar, :sodium, :notes, :created_at, :updated_at
                    )
                """), {
                    'student_id': student[0],
                    'log_date': datetime.now() - timedelta(days=random.randint(1, 30)),
                    'meal_type': random.choice(meals),
                    'food_items': random.choice(food_items),
                    'calories': random.randint(200, 800),
                    'protein': random.uniform(10, 50),
                    'carbs': random.uniform(20, 100),
                    'fat': random.uniform(5, 40),
                    'fiber': random.uniform(2, 15),
                    'sugar': random.uniform(5, 30),
                    'sodium': random.randint(100, 1000),
                    'notes': f"Nutrition log for student {student[0]}",
                    'created_at': datetime.now(),
                    'updated_at': datetime.now()
                })
            except Exception as e:
                print(f"    Error creating nutrition log for student {student[0]}: {e}")
                continue
    
    session.commit()
    print(f"  ✅ Created nutrition logs for students")

def fix_fitness_assessments_consistency(session):
    """Scale up fitness assessments to 1 per student"""
    print("💪 Fixing fitness assessments consistency...")
    
    # Get current counts
    total_students = session.execute(text("SELECT COUNT(*) FROM students")).scalar()
    current_assessments = session.execute(text("SELECT COUNT(*) FROM fitness_assessments")).scalar()
    
    print(f"  Current: {current_assessments} fitness assessments")
    print(f"  Target: {total_students} fitness assessments (1 per student)")
    
    # Get students without fitness assessments
    students_without_assessments = session.execute(text("""
        SELECT s.id
        FROM students s
        LEFT JOIN fitness_assessments fa ON s.id = fa.student_id
        WHERE fa.student_id IS NULL
        LIMIT 4000
    """)).fetchall()
    
    print(f"  Found {len(students_without_assessments)} students without fitness assessments")
    
    for student in students_without_assessments:
        try:
            session.execute(text("""
                INSERT INTO fitness_assessments (
                    student_id, assessment_date, push_ups, sit_ups, mile_run_time,
                    flexibility_score, balance_score, coordination_score,
                    overall_fitness_score, notes, created_at, updated_at
                ) VALUES (
                    :student_id, :assessment_date, :push_ups, :sit_ups, :mile_time,
                    :flexibility, :balance, :coordination, :overall_score,
                    :notes, :created_at, :updated_at
                )
            """), {
                'student_id': student[0],
                'assessment_date': datetime.now() - timedelta(days=random.randint(1, 90)),
                'push_ups': random.randint(5, 50),
                'sit_ups': random.randint(10, 60),
                'mile_time': random.uniform(6.0, 15.0),  # minutes
                'flexibility': random.randint(1, 10),
                'balance': random.randint(1, 10),
                'coordination': random.randint(1, 10),
                'overall_score': random.randint(1, 10),
                'notes': f"Fitness assessment for student {student[0]}",
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            })
        except Exception as e:
            print(f"    Error creating fitness assessment for student {student[0]}: {e}")
            continue
    
    session.commit()
    print(f"  ✅ Created fitness assessments for {len(students_without_assessments)} students")

def fix_enrollment_duplicates(session):
    """Remove duplicate enrollments to ensure 1:1 student-to-enrollment ratio"""
    print("🔄 Fixing enrollment duplicates...")
    
    # Get current counts
    total_students = session.execute(text("SELECT COUNT(*) FROM students")).scalar()
    pe_enrollments = session.execute(text("SELECT COUNT(*) FROM physical_education_class_students")).scalar()
    educational_enrollments = session.execute(text("SELECT COUNT(*) FROM educational_class_students")).scalar()
    
    print(f"  Total Students: {total_students}")
    print(f"  PE Enrollments: {pe_enrollments} (duplicates: {pe_enrollments - total_students})")
    print(f"  Educational Enrollments: {educational_enrollments} (duplicates: {educational_enrollments - total_students})")
    
    # Remove duplicate PE enrollments
    session.execute(text("""
        DELETE FROM physical_education_class_students 
        WHERE id IN (
            SELECT id FROM (
                SELECT id, ROW_NUMBER() OVER (
                    PARTITION BY student_id, class_id 
                    ORDER BY created_at DESC
                ) as rn
                FROM physical_education_class_students
            ) t WHERE rn > 1
        )
    """))
    
    # Remove duplicate educational enrollments
    session.execute(text("""
        DELETE FROM educational_class_students 
        WHERE id IN (
            SELECT id FROM (
                SELECT id, ROW_NUMBER() OVER (
                    PARTITION BY student_id, class_id 
                    ORDER BY created_at DESC
                ) as rn
                FROM educational_class_students
            ) t WHERE rn > 1
        )
    """))
    
    session.commit()
    
    # Check results
    new_pe_enrollments = session.execute(text("SELECT COUNT(*) FROM physical_education_class_students")).scalar()
    new_educational_enrollments = session.execute(text("SELECT COUNT(*) FROM educational_class_students")).scalar()
    
    print(f"  ✅ After cleanup:")
    print(f"    PE Enrollments: {new_pe_enrollments}")
    print(f"    Educational Enrollments: {new_educational_enrollments}")

def add_safety_incidents(session):
    """Generate realistic safety incidents data"""
    print("🛡️ Adding safety incidents data...")
    
    # Get current count
    current_incidents = session.execute(text("SELECT COUNT(*) FROM safety_incidents")).scalar()
    print(f"  Current: {current_incidents} safety incidents")
    print(f"  Target: 200+ safety incidents")
    
    # Get students and classes for realistic incidents
    students = session.execute(text("SELECT id FROM students LIMIT 1000")).fetchall()
    classes = session.execute(text("SELECT id FROM physical_education_classes LIMIT 50")).fetchall()
    
    incident_types = [
        "Minor Scrape", "Bruise", "Sprain", "Fall", "Collision", "Equipment Malfunction",
        "Weather Related", "Heat Exhaustion", "Dehydration", "Allergic Reaction"
    ]
    severity_levels = ["Low", "Medium", "High", "Critical"]
    
    for _ in range(200):
        try:
            student = random.choice(students)
            class_id = random.choice(classes)[0] if classes else None
            
            session.execute(text("""
                INSERT INTO safety_incidents (
                    student_id, class_id, incident_date, incident_type,
                    severity_level, description, location, action_taken,
                    follow_up_required, resolved, created_at, updated_at
                ) VALUES (
                    :student_id, :class_id, :incident_date, :incident_type,
                    :severity, :description, :location, :action_taken,
                    :follow_up, :resolved, :created_at, :updated_at
                )
            """), {
                'student_id': student[0],
                'class_id': class_id,
                'incident_date': datetime.now() - timedelta(days=random.randint(1, 365)),
                'incident_type': random.choice(incident_types),
                'severity': random.choice(severity_levels),
                'description': f"Safety incident involving student {student[0]}",
                'location': random.choice(["Gymnasium", "Playground", "Field", "Pool", "Track"]),
                'action_taken': random.choice(["First Aid", "Ice Pack", "Bandage", "Called Parent", "Sent to Nurse"]),
                'follow_up': random.choice([True, False]),
                'resolved': random.choice([True, False]),
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            })
        except Exception as e:
            print(f"    Error creating safety incident: {e}")
            continue
    
    session.commit()
    print(f"  ✅ Created 200 safety incidents")

def add_equipment_maintenance(session):
    """Generate equipment maintenance records"""
    print("🔧 Adding equipment maintenance data...")
    
    # Get current count
    current_maintenance = session.execute(text("SELECT COUNT(*) FROM equipment_maintenance")).scalar()
    print(f"  Current: {current_maintenance} maintenance records")
    print(f"  Target: 500+ maintenance records")
    
    # Get equipment
    equipment = session.execute(text("SELECT id, name FROM physical_education_equipment LIMIT 100")).fetchall()
    
    maintenance_types = [
        "Routine Check", "Cleaning", "Repair", "Replacement", "Inspection",
        "Calibration", "Lubrication", "Safety Check", "Deep Clean", "Update"
    ]
    statuses = ["Scheduled", "In Progress", "Completed", "Cancelled", "Overdue"]
    
    for _ in range(500):
        try:
            if equipment:
                eq = random.choice(equipment)
                equipment_id = eq[0]
                equipment_name = eq[1]
            else:
                equipment_id = None
                equipment_name = "General Equipment"
            
            session.execute(text("""
                INSERT INTO equipment_maintenance (
                    equipment_id, maintenance_type, scheduled_date,
                    completed_date, status, description, technician,
                    cost, notes, created_at, updated_at
                ) VALUES (
                    :equipment_id, :maintenance_type, :scheduled_date,
                    :completed_date, :status, :description, :technician,
                    :cost, :notes, :created_at, :updated_at
                )
            """), {
                'equipment_id': equipment_id,
                'maintenance_type': random.choice(maintenance_types),
                'scheduled_date': datetime.now() - timedelta(days=random.randint(1, 90)),
                'completed_date': datetime.now() - timedelta(days=random.randint(1, 30)) if random.choice([True, False]) else None,
                'status': random.choice(statuses),
                'description': f"Maintenance for {equipment_name}",
                'technician': f"Tech {random.randint(1, 10)}",
                'cost': random.uniform(10, 500),
                'notes': f"Maintenance notes for {equipment_name}",
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            })
        except Exception as e:
            print(f"    Error creating maintenance record: {e}")
            continue
    
    session.commit()
    print(f"  ✅ Created 500 equipment maintenance records")

def fix_data_consistency():
    """Main function to fix all data consistency issues"""
    print("🔧 STARTING DATA CONSISTENCY FIX")
    print("=" * 50)
    
    session = next(get_db())
    
    try:
        # Fix health data
        fix_health_data_consistency(session)
        
        # Fix nutrition data
        fix_nutrition_data_consistency(session)
        
        # Fix fitness assessments
        fix_fitness_assessments_consistency(session)
        
        # Fix enrollment duplicates
        fix_enrollment_duplicates(session)
        
        # Add safety incidents
        add_safety_incidents(session)
        
        # Add equipment maintenance
        add_equipment_maintenance(session)
        
        print("\n✅ DATA CONSISTENCY FIX COMPLETED!")
        print("=" * 50)
        
        # Final verification
        total_students = session.execute(text("SELECT COUNT(*) FROM students")).scalar()
        health_records = session.execute(text("SELECT COUNT(*) FROM student_health")).scalar()
        nutrition_logs = session.execute(text("SELECT COUNT(*) FROM nutrition_logs")).scalar()
        fitness_assessments = session.execute(text("SELECT COUNT(*) FROM fitness_assessments")).scalar()
        safety_incidents = session.execute(text("SELECT COUNT(*) FROM safety_incidents")).scalar()
        equipment_maintenance = session.execute(text("SELECT COUNT(*) FROM equipment_maintenance")).scalar()
        
        print(f"📊 FINAL RESULTS:")
        print(f"  Students: {total_students:,}")
        print(f"  Health Records: {health_records:,} ({health_records/total_students*100:.1f}%)")
        print(f"  Nutrition Logs: {nutrition_logs:,}")
        print(f"  Fitness Assessments: {fitness_assessments:,} ({fitness_assessments/total_students*100:.1f}%)")
        print(f"  Safety Incidents: {safety_incidents:,}")
        print(f"  Equipment Maintenance: {equipment_maintenance:,}")
        
    except Exception as e:
        print(f"❌ Error during data consistency fix: {e}")
        session.rollback()
        raise
    finally:
        session.close()

if __name__ == "__main__":
    fix_data_consistency()
