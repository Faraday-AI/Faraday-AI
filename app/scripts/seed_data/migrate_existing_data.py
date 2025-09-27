#!/usr/bin/env python3
"""
Migrate and Scale Existing Data for District Consistency
Makes existing data robust and properly scaled for a 4,000+ student district
"""

import random
from datetime import datetime, timedelta
from sqlalchemy import text
from app.db.session import get_db

def migrate_student_health_data(session):
    """Ensure all students have health records"""
    print("🏥 Migrating student health data...")
    
    try:
        # Get all students
        students = session.execute(text("SELECT id FROM students")).fetchall()
        total_students = len(students)
        print(f"  Found {total_students} students")
        
        # Get existing health records
        existing_health = session.execute(text("SELECT student_id FROM student_health")).fetchall()
        existing_student_ids = {row[0] for row in existing_health}
        print(f"  Found {len(existing_student_ids)} existing health records")
        
        # Find students without health records
        missing_health = []
        for student in students:
            if student[0] not in existing_student_ids:
                missing_health.append(student[0])
        
        print(f"  Need to create {len(missing_health)} missing health records")
        
        if not missing_health:
            print("  ✅ All students already have health records")
            return
        
        # Create health records in batches
        health_conditions = ["None", "Asthma", "Allergies", "ADHD", "Diabetes", "Other"]
        batch_size = 100
        
        for i in range(0, len(missing_health), batch_size):
            batch = missing_health[i:i + batch_size]
            health_records = []
            
            for student_id in batch:
                health_records.append({
                    'student_id': student_id,
                    'has_conditions': random.choice([True, False]),
                    'conditions': random.choice(health_conditions),
                    'emergency_name': f'Emergency Contact for Student {student_id}',
                    'emergency_phone': f'555-{random.randint(1000, 9999)}',
                    'insurance_provider': random.choice(['Blue Cross', 'Aetna', 'Cigna', 'UnitedHealth', 'None']),
                    'insurance_number': f'INS{random.randint(100000, 999999)}',
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                    'updated_at': datetime.now()
                })
            
            try:
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
                """), health_records)
                
                session.commit()
                print(f"    Created batch {i//batch_size + 1}/{(len(missing_health) + batch_size - 1)//batch_size}")
                
            except Exception as e:
                print(f"    Error creating health records batch {i//batch_size + 1}: {e}")
                session.rollback()
                continue
        
        # Final count
        final_count = session.execute(text("SELECT COUNT(*) FROM student_health")).scalar()
        print(f"  ✅ Total health records: {final_count} ({final_count/total_students*100:.1f}% of students)")
        
    except Exception as e:
        print(f"  ❌ Error migrating student health data: {e}")
        session.rollback()

def migrate_fitness_assessments_data(session):
    """Ensure all students have fitness assessments"""
    print("💪 Migrating fitness assessments data...")
    
    try:
        # Get all students
        students = session.execute(text("SELECT id FROM students")).fetchall()
        total_students = len(students)
        print(f"  Found {total_students} students")
        
        # Get existing fitness assessments
        existing_assessments = session.execute(text("SELECT user_id FROM fitness_assessments")).fetchall()
        existing_student_ids = {row[0] for row in existing_assessments}
        print(f"  Found {len(existing_student_ids)} existing fitness assessments")
        
        # Find students without fitness assessments
        missing_assessments = []
        for student in students:
            if student[0] not in existing_student_ids:
                missing_assessments.append(student[0])
        
        print(f"  Need to create {len(missing_assessments)} missing fitness assessments")
        
        if not missing_assessments:
            print("  ✅ All students already have fitness assessments")
            return
        
        # Create fitness assessments in batches
        batch_size = 100
        
        for i in range(0, len(missing_assessments), batch_size):
            batch = missing_assessments[i:i + batch_size]
            assessments = []
            
            for student_id in batch:
                assessments.append({
                    'user_id': student_id,
                    'assessment_date': datetime.now() - timedelta(days=random.randint(1, 90)),
                    'assessment_type': random.choice(['Initial', 'Progress', 'Annual']),
                    'cardiovascular_fitness': random.uniform(1, 10),
                    'muscular_strength': random.uniform(1, 10),
                    'muscular_endurance': random.uniform(1, 10),
                    'flexibility': random.uniform(1, 10),
                    'body_composition': random.uniform(1, 10),
                    'overall_score': random.uniform(1, 10),
                    'recommendations': f'Fitness recommendations for student {student_id}',
                    'notes': f'Fitness assessment notes for student {student_id}',
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 90)),
                    'updated_at': datetime.now()
                })
            
            try:
                session.execute(text("""
                    INSERT INTO fitness_assessments (
                        user_id, assessment_date, assessment_type,
                        cardiovascular_fitness, muscular_strength, muscular_endurance,
                        flexibility, body_composition, overall_score, recommendations,
                        notes, created_at, updated_at
                    ) VALUES (
                        :user_id, :assessment_date, :assessment_type,
                        :cardiovascular_fitness, :muscular_strength, :muscular_endurance,
                        :flexibility, :body_composition, :overall_score, :recommendations,
                        :notes, :created_at, :updated_at
                    )
                """), assessments)
                
                session.commit()
                print(f"    Created batch {i//batch_size + 1}/{(len(missing_assessments) + batch_size - 1)//batch_size}")
                
            except Exception as e:
                print(f"    Error creating fitness assessments batch {i//batch_size + 1}: {e}")
                session.rollback()
                continue
        
        # Final count
        final_count = session.execute(text("SELECT COUNT(*) FROM fitness_assessments")).scalar()
        print(f"  ✅ Total fitness assessments: {final_count} ({final_count/total_students*100:.1f}% of students)")
        
    except Exception as e:
        print(f"  ❌ Error migrating fitness assessments data: {e}")
        session.rollback()

def migrate_nutrition_logs_data(session):
    """Scale up nutrition logs to realistic levels"""
    print("🍽️ Migrating nutrition logs data...")
    
    try:
        # Get current count
        current_count = session.execute(text("SELECT COUNT(*) FROM nutrition_logs")).scalar()
        print(f"  Current nutrition logs: {current_count}")
        
        # Get students and food items
        students = session.execute(text("SELECT id FROM students LIMIT 1000")).fetchall()
        food_items = session.execute(text("SELECT id FROM food_items")).fetchall()
        
        if not students or not food_items:
            print("  ⚠️  No students or food items found, skipping nutrition logs migration")
            return
        
        # Target: 3 nutrition logs per student per month (realistic for a year)
        target_count = len(students) * 3 * 12  # 3 logs per month for 12 months
        needed_count = max(0, target_count - current_count)
        
        print(f"  Target nutrition logs: {target_count}")
        print(f"  Need to create: {needed_count}")
        
        if needed_count == 0:
            print("  ✅ Nutrition logs already at target level")
            return
        
        # Create additional nutrition logs in batches
        batch_size = 500
        
        for i in range(0, needed_count, batch_size):
            current_batch_size = min(batch_size, needed_count - i)
            logs = []
            
            for j in range(current_batch_size):
                student = random.choice(students)
                food_item = random.choice(food_items)
                
                logs.append({
                    'student_id': student[0],
                    'date': datetime.now() - timedelta(days=random.randint(1, 365)),
                    'meal_type': random.choice(['BREAKFAST', 'LUNCH', 'DINNER', 'SNACK']),
                    'foods_consumed': f'Food item {food_item[0]}',
                    'calories': random.uniform(50, 500),
                    'protein': random.uniform(0, 30),
                    'carbohydrates': random.uniform(0, 80),
                    'fats': random.uniform(0, 50),
                    'hydration': random.uniform(0, 100),
                    'notes': f'Nutrition log {i+j+1}',
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 365))
                })
            
            try:
                session.execute(text("""
                    INSERT INTO nutrition_logs (
                        student_id, date, meal_type, foods_consumed,
                        calories, protein, carbohydrates, fats, hydration,
                        notes, created_at
                    ) VALUES (
                        :student_id, :date, :meal_type, :foods_consumed,
                        :calories, :protein, :carbohydrates, :fats, :hydration,
                        :notes, :created_at
                    )
                """), logs)
                
                session.commit()
                print(f"    Created batch {i//batch_size + 1}/{(needed_count + batch_size - 1)//batch_size}")
                
            except Exception as e:
                print(f"    Error creating nutrition logs batch {i//batch_size + 1}: {e}")
                session.rollback()
                continue
        
        # Final count
        final_count = session.execute(text("SELECT COUNT(*) FROM nutrition_logs")).scalar()
        print(f"  ✅ Total nutrition logs: {final_count}")
        
    except Exception as e:
        print(f"  ❌ Error migrating nutrition logs data: {e}")
        session.rollback()

def migrate_safety_incidents_data(session):
    """Create realistic safety incidents data"""
    print("🛡️ Migrating safety incidents data...")
    
    try:
        # Get current count
        current_count = session.execute(text("SELECT COUNT(*) FROM safety_incidents")).scalar()
        print(f"  Current safety incidents: {current_count}")
        
        # Get students
        students = session.execute(text("SELECT id FROM students LIMIT 500")).fetchall()
        
        if not students:
            print("  ⚠️  No students found, skipping safety incidents migration")
            return
        
        # Target: 200+ safety incidents for a district this size
        target_count = 200
        needed_count = max(0, target_count - current_count)
        
        print(f"  Target safety incidents: {target_count}")
        print(f"  Need to create: {needed_count}")
        
        if needed_count == 0:
            print("  ✅ Safety incidents already at target level")
            return
        
        # Create safety incidents in batches
        incident_types = ["Minor Scrape", "Bruise", "Fall", "Collision", "Equipment Malfunction"]
        locations = ["Gymnasium", "Playground", "Field", "Track", "Pool"]
        actions = ["First Aid", "Ice Pack", "Bandage", "Called Parent", "Sent to Nurse"]
        batch_size = 50
        
        for i in range(0, needed_count, batch_size):
            current_batch_size = min(batch_size, needed_count - i)
            incidents = []
            
            for j in range(current_batch_size):
                student = random.choice(students)
                
                incidents.append({
                    'student_id': student[0],
                    'incident_date': datetime.now() - timedelta(days=random.randint(1, 180)),
                    'incident_type': random.choice(incident_types),
                    'description': f'Safety incident {i+j+1} - {random.choice(incident_types)}',
                    'location': random.choice(locations),
                    'action_taken': random.choice(actions),
                    'follow_up_required': random.choice([True, False]),
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 180)),
                    'updated_at': datetime.now()
                })
            
            try:
                session.execute(text("""
                    INSERT INTO safety_incidents (
                        student_id, incident_date, incident_type,
                        description, location, action_taken,
                        follow_up_required, created_at, updated_at
                    ) VALUES (
                        :student_id, :incident_date, :incident_type,
                        :description, :location, :action_taken,
                        :follow_up_required, :created_at, :updated_at
                    )
                """), incidents)
                
                session.commit()
                print(f"    Created batch {i//batch_size + 1}/{(needed_count + batch_size - 1)//batch_size}")
                
            except Exception as e:
                print(f"    Error creating safety incidents batch {i//batch_size + 1}: {e}")
                session.rollback()
                continue
        
        # Final count
        final_count = session.execute(text("SELECT COUNT(*) FROM safety_incidents")).scalar()
        print(f"  ✅ Total safety incidents: {final_count}")
        
    except Exception as e:
        print(f"  ❌ Error migrating safety incidents data: {e}")
        session.rollback()

def migrate_equipment_maintenance_data(session):
    """Create realistic equipment maintenance data"""
    print("🔧 Migrating equipment maintenance data...")
    
    try:
        # Get current count
        current_count = session.execute(text("SELECT COUNT(*) FROM equipment_maintenance")).scalar()
        print(f"  Current equipment maintenance records: {current_count}")
        
        # Get equipment (only use existing IDs)
        equipment = session.execute(text("SELECT id FROM physical_education_equipment")).fetchall()
        
        if not equipment:
            print("  ⚠️  No equipment found, skipping equipment maintenance migration")
            return
        
        # Target: 500+ maintenance records
        target_count = 500
        needed_count = max(0, target_count - current_count)
        
        print(f"  Target maintenance records: {target_count}")
        print(f"  Need to create: {needed_count}")
        
        if needed_count == 0:
            print("  ✅ Equipment maintenance already at target level")
            return
        
        # Create maintenance records in batches
        maintenance_types = ["Routine Check", "Cleaning", "Repair", "Replacement", "Inspection"]
        statuses = ["Scheduled", "In Progress", "Completed", "Cancelled", "Overdue"]
        batch_size = 50
        
        for i in range(0, needed_count, batch_size):
            current_batch_size = min(batch_size, needed_count - i)
            maintenance_records = []
            
            for j in range(current_batch_size):
                eq = random.choice(equipment)
                
                maintenance_records.append({
                    'equipment_id': eq[0],
                    'maintenance_type': random.choice(maintenance_types),
                    'description': f'Maintenance for equipment {eq[0]} - {random.choice(maintenance_types)}',
                    'performed_by': f'Tech {random.randint(1, 10)}',
                    'cost': random.uniform(10, 500),
                    'notes': f'Maintenance notes {i+j+1}'
                })
            
            try:
                session.execute(text("""
                    INSERT INTO equipment_maintenance (
                        equipment_id, maintenance_type, description, performed_by,
                        cost, notes
                    ) VALUES (
                        :equipment_id, :maintenance_type, :description, :performed_by,
                        :cost, :notes
                    )
                """), maintenance_records)
                
                session.commit()
                print(f"    Created batch {i//batch_size + 1}/{(needed_count + batch_size - 1)//batch_size}")
                
            except Exception as e:
                print(f"    Error creating maintenance records batch {i//batch_size + 1}: {e}")
                session.rollback()
                continue
        
        # Final count
        final_count = session.execute(text("SELECT COUNT(*) FROM equipment_maintenance")).scalar()
        print(f"  ✅ Total equipment maintenance records: {final_count}")
        
    except Exception as e:
        print(f"  ❌ Error migrating equipment maintenance data: {e}")
        session.rollback()

def migrate_existing_data():
    """Main function to migrate and scale existing data"""
    print("🔄 MIGRATING AND SCALING EXISTING DATA")
    print("=" * 50)
    print("Making existing data robust and properly scaled for district size")
    print("=" * 50)
    
    session = next(get_db())
    
    try:
        # Migrate health data
        migrate_student_health_data(session)
        
        # Migrate fitness data
        migrate_fitness_assessments_data(session)
        
        # Migrate nutrition data
        migrate_nutrition_logs_data(session)
        
        # Migrate safety data
        migrate_safety_incidents_data(session)
        
        # Migrate equipment maintenance data
        migrate_equipment_maintenance_data(session)
        
        print("\n✅ DATA MIGRATION COMPLETED!")
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
        print(f"❌ Error during data migration: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    migrate_existing_data()