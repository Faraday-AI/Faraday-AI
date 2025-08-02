import pytest
import mediapipe as mp
from unittest.mock import patch, MagicMock, AsyncMock
from app.services.physical_education.pe_service import PEService
from app.services.physical_education.video_processor import VideoProcessor
from app.services.physical_education.movement_analyzer import MovementAnalyzer

@pytest.fixture
def pe_service():
    """Create PEService instance for testing."""
    return PEService()

@pytest.fixture
def mock_video_processor():
    """Create a mock VideoProcessor."""
    return MagicMock(spec=VideoProcessor)

@pytest.fixture
def mock_movement_analyzer():
    """Create a mock MovementAnalyzer."""
    return MagicMock(spec=MovementAnalyzer)

@pytest.fixture
def sample_request_data():
    """Create sample request data."""
    return {
        "action": "analyze_movement",
        "data": {
            "video_url": "test_video.mp4"
        }
    }

@pytest.mark.asyncio
async def test_initialization(pe_service, mock_video_processor, mock_movement_analyzer):
    """Test initialization of PEService."""
    with patch.object(pe_service, 'video_processor', mock_video_processor), \
         patch.object(pe_service, 'movement_analyzer', mock_movement_analyzer):
        
        await pe_service.initialize()
        
        mock_video_processor.initialize.assert_called_once()
        mock_movement_analyzer.initialize.assert_called_once()
        assert isinstance(pe_service._model, mp.solutions.pose.Pose)

@pytest.mark.asyncio
async def test_cleanup(pe_service, mock_video_processor, mock_movement_analyzer):
    """Test cleanup of PEService."""
    with patch.object(pe_service, 'video_processor', mock_video_processor), \
         patch.object(pe_service, 'movement_analyzer', mock_movement_analyzer):
        
        await pe_service.cleanup()
        
        mock_video_processor.cleanup.assert_called_once()
        mock_movement_analyzer.cleanup.assert_called_once()

@pytest.mark.asyncio
async def test_process_request(pe_service, sample_request_data):
    """Test processing different types of requests."""
    # Test analyze_movement action
    with patch.object(pe_service, 'analyze_movement', return_value={"status": "success"}):
        result = await pe_service.process_request(sample_request_data)
        assert result["status"] == "success"
    
    # Test generate_lesson_plan action
    lesson_plan_data = {
        "action": "generate_lesson_plan",
        "data": {
            "grade_level": "5",
            "duration": 45,
            "focus_areas": ["running", "jumping"]
        }
    }
    with patch.object(pe_service, 'generate_lesson_plan', return_value={"status": "success"}):
        result = await pe_service.process_request(lesson_plan_data)
        assert result["status"] == "success"
    
    # Test assess_skill action
    skill_data = {
        "action": "assess_skill",
        "data": {
            "student_id": "123",
            "skill_type": "running",
            "assessment_data": {}
        }
    }
    with patch.object(pe_service, 'assess_skill', return_value={"status": "success"}):
        result = await pe_service.process_request(skill_data)
        assert result["status"] == "success"
    
    # Test track_progress action
    progress_data = {
        "action": "track_progress",
        "data": {
            "student_id": "123",
            "time_period": "week"
        }
    }
    with patch.object(pe_service, 'track_progress', return_value={"status": "success"}):
        result = await pe_service.process_request(progress_data)
        assert result["status"] == "success"
    
    # Test invalid action
    invalid_data = {
        "action": "invalid_action",
        "data": {}
    }
    with pytest.raises(ValueError):
        await pe_service.process_request(invalid_data)

@pytest.mark.asyncio
async def test_analyze_movement(pe_service, mock_video_processor, mock_movement_analyzer):
    """Test movement analysis."""
    data = {
        "video_url": "test_video.mp4"
    }
    
    with patch.object(pe_service, 'video_processor', mock_video_processor), \
         patch.object(pe_service, 'movement_analyzer', mock_movement_analyzer), \
         patch.object(pe_service, 'generate_recommendations', return_value=["recommendation"]):
        
        mock_video_processor.process_video.return_value = {"processed": "video"}
        mock_movement_analyzer.analyze.return_value = {"analysis": "results"}
        
        result = await pe_service.analyze_movement(data)
        
        assert result["status"] == "success"
        assert "analysis" in result
        assert "recommendations" in result
        assert result["recommendations"] == ["recommendation"]
        
        # Test with missing video URL
        with pytest.raises(ValueError):
            await pe_service.analyze_movement({})

@pytest.mark.asyncio
async def test_generate_lesson_plan(pe_service):
    """Test lesson plan generation."""
    data = {
        "grade_level": "5",
        "duration": 45,
        "focus_areas": ["running", "jumping"]
    }
    
    with patch.object(pe_service, 'generate_activities', return_value=[{"activity": "test"}]), \
         patch.object(pe_service, 'get_assessment_criteria', return_value={"criteria": "test"}):
        
        result = await pe_service.generate_lesson_plan(data)
        
        assert result["status"] == "success"
        assert "lesson_plan" in result
        assert result["lesson_plan"]["grade_level"] == "5"
        assert result["lesson_plan"]["duration"] == 45
        assert result["lesson_plan"]["focus_areas"] == ["running", "jumping"]
        assert "activities" in result["lesson_plan"]
        assert "assessment_criteria" in result["lesson_plan"]

@pytest.mark.asyncio
async def test_assess_skill(pe_service):
    """Test skill assessment."""
    data = {
        "student_id": "123",
        "skill_type": "running",
        "assessment_data": {}
    }
    
    with patch.object(pe_service, 'calculate_skill_score', return_value=0.8), \
         patch.object(pe_service, 'generate_skill_feedback', return_value="Good job!"):
        
        result = await pe_service.assess_skill(data)
        
        assert result["status"] == "success"
        assert "assessment" in result
        assert result["assessment"]["student_id"] == "123"
        assert result["assessment"]["skill_type"] == "running"
        assert result["assessment"]["score"] == 0.8
        assert result["assessment"]["feedback"] == "Good job!"

@pytest.mark.asyncio
async def test_track_progress(pe_service):
    """Test progress tracking."""
    data = {
        "student_id": "123",
        "time_period": "week"
    }
    
    with patch.object(pe_service, 'get_progress_metrics', return_value={"metrics": "test"}), \
         patch.object(pe_service, 'generate_progress_recommendations', return_value=["recommendation"]):
        
        result = await pe_service.track_progress(data)
        
        assert result["status"] == "success"
        assert "progress" in result
        assert result["progress"]["student_id"] == "123"
        assert result["progress"]["time_period"] == "week"
        assert "metrics" in result["progress"]
        assert "recommendations" in result["progress"]

@pytest.mark.asyncio
async def test_get_service_metrics(pe_service, mock_movement_analyzer):
    """Test getting service metrics."""
    with patch.object(pe_service, 'movement_analyzer', mock_movement_analyzer), \
         patch.object(pe_service, 'get_lesson_plans_count', return_value=10), \
         patch.object(pe_service, 'get_active_students_count', return_value=5):
        
        mock_movement_analyzer.get_total_analyses.return_value = 100
        mock_movement_analyzer.get_average_analysis_time.return_value = 0.5
        
        metrics = await pe_service.get_service_metrics()
        
        assert "total_analyses" in metrics
        assert "lesson_plans_generated" in metrics
        assert "active_students" in metrics
        assert "average_analysis_time" in metrics
        assert metrics["total_analyses"] == 100
        assert metrics["lesson_plans_generated"] == 10
        assert metrics["active_students"] == 5
        assert metrics["average_analysis_time"] == 0.5

@pytest.mark.asyncio
async def test_get_lesson_plans_count(pe_service):
    """Test getting lesson plans count."""
    count = await pe_service.get_lesson_plans_count()
    assert isinstance(count, int)

@pytest.mark.asyncio
async def test_get_active_students_count(pe_service):
    """Test getting active students count."""
    count = await pe_service.get_active_students_count()
    assert isinstance(count, int) 