import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.activity import Activity
from app.models.physical_education.activity_plan.models import ActivityPlan, ActivityPlanActivity
from app.services.physical_education.activity_manager import ActivityManager
from app.core.database import get_db

@pytest.fixture
def db_session():
    """Get a real database session."""
    return next(get_db())

@pytest.fixture
def activity_manager(db_session):
    return ActivityManager(db_session=db_session)

@pytest.mark.asyncio
async def test_create_activity_plan_success(activity_manager, db_session):
    # Setup
    student_id = 1
    class_id = 501  # Use valid class ID from database
    duration_minutes = 60
    focus_areas = ['strength', 'flexibility']
    
    # Test
    result = await activity_manager.create_activity_plan(
        student_id=student_id,
        class_id=class_id,
        duration_minutes=duration_minutes,
        focus_areas=focus_areas
    )
    
    # Verify
    assert 'plan_id' in result
    assert result['success'] is True

@pytest.mark.asyncio
async def test_create_activity_plan_invalid_duration(activity_manager):
    # Setup
    student_id = 1
    class_id = 501  # Use valid class ID from database
    duration_minutes = 0  # Invalid duration
    
    # Test
    result = await activity_manager.create_activity_plan(
        student_id=student_id,
        class_id=class_id,
        duration_minutes=duration_minutes
    )
    
    # Verify
    assert result['success'] is False
    assert 'Invalid duration' in result['message']

@pytest.mark.asyncio
async def test_track_plan_progress_success(activity_manager):
    # Setup
    plan_id = 1  # Use valid plan ID from database
    activity_id = 1
    is_completed = True
    notes = 'Completed successfully'
    
    # Test
    result = await activity_manager.track_plan_progress(
        plan_id=plan_id,
        activity_id=activity_id,
        is_completed=is_completed,
        notes=notes
    )
    
    # Verify
    assert result['success'] is True

@pytest.mark.asyncio
async def test_track_plan_progress_not_found(activity_manager):
    # Setup
    plan_id = 999  # Non-existent plan ID
    activity_id = 1
    
    # Test
    result = await activity_manager.track_plan_progress(
        plan_id=plan_id,
        activity_id=activity_id,
        is_completed=True
    )
    
    # Verify
    assert result['success'] is False
    assert 'Plan activity not found' in result['message']

@pytest.mark.asyncio
async def test_get_student_progress_report(activity_manager):
    # Setup
    student_id = 1
    start_date = datetime.now() - timedelta(days=30)
    end_date = datetime.now()
    
    # Test
    result = await activity_manager.get_student_progress_report(
        student_id=student_id,
        start_date=start_date,
        end_date=end_date
    )
    
    # Verify
    assert 'activities' in result
    assert 'progress_summary' in result
    assert 'recommendations' in result

@pytest.mark.asyncio
async def test_generate_activity_plan_with_focus_areas(activity_manager):
    # Setup
    student_id = 1
    class_id = 501  # Use valid class ID from database
    duration_minutes = 45
    focus_areas = ['strength', 'endurance']
    
    # Test
    result = await activity_manager.generate_activity_plan(
        student_id=student_id,
        class_id=class_id,
        duration_minutes=duration_minutes,
        focus_areas=focus_areas
    )
    
    # Verify
    assert 'plan_id' in result
    assert 'activities' in result
    assert 'duration' in result
    assert result['duration'] == duration_minutes

@pytest.mark.asyncio
async def test_generate_activity_plan_without_focus_areas(activity_manager):
    # Setup
    student_id = 1
    class_id = 501  # Use valid class ID from database
    duration_minutes = 30
    
    # Test
    result = await activity_manager.generate_activity_plan(
        student_id=student_id,
        class_id=class_id,
        duration_minutes=duration_minutes
    )
    
    # Verify
    assert 'plan_id' in result
    assert 'activities' in result
    assert 'duration' in result
    assert result['duration'] == duration_minutes 