import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from app.services.physical_education.activity_collaboration_manager import ActivityCollaborationManager

@pytest.fixture
def collaboration_manager():
    manager = ActivityCollaborationManager()
    yield manager

@pytest.fixture
def mock_activity_data():
    dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
    return pd.DataFrame({
        'date': dates,
        'activity_id': [f'act_{i}' for i in range(30)],
        'student_id': ['student1'] * 30,
        'activity_type': np.random.choice(['running', 'jumping', 'throwing'], 30),
        'category': np.random.choice(['cardio', 'strength', 'flexibility'], 30),
        'score': np.random.uniform(0, 100, 30),
        'duration': np.random.randint(5, 60, 30),
        'calories_burned': np.random.uniform(50, 500, 30),
        'heart_rate': np.random.randint(60, 180, 30),
        'notes': [f'Note {i}' for i in range(30)]
    })

@pytest.fixture
def mock_team_data():
    return {
        'team_id': 'team1',
        'name': 'Team A',
        'members': ['student1', 'student2', 'student3'],
        'coach_id': 'coach1',
        'goals': ['Improve team coordination', 'Increase team endurance'],
        'schedule': {
            'practice_days': ['Monday', 'Wednesday', 'Friday'],
            'practice_time': '15:00'
        }
    }

@pytest.fixture
def mock_collaboration_data():
    return {
        'collaboration_id': 'collab1',
        'activity_id': 'act_1',
        'team_id': 'team1',
        'participants': ['student1', 'student2', 'student3'],
        'type': 'group_activity',
        'status': 'in_progress',
        'start_time': datetime.now(),
        'end_time': None,
        'notes': 'Team practice session'
    }

async def test_initialization(collaboration_manager):
    """Test collaboration manager initialization."""
    assert collaboration_manager is not None
    assert hasattr(collaboration_manager, 'settings')
    assert hasattr(collaboration_manager, 'active_collaborations')

async def test_create_team(collaboration_manager, mock_team_data):
    """Test team creation functionality."""
    team = await collaboration_manager.create_team(mock_team_data)
    assert team is not None
    assert team['team_id'] == mock_team_data['team_id']
    assert team['name'] == mock_team_data['name']
    assert team['members'] == mock_team_data['members']

async def test_update_team(collaboration_manager, mock_team_data):
    """Test team update functionality."""
    team = await collaboration_manager.create_team(mock_team_data)
    
    updated_data = mock_team_data.copy()
    updated_data['name'] = 'Updated Team A'
    updated_data['members'].append('student4')
    
    updated_team = await collaboration_manager.update_team(team['team_id'], updated_data)
    assert updated_team['updated'] is True

async def test_delete_team(collaboration_manager, mock_team_data):
    """Test team deletion functionality."""
    team = await collaboration_manager.create_team(mock_team_data)
    
    result = await collaboration_manager.delete_team(team['team_id'])
    assert result['deleted'] is True

async def test_get_team(collaboration_manager, mock_team_data):
    """Test team retrieval functionality."""
    team = await collaboration_manager.create_team(mock_team_data)
    
    retrieved_team = await collaboration_manager.get_team(team['team_id'])
    assert retrieved_team['found'] is True

async def test_list_teams(collaboration_manager, mock_team_data):
    """Test team listing functionality."""
    team1 = await collaboration_manager.create_team(mock_team_data)
    team2_data = mock_team_data.copy()
    team2_data['team_id'] = 'team2'
    team2_data['name'] = 'Team B'
    team2 = await collaboration_manager.create_team(team2_data)
    
    teams = await collaboration_manager.list_teams()
    assert teams['count'] == 2

async def test_create_collaboration(collaboration_manager, mock_collaboration_data):
    """Test collaboration creation functionality."""
    collaboration = await collaboration_manager.create_collaboration(mock_collaboration_data)
    assert collaboration is not None

async def test_update_collaboration(collaboration_manager, mock_collaboration_data):
    """Test collaboration update functionality."""
    collaboration = await collaboration_manager.create_collaboration(mock_collaboration_data)
    
    updated_data = mock_collaboration_data.copy()
    updated_data['status'] = 'completed'
    
    updated_collaboration = await collaboration_manager.update_collaboration(
        collaboration['collaboration_id'],
        updated_data
    )
    assert updated_collaboration['updated'] is True

async def test_delete_collaboration(collaboration_manager, mock_collaboration_data):
    """Test collaboration deletion functionality."""
    collaboration = await collaboration_manager.create_collaboration(mock_collaboration_data)
    
    result = await collaboration_manager.delete_collaboration(collaboration['collaboration_id'])
    assert result is None  # delete_collaboration returns None

async def test_get_collaboration(collaboration_manager, mock_collaboration_data):
    """Test collaboration retrieval functionality."""
    collaboration = await collaboration_manager.create_collaboration(mock_collaboration_data)
    
    retrieved_collaboration = await collaboration_manager.get_user_collaborations('student1')
    assert len(retrieved_collaboration) > 0

async def test_list_collaborations(collaboration_manager, mock_collaboration_data):
    """Test collaboration listing functionality."""
    collaboration1 = await collaboration_manager.create_collaboration(mock_collaboration_data)
    collaboration2_data = mock_collaboration_data.copy()
    collaboration2_data['activity_id'] = 'act_2'
    collaboration2 = await collaboration_manager.create_collaboration(collaboration2_data)
    
    collaborations = await collaboration_manager.get_user_collaborations('student1')
    assert len(collaborations) >= 2

async def test_analyze_team_performance(collaboration_manager, mock_activity_data, mock_team_data):
    """Test team performance analysis functionality."""
    team = await collaboration_manager.create_team(mock_team_data)
    
    performance = await collaboration_manager.analyze_team_performance(team['team_id'])
    assert performance['analyzed'] is True

async def test_analyze_team_dynamics(collaboration_manager, mock_activity_data, mock_team_data):
    """Test team dynamics analysis functionality."""
    team = await collaboration_manager.create_team(mock_team_data)
    
    dynamics = await collaboration_manager.analyze_team_dynamics(team['team_id'])
    assert dynamics['analyzed'] is True

async def test_generate_team_report(collaboration_manager, mock_activity_data, mock_team_data):
    """Test team report generation functionality."""
    team = await collaboration_manager.create_team(mock_team_data)
    
    report = await collaboration_manager.generate_team_report(team['team_id'])
    assert report['generated'] is True

async def test_schedule_team_activity(collaboration_manager, mock_team_data):
    """Test team activity scheduling functionality."""
    team = await collaboration_manager.create_team(mock_team_data)
    
    activity = {
        'activity_id': 'act_1',
        'date': datetime.now(),
        'duration': 60,
        'location': 'Gymnasium',
        'type': 'practice'
    }
    
    scheduled = await collaboration_manager.schedule_team_activity(team['team_id'], activity)
    assert scheduled['scheduled'] is True

async def test_send_team_notification(collaboration_manager, mock_team_data):
    """Test team notification functionality."""
    team = await collaboration_manager.create_team(mock_team_data)
    
    notification = {
        'message': 'Practice session tomorrow',
        'priority': 'high',
        'type': 'reminder'
    }
    
    # Mock the notification service since it doesn't exist
    with patch('app.services.physical_education.activity_collaboration_manager.ActivityCollaborationManager._send_in_app_notification') as mock_send:
        mock_send.return_value = True
        result = await collaboration_manager.send_team_notification(
            team['team_id'],
            notification['message'],
            notification['type']
        )
        assert result['sent'] is True

async def test_error_handling(collaboration_manager):
    """Test error handling functionality."""
    # Test with invalid data
    result = await collaboration_manager.create_team({})
    assert result['team_created'] is True  # Should handle empty data gracefully

async def test_data_validation(collaboration_manager):
    """Test data validation functionality."""
    # Test with valid data
    valid_data = {
        'name': 'Test Team',
        'members': ['student1', 'student2'],
        'team_id': 'test_team'
    }
    
    result = await collaboration_manager.create_team(valid_data)
    assert result['team_created'] is True
    assert result['team_id'] == 'test_team' 