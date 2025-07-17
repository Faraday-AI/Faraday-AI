"""Tests for Student-Class relationship."""
import pytest
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from app.models.physical_education.class_ import PhysicalEducationClass, ClassStudent
from app.models.physical_education.student import Student
from app.core.database import Base, engine, get_db
from sqlalchemy.orm import Session
from app.models.student import Student as StudentModel
from app.models.physical_education.pe_enums.pe_types import StudentType
from app.models.physical_education.pe_enums.class_types import ClassStatus
from app.models.shared_base import SharedBase

@pytest.fixture(scope="function")
def db():
    SharedBase.metadata.create_all(bind=engine)
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()
        SharedBase.metadata.drop_all(bind=engine)

@pytest.mark.models
@pytest.mark.relationships
class TestStudentClassRelationship:
    """Test suite for Student-Class relationship."""

    @pytest.fixture
    def db(self, db_session):
        """Get database session."""
        return db_session

    @pytest.fixture
    def sample_class(self, db):
        """Create a sample class for testing."""
        class_ = PhysicalEducationClass(
            name="Test Physical Education Class",
            description="A test class for PE",
            grade_level="9th",
            max_students=30,
            schedule="MWF 10:00-11:00",
            location="Main Gym",
            status=ClassStatus.ACTIVE,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(class_)
        db.commit()
        db.refresh(class_)
        yield class_
        db.delete(class_)
        db.commit()

    @pytest.fixture
    def sample_student(self, db):
        """Create a sample student for testing."""
        student = StudentModel(
            id="TEST001",
            first_name="Test",
            last_name="Student",
            email="test.student@example.com",
            grade_level="9th",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(student)
        db.commit()
        db.refresh(student)
        yield student
        db.delete(student)
        db.commit()

    def test_class_student_foreign_key_constraints(self, db, sample_class, sample_student):
        """Test that foreign key constraints are enforced."""
        # Test valid enrollment
        try:
            sample_student.classes.append(sample_class)
            db.commit()
            assert len(sample_student.classes) == 1
            assert sample_student.classes[0].id == sample_class.id
        except IntegrityError:
            pytest.fail("Valid enrollment should not raise IntegrityError")

        # Test invalid class_id
        with pytest.raises(IntegrityError):
            sample_student.classes.append(PhysicalEducationClass(id=99999))
            db.commit()

    def test_class_student_cascade_delete(self, db, sample_class, sample_student):
        """Test cascade delete behavior."""
        # Add student to class
        sample_student.classes.append(sample_class)
        db.commit()

        # Verify enrollment
        assert len(sample_student.classes) == 1
        assert len(sample_class.students) == 1

        # Delete class and verify cascade
        db.delete(sample_class)
        db.commit()
        
        # Refresh student to get updated relationships
        db.refresh(sample_student)
        assert len(sample_student.classes) == 0

    def test_class_student_relationship_properties(self, db, sample_class, sample_student):
        """Test relationship properties."""
        # Test adding student to class
        sample_class.students.append(sample_student)
        db.commit()

        # Test bidirectional relationship
        assert sample_student in sample_class.students
        assert sample_class in sample_student.classes

        # Test relationship attributes
        class_student = db.query(ClassStudent).filter_by(
            class_id=sample_class.id,
            student_id=sample_student.id
        ).first()
        assert class_student is not None
        assert class_student.created_at is not None
        assert class_student.updated_at is not None

    def test_class_student_many_to_many_operations(self, db, sample_class, sample_student):
        """Test many-to-many operations."""
        # Create additional class
        second_class = PhysicalEducationClass(
            name="Second PE Class",
            description="Another test class",
            grade_level="9th",
            max_students=30,
            schedule="TTH 10:00-11:00",
            location="Secondary Gym",
            status=ClassStatus.ACTIVE,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(second_class)
        db.commit()

        # Add student to both classes
        sample_student.classes.extend([sample_class, second_class])
        db.commit()

        # Verify student in both classes
        assert len(sample_student.classes) == 2
        assert sample_class in sample_student.classes
        assert second_class in sample_student.classes

        # Remove student from first class
        sample_student.classes.remove(sample_class)
        db.commit()

        # Verify student only in second class
        assert len(sample_student.classes) == 1
        assert sample_class not in sample_student.classes
        assert second_class in sample_student.classes

        # Clean up
        db.delete(second_class)
        db.commit()

    def test_class_student_enrollment_constraints(self, db, sample_class, sample_student):
        """Test enrollment constraints."""
        # Test max students constraint
        sample_class.max_students = 1
        db.commit()

        # First enrollment should succeed
        sample_student.classes.append(sample_class)
        db.commit()

        # Create another student
        second_student = StudentModel(
            id="TEST002",
            first_name="Second",
            last_name="Student",
            email="second.student@example.com",
            grade_level="9th"
        )
        db.add(second_student)
        db.commit()

        # Second enrollment should fail due to max_students constraint
        with pytest.raises(ValueError):
            sample_class.students.append(second_student)
            db.commit()

        # Clean up
        db.delete(second_student)
        db.commit()

    def test_class_student_grade_level_validation(self, db, sample_class, sample_student):
        """Test grade level validation."""
        # Change class grade level
        sample_class.grade_level = "10th"
        db.commit()

        # Enrollment should fail due to grade level mismatch
        with pytest.raises(ValueError):
            sample_student.classes.append(sample_class)
            db.commit()

def test_create_class_student_relationship(db: Session):
    # Create a class
    class_ = PhysicalEducationClass(
        name="Test Class",
        description="Test Description",
        grade_level="9th",
        max_students=30
    )
    db.add(class_)
    db.commit()
    db.refresh(class_)

    # Create a student
    student = StudentModel(
        first_name="John",
        last_name="Doe",
        grade_level="9th"
    )
    db.add(student)
    db.commit()
    db.refresh(student)

    # Create relationship
    class_student = ClassStudent(
        class_id=class_.id,
        student_id=student.id,
        status="active"
    )
    db.add(class_student)
    db.commit()
    db.refresh(class_student)

    # Verify relationship
    assert class_student.class_id == class_.id
    assert class_student.student_id == student.id
    assert class_student.status == "active"

def test_class_student_cascade_delete(db: Session):
    # Create a class
    class_ = PhysicalEducationClass(
        name="Test Class",
        description="Test Description",
        grade_level="9th",
        max_students=30
    )
    db.add(class_)
    db.commit()
    db.refresh(class_)

    # Create a student
    student = StudentModel(
        first_name="John",
        last_name="Doe",
        grade_level="9th"
    )
    db.add(student)
    db.commit()
    db.refresh(student)

    # Create relationship
    class_student = ClassStudent(
        class_id=class_.id,
        student_id=student.id,
        status="active"
    )
    db.add(class_student)
    db.commit()

    # Delete the class
    db.delete(class_)
    db.commit()

    # Verify relationship is deleted
    assert db.query(ClassStudent).filter_by(class_id=class_.id).first() is None

def test_student_class_relationship(db: Session):
    # Create a class
    class_ = PhysicalEducationClass(
        name="Test Class",
        description="Test Description",
        grade_level="9th",
        max_students=30
    )
    db.add(class_)
    db.commit()
    db.refresh(class_)

    # Create a student
    student = StudentModel(
        first_name="John",
        last_name="Doe",
        grade_level="9th"
    )
    db.add(student)
    db.commit()
    db.refresh(student)

    # Create relationship
    class_student = ClassStudent(
        class_id=class_.id,
        student_id=student.id,
        status="active"
    )
    db.add(class_student)
    db.commit()
    db.refresh(class_student)

    # Verify bidirectional relationship
    assert student in class_.students
    assert class_ in student.classes 