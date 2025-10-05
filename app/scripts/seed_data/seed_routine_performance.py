from datetime import datetime, timedelta
import random
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select
import signal

from app.models.routine import Routine, RoutineActivity, RoutinePerformance
from app.models.physical_education.student import Student
from app.models.physical_education.class_ import PhysicalEducationClass

def seed_routine_performance(session: Session) -> int:
    """Seed routine performance data with comprehensive district coverage."""
    print("Starting routine performance seeding...")
    print("⏱️  This step may take a moment...")
    
    # Set timeout for this function (10 minutes)
    def timeout_handler(signum, frame):
        raise TimeoutError("Routine performance seeding timed out after 10 minutes")
    
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(600)  # 10 minutes
    
    try:
        # Clear existing performance data
        session.execute(RoutinePerformance.__table__.delete())
        session.commit()
        
        print("🔄 Processing routines and creating performance records...")
        
        # Get routines (limit to avoid memory issues)
        print("  Getting routines...")
        routines = session.execute(select(Routine.id, Routine.name, Routine.duration)).fetchall()
        print(f"  Found {len(routines)} routines")
        
        if not routines:
            print("  No routines found, skipping performance creation")
            return 0
        
        # Get students (limit to 50 for performance)
        print("  Getting students...")
        students = session.execute(select(Student.id, Student.grade_level).limit(50)).fetchall()
        print(f"  Using {len(students)} students")
        
        if not students:
            print("  No students found, skipping performance creation")
            return 0
        
        # Get classes (limit to 50 for performance - increased from 20)
        print("  Getting classes...")
        classes = session.execute(select(PhysicalEducationClass.id, PhysicalEducationClass.name, PhysicalEducationClass.grade_level).limit(50)).fetchall()
        print(f"  Using {len(classes)} classes")
        
        if not classes:
            print("  No classes found, skipping performance creation")
            return 0
        
        print("  Creating performance records...")
        performance_count = 0
        
        # Create comprehensive performance data
        performance_scenarios = [
            # Regular PE class performances
            {"frequency": 0.4, "performance_levels": ["EXCELLENT", "GOOD", "SATISFACTORY"], "score_range": (75, 95)},
            # Advanced class performances
            {"frequency": 0.3, "performance_levels": ["EXCELLENT", "GOOD"], "score_range": (80, 98)},
            # Special needs adaptations
            {"frequency": 0.2, "performance_levels": ["GOOD", "SATISFACTORY", "NEEDS_IMPROVEMENT"], "score_range": (60, 85)},
            # Athletic program performances
            {"frequency": 0.1, "performance_levels": ["EXCELLENT", "GOOD"], "score_range": (85, 100)}
        ]
        
        # Create performance records for each routine
        for routine_idx, routine in enumerate(routines):
            print(f"    Processing routine {routine_idx + 1}/{len(routines)}...")
            
            # Determine how many students will perform this routine
            # More popular routines get more performances (reduced scale)
            routine_popularity = random.uniform(0.1, 0.3)  # Reduced from 0.3-1.0 to 0.1-0.3
            num_performances = int(len(students) * routine_popularity)
            
            # Select students for this routine
            selected_students = random.sample(students, min(num_performances, len(students)))
            
            for student in selected_students:
                # Select performance scenario based on student grade and class type
                student_grade = student[1]
                if student_grade in ["KINDERGARTEN", "FIRST", "SECOND"]:
                    scenario = performance_scenarios[0]  # Regular PE
                elif student_grade in ["THIRD", "FOURTH", "FIFTH"]:
                    scenario = random.choices(performance_scenarios, weights=[0.5, 0.3, 0.15, 0.05])[0]
                elif student_grade in ["SIXTH", "SEVENTH", "EIGHTH"]:
                    scenario = random.choices(performance_scenarios, weights=[0.4, 0.3, 0.2, 0.1])[0]
                else:  # High school
                    scenario = random.choices(performance_scenarios, weights=[0.3, 0.3, 0.2, 0.2])[0]
                
                # Create performance record
                performance = RoutinePerformance(
                    routine_id=routine[0],
                    student_id=student[0],
                    completion_time=random.uniform(0.8, 1.2) * routine[2],  # 80-120% of routine duration
                    energy_level=random.randint(6, 10),  # 6-10 scale
                    difficulty_rating=random.randint(4, 8),  # 4-8 scale
                    notes=f"Performance of {routine[1]} by student in grade {student[1]} with scenario {scenario['performance_levels'][0]}"
                )
                
                session.add(performance)
                performance_count += 1
                
                # Flush every 50 records to manage memory
                if performance_count % 50 == 0:
                    session.flush()
                    print(f"      Created {performance_count} performance records...")
        
        print("  Committing all performance records...")
        session.commit()
        
        print(f"✅ Routine performance seeded successfully! Created {performance_count} performance records")
        
        # Cancel the alarm
        signal.alarm(0)
        return performance_count
        
    except TimeoutError:
        print("⚠️  Routine performance seeding timed out, committing what we have...")
        session.commit()
        final_count = session.execute(select(RoutinePerformance)).count()
        print(f"✅ Created {final_count} performance records before timeout")
        signal.alarm(0)
        return final_count
        
    except Exception as e:
        print(f"❌ Error in routine performance seeding: {e}")
        session.rollback()
        signal.alarm(0)
        return 0