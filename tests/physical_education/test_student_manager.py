import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, AsyncMock, Mock
import json
from app.services.physical_education.services.student_manager import StudentManager
from app.services.physical_education.services.assessment_system import AssessmentSystem
from app.services.physical_education.services.lesson_planner import LessonPlanner
from sqlalchemy.orm import Session
from app.models.physical_education.class_ import PhysicalEducationClass
from app.models.physical_education.student import Student
from app.core.database import Base, engine
from app.models.shared_base import SharedBase

@pytest.fixture
def student_manager():
    """Create StudentManager instance for testing."""
    manager = StudentManager()
    manager.assessment_system = Mock(spec=AssessmentSystem)
    manager.lesson_planner = Mock(spec=LessonPlanner)
    return manager

@pytest.fixture
def mock_assessment_system():
    """Create a mock AssessmentSystem."""
    return MagicMock(spec=AssessmentSystem)

@pytest.fixture
def mock_lesson_planner():
    """Create a mock LessonPlanner."""
    return MagicMock(spec=LessonPlanner)

@pytest.fixture
def sample_student_data():
    """Create sample student data."""
    return {
        "student_id": "student1",
        "first_name": "John",
        "last_name": "Doe",
        "grade_level": "5",
        "date_of_birth": datetime.now() - timedelta(days=365*10),
        "medical_conditions": ["asthma"],
        "emergency_contact": {
            "name": "Jane Doe",
            "relationship": "parent",
            "phone": "123-456-7890"
        }
    }

@pytest.fixture
def sample_class_data():
    """Create sample class data."""
    return {
        "class_id": "class1",
        "name": "Physical Education 5",
        "grade_level": "5",
        "max_size": 30,
        "schedule": {
            "days": ["Monday", "Wednesday", "Friday"],
            "time": "10:00-11:00"
        }
    }

@pytest.fixture
def mock_progress_data():
    return {
        "fitness": {
            "cardiovascular_endurance": 75,
            "muscular_strength": 80,
            "flexibility": 70,
            "body_composition": 85
        },
        "skills": {
            "locomotor_skills": 80,
            "non_locomotor_skills": 75,
            "manipulative_skills": 85
        },
        "social": {
            "teamwork": 90,
            "sportsmanship": 85,
            "leadership": 80,
            "communication": 75
        }
    }

@pytest.fixture(scope="function")
def db():
    SharedBase.metadata.create_all(bind=engine)
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()
        SharedBase.metadata.drop_all(bind=engine)

@pytest.fixture
def sample_class(db):
    class_ = PhysicalEducationClass(
        name="Test PE Class",
        description="Test Description",
        grade_level="9th",
        max_students=30
    )
    db.add(class_)
    db.commit()
    db.refresh(class_)
    return class_

@pytest.fixture
def sample_student(db):
    student = Student(
        first_name="John",
        last_name="Doe",
        grade_level="9th"
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    return student

@pytest.mark.asyncio
async def test_initialization(student_manager):
    """Test initialization of StudentManager."""
    assert student_manager.settings
    assert student_manager.progress_metrics
    assert isinstance(student_manager.assessment_system, Mock)
    assert isinstance(student_manager.lesson_planner, Mock)
    await student_manager.initialize()
    assert student_manager.students == {}
    assert student_manager.classes == {}

@pytest.mark.asyncio
async def test_create_student_profile(student_manager, sample_student_data):
    """Test creating a student profile (incorporating checks from both versions)."""
    student_manager.lesson_planner.curriculum_standards = {
        "state": {
            "grade_levels": ["5"]
        }
    }
    result = await student_manager.create_student_profile(**sample_student_data)

    assert result["student_id"] == sample_student_data["student_id"]
    assert result["first_name"] == sample_student_data["first_name"]
    assert result["last_name"] == sample_student_data["last_name"]
    assert result["grade_level"] == sample_student_data["grade_level"]
    assert result["medical_conditions"] == sample_student_data["medical_conditions"]
    assert result["emergency_contact"] == sample_student_data["emergency_contact"]
    assert result["skill_level"] == "beginner"
    assert result["attendance_rate"] == 1.0

    with pytest.raises(ValueError):
        await student_manager.create_student_profile(
            student_id="student2",
            first_name="Jane",
            last_name="Smith",
            grade_level="invalid",
            date_of_birth=datetime.now() - timedelta(days=365*10)
        )

    assert sample_student_data["student_id"] in student_manager.students
    with pytest.raises(ValueError, match="already exists"):
        await student_manager.create_student_profile(**sample_student_data)

@pytest.mark.asyncio
async def test_create_class(student_manager, sample_class_data):
    """Test creating a class (incorporating checks from both versions)."""
    result = await student_manager.create_class(**sample_class_data)

    assert result["class_id"] == sample_class_data["class_id"]
    assert result["name"] == sample_class_data["name"]
    assert result["grade_level"] == sample_class_data["grade_level"]
    assert result["max_size"] == sample_class_data["max_size"]
    assert result["current_size"] == 0
    assert result["schedule"] == sample_class_data["schedule"]

    invalid_size_data = sample_class_data.copy()
    invalid_size_data["class_id"] = "class_invalid_size"
    invalid_size_data["max_size"] = student_manager.settings["max_class_size"] + 1
    with pytest.raises(ValueError, match="exceeds maximum"):
        await student_manager.create_class(**invalid_size_data)

    with pytest.raises(ValueError):
        await student_manager.create_class(
            class_id="class_invalid_grade",
            name="Invalid Class",
            grade_level="invalid",
            max_size=30,
            schedule={"days": ["Monday"], "time": "10:00-11:00"}
        )

    assert sample_class_data["class_id"] in student_manager.classes
    with pytest.raises(ValueError):
        await student_manager.create_class(**sample_class_data)

@pytest.mark.asyncio
async def test_enroll_student(student_manager, sample_student_data, sample_class_data):
    """Test enrolling a student in a class."""
    await student_manager.create_student_profile(**sample_student_data)
    await student_manager.create_class(**sample_class_data)

    result = await student_manager.enroll_student(
        student_id=sample_student_data["student_id"],
        class_id=sample_class_data["class_id"]
    )

    assert result is True
    assert sample_student_data["student_id"] in student_manager.classes[sample_class_data["class_id"]]["students"]
    assert sample_class_data["class_id"] in student_manager.students[sample_student_data["student_id"]]["current_classes"]

    result_non_student = await student_manager.enroll_student("nonexistent", sample_class_data["class_id"])
    assert result_non_student is False

    result_non_class = await student_manager.enroll_student(sample_student_data["student_id"], "nonexistent")
    assert result_non_class is False

    result_already_enrolled = await student_manager.enroll_student(
        student_id=sample_student_data["student_id"],
        class_id=sample_class_data["class_id"]
    )
    assert result_already_enrolled is False

    full_class_data = sample_class_data.copy()
    full_class_data["class_id"] = "class_full"
    full_class_data["max_size"] = 0
    await student_manager.create_class(**full_class_data)
    result_full_class = await student_manager.enroll_student(sample_student_data["student_id"], full_class_data["class_id"])
    assert result_full_class is False

@pytest.mark.asyncio
async def test_record_attendance(student_manager, sample_student_data, sample_class_data):
    """Test recording student attendance."""
    await student_manager.create_student_profile(**sample_student_data)
    await student_manager.create_class(**sample_class_data)
    await student_manager.enroll_student(
        student_id=sample_student_data["student_id"],
        class_id=sample_class_data["class_id"]
    )

    date = datetime.now().date()
    result = await student_manager.record_attendance(
        class_id=sample_class_data["class_id"],
        student_id=sample_student_data["student_id"],
        date=date,
        present=True
    )

    assert result is True
    assert date in student_manager.attendance_records[sample_class_data["class_id"]][sample_student_data["student_id"]]
    assert student_manager.attendance_records[sample_class_data["class_id"]][sample_student_data["student_id"]][date] is True

    date_absent = date + timedelta(days=1)
    result_absent = await student_manager.record_attendance(
        class_id=sample_class_data["class_id"],
        student_id=sample_student_data["student_id"],
        date=date_absent,
        present=False
    )
    assert result_absent is True
    assert student_manager.attendance_records[sample_class_data["class_id"]][sample_student_data["student_id"]][date_absent] is False

    result_non_student = await student_manager.record_attendance(
        class_id=sample_class_data["class_id"],
        student_id="nonexistent",
        date=date,
        present=True
    )
    assert result_non_student is False

@pytest.mark.asyncio
async def test_record_progress(student_manager, sample_student_data, sample_class_data, mock_progress_data):
    """Test recording student progress."""
    await student_manager.create_student_profile(**sample_student_data)
    await student_manager.create_class(**sample_class_data)
    await student_manager.enroll_student(
        student_id=sample_student_data["student_id"],
        class_id=sample_class_data["class_id"]
    )

    result = await student_manager.record_progress(
        student_id=sample_student_data["student_id"],
        class_id=sample_class_data["class_id"],
        metrics=mock_progress_data
    )

    assert result is True
    assert len(student_manager.progress_records[sample_student_data["student_id"]][sample_class_data["class_id"]]) == 1
    recorded_metric = student_manager.progress_records[sample_student_data["student_id"]][sample_class_data["class_id"]][0]
    assert recorded_metric["metrics"] == mock_progress_data
    assert isinstance(recorded_metric["date"], datetime)

    with pytest.raises(ValueError, match="Invalid progress metrics"):
        await student_manager.record_progress(
            student_id=sample_student_data["student_id"],
            class_id=sample_class_data["class_id"],
            metrics={"invalid": "metric"}
        )

@pytest.mark.asyncio
async def test_generate_progress_report(student_manager, sample_student_data, sample_class_data, mock_progress_data):
    """Test generating progress report."""
    await student_manager.create_student_profile(**sample_student_data)
    await student_manager.create_class(**sample_class_data)
    await student_manager.enroll_student(sample_student_data["student_id"], sample_class_data["class_id"])

    date1 = datetime.now() - timedelta(days=10)
    date2 = datetime.now()
    await student_manager.record_progress(sample_student_data["student_id"], sample_class_data["class_id"], mock_progress_data, date1)
    await student_manager.record_progress(sample_student_data["student_id"], sample_class_data["class_id"], mock_progress_data, date2)

    student_manager.assessment_system.calculate_overall_progress = AsyncMock(return_value=85.5)
    student_manager.assessment_system.identify_strengths_weaknesses = AsyncMock(return_value=([], []))
    student_manager.lesson_planner.suggest_activities = AsyncMock(return_value=[])

    start_date = datetime.now() - timedelta(days=30)
    end_date = datetime.now()
    result = await student_manager.generate_progress_report(
        student_id=sample_student_data["student_id"],
        class_id=sample_class_data["class_id"],
        start_date=start_date,
        end_date=end_date
    )

    assert "summary" in result
    assert "progress_history" in result
    assert len(result["progress_history"]) == 2
    assert "recommendations" in result

@pytest.mark.asyncio
async def test_generate_recommendations(student_manager, sample_student_data, sample_class_data, mock_progress_data):
    """Test generating recommendations."""
    await student_manager.create_student_profile(**sample_student_data)
    await student_manager.create_class(**sample_class_data)
    await student_manager.enroll_student(sample_student_data["student_id"], sample_class_data["class_id"])
    await student_manager.record_progress(sample_student_data["student_id"], sample_class_data["class_id"], mock_progress_data)

    student_manager.assessment_system.identify_strengths_weaknesses = AsyncMock(return_value=(
        ["cardiovascular_endurance"], ["flexibility"]
    ))
    student_manager.lesson_planner.suggest_activities = AsyncMock(return_value=[
        {"activity_id": "act1", "name": "Yoga"}, {"activity_id": "act2", "name": "Stretching"}
    ])

    progress_records = student_manager.progress_records[sample_student_data["student_id"]][sample_class_data["class_id"]]

    result = await student_manager.generate_recommendations(
        student_id=sample_student_data["student_id"],
        class_id=sample_class_data["class_id"],
        progress_records=progress_records
    )

    assert "areas_for_improvement" in result
    assert "suggested_activities" in result
    assert "strengths" in result
    assert "flexibility" in result["areas_for_improvement"]
    assert len(result["suggested_activities"]) == 2

@patch("builtins.open", new_callable=unittest.mock.mock_open)
@patch("json.dump")
def test_save_student_data(mock_json_dump, mock_open, student_manager, sample_student_data):
    """Test saving student data to a file."""
    student_id = sample_student_data["student_id"]
    student_manager.students = {student_id: sample_student_data}
    filename = f"{student_id}.json"

    student_manager.save_student_data(student_id, filename)

    mock_open.assert_called_once_with(filename, 'w')
    mock_json_dump.assert_called_once()

@patch("builtins.open", new_callable=unittest.mock.mock_open)
@patch("json.dump")
def test_save_class_data(mock_json_dump, mock_open, student_manager, sample_class_data):
    """Test saving class data to a file."""
    class_id = sample_class_data["class_id"]
    student_manager.classes = {class_id: sample_class_data}
    filename = f"{class_id}.json"

    student_manager.save_class_data(class_id, filename)

    mock_open.assert_called_once_with(filename, 'w')
    mock_json_dump.assert_called_once_with(sample_class_data, mock_open(), indent=4)

@pytest.mark.asyncio
async def test_error_handling(student_manager):
    """Test various error scenarios."""
    with pytest.raises(ValueError):
        await student_manager.get_student_profile("nonexistent")

    with pytest.raises(ValueError):
        await student_manager.get_class_info("nonexistent")

    result_att = await student_manager.record_attendance("nonexistent_class", "student1", datetime.now().date(), True)
    assert result_att is False

    with pytest.raises(ValueError):
        await student_manager.record_progress("nonexistent_student", "class1", {})

def test_add_student_to_class(db, sample_class, sample_student):
    manager = StudentManager(db)
    manager.add_student_to_class(sample_student.id, sample_class.id)
    
    # Verify student was added to class
    assert sample_student in sample_class.students
    assert sample_class in sample_student.classes

def test_remove_student_from_class(db, sample_class, sample_student):
    manager = StudentManager(db)
    
    # First add the student
    manager.add_student_to_class(sample_student.id, sample_class.id)
    
    # Then remove them
    manager.remove_student_from_class(sample_student.id, sample_class.id)
    
    # Verify student was removed
    assert sample_student not in sample_class.students
    assert sample_class not in sample_student.classes

def test_get_student_classes(db, sample_class, sample_student):
    manager = StudentManager(db)
    
    # Add student to class
    manager.add_student_to_class(sample_student.id, sample_class.id)
    
    # Get student's classes
    classes = manager.get_student_classes(sample_student.id)
    
    # Verify class is in the list
    assert sample_class in classes

def test_get_class_students(db, sample_class, sample_student):
    manager = StudentManager(db)
    
    # Add student to class
    manager.add_student_to_class(sample_student.id, sample_class.id)
    
    # Get class's students
    students = manager.get_class_students(sample_class.id)
    
    # Verify student is in the list
    assert sample_student in students

def test_class_capacity(db, sample_class):
    manager = StudentManager(db)
    
    # Create and add maximum number of students
    for i in range(sample_class.max_students):
        student = Student(
            first_name=f"Student{i}",
            last_name=f"Last{i}",
            grade_level="9th"
        )
        db.add(student)
        db.commit()
        db.refresh(student)
        manager.add_student_to_class(student.id, sample_class.id)
    
    # Try to add one more student
    extra_student = Student(
        first_name="Extra",
        last_name="Student",
        grade_level="9th"
    )
    db.add(extra_student)
    db.commit()
    db.refresh(extra_student)
    
    # Should raise an exception
    with pytest.raises(ValueError):
        manager.add_student_to_class(extra_student.id, sample_class.id) 