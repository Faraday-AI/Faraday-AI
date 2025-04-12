from datetime import datetime
from app.services.physical_education.models.student import Student

async def seed_students(session):
    """Seed the students table with initial data."""
    students = [
        {
            "id": "STU001",
            "name": "John Smith",
            "email": "john.smith@example.com",
            "grade": "5",
            "age": 11,
            "medical_conditions": {"asthma": "mild", "allergies": ["peanuts"]},
            "fitness_level": "intermediate"
        },
        {
            "id": "STU002",
            "name": "Emily Johnson",
            "email": "emily.johnson@example.com",
            "grade": "6",
            "age": 12,
            "medical_conditions": None,
            "fitness_level": "advanced"
        },
        {
            "id": "STU003",
            "name": "Michael Brown",
            "email": "michael.brown@example.com",
            "grade": "5",
            "age": 11,
            "medical_conditions": {"asthma": "moderate"},
            "fitness_level": "beginner"
        },
        {
            "id": "STU004",
            "name": "Sarah Davis",
            "email": "sarah.davis@example.com",
            "grade": "6",
            "age": 12,
            "medical_conditions": None,
            "fitness_level": "intermediate"
        },
        {
            "id": "STU005",
            "name": "David Wilson",
            "email": "david.wilson@example.com",
            "grade": "5",
            "age": 11,
            "medical_conditions": {"diabetes": "type 1"},
            "fitness_level": "intermediate"
        },
        {
            "id": "STU006",
            "name": "Jessica Taylor",
            "email": "jessica.taylor@example.com",
            "grade": "6",
            "age": 12,
            "medical_conditions": None,
            "fitness_level": "advanced"
        },
        {
            "id": "STU007",
            "name": "Robert Anderson",
            "email": "robert.anderson@example.com",
            "grade": "5",
            "age": 11,
            "medical_conditions": None,
            "fitness_level": "beginner"
        },
        {
            "id": "STU008",
            "name": "Jennifer Martinez",
            "email": "jennifer.martinez@example.com",
            "grade": "6",
            "age": 12,
            "medical_conditions": {"asthma": "mild"},
            "fitness_level": "intermediate"
        }
    ]

    for student_data in students:
        student = Student(**student_data)
        session.add(student)

    await session.flush()
    print("Students seeded successfully!") 