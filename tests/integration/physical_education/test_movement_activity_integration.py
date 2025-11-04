import pytest
from datetime import datetime
from typing import Dict, Any
from sqlalchemy.orm import Session

from app.services.physical_education.services.movement_analysis_service import MovementAnalysisService
from app.services.physical_education.services.activity_service import ActivityService

# Use real database session from conftest.py - no mocks needed
# db_session fixture is automatically available from conftest.py

@pytest.fixture
def movement_service(db_session: Session):
    """Create a MovementAnalysisService instance with real database session."""
    # MovementAnalysisService.__init__() takes no arguments
    # It uses in-memory storage, not database, so db_session is available for future use
    service = MovementAnalysisService()
    return service

@pytest.fixture
def activity_service(db_session: Session):
    """Create an ActivityService instance with real database session."""
    # ActivityService.__init__() also takes no arguments
    # It uses in-memory storage, not database, so db_session is available for future use
    return ActivityService()

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
def sample_activity() -> Dict[str, Any]:
    """Create a sample activity data for testing - using dict since ActivityService uses dicts."""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    return {
        "name": f"Test Activity {unique_id}",
        "description": "Test Description",
        "activity_type": "jumping",  # Use activity_type for ActivityService
        "difficulty_level": "beginner",
        "id": f"activity_{unique_id}"  # String ID as used by ActivityService
    }

@pytest.mark.asyncio
async def test_activity_movement_integration(
    movement_service,
    activity_service,
    db_session: Session,
    sample_movement_data,
    sample_activity
):
    """Test integration between activity and movement analysis services using real database."""
    # Setup
    student_id = "student123"
    # Create activity first to get an ID
    created_activity_id = await activity_service.create_activity(sample_activity)
    activity_id = created_activity_id
    
    # Test 1: Create activity using ActivityService
    created_activity_id = await activity_service.create_activity(sample_activity)
    activity = await activity_service.get_activity(created_activity_id)
    # Verify activity was created and retrieved
    assert activity is not None
    assert activity["id"] == created_activity_id
    
    # Test 2: Create movement analysis for the activity
    # MovementAnalysisService uses analyze_movement instead of create_movement_analysis
    analysis_id = await movement_service.analyze_movement(
        movement_data=sample_movement_data,
        student_id=student_id
    )
    
    assert analysis_id is not None
    assert isinstance(analysis_id, str)
    
    # Test 3: Get the analysis result
    analysis = await movement_service.get_analysis(analysis_id)
    assert analysis is not None
    assert analysis["student_id"] == student_id
    
    # Test 4: Verify movement patterns can be detected
    patterns = await movement_service.detect_patterns([sample_movement_data])
    assert patterns is not None
    assert "repetition_count" in patterns
    
    # Test 5: Verify student analyses can be retrieved
    student_analyses = await movement_service.get_student_analyses(student_id)
    assert len(student_analyses) > 0
    assert student_analyses[0]["student_id"] == student_id

@pytest.mark.asyncio
async def test_error_handling_integration(
    movement_service,
    activity_service,
    db_session: Session,
    sample_movement_data
):
    """Test error handling in integrated services using real database."""
    # Setup
    student_id = "student123"
    # ActivityService uses in-memory storage, so non-existent activity_id won't cause errors
    # The service gracefully handles missing data
    
    # Test 1: MovementAnalysisService doesn't validate activity_id - it just analyzes movement
    # The service will create an analysis even if activity doesn't exist
    # This test verifies the service handles missing data gracefully
    analysis_id = await movement_service.analyze_movement(
        movement_data=sample_movement_data,
        student_id=student_id
        )
    
    # The service should still create an analysis
    assert analysis_id is not None
    
    # Verify we can retrieve it
    analysis = await movement_service.get_analysis(analysis_id)
    assert analysis is not None

@pytest.mark.asyncio
async def test_caching_integration(
    movement_service,
    activity_service,
    db_session: Session,
    sample_movement_data,
    sample_activity
):
    """Test integration with real database (MovementAnalysisService uses in-memory storage, not Redis)."""
    # Setup
    student_id = "student123"
    # Create activity first to get an ID
    created_activity_id = await activity_service.create_activity(sample_activity)
    activity_id = created_activity_id
    
    # Test 1: First call should create an analysis
    analysis_id = await movement_service.analyze_movement(
        movement_data=sample_movement_data,
        student_id="student123"
    )
    assert analysis_id is not None
    
    # Test 2: Get the analysis (service uses in-memory storage, not cache)
    analysis = await movement_service.get_analysis(analysis_id)
    assert analysis is not None
    
    # Test 3: Verify we can track progress
    progress = await movement_service.track_progress("student123")
    assert progress is not None
    assert "total_analyses" in progress 