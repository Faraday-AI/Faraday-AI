import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock, AsyncMock
import json

from app.services.physical_education.lesson_planner import LessonPlanner
from app.services.physical_education.assessment_system import AssessmentSystem

@pytest.fixture
def mock_assessment_system():
    """Create a mock AssessmentSystem."""
    return MagicMock(spec=AssessmentSystem)

@pytest.fixture
def lesson_planner(mock_assessment_system):
    """Create LessonPlanner instance with mocked AssessmentSystem."""
    planner = LessonPlanner()
    planner.assessment_system = mock_assessment_system
    return planner

@pytest.fixture
def sample_lesson_parameters():
    """Create sample lesson parameters."""
    return {
        "grade_level": "3-5",
        "focus_area": "fitness",
        "skill_level": "intermediate",
        "class_size": 25,
        "available_equipment": ["cones", "whistle", "balls", "jump ropes"]
    }

@pytest.fixture
def mock_activity_data():
    """Provide mock activity data for testing."""
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
            "fitness_circuit": {
                "duration": 20,
                "equipment": "basic",
                "skills": ["strength", "endurance", "agility"],
                "variations": ["timed stations", "repetition based"]
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
async def test_initialization(lesson_planner, mock_assessment_system):
    """Test initialization of LessonPlanner."""
    assert lesson_planner.settings
    assert lesson_planner.curriculum_standards
    assert lesson_planner.activities
    assert lesson_planner.lesson_templates
    assert lesson_planner.assessment_system == mock_assessment_system

@pytest.mark.asyncio
async def test_initialize_success(lesson_planner, mock_assessment_system):
    """Test successful initialization process."""
    mock_assessment_system.initialize = AsyncMock()
    lesson_planner.load_lesson_templates = MagicMock()
    lesson_planner.initialize_activity_database = MagicMock()
    
    await lesson_planner.initialize()
    
    mock_assessment_system.initialize.assert_called_once()
    lesson_planner.load_lesson_templates.assert_called_once()
    lesson_planner.initialize_activity_database.assert_called_once()
    assert lesson_planner.settings["lesson_duration"] == 45
    assert lesson_planner.settings["max_students_per_group"] == 6

# Tests for lesson plan creation
@pytest.mark.asyncio
async def test_create_lesson_plan_success(lesson_planner, sample_lesson_parameters):
    """Test creating a lesson plan successfully."""
    lesson_planner.validate_parameters = MagicMock()
    lesson_planner.select_template = MagicMock(return_value={
        "warmup": "dynamic_stretching",
        "main_activity": "fitness_circuit",
        "cooldown": "static_stretching"
    })
    lesson_planner.generate_activities = AsyncMock(return_value=[
        {"name": "dynamic_stretching", "duration": 5, "equipment": [], "skills": [], "description": "", "modifications": {}},
        {"name": "fitness_circuit", "duration": 20, "equipment": [], "skills": [], "description": "", "modifications": {}},
        {"name": "static_stretching", "duration": 5, "equipment": [], "skills": [], "description": "", "modifications": {}}
    ])
    lesson_planner.determine_equipment_needs = MagicMock(return_value=["cones"])
    lesson_planner.generate_objectives = MagicMock(return_value=["obj1"])
    lesson_planner.generate_assessment_criteria = MagicMock(return_value={"criteria": "crit1"})
    lesson_planner.generate_safety_considerations = MagicMock(return_value=["safety1"])
    lesson_planner.generate_activity_modifications = MagicMock(return_value={"mod": "mod1"})

    result = await lesson_planner.create_lesson_plan(**sample_lesson_parameters)
    
    assert result["grade_level"] == sample_lesson_parameters["grade_level"]
    assert result["focus_area"] == sample_lesson_parameters["focus_area"]
    assert result["skill_level"] == sample_lesson_parameters["skill_level"]
    assert result["class_size"] == sample_lesson_parameters["class_size"]
    assert result["duration"] == lesson_planner.settings["lesson_duration"]
    assert "activities" in result
    assert "equipment_needed" in result
    assert "objectives" in result
    assert "assessment_criteria" in result
    assert "safety_considerations" in result
    assert "modifications" in result
    lesson_planner.validate_parameters.assert_called_once_with(sample_lesson_parameters)

@pytest.mark.asyncio
async def test_create_lesson_plan_invalid_parameters(lesson_planner, sample_lesson_parameters):
    """Test lesson plan creation with various invalid parameters."""
    
    # Test with invalid grade level
    invalid_params = sample_lesson_parameters.copy()
    invalid_params["grade_level"] = "invalid"
    with pytest.raises(ValueError, match="Invalid grade level"):
        await lesson_planner.create_lesson_plan(**invalid_params)
    
    # Test with invalid focus area
    invalid_params = sample_lesson_parameters.copy()
    invalid_params["focus_area"] = "invalid"
    with pytest.raises(ValueError, match="Invalid focus area"):
        await lesson_planner.create_lesson_plan(**invalid_params)
    
    # Test with invalid skill level
    invalid_params = sample_lesson_parameters.copy()
    invalid_params["skill_level"] = "invalid"
    with pytest.raises(ValueError, match="Invalid skill level"):
        await lesson_planner.create_lesson_plan(**invalid_params)
    
    # Test with invalid class size
    invalid_params = sample_lesson_parameters.copy()
    invalid_params["class_size"] = 0
    with pytest.raises(ValueError, match="Class size must be positive"):
        await lesson_planner.create_lesson_plan(**invalid_params)

# Tests for template selection
def test_select_template_success(lesson_planner):
    """Test selecting lesson template successfully."""
    template = lesson_planner.select_template("skill_development")
    assert template["warmup"] == "dynamic_stretching"
    assert template["main_activity"] == "individual_skills"
    assert template["cooldown"] == "static_stretching"

def test_select_template_invalid_focus(lesson_planner):
    """Test selecting template with invalid focus area."""
    with pytest.raises(ValueError, match="Invalid focus area"):
        lesson_planner.select_template("invalid_focus")

# Tests for activity generation
@pytest.mark.asyncio
async def test_generate_activities_success(lesson_planner, sample_lesson_parameters, mock_activity_data):
    """Test generating activities for a lesson plan."""
    lesson_planner.activities = mock_activity_data # Use mock data
    template = lesson_planner.select_template("fitness")
    activities = await lesson_planner.generate_activities(
        template=template,
        grade_level=sample_lesson_parameters["grade_level"],
        skill_level=sample_lesson_parameters["skill_level"],
        class_size=sample_lesson_parameters["class_size"],
        available_equipment=sample_lesson_parameters["available_equipment"]
    )
    
    assert len(activities) == 3 # Warmup, main, cooldown
    for activity in activities:
        assert "name" in activity
        assert "duration" in activity
        assert "equipment" in activity
        assert "skills" in activity
        assert "description" in activity
        assert "modifications" in activity

# Tests for activity selection
def test_select_activity_success(lesson_planner, sample_lesson_parameters, mock_activity_data):
    """Test selecting a specific activity."""
    lesson_planner.activities = mock_activity_data # Use mock data
    activity = lesson_planner.select_activity(
        category="main_activities",
        activity_type="fitness_circuit",
        grade_level=sample_lesson_parameters["grade_level"],
        skill_level=sample_lesson_parameters["skill_level"],
        class_size=sample_lesson_parameters["class_size"],
        available_equipment=sample_lesson_parameters["available_equipment"]
    )
    
    assert activity is not None
    assert activity["duration"] == 20
    assert activity["equipment"] == "basic"
    assert "skills" in activity
    assert "variations" in activity

# Tests for equipment validation
def test_check_equipment_requirements_success(lesson_planner):
    """Test checking equipment requirements when sufficient."""
    assert lesson_planner.check_equipment_requirements("minimal", ["cones", "whistle"]) is True
    assert lesson_planner.check_equipment_requirements("basic", ["cones", "balls", "jump ropes"]) is True

def test_check_equipment_requirements_failure(lesson_planner):
    """Test checking equipment requirements when insufficient."""
    assert lesson_planner.check_equipment_requirements("basic", ["cones", "whistle"]) is False
    assert lesson_planner.check_equipment_requirements("full", ["cones", "balls"]) is False

# Tests for choosing activity from options
def test_choose_activity(lesson_planner):
    """Test choosing an activity based on parameters."""
    activities = {
        "activity1": {"duration": 10, "equipment": "minimal", "skills": ["s1"], "variations": []},
        "activity2": {"duration": 15, "equipment": "basic", "skills": ["s2"], "variations": []}
    }
    activity = lesson_planner.choose_activity(activities, "intermediate", 25)
    assert activity is not None
    assert activity in activities.values()

# Tests for activity modifications
def test_generate_activity_modifications_success(lesson_planner, sample_lesson_parameters, mock_activity_data):
    """Test generating activity modifications."""
    activity = mock_activity_data["main_activities"]["fitness_circuit"]
    result = lesson_planner.generate_activity_modifications(
        activity=activity,
        grade_level=sample_lesson_parameters["grade_level"],
        skill_level=sample_lesson_parameters["skill_level"],
        class_size=sample_lesson_parameters["class_size"]
    )
    assert "modifications" in result
    assert "group_size" in result
    assert "equipment_modifications" in result

# Tests for group size calculation
def test_calculate_group_size(lesson_planner):
    """Test calculating appropriate group size."""
    assert lesson_planner.calculate_group_size(25) <= lesson_planner.settings["max_students_per_group"]
    assert lesson_planner.calculate_group_size(5) == 5

# Tests for equipment modifications generation
def test_generate_equipment_modifications(lesson_planner):
    """Test generating equipment modifications based on type."""
    result = lesson_planner.generate_equipment_modifications("basic")
    assert isinstance(result, list)
    assert all(isinstance(item, str) for item in result)
    assert "Use lighter balls" in result # Example modification

# Tests for determining equipment needs
def test_determine_equipment_needs(lesson_planner, mock_activity_data):
    """Test determining overall equipment needs for a lesson."""
    activities = [
        mock_activity_data["warmup"]["dynamic_stretching"],
        mock_activity_data["main_activities"]["fitness_circuit"],
        mock_activity_data["cooldown"]["static_stretching"]
    ]
    equipment = lesson_planner.determine_equipment_needs(activities)
    assert isinstance(equipment, list)
    assert "cones" in equipment or "balls" in equipment # Depending on 'basic' definition

# Tests for objectives generation
def test_generate_objectives(lesson_planner, sample_lesson_parameters):
    """Test generating lesson objectives."""
    result = lesson_planner.generate_objectives(
        sample_lesson_parameters["grade_level"],
        sample_lesson_parameters["focus_area"]
    )
    assert isinstance(result, list)
    assert len(result) > 0
    assert all(isinstance(obj, str) for obj in result)

# Tests for assessment criteria generation
def test_generate_assessment_criteria(lesson_planner, sample_lesson_parameters):
    """Test generating assessment criteria."""
    result = lesson_planner.generate_assessment_criteria(sample_lesson_parameters["focus_area"])
    assert isinstance(result, dict)
    assert "criteria" in result

# Tests for safety considerations generation
def test_generate_safety_considerations(lesson_planner):
    """Test generating safety considerations."""
    activities = [
        {"equipment": "minimal"}, 
        {"equipment": "basic"}
    ]
    result = lesson_planner.generate_safety_considerations(activities)
    assert isinstance(result, list)
    assert len(result) > 0
    assert "Ensure adequate spacing" in result # Example consideration

# Tests for saving and loading templates (Mocked)
def test_save_lesson_templates(lesson_planner):
    """Test saving lesson templates (mocked file IO)."""
    with patch("builtins.open", new_callable=MagicMock()) as mock_open, \
         patch("json.dump") as mock_json_dump:
        lesson_planner.save_lesson_templates()
        mock_open.assert_called_once_with(lesson_planner.template_file, 'w')
        mock_json_dump.assert_called_once()

def test_load_lesson_templates_success(lesson_planner):
    """Test loading lesson templates successfully (mocked file IO)."""
    mock_data = {"fitness": {}}
    with patch("builtins.open", new_callable=MagicMock()) as mock_open, \
         patch("json.load", return_value=mock_data) as mock_json_load:
        mock_open.return_value.__enter__.return_value.read.return_value = json.dumps(mock_data)
        lesson_planner.load_lesson_templates()
        mock_open.assert_called_once_with(lesson_planner.template_file, 'r')
        mock_json_load.assert_called_once()
        assert lesson_planner.lesson_templates == mock_data

def test_load_lesson_templates_file_not_found(lesson_planner):
    """Test loading templates when file not found (mocked file IO)."""
    with patch("builtins.open", side_effect=FileNotFoundError):
        lesson_planner.load_lesson_templates()
        assert lesson_planner.lesson_templates == {} # Should default to empty

# Tests for error handling
@pytest.mark.asyncio
async def test_error_handling_general(lesson_planner, sample_lesson_parameters):
    """Test general error handling during lesson plan creation."""
    # Simulate an error during activity generation
    lesson_planner.generate_activities = AsyncMock(side_effect=Exception("Generation failed"))
    
    with pytest.raises(Exception, match="Generation failed"):
        await lesson_planner.create_lesson_plan(**sample_lesson_parameters) 