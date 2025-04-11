import pytest
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock
import json

from app.services.physical_education.services.lesson_planner import LessonPlanner
from app.services.physical_education.services.assessment_system import AssessmentSystem

@pytest.fixture
def lesson_planner():
    planner = LessonPlanner()
    planner.assessment_system = Mock(spec=AssessmentSystem)
    return planner

@pytest.fixture
def mock_lesson_parameters():
    return {
        "grade_level": "3-5",
        "focus_area": "skill_development",
        "skill_level": "intermediate",
        "class_size": 25,
        "available_equipment": ["cones", "whistle", "balls", "jump ropes"]
    }

@pytest.fixture
def mock_activity_data():
    return {
        "warmup": {
            "dynamic_stretching": {
                "duration": 5,
                "equipment": "minimal",
                "skills": ["flexibility", "coordination"],
                "description": "Dynamic stretching exercises"
            }
        },
        "main_activities": {
            "team_sports": {
                "basketball": {
                    "duration": 20,
                    "equipment": "basic",
                    "skills": ["dribbling", "passing", "shooting", "teamwork"],
                    "variations": ["3v3", "5v5", "skill drills"]
                }
            }
        },
        "cooldown": {
            "static_stretching": {
                "duration": 5,
                "equipment": "minimal",
                "skills": ["flexibility", "recovery"],
                "description": "Static stretching exercises"
            }
        }
    }

# Tests for initialization
@pytest.mark.asyncio
async def test_initialization(lesson_planner):
    assert lesson_planner.settings
    assert lesson_planner.curriculum_standards
    assert lesson_planner.activities
    assert lesson_planner.lesson_templates
    assert isinstance(lesson_planner.assessment_system, Mock)

@pytest.mark.asyncio
async def test_initialize_success(lesson_planner):
    lesson_planner.assessment_system.initialize = AsyncMock()
    lesson_planner.load_lesson_templates = Mock()
    lesson_planner.initialize_activity_database = Mock()
    
    await lesson_planner.initialize()
    
    lesson_planner.assessment_system.initialize.assert_called_once()
    lesson_planner.load_lesson_templates.assert_called_once()
    lesson_planner.initialize_activity_database.assert_called_once()

# Tests for lesson plan creation
@pytest.mark.asyncio
async def test_create_lesson_plan_success(lesson_planner, mock_lesson_parameters):
    lesson_planner.validate_parameters = Mock()
    lesson_planner.select_template = Mock(return_value={
        "warmup": "dynamic_stretching",
        "main_activity": "individual_skills",
        "cooldown": "static_stretching"
    })
    lesson_planner.generate_activities = AsyncMock(return_value=[
        {"name": "dynamic_stretching", "duration": 5},
        {"name": "jumping", "duration": 15},
        {"name": "static_stretching", "duration": 5}
    ])
    
    result = await lesson_planner.create_lesson_plan(**mock_lesson_parameters)
    
    assert "warmup" in result
    assert "main_activities" in result
    assert "cooldown" in result
    assert "objectives" in result
    assert "assessment_criteria" in result
    assert "safety_considerations" in result

@pytest.mark.asyncio
async def test_create_lesson_plan_invalid_grade_level(lesson_planner, mock_lesson_parameters):
    mock_lesson_parameters["grade_level"] = "invalid"
    
    with pytest.raises(ValueError, match="Invalid grade level"):
        await lesson_planner.create_lesson_plan(**mock_lesson_parameters)

# Tests for activity generation
@pytest.mark.asyncio
async def test_generate_activities_success(lesson_planner, mock_lesson_parameters):
    template = {
        "warmup": "dynamic_stretching",
        "main_activity": "individual_skills",
        "cooldown": "static_stretching"
    }
    
    result = await lesson_planner.generate_activities(
        template,
        mock_lesson_parameters["grade_level"],
        mock_lesson_parameters["skill_level"],
        mock_lesson_parameters["class_size"],
        mock_lesson_parameters["available_equipment"]
    )
    
    assert len(result) > 0
    assert all("name" in activity for activity in result)
    assert all("duration" in activity for activity in result)

# Tests for activity selection
def test_select_activity_success(lesson_planner, mock_activity_data):
    result = lesson_planner.select_activity(
        "warmup",
        "dynamic_stretching",
        "3-5",
        "intermediate",
        25,
        ["cones", "whistle"]
    )
    
    assert result["name"] == "dynamic_stretching"
    assert result["duration"] == 5
    assert "skills" in result
    assert "description" in result

# Tests for equipment validation
def test_check_equipment_requirements_success(lesson_planner):
    assert lesson_planner.check_equipment_requirements(
        "minimal",
        ["cones", "whistle"]
    )

def test_check_equipment_requirements_failure(lesson_planner):
    assert not lesson_planner.check_equipment_requirements(
        "full",
        ["cones", "whistle"]
    )

# Tests for activity modifications
def test_generate_activity_modifications_success(lesson_planner):
    activity = {
        "name": "basketball",
        "duration": 20,
        "equipment": "basic",
        "skills": ["dribbling", "passing", "shooting", "teamwork"],
        "variations": ["3v3", "5v5", "skill drills"]
    }
    
    result = lesson_planner.generate_activity_modifications(
        activity,
        "3-5",
        "intermediate",
        25
    )
    
    assert "modifications" in result
    assert "group_size" in result
    assert "equipment_modifications" in result

# Tests for group size calculation
def test_calculate_group_size(lesson_planner):
    assert lesson_planner.calculate_group_size(25) <= lesson_planner.settings["max_students_per_group"]

# Tests for equipment modifications
def test_generate_equipment_modifications(lesson_planner):
    result = lesson_planner.generate_equipment_modifications("basic")
    assert isinstance(result, list)
    assert all(isinstance(item, str) for item in result)

# Tests for objectives generation
def test_generate_objectives(lesson_planner):
    result = lesson_planner.generate_objectives("3-5", "skill_development")
    assert isinstance(result, list)
    assert len(result) > 0
    assert all(isinstance(obj, str) for obj in result)

# Tests for assessment criteria
def test_generate_assessment_criteria(lesson_planner):
    result = lesson_planner.generate_assessment_criteria("skill_development")
    assert isinstance(result, dict)
    assert "criteria" in result
    assert "rubric" in result

# Tests for safety considerations
def test_generate_safety_considerations(lesson_planner):
    activities = [
        {"name": "dynamic_stretching", "equipment": "minimal"},
        {"name": "basketball", "equipment": "basic"}
    ]
    
    result = lesson_planner.generate_safety_considerations(activities)
    assert isinstance(result, list)
    assert len(result) > 0
    assert all(isinstance(consideration, str) for consideration in result)

# Tests for data persistence
def test_save_lesson_templates(lesson_planner):
    with patch("builtins.open", unittest.mock.mock_open()) as mock_file:
        lesson_planner.save_lesson_templates()
        
        mock_file.assert_called_once()
        # Verify that the data was written correctly
        mock_file().write.assert_called_with(json.dumps(lesson_planner.lesson_templates)) 