import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, AsyncMock
from app.services.physical_education.services.student_manager import StudentManager
from app.services.physical_education.services.assessment_system import AssessmentSystem
from app.services.physical_education.services.lesson_planner import LessonPlanner

@pytest.fixture
def student_manager():
    """Create StudentManager instance for testing."""
    return StudentManager()

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

@pytest.mark.asyncio
async def test_initialization(student_manager, mock_assessment_system, mock_lesson_planner):
    """Test initialization of StudentManager."""
    with patch.object(student_manager, 'assessment_system', mock_assessment_system), \
         patch.object(student_manager, 'lesson_planner', mock_lesson_planner):
        
        await student_manager.initialize()
        
        mock_assessment_system.initialize.assert_called_once()
        mock_lesson_planner.initialize.assert_called_once()

@pytest.mark.asyncio
async def test_create_student_profile(student_manager, sample_student_data):
    """Test creating a student profile."""
    # Test successful creation
    result = await student_manager.create_student_profile(**sample_student_data)
    
    assert result["student_id"] == sample_student_data["student_id"]
    assert result["first_name"] == sample_student_data["first_name"]
    assert result["last_name"] == sample_student_data["last_name"]
    assert result["grade_level"] == sample_student_data["grade_level"]
    assert result["medical_conditions"] == sample_student_data["medical_conditions"]
    assert result["emergency_contact"] == sample_student_data["emergency_contact"]
    assert result["skill_level"] == "beginner"
    assert result["attendance_rate"] == 1.0
    
    # Test with invalid grade level
    with pytest.raises(ValueError):
        await student_manager.create_student_profile(
            student_id="student2",
            first_name="Jane",
            last_name="Smith",
            grade_level="invalid",
            date_of_birth=datetime.now() - timedelta(days=365*10)
        )
    
    # Test with duplicate student ID
    with pytest.raises(ValueError):
        await student_manager.create_student_profile(**sample_student_data)

@pytest.mark.asyncio
async def test_create_class(student_manager, sample_class_data):
    """Test creating a class."""
    # Test successful creation
    result = await student_manager.create_class(**sample_class_data)
    
    assert result["class_id"] == sample_class_data["class_id"]
    assert result["name"] == sample_class_data["name"]
    assert result["grade_level"] == sample_class_data["grade_level"]
    assert result["max_size"] == sample_class_data["max_size"]
    assert result["current_size"] == 0
    assert result["schedule"] == sample_class_data["schedule"]
    
    # Test with invalid grade level
    with pytest.raises(ValueError):
        await student_manager.create_class(
            class_id="class2",
            name="Invalid Class",
            grade_level="invalid",
            max_size=30,
            schedule={"days": ["Monday"], "time": "10:00-11:00"}
        )
    
    # Test with duplicate class ID
    with pytest.raises(ValueError):
        await student_manager.create_class(**sample_class_data)

@pytest.mark.asyncio
async def test_enroll_student(student_manager, sample_student_data, sample_class_data):
    """Test enrolling a student in a class."""
    # Create student and class first
    await student_manager.create_student_profile(**sample_student_data)
    await student_manager.create_class(**sample_class_data)
    
    # Test successful enrollment
    result = await student_manager.enroll_student(
        student_id=sample_student_data["student_id"],
        class_id=sample_class_data["class_id"]
    )
    
    assert result is True
    assert sample_student_data["student_id"] in student_manager.classes[sample_class_data["class_id"]]["students"]
    assert sample_class_data["class_id"] in student_manager.students[sample_student_data["student_id"]]["current_classes"]
    
    # Test enrolling non-existent student
    result = await student_manager.enroll_student("nonexistent", sample_class_data["class_id"])
    assert result is False
    
    # Test enrolling in non-existent class
    result = await student_manager.enroll_student(sample_student_data["student_id"], "nonexistent")
    assert result is False

@pytest.mark.asyncio
async def test_record_attendance(student_manager, sample_student_data, sample_class_data):
    """Test recording student attendance."""
    # Create student and class first
    await student_manager.create_student_profile(**sample_student_data)
    await student_manager.create_class(**sample_class_data)
    await student_manager.enroll_student(
        student_id=sample_student_data["student_id"],
        class_id=sample_class_data["class_id"]
    )
    
    # Test recording attendance
    date = datetime.now()
    result = await student_manager.record_attendance(
        class_id=sample_class_data["class_id"],
        student_id=sample_student_data["student_id"],
        date=date,
        present=True
    )
    
    assert result is True
    assert date in student_manager.attendance_records[sample_class_data["class_id"]][sample_student_data["student_id"]]
    
    # Test recording attendance for non-enrolled student
    result = await student_manager.record_attendance(
        class_id=sample_class_data["class_id"],
        student_id="nonexistent",
        date=date,
        present=True
    )
    assert result is False

@pytest.mark.asyncio
async def test_record_progress(student_manager, sample_student_data, sample_class_data):
    """Test recording student progress."""
    # Create student and class first
    await student_manager.create_student_profile(**sample_student_data)
    await student_manager.create_class(**sample_class_data)
    await student_manager.enroll_student(
        student_id=sample_student_data["student_id"],
        class_id=sample_class_data["class_id"]
    )
    
    # Test recording progress
    metrics = {
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
    
    result = await student_manager.record_progress(
        student_id=sample_student_data["student_id"],
        class_id=sample_class_data["class_id"],
        metrics=metrics
    )
    
    assert result is True
    assert len(student_manager.progress_records[sample_student_data["student_id"]][sample_class_data["class_id"]]) == 1
    
    # Test with invalid metrics
    with pytest.raises(ValueError):
        await student_manager.record_progress(
            student_id=sample_student_data["student_id"],
            class_id=sample_class_data["class_id"],
            metrics={"invalid": 100}
        )

@pytest.mark.asyncio
async def test_generate_progress_report(student_manager, sample_student_data, sample_class_data):
    """Test generating progress report."""
    # Create student and class first
    await student_manager.create_student_profile(**sample_student_data)
    await student_manager.create_class(**sample_class_data)
    await student_manager.enroll_student(
        student_id=sample_student_data["student_id"],
        class_id=sample_class_data["class_id"]
    )
    
    # Record some progress
    metrics = {
        "fitness": {"cardiovascular_endurance": 75},
        "skills": {"locomotor_skills": 80},
        "social": {"teamwork": 90}
    }
    await student_manager.record_progress(
        student_id=sample_student_data["student_id"],
        class_id=sample_class_data["class_id"],
        metrics=metrics
    )
    
    # Generate report
    start_date = datetime.now() - timedelta(days=30)
    end_date = datetime.now()
    report = await student_manager.generate_progress_report(
        student_id=sample_student_data["student_id"],
        class_id=sample_class_data["class_id"],
        start_date=start_date,
        end_date=end_date
    )
    
    assert "student_info" in report
    assert "progress_summary" in report
    assert "attendance_summary" in report
    assert "recommendations" in report

@pytest.mark.asyncio
async def test_generate_recommendations(student_manager, sample_student_data, sample_class_data):
    """Test generating recommendations."""
    # Create student and class first
    await student_manager.create_student_profile(**sample_student_data)
    await student_manager.create_class(**sample_class_data)
    await student_manager.enroll_student(
        student_id=sample_student_data["student_id"],
        class_id=sample_class_data["class_id"]
    )
    
    # Record some progress
    metrics = {
        "fitness": {"cardiovascular_endurance": 50},  # Low score
        "skills": {"locomotor_skills": 80},
        "social": {"teamwork": 90}
    }
    await student_manager.record_progress(
        student_id=sample_student_data["student_id"],
        class_id=sample_class_data["class_id"],
        metrics=metrics
    )
    
    # Get recommendations
    progress_records = student_manager.progress_records[sample_student_data["student_id"]][sample_class_data["class_id"]]
    recommendations = await student_manager.generate_recommendations(
        student_id=sample_student_data["student_id"],
        class_id=sample_class_data["class_id"],
        progress_records=progress_records
    )
    
    assert isinstance(recommendations, list)
    assert len(recommendations) > 0
    assert any("cardiovascular" in rec.lower() for rec in recommendations)  # Should recommend improving low score

@pytest.mark.asyncio
async def test_error_handling(student_manager):
    """Test error handling in student operations."""
    # Test with invalid student data
    with pytest.raises(ValueError):
        await student_manager.create_student_profile(
            student_id="",
            first_name="",
            last_name="",
            grade_level="invalid",
            date_of_birth=datetime.now() + timedelta(days=1)  # Future date
        )
    
    # Test with invalid class data
    with pytest.raises(ValueError):
        await student_manager.create_class(
            class_id="",
            name="",
            grade_level="invalid",
            max_size=0,
            schedule={}
        )
    
    # Test with invalid progress metrics
    with pytest.raises(ValueError):
        await student_manager.record_progress(
            student_id="nonexistent",
            class_id="nonexistent",
            metrics={"invalid": 100}
        ) 