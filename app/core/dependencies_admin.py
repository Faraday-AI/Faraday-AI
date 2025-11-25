"""
Admin-Aware Dependencies for FastAPI Endpoints

PRODUCTION-READY PATTERN:
Use these dependencies in all endpoints to automatically get admin context.
This ensures admin users have access to all data across all 545 tables.

USAGE:
    from app.core.dependencies_admin import get_admin_context
    
    @router.get("/items")
    async def get_items(
        admin_context: dict = Depends(get_admin_context),
        db: Session = Depends(get_db)
    ):
        if admin_context['is_admin']:
            # Return all items
            return db.query(Item).all()
        else:
            # Return filtered items
            return db.query(Item).filter(Item.user_id == admin_context['user_id']).all()
"""

from typing import Dict, Any, Optional
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.core.user import User
from app.models.teacher_registration import TeacherRegistration
from app.utils.admin_check import get_admin_context as _get_admin_context


async def get_admin_context(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    FastAPI dependency that provides admin context for endpoints.
    
    This is the RECOMMENDED way to get user context in endpoints.
    It automatically:
    - Looks up the User model from database
    - Checks admin/superuser status
    - Returns all context needed for admin-aware queries
    
    Returns:
        Dict with:
            - db_user: User model from database
            - is_admin: bool indicating admin status
            - user_id: User ID
            - email: User email
            - teacher: TeacherRegistration (if available)
            - teacher_id: TeacherRegistration ID (if available)
            
    Example:
        @router.get("/students")
        async def get_students(
            admin_context: dict = Depends(get_admin_context),
            db: Session = Depends(get_db)
        ):
            base_query = db.query(BetaStudent)
            if admin_context['is_admin']:
                # Admin: return all students
                students = base_query.all()
            else:
                # Regular teacher: filter by teacher_id
                students = base_query.filter(
                    BetaStudent.created_by_teacher_id == admin_context['teacher_id']
                ).all()
            return students
    """
    try:
        # Get User model from database
        db_user = db.query(User).filter(User.email == current_user.email).first()
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found in database"
            )
        
        # Get TeacherRegistration if available
        teacher = db.query(TeacherRegistration).filter(
            TeacherRegistration.email == current_user.email
        ).first()
        
        # Get admin context
        context = _get_admin_context(
            user=db_user,
            teacher_registration=teacher,
            db=db,
            email=current_user.email
        )
        
        # Add additional context
        context['user_id'] = db_user.id
        context['teacher'] = teacher
        context['teacher_id'] = str(teacher.id) if teacher else None
        
        return context
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting admin context: {str(e)}"
        )


async def get_admin_context_from_teacher(
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    FastAPI dependency for endpoints that use TeacherRegistration.
    
    Use this when the endpoint dependency is TeacherRegistration instead of User.
    
    Example:
        @router.get("/beta/students")
        async def get_beta_students(
            admin_context: dict = Depends(get_admin_context_from_teacher),
            db: Session = Depends(get_db)
        ):
            base_query = db.query(BetaStudent)
            if admin_context['is_admin']:
                students = base_query.all()
            else:
                students = base_query.filter(
                    BetaStudent.created_by_teacher_id == admin_context['teacher_id']
                ).all()
            return students
    """
    try:
        # Get User model from database
        db_user = db.query(User).filter(User.email == current_teacher.email).first()
        
        # Get admin context
        context = _get_admin_context(
            db_user=db_user,
            teacher_registration=current_teacher,
            db=db,
            email=current_teacher.email
        )
        
        # Add additional context
        context['user_id'] = db_user.id if db_user else None
        context['teacher'] = current_teacher
        context['teacher_id'] = str(current_teacher.id)
        
        return context
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting admin context: {str(e)}"
        )

