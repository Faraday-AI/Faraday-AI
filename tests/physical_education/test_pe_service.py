import pytest
# PRODUCTION-READY: Removed module-level MediaPipe import to prevent hangs during test collection
# MediaPipe will be mocked in tests or lazily imported in PEService if needed
from unittest.mock import patch, MagicMock, AsyncMock
from app.services.physical_education.pe_service import PEService
from app.services.physical_education.service_integration import service_integration

# Note: Using real db_session from conftest.py (Azure PostgreSQL) for final stage development
# Only mock external dependencies like video processing that would be expensive in tests

@pytest.fixture
def pe_service():
    """Create PEService instance for testing with real database."""
    return PEService()

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
async def test_initialization(pe_service, db_session):
    """Test initialization of PEService with real database and services."""
    # For final stage: use real database, initialize service_integration first
    with patch('app.services.physical_education.pe_service.get_db') as mock_get_db:
        mock_get_db.return_value = iter([db_session])
        
        # Initialize service_integration with real database session
        # This ensures all services are available when PEService initializes
        try:
            await service_integration.initialize(db_session)
        except Exception as e:
            # If already initialized, that's fine
            if "already initialized" not in str(e).lower():
                raise
        
        await pe_service.initialize()
        
        # Verify real services were initialized
        assert pe_service.db == db_session
        assert pe_service.video_processor is not None
        assert pe_service.movement_analyzer is not None
        assert pe_service.assessment_system is not None
        assert pe_service.lesson_planner is not None
        assert pe_service.safety_manager is not None
        assert pe_service.student_manager is not None
        assert pe_service.activity_manager is not None
        # Check that model exists (may be mock if mediapipe failed)
        assert pe_service._model is not None

@pytest.mark.asyncio
async def test_cleanup(pe_service, db_session):
    """Test cleanup of PEService with real services."""
    # Initialize first to set up real services
    with patch('app.services.physical_education.pe_service.get_db') as mock_get_db:
        mock_get_db.return_value = iter([db_session])
        
        if not service_integration._initialized:
            try:
                await service_integration.initialize(db_session)
            except Exception:
                pass
        
        await pe_service.initialize()
        
        # Now test cleanup
        await pe_service.cleanup()
        
        # Verify services were cleaned up
        assert pe_service.video_processor is None
        assert pe_service.movement_analyzer is None
        assert pe_service.db is None

@pytest.mark.asyncio
async def test_process_request(pe_service, db_session, sample_request_data):
    """Test processing different types of requests."""
    # Initialize service first
    with patch('app.services.physical_education.pe_service.get_db') as mock_get_db:
        mock_get_db.return_value = iter([db_session])
        
        try:
            await service_integration.initialize(db_session)
        except Exception:
            pass
        
        await pe_service.initialize()
        
        # Test analyze_movement action - mock video processing to avoid actual video work
        with patch.object(pe_service.video_processor, 'process_video', return_value={"processed": "video"}), \
             patch.object(pe_service.movement_analyzer, 'analyze', return_value={"analysis": "results"}), \
             patch.object(pe_service, 'generate_recommendations', return_value=["recommendation"]):
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
        with patch.object(pe_service, 'generate_activities', return_value=[{"activity": "test"}]), \
             patch.object(pe_service, 'get_assessment_criteria', return_value={"criteria": "test"}):
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
        with patch.object(pe_service, 'calculate_skill_score', return_value=0.8), \
             patch.object(pe_service, 'generate_skill_feedback', return_value="Good job!"):
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
        with patch.object(pe_service, 'get_progress_metrics', return_value={"metrics": "test"}), \
             patch.object(pe_service, 'generate_progress_recommendations', return_value=["recommendation"]):
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
async def test_analyze_movement(pe_service, db_session):
    """Test movement analysis with real services."""
    data = {
        "video_url": "test_video.mp4"
    }
    
    # Initialize service first
    with patch('app.services.physical_education.pe_service.get_db') as mock_get_db:
        mock_get_db.return_value = iter([db_session])
        
        try:
            await service_integration.initialize(db_session)
        except Exception:
            pass
        
        await pe_service.initialize()
        
        # Mock video processing to avoid actual video work, but use real movement_analyzer structure
        with patch.object(pe_service.video_processor, 'process_video', return_value={"processed": "video"}), \
             patch.object(pe_service.movement_analyzer, 'analyze', return_value={"analysis": "results"}), \
             patch.object(pe_service, 'generate_recommendations', return_value=["recommendation"]):
            
            result = await pe_service.analyze_movement(data)
            
            assert result["status"] == "success"
            assert "analysis" in result
            assert "recommendations" in result
            assert result["recommendations"] == ["recommendation"]
        
        # Test with missing video URL
        with pytest.raises(ValueError):
            await pe_service.analyze_movement({})

@pytest.mark.asyncio
async def test_generate_lesson_plan(pe_service, db_session):
    """Test lesson plan generation with real services."""
    data = {
        "grade_level": "5",
        "duration": 45,
        "focus_areas": ["running", "jumping"]
    }
    
    # Initialize service first
    with patch('app.services.physical_education.pe_service.get_db') as mock_get_db:
        mock_get_db.return_value = iter([db_session])
        
        try:
            await service_integration.initialize(db_session)
        except Exception:
            pass
        
        await pe_service.initialize()
        
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
async def test_get_service_metrics(pe_service, db_session):
    """Test getting service metrics with real services."""
    # Initialize service first
    with patch('app.services.physical_education.pe_service.get_db') as mock_get_db:
        mock_get_db.return_value = iter([db_session])
        
        try:
            await service_integration.initialize(db_session)
        except Exception:
            pass
        
        await pe_service.initialize()
        
        # Mock only the methods that depend on database/external state
        # MovementAnalyzer needs async methods for get_total_analyses and get_average_analysis_time
        async def mock_get_total_analyses():
            return 100
        async def mock_get_average_analysis_time():
            return 0.5
        
        pe_service.movement_analyzer.get_total_analyses = mock_get_total_analyses
        pe_service.movement_analyzer.get_average_analysis_time = mock_get_average_analysis_time
        
        with patch.object(pe_service, 'get_lesson_plans_count', return_value=10), \
             patch.object(pe_service, 'get_active_students_count', return_value=5):
            
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