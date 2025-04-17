from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.physical_education.models.class_ import Class
from app.services.physical_education.models.class_types import ClassStatus
from app.services.physical_education.models.student import Student
from app.services.physical_education.models.routine import Routine
from app.services.physical_education.services.class_service import ClassService
from pydantic import BaseModel, Field, ConfigDict

router = APIRouter(prefix="/classes", tags=["classes"])

class ClassBase(BaseModel):
    """Base model for class data."""
    name: str
    description: str
    grade_level: str
    max_students: int
    schedule: str
    location: str
    status: ClassStatus

class ClassCreate(ClassBase):
    """Model for creating a new class."""
    pass

class ClassUpdate(ClassBase):
    """Model for updating an existing class."""
    name: Optional[str] = None
    description: Optional[str] = None
    grade_level: Optional[str] = None
    max_students: Optional[int] = None
    schedule: Optional[str] = None
    location: Optional[str] = None
    status: Optional[ClassStatus] = None

class ClassResponse(ClassBase):
    """Model for class response."""
    id: int
    created_at: str
    updated_at: str

    model_config = ConfigDict(from_attributes=True)

@router.post("/", response_model=ClassResponse)
def create_class(class_: ClassCreate, db: Session = Depends(get_db)):
    """Create a new physical education class."""
    service = ClassService(db)
    try:
        return service.create_class(class_.model_dump())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{class_id}", response_model=ClassResponse)
def get_class(class_id: int, db: Session = Depends(get_db)):
    """Get a class by ID."""
    service = ClassService(db)
    class_ = service.get_class(class_id)
    if not class_:
        raise HTTPException(status_code=404, detail="Class not found")
    return class_

@router.get("/", response_model=List[ClassResponse])
def get_classes(
    grade_level: Optional[str] = None,
    status: Optional[ClassStatus] = None,
    db: Session = Depends(get_db)
):
    """Get classes with optional filters."""
    service = ClassService(db)
    
    if grade_level:
        return service.get_classes_by_grade(grade_level)
    elif status:
        return service.get_classes_by_status(status)
    else:
        return service.get_all_classes()

@router.put("/{class_id}", response_model=ClassResponse)
def update_class(
    class_id: int,
    class_: ClassUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing class."""
    service = ClassService(db)
    updated_class = service.update_class(class_id, class_.model_dump(exclude_unset=True))
    if not updated_class:
        raise HTTPException(status_code=404, detail="Class not found")
    return updated_class

@router.delete("/{class_id}")
def delete_class(class_id: int, db: Session = Depends(get_db)):
    """Delete a class."""
    service = ClassService(db)
    success = service.delete_class(class_id)
    if not success:
        raise HTTPException(status_code=404, detail="Class not found")
    return {"message": "Class deleted successfully"}

@router.post("/{class_id}/enroll/{student_id}")
def enroll_student(class_id: int, student_id: str, db: Session = Depends(get_db)):
    """Enroll a student in a class."""
    service = ClassService(db)
    success = service.enroll_student(class_id, student_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to enroll student")
    return {"message": "Student enrolled successfully"}

@router.delete("/{class_id}/enroll/{student_id}")
def remove_student(class_id: int, student_id: str, db: Session = Depends(get_db)):
    """Remove a student from a class."""
    service = ClassService(db)
    success = service.remove_student(class_id, student_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to remove student")
    return {"message": "Student removed successfully"}

@router.get("/{class_id}/students", response_model=List[Student])
def get_class_students(class_id: int, db: Session = Depends(get_db)):
    """Get all students enrolled in a class."""
    service = ClassService(db)
    students = service.get_class_students(class_id)
    if not students:
        raise HTTPException(status_code=404, detail="Class not found")
    return students

@router.get("/student/{student_id}", response_model=List[ClassResponse])
def get_student_classes(student_id: str, db: Session = Depends(get_db)):
    """Get all classes a student is enrolled in."""
    service = ClassService(db)
    classes = service.get_student_classes(student_id)
    return classes

@router.get("/{class_id}/routines", response_model=List[Routine])
def get_class_routines(class_id: int, db: Session = Depends(get_db)):
    """Get all routines associated with a class."""
    service = ClassService(db)
    routines = service.get_class_routines(class_id)
    if not routines:
        raise HTTPException(status_code=404, detail="Class not found")
    return routines 