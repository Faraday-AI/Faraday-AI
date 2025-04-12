from datetime import datetime
from app.services.physical_education.models.class_ import ClassStudent

async def seed_class_students(session):
    """Seed the class_students table with initial data."""
    class_students = [
        # Grade 5 Regular PE (PE501)
        {"class_id": "PE501", "student_id": "STU001", "enrollment_date": datetime.now(), "status": "active"},
        {"class_id": "PE501", "student_id": "STU003", "enrollment_date": datetime.now(), "status": "active"},
        {"class_id": "PE501", "student_id": "STU005", "enrollment_date": datetime.now(), "status": "active"},
        {"class_id": "PE501", "student_id": "STU007", "enrollment_date": datetime.now(), "status": "active"},
        
        # Grade 6 Regular PE (PE601)
        {"class_id": "PE601", "student_id": "STU002", "enrollment_date": datetime.now(), "status": "active"},
        {"class_id": "PE601", "student_id": "STU004", "enrollment_date": datetime.now(), "status": "active"},
        {"class_id": "PE601", "student_id": "STU006", "enrollment_date": datetime.now(), "status": "active"},
        {"class_id": "PE601", "student_id": "STU008", "enrollment_date": datetime.now(), "status": "active"},
        
        # Grade 5 Advanced PE (PE502)
        {"class_id": "PE502", "student_id": "STU001", "enrollment_date": datetime.now(), "status": "active"},
        {"class_id": "PE502", "student_id": "STU005", "enrollment_date": datetime.now(), "status": "active"},
        
        # Grade 6 Advanced PE (PE602)
        {"class_id": "PE602", "student_id": "STU002", "enrollment_date": datetime.now(), "status": "active"},
        {"class_id": "PE602", "student_id": "STU006", "enrollment_date": datetime.now(), "status": "active"}
    ]

    for class_student_data in class_students:
        class_student = ClassStudent(**class_student_data)
        session.add(class_student)

    await session.flush()
    print("Class students seeded successfully!") 