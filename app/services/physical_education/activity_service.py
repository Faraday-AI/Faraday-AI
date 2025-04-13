from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.services.physical_education.models.activity import Activity, ActivityType, DifficultyLevel, EquipmentRequirement
from app.services.physical_education.models.exercise import Exercise
from app.services.physical_education.models.risk_assessment import RiskAssessment
from app.services.physical_education.models.activity_category_association import ActivityCategoryAssociation

class ActivityService:
    """Service for managing physical education activities and related operations."""
    
    def __init__(self, db: Session):
        self.db = db

    def create_activity(self, activity_data: Dict[str, Any]) -> Activity:
        """
        Create a new physical education activity.
        
        Args:
            activity_data: Dictionary containing activity details including:
                - name: str
                - description: str
                - activity_type: ActivityType
                - difficulty: DifficultyLevel
                - equipment_required: EquipmentRequirement
                - duration_minutes: int
                - categories: List[str] (optional)
        
        Returns:
            Activity: The created activity object
        """
        try:
            # Extract categories if present
            categories = activity_data.pop('categories', [])
            
            # Create the activity
            activity = Activity(**activity_data)
            self.db.add(activity)
            self.db.flush()  # Get the activity ID
            
            # Add categories if provided
            if categories:
                for category in categories:
                    category_assoc = ActivityCategoryAssociation(
                        activity_id=activity.id,
                        category=category
                    )
                    self.db.add(category_assoc)
            
            self.db.commit()
            return activity
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e

    def get_activity(self, activity_id: int) -> Optional[Activity]:
        """
        Retrieve an activity by its ID.
        
        Args:
            activity_id: The ID of the activity to retrieve
            
        Returns:
            Optional[Activity]: The activity if found, None otherwise
        """
        return self.db.query(Activity).filter(Activity.id == activity_id).first()

    def get_activities_by_type(self, activity_type: ActivityType) -> List[Activity]:
        """
        Retrieve all activities of a specific type.
        
        Args:
            activity_type: The type of activities to retrieve
            
        Returns:
            List[Activity]: List of activities matching the type
        """
        return self.db.query(Activity).filter(Activity.activity_type == activity_type).all()

    def get_activities_by_difficulty(self, difficulty: DifficultyLevel) -> List[Activity]:
        """
        Retrieve all activities of a specific difficulty level.
        
        Args:
            difficulty: The difficulty level to filter by
            
        Returns:
            List[Activity]: List of activities matching the difficulty level
        """
        return self.db.query(Activity).filter(Activity.difficulty == difficulty).all()

    def update_activity(self, activity_id: int, activity_data: Dict[str, Any]) -> Optional[Activity]:
        """
        Update an existing activity.
        
        Args:
            activity_id: The ID of the activity to update
            activity_data: Dictionary containing updated activity details
            
        Returns:
            Optional[Activity]: The updated activity if found, None otherwise
        """
        try:
            activity = self.get_activity(activity_id)
            if not activity:
                return None
                
            # Extract categories if present
            categories = activity_data.pop('categories', None)
            
            # Update activity fields
            for key, value in activity_data.items():
                setattr(activity, key, value)
            
            # Update categories if provided
            if categories is not None:
                # Remove existing categories
                self.db.query(ActivityCategoryAssociation).filter(
                    ActivityCategoryAssociation.activity_id == activity_id
                ).delete()
                
                # Add new categories
                for category in categories:
                    category_assoc = ActivityCategoryAssociation(
                        activity_id=activity_id,
                        category=category
                    )
                    self.db.add(category_assoc)
            
            self.db.commit()
            return activity
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e

    def delete_activity(self, activity_id: int) -> bool:
        """
        Delete an activity and its associated records.
        
        Args:
            activity_id: The ID of the activity to delete
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        try:
            activity = self.get_activity(activity_id)
            if not activity:
                return False
                
            # Delete associated records
            self.db.query(ActivityCategoryAssociation).filter(
                ActivityCategoryAssociation.activity_id == activity_id
            ).delete()
            
            self.db.delete(activity)
            self.db.commit()
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e

    def get_activity_categories(self, activity_id: int) -> List[str]:
        """
        Get all categories associated with an activity.
        
        Args:
            activity_id: The ID of the activity
            
        Returns:
            List[str]: List of category names
        """
        categories = self.db.query(ActivityCategoryAssociation.category).filter(
            ActivityCategoryAssociation.activity_id == activity_id
        ).all()
        return [category[0] for category in categories]

    def get_activities_by_category(self, category: str) -> List[Activity]:
        """
        Get all activities in a specific category.
        
        Args:
            category: The category name to filter by
            
        Returns:
            List[Activity]: List of activities in the category
        """
        return self.db.query(Activity).join(
            ActivityCategoryAssociation
        ).filter(
            ActivityCategoryAssociation.category == category
        ).all()

    def get_activities_by_equipment(self, equipment: EquipmentRequirement) -> List[Activity]:
        """
        Get all activities that match a specific equipment requirement.
        
        Args:
            equipment: The equipment requirement to filter by
            
        Returns:
            List[Activity]: List of activities matching the equipment requirement
        """
        return self.db.query(Activity).filter(
            Activity.equipment_required == equipment
        ).all()

    def get_activities_by_duration(self, max_duration: int) -> List[Activity]:
        """
        Get all activities that can be completed within a specified duration.
        
        Args:
            max_duration: Maximum duration in minutes
            
        Returns:
            List[Activity]: List of activities that can be completed within the duration
        """
        return self.db.query(Activity).filter(
            Activity.duration_minutes <= max_duration
        ).all() 