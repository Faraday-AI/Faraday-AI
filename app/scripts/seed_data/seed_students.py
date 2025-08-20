from datetime import datetime, timedelta
import random
from typing import List
from sqlalchemy.orm import Session
from app.models.core.core_models import (
    Gender, GoalType, GoalStatus,
    GoalCategory, GoalTimeframe
)
from app.models.physical_education.pe_enums.pe_types import (
    GradeLevel, StudentLevel, StudentStatus, StudentCategory
)
from app.models.physical_education.student.models import Student
from sqlalchemy import text

def seed_students(session):
    """Seed the students table with 2,500+ students for our 6-school district structure."""
    
    # First delete existing students and related data to avoid foreign key violations
    print("Clearing existing student data...")
    
    # Delete in order of dependency (child tables first, then parent tables)
    try:
        # Delete activity progressions first (they reference students)
        session.execute(text("DELETE FROM activity_progressions"))
        print("  - Cleared activity progressions")
    except Exception as e:
        print(f"  - Note: Could not clear activity progressions: {e}")
    
    try:
        # Delete activity plans (they reference students)
        session.execute(text("DELETE FROM activity_plan_activities"))
        session.execute(text("DELETE FROM activity_plans"))
        print("  - Cleared activity plans")
    except Exception as e:
        print(f"  - Note: Could not clear activity plans: {e}")
    
    try:
        # Delete class enrollments (they reference students)
        session.execute(text("DELETE FROM physical_education_class_students"))
        print("  - Cleared class enrollments")
    except Exception as e:
        print(f"  - Note: Could not clear class enrollments: {e}")
    
    # Now delete students
    session.execute(Student.__table__.delete())
    print("  - Cleared existing students")
    
    session.commit()
    print("Data clearing completed.")
    
    # Generate comprehensive student data for 6-school district
    students = []
    
    # First names for diversity
    first_names_male = [
        "James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph", "Thomas", "Christopher",
        "Charles", "Daniel", "Matthew", "Anthony", "Mark", "Donald", "Steven", "Paul", "Andrew", "Joshua",
        "Kenneth", "Kevin", "Brian", "George", "Edward", "Ronald", "Timothy", "Jason", "Jeffrey", "Ryan",
        "Jacob", "Gary", "Nicholas", "Eric", "Jonathan", "Stephen", "Larry", "Justin", "Scott", "Brandon",
        "Benjamin", "Samuel", "Frank", "Gregory", "Raymond", "Alexander", "Patrick", "Jack", "Dennis", "Jerry",
        "Tyler", "Aaron", "Jose", "Adam", "Nathan", "Henry", "Douglas", "Zachary", "Peter", "Kyle",
        "Walter", "Ethan", "Jeremy", "Harold", "Carl", "Keith", "Roger", "Gerald", "Lawrence", "Sean",
        "Christian", "Eugene", "Dylan", "Jesse", "Bryan", "Jordan", "Billy", "Joe", "Bruce", "Gabriel",
        "Logan", "Albert", "Willie", "Alan", "Juan", "Wayne", "Elijah", "Randy", "Roy", "Vincent",
        "Ralph", "Eugene", "Russell", "Bobby", "Mason", "Philip", "Johnny", "Bradley", "Dale", "Caleb"
    ]
    
    first_names_female = [
        "Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Susan", "Jessica", "Sarah", "Karen",
        "Nancy", "Lisa", "Betty", "Helen", "Sandra", "Donna", "Carol", "Ruth", "Sharon", "Michelle",
        "Laura", "Emily", "Kimberly", "Deborah", "Dorothy", "Lisa", "Nancy", "Karen", "Betty", "Helen",
        "Sandra", "Donna", "Carol", "Ruth", "Sharon", "Michelle", "Laura", "Emily", "Kimberly", "Deborah",
        "Dorothy", "Lisa", "Nancy", "Karen", "Betty", "Helen", "Sandra", "Donna", "Carol", "Ruth",
        "Sharon", "Michelle", "Laura", "Emily", "Kimberly", "Deborah", "Dorothy", "Lisa", "Nancy", "Karen",
        "Betty", "Helen", "Sandra", "Donna", "Carol", "Ruth", "Sharon", "Michelle", "Laura", "Emily",
        "Kimberly", "Deborah", "Dorothy", "Lisa", "Nancy", "Karen", "Betty", "Helen", "Sandra", "Donna",
        "Carol", "Ruth", "Sharon", "Michelle", "Laura", "Emily", "Kimberly", "Deborah", "Dorothy", "Lisa",
        "Nancy", "Karen", "Betty", "Helen", "Sandra", "Donna", "Carol", "Ruth", "Sharon", "Michelle"
    ]
    
    last_names = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
        "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
        "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson",
        "Walker", "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores", "Green",
        "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell", "Carter", "Roberts", "Gomez",
        "Phillips", "Evans", "Turner", "Diaz", "Parker", "Cruz", "Edwards", "Collins", "Reyes", "Stewart",
        "Morris", "Morales", "Murphy", "Cook", "Rogers", "Gutierrez", "Ortiz", "Morgan", "Cooper", "Peterson",
        "Bailey", "Reed", "Kelly", "Howard", "Ramos", "Kim", "Cox", "Ward", "Torres", "Peterson", "Gray",
        "Ramirez", "James", "Watson", "Brooks", "Kelly", "Sanders", "Price", "Bennett", "Wood", "Barnes",
        "Ross", "Henderson", "Coleman", "Jenkins", "Perry", "Powell", "Long", "Patterson", "Hughes", "Flores"
    ]
    
    # Medical conditions for diversity
    medical_conditions = [
        None, "Mild asthma", "Moderate asthma", "Peanut allergy", "Tree nut allergy", "Dairy allergy",
        "Type 1 diabetes", "Type 2 diabetes", "ADHD", "Dyslexia", "Mild hearing impairment",
        "Corrective lenses", "Mild scoliosis", "Joint hypermobility", "Exercise-induced asthma",
        "Seasonal allergies", "Eczema", "Mild anxiety", "Depression", "Autism spectrum disorder"
    ]
    
    # School assignments for 6 schools
    schools = [
        ("Lincoln Elementary School", 1, "K", "5"),      # school_name, school_id, min_grade, max_grade
        ("Washington Elementary School", 2, "K", "5"),
        ("Roosevelt Elementary School", 3, "K", "5"),
        ("Jefferson Elementary School", 4, "K", "5"),
        ("Springfield Middle School", 5, "6", "8"),
        ("Springfield High School", 6, "9", "12")
    ]
    
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
    
    # Generate students for each school
    student_id = 1001  # Start with 1001 to avoid conflicts
    
    for school_name, school_id, min_grade, max_grade in schools:
        # Calculate target students per school based on capacity
        if min_grade == "K" and max_grade == "5":  # Elementary
            target_students = random.randint(350, 500)
        elif min_grade == "6" and max_grade == "8":  # Middle
            target_students = random.randint(950, 1150)
        else:  # High
            target_students = random.randint(1000, 1400)
        
        # Generate students for each grade in the school
        for grade in range(int(min_grade) if min_grade != "K" else 0, int(max_grade) + 1):
            grade_str = "K" if grade == 0 else str(grade)
            # Calculate students per grade, handling kindergarten properly
            if min_grade == "K":
                students_per_grade = target_students // 6  # K, 1, 2, 3, 4, 5 = 6 grades
            elif min_grade == "6":
                students_per_grade = target_students // 3  # 6, 7, 8 = 3 grades
            else:
                students_per_grade = target_students // 4  # 9, 10, 11, 12 = 4 grades
            
            for i in range(students_per_grade):
                # Randomly select gender
                gender = random.choice([Gender.MALE, Gender.FEMALE])
                first_names = first_names_male if gender == Gender.MALE else first_names_female
                
                # Generate student data
                first_name = random.choice(first_names)
                last_name = random.choice(last_names)
                
                # Calculate age based on grade
                if grade == 0:  # Kindergarten
                    age = random.randint(5, 6)
                else:
                    age = grade + 5 + random.randint(0, 1)  # Grade + 5-6 years
                
                date_of_birth = datetime.now() - timedelta(days=age*365 + random.randint(0, 365))
                
                # Generate email
                email = f"{first_name.lower()}.{last_name.lower()}{student_id}@springfield.edu"
                
                # Randomly assign level and status
                level = random.choice([StudentLevel.BEGINNER, StudentLevel.INTERMEDIATE, StudentLevel.ADVANCED])
                status = random.choice([StudentStatus.ACTIVE, StudentStatus.ACTIVE, StudentStatus.ACTIVE, StudentStatus.INACTIVE])
                category = random.choice([StudentCategory.REGULAR, StudentCategory.REGULAR, StudentCategory.REGULAR, StudentCategory.SPECIAL_NEEDS])
                
                # Randomly assign medical conditions
                medical_condition = random.choice(medical_conditions)
                
                # Generate emergency contact and parent info
                emergency_contact = f"973-555-{random.randint(1000, 9999)}"
                parent_name = f"{random.choice(first_names_female)} {last_name}"
                parent_phone = f"973-555-{random.randint(1000, 9999)}"
                
                # Create student record
                student_data = {
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                    "date_of_birth": date_of_birth,
                    "gender": gender,
                    "grade_level": grade_mappings[grade_str],
                    "level": level,
                    "status": status,
                    "category": category,
                    "medical_conditions": medical_condition,
                    "emergency_contact": emergency_contact,
                    "parent_name": parent_name,
                    "parent_phone": parent_phone
                }
                
                students.append(student_data)
                student_id += 1

    # Create and add students in batches to avoid connection timeouts
    created_students = []
    batch_size = 500  # Process 500 students at a time
    
    for i in range(0, len(students), batch_size):
        batch = students[i:i + batch_size]
        batch_students = []
        
        for student_data in batch:
            student = Student(**student_data)
            session.add(student)
            batch_students.append(student)
        
        # Commit each batch
        session.commit()
        created_students.extend(batch_students)
        
        # Clear the session to free memory
        session.expunge_all()
        
        print(f"Processed batch {i//batch_size + 1}/{(len(students) + batch_size - 1)//batch_size} ({len(batch)} students)")
    
    # Verify students were created
    result = session.execute(text("SELECT COUNT(*) FROM students"))
    count = result.scalar()
    print(f"Students seeded successfully! Total students in database: {count}")
    print(f"Expected: 2,500+ students for 6-school district structure")
    
    # Print students by grade level
    result = session.execute(text("SELECT grade_level, COUNT(*) FROM students GROUP BY grade_level ORDER BY grade_level"))
    grade_data = result.fetchall()
    
    print("\nStudents by grade level:")
    for grade_info in grade_data:
        print(f"  - {grade_info.grade_level}: {grade_info.count} students")
    
    # Print students by school (if school_id is available)
    try:
        result = session.execute(text("SELECT school_id, COUNT(*) FROM students GROUP BY school_id ORDER BY school_id"))
        school_data = result.fetchall()
        
        print("\nStudents by school:")
        for school_info in school_data:
            school_name = "Unknown" if school_info.school_id is None else f"School {school_info.school_id}"
            print(f"  - {school_name}: {school_info.count} students")
    except:
        print("\nNote: School assignments will be created in separate relationship seeding")
    
    return created_students

if __name__ == "__main__":
    from app.core.database import SessionLocal
    
    session = SessionLocal()
    try:
        seed_students(session)
    finally:
        session.close() 