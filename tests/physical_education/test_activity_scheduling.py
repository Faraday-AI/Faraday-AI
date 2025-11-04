import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import uuid
from app.models.activity import Activity
from app.models.physical_education.activity_plan.models import ActivityPlan, ActivityPlanActivity
from app.models.physical_education.class_.models import PhysicalEducationClass, ClassType
from app.models.physical_education.student.models import Student
from app.models.physical_education.pe_enums.pe_types import GradeLevel
from app.services.physical_education.activity_manager import ActivityManager
from app.core.database import get_db

# Import db_session from conftest - it will be available via pytest fixtures

@pytest.fixture
def activity_manager(db_session):
    return ActivityManager(db_session=db_session)

@pytest.fixture
def test_teacher(db_session):
    """Create a real Teacher record for foreign key constraints."""
    from sqlalchemy import text
    import uuid
    
    # First create a User
    from app.models.core.user import User
    unique_id = uuid.uuid4().hex[:8]
    user = User(
        email=f"test.user.{unique_id}@example.com",
        password_hash="hashed_password_placeholder",
        first_name="Test",
        last_name=f"Teacher{unique_id}",
        role="teacher"
    )
    db_session.add(user)
    db_session.flush()
    db_session.refresh(user)
    
    # Then create a Teacher record in teachers table
    # PRODUCTION-READY: Both constraints on physical_education_classes.teacher_id require the same value:
    # 1. fk_physical_education_classes_teacher_id -> teachers.id
    # 2. physical_education_classes_teacher_id_fkey -> users.id
    # To satisfy both, we need teachers.id = users.id (which matches seeded data pattern)
    result = db_session.execute(
        text("""
            INSERT INTO teachers (id, first_name, last_name, email, user_id, is_active)
            VALUES (:id, :first_name, :last_name, :email, :user_id, :is_active)
            RETURNING id
        """),
        {
            "id": user.id,  # Use same ID as user to satisfy both constraints
            "first_name": "Test",
            "last_name": f"Teacher{unique_id}",
            "email": f"test.teacher.{unique_id}@example.com",
            "user_id": user.id,
            "is_active": True
        }
    )
    teacher_id = result.scalar()
    db_session.flush()
    
    return {"id": teacher_id, "user_id": user.id}

@pytest.fixture
def test_student(db_session):
    """Create a real Student for foreign key constraints."""
    unique_id = uuid.uuid4().hex[:8]
    student = Student(
        first_name="Test",
        last_name=f"Student{unique_id}",
        email=f"test.student.{unique_id}@example.com",
        date_of_birth=datetime.now() - timedelta(days=365*15),  # 15 years old
        grade_level=GradeLevel.NINTH,
    )
    db_session.add(student)
    db_session.flush()  # Use flush for SAVEPOINT transactions
    db_session.refresh(student)
    return student

@pytest.fixture
def test_class(db_session, test_teacher):
    """Create a test PhysicalEducationClass for testing."""
    unique_id = str(uuid.uuid4())[:8]
    test_class = PhysicalEducationClass(
        name=f"Test Class {unique_id}",
        class_type=ClassType.REGULAR,
        teacher_id=test_teacher["id"],  # Both constraints require same value: fk_physical_education_classes_teacher_id->teachers.id AND physical_education_classes_teacher_id_fkey->users.id. Since teachers.id=users.id in fixture, use test_teacher["id"]
        start_date=datetime.utcnow(),
        end_date=datetime.utcnow() + timedelta(days=90),  # Required field
        grade_level=GradeLevel.NINTH,  # Required field
        max_students=30
    )
    db_session.add(test_class)
    db_session.flush()  # Use flush for SAVEPOINT transactions
    db_session.refresh(test_class)
    return test_class

@pytest.mark.asyncio
async def test_create_activity_plan_success(activity_manager, db_session, test_class, test_student):
    # Setup - use the test_class and test_student we created
    student_id = test_student.id  # Use real student ID
    class_id = test_class.id
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
async def test_create_activity_plan_invalid_duration(activity_manager, db_session, test_class, test_student):
    # Setup
    student_id = test_student.id  # Use real student ID
    class_id = test_class.id
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
async def test_track_plan_progress_success(activity_manager, db_session, test_class, test_student):
    # Setup - first create a real activity plan
    student_id = test_student.id
    class_id = test_class.id
    duration_minutes = 60
    focus_areas = ['strength', 'flexibility']
    
    # Create an activity plan first
    plan_result = await activity_manager.create_activity_plan(
        student_id=student_id,
        class_id=class_id,
        duration_minutes=duration_minutes,
        focus_areas=focus_areas
    )
    
    # Get the plan_id from the result
    plan_id = plan_result.get('plan_id')
    assert plan_id is not None, "Failed to create activity plan"
    
    # Get the first activity_id from the plan (if available)
    # If the plan creation doesn't return activity IDs, we need to query the database
    from app.models.physical_education.activity_plan.models import ActivityPlanActivity
    plan_activity = db_session.query(ActivityPlanActivity).filter(
        ActivityPlanActivity.plan_id == plan_id
    ).first()
    
    if not plan_activity:
        pytest.skip("Activity plan created but no activities found - may need to create activities first")
    
    activity_id = plan_activity.activity_id
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
async def test_get_student_progress_report(activity_manager, test_student):
    # Setup
    student_id = test_student.id  # Use real student ID
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
async def test_generate_activity_plan_with_focus_areas(activity_manager, db_session, test_class, test_student):
    # Setup
    student_id = test_student.id  # Use real student ID
    class_id = test_class.id
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
async def test_generate_activity_plan_without_focus_areas(activity_manager, db_session, test_class, test_student):
    # Setup
    student_id = test_student.id  # Use real student ID
    class_id = test_class.id
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