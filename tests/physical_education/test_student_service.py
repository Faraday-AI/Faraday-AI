import pytest
import pytest_asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from app.services.physical_education.student_service import StudentService
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session

@pytest_asyncio.fixture
async def db_session():
    """Create a mock database session."""
    return AsyncMock(spec=Session)

@pytest_asyncio.fixture
async def student_service(db_session):
    """Create StudentService instance for testing."""
    service = StudentService(db_session)
    return service

@pytest.fixture
def sample_student_data():
    """Create sample student data for testing."""
    return {
        'student_id': '12345',
        'first_name': 'Test',
        'last_name': 'Student',
        'grade_level': '10th',
        'date_of_birth': datetime(2009, 1, 1).isoformat(),
        'medical_conditions': [],
        'emergency_contact': {
            'name': 'Parent',
            'relationship': 'parent',
            'phone': '123-456-7890'
        },
        'skill_level': 'beginner',
        'attendance_rate': 1.0,
        'current_classes': [],
        'progress_history': [],
        'assessments': [],
        'created_at': datetime.now().isoformat(),
        'last_updated': datetime.now().isoformat()
    }

@pytest.mark.asyncio
async def test_register_student(student_service, sample_student_data):
    """Test student registration."""
    with patch.object(student_service.student_manager, 'create_student_profile', new_callable=AsyncMock) as mock_create:
        mock_create.return_value = sample_student_data
        result = await student_service.create_student(
            first_name='Test',
            last_name='Student',
            email='12345',  # Using this as student_id
            date_of_birth='2009-01-01',
            gender='male',
            grade_level='10th',
            medical_conditions=[],
            allergies=[],
            emergency_contact={
                'name': 'Parent',
                'relationship': 'parent',
                'phone': '123-456-7890'
            }
        )
        assert result == sample_student_data
        mock_create.assert_called_once_with(
            student_id='12345',
            first_name='Test',
            last_name='Student',
            grade_level='10th',
            date_of_birth=datetime(2009, 1, 1),
            medical_conditions=[],
            emergency_contact={
                'name': 'Parent',
                'relationship': 'parent',
                'phone': '123-456-7890'
            }
        )

@pytest.mark.asyncio
async def test_get_student_profile(student_service, sample_student_data):
    """Test retrieving student profile."""
    with patch.object(student_service.student_manager, 'students', {}) as mock_students:
        mock_students['12345'] = sample_student_data
        result = await student_service.get_student('12345')
        assert result == sample_student_data

@pytest.mark.asyncio
async def test_update_student_profile(student_service, sample_student_data):
    """Test updating student profile."""
    with patch.object(student_service.student_manager, 'students', {}) as mock_students:
        mock_students['12345'] = sample_student_data.copy()
        result = await student_service.update_student('12345', skill_level='advanced')
        assert result['skill_level'] == 'advanced'
        assert 'last_updated' in result

@pytest.mark.asyncio
async def test_get_student_progress(student_service):
    """Test retrieving student progress."""
    with patch.object(student_service.student_manager, 'generate_progress_report', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = {
            'fitness_score': 85,
            'attendance_rate': 0.95,
            'improvement_rate': 0.15
        }
        result = await student_service.get_student_progress('12345')
        assert 'fitness_score' in result
        assert 'attendance_rate' in result
        assert 'improvement_rate' in result
        mock_get.assert_called_once()

@pytest.mark.asyncio
async def test_get_student_activities(student_service):
    """Test retrieving student activities."""
    with patch.object(student_service.student_manager, 'progress_records', {}) as mock_records:
        mock_records['12345'] = {
            'activities': [
                {'activity_id': '1', 'name': 'Basketball', 'date': '2024-03-15'},
                {'activity_id': '2', 'name': 'Swimming', 'date': '2024-03-16'}
            ]
        }
        result = await student_service.get_student_activities('12345')
        assert len(result) == 2
        assert result[0]['name'] == 'Basketball'

@pytest.mark.asyncio
async def test_get_student_assessments(student_service):
    """Test retrieving student assessments."""
    with patch.object(student_service.student_manager, 'students', {}) as mock_students:
        mock_students['12345'] = {
            'assessments': [
                {'assessment_id': '1', 'type': 'fitness', 'date': '2024-03-15'},
                {'assessment_id': '2', 'type': 'skill', 'date': '2024-03-16'}
            ]
        }
        result = await student_service.get_student_assessments('12345')
        assert len(result) == 2
        assert result[0]['type'] == 'fitness'

@pytest.mark.asyncio
async def test_get_student_incidents(student_service):
    """Test retrieving student safety incidents."""
    with patch.object(student_service.student_manager, 'students', {}) as mock_students:
        mock_students['12345'] = {
            'incidents': [
                {'incident_id': '1', 'description': 'Minor injury', 'date': '2024-03-15'},
                {'incident_id': '2', 'description': 'Equipment issue', 'date': '2024-03-16'}
            ]
        }
        result = await student_service.get_student_incidents('12345')
        assert len(result) == 2
        assert result[0]['description'] == 'Minor injury'

@pytest.mark.asyncio
async def test_get_students_by_class(student_service):
    """Test retrieving students by class."""
    with patch.object(student_service.student_manager, 'classes', {}) as mock_classes:
        mock_classes['class1'] = {
            'students': [
                {'student_id': '1', 'name': 'Student 1'},
                {'student_id': '2', 'name': 'Student 2'}
            ]
        }
        result = await student_service.get_students_by_class('class1')
        assert len(result) == 2
        assert result[0]['name'] == 'Student 1'

@pytest.mark.asyncio
async def test_delete_student(student_service):
    """Test deleting a student."""
    with patch.object(student_service.student_manager, 'students', {}) as mock_students:
        mock_students['12345'] = {'student_id': '12345'}
        result = await student_service.delete_student('12345')
        assert result is True
        assert '12345' not in mock_students 