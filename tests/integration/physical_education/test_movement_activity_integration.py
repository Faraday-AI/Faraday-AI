import pytest
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime
from typing import Dict, Any
import aioredis

from app.services.physical_education.services.movement_analysis_service import MovementAnalysisService
from app.services.physical_education.services.activity_service import ActivityService
from app.services.physical_education.models.movement_analysis.movement_models import MovementAnalysis
from app.services.physical_education.models.activity_models import Activity

@pytest.fixture
def mock_db():
    """Create a mock database session."""
    db = Mock()
    db.commit = AsyncMock()
    db.rollback = AsyncMock()
    db.flush = AsyncMock()
    db.add = Mock()
    db.query = Mock()
    return db

@pytest.fixture
def mock_redis():
    """Create a mock Redis client."""
    redis = Mock(spec=aioredis.Redis)
    redis.get = AsyncMock()
    redis.set = AsyncMock()
    redis.delete = AsyncMock()
    return redis

@pytest.fixture
def mock_analyzer():
    """Create a mock MovementAnalyzer."""
    with patch('app.services.physical_education.services.movement_analysis_service.MovementAnalyzer') as mock:
        analyzer = mock.return_value
        analyzer.initialize = AsyncMock()
        analyzer.cleanup = AsyncMock()
        analyzer.analyze = AsyncMock()
        analyzer.extract_movement_patterns = AsyncMock()
        yield analyzer

@pytest.fixture
def movement_service(mock_db, mock_redis, mock_analyzer):
    """Create a MovementAnalysisService instance with mocked dependencies."""
    return MovementAnalysisService(mock_db, mock_redis)

@pytest.fixture
def activity_service(mock_db):
    """Create an ActivityService instance with mocked dependencies."""
    return ActivityService(mock_db)

@pytest.fixture
def sample_movement_data() -> Dict[str, Any]:
    """Create sample movement data for testing."""
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "joint_positions": {
            "left_shoulder": {"x": 0.5, "y": 0.6, "z": 0.1},
            "right_shoulder": {"x": -0.5, "y": 0.6, "z": 0.1}
        },
        "velocities": {
            "left_arm": 0.5,
            "right_arm": 0.6
        },
        "accelerations": {
            "left_arm": 1.0,
            "right_arm": 1.1
        }
    }

@pytest.fixture
def sample_activity() -> Activity:
    """Create a sample activity for testing."""
    return Activity(
        id=1,
        name="Test Activity",
        description="Test Description",
        movement_type="jumping",
        difficulty_level="beginner",
        safety_requirements=["proper warmup", "adequate space"],
        created_at=datetime.utcnow()
    )

@pytest.mark.asyncio
async def test_activity_movement_integration(
    movement_service,
    activity_service,
    mock_db,
    mock_redis,
    mock_analyzer,
    sample_movement_data,
    sample_activity
):
    """Test integration between activity and movement analysis services."""
    # Setup
    student_id = "student123"
    activity_id = sample_activity.id
    
    # Mock activity retrieval
    mock_db.query.return_value.filter.return_value.first.return_value = sample_activity
    
    # Mock movement analysis results
    mock_analyzer.analyze.return_value = {
        "confidence_score": 0.85,
        "movement_quality": "good",
        "issues_detected": [],
        "recommendations": ["Maintain current form"]
    }
    
    mock_analyzer.extract_movement_patterns.return_value = [
        {
            "type": "jump",
            "data": {"height": 0.5, "form": "good"},
            "confidence_score": 0.9
        }
    ]
    
    # Test 1: Create activity and movement analysis
    activity = await activity_service.get_activity(activity_id)
    assert activity is not None
    assert activity.id == activity_id
    
    # Test 2: Create movement analysis for the activity
    movement_analysis = await movement_service.create_movement_analysis(
        student_id=student_id,
        activity_id=activity_id,
        movement_data=sample_movement_data
    )
    
    assert movement_analysis is not None
    assert movement_analysis.activity_id == activity_id
    assert movement_analysis.student_id == student_id
    
    # Verify cache invalidation was called
    mock_redis.delete.assert_called()
    
    # Test 3: Verify movement patterns were created
    patterns = await movement_service.get_movement_patterns(movement_analysis.id)
    assert len(patterns) > 0
    assert patterns[0].pattern_type == "jump"
    
    # Test 4: Verify activity statistics were updated
    stats = await movement_service.get_analysis_statistics(student_id)
    assert stats["total_analyses"] > 0
    assert stats["average_confidence_score"] > 0

@pytest.mark.asyncio
async def test_error_handling_integration(
    movement_service,
    activity_service,
    mock_db,
    mock_redis,
    mock_analyzer,
    sample_movement_data
):
    """Test error handling in integrated services."""
    # Setup
    student_id = "student123"
    activity_id = 999  # Non-existent activity
    
    # Mock activity retrieval to return None
    mock_db.query.return_value.filter.return_value.first.return_value = None
    
    # Test 1: Attempt to create movement analysis for non-existent activity
    with pytest.raises(ValueError):
        await movement_service.create_movement_analysis(
            student_id=student_id,
            activity_id=activity_id,
            movement_data=sample_movement_data
        )
    
    # Verify rollback was called
    mock_db.rollback.assert_called_once()
    
    # Verify cache invalidation was not called
    mock_redis.delete.assert_not_called()

@pytest.mark.asyncio
async def test_caching_integration(
    movement_service,
    mock_db,
    mock_redis,
    mock_analyzer,
    sample_movement_data,
    sample_activity
):
    """Test Redis caching integration."""
    # Setup
    student_id = "student123"
    activity_id = sample_activity.id
    
    # Mock activity retrieval
    mock_db.query.return_value.filter.return_value.first.return_value = sample_activity
    
    # Mock movement analysis results
    mock_analyzer.analyze.return_value = {
        "confidence_score": 0.85,
        "movement_quality": "good"
    }
    
    # Test 1: First call should hit the database
    await movement_service.get_movement_analysis(activity_id)
    mock_db.query.assert_called()
    
    # Test 2: Second call should hit the cache
    mock_db.query.reset_mock()
    mock_redis.get.return_value = '{"id": 1, "activity_id": 1}'
    await movement_service.get_movement_analysis(activity_id)
    mock_db.query.assert_not_called()
    
    # Test 3: Update should invalidate cache
    await movement_service.update_movement_analysis(
        activity_id,
        movement_data=sample_movement_data
    )
    mock_redis.delete.assert_called() 