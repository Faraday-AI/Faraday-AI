from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.core.database import get_db
from app.models.physical_education.class_ import PhysicalEducationClass
from app.models.physical_education.student import Student
from app.models.routine import Routine
from app.models.activity import Activity
from app.models.lesson_plan import LessonPlan
from app.models.movement_analysis.analysis.movement_analysis import MovementAnalysis, MovementPattern
from app.models.physical_education.pe_enums.pe_types import ClassStatus

class ClassService:
    """Service for managing physical education classes and related operations."""
    
    def __init__(self, db: Session):
        self.db = db

    def create_class(self, class_data: Dict[str, Any]) -> PhysicalEducationClass:
        """
        Create a new physical education class.
        
        Args:
            class_data: Dictionary containing class details including:
                - name: str
                - description: str
                - grade_level: str
                - max_students: int
                - schedule: str
                - location: str
                - status: ClassStatus
        
        Returns:
            PhysicalEducationClass: The created class object
        """
        class_ = PhysicalEducationClass(**class_data)
        self.db.add(class_)
        self.db.commit()
        self.db.refresh(class_)
        return class_

    def get_class(self, class_id: int) -> Optional[PhysicalEducationClass]:
        """
        Retrieve a class by its ID.
        
        Args:
            class_id: The ID of the class to retrieve
            
        Returns:
            Optional[PhysicalEducationClass]: The class if found, None otherwise
        """
        return self.db.query(PhysicalEducationClass).filter(PhysicalEducationClass.id == class_id).first()

    def get_classes_by_grade(self, grade_level: str) -> List[PhysicalEducationClass]:
        """
        Retrieve all classes for a specific grade level.
        
        Args:
            grade_level: The grade level to filter by
            
        Returns:
            List[PhysicalEducationClass]: List of classes for the grade level
        """
        return self.db.query(PhysicalEducationClass).filter(PhysicalEducationClass.grade_level == grade_level).all()

    def get_classes_by_status(self, status: ClassStatus) -> List[PhysicalEducationClass]:
        """
        Retrieve all classes with a specific status.
        
        Args:
            status: The class status to filter by
            
        Returns:
            List[PhysicalEducationClass]: List of classes with the specified status
        """
        return self.db.query(PhysicalEducationClass).filter(PhysicalEducationClass.status == status).all()

    def update_class(self, class_id: int, class_data: Dict[str, Any]) -> Optional[PhysicalEducationClass]:
        """
        Update an existing class.
        
        Args:
            class_id: The ID of the class to update
            class_data: Dictionary containing updated class details
            
        Returns:
            Optional[PhysicalEducationClass]: The updated class if found, None otherwise
        """
        class_ = self.get_class(class_id)
        if class_:
            for key, value in class_data.items():
                setattr(class_, key, value)
            self.db.commit()
            self.db.refresh(class_)
        return class_

    def delete_class(self, class_id: int) -> bool:
        """
        Delete a class and its associated records.
        
        Args:
            class_id: The ID of the class to delete
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        class_ = self.get_class(class_id)
        if class_:
            self.db.delete(class_)
            self.db.commit()
            return True
        return False

    def enroll_student(self, class_id: int, student_id: str) -> bool:
        """
        Enroll a student in a class.
        
        Args:
            class_id: The ID of the class
            student_id: The ID of the student
            
        Returns:
            bool: True if enrollment was successful, False otherwise
        """
        try:
            # Check if class exists and has space
            class_ = self.get_class(class_id)
            if not class_:
                return False
                
            current_enrollment = self.db.query(ClassStudent).filter(
                ClassStudent.class_id == class_id
            ).count()
            
            if current_enrollment >= class_.max_students:
                return False
                
            # Check if student is already enrolled
            existing_enrollment = self.db.query(ClassStudent).filter(
                ClassStudent.class_id == class_id,
                ClassStudent.student_id == student_id
            ).first()
            
            if existing_enrollment:
                return False
                
            # Create enrollment
            enrollment = ClassStudent(
                class_id=class_id,
                student_id=student_id
            )
            self.db.add(enrollment)
            self.db.commit()
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e

    def remove_student(self, class_id: int, student_id: str) -> bool:
        """
        Remove a student from a class.
        
        Args:
            class_id: The ID of the class
            student_id: The ID of the student
            
        Returns:
            bool: True if removal was successful, False otherwise
        """
        try:
            enrollment = self.db.query(ClassStudent).filter(
                ClassStudent.class_id == class_id,
                ClassStudent.student_id == student_id
            ).first()
            
            if not enrollment:
                return False
                
            self.db.delete(enrollment)
            self.db.commit()
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e

    def get_students(self, class_id: int) -> List[Student]:
        """
        Get all students enrolled in a class.
        
        Args:
            class_id: The ID of the class
            
        Returns:
            List[Student]: List of enrolled students
        """
        class_ = self.get_class(class_id)
        if class_:
            return [enrollment.student for enrollment in class_.student_enrollments]
        return []

    def get_student_classes(self, student_id: str) -> List[PhysicalEducationClass]:
        """
        Get all classes a student is enrolled in.
        
        Args:
            student_id: The ID of the student
            
        Returns:
            List[PhysicalEducationClass]: List of enrolled classes
        """
        return self.db.query(PhysicalEducationClass).join(
            ClassStudent
        ).filter(
            ClassStudent.student_id == student_id
        ).all()

    def get_class_routines(self, class_id: int) -> List[Routine]:
        """
        Get all routines associated with a class.
        
        Args:
            class_id: The ID of the class
            
        Returns:
            List[Routine]: List of class routines
        """
        return self.db.query(Routine).filter(
            Routine.class_id == class_id
        ).all() 