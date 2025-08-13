import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch
from fastapi import HTTPException
from typing import Dict, Any
import json
import redis.asyncio as redis
from sqlalchemy.exc import SQLAlchemyError
import numpy as np
from sqlalchemy.orm import Session
from functools import wraps
import inspect
import time

from app.services.physical_education.services.movement_analysis_service import (
    MovementAnalysisService,
    AnalysisTimeoutError,
    AnalysisOverloadError,
    MovementAnalysis,
    MovementAnalysisResult,
    MovementAnalysisMetrics,
    MovementAnalysisError
)
from app.models.movement_analysis.analysis.movement_analysis import MovementAnalysis as MovementAnalysisModel
from app.services.physical_education.activity_manager import ActivityManager
from app.services.physical_education.services.safety_manager import SafetyManager
from app.services.physical_education.services.student_manager import StudentManager
from app.services.physical_education.services.video_processor import VideoProcessor
from app.services.physical_education.services.cache_monitor import CacheMonitor
from app.services.physical_education.services.movement_analyzer import MovementAnalyzer
from app.services.physical_education.models.skill_assessment.skill_assessment_models import SkillModels
from app.services.physical_education.services.rate_limiter import RateLimiter
from app.services.physical_education.services.circuit_breaker import CircuitBreaker

# Mock ActivityVisualizationManager to avoid moviepy dependency
class MockActivityVisualizationManager:
    def __init__(self):
        self.visualization_types = []
        self.visualization_config = {}
        self.export_dir = "exports/visualizations"
        self.drill_down_state = {}
    
    def generate_visualizations(self, *args, **kwargs):
        return {}
    
    def _save_video(self, *args, **kwargs):
        return None

@pytest.fixture
async def redis_client():
    """Create a Redis client for testing."""
    redis_client = redis.Redis(host='redis', port=6379, db=1)
    yield redis_client
    await redis_client.flushdb()
    await redis_client.close()

@pytest.fixture
async def db_session():
    """Create a database session for testing."""
    # Setup test database session
    session = Mock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.flush = AsyncMock()
    session.delete = AsyncMock()
    session.add = Mock()
    session.query = Mock()
    yield session

@pytest.fixture
async def service(db_session, redis_client):
    """Create a MovementAnalysisService instance."""
    # Create mocks for all dependencies
    mock_analyzer = Mock(spec=MovementAnalyzer)
    mock_analyzer.initialize = AsyncMock()
    mock_analyzer.cleanup = AsyncMock()
    mock_analyzer.analyze = AsyncMock(return_value={
        'confidence_score': 0.85,
        'movement_quality': 'good',
        'issues_detected': [],
        'recommendations': ['Maintain current form']
    })
    mock_analyzer.extract_movement_patterns = AsyncMock(return_value=[])
    
    mock_activity_manager = Mock(spec=ActivityManager)
    mock_safety_manager = Mock(spec=SafetyManager)
    mock_student_manager = Mock(spec=StudentManager)
    mock_video_processor = Mock(spec=VideoProcessor)
    
    # Create service instance
    service = MovementAnalysisService(db_session, redis_client)
    
    # Replace dependencies with mocks
    service.analyzer = mock_analyzer
    service.activity_manager = mock_activity_manager
    service.safety_manager = mock_safety_manager
    service.student_manager = mock_student_manager
    service.video_processor = mock_video_processor
    
    # Mock rate limiter and circuit breaker
    service.rate_limiter = Mock(spec=RateLimiter)
    service.rate_limiter.acquire_token = AsyncMock(return_value=True)
    service.rate_limiter.cleanup = AsyncMock()
    
    service.circuit_breaker = Mock(spec=CircuitBreaker)
    service.circuit_breaker.state = "closed"  # Set initial state
    service.circuit_breaker._should_reset = Mock(return_value=True)  # Allow reset attempts
    service.circuit_breaker.cleanup = AsyncMock()
    
    # Mock cache monitor
    service.cache_monitor = Mock(spec=CacheMonitor)
    service.cache_monitor.check_cache_health = AsyncMock(return_value={"success": True})
    service.cache_monitor.track_cache_hit = AsyncMock()
    service.cache_monitor.track_cache_miss = AsyncMock()
    service.cache_monitor.track_cache_operation = AsyncMock()
    service.cache_monitor.track_cache_error = AsyncMock()
    
    # Initialize service
    await service.initialize()
    
    try:
        yield service
    finally:
        # Cleanup
        await service.cleanup()

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
        }
    }

@pytest.fixture
def sample_analysis_results() -> Dict[str, Any]:
    """Create sample analysis results for testing."""
    return {
        "confidence_score": 0.85,
        "movement_quality": "good",
        "issues_detected": [],
        "recommendations": ["Maintain current form"],
        "metrics": {
            "symmetry_score": 0.9,
            "stability_score": 0.8,
            "efficiency_score": 0.85
        }
    }

@pytest.fixture
def sample_movement_patterns() -> list:
    """Create sample movement patterns for testing."""
    return [
        {
            "type": "arm_swing",
            "data": {
                "amplitude": 0.8,
                "frequency": 1.2,
                "symmetry": 0.9
            },
            "confidence_score": 0.9
        },
        {
            "type": "shoulder_rotation",
            "data": {
                "range": 85.0,
                "smoothness": 0.85,
                "control": 0.88
            },
            "confidence_score": 0.87
        }
    ]

@pytest.fixture
def mock_activity_manager():
    manager = Mock(spec=ActivityManager)
    manager.visualization_manager = MockActivityVisualizationManager()
    return manager

@pytest.mark.asyncio
async def test_initialization(service):
    """Test service initialization."""
    assert service.rate_limiter is not None
    assert service.circuit_breaker is not None
    assert service.cache_monitor is not None
    assert service.batch_size == 50
    assert service.max_concurrent_batches == 2
    assert service.analysis_timeout == 30

@pytest.mark.asyncio
async def test_create_movement_analysis(service, sample_movement_data):
    """Test creating a movement analysis."""
    result = await service.create_movement_analysis(
        student_id="student1",
        activity_id=1,
        movement_data=sample_movement_data
    )
    
    assert isinstance(result, MovementAnalysis)
    assert result.student_id == "student1"
    assert result.activity_id == 1
    assert result.is_completed is True

@pytest.mark.asyncio
async def test_rate_limiting(service, sample_movement_data):
    """Test rate limiting functionality."""
    # Setup rate limiter to reject requests
    service.rate_limiter.acquire_token.return_value = False
    
    with pytest.raises(HTTPException) as exc_info:
        await service.create_movement_analysis(
            student_id="student1",
            activity_id=1,
            movement_data=sample_movement_data
        )
    
    assert exc_info.value.status_code == 429
    assert "Rate limit exceeded" in str(exc_info.value.detail)

@pytest.mark.asyncio
async def test_circuit_breaker(service, sample_movement_data):
    """Test circuit breaker functionality."""
    # Setup circuit breaker to be open
    service.circuit_breaker.state = "open"
    
    with pytest.raises(HTTPException) as exc_info:
        await service.create_movement_analysis(
            student_id="student1",
            activity_id=1,
            movement_data=sample_movement_data
        )
    
    assert exc_info.value.status_code == 503
    assert "Service temporarily unavailable" in str(exc_info.value.detail)

@pytest.mark.asyncio
async def test_batch_processing(service, sample_movement_data):
    """Test batch processing of multiple analyses."""
    movement_data_list = [sample_movement_data] * 100
    results = await service.batch_process_analyses(
        student_id="student1",
        activity_id=1,
        movement_data_list=movement_data_list
    )
    
    assert len(results) == 100
    assert all(isinstance(result, MovementAnalysis) for result in results)

@pytest.mark.asyncio
async def test_concurrent_operations(service, sample_movement_data):
    """Test concurrent operations handling."""
    # Get the actual service instance by awaiting the fixture
    service_instance = await anext(service)
    
    # Mock Redis client
    mock_redis = Mock(spec=redis.Redis)
    mock_redis.set = AsyncMock(return_value=True)
    mock_redis.get = AsyncMock(return_value=None)
    mock_redis.delete = AsyncMock(return_value=True)
    mock_redis.dbsize = AsyncMock(return_value=0)
    
    # Update service dependencies
    service_instance.redis = mock_redis
    service_instance.cache_monitor.redis = mock_redis
    
    # Mock both decorators
    def mock_track_metrics(endpoint: str = None):
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # For create_movement_analysis, we know it's a method with self, student_id, activity_id, and movement_data
                if func.__name__ == 'create_movement_analysis':
                    self_arg = args[0]
                    student_id = kwargs.get('student_id')
                    activity_id = kwargs.get('activity_id')
                    movement_data = kwargs.get('movement_data')
                    return await func(self_arg, student_id=student_id, activity_id=activity_id, movement_data=movement_data)
                else:
                    # For other methods, use the original behavior
                    return await func(*args, **kwargs)
            return wrapper
        return decorator

    def mock_cache_result(ttl: int = 300):
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Pass through all arguments
                return await func(*args, **kwargs)
            return wrapper
        return decorator

    # Mock circuit breaker
    async def mock_circuit_breaker(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if service_instance.circuit_breaker.state == "open":
                raise HTTPException(status_code=503, detail="Service temporarily unavailable")
            return await func(*args, **kwargs)
        return wrapper

    service_instance.circuit_breaker.__call__ = mock_circuit_breaker
    service_instance.circuit_breaker.state = "closed"

    # Patch both decorators
    with patch('app.core.monitoring.track_metrics', new=mock_track_metrics), \
         patch('app.services.physical_education.services.movement_analysis_service.cache_result', new=mock_cache_result):
        
        async def simulate_analysis(student_id: str, activity_id: int):
            try:
                # Simulate rate limiting
                if activity_id % 3 == 0:
                    service_instance.rate_limiter.acquire_token.return_value = False
                else:
                    service_instance.rate_limiter.acquire_token.return_value = True
                    
                # Simulate circuit breaker
                if activity_id % 5 == 0:
                    service_instance.circuit_breaker.state = "open"
                else:
                    service_instance.circuit_breaker.state = "closed"
                    
                result = await service_instance.create_movement_analysis(
                    student_id=student_id,
                    activity_id=activity_id,
                    movement_data=sample_movement_data
                )
                return result
            except HTTPException as e:
                if "Rate limit exceeded" in str(e):
                    return "rate_limit_error"
                elif "Circuit breaker is open" in str(e):
                    return "circuit_breaker_error"
                raise
        
        # Simulate concurrent analyses with different scenarios
        tasks = [
            simulate_analysis(f"student{i}", i)
            for i in range(10)
        ]
        
        # Add a task that should trigger rate limiting
        service_instance.rate_limiter.acquire_token.return_value = False
        tasks.append(simulate_analysis("rate_limited_student", 11))
        
        # Add a task that should trigger circuit breaker
        service_instance.circuit_breaker.state = "open"
        tasks.append(simulate_analysis("circuit_breaker_student", 12))
        
        # Run all tasks with a timeout
        try:
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=30.0
            )
        except asyncio.TimeoutError:
            pytest.fail("Test timed out while waiting for concurrent operations")
        
        # Analyze results
        successful_results = []
        rate_limit_errors = []
        circuit_breaker_errors = []
        other_errors = []
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                if isinstance(result, HTTPException):
                    if result.status_code == 429:
                        rate_limit_errors.append((i, result))
                    elif result.status_code == 503:
                        circuit_breaker_errors.append((i, result))
                    else:
                        other_errors.append((i, result))
                else:
                    other_errors.append((i, result))
            else:
                successful_results.append(result)
        
        # Print detailed error information
        if rate_limit_errors:
            print(f"Rate limit errors: {len(rate_limit_errors)}")
            for i, error in rate_limit_errors:
                print(f"Task {i} failed with rate limit error: {str(error)}")
        
        if circuit_breaker_errors:
            print(f"Circuit breaker errors: {len(circuit_breaker_errors)}")
            for i, error in circuit_breaker_errors:
                print(f"Task {i} failed with circuit breaker error: {str(error)}")
        
        if other_errors:
            print(f"Other errors: {len(other_errors)}")
            for i, error in other_errors:
                print(f"Task {i} failed with error: {str(error)}")
        
        # Verify results
        assert len(successful_results) >= 8  # At least 80% should succeed
        assert len(rate_limit_errors) == 1  # One rate limit error
        assert len(circuit_breaker_errors) == 1  # One circuit breaker error

@pytest.mark.asyncio
async def test_error_handling(service, sample_movement_data):
    """Test error handling in various scenarios."""
    # Test database error
    service.db.commit.side_effect = SQLAlchemyError("Database error")
    
    with pytest.raises(HTTPException) as exc_info:
        await service.create_movement_analysis(
            student_id="student1",
            activity_id=1,
            movement_data=sample_movement_data
        )
    
    assert exc_info.value.status_code == 500
    
    # Test timeout error
    service.analyzer.analyze.side_effect = asyncio.TimeoutError()
    
    with pytest.raises(HTTPException) as exc_info:
        await service.create_movement_analysis(
            student_id="student1",
            activity_id=1,
            movement_data=sample_movement_data
        )
    
    assert exc_info.value.status_code == 500

@pytest.mark.asyncio
async def test_performance_metrics(service):
    """Test performance metrics collection."""
    metrics = await service.get_performance_metrics()
    
    assert metrics is not None
    assert 'active_analyses' in metrics
    assert 'batch_size' in metrics
    assert 'circuit_breaker_state' in metrics
    assert 'rate_limiter_stats' in metrics
    assert 'cache_stats' in metrics
    assert 'error_counts' in metrics

@pytest.mark.asyncio
async def test_cache_operations(service, sample_movement_data):
    """Test cache operations."""
    # Test cache miss
    service.redis.get.return_value = None
    result = await service.get_movement_analysis(1)
    assert service.redis.set.called
    
    # Test cache hit
    service.redis.get.return_value = json.dumps({"id": 1})
    result = await service.get_movement_analysis(1)
    assert not service.redis.set.called

@pytest.mark.asyncio
async def test_cleanup(service):
    """Test service cleanup."""
    await service.cleanup()
    assert service.analyzer.cleanup.called
    assert service.rate_limiter.cleanup.called
    assert service.circuit_breaker.cleanup.called
    assert service.cache_monitor.cleanup.called

@pytest.mark.asyncio
async def test_create_movement_analysis_success(
    service,
    mock_db,
    mock_analyzer,
    sample_movement_data,
    sample_analysis_results,
    sample_movement_patterns
):
    """Test successful creation of movement analysis."""
    # Setup
    student_id = "student123"
    activity_id = 456
    mock_analyzer.analyze.return_value = sample_analysis_results
    mock_analyzer.extract_movement_patterns.return_value = sample_movement_patterns
    
    # Execute
    result = await service.create_movement_analysis(student_id, activity_id, sample_movement_data)
    
    # Verify
    assert isinstance(result, MovementAnalysis)
    assert result.student_id == student_id
    assert result.activity_id == activity_id
    assert result.movement_data == sample_movement_data
    assert result.analysis_results == sample_analysis_results
    assert result.confidence_score == sample_analysis_results["confidence_score"]
    assert result.is_completed is True
    
    mock_db.add.assert_called()
    mock_db.flush.assert_called_once()
    mock_db.commit.assert_called_once()

@pytest.mark.asyncio
async def test_create_movement_analysis_db_error(
    service,
    mock_db,
    mock_analyzer,
    sample_movement_data
):
    """Test database error handling during movement analysis creation."""
    # Setup
    mock_db.commit.side_effect = SQLAlchemyError("Database error")
    
    # Execute and verify
    with pytest.raises(SQLAlchemyError):
        await service.create_movement_analysis("student123", 456, sample_movement_data)
    
    mock_db.rollback.assert_called_once()

@pytest.mark.asyncio
async def test_get_movement_analysis(service, mock_db):
    """Test retrieving a movement analysis by ID."""
    # Setup
    analysis_id = 123
    expected_analysis = MovementAnalysisModel(id=analysis_id)
    mock_db.query.return_value.filter.return_value.first.return_value = expected_analysis
    
    # Execute
    result = await service.get_movement_analysis(analysis_id)
    
    # Verify
    assert result == expected_analysis
    mock_db.query.assert_called_with(MovementAnalysisModel)

@pytest.mark.asyncio
async def test_get_student_analyses(service, mock_db):
    """Test retrieving all analyses for a student."""
    # Setup
    student_id = "student123"
    expected_analyses = [MovementAnalysisModel(id=1), MovementAnalysisModel(id=2)]
    mock_db.query.return_value.filter.return_value.all.return_value = expected_analyses
    
    # Execute
    result = await service.get_student_analyses(student_id)
    
    # Verify
    assert result == expected_analyses
    mock_db.query.assert_called_with(MovementAnalysisModel)

@pytest.mark.asyncio
async def test_update_movement_analysis(
    service,
    mock_db,
    mock_analyzer,
    sample_movement_data,
    sample_analysis_results,
    sample_movement_patterns
):
    """Test updating a movement analysis."""
    # Setup
    analysis_id = 123
    existing_analysis = MovementAnalysisModel(id=analysis_id)
    mock_db.query.return_value.filter.return_value.first.return_value = existing_analysis
    mock_analyzer.analyze.return_value = sample_analysis_results
    mock_analyzer.extract_movement_patterns.return_value = sample_movement_patterns
    
    # Execute
    result = await service.update_movement_analysis(
        analysis_id,
        movement_data=sample_movement_data,
        is_completed=True
    )
    
    # Verify
    assert result == existing_analysis
    assert result.movement_data == sample_movement_data
    assert result.analysis_results == sample_analysis_results
    assert result.is_completed is True
    mock_db.commit.assert_called_once()

@pytest.mark.asyncio
async def test_delete_movement_analysis(service, mock_db):
    """Test deleting a movement analysis."""
    # Setup
    analysis_id = 123
    existing_analysis = MovementAnalysisModel(id=analysis_id)
    mock_db.query.return_value.filter.return_value.first.return_value = existing_analysis
    
    # Execute
    result = await service.delete_movement_analysis(analysis_id)
    
    # Verify
    assert result is True
    mock_db.delete.assert_called_with(existing_analysis)
    mock_db.commit.assert_called_once()

@pytest.mark.asyncio
async def test_get_analysis_statistics(service, mock_db):
    """Test retrieving analysis statistics for a student."""
    # Setup
    student_id = "student123"
    analyses = [
        MovementAnalysisModel(
            id=1,
            confidence_score=0.8,
            is_completed=True,
            created_at=datetime(2024, 1, 1)
        ),
        MovementAnalysisModel(
            id=2,
            confidence_score=0.9,
            is_completed=True,
            created_at=datetime(2024, 1, 2)
        ),
        MovementAnalysisModel(
            id=3,
            confidence_score=0.7,
            is_completed=False,
            created_at=datetime(2024, 1, 3)
        )
    ]
    mock_db.query.return_value.filter.return_value.all.return_value = analyses
    
    # Execute
    stats = await service.get_analysis_statistics(student_id)
    
    # Verify
    assert stats["total_analyses"] == 3
    assert stats["completed_analyses"] == 2
    assert stats["average_confidence_score"] == 0.8
    assert stats["last_analysis_date"] == datetime(2024, 1, 3)

@pytest.mark.asyncio
async def test_get_movement_patterns(service, mock_db):
    """Test retrieving movement patterns for an analysis."""
    # Setup
    analysis_id = 123
    expected_patterns = [
        MovementAnalysisModel(id=1, analysis_id=analysis_id),
        MovementAnalysisModel(id=2, analysis_id=analysis_id)
    ]
    mock_db.query.return_value.filter.return_value.all.return_value = expected_patterns
    
    # Execute
    result = await service.get_movement_patterns(analysis_id)
    
    # Verify
    assert result == expected_patterns
    mock_db.query.assert_called_with(MovementAnalysisModel) 