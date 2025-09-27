#!/usr/bin/env python3
"""
Simple Data Consistency Fix Script
Fixes data scaling issues without getting stuck in loops
"""

import random
from datetime import datetime, timedelta
from sqlalchemy import text
from app.db.session import get_db

def fix_health_data_simple(session):
    """Add health records for students without them"""
    print("🏥 Adding health records...")
    
    try:
        # Get students without health records (limit to 1000 to avoid overwhelming)
        students = session.execute(text("""
            SELECT s.id FROM students s
            LEFT JOIN student_health sh ON s.id = sh.student_id
            WHERE sh.student_id IS NULL
            LIMIT 1000
        """)).fetchall()
        
        print(f"  Found {len(students)} students without health records")
        
        for i, student in enumerate(students):
            if i % 100 == 0:
                print(f"    Processing student {i+1}/{len(students)}")
                session.commit()  # Commit every 100 records
            
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
                    'conditions': random.choice(["None", "Asthma", "Allergies", "ADHD"]),
                    'emergency_name': f"Emergency Contact {student[0]}",
                    'emergency_phone': f"555-{random.randint(1000, 9999)}",
                    'insurance_provider': random.choice(["Blue Cross", "Aetna", "None"]),
                    'insurance_number': f"INS{random.randint(100000, 999999)}",
                    'created_at': datetime.now(),
                    'updated_at': datetime.now()
                })
                
            except Exception as e:
                print(f"    Error with student {student[0]}: {e}")
                session.rollback()
                continue
        
        session.commit()
        print(f"  ✅ Added health records for {len(students)} students")
        
    except Exception as e:
        print(f"  ❌ Error in health data fix: {e}")
        session.rollback()

def fix_nutrition_data_simple(session):
    """Add nutrition logs (limit to avoid overwhelming)"""
    print("🍽️ Adding nutrition logs...")
    
    try:
        # Get current count
        current_logs = session.execute(text("SELECT COUNT(*) FROM nutrition_logs")).scalar()
        print(f"  Current nutrition logs: {current_logs}")
        
        # Add 1000 more nutrition logs
        students = session.execute(text("SELECT id FROM students LIMIT 500")).fetchall()
        
        for i in range(1000):
            if i % 100 == 0:
                print(f"    Processing nutrition log {i+1}/1000")
                session.commit()
            
            try:
                student = random.choice(students)
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
                    'meal_type': random.choice(["Breakfast", "Lunch", "Dinner", "Snack"]),
                    'food_items': random.choice(["Apple", "Sandwich", "Salad", "Milk"]),
                    'calories': random.randint(200, 600),
                    'protein': round(random.uniform(10, 30), 1),
                    'carbs': round(random.uniform(20, 60), 1),
                    'fat': round(random.uniform(5, 25), 1),
                    'fiber': round(random.uniform(2, 10), 1),
                    'sugar': round(random.uniform(5, 20), 1),
                    'sodium': random.randint(100, 800),
                    'notes': f"Nutrition log {i+1}",
                    'created_at': datetime.now(),
                    'updated_at': datetime.now()
                })
                
            except Exception as e:
                print(f"    Error with nutrition log {i+1}: {e}")
                session.rollback()
                continue
        
        session.commit()
        print(f"  ✅ Added 1000 nutrition logs")
        
    except Exception as e:
        print(f"  ❌ Error in nutrition data fix: {e}")
        session.rollback()

def fix_fitness_assessments_simple(session):
    """Add fitness assessments for students without them"""
    print("💪 Adding fitness assessments...")
    
    try:
        # Get students without fitness assessments (limit to 1000)
        students = session.execute(text("""
            SELECT s.id FROM students s
            LEFT JOIN fitness_assessments fa ON s.id = fa.student_id
            WHERE fa.student_id IS NULL
            LIMIT 1000
        """)).fetchall()
        
        print(f"  Found {len(students)} students without fitness assessments")
        
        for i, student in enumerate(students):
            if i % 100 == 0:
                print(f"    Processing student {i+1}/{len(students)}")
                session.commit()
            
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
                    'push_ups': random.randint(5, 40),
                    'sit_ups': random.randint(10, 50),
                    'mile_time': round(random.uniform(6.0, 12.0), 1),
                    'flexibility': random.randint(1, 10),
                    'balance': random.randint(1, 10),
                    'coordination': random.randint(1, 10),
                    'overall_score': random.randint(1, 10),
                    'notes': f"Fitness assessment for student {student[0]}",
                    'created_at': datetime.now(),
                    'updated_at': datetime.now()
                })
                
            except Exception as e:
                print(f"    Error with student {student[0]}: {e}")
                session.rollback()
                continue
        
        session.commit()
        print(f"  ✅ Added fitness assessments for {len(students)} students")
        
    except Exception as e:
        print(f"  ❌ Error in fitness assessments fix: {e}")
        session.rollback()

def add_safety_incidents_simple(session):
    """Add safety incidents data"""
    print("🛡️ Adding safety incidents...")
    
    try:
        # Add 100 safety incidents
        students = session.execute(text("SELECT id FROM students LIMIT 200")).fetchall()
        
        for i in range(100):
            if i % 20 == 0:
                print(f"    Processing incident {i+1}/100")
                session.commit()
            
            try:
                student = random.choice(students)
                session.execute(text("""
                    INSERT INTO safety_incidents (
                        student_id, incident_date, incident_type,
                        severity_level, description, location, action_taken,
                        follow_up_required, resolved, created_at, updated_at
                    ) VALUES (
                        :student_id, :incident_date, :incident_type,
                        :severity, :description, :location, :action_taken,
                        :follow_up, :resolved, :created_at, :updated_at
                    )
                """), {
                    'student_id': student[0],
                    'incident_date': datetime.now() - timedelta(days=random.randint(1, 180)),
                    'incident_type': random.choice(["Minor Scrape", "Bruise", "Fall", "Collision"]),
                    'severity': random.choice(["Low", "Medium", "High"]),
                    'description': f"Safety incident {i+1}",
                    'location': random.choice(["Gymnasium", "Playground", "Field"]),
                    'action_taken': random.choice(["First Aid", "Ice Pack", "Bandage"]),
                    'follow_up': random.choice([True, False]),
                    'resolved': random.choice([True, False]),
                    'created_at': datetime.now(),
                    'updated_at': datetime.now()
                })
                
            except Exception as e:
                print(f"    Error with incident {i+1}: {e}")
                session.rollback()
                continue
        
        session.commit()
        print(f"  ✅ Added 100 safety incidents")
        
    except Exception as e:
        print(f"  ❌ Error in safety incidents fix: {e}")
        session.rollback()

def fix_data_consistency_simple():
    """Simple data consistency fix without loops"""
    print("🔧 SIMPLE DATA CONSISTENCY FIX")
    print("=" * 40)
    
    session = next(get_db())
    
    try:
        # Fix health data
        fix_health_data_simple(session)
        
        # Fix nutrition data
        fix_nutrition_data_simple(session)
        
        # Fix fitness assessments
        fix_fitness_assessments_simple(session)
        
        # Add safety incidents
        add_safety_incidents_simple(session)
        
        print("\n✅ SIMPLE DATA CONSISTENCY FIX COMPLETED!")
        print("=" * 40)
        
        # Final verification
        total_students = session.execute(text("SELECT COUNT(*) FROM students")).scalar()
        health_records = session.execute(text("SELECT COUNT(*) FROM student_health")).scalar()
        nutrition_logs = session.execute(text("SELECT COUNT(*) FROM nutrition_logs")).scalar()
        fitness_assessments = session.execute(text("SELECT COUNT(*) FROM fitness_assessments")).scalar()
        safety_incidents = session.execute(text("SELECT COUNT(*) FROM safety_incidents")).scalar()
        
        print(f"📊 FINAL RESULTS:")
        print(f"  Students: {total_students:,}")
        print(f"  Health Records: {health_records:,} ({health_records/total_students*100:.1f}%)")
        print(f"  Nutrition Logs: {nutrition_logs:,}")
        print(f"  Fitness Assessments: {fitness_assessments:,} ({fitness_assessments/total_students*100:.1f}%)")
        print(f"  Safety Incidents: {safety_incidents:,}")
        
    except Exception as e:
        print(f"❌ Error during data consistency fix: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    fix_data_consistency_simple()
