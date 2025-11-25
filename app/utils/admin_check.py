"""
Utility functions for checking admin/superuser status and building queries accordingly.

This module provides helper functions to check if a user is an admin or superuser,
and to build database queries that either filter by user/teacher ID (for regular users)
or return all data (for admin users).

PRODUCTION-READY PATTERN:
All services should use these utilities to ensure admin users have access to all data
across all 545 tables, while regular users only see their own data.
"""

from typing import Optional, Union, TypeVar, Type, Any, Dict
from sqlalchemy.orm import Query, Session
from sqlalchemy import Column
from app.models.core.user import User
from app.models.teacher_registration import TeacherRegistration

T = TypeVar('T')


def is_admin_user(
    user: Optional[User] = None, 
    db_user: Optional[User] = None, 
    teacher_registration: Optional[TeacherRegistration] = None,
    db: Optional[Session] = None,
    email: Optional[str] = None
) -> bool:
    """
    Check if a user is an admin or superuser.
    
    This is the PRIMARY function for checking admin status across the application.
    Use this in all services and endpoints to determine if a user should see all data.
    
    Args:
        user: User model instance
        db_user: User model from database (most reliable)
        teacher_registration: TeacherRegistration model
        db: Database session (required if checking by teacher_registration or email)
        email: User email (will lookup User from database)
        
    Returns:
        True if user is admin or superuser, False otherwise
        
    Example:
        # In an endpoint:
        db_user = db.query(User).filter(User.email == current_teacher.email).first()
        if is_admin_user(db_user=db_user):
            # Return all data
        else:
            # Return filtered data
    """
    # Check User model directly (most reliable)
    if db_user:
        return bool((db_user.role == "admin" or db_user.is_superuser) if hasattr(db_user, 'role') else False)
    
    if user:
        return bool((user.role == "admin" or user.is_superuser) if hasattr(user, 'role') else False)
    
    # Check via email lookup
    if email and db:
        try:
            db_user = db.query(User).filter(User.email == email).first()
            if db_user:
                return bool((db_user.role == "admin" or db_user.is_superuser) if hasattr(db_user, 'role') else False)
        except Exception:
            pass
    
    # Check via TeacherRegistration -> User lookup
    if teacher_registration and db:
        try:
            db_user = db.query(User).filter(
                User.email == teacher_registration.email
            ).first()
            if db_user:
                return bool((db_user.role == "admin" or db_user.is_superuser) if hasattr(db_user, 'role') else False)
        except Exception:
            pass
    
    return False


def build_filtered_query(
    query: Query,
    filter_column: Column,
    filter_value: Union[int, str],
    user: Optional[User] = None,
    db_user: Optional[User] = None,
    teacher_registration: Optional[TeacherRegistration] = None,
    db: Optional[Session] = None,
    email: Optional[str] = None
) -> Query:
    """
    Build a query that filters by user/teacher ID for regular users,
    or returns all data for admin users.
    
    PRODUCTION PATTERN: Use this in all service methods that query data.
    
    Args:
        query: Base SQLAlchemy query
        filter_column: Column to filter by (e.g., BetaStudent.created_by_teacher_id)
        filter_value: Value to filter by (e.g., teacher.id)
        user: User model instance
        db_user: User model from database (preferred)
        teacher_registration: TeacherRegistration model
        db: Database session
        email: User email (will lookup User from database)
        
    Returns:
        Query filtered by user/teacher ID (for regular users) or unfiltered (for admins)
        
    Example:
        # In a service method:
        base_query = db.query(BetaStudent)
        query = build_filtered_query(
            base_query,
            BetaStudent.created_by_teacher_id,
            current_teacher.id,
            teacher_registration=current_teacher,
            db=db
        )
        students = query.all()
    """
    if is_admin_user(
        user=user, 
        db_user=db_user, 
        teacher_registration=teacher_registration, 
        db=db,
        email=email
    ):
        # Admin: return all data (no filter) - access to all 545 tables
        return query
    else:
        # Regular user: filter by their ID
        return query.filter(filter_column == filter_value)


def get_all_if_admin(
    query: Query,
    filter_column: Column,
    filter_value: Union[int, str],
    user: Optional[User] = None,
    db_user: Optional[User] = None,
    teacher_registration: Optional[TeacherRegistration] = None,
    db: Optional[Session] = None,
    email: Optional[str] = None
) -> Query:
    """
    Alias for build_filtered_query for backward compatibility.
    """
    return build_filtered_query(
        query, filter_column, filter_value,
        user=user, db_user=db_user, teacher_registration=teacher_registration, db=db, email=email
    )


def get_admin_context(
    teacher_registration: Optional[TeacherRegistration] = None,
    user: Optional[User] = None,
    db: Optional[Session] = None,
    email: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get admin context for a user - returns both User model and admin status.
    
    This is the RECOMMENDED way to get user context in endpoints.
    It performs a single database lookup and returns everything needed.
    
    Args:
        teacher_registration: TeacherRegistration model
        user: User model instance
        db: Database session
        email: User email
        
    Returns:
        Dict with:
            - db_user: User model from database
            - is_admin: bool indicating admin status
            - email: user email
            
    Example:
        # In an endpoint:
        context = get_admin_context(
            teacher_registration=current_teacher,
            db=db
        )
        if context['is_admin']:
            # Return all data
        else:
            # Return filtered data
    """
    db_user = None
    
    # Try to get User model
    if user:
        db_user = user
    elif email and db:
        db_user = db.query(User).filter(User.email == email).first()
    elif teacher_registration and db:
        db_user = db.query(User).filter(User.email == teacher_registration.email).first()
    
    is_admin = is_admin_user(db_user=db_user, teacher_registration=teacher_registration, db=db, email=email)
    
    return {
        'db_user': db_user,
        'is_admin': is_admin,
        'email': email or (teacher_registration.email if teacher_registration else None) or (db_user.email if db_user else None)
    }

