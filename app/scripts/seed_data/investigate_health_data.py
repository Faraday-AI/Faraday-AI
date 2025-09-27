#!/usr/bin/env python3
"""
Investigate Health Data Issues
Check student_health table and foreign key relationships
"""

import sys
import os
sys.path.insert(0, '/app')

from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.database import SessionLocal

def investigate_health_data():
    """Investigate the health data issues"""
    print("="*70)
    print("🔍 INVESTIGATING HEALTH DATA ISSUES")
    print("="*70)
    
    session = SessionLocal()
    try:
        # Check student counts
        student_count = session.execute(text("SELECT COUNT(*) FROM students")).scalar()
        student_health_count = session.execute(text("SELECT COUNT(*) FROM student_health")).scalar()
        
        print(f"📊 Total students: {student_count:,}")
        print(f"📊 Students with health records: {student_health_count:,}")
        
        if student_health_count > 0:
            # Check student_health ID range
            result = session.execute(text("SELECT MIN(student_id) as min_id, MAX(student_id) as max_id FROM student_health")).fetchone()
            print(f"📊 student_health ID range: {result[0]} to {result[1]}")
            
            # Check students ID range
            result = session.execute(text("SELECT MIN(id) as min_id, MAX(id) as max_id FROM students")).fetchone()
            print(f"📊 students ID range: {result[0]} to {result[1]}")
            
            # Check for gaps
            missing_health = session.execute(text("""
                SELECT COUNT(*) FROM students s 
                LEFT JOIN student_health sh ON s.id = sh.student_id 
                WHERE sh.student_id IS NULL
            """)).scalar()
            print(f"📊 Students missing health records: {missing_health:,}")
            
            # Sample some student_health IDs
            sample_ids = session.execute(text("SELECT student_id FROM student_health ORDER BY student_id LIMIT 10")).fetchall()
            print(f"📊 Sample student_health IDs: {[row[0] for row in sample_ids]}")
            
            # Check if these IDs exist in students table
            for row in sample_ids:
                student_id = row[0]
                exists = session.execute(text("SELECT COUNT(*) FROM students WHERE id = :id"), {"id": student_id}).scalar()
                print(f"  Student ID {student_id}: {'EXISTS' if exists else 'MISSING'} in students table")
        
        # Check fitness_assessments current state
        fitness_count = session.execute(text("SELECT COUNT(*) FROM fitness_assessments")).scalar()
        print(f"📊 Current fitness_assessments: {fitness_count:,}")
        
        # Check student_health_fitness_goals current state
        goals_count = session.execute(text("SELECT COUNT(*) FROM student_health_fitness_goals")).scalar()
        print(f"📊 Current student_health_fitness_goals: {goals_count:,}")
        
    except Exception as e:
        print(f"❌ Error investigating: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    investigate_health_data()
