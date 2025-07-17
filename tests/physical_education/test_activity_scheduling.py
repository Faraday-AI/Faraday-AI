import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.activity import Activity
from app.services.physical_education.models.activity_plan import ActivityPlan, ActivityPlanActivity
from app.services.physical_education.activity_manager import ActivityManager

@pytest.fixture
def mock_db():
    return MagicMock()

@pytest.fixture
def activity_manager(mock_db):
    return ActivityManager(db=mock_db)

@pytest.mark.asyncio
async def test_create_activity_plan_success(activity_manager, mock_db):
    # Setup
    student_id = 'student1'
    class_id = 'class1'
    duration_minutes = 60
    focus_areas = ['strength', 'flexibility']
    
    mock_plan = MagicMock(spec=ActivityPlan)
    mock_plan.id = 'plan1'
    mock_db.add.return_value = None
    mock_db.commit.return_value = None
    mock_db.refresh.return_value = None
    
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
    mock_db.add.assert_called()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()

@pytest.mark.asyncio
async def test_create_activity_plan_invalid_duration(activity_manager, mock_db):
    # Setup
    student_id = 'student1'
    class_id = 'class1'
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
async def test_track_plan_progress_success(activity_manager, mock_db):
    # Setup
    plan_id = 'plan1'
    activity_id = 'activity1'
    is_completed = True
    notes = 'Completed successfully'
    
    mock_plan_activity = MagicMock(spec=ActivityPlanActivity)
    mock_db.query.return_value.filter.return_value.first.return_value = mock_plan_activity
    
    # Test
    result = await activity_manager.track_plan_progress(
        plan_id=plan_id,
        activity_id=activity_id,
        is_completed=is_completed,
        notes=notes
    )
    
    # Verify
    assert result['success'] is True
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()

@pytest.mark.asyncio
async def test_track_plan_progress_not_found(activity_manager, mock_db):
    # Setup
    plan_id = 'nonexistent'
    activity_id = 'activity1'
    mock_db.query.return_value.filter.return_value.first.return_value = None
    
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
async def test_get_student_progress_report(activity_manager, mock_db):
    # Setup
    student_id = 'student1'
    start_date = datetime.now() - timedelta(days=30)
    end_date = datetime.now()
    
    mock_activities = [
        MagicMock(spec=Activity, id=f'activity{i}', name=f'Activity {i}')
        for i in range(3)
    ]
    mock_db.query.return_value.filter.return_value.all.return_value = mock_activities
    
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
    assert len(result['activities']) == 3

@pytest.mark.asyncio
async def test_generate_activity_plan_with_focus_areas(activity_manager, mock_db):
    # Setup
    student_id = 'student1'
    class_id = 'class1'
    duration_minutes = 45
    focus_areas = ['strength', 'endurance']
    
    mock_activities = [
        MagicMock(spec=Activity, id=f'activity{i}', name=f'Activity {i}')
        for i in range(4)
    ]
    mock_db.query.return_value.filter.return_value.all.return_value = mock_activities
    
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
    assert len(result['activities']) > 0

@pytest.mark.asyncio
async def test_generate_activity_plan_without_focus_areas(activity_manager, mock_db):
    # Setup
    student_id = 'student1'
    class_id = 'class1'
    duration_minutes = 30
    
    mock_activities = [
        MagicMock(spec=Activity, id=f'activity{i}', name=f'Activity {i}')
        for i in range(3)
    ]
    mock_db.query.return_value.filter.return_value.all.return_value = mock_activities
    
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
    assert len(result['activities']) > 0 