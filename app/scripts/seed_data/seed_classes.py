from datetime import datetime, time, timedelta
from app.models.physical_education.class_ import PhysicalEducationClass, ClassStudent
from app.models.core.core_models import (
    ClassType,
    StudentType
)
from app.models.physical_education.pe_enums.pe_types import ClassStatus, ClassType
from app.models.app_models import GradeLevel
from sqlalchemy import select, update, text
import random
from typing import List
from sqlalchemy.orm import Session

def seed_classes(session):
    """Seed the classes table with 170+ classes for our 6-school district structure."""
    
    # First delete all class_students records
    session.execute(ClassStudent.__table__.delete())
    
    # Then delete all classes
    session.execute(PhysicalEducationClass.__table__.delete())
    
    # Set up dates for the school year
    current_year = datetime.now().year
    start_date = datetime(current_year, 9, 1)  # September 1st
    end_date = datetime(current_year + 1, 6, 15)  # June 15th next year

    # Generate comprehensive class structure for 6 schools
    classes = []
    class_id = 1001  # Start with 1001 to avoid conflicts
    
    # Grade level mappings
    grade_mappings = {
        "K": GradeLevel.KINDERGARTEN,
        "1": GradeLevel.FIRST,
        "2": GradeLevel.SECOND,
        "3": GradeLevel.THIRD,
        "4": GradeLevel.FOURTH,
        "5": GradeLevel.FIFTH,
        "6": GradeLevel.SIXTH,
        "7": GradeLevel.SEVENTH,
        "8": GradeLevel.EIGHTH,
        "9": GradeLevel.NINTH,
        "10": GradeLevel.TENTH,
        "11": GradeLevel.ELEVENTH,
        "12": GradeLevel.TWELFTH
    }
    
    # Get actual school IDs from database
    schools_result = session.execute(text("SELECT id, name, min_grade, max_grade FROM schools ORDER BY name")).fetchall()
    if not schools_result:
        print("Warning: No schools found in database. Classes will not have school assignments.")
        return
    
    # Elementary Schools (K-5) - 80-95 Classes Total
    elementary_schools = []
    for school in schools_result:
        if school.min_grade == "K" and school.max_grade == "5":
            elementary_schools.append((school.name, f"{school.name[:3].upper()}-EL", school.id, 4))
    
    print(f"Found {len(elementary_schools)} elementary schools for class assignment")
    
    for school_name, school_code, school_id, teacher_count in elementary_schools:
        for grade in ["K", "1", "2", "3", "4", "5"]:
            # Regular PE classes (2 per grade)
            for section in ["A", "B"]:
                classes.append({
                    "id": class_id,
                    "name": f"Grade {grade} Physical Education {section}",
                    "description": f"Comprehensive physical education for {grade} grade students at {school_name}",
                    "class_type": ClassType.REGULAR,
                    "teacher_id": random.randint(1, teacher_count),
                    "grade_level": grade_mappings[grade],
                    "max_students": 25,
                    "schedule": str({
                        "monday": {"start": "09:00", "end": "10:00", "location": f"Gymnasium {section}"},
                        "wednesday": {"start": "09:00", "end": "10:00", "location": f"Gymnasium {section}"},
                        "friday": {"start": "09:00", "end": "10:00", "location": f"Gymnasium {section}"}
                    }),
                    "location": f"Gymnasium {section}",
                    "start_date": start_date,
                    "end_date": end_date,
                    "curriculum_focus": "Fundamental movement skills, team sports, fitness",
                    "assessment_methods": "Skill demonstrations, fitness tests, participation",
                    "created_at": datetime.now(),
                    "updated_at": datetime.now()
                })
                class_id += 1
            
            # Advanced PE classes (1 per grade)
            classes.append({
                "id": class_id,
                "name": f"Grade {grade} Advanced PE",
                "description": f"Advanced physical education for {grade} grade students at {school_name}",
                "class_type": ClassType.ADVANCED,
                "teacher_id": random.randint(1, teacher_count),
                "grade_level": grade_mappings[grade],
                "max_students": 20,
                "schedule": str({
                    "tuesday": {"start": "14:00", "end": "15:00", "location": "Advanced Gym"},
                    "thursday": {"start": "14:00", "end": "15:00", "location": "Advanced Gym"}
                }),
                "location": "Advanced Gym",
                "start_date": start_date,
                "end_date": end_date,
                "curriculum_focus": "Advanced skills, competitive games, leadership development",
                "assessment_methods": "Advanced skill assessments, leadership evaluation, competitive performance",
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            })
            class_id += 1
            
            # Special needs/Adaptive PE (1 per grade)
            classes.append({
                "id": class_id,
                "name": f"Grade {grade} Adaptive PE",
                "description": f"Adaptive physical education for {grade} grade students at {school_name}",
                "class_type": ClassType.SPECIAL_NEEDS,
                "teacher_id": random.randint(1, teacher_count),
                "grade_level": grade_mappings[grade],
                "max_students": 15,
                "schedule": str({
                    "monday": {"start": "10:00", "end": "11:00", "location": "Adaptive Gym"},
                    "wednesday": {"start": "10:00", "end": "11:00", "location": "Adaptive Gym"}
                }),
                "location": "Adaptive Gym",
                "start_date": start_date,
                "end_date": end_date,
                "curriculum_focus": "Adaptive movement skills, inclusive sports, individual progress",
                "assessment_methods": "Individual progress tracking, adaptive skill assessments, participation",
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            })
            class_id += 1
    
    # Springfield Middle School (6-8) - 45-55 Classes Total
    middle_school_teacher_count = 6
    for grade in ["6", "7", "8"]:
        # Regular PE classes (3 per grade)
        for section in ["A", "B", "C"]:
            classes.append({
                "id": class_id,
                "name": f"Grade {grade} Physical Education {section}",
                "description": f"Comprehensive physical education for {grade} grade students at Springfield Middle School",
                "class_type": ClassType.REGULAR,
                "teacher_id": random.randint(1, middle_school_teacher_count),
                "grade_level": grade_mappings[grade],
                "max_students": 30,
                "schedule": str({
                    "monday": {"start": "09:00", "end": "10:00", "location": f"Gymnasium {section}"},
                    "wednesday": {"start": "09:00", "end": "10:00", "location": f"Gymnasium {section}"},
                    "friday": {"start": "09:00", "end": "10:00", "location": f"Gymnasium {section}"}
                }),
                "location": f"Gymnasium {section}",
                "start_date": start_date,
                "end_date": end_date,
                "curriculum_focus": "Advanced sports skills, fitness training, competitive athletics",
                "assessment_methods": "Skill demonstrations, fitness tests, competitive performance",
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            })
            class_id += 1
        
        # Advanced PE classes (2 per grade)
        for section in ["A", "B"]:
            classes.append({
                "id": class_id,
                "name": f"Grade {grade} Advanced PE {section}",
                "description": f"Advanced physical education for {grade} grade students at Springfield Middle School",
                "class_type": ClassType.ADVANCED,
                "teacher_id": random.randint(1, middle_school_teacher_count),
                "grade_level": grade_mappings[grade],
                "max_students": 25,
                "schedule": str({
                    "tuesday": {"start": "14:00", "end": "15:00", "location": "Advanced Gym"},
                    "thursday": {"start": "14:00", "end": "15:00", "location": "Advanced Gym"}
                }),
                "location": "Advanced Gym",
                "start_date": start_date,
                "end_date": end_date,
                "curriculum_focus": "Advanced skills, competitive games, leadership development",
                "assessment_methods": "Advanced skill assessments, leadership evaluation, competitive performance",
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            })
            class_id += 1
        
        # Athletic classes (2 per grade)
        for sport in ["Basketball", "Soccer", "Track", "Volleyball"]:
            classes.append({
                "id": class_id,
                "name": f"Grade {grade} {sport} Academy",
                "description": f"{sport} academy for {grade} grade students at Springfield Middle School",
                "class_type": ClassType.ATHLETIC,
                "teacher_id": random.randint(1, middle_school_teacher_count),
                "grade_level": grade_mappings[grade],
                "max_students": 22,
                "schedule": str({
                    "tuesday": {"start": "15:00", "end": "16:00", "location": f"{sport} Court/Field"},
                    "thursday": {"start": "15:00", "end": "16:00", "location": f"{sport} Court/Field"}
                }),
                "location": f"{sport} Court/Field",
                "start_date": start_date,
                "end_date": end_date,
                "curriculum_focus": f"{sport} techniques, tactical awareness, physical fitness",
                "assessment_methods": "Technical skills, tactical understanding, fitness levels",
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            })
            class_id += 1
    
    # Springfield High School (9-12) - 45-55 Classes Total
    high_school_teacher_count = 8
    for grade in ["9", "10", "11", "12"]:
        # Regular PE classes (3 per grade)
        for section in ["A", "B", "C"]:
            classes.append({
                "id": class_id,
                "name": f"Grade {grade} Physical Education {section}",
                "description": f"Comprehensive physical education for {grade} grade students at Springfield High School",
                "class_type": ClassType.REGULAR,
                "teacher_id": random.randint(1, high_school_teacher_count),
                "grade_level": grade_mappings[grade],
                "max_students": 30,
                "schedule": str({
                    "monday": {"start": "09:00", "end": "10:00", "location": f"Gymnasium {section}"},
                    "wednesday": {"start": "09:00", "end": "10:00", "location": f"Gymnasium {section}"},
                    "friday": {"start": "09:00", "end": "10:00", "location": f"Gymnasium {section}"}
                }),
                "location": f"Gymnasium {section}",
                "start_date": start_date,
                "end_date": end_date,
                "curriculum_focus": "Advanced athletics, sports medicine, fitness science",
                "assessment_methods": "Skill demonstrations, fitness tests, competitive performance",
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            })
            class_id += 1
        
        # Advanced PE classes (2 per grade)
        for section in ["A", "B"]:
            classes.append({
                "id": class_id,
                "name": f"Grade {grade} Advanced PE {section}",
                "description": f"Advanced physical education for {grade} grade students at Springfield High School",
                "class_type": ClassType.ADVANCED,
                "teacher_id": random.randint(1, high_school_teacher_count),
                "grade_level": grade_mappings[grade],
                "max_students": 25,
                "schedule": str({
                    "tuesday": {"start": "14:00", "end": "15:00", "location": "Advanced Gym"},
                    "thursday": {"start": "14:00", "end": "15:00", "location": "Advanced Gym"}
                }),
                "location": "Advanced Gym",
                "start_date": start_date,
                "end_date": end_date,
                "curriculum_focus": "Advanced skills, competitive games, leadership development",
                "assessment_methods": "Advanced skill assessments, leadership evaluation, competitive performance",
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            })
            class_id += 1
        
        # Athletic classes (2 per grade)
        for sport in ["Basketball", "Soccer", "Track", "Volleyball", "Tennis", "Swimming"]:
            classes.append({
                "id": class_id,
                "name": f"Grade {grade} {sport} Academy",
                "description": f"{sport} academy for {grade} grade students at Springfield High School",
                "class_type": ClassType.ATHLETIC,
                "teacher_id": random.randint(1, high_school_teacher_count),
                "grade_level": grade_mappings[grade],
                "max_students": 22,
                "schedule": str({
                    "tuesday": {"start": "15:00", "end": "16:00", "location": f"{sport} Court/Field/Pool"},
                    "thursday": {"start": "15:00", "end": "16:00", "location": f"{sport} Court/Field/Pool"}
                }),
                "location": f"{sport} Court/Field/Pool",
                "start_date": start_date,
                "end_date": end_date,
                "curriculum_focus": f"{sport} techniques, tactical awareness, physical fitness",
                "assessment_methods": "Technical skills, tactical understanding, fitness levels",
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            })
            class_id += 1
    
    # Add competitive and recreational classes
    competitive_sports = ["Basketball", "Soccer", "Track", "Volleyball", "Tennis", "Swimming", "Baseball", "Softball"]
    for sport in competitive_sports:
        classes.append({
            "id": class_id,
            "name": f"Competitive {sport}",
            "description": f"Competitive {sport} program for advanced students",
            "class_type": ClassType.COMPETITIVE,
            "teacher_id": random.randint(1, high_school_teacher_count),
            "grade_level": GradeLevel.NINTH,  # Mixed grades
            "max_students": 20,
            "schedule": str({
                "monday": {"start": "15:00", "end": "17:00", "location": f"{sport} Facility"},
                "wednesday": {"start": "15:00", "end": "17:00", "location": f"{sport} Facility"},
                "friday": {"start": "15:00", "end": "17:00", "location": f"{sport} Facility"}
            }),
            "location": f"{sport} Facility",
            "start_date": start_date,
            "end_date": end_date,
            "curriculum_focus": f"Competitive {sport}, advanced techniques, tournament preparation",
            "assessment_methods": "Competitive performance, skill mastery, tournament results",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        })
        class_id += 1
    
    # Add recreational classes
    recreational_activities = ["Fitness", "Yoga", "Dance", "Martial Arts", "Rock Climbing", "Archery"]
    for activity in recreational_activities:
        classes.append({
            "id": class_id,
            "name": f"Recreational {activity}",
            "description": f"Recreational {activity} program for all skill levels",
            "class_type": ClassType.RECREATIONAL,
            "teacher_id": random.randint(1, high_school_teacher_count),
            "grade_level": GradeLevel.NINTH,  # Mixed grades
            "max_students": 25,
            "schedule": str({
                "tuesday": {"start": "16:00", "end": "17:00", "location": f"{activity} Studio"},
                "thursday": {"start": "16:00", "end": "17:00", "location": f"{activity} Studio"}
            }),
            "location": f"{activity} Studio",
            "start_date": start_date,
            "end_date": end_date,
            "curriculum_focus": f"{activity} fundamentals, fitness, stress relief",
            "assessment_methods": "Participation, skill development, fitness improvement",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        })
        class_id += 1

    # Create and add classes
    for class_data in classes:
        pe_class = PhysicalEducationClass(**class_data)
        session.add(pe_class)

    session.commit()
    
    # Verify classes were created
    result = session.execute(text("SELECT COUNT(*) FROM physical_education_classes"))
    count = result.scalar()
    print(f"Classes seeded successfully! Total classes in database: {count}")
    print(f"Expected: 170+ classes for 6-school district structure")
    
    # Print classes by type
    result = session.execute(text("SELECT id, name, class_type, grade_level, max_students FROM physical_education_classes ORDER BY id"))
    classes_data = result.fetchall()
    
    print("\nClasses by type:")
    type_groups = {}
    for class_info in classes_data:
        class_type = class_info.class_type
        if class_type not in type_groups:
            type_groups[class_type] = []
        type_groups[class_type].append(class_info)
    
    for class_type, class_list in type_groups.items():
        print(f"\n{class_type} ({len(class_list)} classes):")
        for cls in class_list:
            print(f"  - {cls.name} (Grade {cls.grade_level}, Max: {cls.max_students})")
    
    # Check for gaps in IDs
    ids = [cls.id for cls in classes_data]
    if len(ids) > 1:
        gaps = []
        for i in range(1, len(ids)):
            if ids[i] - ids[i-1] > 1:
                gaps.append(f"{ids[i-1]} to {ids[i]}")
        if gaps:
            print(f"\nGaps in class IDs: {', '.join(gaps)}")
        else:
            print("\nNo gaps in class IDs")
    
    # Create school assignments for all classes
    print("\nCreating school assignments for classes...")
    from app.models.physical_education.schools.relationships import ClassSchoolAssignment
    
    # Get current academic year
    academic_year_result = session.execute(text("SELECT academic_year FROM school_academic_years WHERE is_current = true LIMIT 1")).fetchall()
    current_academic_year = academic_year_result[0].academic_year if academic_year_result else "2025-2026"
    
    # Create assignments for each class based on their grade level
    assignments_created = 0
    for class_info in classes_data:
        # Find the appropriate school for this class's grade level
        grade_level = class_info.grade_level
        
        # Handle grade level conversion (it's an enum object from the database)
        if hasattr(grade_level, 'name'):
            # It's an enum object, get the name
            grade_name = grade_level.name
        else:
            # It's already a string
            grade_name = str(grade_level)
        
        # Convert enum names to school grade format
        if grade_name == "KINDERGARTEN":
            grade_str = "K"
        elif grade_name == "FIRST":
            grade_str = "1"
        elif grade_name == "SECOND":
            grade_str = "2"
        elif grade_name == "THIRD":
            grade_str = "3"
        elif grade_name == "FOURTH":
            grade_str = "4"
        elif grade_name == "FIFTH":
            grade_str = "5"
        elif grade_name == "SIXTH":
            grade_str = "6"
        elif grade_name == "SEVENTH":
            grade_str = "7"
        elif grade_name == "EIGHTH":
            grade_str = "8"
        elif grade_name == "NINTH":
            grade_str = "9"
        elif grade_name == "TENTH":
            grade_str = "10"
        elif grade_name == "ELEVENTH":
            grade_str = "11"
        elif grade_name == "TWELFTH":
            grade_str = "12"
        else:
            grade_str = grade_name
        
        # Find ALL schools that cover this grade for proper distribution
        if grade_str == "K":
            # Kindergarten should go to elementary schools - get ALL of them
            school_result = session.execute(text(
                "SELECT id FROM schools WHERE min_grade = 'K' ORDER BY name"
            )).fetchall()
        else:
            # Numeric grades - need to handle mixed K/numeric data properly
            try:
                grade_num = int(grade_str)
                school_result = session.execute(text(
                    """SELECT id FROM schools 
                       WHERE (min_grade != 'K' AND CAST(min_grade AS INTEGER) <= :grade) 
                       AND (max_grade != 'K' AND CAST(max_grade AS INTEGER) >= :grade) 
                       ORDER BY name"""
                ), {"grade": grade_num}).fetchall()
            except ValueError:
                # Fallback for non-numeric grades
                school_result = session.execute(text(
                    "SELECT id FROM schools WHERE min_grade = :grade OR max_grade = :grade ORDER BY name"
                ), {"grade": grade_str}).fetchall()
        
        if school_result:
            # Randomly select from available schools for better distribution
            selected_school = random.choice(school_result)
            school_id = selected_school.id
            
            # Create assignment
            assignment = ClassSchoolAssignment(
                class_id=class_info.id,
                school_id=school_id,
                academic_year=current_academic_year,
                semester="Full Year",
                status="ACTIVE"
            )
            session.add(assignment)
            assignments_created += 1
    
    session.commit()
    print(f"Created {assignments_created} class school assignments")
    
    return classes

if __name__ == "__main__":
    from app.core.database import SessionLocal
    
    session = SessionLocal()
    try:
        seed_classes(session)
    finally:
        session.close() 