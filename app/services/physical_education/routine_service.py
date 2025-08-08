from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.routine import (
    Routine, 
    RoutineActivity
)
from app.models.physical_education.pe_enums.pe_types import (
    RoutineType,
    RoutineStatus,
    DifficultyLevel
)
from app.models.physical_education.class_ import PhysicalEducationClass
from app.models.student import Student
from app.core.database import get_db
from app.models.activity import Activity

class RoutineService:
    """Service for managing physical education routines and related operations."""
    
    def __init__(self, db: Session):
        self.db = db

    def create_routine(self, routine_data: Dict[str, Any]) -> Routine:
        """
        Create a new physical education routine.
        
        Args:
            routine_data: Dictionary containing routine details including:
                - name: str
                - description: str
                - class_id: int
                - focus_areas: List[str]
                - status: RoutineStatus
                - activities: List[Dict] (optional) containing:
                    - activity_id: int
                    - order: int
                    - duration_minutes: int
                    - activity_type: str
        
        Returns:
            Routine: The created routine object
        """
        try:
            # Extract activities if present
            activities = routine_data.pop('activities', [])
            
            # Create the routine
            routine = Routine(**routine_data)
            self.db.add(routine)
            self.db.flush()  # Get the routine ID
            
            # Add activities if provided
            if activities:
                for activity_data in activities:
                    routine_activity = RoutineActivity(
                        routine_id=routine.id,
                        **activity_data
                    )
                    self.db.add(routine_activity)
            
            self.db.commit()
            return routine
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e

    def get_routine(self, routine_id: int) -> Optional[Routine]:
        """
        Retrieve a routine by its ID.
        
        Args:
            routine_id: The ID of the routine to retrieve
            
        Returns:
            Optional[Routine]: The routine if found, None otherwise
        """
        return self.db.query(Routine).filter(Routine.id == routine_id).first()

    def get_routines_by_class(self, class_id: int) -> List[Routine]:
        """
        Retrieve all routines for a specific class.
        
        Args:
            class_id: The ID of the class
            
        Returns:
            List[Routine]: List of routines for the class
        """
        return self.db.query(Routine).filter(Routine.class_id == class_id).all()

    def get_routines_by_status(self, status: RoutineStatus) -> List[Routine]:
        """
        Retrieve all routines with a specific status.
        
        Args:
            status: The routine status to filter by
            
        Returns:
            List[Routine]: List of routines with the specified status
        """
        return self.db.query(Routine).filter(Routine.status == status).all()

    def update_routine(self, routine_id: int, routine_data: Dict[str, Any]) -> Optional[Routine]:
        """
        Update an existing routine.
        
        Args:
            routine_id: The ID of the routine to update
            routine_data: Dictionary containing updated routine details
            
        Returns:
            Optional[Routine]: The updated routine if found, None otherwise
        """
        try:
            routine = self.get_routine(routine_id)
            if not routine:
                return None
                
            # Extract activities if present
            activities = routine_data.pop('activities', None)
            
            # Update routine fields
            for key, value in routine_data.items():
                setattr(routine, key, value)
            
            # Update activities if provided
            if activities is not None:
                # Remove existing activities
                self.db.query(RoutineActivity).filter(
                    RoutineActivity.routine_id == routine_id
                ).delete()
                
                # Add new activities
                for activity_data in activities:
                    routine_activity = RoutineActivity(
                        routine_id=routine_id,
                        **activity_data
                    )
                    self.db.add(routine_activity)
            
            self.db.commit()
            return routine
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e

    def delete_routine(self, routine_id: int) -> bool:
        """
        Delete a routine and its associated records.
        
        Args:
            routine_id: The ID of the routine to delete
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        try:
            routine = self.get_routine(routine_id)
            if not routine:
                return False
                
            # Delete associated records
            self.db.query(RoutineActivity).filter(
                RoutineActivity.routine_id == routine_id
            ).delete()
            
            self.db.delete(routine)
            self.db.commit()
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e

    def add_activity_to_routine(
        self,
        routine_id: int,
        activity_id: int,
        order: int,
        duration_minutes: int,
        activity_type: str
    ) -> bool:
        """
        Add an activity to a routine.
        
        Args:
            routine_id: The ID of the routine
            activity_id: The ID of the activity
            order: The order of the activity in the routine
            duration_minutes: The duration of the activity
            activity_type: The type of activity (warm-up, main, cool-down)
            
        Returns:
            bool: True if addition was successful, False otherwise
        """
        try:
            routine_activity = RoutineActivity(
                routine_id=routine_id,
                activity_id=activity_id,
                order=order,
                duration_minutes=duration_minutes,
                activity_type=activity_type
            )
            self.db.add(routine_activity)
            self.db.commit()
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e

    def remove_activity_from_routine(self, routine_id: int, activity_id: int) -> bool:
        """
        Remove an activity from a routine.
        
        Args:
            routine_id: The ID of the routine
            activity_id: The ID of the activity
            
        Returns:
            bool: True if removal was successful, False otherwise
        """
        try:
            routine_activity = self.db.query(RoutineActivity).filter(
                RoutineActivity.routine_id == routine_id,
                RoutineActivity.activity_id == activity_id
            ).first()
            
            if not routine_activity:
                return False
                
            self.db.delete(routine_activity)
            self.db.commit()
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e

    def get_routine_activities(self, routine_id: int) -> List[Activity]:
        """
        Get all activities in a routine.
        
        Args:
            routine_id: The ID of the routine
            
        Returns:
            List[Activity]: List of activities in the routine
        """
        return self.db.query(Activity).join(
            RoutineActivity
        ).filter(
            RoutineActivity.routine_id == routine_id
        ).order_by(
            RoutineActivity.order
        ).all()

    def get_routine_class(self, routine_id: int) -> Optional[PhysicalEducationClass]:
        """
        Get the class associated with a routine.
        
        Args:
            routine_id: The ID of the routine
            
        Returns:
            Optional[PhysicalEducationClass]: The associated class if found, None otherwise
        """
        routine = self.get_routine(routine_id)
        if not routine:
            return None
        return self.db.query(PhysicalEducationClass).filter(PhysicalEducationClass.id == routine.class_id).first() 