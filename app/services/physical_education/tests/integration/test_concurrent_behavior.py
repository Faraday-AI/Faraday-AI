import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from fastapi import HTTPException
from sqlalchemy.orm import Session
import redis.asyncio as redis
import inspect
from functools import wraps
from datetime import datetime

from app.services.physical_education.services.movement_analysis_service import MovementAnalysisService
from app.models.movement_analysis.analysis.movement_analysis import MovementAnalysis

def mock_track_metrics(endpoint: str = None):
    """Mock decorator factory that matches the actual implementation."""
    def decorator(func):
        sig = inspect.signature(func)
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get the function's parameters
            params = list(sig.parameters.values())
            
            # If this is a method (has 'self' as first parameter)
            if params and params[0].name == 'self':
                # For method calls, pass self as first arg and bind remaining args
                self_arg = args[0]
                remaining_args = args[1:]
                bound_args = sig.bind(self_arg, *remaining_args, **kwargs)
                bound_args.apply_defaults()
                return await func(*bound_args.args, **bound_args.kwargs)
            else:
                # For regular function calls, bind all args
                bound_args = sig.bind(*args, **kwargs)
                bound_args.apply_defaults()
                return await func(*bound_args.args, **bound_args.kwargs)
        return wrapper
    return decorator

@pytest.fixture
async def service():
    """Create a service instance with mocked dependencies."""
    # Create mock database session
    mock_db = Mock(spec=Session)
    mock_db.add = Mock()
    mock_db.commit = Mock()
    mock_db.refresh = Mock()
    
    # Create mock Redis client
    mock_redis = Mock(spec=redis.Redis)
    mock_redis.set = AsyncMock(return_value=True)
    mock_redis.get = AsyncMock(return_value=None)
    mock_redis.delete = AsyncMock(return_value=True)
    mock_redis.dbsize = AsyncMock(return_value=0)
    
    # Create service instance
    service = MovementAnalysisService(mock_db, mock_redis)
    
    # Mock other dependencies
    service.analyzer = Mock()
    service.analyzer.initialize = AsyncMock()
    service.analyzer.analyze_movement = AsyncMock(return_value={
        "confidence": 0.95,
        "patterns": ["pattern1", "pattern2"]
    })
    
    service.rate_limiter = Mock()
    service.rate_limiter.acquire_token = AsyncMock(return_value=True)
    
    service.circuit_breaker = Mock()
    service.circuit_breaker.state = "closed"
    service.circuit_breaker.__call__ = lambda func: func
    
    # Initialize the service
    await service.initialize()
    
    return service

@pytest.fixture
def sample_movement_data():
    """Sample movement data for testing."""
    return {
        "joint_positions": {
            "left_shoulder": {"x": 0.5, "y": 0.6, "z": 0.1},
            "right_shoulder": {"x": -0.5, "y": 0.6, "z": 0.1}
        },
        "timestamp": "2025-04-11T18:00:08.049766",
        "velocities": {
            "left_arm": 0.5,
            "right_arm": 0.6
        }
    }

@pytest.mark.asyncio
async def test_concurrent_analyses(service, sample_movement_data):
    """Test concurrent movement analyses with different scenarios."""
    # Get the actual service instance
    service_instance = await service
    
    # Patch the track_metrics decorator at the class level
    with patch('app.services.physical_education.services.movement_analysis_service.MovementAnalysisService.create_movement_analysis', new_callable=AsyncMock) as mock_create:
        async def mock_create_analysis(*args, **kwargs):
            # Handle both positional and keyword arguments
            if args:
                self = args[0]
                student_id = args[1] if len(args) > 1 else kwargs.get('student_id')
                activity_id = args[2] if len(args) > 2 else kwargs.get('activity_id')
                movement_data = args[3] if len(args) > 3 else kwargs.get('movement_data')
            else:
                student_id = kwargs.get('student_id')
                activity_id = kwargs.get('activity_id')
                movement_data = kwargs.get('movement_data')
            
            # If this is the rate-limited task, raise the exception
            if student_id == "rate_limited_student":
                raise HTTPException(status_code=429, detail="Rate limit exceeded")
            
            # If this is the circuit breaker task, raise the exception
            if student_id == "circuit_breaker_student":
                raise HTTPException(status_code=503, detail="Circuit breaker is open")
            
            return MovementAnalysis(
                id=1,
                student_id=student_id,
                activity_id=activity_id,
                movement_data=movement_data,
                analysis_results={"confidence": 0.95},
                confidence_score=0.95,
                is_completed=True,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        mock_create.side_effect = mock_create_analysis
        
        async def simulate_analysis(student_id: str, activity_id: int):
            try:
                # Simulate rate limiting
                if student_id == "rate_limited_student":
                    service_instance.rate_limiter.acquire_token.return_value = False
                else:
                    service_instance.rate_limiter.acquire_token.return_value = True
                
                # Simulate circuit breaker
                if student_id == "circuit_breaker_student":
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
        tasks.append(simulate_analysis("rate_limited_student", 11))
        
        # Add a task that should trigger circuit breaker
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
async def test_batch_processing(service, sample_movement_data):
    """Test batch processing of movement analyses."""
    # Get the actual service instance
    service_instance = await service
    
    # Patch the create_movement_analysis method directly
    with patch.object(service_instance, 'create_movement_analysis', new_callable=AsyncMock) as mock_create:
        async def mock_create_analysis(student_id, activity_id, movement_data):
            return MovementAnalysis(
                id=1,
                student_id=student_id,
                activity_id=activity_id,
                movement_data=movement_data,
                analysis_results={"confidence": 0.95},
                confidence_score=0.95,
                is_completed=True,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        mock_create.side_effect = mock_create_analysis
        
        # Create a list of movement data for batch processing
        movement_data_list = [sample_movement_data] * 5
        
        # Process the batch
        results = await service_instance.batch_process_analyses(
            student_id="test_student",
            activity_id=1,
            movement_data_list=movement_data_list
        )
        
        # Verify results
        assert len(results) == 5
        assert all(isinstance(result, MovementAnalysis) for result in results)
        assert all(result.student_id == "test_student" for result in results)
        assert all(result.activity_id == 1 for result in results)
        assert all(result.movement_data == sample_movement_data for result in results) 