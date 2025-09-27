"""
Seed Schools Data

This script creates the 6 schools for our NJ K-12 district structure.
"""

from datetime import datetime, timedelta
from app.models.physical_education.schools import (
    School, 
    SchoolFacility, 
    SchoolType, 
    SchoolStatus
)
from app.models.physical_education.schools.relationships import SchoolAcademicYear
from sqlalchemy import text
import random

def seed_schools(session):
    """Seed the schools table with our 6-school district structure."""
    
    # First delete existing schools and related data - use safer deletion
    try:
        session.execute(text("DELETE FROM school_facilities"))
    except:
        pass  # Table doesn't exist yet
    
    try:
        session.execute(text("DELETE FROM teacher_school_assignments"))
    except:
        pass  # Table doesn't exist yet
    
    try:
        session.execute(text("DELETE FROM student_school_enrollments"))
    except:
        pass  # Table doesn't exist yet
    
    try:
        session.execute(text("DELETE FROM class_school_assignments"))
    except:
        pass  # Table doesn't exist yet
    
    try:
        session.execute(text("DELETE FROM school_academic_years"))
    except:
        pass  # Table doesn't exist yet
    
    try:
        session.execute(text("DELETE FROM schools"))
    except:
        pass  # Table doesn't exist yet
    
    # Set up academic year - check if it already exists
    current_year = datetime.now().year
    academic_year = f"{current_year}-{current_year + 1}"
    
    # Check if academic year already exists
    existing_year = session.execute(text("SELECT id FROM school_academic_years WHERE academic_year = :year"), 
                                   {"year": academic_year}).fetchone()
    
    if existing_year:
        print(f"  📋 Academic year {academic_year} already exists, using existing record")
        academic_year_id = existing_year[0]
    else:
        print(f"  📝 Creating new academic year {academic_year}")
        start_date = datetime(current_year, 9, 1)  # September 1st
        end_date = datetime(current_year + 1, 6, 15)  # June 15th next year
        
        # Create academic year
        academic_year_record = SchoolAcademicYear(
            academic_year=academic_year,
            start_date=start_date,
            end_date=end_date,
            is_current=True,
            status="ACTIVE",
            description=f"Academic Year {academic_year}",
            special_events="Olympics Week, Fitness Challenge, Sports Tournament, Wellness Fair",
            notes="Standard academic year with enhanced PE programs"
        )
        session.add(academic_year_record)
        session.flush()  # Get the ID
        academic_year_id = academic_year_record.id
    
    # Create the 6 schools
    schools = [
        # Elementary Schools (K-5)
        {
            "name": "Lincoln Elementary School",
            "school_code": "LIN-EL",
            "school_type": SchoolType.ELEMENTARY,
            "status": SchoolStatus.ACTIVE,
            "address": "123 Lincoln Avenue",
            "city": "Springfield",
            "state": "NJ",
            "zip_code": "07081",
            "phone": "973-555-0101",
            "email": "lincoln@springfield.edu",
            "principal_name": "Dr. Sarah Martinez",
            "assistant_principal_name": "Mr. James Wilson",
            "enrollment_capacity": 500,
            "current_enrollment": 0,  # Will be updated when students are assigned
            "min_grade": "K",
            "max_grade": "5",
            "pe_department_head": "Ms. Jennifer Rodriguez",
            "pe_teacher_count": 0,  # Will be updated when teachers are assigned
            "pe_class_count": 0,  # Will be updated when classes are assigned
            "gymnasium_count": 1,
            "outdoor_facilities": "Playground, Basketball Court, Soccer Field, Running Track",
            "description": "Lincoln Elementary focuses on fundamental movement skills and basic sports for K-5 students.",
            "special_programs": "Adaptive PE Program, Fundamental Movement Skills, Team Sports Introduction",
            "facilities_notes": "Modern gymnasium with climbing wall, outdoor sports complex"
        },
        {
            "name": "Washington Elementary School",
            "school_code": "WAS-EL",
            "school_type": SchoolType.ELEMENTARY,
            "status": SchoolStatus.ACTIVE,
            "address": "456 Washington Street",
            "city": "Springfield",
            "state": "NJ",
            "zip_code": "07081",
            "phone": "973-555-0102",
            "email": "washington@springfield.edu",
            "principal_name": "Dr. Michael Chen",
            "assistant_principal_name": "Ms. Lisa Thompson",
            "enrollment_capacity": 450,
            "current_enrollment": 0,
            "min_grade": "K",
            "max_grade": "5",
            "pe_department_head": "Mr. David Johnson",
            "pe_teacher_count": 0,
            "pe_class_count": 0,
            "gymnasium_count": 1,
            "outdoor_facilities": "Playground, Baseball Field, Tennis Courts, Running Track",
            "description": "Washington Elementary emphasizes team sports and coordination development.",
            "special_programs": "Team Sports Academy, Coordination Development, Leadership in Sports",
            "facilities_notes": "Spacious gymnasium with multiple activity areas, outdoor sports complex"
        },
        {
            "name": "Roosevelt Elementary School",
            "school_code": "ROO-EL",
            "school_type": SchoolType.ELEMENTARY,
            "status": SchoolStatus.ACTIVE,
            "address": "789 Roosevelt Boulevard",
            "city": "Springfield",
            "state": "NJ",
            "zip_code": "07081",
            "phone": "973-555-0103",
            "email": "roosevelt@springfield.edu",
            "principal_name": "Dr. Emily Davis",
            "assistant_principal_name": "Mr. Robert Garcia",
            "enrollment_capacity": 500,
            "current_enrollment": 0,
            "min_grade": "K",
            "max_grade": "5",
            "pe_department_head": "Ms. Amanda Foster",
            "pe_teacher_count": 0,
            "pe_class_count": 0,
            "gymnasium_count": 1,
            "outdoor_facilities": "Playground, Fitness Trail, Basketball Courts, Soccer Field",
            "description": "Roosevelt Elementary focuses on fitness, wellness, and basic athletics.",
            "special_programs": "Fitness and Wellness Program, Basic Athletics, Health Education",
            "facilities_notes": "Well-equipped gymnasium with fitness center, outdoor fitness trail"
        },
        {
            "name": "Jefferson Elementary School",
            "school_code": "JEF-EL",
            "school_type": SchoolType.ELEMENTARY,
            "status": SchoolStatus.ACTIVE,
            "address": "321 Jefferson Lane",
            "city": "Springfield",
            "state": "NJ",
            "zip_code": "07081",
            "phone": "973-555-0104",
            "email": "jefferson@springfield.edu",
            "principal_name": "Dr. Patricia Brown",
            "assistant_principal_name": "Mr. Kevin Lee",
            "enrollment_capacity": 450,
            "current_enrollment": 0,
            "min_grade": "K",
            "max_grade": "5",
            "pe_department_head": "Ms. Rachel Green",
            "pe_teacher_count": 0,
            "pe_class_count": 0,
            "gymnasium_count": 1,
            "outdoor_facilities": "Adaptive Playground, Sensory Garden, Accessible Sports Court, Walking Path",
            "description": "Jefferson Elementary specializes in adaptive PE and inclusive sports programs.",
            "special_programs": "Adaptive PE Program, Inclusive Sports, Special Needs Support, Sensory Integration",
            "facilities_notes": "Fully accessible gymnasium with adaptive equipment, sensory-friendly spaces"
        },
        
        # Middle School (6-8)
        {
            "name": "Springfield Middle School",
            "school_code": "SPR-MS",
            "school_type": SchoolType.MIDDLE,
            "status": SchoolStatus.ACTIVE,
            "address": "654 Springfield Road",
            "city": "Springfield",
            "state": "NJ",
            "zip_code": "07081",
            "phone": "973-555-0201",
            "email": "middle@springfield.edu",
            "principal_name": "Dr. Christopher Anderson",
            "assistant_principal_name": "Ms. Michelle Rodriguez",
            "enrollment_capacity": 1150,
            "current_enrollment": 0,
            "min_grade": "6",
            "max_grade": "8",
            "pe_department_head": "Mr. Thomas Williams",
            "pe_teacher_count": 0,
            "pe_class_count": 0,
            "gymnasium_count": 3,
            "outdoor_facilities": "Football Field, Track and Field Complex, Tennis Courts, Basketball Courts, Soccer Fields, Baseball Complex",
            "description": "Springfield Middle School offers comprehensive programs in advanced sports skills, fitness training, competitive athletics, and leadership development.",
            "special_programs": "Advanced Sports Skills, Fitness Training, Competitive Athletics, Leadership Development, Sports Academy, Team Building",
            "facilities_notes": "Three full-size gymnasiums, weight room, sports academy center, outdoor sports complex"
        },
        
        # High School (9-12)
        {
            "name": "Springfield High School",
            "school_code": "SPR-HS",
            "school_type": SchoolType.HIGH,
            "status": SchoolStatus.ACTIVE,
            "address": "147 High School Boulevard",
            "city": "Springfield",
            "state": "NJ",
            "zip_code": "07081",
            "phone": "973-555-0301",
            "email": "high@springfield.edu",
            "principal_name": "Dr. Robert Johnson",
            "assistant_principal_name": "Ms. Lisa Chen",
            "enrollment_capacity": 1400,
            "current_enrollment": 0,
            "min_grade": "9",
            "max_grade": "12",
            "pe_department_head": "Mr. Richard Davis",
            "pe_teacher_count": 0,
            "pe_class_count": 0,
            "gymnasium_count": 4,
            "outdoor_facilities": "Football Stadium, Olympic-Size Track, Tennis Complex, Soccer Fields, Baseball Diamond, Soccer Complex, Tennis Academy, Basketball Courts, Fitness Trail",
            "description": "Springfield High School offers comprehensive programs in advanced athletics, sports medicine, fitness science, sports academies, competitive programs, and wellness initiatives.",
            "special_programs": "Advanced Athletics Program, Sports Medicine, Fitness Science, Wellness Programs, Competitive Sports, Sports Academy Program, Leadership Development",
            "facilities_notes": "Four gymnasiums, weight room, sports medicine center, sports academy center, outdoor stadium complex"
        }
    ]
    
    # Create and add schools
    created_schools = []
    for school_data in schools:
        school = School(**school_data)
        session.add(school)
        created_schools.append(school)
    
    session.flush()  # Get the IDs
    
    # Create facilities for each school
    for school in created_schools:
        if school.school_type == SchoolType.ELEMENTARY:
            # Elementary school facilities
            facilities = [
                {
                    "facility_name": "Main Gymnasium",
                    "facility_type": "Gymnasium",
                    "capacity": 30,
                    "description": "Primary PE facility with basketball hoops, volleyball nets, and climbing equipment",
                    "equipment_included": "Basketball hoops, volleyball nets, climbing wall, gymnastics mats, jump ropes",
                    "maintenance_schedule": "Monthly",
                    "last_maintenance": datetime.now() - timedelta(days=15),
                    "next_maintenance": datetime.now() + timedelta(days=15)
                },
                {
                    "facility_name": "Outdoor Playground",
                    "facility_type": "Playground",
                    "capacity": 50,
                    "description": "Outdoor play area with age-appropriate equipment",
                    "equipment_included": "Swings, slides, climbing structures, sandbox, play equipment",
                    "maintenance_schedule": "Weekly",
                    "last_maintenance": datetime.now() - timedelta(days=3),
                    "next_maintenance": datetime.now() + timedelta(days=4)
                }
            ]
        elif school.school_type == SchoolType.MIDDLE:
            # Middle school facilities
            facilities = [
                {
                    "facility_name": "Gymnasium A",
                    "facility_type": "Gymnasium",
                    "capacity": 35,
                    "description": "Primary gymnasium for team sports and fitness activities",
                    "equipment_included": "Basketball hoops, volleyball nets, badminton courts, fitness equipment",
                    "maintenance_schedule": "Bi-weekly",
                    "last_maintenance": datetime.now() - timedelta(days=10),
                    "next_maintenance": datetime.now() + timedelta(days=4)
                },
                {
                    "facility_name": "Gymnasium B",
                    "facility_type": "Gymnasium",
                    "capacity": 35,
                    "description": "Secondary gymnasium for specialized activities and smaller groups",
                    "equipment_included": "Wrestling mats, gymnastics equipment, dance studio mirrors, fitness stations",
                    "maintenance_schedule": "Bi-weekly",
                    "last_maintenance": datetime.now() - timedelta(days=12),
                    "next_maintenance": datetime.now() + timedelta(days=2)
                }
            ]
        else:  # High school
            # High school facilities
            facilities = [
                {
                    "facility_name": "Main Gymnasium",
                    "facility_type": "Gymnasium",
                    "capacity": 40,
                    "description": "Primary gymnasium for varsity sports and large group activities",
                    "equipment_included": "Basketball hoops, volleyball nets, scoreboards, bleachers, sound system",
                    "maintenance_schedule": "Weekly",
                    "last_maintenance": datetime.now() - timedelta(days=5),
                    "next_maintenance": datetime.now() + timedelta(days=2)
                },
                {
                    "facility_name": "Auxiliary Gymnasium",
                    "facility_type": "Gymnasium",
                    "capacity": 35,
                    "description": "Secondary gymnasium for PE classes and practice sessions",
                    "equipment_included": "Basketball hoops, volleyball nets, fitness equipment, weight machines",
                    "maintenance_schedule": "Weekly",
                    "last_maintenance": datetime.now() - timedelta(days=6),
                    "next_maintenance": datetime.now() + timedelta(days=1)
                },
                {
                    "facility_name": "Weight Room",
                    "facility_type": "Fitness Center",
                    "capacity": 25,
                    "description": "Fully equipped weight room for strength training and conditioning",
                    "equipment_included": "Free weights, weight machines, cardio equipment, fitness monitoring",
                    "maintenance_schedule": "Weekly",
                    "last_maintenance": datetime.now() - timedelta(days=4),
                    "next_maintenance": datetime.now() + timedelta(days=3)
                }
            ]
        
        # Add special facilities for Jefferson Elementary (Adaptive PE)
        if school.school_code == "JEF-EL":
            facilities.append({
                "facility_name": "Adaptive PE Room",
                "facility_type": "Specialized",
                "capacity": 15,
                "description": "Specialized facility for adaptive PE and special needs students",
                "equipment_included": "Adaptive equipment, sensory tools, specialized mats, therapeutic equipment",
                "maintenance_schedule": "Weekly",
                "last_maintenance": datetime.now() - timedelta(days=2),
                "next_maintenance": datetime.now() + timedelta(days=5)
            })
        
        # Create facilities
        for facility_data in facilities:
            facility = SchoolFacility(
                school_id=school.id,
                **facility_data
            )
            session.add(facility)
    
    session.commit()
    
    # Verify schools were created
    result = session.execute(text("SELECT COUNT(*) FROM schools"))
    count = result.scalar()
    print(f"Schools seeded successfully! Total schools in database: {count}")
    
    # Print schools by type
    result = session.execute(text("SELECT id, name, school_code, school_type, min_grade, max_grade, enrollment_capacity FROM schools ORDER BY school_type, name"))
    schools_data = result.fetchall()
    
    print("\nSchools by type:")
    type_groups = {}
    for school_info in schools_data:
        school_type = school_info.school_type
        if school_type not in type_groups:
            type_groups[school_type] = []
        type_groups[school_type].append(school_info)
    
    for school_type, school_list in type_groups.items():
        print(f"\n{school_type.upper()} SCHOOLS ({len(school_list)} schools):")
        for school in school_list:
            print(f"  - {school.name} ({school.school_code}) - Grades {school.min_grade}-{school.max_grade}, Capacity: {school.enrollment_capacity}")
    
    # Print facilities summary
    result = session.execute(text("SELECT COUNT(*) FROM school_facilities"))
    facility_count = result.scalar()
    print(f"\nSchool facilities created: {facility_count}")
    
    # Print academic year
    print(f"Academic year created: {academic_year} ({start_date.strftime('%B %d, %Y')} - {end_date.strftime('%B %d, %Y')})")
    
    return created_schools 