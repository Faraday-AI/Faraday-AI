import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
import json

from app.services.physical_education.services.student_manager import StudentManager
from app.services.physical_education.services.assessment_system import AssessmentSystem
from app.services.physical_education.services.lesson_planner import LessonPlanner

@pytest.fixture
def student_manager():
    manager = StudentManager()
    manager.assessment_system = Mock(spec=AssessmentSystem)
    manager.lesson_planner = Mock(spec=LessonPlanner)
    return manager

@pytest.fixture
def mock_student_data():
    return {
        "student_id": "student123",
        "first_name": "John",
        "last_name": "Doe",
        "grade_level": "5",
        "date_of_birth": datetime.now() - timedelta(days=365*12),
        "medical_conditions": ["asthma"],
        "emergency_contact": {
            "name": "Jane Doe",
            "relationship": "parent",
            "phone": "123-456-7890"
        }
    }

@pytest.fixture
def mock_class_data():
    return {
        "class_id": "class123",
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

# Tests for initialization
@pytest.mark.asyncio
async def test_initialization(student_manager):
    assert student_manager.settings
    assert student_manager.progress_metrics
    assert isinstance(student_manager.assessment_system, Mock)
    assert isinstance(student_manager.lesson_planner, Mock)

@pytest.mark.asyncio
async def test_initialize_success(student_manager):
    student_manager.assessment_system.initialize = AsyncMock()
    student_manager.lesson_planner.initialize = AsyncMock()
    
    await student_manager.initialize()
    
    student_manager.assessment_system.initialize.assert_called_once()
    student_manager.lesson_planner.initialize.assert_called_once()

# Tests for student profile management
@pytest.mark.asyncio
async def test_create_student_profile_success(student_manager, mock_student_data):
    student_manager.lesson_planner.curriculum_standards = {
        "state": {
            "grade_levels": ["5"]
        }
    }
    
    result = await student_manager.create_student_profile(**mock_student_data)
    
    assert result["student_id"] == mock_student_data["student_id"]
    assert result["first_name"] == mock_student_data["first_name"]
    assert result["last_name"] == mock_student_data["last_name"]
    assert result["grade_level"] == mock_student_data["grade_level"]
    assert result["medical_conditions"] == mock_student_data["medical_conditions"]
    assert result["emergency_contact"] == mock_student_data["emergency_contact"]

@pytest.mark.asyncio
async def test_create_student_profile_duplicate_id(student_manager, mock_student_data):
    student_manager.students = {mock_student_data["student_id"]: {}}
    
    with pytest.raises(ValueError, match="already exists"):
        await student_manager.create_student_profile(**mock_student_data)

# Tests for class management
@pytest.mark.asyncio
async def test_create_class_success(student_manager, mock_class_data):
    result = await student_manager.create_class(**mock_class_data)
    
    assert result["class_id"] == mock_class_data["class_id"]
    assert result["name"] == mock_class_data["name"]
    assert result["grade_level"] == mock_class_data["grade_level"]
    assert result["max_size"] == mock_class_data["max_size"]
    assert result["schedule"] == mock_class_data["schedule"]

@pytest.mark.asyncio
async def test_create_class_invalid_size(student_manager, mock_class_data):
    mock_class_data["max_size"] = student_manager.settings["max_class_size"] + 1
    
    with pytest.raises(ValueError, match="exceeds maximum"):
        await student_manager.create_class(**mock_class_data)

# Tests for enrollment
@pytest.mark.asyncio
async def test_enroll_student_success(student_manager, mock_student_data, mock_class_data):
    student_manager.students = {mock_student_data["student_id"]: mock_student_data}
    student_manager.classes = {mock_class_data["class_id"]: mock_class_data}
    
    result = await student_manager.enroll_student(
        student_id=mock_student_data["student_id"],
        class_id=mock_class_data["class_id"]
    )
    
    assert result is True
    assert mock_class_data["class_id"] in student_manager.students[mock_student_data["student_id"]]["current_classes"]

# Tests for attendance
@pytest.mark.asyncio
async def test_record_attendance_success(student_manager, mock_student_data, mock_class_data):
    student_manager.students = {mock_student_data["student_id"]: mock_student_data}
    student_manager.classes = {mock_class_data["class_id"]: mock_class_data}
    student_manager.attendance_records = {
        mock_class_data["class_id"]: {
            mock_student_data["student_id"]: []
        }
    }
    
    result = await student_manager.record_attendance(
        class_id=mock_class_data["class_id"],
        student_id=mock_student_data["student_id"],
        date=datetime.now(),
        present=True
    )
    
    assert result is True

# Tests for progress tracking
@pytest.mark.asyncio
async def test_record_progress_success(student_manager, mock_student_data, mock_class_data, mock_progress_data):
    student_manager.students = {mock_student_data["student_id"]: mock_student_data}
    student_manager.classes = {mock_class_data["class_id"]: mock_class_data}
    student_manager.progress_records = {
        mock_class_data["class_id"]: {
            mock_student_data["student_id"]: []
        }
    }
    
    result = await student_manager.record_progress(
        student_id=mock_student_data["student_id"],
        class_id=mock_class_data["class_id"],
        metrics=mock_progress_data
    )
    
    assert result is True

@pytest.mark.asyncio
async def test_record_progress_invalid_metrics(student_manager, mock_student_data, mock_class_data):
    student_manager.students = {mock_student_data["student_id"]: mock_student_data}
    student_manager.classes = {mock_class_data["class_id"]: mock_class_data}
    
    with pytest.raises(ValueError, match="Invalid progress metrics"):
        await student_manager.record_progress(
            student_id=mock_student_data["student_id"],
            class_id=mock_class_data["class_id"],
            metrics={"invalid": "metric"}
        )

# Tests for progress reporting
@pytest.mark.asyncio
async def test_generate_progress_report(student_manager, mock_student_data, mock_class_data):
    student_manager.students = {mock_student_data["student_id"]: mock_student_data}
    student_manager.classes = {mock_class_data["class_id"]: mock_class_data}
    student_manager.progress_records = {
        mock_class_data["class_id"]: {
            mock_student_data["student_id"]: [
                {
                    "date": datetime.now().isoformat(),
                    "metrics": {
                        "fitness": {"score": 80},
                        "skills": {"score": 75},
                        "social": {"score": 85}
                    }
                }
            ]
        }
    }
    
    result = await student_manager.generate_progress_report(
        student_id=mock_student_data["student_id"],
        class_id=mock_class_data["class_id"],
        start_date=datetime.now() - timedelta(days=30),
        end_date=datetime.now()
    )
    
    assert "summary" in result
    assert "progress_history" in result
    assert "recommendations" in result

# Tests for recommendations
@pytest.mark.asyncio
async def test_generate_recommendations(student_manager, mock_student_data, mock_class_data):
    student_manager.students = {mock_student_data["student_id"]: mock_student_data}
    student_manager.classes = {mock_class_data["class_id"]: mock_class_data}
    student_manager.progress_records = {
        mock_class_data["class_id"]: {
            mock_student_data["student_id"]: [
                {
                    "date": datetime.now().isoformat(),
                    "metrics": {
                        "fitness": {"score": 60},
                        "skills": {"score": 75},
                        "social": {"score": 85}
                    }
                }
            ]
        }
    }
    
    result = await student_manager.generate_recommendations(
        student_id=mock_student_data["student_id"],
        class_id=mock_class_data["class_id"],
        progress_records=student_manager.progress_records[mock_class_data["class_id"]][mock_student_data["student_id"]]
    )
    
    assert isinstance(result, list)
    assert len(result) > 0

# Tests for data persistence
def test_save_student_data(student_manager, mock_student_data):
    student_manager.students = {mock_student_data["student_id"]: mock_student_data}
    
    with patch("builtins.open", unittest.mock.mock_open()) as mock_file:
        student_manager.save_student_data()
        
        mock_file.assert_called_once()
        # Verify that the data was written correctly
        mock_file().write.assert_called_with(json.dumps(student_manager.students))

def test_save_class_data(student_manager, mock_class_data):
    student_manager.classes = {mock_class_data["class_id"]: mock_class_data}
    
    with patch("builtins.open", unittest.mock.mock_open()) as mock_file:
        student_manager.save_class_data()
        
        mock_file.assert_called_once()
        # Verify that the data was written correctly
        mock_file().write.assert_called_with(json.dumps(student_manager.classes)) 