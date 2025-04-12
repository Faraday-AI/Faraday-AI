from datetime import datetime, time
from app.services.physical_education.models.class_ import Class

async def seed_classes(session):
    """Seed the classes table with initial data."""
    classes = [
        {
            "id": "PE501",
            "name": "Grade 5 Physical Education",
            "description": "Physical education class for 5th grade students",
            "grade_level": "5",
            "max_students": 30,
            "schedule": {
                "monday": {"start": "09:00", "end": "10:00"},
                "wednesday": {"start": "09:00", "end": "10:00"},
                "friday": {"start": "09:00", "end": "10:00"}
            },
            "location": "Gymnasium A",
            "status": "active"
        },
        {
            "id": "PE601",
            "name": "Grade 6 Physical Education",
            "description": "Physical education class for 6th grade students",
            "grade_level": "6",
            "max_students": 30,
            "schedule": {
                "tuesday": {"start": "10:00", "end": "11:00"},
                "thursday": {"start": "10:00", "end": "11:00"}
            },
            "location": "Gymnasium B",
            "status": "active"
        },
        {
            "id": "PE502",
            "name": "Grade 5 Advanced PE",
            "description": "Advanced physical education for 5th grade students",
            "grade_level": "5",
            "max_students": 20,
            "schedule": {
                "monday": {"start": "14:00", "end": "15:00"},
                "wednesday": {"start": "14:00", "end": "15:00"}
            },
            "location": "Gymnasium A",
            "status": "active"
        },
        {
            "id": "PE602",
            "name": "Grade 6 Advanced PE",
            "description": "Advanced physical education for 6th grade students",
            "grade_level": "6",
            "max_students": 20,
            "schedule": {
                "tuesday": {"start": "14:00", "end": "15:00"},
                "thursday": {"start": "14:00", "end": "15:00"}
            },
            "location": "Gymnasium B",
            "status": "active"
        }
    ]

    for class_data in classes:
        pe_class = Class(**class_data)
        session.add(pe_class)

    await session.flush()
    print("Classes seeded successfully!") 