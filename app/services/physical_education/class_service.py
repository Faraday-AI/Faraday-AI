from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.services.physical_education.models.class_ import Class, ClassStatus
from app.services.physical_education.models.class_student import ClassStudent
from app.services.physical_education.models.student import Student
from app.services.physical_education.models.routine import Routine

class ClassService:
    """Service for managing physical education classes and related operations."""
    
    def __init__(self, db: Session):
        self.db = db

    def create_class(self, class_data: Dict[str, Any]) -> Class:
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
            Class: The created class object
        """
        try:
            class_ = Class(**class_data)
            self.db.add(class_)
            self.db.commit()
            return class_
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e

    def get_class(self, class_id: int) -> Optional[Class]:
        """
        Retrieve a class by its ID.
        
        Args:
            class_id: The ID of the class to retrieve
            
        Returns:
            Optional[Class]: The class if found, None otherwise
        """
        return self.db.query(Class).filter(Class.id == class_id).first()

    def get_classes_by_grade(self, grade_level: str) -> List[Class]:
        """
        Retrieve all classes for a specific grade level.
        
        Args:
            grade_level: The grade level to filter by
            
        Returns:
            List[Class]: List of classes for the grade level
        """
        return self.db.query(Class).filter(Class.grade_level == grade_level).all()

    def get_classes_by_status(self, status: ClassStatus) -> List[Class]:
        """
        Retrieve all classes with a specific status.
        
        Args:
            status: The class status to filter by
            
        Returns:
            List[Class]: List of classes with the specified status
        """
        return self.db.query(Class).filter(Class.status == status).all()

    def update_class(self, class_id: int, class_data: Dict[str, Any]) -> Optional[Class]:
        """
        Update an existing class.
        
        Args:
            class_id: The ID of the class to update
            class_data: Dictionary containing updated class details
            
        Returns:
            Optional[Class]: The updated class if found, None otherwise
        """
        try:
            class_ = self.get_class(class_id)
            if not class_:
                return None
                
            for key, value in class_data.items():
                setattr(class_, key, value)
            
            self.db.commit()
            return class_
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e

    def delete_class(self, class_id: int) -> bool:
        """
        Delete a class and its associated records.
        
        Args:
            class_id: The ID of the class to delete
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        try:
            class_ = self.get_class(class_id)
            if not class_:
                return False
                
            # Delete associated records
            self.db.query(ClassStudent).filter(
                ClassStudent.class_id == class_id
            ).delete()
            
            self.db.delete(class_)
            self.db.commit()
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e

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

    def get_class_students(self, class_id: int) -> List[Student]:
        """
        Get all students enrolled in a class.
        
        Args:
            class_id: The ID of the class
            
        Returns:
            List[Student]: List of enrolled students
        """
        return self.db.query(Student).join(
            ClassStudent
        ).filter(
            ClassStudent.class_id == class_id
        ).all()

    def get_student_classes(self, student_id: str) -> List[Class]:
        """
        Get all classes a student is enrolled in.
        
        Args:
            student_id: The ID of the student
            
        Returns:
            List[Class]: List of enrolled classes
        """
        return self.db.query(Class).join(
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