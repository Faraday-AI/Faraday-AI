"""
Beta Teacher Student Management API Endpoints
Allows beta teachers to create and manage their own student data
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr
import uuid

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.teacher_registration import TeacherRegistration
from app.models.beta_students import BetaStudent
from app.models.physical_education.student.models import (
    GradeLevel, Gender, StudentStatus, StudentLevel, StudentCategory
)

router = APIRouter(prefix="/beta/students", tags=["Beta Teacher Students"])


# ==================== PYDANTIC SCHEMAS ====================

class StudentCreate(BaseModel):
    """Schema for creating a student"""
    first_name: str = Field(..., min_length=1, max_length=50, description="Student first name")
    last_name: str = Field(..., min_length=1, max_length=50, description="Student last name")
    email: Optional[EmailStr] = Field(None, description="Student email (optional, must be unique if provided)")
    date_of_birth: datetime = Field(..., description="Student date of birth")
    gender: Optional[str] = Field(None, description="Student gender (male, female, other)")
    grade_level: str = Field(..., description="Student grade level")
    medical_conditions: Optional[str] = Field(None, description="Medical conditions or notes")
    emergency_contact: Optional[str] = Field(None, max_length=100, description="Emergency contact information")
    parent_name: Optional[str] = Field(None, max_length=100, description="Parent/guardian name")
    parent_phone: Optional[str] = Field(None, max_length=20, description="Parent/guardian phone")
    height_cm: Optional[float] = Field(None, ge=0, description="Height in centimeters")
    weight_kg: Optional[float] = Field(None, ge=0, description="Weight in kilograms")


class StudentResponse(BaseModel):
    """Schema for student response"""
    id: str  # UUID as string
    first_name: str
    last_name: str
    email: Optional[str]
    date_of_birth: datetime
    gender: Optional[str]
    grade_level: str
    status: str
    level: str
    category: str
    medical_conditions: Optional[str]
    emergency_contact: Optional[str]
    parent_name: Optional[str]
    parent_phone: Optional[str]
    height_cm: Optional[float]
    weight_kg: Optional[float]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class StudentUpdate(BaseModel):
    """Schema for updating a student"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    email: Optional[EmailStr] = None
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    grade_level: Optional[str] = None
    status: Optional[str] = None
    level: Optional[str] = None
    category: Optional[str] = None
    medical_conditions: Optional[str] = None
    emergency_contact: Optional[str] = None
    parent_name: Optional[str] = None
    parent_phone: Optional[str] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None


# ==================== HELPER FUNCTIONS ====================

def map_grade_level(grade_str: str) -> GradeLevel:
    """Map string grade level to enum"""
    grade_map = {
        "K": GradeLevel.KINDERGARTEN,
        "1": GradeLevel.FIRST, "2": GradeLevel.SECOND, "3": GradeLevel.THIRD,
        "4": GradeLevel.FOURTH, "5": GradeLevel.FIFTH, "6": GradeLevel.SIXTH,
        "7": GradeLevel.SEVENTH, "8": GradeLevel.EIGHTH, "9": GradeLevel.NINTH,
        "10": GradeLevel.TENTH, "11": GradeLevel.ELEVENTH, "12": GradeLevel.TWELFTH,
        "kindergarten": GradeLevel.KINDERGARTEN,
        "elementary": GradeLevel.ELEMENTARY,
        "middle": GradeLevel.MIDDLE_SCHOOL,
        "high": GradeLevel.HIGH_SCHOOL,
    }
    return grade_map.get(grade_str.lower(), GradeLevel.ELEMENTARY)


def map_gender(gender_str: Optional[str]) -> Optional[Gender]:
    """Map string gender to enum"""
    if not gender_str:
        return None
    gender_map = {
        "male": Gender.MALE,
        "female": Gender.FEMALE,
        "other": Gender.OTHER,
    }
    return gender_map.get(gender_str.lower())


# ==================== STUDENT MANAGEMENT ENDPOINTS ====================

@router.post("", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
async def create_student(
    student_data: StudentCreate,
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new student for the beta teacher
    
    Beta teachers can create and manage their own student data.
    Students are associated with the teacher who creates them.
    """
    try:
        # Check if email already exists in beta_students table (if provided)
        if student_data.email:
            existing = db.query(BetaStudent).filter(BetaStudent.email == student_data.email).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Student with email {student_data.email} already exists"
                )
        
        # Generate unique email if not provided
        if not student_data.email:
            student_data.email = f"student.{uuid.uuid4().hex[:8]}@{current_teacher.email.split('@')[1] if '@' in current_teacher.email else 'beta.local'}"
            # Ensure uniqueness
            existing = db.query(BetaStudent).filter(BetaStudent.email == student_data.email).first()
            if existing:
                student_data.email = f"student.{uuid.uuid4().hex[:12]}@{current_teacher.email.split('@')[1] if '@' in current_teacher.email else 'beta.local'}"
        
        # Create beta student record (independent from district students table)
        student = BetaStudent(
            created_by_teacher_id=current_teacher.id,
            first_name=student_data.first_name,
            last_name=student_data.last_name,
            email=student_data.email,
            date_of_birth=student_data.date_of_birth,
            gender=map_gender(student_data.gender),
            grade_level=map_grade_level(student_data.grade_level),
            status=StudentStatus.ACTIVE,
            level=StudentLevel.BEGINNER,
            category=StudentCategory.REGULAR,
            medical_conditions=student_data.medical_conditions,
            emergency_contact=student_data.emergency_contact,
            parent_name=student_data.parent_name,
            parent_phone=student_data.parent_phone,
            height_cm=student_data.height_cm,
            weight_kg=student_data.weight_kg
        )
        
        db.add(student)
        db.commit()
        db.refresh(student)
        
        return StudentResponse(
            id=str(student.id),  # Convert UUID to string
            first_name=student.first_name,
            last_name=student.last_name,
            email=student.email,
            date_of_birth=student.date_of_birth,
            gender=student.gender.value if student.gender else None,
            grade_level=student.grade_level.value,
            status=student.status.value,
            level=student.level.value,
            category=student.category.value,
            medical_conditions=student.medical_conditions,
            emergency_contact=student.emergency_contact,
            parent_name=student.parent_name,
            parent_phone=student.parent_phone,
            height_cm=student.height_cm,
            weight_kg=student.weight_kg,
            created_at=student.created_at,
            updated_at=student.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create student: {str(e)}"
        )


@router.get("", response_model=List[StudentResponse])
async def get_teacher_students(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all students created/managed by the beta teacher
    
    Only returns students that belong to the authenticated teacher.
    """
    try:
        # Get all beta students created by this teacher
        students = db.query(BetaStudent).filter(
            BetaStudent.created_by_teacher_id == current_teacher.id
        ).offset(skip).limit(limit).all()
        
        return [
            StudentResponse(
                id=str(student.id),  # Convert UUID to string
                first_name=student.first_name,
                last_name=student.last_name,
                email=student.email,
                date_of_birth=student.date_of_birth,
                gender=student.gender.value if student.gender else None,
                grade_level=student.grade_level.value if student.grade_level else None,
                status=student.status.value if student.status else None,
                level=student.level.value if student.level else None,
                category=student.category.value if student.category else None,
                medical_conditions=student.medical_conditions,
                emergency_contact=student.emergency_contact,
                parent_name=student.parent_name,
                parent_phone=student.parent_phone,
                height_cm=student.height_cm,
                weight_kg=student.weight_kg,
                created_at=student.created_at,
                updated_at=student.updated_at
            )
            for student in students
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve students: {str(e)}"
        )


@router.get("/{student_id}", response_model=StudentResponse)
async def get_student(
    student_id: str,  # UUID as string
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific student by ID (only if teacher created it)"""
    try:
        # Convert string UUID to UUID object for query
        try:
            student_uuid = uuid.UUID(student_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid student ID format: {student_id}"
            )
        
        # Verify teacher created this student
        student = db.query(BetaStudent).filter(
            BetaStudent.id == student_uuid,
            BetaStudent.created_by_teacher_id == current_teacher.id
        ).first()
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Student with ID {student_id} not found"
            )
        
        return StudentResponse(
            id=str(student.id),  # Convert UUID to string
            first_name=student.first_name,
            last_name=student.last_name,
            email=student.email,
            date_of_birth=student.date_of_birth,
            gender=student.gender.value if student.gender else None,
            grade_level=student.grade_level.value,
            status=student.status.value,
            level=student.level.value,
            category=student.category.value,
            medical_conditions=student.medical_conditions,
            emergency_contact=student.emergency_contact,
            parent_name=student.parent_name,
            parent_phone=student.parent_phone,
            height_cm=student.height_cm,
            weight_kg=student.weight_kg,
            created_at=student.created_at,
            updated_at=student.updated_at
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve student: {str(e)}"
        )


@router.put("/{student_id}", response_model=StudentResponse)
async def update_student(
    student_id: str,  # UUID as string
    student_data: StudentUpdate,
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a student's information (only if teacher created it)"""
    try:
        # Convert string UUID to UUID object for query
        try:
            student_uuid = uuid.UUID(student_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid student ID format: {student_id}"
            )
        
        # Verify teacher created this student
        student = db.query(BetaStudent).filter(
            BetaStudent.id == student_uuid,
            BetaStudent.created_by_teacher_id == current_teacher.id
        ).first()
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Student with ID {student_id} not found"
            )
        
        # Update fields
        if student_data.first_name is not None:
            student.first_name = student_data.first_name
        if student_data.last_name is not None:
            student.last_name = student_data.last_name
        if student_data.email is not None:
            # Check if email is unique (excluding current student)
            # student_uuid already defined above
            existing = db.query(BetaStudent).filter(
                BetaStudent.email == student_data.email,
                BetaStudent.id != student_uuid
            ).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Email {student_data.email} already exists"
                )
            student.email = student_data.email
        if student_data.date_of_birth is not None:
            student.date_of_birth = student_data.date_of_birth
        if student_data.gender is not None:
            student.gender = map_gender(student_data.gender)
        if student_data.grade_level is not None:
            student.grade_level = map_grade_level(student_data.grade_level)
        if student_data.status is not None:
            student.status = StudentStatus[student_data.status.upper()]
        if student_data.level is not None:
            student.level = StudentLevel[student_data.level.upper()]
        if student_data.category is not None:
            student.category = StudentCategory[student_data.category.upper()]
        if student_data.medical_conditions is not None:
            student.medical_conditions = student_data.medical_conditions
        if student_data.emergency_contact is not None:
            student.emergency_contact = student_data.emergency_contact
        if student_data.parent_name is not None:
            student.parent_name = student_data.parent_name
        if student_data.parent_phone is not None:
            student.parent_phone = student_data.parent_phone
        if student_data.height_cm is not None:
            student.height_cm = student_data.height_cm
        if student_data.weight_kg is not None:
            student.weight_kg = student_data.weight_kg
        
        student.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(student)
        
        return StudentResponse(
            id=str(student.id),  # Convert UUID to string
            first_name=student.first_name,
            last_name=student.last_name,
            email=student.email,
            date_of_birth=student.date_of_birth,
            gender=student.gender.value if student.gender else None,
            grade_level=student.grade_level.value,
            status=student.status.value,
            level=student.level.value,
            category=student.category.value,
            medical_conditions=student.medical_conditions,
            emergency_contact=student.emergency_contact,
            parent_name=student.parent_name,
            parent_phone=student.parent_phone,
            height_cm=student.height_cm,
            weight_kg=student.weight_kg,
            created_at=student.created_at,
            updated_at=student.updated_at
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update student: {str(e)}"
        )


@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_student(
    student_id: str,  # UUID as string
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a student (only if teacher created it)"""
    try:
        # Convert string UUID to UUID object for query
        try:
            student_uuid = uuid.UUID(student_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid student ID format: {student_id}"
            )
        
        # Verify teacher created this student
        student = db.query(BetaStudent).filter(
            BetaStudent.id == student_uuid,
            BetaStudent.created_by_teacher_id == current_teacher.id
        ).first()
        
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Student with ID {student_id} not found or you don't have access"
            )
        
        # Delete the student (cascade will handle related records if any)
        db.delete(student)
        db.commit()
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete student: {str(e)}"
        )

