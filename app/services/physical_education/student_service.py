from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import Depends
from app.core.database import get_db
from app.core.monitoring import track_metrics
from app.services.physical_education import service_integration
from app.models.student import (
    Student,
    HealthMetricThreshold,
    StudentHealthFitnessGoal,
    StudentHealthGoalProgress,
    StudentHealthGoalRecommendation
)
from app.models.health_fitness.metrics.health import HealthMetric, HealthMetricHistory
from app.models.physical_education.pe_enums.pe_types import (
    Gender,
    FitnessLevel,
    GoalType,
    GoalStatus,
    GoalCategory,
    GoalTimeframe
)
from app.models.core.core_models import (
    MetricType,
    MeasurementUnit
)
from app.services.physical_education.student_manager import StudentManager
from app.models.movement_analysis.analysis.movement_analysis import MovementAnalysis, MovementPattern

class StudentService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
        self.student_manager = StudentManager()
        self.student_manager.db = db  # Set the db after initialization

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
        return await self.student_manager.create_student_profile(
            student_id=email,  # Using email as student_id
            first_name=first_name,
            last_name=last_name,
            grade_level=grade_level,
            date_of_birth=datetime.fromisoformat(date_of_birth),
            medical_conditions=medical_conditions or [],
            emergency_contact=emergency_contact or {}
        )

    async def get_student(self, student_id: str) -> Optional[Student]:
        """Get a student by ID."""
        return self.student_manager.students.get(student_id)

    async def get_students_by_class(self, class_id: str) -> List[Student]:
        """Get all students in a class."""
        class_data = self.student_manager.classes.get(class_id, {})
        return class_data.get('students', [])

    async def update_student(
        self,
        student_id: str,
        **kwargs
    ) -> Optional[Student]:
        """Update a student."""
        if student_id in self.student_manager.students:
            student = self.student_manager.students[student_id]
            student.update(kwargs)
            student['last_updated'] = datetime.now().isoformat()
            return student
        return None

    async def delete_student(self, student_id: str) -> bool:
        """Delete a student."""
        if student_id in self.student_manager.students:
            del self.student_manager.students[student_id]
            return True
        return False

    async def get_student_activities(self, student_id: str) -> List[dict]:
        """Get all activities for a student."""
        progress_records = self.student_manager.progress_records.get(student_id, {})
        return progress_records.get('activities', [])

    async def get_student_progress(self, student_id: str) -> dict:
        """Get progress metrics for a student."""
        return await self.student_manager.generate_progress_report(
            student_id=student_id,
            class_id=None,  # TODO: Get class_id from student data
            start_date=datetime.now() - timedelta(days=30),
            end_date=datetime.now()
        )

    async def get_student_assessments(self, student_id: str) -> List[dict]:
        """Get all assessments for a student."""
        student = self.student_manager.students.get(student_id, {})
        return student.get('assessments', [])

    async def get_student_incidents(self, student_id: str) -> List[dict]:
        """Get all safety incidents for a student."""
        student = self.student_manager.students.get(student_id, {})
        return student.get('incidents', [])

def get_student_service(db: Session = Depends(get_db)) -> StudentService:
    """Dependency injection for StudentService."""
    return StudentService(db) 