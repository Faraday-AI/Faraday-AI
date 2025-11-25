"""
Base Admin-Aware Service Class

This is the PRODUCTION-READY base service class that all services should inherit from.
It provides automatic admin-aware query building, ensuring admin users have access
to all data across all 545 tables while regular users only see their own data.

USAGE:
    from app.services.base_admin_service import BaseAdminService
    
    class MyService(BaseAdminService):
        def __init__(self, db: Session, current_user: Optional[User] = None, 
                     current_teacher: Optional[TeacherRegistration] = None):
            super().__init__(db, current_user, current_teacher)
        
        def get_items(self):
            # Automatically handles admin filtering
            query = self.build_admin_query(
                db.query(MyModel),
                MyModel.user_id,
                self.current_user_id
            )
            return query.all()
"""

from typing import Optional, TypeVar, Generic, List, Dict, Any, Union
from sqlalchemy.orm import Query, Session
from sqlalchemy import Column
from app.models.core.user import User
from app.models.teacher_registration import TeacherRegistration
from app.utils.admin_check import is_admin_user, build_filtered_query, get_admin_context

T = TypeVar('T')


class BaseAdminService:
    """
    Base service class with automatic admin-aware query building.
    
    This class ensures that:
    - Admin users automatically get access to ALL data (all 545 tables)
    - Regular users only see their own data (filtered by user_id/teacher_id)
    - No manual admin checks needed in service methods
    - Consistent behavior across all services
    """
    
    def __init__(
        self,
        db: Session,
        current_user: Optional[User] = None,
        current_teacher: Optional[TeacherRegistration] = None,
        current_user_id: Optional[Union[int, str]] = None,
        current_teacher_id: Optional[Union[int, str]] = None
    ):
        """
        Initialize base admin service.
        
        Args:
            db: Database session
            current_user: Current User model (preferred)
            current_teacher: Current TeacherRegistration model
            current_user_id: Current user ID (if User model not available)
            current_teacher_id: Current teacher ID (if TeacherRegistration not available)
        """
        self.db = db
        self.current_user = current_user
        self.current_teacher = current_teacher
        self.current_user_id = current_user_id
        self.current_teacher_id = current_teacher_id
        
        # Get admin context once at initialization
        self._admin_context = get_admin_context(
            teacher_registration=current_teacher,
            user=current_user,
            db=db
        )
        self.is_admin = self._admin_context['is_admin']
        self.db_user = self._admin_context['db_user']
    
    def build_admin_query(
        self,
        query: Query,
        filter_column: Column,
        filter_value: Union[int, str]
    ) -> Query:
        """
        Build a query that automatically handles admin filtering.
        
        PRODUCTION PATTERN: Use this in all service methods.
        
        Args:
            query: Base SQLAlchemy query
            filter_column: Column to filter by (e.g., BetaStudent.created_by_teacher_id)
            filter_value: Value to filter by (e.g., teacher.id)
            
        Returns:
            Query filtered by user/teacher ID (for regular users) or unfiltered (for admins)
            
        Example:
            def get_students(self):
                base_query = self.db.query(BetaStudent)
                query = self.build_admin_query(
                    base_query,
                    BetaStudent.created_by_teacher_id,
                    self.current_teacher_id
                )
                return query.all()
        """
        return build_filtered_query(
            query,
            filter_column,
            filter_value,
            user=self.current_user,
            db_user=self.db_user,
            teacher_registration=self.current_teacher,
            db=self.db
        )
    
    def get_all_if_admin(self, query: Query, filter_column: Column, filter_value: Union[int, str]) -> Query:
        """Alias for build_admin_query for backward compatibility."""
        return self.build_admin_query(query, filter_column, filter_value)
    
    def check_admin_access(self) -> bool:
        """Check if current user is admin. Cached for performance."""
        return self.is_admin
    
    def get_user_context(self) -> Dict[str, Any]:
        """Get full user context including admin status."""
        return {
            'user': self.current_user,
            'db_user': self.db_user,
            'teacher': self.current_teacher,
            'user_id': self.current_user_id or (self.db_user.id if self.db_user else None),
            'teacher_id': self.current_teacher_id or (str(self.current_teacher.id) if self.current_teacher else None),
            'is_admin': self.is_admin,
            'email': self._admin_context.get('email')
        }

