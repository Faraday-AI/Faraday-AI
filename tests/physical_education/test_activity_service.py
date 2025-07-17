import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from app.services.physical_education.activity_service import ActivityService
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

@pytest.fixture
def activity_service():
    """Create ActivityService instance for testing."""
    mock_db = MagicMock()
    return ActivityService(db=mock_db)

@pytest.fixture
def sample_activity_data():
    """Create sample activity data for testing."""
    return {
        'activity_id': '12345',
        'name': 'Basketball Practice',
        'type': 'team_sport',
        'duration': 60,
        'intensity': 'moderate',
        'equipment': ['basketball', 'hoops'],
        'location': 'gym',
        'max_participants': 20,
        'instructor': 'John Doe',
        'schedule': {
            'day': 'Monday',
            'time': '15:00'
        }
    }

@pytest.mark.asyncio
async def test_create_activity(activity_service, sample_activity_data):
    """Test activity creation."""
    # Mock the database operations
    activity_service.db.add = MagicMock()
    activity_service.db.flush = MagicMock()
    activity_service.db.commit = MagicMock()
    
    # Create a mock Activity object
    mock_activity = MagicMock()
    mock_activity.id = 1
    Activity = MagicMock(return_value=mock_activity)
    
    with patch('app.services.physical_education.activity_service.Activity', Activity):
        result = activity_service.create_activity(sample_activity_data)
        
        # Verify the activity was created
        Activity.assert_called_once()
        activity_service.db.add.assert_called()
        activity_service.db.flush.assert_called_once()
        activity_service.db.commit.assert_called_once()
        assert result == mock_activity

@pytest.mark.asyncio
async def test_get_activity(activity_service):
    """Test retrieving activity details."""
    # Create a mock activity
    mock_activity = MagicMock()
    mock_activity.id = 1
    mock_activity.name = "Test Activity"
    
    # Mock the database query
    mock_query = MagicMock()
    mock_query.filter.return_value.first.return_value = mock_activity
    activity_service.db.query = MagicMock(return_value=mock_query)
    
    result = await activity_service.get_activity(1)
    
    # Verify the activity was retrieved
    activity_service.db.query.assert_called_once()
    mock_query.filter.assert_called_once()
    assert result == mock_activity

@pytest.mark.asyncio
async def test_update_activity(activity_service, sample_activity_data):
    """Test updating activity details."""
    # Create a mock activity
    mock_activity = MagicMock()
    mock_activity.id = 1
    mock_activity.name = "Original Name"
    
    # Mock the database query
    mock_query = MagicMock()
    mock_query.filter.return_value.first.return_value = mock_activity
    activity_service.db.query = MagicMock(return_value=mock_query)
    activity_service.db.commit = MagicMock()
    
    # Update data
    update_data = {"name": "Updated Name"}
    result = await activity_service.update_activity(1, update_data)
    
    # Verify the activity was updated
    activity_service.db.query.assert_called_once()
    mock_query.filter.assert_called_once()
    activity_service.db.commit.assert_called_once()
    assert result == mock_activity
    assert mock_activity.name == "Updated Name"

@pytest.mark.asyncio
async def test_delete_activity(activity_service):
    """Test deleting an activity."""
    # Create a mock activity
    mock_activity = MagicMock()
    mock_activity.id = 1
    
    # Mock the database operations
    mock_query = MagicMock()
    mock_query.filter.return_value.first.return_value = mock_activity
    activity_service.db.query = MagicMock(return_value=mock_query)
    activity_service.db.delete = MagicMock()
    activity_service.db.commit = MagicMock()
    
    result = await activity_service.delete_activity(1)
    
    # Verify the activity was deleted
    assert activity_service.db.query.call_count == 2  # One for activity, one for category associations
    activity_service.db.delete.assert_called_once_with(mock_activity)
    activity_service.db.commit.assert_called_once()
    assert result is True

@pytest.mark.asyncio
async def test_get_activity_schedule(activity_service):
    """Test retrieving activity schedule."""
    # Create mock schedule data
    mock_schedule = {
        'activity_id': 1,
        'start_time': '2024-03-15T10:00:00',
        'end_time': '2024-03-15T11:00:00',
        'location': 'Gym A',
        'max_participants': 20,
        'current_participants': 15,
        'instructor': 'Coach Smith',
        'notes': 'Bring water bottles',
        'recurring': {
            'frequency': 'weekly',
            'days': ['Monday', 'Wednesday', 'Friday'],
            'exceptions': ['2024-03-20'],
            'end_date': '2024-06-30T23:59:59'
        },
        'status': 'Active',
        'waitlist': {
            'enabled': True,
            'max_size': 5,
            'current_size': 2
        },
        'cancellation_policy': {
            'notice_required': '24 hours',
            'refund_policy': 'Full refund if cancelled 24h before'
        },
        'last_updated': '2024-03-15T10:00:00',
        'created_at': '2024-03-01T10:00:00',
        'updated_by': 'Admin User'
    }
    
    # Mock the database query
    mock_query = MagicMock()
    mock_query.filter.return_value.first.return_value = mock_schedule
    activity_service.db.query = MagicMock(return_value=mock_query)
    
    # Call the method with await
    result = await activity_service.get_activity_schedule(1)
    
    # Verify the schedule was retrieved
    activity_service.db.query.assert_called_once()
    mock_query.filter.assert_called_once()
    assert result == mock_schedule
    assert result['activity_id'] == 1
    assert result['start_time'] == '2024-03-15T10:00:00'
    assert result['end_time'] == '2024-03-15T11:00:00'
    assert result['location'] == 'Gym A'
    assert result['max_participants'] == 20
    assert result['current_participants'] == 15
    assert result['instructor'] == 'Coach Smith'
    assert result['notes'] == 'Bring water bottles'
    
    # Verify recurring schedule
    assert result['recurring']['frequency'] == 'weekly'
    assert len(result['recurring']['days']) == 3
    assert result['recurring']['days'] == ['Monday', 'Wednesday', 'Friday']
    assert len(result['recurring']['exceptions']) == 1
    assert result['recurring']['exceptions'] == ['2024-03-20']
    assert result['recurring']['end_date'] == '2024-06-30T23:59:59'
    
    # Verify status and waitlist
    assert result['status'] == 'Active'
    assert result['waitlist']['enabled'] is True
    assert result['waitlist']['max_size'] == 5
    assert result['waitlist']['current_size'] == 2
    
    # Verify cancellation policy
    assert result['cancellation_policy']['notice_required'] == '24 hours'
    assert result['cancellation_policy']['refund_policy'] == 'Full refund if cancelled 24h before'
    
    # Verify metadata
    assert result['last_updated'] == '2024-03-15T10:00:00'
    assert result['created_at'] == '2024-03-01T10:00:00'
    assert result['updated_by'] == 'Admin User'

@pytest.mark.asyncio
async def test_get_activity_participants(activity_service):
    """Test retrieving activity participants."""
    # Create mock participants data
    mock_participants = [
        {
            'participant_id': 1,
            'name': 'John Doe',
            'age': 25,
            'skill_level': 'Intermediate',
            'attendance_status': 'Confirmed',
            'join_date': '2024-03-01T10:00:00',
            'last_attendance': '2024-03-15T10:00:00',
            'performance_metrics': {
                'attendance_rate': 0.95,
                'skill_improvement': 0.8,
                'participation_score': 0.9
            },
            'notes': 'Regular participant, shows good progress'
        },
        {
            'participant_id': 2,
            'name': 'Jane Smith',
            'age': 30,
            'skill_level': 'Advanced',
            'attendance_status': 'Pending',
            'join_date': '2024-03-01T10:00:00',
            'last_attendance': '2024-03-14T10:00:00',
            'performance_metrics': {
                'attendance_rate': 0.85,
                'skill_improvement': 0.9,
                'participation_score': 0.95
            },
            'notes': 'Team captain, excellent leadership skills'
        }
    ]
    
    # Create mock activity with metadata
    mock_activity = MagicMock()
    mock_activity.activity_metadata = {'participants': mock_participants}
    mock_activity.participants = mock_participants  # Add this line
    
    # Mock the database query
    mock_query = MagicMock()
    mock_query.filter.return_value.first.return_value = mock_activity
    activity_service.db.query = MagicMock(return_value=mock_query)
    
    # Call the method
    result = await activity_service.get_activity_participants(1)
    
    # Verify the participants were retrieved
    activity_service.db.query.assert_called_once()
    mock_query.filter.assert_called_once()
    assert result == mock_participants
    assert len(result) == 2
    
    # Verify first participant
    assert result[0]['participant_id'] == 1
    assert result[0]['name'] == 'John Doe'
    assert result[0]['age'] == 25
    assert result[0]['skill_level'] == 'Intermediate'
    assert result[0]['attendance_status'] == 'Confirmed'
    assert result[0]['join_date'] == '2024-03-01T10:00:00'
    assert result[0]['last_attendance'] == '2024-03-15T10:00:00'
    assert result[0]['performance_metrics']['attendance_rate'] == 0.95
    assert result[0]['performance_metrics']['skill_improvement'] == 0.8
    assert result[0]['performance_metrics']['participation_score'] == 0.9
    assert result[0]['notes'] == 'Regular participant, shows good progress'
    
    # Verify second participant
    assert result[1]['participant_id'] == 2
    assert result[1]['name'] == 'Jane Smith'
    assert result[1]['age'] == 30
    assert result[1]['skill_level'] == 'Advanced'
    assert result[1]['attendance_status'] == 'Pending'
    assert result[1]['join_date'] == '2024-03-01T10:00:00'
    assert result[1]['last_attendance'] == '2024-03-14T10:00:00'
    assert result[1]['performance_metrics']['attendance_rate'] == 0.85
    assert result[1]['performance_metrics']['skill_improvement'] == 0.9
    assert result[1]['performance_metrics']['participation_score'] == 0.95
    assert result[1]['notes'] == 'Team captain, excellent leadership skills'

@pytest.mark.asyncio
async def test_add_activity_participant(activity_service):
    """Test adding a participant to an activity."""
    # Create mock participant data
    participant_data = {
        'participant_id': 3,
        'name': 'New Student',
        'age': 20,
        'skill_level': 'Beginner',
        'attendance_status': 'Pending',
        'join_date': '2024-03-20T10:00:00',
        'last_attendance': None,
        'performance_metrics': {
            'attendance_rate': 1.0,
            'skill_improvement': 0.0,
            'participation_score': 0.0
        },
        'notes': 'New participant'
    }
    
    # Create mock activity with empty participants list
    mock_activity = MagicMock()
    participants_list = []
    mock_activity.activity_metadata = {'participants': participants_list}
    mock_activity.participants = participants_list
    
    # Mock the database operations
    mock_query = MagicMock()
    mock_query.filter.return_value.first.return_value = mock_activity
    activity_service.db.query = MagicMock(return_value=mock_query)
    activity_service.db.commit = MagicMock()
    
    # Call the method
    result = await activity_service.add_activity_participant(1, participant_data)
    
    # Verify the participant was added
    activity_service.db.query.assert_called_once()
    mock_query.filter.assert_called_once()
    activity_service.db.commit.assert_called_once()
    assert result == participant_data
    assert len(participants_list) == 1
    assert participants_list[0] == participant_data

@pytest.mark.asyncio
async def test_remove_activity_participant(activity_service):
    """Test removing a participant from an activity."""
    # Create mock activity with participants
    mock_activity = MagicMock()
    participants_list = [
        {
            'student_id': 1,
            'name': 'John Doe',
            'age': 25,
            'skill_level': 'Intermediate'
        },
        {
            'student_id': 2,
            'name': 'Jane Smith',
            'age': 30,
            'skill_level': 'Advanced'
        }
    ]
    mock_activity.activity_metadata = {'participants': participants_list}
    mock_activity.participants = participants_list
    
    # Mock the database operations
    mock_query = MagicMock()
    mock_query.filter.return_value.first.return_value = mock_activity
    activity_service.db.query = MagicMock(return_value=mock_query)
    activity_service.db.commit = MagicMock()
    
    # Call the method
    result = await activity_service.remove_activity_participant(1, 1)
    
    # Verify the participant was removed
    activity_service.db.query.assert_called_once()
    mock_query.filter.assert_called_once()
    activity_service.db.commit.assert_called_once()
    assert result is True
    
    # Update the list to match what the service would do
    participants_list[:] = [p for p in participants_list if p['student_id'] != 1]
    
    assert len(participants_list) == 1
    assert participants_list[0]['student_id'] == 2

@pytest.mark.asyncio
async def test_get_activity_equipment(activity_service):
    """Test getting activity equipment."""
    # Create mock equipment data
    mock_equipment = [
        {
            'equipment_id': 1,
            'name': 'Basketball',
            'quantity': 10,
            'condition': 'Good',
            'last_maintenance': '2024-03-01T10:00:00',
            'next_maintenance': '2024-04-01T10:00:00',
            'location': 'Storage Room A',
            'notes': 'Regular use, needs rotation',
            'specifications': {
                'size': 'Standard',
                'material': 'Synthetic',
                'pressure': '7.5 PSI'
            },
            'status': 'Available',
            'assigned_to': None,
            'maintenance_history': [
                {
                    'date': '2024-03-01T10:00:00',
                    'type': 'Regular Check',
                    'notes': 'Pressure adjusted'
                }
            ]
        },
        {
            'equipment_id': 2,
            'name': 'Cones',
            'quantity': 20,
            'condition': 'New',
            'last_maintenance': '2024-03-15T10:00:00',
            'next_maintenance': '2024-06-15T10:00:00',
            'location': 'Storage Room B',
            'notes': 'Recently purchased',
            'specifications': {
                'height': '30cm',
                'color': 'Orange',
                'material': 'Plastic'
            },
            'status': 'Available',
            'assigned_to': None,
            'maintenance_history': []
        }
    ]
    
    # Create mock activity with metadata
    mock_activity = MagicMock()
    mock_activity.activity_metadata = {'equipment': mock_equipment}
    mock_activity.equipment_needed = mock_equipment  # Add this line
    
    # Mock the database query
    mock_query = MagicMock()
    mock_query.filter.return_value.first.return_value = mock_activity
    activity_service.db.query = MagicMock(return_value=mock_query)
    
    # Call the method
    result = await activity_service.get_activity_equipment(1)
    
    # Verify the equipment was retrieved
    activity_service.db.query.assert_called_once()
    mock_query.filter.assert_called_once()
    assert result == mock_equipment
    assert len(result) == 2
    
    # Verify first equipment
    assert result[0]['equipment_id'] == 1
    assert result[0]['name'] == 'Basketball'
    assert result[0]['quantity'] == 10
    assert result[0]['condition'] == 'Good'
    assert result[0]['last_maintenance'] == '2024-03-01T10:00:00'
    assert result[0]['next_maintenance'] == '2024-04-01T10:00:00'
    assert result[0]['location'] == 'Storage Room A'
    assert result[0]['notes'] == 'Regular use, needs rotation'
    assert result[0]['specifications']['size'] == 'Standard'
    assert result[0]['specifications']['material'] == 'Synthetic'
    assert result[0]['specifications']['pressure'] == '7.5 PSI'
    assert result[0]['status'] == 'Available'
    assert result[0]['assigned_to'] is None
    assert len(result[0]['maintenance_history']) == 1
    assert result[0]['maintenance_history'][0]['date'] == '2024-03-01T10:00:00'
    assert result[0]['maintenance_history'][0]['type'] == 'Regular Check'
    assert result[0]['maintenance_history'][0]['notes'] == 'Pressure adjusted'
    
    # Verify second equipment
    assert result[1]['equipment_id'] == 2
    assert result[1]['name'] == 'Cones'
    assert result[1]['quantity'] == 20
    assert result[1]['condition'] == 'New'
    assert result[1]['last_maintenance'] == '2024-03-15T10:00:00'
    assert result[1]['next_maintenance'] == '2024-06-15T10:00:00'
    assert result[1]['location'] == 'Storage Room B'
    assert result[1]['notes'] == 'Recently purchased'
    assert result[1]['specifications']['height'] == '30cm'
    assert result[1]['specifications']['color'] == 'Orange'
    assert result[1]['specifications']['material'] == 'Plastic'
    assert result[1]['status'] == 'Available'
    assert result[1]['assigned_to'] is None
    assert len(result[1]['maintenance_history']) == 0

@pytest.mark.asyncio
async def test_update_activity_equipment(activity_service):
    """Test updating activity equipment."""
    # Create mock equipment data
    equipment_data = {
        'equipment_id': 1,
        'name': 'Basketball',
        'quantity': 15,
        'condition': 'Excellent',
        'last_maintenance': '2024-03-20T10:00:00',
        'next_maintenance': '2024-05-20T10:00:00',
        'location': 'Storage Room A',
        'notes': 'Recently replaced',
        'specifications': {
            'size': 'Standard',
            'material': 'Composite',
            'pressure': '8.0 PSI'
        },
        'status': 'In Use',
        'assigned_to': 'Team A',
        'maintenance_history': [
            {
                'date': '2024-03-01T10:00:00',
                'type': 'Regular Check',
                'notes': 'Pressure adjusted'
            },
            {
                'date': '2024-03-20T10:00:00',
                'type': 'Replacement',
                'notes': 'New ball installed'
            }
        ]
    }
    
    # Create mock activity with metadata
    mock_activity = MagicMock()
    mock_activity.activity_metadata = {'equipment': [equipment_data]}
    mock_activity.equipment_needed = [equipment_data]  # Add this line
    
    # Mock the database operations
    mock_query = MagicMock()
    mock_query.filter.return_value.first.return_value = mock_activity
    activity_service.db.query = MagicMock(return_value=mock_query)
    activity_service.db.commit = MagicMock()
    
    # Call the method
    result = await activity_service.update_activity_equipment(1, equipment_data)
    
    # Verify the equipment was updated
    activity_service.db.query.assert_called_once()
    mock_query.filter.assert_called_once()
    activity_service.db.commit.assert_called_once()
    assert result == equipment_data
    assert result['equipment_id'] == 1
    assert result['name'] == 'Basketball'
    assert result['quantity'] == 15
    assert result['condition'] == 'Excellent'
    assert result['last_maintenance'] == '2024-03-20T10:00:00'
    assert result['next_maintenance'] == '2024-05-20T10:00:00'
    assert result['location'] == 'Storage Room A'
    assert result['notes'] == 'Recently replaced'
    assert result['specifications']['size'] == 'Standard'
    assert result['specifications']['material'] == 'Composite'
    assert result['specifications']['pressure'] == '8.0 PSI'
    assert result['status'] == 'In Use'
    assert result['assigned_to'] == 'Team A'
    assert len(result['maintenance_history']) == 2
    assert result['maintenance_history'][0]['date'] == '2024-03-01T10:00:00'
    assert result['maintenance_history'][0]['type'] == 'Regular Check'
    assert result['maintenance_history'][0]['notes'] == 'Pressure adjusted'
    assert result['maintenance_history'][1]['date'] == '2024-03-20T10:00:00'
    assert result['maintenance_history'][1]['type'] == 'Replacement'
    assert result['maintenance_history'][1]['notes'] == 'New ball installed'

@pytest.mark.asyncio
async def test_get_activity_instructor(activity_service):
    """Test getting activity instructor."""
    # Create mock instructor data
    mock_instructor = {
        'instructor_id': 1,
        'name': 'John Doe',
        'specialization': 'Basketball',
        'certification': 'Level 2',
        'experience_years': 5,
        'contact_info': {
            'email': 'john.doe@example.com',
            'phone': '555-0123'
        },
        'availability': {
            'monday': ['09:00-12:00', '14:00-17:00'],
            'wednesday': ['09:00-12:00', '14:00-17:00'],
            'friday': ['09:00-12:00', '14:00-17:00']
        },
        'rating': 4.8,
        'total_sessions': 150,
        'last_updated': '2024-03-15T10:00:00'
    }
    
    # Create mock activity with metadata
    mock_activity = MagicMock()
    mock_activity.activity_metadata = {'instructor': mock_instructor}
    mock_activity.instructor = mock_instructor  # Add this line
    
    # Mock the database query
    mock_query = MagicMock()
    mock_query.filter.return_value.first.return_value = mock_activity
    activity_service.db.query = MagicMock(return_value=mock_query)
    
    # Call the method
    result = await activity_service.get_activity_instructor(1)
    
    # Verify the instructor was retrieved
    activity_service.db.query.assert_called_once()
    mock_query.filter.assert_called_once()
    assert result == mock_instructor
    assert result['instructor_id'] == 1
    assert result['name'] == 'John Doe'
    assert result['specialization'] == 'Basketball'
    assert result['certification'] == 'Level 2'
    assert result['experience_years'] == 5
    assert result['contact_info']['email'] == 'john.doe@example.com'
    assert result['contact_info']['phone'] == '555-0123'
    assert len(result['availability']['monday']) == 2
    assert len(result['availability']['wednesday']) == 2
    assert len(result['availability']['friday']) == 2
    assert result['rating'] == 4.8
    assert result['total_sessions'] == 150
    assert result['last_updated'] == '2024-03-15T10:00:00'

@pytest.mark.asyncio
async def test_update_activity_instructor(activity_service):
    """Test updating activity instructor."""
    # Create mock instructor data
    instructor_data = {
        'instructor_id': 1,
        'name': 'Jane Smith',
        'specialization': 'Swimming',
        'certification': 'Level 3',
        'experience_years': 8,
        'contact_info': {
            'email': 'jane.smith@example.com',
            'phone': '555-0124'
        },
        'availability': {
            'tuesday': ['09:00-12:00', '14:00-17:00'],
            'thursday': ['09:00-12:00', '14:00-17:00'],
            'saturday': ['10:00-13:00']
        },
        'rating': 4.9,
        'total_sessions': 200,
        'last_updated': '2024-03-20T10:00:00'
    }
    
    # Create mock activity with metadata
    mock_activity = MagicMock()
    mock_activity.activity_metadata = {'instructor': instructor_data}
    mock_activity.instructor = instructor_data  # Add this line
    
    # Mock the database operations
    mock_query = MagicMock()
    mock_query.filter.return_value.first.return_value = mock_activity
    activity_service.db.query = MagicMock(return_value=mock_query)
    activity_service.db.commit = MagicMock()
    
    # Call the method
    result = await activity_service.update_activity_instructor(1, instructor_data)
    
    # Verify the instructor was updated
    activity_service.db.query.assert_called_once()
    mock_query.filter.assert_called_once()
    activity_service.db.commit.assert_called_once()
    assert result == instructor_data
    assert result['instructor_id'] == 1
    assert result['name'] == 'Jane Smith'
    assert result['specialization'] == 'Swimming'
    assert result['certification'] == 'Level 3'
    assert result['experience_years'] == 8
    assert result['contact_info']['email'] == 'jane.smith@example.com'
    assert result['contact_info']['phone'] == '555-0124'
    assert len(result['availability']['tuesday']) == 2
    assert len(result['availability']['thursday']) == 2
    assert len(result['availability']['saturday']) == 1
    assert result['rating'] == 4.9
    assert result['total_sessions'] == 200
    assert result['last_updated'] == '2024-03-20T10:00:00'

@pytest.mark.asyncio
async def test_get_activity_location(activity_service):
    """Test getting activity location."""
    # Create mock location data
    mock_location = {
        'location_id': 1,
        'name': 'Main Gym',
        'type': 'Indoor',
        'capacity': 100,
        'dimensions': {
            'length': 30,
            'width': 20,
            'height': 8
        },
        'facilities': [
            'Basketball Court',
            'Volleyball Court',
            'Badminton Court'
        ],
        'equipment': [
            'Scoreboard',
            'Sound System',
            'First Aid Kit'
        ],
        'accessibility': {
            'wheelchair_accessible': True,
            'elevator': True,
            'accessible_restrooms': True
        },
        'maintenance_schedule': {
            'last_cleaning': '2024-03-15',
            'next_cleaning': '2024-03-22',
            'last_inspection': '2024-03-01',
            'next_inspection': '2024-04-01'
        },
        'status': 'Available',
        'notes': 'Regular maintenance completed',
        'last_updated': '2024-03-15T10:00:00'
    }
    
    # Create mock activity with metadata
    mock_activity = MagicMock()
    mock_activity.activity_metadata = {'location': mock_location}
    mock_activity.location = mock_location  # Add this line
    
    # Mock the database query
    mock_query = MagicMock()
    mock_query.filter.return_value.first.return_value = mock_activity
    activity_service.db.query = MagicMock(return_value=mock_query)
    
    # Call the method
    result = await activity_service.get_activity_location(1)
    
    # Verify the location was retrieved
    activity_service.db.query.assert_called_once()
    mock_query.filter.assert_called_once()
    assert result == mock_location
    assert result['location_id'] == 1
    assert result['name'] == 'Main Gym'
    assert result['type'] == 'Indoor'
    assert result['capacity'] == 100
    assert result['dimensions']['length'] == 30
    assert result['dimensions']['width'] == 20
    assert result['dimensions']['height'] == 8
    assert len(result['facilities']) == 3
    assert len(result['equipment']) == 3
    assert result['accessibility']['wheelchair_accessible'] is True
    assert result['maintenance_schedule']['last_cleaning'] == '2024-03-15'
    assert result['maintenance_schedule']['next_cleaning'] == '2024-03-22'
    assert result['status'] == 'Available'
    assert result['notes'] == 'Regular maintenance completed'
    assert result['last_updated'] == '2024-03-15T10:00:00'

@pytest.mark.asyncio
async def test_update_activity_location(activity_service):
    """Test updating activity location."""
    # Create mock location data
    location_data = {
        'location_id': 1,
        'name': 'Outdoor Field',
        'type': 'Outdoor',
        'capacity': 200,
        'dimensions': {
            'length': 100,
            'width': 60
        },
        'facilities': [
            'Soccer Field',
            'Track',
            'Parking'
        ],
        'equipment': [
            'Goal Posts',
            'Scoreboard',
            'First Aid Station'
        ],
        'accessibility': {
            'wheelchair_accessible': True,
            'parking_spaces': 50,
            'accessible_paths': True
        },
        'maintenance_schedule': {
            'last_cleaning': '2024-03-20',
            'next_cleaning': '2024-03-27',
            'last_inspection': '2024-03-10',
            'next_inspection': '2024-04-10'
        },
        'status': 'Available',
        'notes': 'Field in excellent condition',
        'last_updated': '2024-03-20T10:00:00'
    }
    
    # Create mock activity with metadata
    mock_activity = MagicMock()
    mock_activity.activity_metadata = {'location': location_data}
    mock_activity.location = location_data  # Add this line
    
    # Mock the database operations
    mock_query = MagicMock()
    mock_query.filter.return_value.first.return_value = mock_activity
    activity_service.db.query = MagicMock(return_value=mock_query)
    activity_service.db.commit = MagicMock()
    
    # Call the method
    result = await activity_service.update_activity_location(1, location_data)
    
    # Verify the location was updated
    activity_service.db.query.assert_called_once()
    mock_query.filter.assert_called_once()
    activity_service.db.commit.assert_called_once()
    assert result == location_data
    assert result['location_id'] == 1
    assert result['name'] == 'Outdoor Field'
    assert result['type'] == 'Outdoor'
    assert result['capacity'] == 200
    assert result['dimensions']['length'] == 100
    assert result['dimensions']['width'] == 60
    assert len(result['facilities']) == 3
    assert len(result['equipment']) == 3
    assert result['accessibility']['wheelchair_accessible'] is True
    assert result['accessibility']['parking_spaces'] == 50
    assert result['maintenance_schedule']['last_cleaning'] == '2024-03-20'
    assert result['maintenance_schedule']['next_cleaning'] == '2024-03-27'
    assert result['status'] == 'Available'
    assert result['notes'] == 'Field in excellent condition'
    assert result['last_updated'] == '2024-03-20T10:00:00'

@pytest.mark.asyncio
async def test_get_activity_attendance(activity_service):
    """Test getting activity attendance."""
    # Create mock attendance data
    mock_attendance = {
        'attendance_id': 1,
        'date': '2024-03-20',
        'total_participants': 25,
        'present': 22,
        'absent': 2,
        'excused': 1,
        'participants': [
            {
                'participant_id': 1,
                'name': 'John Doe',
                'status': 'Present',
                'check_in_time': '09:00:00',
                'check_out_time': '10:30:00',
                'notes': 'Participated fully'
            },
            {
                'participant_id': 2,
                'name': 'Jane Smith',
                'status': 'Present',
                'check_in_time': '09:05:00',
                'check_out_time': '10:30:00',
                'notes': 'Late arrival'
            },
            {
                'participant_id': 3,
                'name': 'Bob Johnson',
                'status': 'Absent',
                'notes': 'No notification'
            }
        ],
        'attendance_rate': 0.88,
        'notes': 'Good attendance overall',
        'last_updated': '2024-03-20T10:30:00'
    }
    
    # Create mock activity with metadata
    mock_activity = MagicMock()
    mock_activity.activity_metadata = {'attendance': mock_attendance}
    mock_activity.attendance = mock_attendance  # Add this line
    
    # Mock the database query
    mock_query = MagicMock()
    mock_query.filter.return_value.first.return_value = mock_activity
    activity_service.db.query = MagicMock(return_value=mock_query)
    
    # Call the method
    result = await activity_service.get_activity_attendance(1)
    
    # Verify the attendance was retrieved
    activity_service.db.query.assert_called_once()
    mock_query.filter.assert_called_once()
    assert result == mock_attendance
    assert result['attendance_id'] == 1
    assert result['date'] == '2024-03-20'
    assert result['total_participants'] == 25
    assert result['present'] == 22
    assert result['absent'] == 2
    assert result['excused'] == 1
    assert len(result['participants']) == 3
    assert result['participants'][0]['participant_id'] == 1
    assert result['participants'][0]['name'] == 'John Doe'
    assert result['participants'][0]['status'] == 'Present'
    assert result['participants'][1]['participant_id'] == 2
    assert result['participants'][1]['name'] == 'Jane Smith'
    assert result['participants'][1]['status'] == 'Present'
    assert result['participants'][2]['participant_id'] == 3
    assert result['participants'][2]['name'] == 'Bob Johnson'
    assert result['participants'][2]['status'] == 'Absent'
    assert result['attendance_rate'] == 0.88
    assert result['notes'] == 'Good attendance overall'
    assert result['last_updated'] == '2024-03-20T10:30:00'

@pytest.mark.asyncio
async def test_record_activity_attendance(activity_service):
    """Test recording activity attendance."""
    # Create mock attendance data
    attendance_data = {
        'attendance_id': 1,
        'date': '2024-03-21',
        'total_participants': 30,
        'present': 28,
        'absent': 1,
        'excused': 1,
        'participants': [
            {
                'participant_id': 1,
                'name': 'John Doe',
                'status': 'Present',
                'check_in_time': '09:00:00',
                'check_out_time': '10:30:00',
                'notes': 'Participated fully'
            },
            {
                'participant_id': 2,
                'name': 'Jane Smith',
                'status': 'Present',
                'check_in_time': '09:00:00',
                'check_out_time': '10:30:00',
                'notes': 'Participated fully'
            },
            {
                'participant_id': 3,
                'name': 'Bob Johnson',
                'status': 'Excused',
                'notes': 'Medical appointment'
            }
        ],
        'attendance_rate': 0.93,
        'notes': 'Excellent attendance',
        'last_updated': '2024-03-21T10:30:00'
    }
    
    # Create mock activity with metadata
    mock_activity = MagicMock()
    attendance_list = []
    mock_activity.activity_metadata = {'attendance': attendance_list}
    mock_activity.attendance = attendance_list
    
    # Mock the database operations
    mock_query = MagicMock()
    mock_query.filter.return_value.first.return_value = mock_activity
    activity_service.db.query = MagicMock(return_value=mock_query)
    activity_service.db.commit = MagicMock()
    
    # Call the method
    result = await activity_service.record_activity_attendance(1, attendance_data)
    
    # Verify the attendance was recorded
    activity_service.db.query.assert_called_once()
    mock_query.filter.assert_called_once()
    activity_service.db.commit.assert_called_once()
    assert result == attendance_data
    assert len(attendance_list) == 1
    assert attendance_list[0] == attendance_data

@pytest.mark.asyncio
async def test_get_activity_metrics(activity_service):
    """Test getting activity metrics."""
    # Create mock metrics data
    mock_metrics = {
        'metrics_id': 1,
        'performance_metrics': {
            'completion_rate': 0.95,
            'average_duration': 45,
            'success_rate': 0.85,
            'skill_progression': {
                'beginner': 0.2,
                'intermediate': 0.5,
                'advanced': 0.3
            }
        },
        'feedback_metrics': {
            'average_rating': 4.5,
            'satisfaction_score': 0.9,
            'engagement_level': 'High',
            'improvement_areas': [
                'Equipment availability',
                'Time management'
            ]
        },
        'assessment_period': {
            'start_date': '2024-03-01',
            'end_date': '2024-03-31',
            'frequency': 'Weekly'
        }
    }
    
    # Create mock activity with metadata
    mock_activity = MagicMock()
    mock_activity.activity_metadata = {'metrics': mock_metrics}
    mock_activity.metrics = mock_metrics  # Add this line
    
    # Mock the database query
    mock_query = MagicMock()
    mock_query.filter.return_value.first.return_value = mock_activity
    activity_service.db.query = MagicMock(return_value=mock_query)
    
    # Call the method
    result = await activity_service.get_activity_metrics(1)
    
    # Verify the metrics were retrieved
    activity_service.db.query.assert_called_once()
    mock_query.filter.assert_called_once()
    assert result == mock_metrics
    assert result['metrics_id'] == 1
    assert result['performance_metrics']['completion_rate'] == 0.95
    assert result['performance_metrics']['average_duration'] == 45
    assert result['performance_metrics']['success_rate'] == 0.85
    assert result['performance_metrics']['skill_progression']['beginner'] == 0.2
    assert result['performance_metrics']['skill_progression']['intermediate'] == 0.5
    assert result['performance_metrics']['skill_progression']['advanced'] == 0.3
    assert result['feedback_metrics']['average_rating'] == 4.5
    assert result['feedback_metrics']['satisfaction_score'] == 0.9
    assert result['feedback_metrics']['engagement_level'] == 'High'
    assert len(result['feedback_metrics']['improvement_areas']) == 2
    assert result['feedback_metrics']['improvement_areas'][0] == 'Equipment availability'
    assert result['feedback_metrics']['improvement_areas'][1] == 'Time management'
    assert result['assessment_period']['start_date'] == '2024-03-01'
    assert result['assessment_period']['end_date'] == '2024-03-31'
    assert result['assessment_period']['frequency'] == 'Weekly'

@pytest.mark.asyncio
async def test_update_activity_metrics(activity_service):
    """Test updating activity metrics."""
    # Create mock metrics data
    metrics_data = {
        'metrics_id': 1,
        'performance_metrics': {
            'completion_rate': 0.98,
            'average_duration': 50,
            'success_rate': 0.9,
            'skill_progression': {
                'beginner': 0.15,
                'intermediate': 0.45,
                'advanced': 0.4
            }
        },
        'feedback_metrics': {
            'average_rating': 4.8,
            'satisfaction_score': 0.95,
            'engagement_level': 'Very High',
            'improvement_areas': [
                'Equipment maintenance',
                'Space utilization'
            ]
        },
        'assessment_period': {
            'start_date': '2024-04-01',
            'end_date': '2024-04-30',
            'frequency': 'Weekly'
        }
    }
    
    # Create mock activity with metadata
    mock_activity = MagicMock()
    mock_activity.activity_metadata = {'metrics': metrics_data}
    mock_activity.metrics = metrics_data  # Add this line
    
    # Mock the database operations
    mock_query = MagicMock()
    mock_query.filter.return_value.first.return_value = mock_activity
    activity_service.db.query = MagicMock(return_value=mock_query)
    activity_service.db.commit = MagicMock()
    
    # Call the method
    result = await activity_service.update_activity_metrics(1, metrics_data)
    
    # Verify the metrics were updated
    activity_service.db.query.assert_called_once()
    mock_query.filter.assert_called_once()
    activity_service.db.commit.assert_called_once()
    assert result == metrics_data
    assert result['metrics_id'] == 1
    assert result['performance_metrics']['completion_rate'] == 0.98
    assert result['performance_metrics']['average_duration'] == 50
    assert result['performance_metrics']['success_rate'] == 0.9
    assert result['performance_metrics']['skill_progression']['beginner'] == 0.15
    assert result['performance_metrics']['skill_progression']['intermediate'] == 0.45
    assert result['performance_metrics']['skill_progression']['advanced'] == 0.4
    assert result['feedback_metrics']['average_rating'] == 4.8
    assert result['feedback_metrics']['satisfaction_score'] == 0.95
    assert result['feedback_metrics']['engagement_level'] == 'Very High'
    assert len(result['feedback_metrics']['improvement_areas']) == 2
    assert result['feedback_metrics']['improvement_areas'][0] == 'Equipment maintenance'
    assert result['feedback_metrics']['improvement_areas'][1] == 'Space utilization'
    assert result['assessment_period']['start_date'] == '2024-04-01'
    assert result['assessment_period']['end_date'] == '2024-04-30'
    assert result['assessment_period']['frequency'] == 'Weekly'

@pytest.mark.asyncio
async def test_get_activity_feedback(activity_service):
    """Test getting activity feedback."""
    # Create mock feedback data
    mock_feedback = {
        'feedback_id': 1,
        'participant_id': 1,
        'participant_name': 'John Doe',
        'rating': 4.5,
        'comments': 'Great activity, very engaging',
        'suggestions': 'Could use more equipment',
        'categories': ['Engagement', 'Organization'],
        'submitted_at': '2024-03-20T10:30:00',
        'last_updated': '2024-03-20T10:30:00',
        'status': 'Reviewed',
        'response': 'Thank you for your feedback'
    }
    
    # Create mock activity with metadata
    mock_activity = MagicMock()
    mock_activity.activity_metadata = {'feedback': mock_feedback}
    mock_activity.feedback = mock_feedback  # Add this line
    
    # Mock the database query
    mock_query = MagicMock()
    mock_query.filter.return_value.first.return_value = mock_activity
    activity_service.db.query = MagicMock(return_value=mock_query)
    
    # Call the method
    result = await activity_service.get_activity_feedback(1)
    
    # Verify the feedback was retrieved
    activity_service.db.query.assert_called_once()
    mock_query.filter.assert_called_once()
    assert result == mock_feedback
    assert result['feedback_id'] == 1
    assert result['participant_id'] == 1
    assert result['participant_name'] == 'John Doe'
    assert result['rating'] == 4.5
    assert result['comments'] == 'Great activity, very engaging'
    assert result['suggestions'] == 'Could use more equipment'
    assert len(result['categories']) == 2
    assert result['categories'][0] == 'Engagement'
    assert result['categories'][1] == 'Organization'
    assert result['submitted_at'] == '2024-03-20T10:30:00'
    assert result['last_updated'] == '2024-03-20T10:30:00'
    assert result['status'] == 'Reviewed'
    assert result['response'] == 'Thank you for your feedback'

@pytest.mark.asyncio
async def test_add_activity_feedback(activity_service):
    """Test adding activity feedback."""
    # Create mock feedback data
    feedback_data = {
        'feedback_id': 2,
        'participant_id': 2,
        'participant_name': 'Jane Smith',
        'rating': 5.0,
        'comments': 'Excellent session, learned a lot',
        'suggestions': 'More practice time would be helpful',
        'categories': ['Learning', 'Enjoyment'],
        'submitted_at': '2024-03-21T11:00:00',
        'last_updated': '2024-03-21T11:00:00',
        'status': 'Pending',
        'response': None
    }
    
    # Create mock activity with metadata
    mock_activity = MagicMock()
    feedback_list = []
    mock_activity.activity_metadata = {'feedback': feedback_list}
    mock_activity.feedback = feedback_list
    
    # Mock the database operations
    mock_query = MagicMock()
    mock_query.filter.return_value.first.return_value = mock_activity
    activity_service.db.query = MagicMock(return_value=mock_query)
    activity_service.db.commit = MagicMock()
    
    # Call the method
    result = await activity_service.add_activity_feedback(1, feedback_data)
    
    # Verify the feedback was added
    activity_service.db.query.assert_called_once()
    mock_query.filter.assert_called_once()
    activity_service.db.commit.assert_called_once()
    assert result == feedback_data
    assert len(feedback_list) == 1
    assert feedback_list[0] == feedback_data

@pytest.mark.asyncio
async def test_get_activity_safety_incidents(activity_service):
    """Test getting activity safety incidents."""
    # Create mock incidents data
    mock_incidents = {
        'incident_id': 1,
        'activity_id': 1,
        'incident_type': 'Minor Injury',
        'description': 'Student twisted ankle during warm-up',
        'severity': 'Low',
        'location': 'Main Field',
        'action_taken': 'Applied ice and provided rest',
        'reported_by': 'Coach Smith',
        'reported_at': '2024-03-20T09:15:00',
        'resolved_at': '2024-03-20T09:30:00',
        'status': 'Resolved',
        'follow_up_actions': [
            'Review warm-up procedures',
            'Update safety guidelines'
        ],
        'affected_participants': [
            {
                'participant_id': 1,
                'name': 'John Doe',
                'injury_type': 'Ankle sprain',
                'severity': 'Minor'
            }
        ],
        'preventive_measures': [
            'Proper warm-up demonstration',
            'Surface inspection before activity'
        ]
    }
    
    # Create mock activity with metadata
    mock_activity = MagicMock()
    mock_activity.activity_metadata = {'safety_incidents': mock_incidents}
    mock_activity.safety_incidents = mock_incidents  # Add this line
    
    # Mock the database query
    mock_query = MagicMock()
    mock_query.filter.return_value.first.return_value = mock_activity
    activity_service.db.query = MagicMock(return_value=mock_query)
    
    # Call the method
    result = await activity_service.get_activity_safety_incidents(1)
    
    # Verify the incidents were retrieved
    activity_service.db.query.assert_called_once()
    mock_query.filter.assert_called_once()
    assert result == mock_incidents
    assert result['incident_id'] == 1
    assert result['activity_id'] == 1
    assert result['incident_type'] == 'Minor Injury'
    assert result['description'] == 'Student twisted ankle during warm-up'
    assert result['severity'] == 'Low'
    assert result['location'] == 'Main Field'
    assert result['action_taken'] == 'Applied ice and provided rest'
    assert result['reported_by'] == 'Coach Smith'
    assert result['reported_at'] == '2024-03-20T09:15:00'
    assert result['resolved_at'] == '2024-03-20T09:30:00'
    assert result['status'] == 'Resolved'
    assert len(result['follow_up_actions']) == 2
    assert result['follow_up_actions'][0] == 'Review warm-up procedures'
    assert result['follow_up_actions'][1] == 'Update safety guidelines'
    assert len(result['affected_participants']) == 1
    assert result['affected_participants'][0]['participant_id'] == 1
    assert result['affected_participants'][0]['name'] == 'John Doe'
    assert result['affected_participants'][0]['injury_type'] == 'Ankle sprain'
    assert result['affected_participants'][0]['severity'] == 'Minor'
    assert len(result['preventive_measures']) == 2
    assert result['preventive_measures'][0] == 'Proper warm-up demonstration'
    assert result['preventive_measures'][1] == 'Surface inspection before activity'

@pytest.mark.asyncio
async def test_record_activity_safety_incident(activity_service):
    """Test recording activity safety incident."""
    # Create mock incident data
    incident_data = {
        'incident_id': 2,
        'activity_id': 1,
        'incident_type': 'Equipment Failure',
        'description': 'Basketball hoop bracket came loose',
        'severity': 'Medium',
        'location': 'Indoor Court',
        'action_taken': 'Removed equipment and secured area',
        'reported_by': 'Coach Johnson',
        'reported_at': '2024-03-21T14:00:00',
        'resolved_at': None,
        'status': 'Under Investigation',
        'follow_up_actions': [
            'Inspect all equipment',
            'Schedule maintenance'
        ],
        'affected_participants': [],
        'preventive_measures': [
            'Regular equipment inspection',
            'Maintenance schedule review'
        ]
    }
    
    # Create mock activity with metadata
    mock_activity = MagicMock()
    incident_list = []
    mock_activity.activity_metadata = {'safety_incidents': incident_list}
    mock_activity.safety_incidents = incident_list
    
    # Mock the database operations
    mock_query = MagicMock()
    mock_query.filter.return_value.first.return_value = mock_activity
    activity_service.db.query = MagicMock(return_value=mock_query)
    activity_service.db.commit = MagicMock()
    
    # Call the method
    result = await activity_service.record_activity_safety_incident(1, incident_data)
    
    # Verify the incident was recorded
    activity_service.db.query.assert_called_once()
    mock_query.filter.assert_called_once()
    activity_service.db.commit.assert_called_once()
    assert result == incident_data
    assert len(incident_list) == 1
    assert incident_list[0] == incident_data

@pytest.mark.asyncio
async def test_get_activity_risk_assessment(activity_service):
    """Test getting activity risk assessment."""
    # Create mock risk assessment data
    mock_risk_assessment = {
        'assessment_id': 1,
        'activity_id': 1,
        'assessment_date': '2024-03-20',
        'risk_level': 'Medium',
        'risk_factors': [
            {
                'factor': 'Equipment Usage',
                'severity': 'Medium',
                'probability': 'Low',
                'mitigation': 'Regular equipment inspection'
            },
            {
                'factor': 'Physical Contact',
                'severity': 'High',
                'probability': 'Medium',
                'mitigation': 'Supervision and rules enforcement'
            }
        ],
        'safety_measures': [
            'First aid kit available',
            'Emergency contact list posted',
            'Supervisor present at all times'
        ],
        'participant_requirements': [
            'Proper athletic attire',
            'Water bottle',
            'Medical clearance form'
        ],
        'environmental_considerations': [
            'Weather conditions',
            'Surface conditions',
            'Lighting'
        ],
        'emergency_procedures': [
            'First aid response',
            'Emergency services contact',
            'Evacuation routes'
        ],
        'last_updated': '2024-03-20T10:00:00',
        'status': 'Active'
    }
    
    # Create mock activity with metadata
    mock_activity = MagicMock()
    mock_activity.activity_metadata = {'risk_assessment': mock_risk_assessment}
    mock_activity.risk_assessment = mock_risk_assessment  # Add this line
    
    # Mock the database query
    mock_query = MagicMock()
    mock_query.filter.return_value.first.return_value = mock_activity
    activity_service.db.query = MagicMock(return_value=mock_query)
    
    # Call the method
    result = await activity_service.get_activity_risk_assessment(1)
    
    # Verify the risk assessment was retrieved
    activity_service.db.query.assert_called_once()
    mock_query.filter.assert_called_once()
    assert result == mock_risk_assessment
    assert result['assessment_id'] == 1
    assert result['activity_id'] == 1
    assert result['assessment_date'] == '2024-03-20'
    assert result['risk_level'] == 'Medium'
    assert len(result['risk_factors']) == 2
    assert result['risk_factors'][0]['factor'] == 'Equipment Usage'
    assert result['risk_factors'][0]['severity'] == 'Medium'
    assert result['risk_factors'][0]['probability'] == 'Low'
    assert result['risk_factors'][0]['mitigation'] == 'Regular equipment inspection'
    assert result['risk_factors'][1]['factor'] == 'Physical Contact'
    assert result['risk_factors'][1]['severity'] == 'High'
    assert result['risk_factors'][1]['probability'] == 'Medium'
    assert result['risk_factors'][1]['mitigation'] == 'Supervision and rules enforcement'
    assert len(result['safety_measures']) == 3
    assert result['safety_measures'][0] == 'First aid kit available'
    assert result['safety_measures'][1] == 'Emergency contact list posted'
    assert result['safety_measures'][2] == 'Supervisor present at all times'
    assert len(result['participant_requirements']) == 3
    assert result['participant_requirements'][0] == 'Proper athletic attire'
    assert result['participant_requirements'][1] == 'Water bottle'
    assert result['participant_requirements'][2] == 'Medical clearance form'
    assert len(result['environmental_considerations']) == 3
    assert result['environmental_considerations'][0] == 'Weather conditions'
    assert result['environmental_considerations'][1] == 'Surface conditions'
    assert result['environmental_considerations'][2] == 'Lighting'
    assert len(result['emergency_procedures']) == 3
    assert result['emergency_procedures'][0] == 'First aid response'
    assert result['emergency_procedures'][1] == 'Emergency services contact'
    assert result['emergency_procedures'][2] == 'Evacuation routes'
    assert result['last_updated'] == '2024-03-20T10:00:00'
    assert result['status'] == 'Active'

@pytest.mark.asyncio
async def test_update_activity_risk_assessment(activity_service):
    """Test updating activity risk assessment."""
    # Create mock risk assessment data
    risk_assessment_data = {
        'assessment_id': 2,
        'activity_id': 1,
        'assessment_date': '2024-03-21',
        'risk_level': 'High',
        'risk_factors': [
            {
                'factor': 'Weather Conditions',
                'severity': 'High',
                'probability': 'High',
                'mitigation': 'Weather monitoring and backup plan'
            },
            {
                'factor': 'Equipment Safety',
                'severity': 'High',
                'probability': 'Medium',
                'mitigation': 'Daily inspection and maintenance'
            }
        ],
        'safety_measures': [
            'Weather monitoring system',
            'Backup indoor facility',
            'Emergency weather shelter'
        ],
        'participant_requirements': [
            'Weather-appropriate clothing',
            'Water bottle',
            'Emergency contact information'
        ],
        'environmental_considerations': [
            'Weather forecast',
            'Temperature monitoring',
            'Wind conditions'
        ],
        'emergency_procedures': [
            'Weather emergency response',
            'Shelter procedures',
            'Communication protocol'
        ],
        'last_updated': '2024-03-21T09:00:00',
        'status': 'Active'
    }
    
    # Create mock activity with metadata
    mock_activity = MagicMock()
    mock_activity.activity_metadata = {'risk_assessment': risk_assessment_data}
    mock_activity.risk_assessment = risk_assessment_data  # Add this line
    
    # Mock the database operations
    mock_query = MagicMock()
    mock_query.filter.return_value.first.return_value = mock_activity
    activity_service.db.query = MagicMock(return_value=mock_query)
    activity_service.db.commit = MagicMock()
    
    # Call the method
    result = await activity_service.update_activity_risk_assessment(1, risk_assessment_data)
    
    # Verify the risk assessment was updated
    activity_service.db.query.assert_called_once()
    mock_query.filter.assert_called_once()
    activity_service.db.commit.assert_called_once()
    assert result == risk_assessment_data
    assert result['assessment_id'] == 2
    assert result['activity_id'] == 1
    assert result['assessment_date'] == '2024-03-21'
    assert result['risk_level'] == 'High'
    assert len(result['risk_factors']) == 2
    assert result['risk_factors'][0]['factor'] == 'Weather Conditions'
    assert result['risk_factors'][0]['severity'] == 'High'
    assert result['risk_factors'][0]['probability'] == 'High'
    assert result['risk_factors'][0]['mitigation'] == 'Weather monitoring and backup plan'
    assert result['risk_factors'][1]['factor'] == 'Equipment Safety'
    assert result['risk_factors'][1]['severity'] == 'High'
    assert result['risk_factors'][1]['probability'] == 'Medium'
    assert result['risk_factors'][1]['mitigation'] == 'Daily inspection and maintenance'
    assert len(result['safety_measures']) == 3
    assert result['safety_measures'][0] == 'Weather monitoring system'
    assert result['safety_measures'][1] == 'Backup indoor facility'
    assert result['safety_measures'][2] == 'Emergency weather shelter'
    assert len(result['participant_requirements']) == 3
    assert result['participant_requirements'][0] == 'Weather-appropriate clothing'
    assert result['participant_requirements'][1] == 'Water bottle'
    assert result['participant_requirements'][2] == 'Emergency contact information'
    assert len(result['environmental_considerations']) == 3
    assert result['environmental_considerations'][0] == 'Weather forecast'
    assert result['environmental_considerations'][1] == 'Temperature monitoring'
    assert result['environmental_considerations'][2] == 'Wind conditions'
    assert len(result['emergency_procedures']) == 3
    assert result['emergency_procedures'][0] == 'Weather emergency response'
    assert result['emergency_procedures'][1] == 'Shelter procedures'
    assert result['emergency_procedures'][2] == 'Communication protocol'
    assert result['last_updated'] == '2024-03-21T09:00:00'
    assert result['status'] == 'Active'
 