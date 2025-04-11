import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from app.services.physical_education.services.activity_collaboration_manager import ActivityCollaborationManager

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

def test_initialization(collaboration_manager):
    """Test proper initialization of ActivityCollaborationManager."""
    assert collaboration_manager.collaboration_config is not None
    assert isinstance(collaboration_manager.collaboration_config, dict)
    assert 'team_settings' in collaboration_manager.collaboration_config
    assert 'communication_settings' in collaboration_manager.collaboration_config
    assert 'collaboration_types' in collaboration_manager.collaboration_config

def test_create_team(collaboration_manager, mock_team_data):
    """Test team creation functionality."""
    team = collaboration_manager.create_team(mock_team_data)
    assert team is not None
    assert team['team_id'] == mock_team_data['team_id']
    assert team['name'] == mock_team_data['name']
    assert team['members'] == mock_team_data['members']

def test_update_team(collaboration_manager, mock_team_data):
    """Test team update functionality."""
    team = collaboration_manager.create_team(mock_team_data)
    
    updated_data = mock_team_data.copy()
    updated_data['name'] = 'Updated Team A'
    updated_data['members'].append('student4')
    
    updated_team = collaboration_manager.update_team(team['team_id'], updated_data)
    assert updated_team['name'] == 'Updated Team A'
    assert len(updated_team['members']) == 4

def test_delete_team(collaboration_manager, mock_team_data):
    """Test team deletion functionality."""
    team = collaboration_manager.create_team(mock_team_data)
    
    result = collaboration_manager.delete_team(team['team_id'])
    assert result is True
    
    with pytest.raises(Exception):
        collaboration_manager.get_team(team['team_id'])

def test_get_team(collaboration_manager, mock_team_data):
    """Test team retrieval functionality."""
    team = collaboration_manager.create_team(mock_team_data)
    
    retrieved_team = collaboration_manager.get_team(team['team_id'])
    assert retrieved_team['team_id'] == team['team_id']
    assert retrieved_team['name'] == team['name']

def test_list_teams(collaboration_manager, mock_team_data):
    """Test team listing functionality."""
    team1 = collaboration_manager.create_team(mock_team_data)
    team2_data = mock_team_data.copy()
    team2_data['team_id'] = 'team2'
    team2_data['name'] = 'Team B'
    team2 = collaboration_manager.create_team(team2_data)
    
    teams = collaboration_manager.list_teams()
    assert len(teams) == 2
    
    filtered_teams = collaboration_manager.list_teams(coach_id='coach1')
    assert len(filtered_teams) == 2

def test_create_collaboration(collaboration_manager, mock_collaboration_data):
    """Test collaboration creation functionality."""
    collaboration = collaboration_manager.create_collaboration(mock_collaboration_data)
    assert collaboration is not None
    assert collaboration['collaboration_id'] == mock_collaboration_data['collaboration_id']
    assert collaboration['team_id'] == mock_collaboration_data['team_id']
    assert collaboration['type'] == mock_collaboration_data['type']

def test_update_collaboration(collaboration_manager, mock_collaboration_data):
    """Test collaboration update functionality."""
    collaboration = collaboration_manager.create_collaboration(mock_collaboration_data)
    
    updated_data = mock_collaboration_data.copy()
    updated_data['status'] = 'completed'
    updated_data['end_time'] = datetime.now()
    
    updated_collaboration = collaboration_manager.update_collaboration(
        collaboration['collaboration_id'],
        updated_data
    )
    assert updated_collaboration['status'] == 'completed'
    assert updated_collaboration['end_time'] is not None

def test_delete_collaboration(collaboration_manager, mock_collaboration_data):
    """Test collaboration deletion functionality."""
    collaboration = collaboration_manager.create_collaboration(mock_collaboration_data)
    
    result = collaboration_manager.delete_collaboration(collaboration['collaboration_id'])
    assert result is True
    
    with pytest.raises(Exception):
        collaboration_manager.get_collaboration(collaboration['collaboration_id'])

def test_get_collaboration(collaboration_manager, mock_collaboration_data):
    """Test collaboration retrieval functionality."""
    collaboration = collaboration_manager.create_collaboration(mock_collaboration_data)
    
    retrieved_collaboration = collaboration_manager.get_collaboration(collaboration['collaboration_id'])
    assert retrieved_collaboration['collaboration_id'] == collaboration['collaboration_id']
    assert retrieved_collaboration['team_id'] == collaboration['team_id']

def test_list_collaborations(collaboration_manager, mock_collaboration_data):
    """Test collaboration listing functionality."""
    collaboration1 = collaboration_manager.create_collaboration(mock_collaboration_data)
    collaboration2_data = mock_collaboration_data.copy()
    collaboration2_data['collaboration_id'] = 'collab2'
    collaboration2 = collaboration_manager.create_collaboration(collaboration2_data)
    
    collaborations = collaboration_manager.list_collaborations()
    assert len(collaborations) == 2
    
    filtered_collaborations = collaboration_manager.list_collaborations(team_id='team1')
    assert len(filtered_collaborations) == 2

def test_analyze_team_performance(collaboration_manager, mock_activity_data, mock_team_data):
    """Test team performance analysis."""
    team = collaboration_manager.create_team(mock_team_data)
    performance = collaboration_manager.analyze_team_performance(team['team_id'], mock_activity_data)
    assert 'team_metrics' in performance
    assert 'individual_contributions' in performance
    assert 'improvement_areas' in performance
    assert 'recommendations' in performance

def test_analyze_team_dynamics(collaboration_manager, mock_activity_data, mock_team_data):
    """Test team dynamics analysis."""
    team = collaboration_manager.create_team(mock_team_data)
    dynamics = collaboration_manager.analyze_team_dynamics(team['team_id'], mock_activity_data)
    assert 'communication_patterns' in dynamics
    assert 'leadership_distribution' in dynamics
    assert 'team_cohesion' in dynamics
    assert 'recommendations' in dynamics

def test_generate_team_report(collaboration_manager, mock_activity_data, mock_team_data):
    """Test team report generation."""
    team = collaboration_manager.create_team(mock_team_data)
    report = collaboration_manager.generate_team_report(team['team_id'], mock_activity_data)
    assert 'team_summary' in report
    assert 'performance_metrics' in report
    assert 'dynamics_analysis' in report
    assert 'recommendations' in report

def test_schedule_team_activity(collaboration_manager, mock_team_data):
    """Test team activity scheduling."""
    team = collaboration_manager.create_team(mock_team_data)
    activity = {
        'activity_id': 'act_1',
        'type': 'practice',
        'date': datetime.now() + timedelta(days=1),
        'duration': 60,
        'location': 'Gymnasium'
    }
    
    scheduled = collaboration_manager.schedule_team_activity(team['team_id'], activity)
    assert scheduled is True
    assert 'schedule' in team
    assert len(team['schedule']) > 0

def test_send_team_notification(collaboration_manager, mock_team_data):
    """Test team notification sending."""
    team = collaboration_manager.create_team(mock_team_data)
    notification = {
        'type': 'reminder',
        'message': 'Practice session tomorrow',
        'priority': 'high'
    }
    
    with patch('app.services.notification_service.send_notification') as mock_send:
        collaboration_manager.send_team_notification(team['team_id'], notification)
        mock_send.assert_called()

def test_error_handling(collaboration_manager):
    """Test error handling in collaboration operations."""
    with pytest.raises(Exception):
        collaboration_manager.create_team(None)
    
    with pytest.raises(Exception):
        collaboration_manager.update_team('nonexistent_id', {})
    
    with pytest.raises(Exception):
        collaboration_manager.delete_team('nonexistent_id')
    
    with pytest.raises(Exception):
        collaboration_manager.get_team('nonexistent_id')

def test_data_validation(collaboration_manager):
    """Test data validation in collaboration operations."""
    invalid_team_data = {
        'team_id': 'team1',
        'name': '',  # Empty name
        'members': []  # Empty members list
    }
    
    with pytest.raises(Exception):
        collaboration_manager._validate_team_data(invalid_team_data) 