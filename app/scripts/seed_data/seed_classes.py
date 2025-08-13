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
    """Seed the classes table with comprehensive and realistic initial data."""
    
    # First delete all class_students records
    session.execute(ClassStudent.__table__.delete())
    
    # Then delete all classes
    session.execute(PhysicalEducationClass.__table__.delete())
    
    # Set up dates for the school year
    current_year = datetime.now().year
    start_date = datetime(current_year, 9, 1)  # September 1st
    end_date = datetime(current_year + 1, 6, 15)  # June 15th next year

    classes = [
        # REGULAR PHYSICAL EDUCATION CLASSES
        {
            "id": 501,
            "name": "Grade 5 Physical Education",
            "description": "Comprehensive physical education class for 5th grade students covering fundamental movement skills, team sports, and fitness concepts",
            "class_type": ClassType.REGULAR,
            "teacher_id": 1,
            "grade_level": GradeLevel.FIFTH,
            "max_students": 30,
            "schedule": str({
                "monday": {"start": "09:00", "end": "10:00", "location": "Gymnasium A"},
                "wednesday": {"start": "09:00", "end": "10:00", "location": "Gymnasium A"},
                "friday": {"start": "09:00", "end": "10:00", "location": "Gymnasium A"}
            }),
            "location": "Gymnasium A",
            "start_date": start_date,
            "end_date": end_date,
            "curriculum_focus": "Fundamental movement skills, team sports, fitness",
            "assessment_methods": "Skill demonstrations, fitness tests, participation",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "id": 601,
            "name": "Grade 6 Physical Education",
            "description": "Comprehensive physical education class for 6th grade students building on 5th grade skills with more complex activities",
            "class_type": ClassType.REGULAR,
            "teacher_id": 1,
            "grade_level": GradeLevel.SIXTH,
            "max_students": 30,
            "schedule": str({
                "tuesday": {"start": "10:00", "end": "11:00", "location": "Gymnasium B"},
                "thursday": {"start": "10:00", "end": "11:00", "location": "Gymnasium B"}
            }),
            "location": "Gymnasium B",
            "start_date": start_date,
            "end_date": end_date,
            "curriculum_focus": "Advanced movement skills, team sports, fitness assessment",
            "assessment_methods": "Skill demonstrations, fitness tests, game play",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        
        # ADVANCED PHYSICAL EDUCATION CLASSES
        {
            "id": 502,
            "name": "Grade 5 Advanced PE",
            "description": "Advanced physical education for 5th grade students who demonstrate exceptional skills and interest in physical activities",
            "class_type": ClassType.ADVANCED,
            "teacher_id": 1,
            "grade_level": GradeLevel.FIFTH,
            "max_students": 20,
            "schedule": str({
                "monday": {"start": "14:00", "end": "15:00", "location": "Gymnasium A"},
                "wednesday": {"start": "14:00", "end": "15:00", "location": "Gymnasium A"}
            }),
            "location": "Gymnasium A",
            "start_date": start_date,
            "end_date": end_date,
            "curriculum_focus": "Advanced skills, competitive games, leadership development",
            "assessment_methods": "Advanced skill assessments, leadership evaluation, competitive performance",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "id": 602,
            "name": "Grade 6 Advanced PE",
            "description": "Advanced physical education for 6th grade students focusing on competitive sports and advanced fitness training",
            "class_type": ClassType.ADVANCED,
            "teacher_id": 1,
            "grade_level": GradeLevel.SIXTH,
            "max_students": 20,
            "schedule": str({
                "tuesday": {"start": "14:00", "end": "15:00", "location": "Gymnasium B"},
                "thursday": {"start": "14:00", "end": "15:00", "location": "Gymnasium B"}
            }),
            "location": "Gymnasium B",
            "start_date": start_date,
            "end_date": end_date,
            "curriculum_focus": "Competitive sports, advanced fitness, sports psychology",
            "assessment_methods": "Competitive performance, fitness benchmarks, mental preparation",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        
        # SPECIALIZED PHYSICAL EDUCATION CLASSES
        {
            "id": 503,
            "name": "Adaptive Physical Education",
            "description": "Specialized physical education class designed for students with diverse learning needs and physical abilities",
            "class_type": ClassType.SPECIAL_NEEDS,
            "teacher_id": 1,
            "grade_level": GradeLevel.FIFTH,
            "max_students": 15,
            "schedule": str({
                "monday": {"start": "11:00", "end": "12:00", "location": "Adaptive PE Room"},
                "wednesday": {"start": "11:00", "end": "12:00", "location": "Adaptive PE Room"},
                "friday": {"start": "11:00", "end": "12:00", "location": "Adaptive PE Room"}
            }),
            "location": "Adaptive PE Room",
            "start_date": start_date,
            "end_date": end_date,
            "curriculum_focus": "Individualized movement skills, adaptive sports, confidence building",
            "assessment_methods": "Individual progress tracking, adaptive assessments, personal goals",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "id": 603,
            "name": "Fitness and Wellness",
            "description": "Specialized class focusing on fitness, nutrition, and overall wellness for students interested in health sciences",
            "class_type": ClassType.ADVANCED,
            "teacher_id": 1,
            "grade_level": GradeLevel.SIXTH,
            "max_students": 25,
            "schedule": str({
                "tuesday": {"start": "13:00", "end": "14:00", "location": "Fitness Center"},
                "thursday": {"start": "13:00", "end": "14:00", "location": "Fitness Center"}
            }),
            "location": "Fitness Center",
            "start_date": start_date,
            "end_date": end_date,
            "curriculum_focus": "Fitness training, nutrition education, wellness practices",
            "assessment_methods": "Fitness assessments, nutrition knowledge, wellness journal",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        
        # SPORTS-SPECIFIC CLASSES
        {
            "id": 504,
            "name": "Basketball Skills Development",
            "description": "Specialized basketball class focusing on fundamental skills, game strategies, and team play",
            "class_type": ClassType.ATHLETIC,
            "teacher_id": 1,
            "grade_level": GradeLevel.FIFTH,
            "max_students": 20,
            "schedule": str({
                "monday": {"start": "15:00", "end": "16:00", "location": "Basketball Court"},
                "wednesday": {"start": "15:00", "end": "16:00", "location": "Basketball Court"}
            }),
            "location": "Basketball Court",
            "start_date": start_date,
            "end_date": end_date,
            "curriculum_focus": "Basketball fundamentals, game strategies, team dynamics",
            "assessment_methods": "Skill demonstrations, game performance, teamwork evaluation",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "id": 604,
            "name": "Soccer Academy",
            "description": "Comprehensive soccer program covering technical skills, tactical understanding, and physical conditioning",
            "class_type": ClassType.ATHLETIC,
            "teacher_id": 1,
            "grade_level": GradeLevel.SIXTH,
            "max_students": 22,
            "schedule": str({
                "tuesday": {"start": "15:00", "end": "16:00", "location": "Soccer Field"},
                "thursday": {"start": "15:00", "end": "16:00", "location": "Soccer Field"}
            }),
            "location": "Soccer Field",
            "start_date": start_date,
            "end_date": end_date,
            "curriculum_focus": "Soccer techniques, tactical awareness, physical fitness",
            "assessment_methods": "Technical skills, tactical understanding, fitness levels",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        
        # SUMMER/EXTENDED LEARNING CLASSES
        {
            "id": 505,
            "name": "Summer Sports Camp",
            "description": "Intensive summer program covering multiple sports and fitness activities for motivated students",
            "class_type": ClassType.RECREATIONAL,
            "teacher_id": 1,
            "grade_level": GradeLevel.FIFTH,
            "max_students": 25,
            "schedule": str({
                "monday": {"start": "08:00", "end": "11:00", "location": "Multiple Venues"},
                "tuesday": {"start": "08:00", "end": "11:00", "location": "Multiple Venues"},
                "wednesday": {"start": "08:00", "end": "11:00", "location": "Multiple Venues"},
                "thursday": {"start": "08:00", "end": "11:00", "location": "Multiple Venues"},
                "friday": {"start": "08:00", "end": "11:00", "location": "Multiple Venues"}
            }),
            "location": "Multiple Venues",
            "start_date": datetime(current_year, 7, 1),
            "end_date": datetime(current_year, 7, 31),
            "curriculum_focus": "Multi-sport exposure, intensive training, skill development",
            "assessment_methods": "Daily participation, skill improvement, sportsmanship",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
    ]

    # Create and add classes
    for class_data in classes:
        pe_class = PhysicalEducationClass(**class_data)
        session.add(pe_class)

    session.commit()
    
    # Verify classes were created
    result = session.execute(text("SELECT COUNT(*) FROM physical_education_classes"))
    count = result.scalar()
    print(f"Classes seeded successfully! Total classes in database: {count}")
    
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