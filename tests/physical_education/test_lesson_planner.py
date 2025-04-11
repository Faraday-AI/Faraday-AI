import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock, AsyncMock
from app.services.physical_education.services.lesson_planner import LessonPlanner
from app.services.physical_education.services.assessment_system import AssessmentSystem

@pytest.fixture
def lesson_planner():
    """Create LessonPlanner instance for testing."""
    return LessonPlanner()

@pytest.fixture
def mock_assessment_system():
    """Create a mock AssessmentSystem."""
    return MagicMock(spec=AssessmentSystem)

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

@pytest.mark.asyncio
async def test_initialization(lesson_planner, mock_assessment_system):
    """Test initialization of LessonPlanner."""
    with patch.object(lesson_planner, 'assessment_system', mock_assessment_system):
        await lesson_planner.initialize()
        
        mock_assessment_system.initialize.assert_called_once()
        assert lesson_planner.settings["lesson_duration"] == 45
        assert lesson_planner.settings["max_students_per_group"] == 6

@pytest.mark.asyncio
async def test_create_lesson_plan(lesson_planner, sample_lesson_parameters):
    """Test creating a lesson plan."""
    # Test successful creation
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
    
    # Test with invalid grade level
    with pytest.raises(ValueError):
        await lesson_planner.create_lesson_plan(
            grade_level="invalid",
            focus_area="fitness",
            skill_level="intermediate",
            class_size=25,
            available_equipment=["cones", "whistle"]
        )
    
    # Test with invalid focus area
    with pytest.raises(ValueError):
        await lesson_planner.create_lesson_plan(
            grade_level="3-5",
            focus_area="invalid",
            skill_level="intermediate",
            class_size=25,
            available_equipment=["cones", "whistle"]
        )
    
    # Test with invalid skill level
    with pytest.raises(ValueError):
        await lesson_planner.create_lesson_plan(
            grade_level="3-5",
            focus_area="fitness",
            skill_level="invalid",
            class_size=25,
            available_equipment=["cones", "whistle"]
        )
    
    # Test with invalid class size
    with pytest.raises(ValueError):
        await lesson_planner.create_lesson_plan(
            grade_level="3-5",
            focus_area="fitness",
            skill_level="intermediate",
            class_size=0,
            available_equipment=["cones", "whistle"]
        )
    
    # Test with insufficient equipment
    with pytest.raises(ValueError):
        await lesson_planner.create_lesson_plan(
            grade_level="3-5",
            focus_area="fitness",
            skill_level="intermediate",
            class_size=25,
            available_equipment=["invalid"]
        )

def test_select_template(lesson_planner):
    """Test selecting lesson template."""
    # Test with valid focus area
    template = lesson_planner.select_template("skill_development")
    assert template["warmup"] == "dynamic_stretching"
    assert template["main_activity"] == "individual_skills"
    assert template["cooldown"] == "static_stretching"
    
    # Test with invalid focus area
    with pytest.raises(ValueError):
        lesson_planner.select_template("invalid")

@pytest.mark.asyncio
async def test_generate_activities(lesson_planner, sample_lesson_parameters):
    """Test generating activities for a lesson plan."""
    template = lesson_planner.select_template("skill_development")
    activities = await lesson_planner.generate_activities(
        template=template,
        grade_level=sample_lesson_parameters["grade_level"],
        skill_level=sample_lesson_parameters["skill_level"],
        class_size=sample_lesson_parameters["class_size"],
        available_equipment=sample_lesson_parameters["available_equipment"]
    )
    
    assert len(activities) > 0
    for activity in activities:
        assert "name" in activity
        assert "duration" in activity
        assert "equipment" in activity
        assert "skills" in activity
        assert "description" in activity
        assert "modifications" in activity

def test_select_activity(lesson_planner, sample_lesson_parameters):
    """Test selecting an activity."""
    activity = lesson_planner.select_activity(
        category="main_activities",
        activity_type="individual_skills",
        grade_level=sample_lesson_parameters["grade_level"],
        skill_level=sample_lesson_parameters["skill_level"],
        class_size=sample_lesson_parameters["class_size"],
        available_equipment=sample_lesson_parameters["available_equipment"]
    )
    
    assert activity is not None
    assert "duration" in activity
    assert "equipment" in activity
    assert "skills" in activity
    assert "variations" in activity

def test_check_equipment_requirements(lesson_planner):
    """Test checking equipment requirements."""
    # Test with sufficient equipment
    assert lesson_planner.check_equipment_requirements(
        "minimal",
        ["cones", "whistle"]
    ) is True
    
    # Test with insufficient equipment
    assert lesson_planner.check_equipment_requirements(
        "basic",
        ["cones", "whistle"]
    ) is False

def test_choose_activity(lesson_planner):
    """Test choosing an activity based on parameters."""
    activities = {
        "jumping": {
            "duration": 15,
            "equipment": "minimal",
            "skills": ["power", "coordination"],
            "variations": ["long jump", "high jump"]
        },
        "throwing": {
            "duration": 15,
            "equipment": "basic",
            "skills": ["accuracy", "power"],
            "variations": ["overhand", "underhand"]
        }
    }
    
    activity = lesson_planner.choose_activity(
        activities=activities,
        skill_level="intermediate",
        class_size=25
    )
    
    assert activity is not None
    assert activity in activities.values()

def test_generate_activity_modifications(lesson_planner, sample_lesson_parameters):
    """Test generating activity modifications."""
    activity = {
        "name": "basketball",
        "duration": 20,
        "equipment": "basic",
        "skills": ["dribbling", "passing", "shooting"],
        "variations": ["3v3", "5v5"]
    }
    
    modifications = lesson_planner.generate_activity_modifications(
        activity=activity,
        grade_level=sample_lesson_parameters["grade_level"],
        skill_level=sample_lesson_parameters["skill_level"],
        class_size=sample_lesson_parameters["class_size"]
    )
    
    assert "simplified_rules" in modifications
    assert "equipment_modifications" in modifications
    assert "group_size_adjustments" in modifications
    assert "skill_level_adaptations" in modifications

def test_calculate_group_size(lesson_planner):
    """Test calculating group size."""
    assert lesson_planner.calculate_group_size(25) <= lesson_planner.settings["max_students_per_group"]
    assert lesson_planner.calculate_group_size(6) == 6
    assert lesson_planner.calculate_group_size(12) == 6

def test_generate_equipment_modifications(lesson_planner):
    """Test generating equipment modifications."""
    modifications = lesson_planner.generate_equipment_modifications("basic")
    assert isinstance(modifications, list)
    assert len(modifications) > 0

def test_determine_equipment_needs(lesson_planner):
    """Test determining equipment needs."""
    activities = [
        {
            "equipment": "minimal",
            "name": "warmup"
        },
        {
            "equipment": "basic",
            "name": "main_activity"
        }
    ]
    
    equipment_needs = lesson_planner.determine_equipment_needs(activities)
    assert isinstance(equipment_needs, list)
    assert len(equipment_needs) > 0

def test_generate_objectives(lesson_planner, sample_lesson_parameters):
    """Test generating lesson objectives."""
    objectives = lesson_planner.generate_objectives(
        grade_level=sample_lesson_parameters["grade_level"],
        focus_area=sample_lesson_parameters["focus_area"]
    )
    
    assert isinstance(objectives, list)
    assert len(objectives) > 0
    assert all(isinstance(obj, str) for obj in objectives)

def test_generate_assessment_criteria(lesson_planner, sample_lesson_parameters):
    """Test generating assessment criteria."""
    criteria = lesson_planner.generate_assessment_criteria(
        focus_area=sample_lesson_parameters["focus_area"]
    )
    
    assert isinstance(criteria, dict)
    assert "performance_indicators" in criteria
    assert "evaluation_methods" in criteria
    assert "scoring_rubric" in criteria

def test_generate_safety_considerations(lesson_planner):
    """Test generating safety considerations."""
    activities = [
        {
            "name": "basketball",
            "equipment": "basic",
            "skills": ["dribbling", "passing"]
        }
    ]
    
    safety_considerations = lesson_planner.generate_safety_considerations(activities)
    assert isinstance(safety_considerations, list)
    assert len(safety_considerations) > 0
    assert all(isinstance(consideration, str) for consideration in safety_considerations)

@pytest.mark.asyncio
async def test_error_handling(lesson_planner):
    """Test error handling in lesson planning operations."""
    # Test with invalid parameters
    with pytest.raises(ValueError):
        await lesson_planner.create_lesson_plan(
            grade_level="invalid",
            focus_area="invalid",
            skill_level="invalid",
            class_size=0,
            available_equipment=[]
        )
    
    # Test with invalid template
    with pytest.raises(ValueError):
        lesson_planner.select_template("invalid")
    
    # Test with invalid activity selection
    with pytest.raises(ValueError):
        lesson_planner.select_activity(
            category="invalid",
            activity_type="invalid",
            grade_level="3-5",
            skill_level="intermediate",
            class_size=25,
            available_equipment=["cones", "whistle"]
        ) 