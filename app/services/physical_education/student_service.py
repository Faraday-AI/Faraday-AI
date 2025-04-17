from typing import List, Optional
from fastapi import Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.physical_education.models.student import Student
from app.services.physical_education.student_manager import StudentManager

class StudentService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
        self.student_manager = StudentManager(db)

    async def create_student(
        self,
        first_name: str,
        last_name: str,
        email: str,
        date_of_birth: str,
        gender: str,
        grade_level: str,
        medical_conditions: Optional[List[str]] = None,
        allergies: Optional[List[str]] = None,
        emergency_contact: Optional[dict] = None,
        student_metadata: Optional[dict] = None
    ) -> Student:
        """Create a new student."""
        return await self.student_manager.create_student(
            first_name=first_name,
            last_name=last_name,
            email=email,
            date_of_birth=date_of_birth,
            gender=gender,
            grade_level=grade_level,
            medical_conditions=medical_conditions,
            allergies=allergies,
            emergency_contact=emergency_contact,
            student_metadata=student_metadata
        )

    async def get_student(self, student_id: str) -> Optional[Student]:
        """Get a student by ID."""
        return await self.student_manager.get_student(student_id)

    async def get_students_by_class(self, class_id: str) -> List[Student]:
        """Get all students in a class."""
        return await self.student_manager.get_students_by_class(class_id)

    async def update_student(
        self,
        student_id: str,
        **kwargs
    ) -> Optional[Student]:
        """Update a student."""
        return await self.student_manager.update_student(student_id, **kwargs)

    async def delete_student(self, student_id: str) -> bool:
        """Delete a student."""
        return await self.student_manager.delete_student(student_id)

    async def get_student_activities(self, student_id: str) -> List[dict]:
        """Get all activities for a student."""
        return await self.student_manager.get_student_activities(student_id)

    async def get_student_progress(self, student_id: str) -> dict:
        """Get progress metrics for a student."""
        return await self.student_manager.get_student_progress(student_id)

    async def get_student_assessments(self, student_id: str) -> List[dict]:
        """Get all assessments for a student."""
        return await self.student_manager.get_student_assessments(student_id)

    async def get_student_incidents(self, student_id: str) -> List[dict]:
        """Get all safety incidents for a student."""
        return await self.student_manager.get_student_incidents(student_id)

def get_student_service(db: Session = Depends(get_db)) -> StudentService:
    """Dependency injection for StudentService."""
    return StudentService(db) 