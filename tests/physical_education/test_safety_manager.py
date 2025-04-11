import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from app.services.physical_education.services.safety_manager import SafetyManager

@pytest.fixture
def safety_manager():
    manager = SafetyManager()
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
def mock_student_data():
    return {
        'student_id': 'student1',
        'name': 'John Doe',
        'age': 15,
        'grade': '9',
        'fitness_level': 'intermediate',
        'medical_conditions': ['asthma'],
        'goals': ['improve endurance', 'increase strength']
    }

@pytest.fixture
def mock_incident_data():
    return {
        'incident_id': 'inc1',
        'student_id': 'student1',
        'activity_id': 'act1',
        'date': datetime.now(),
        'type': 'injury',
        'severity': 'minor',
        'description': 'Sprained ankle during running',
        'action_taken': 'Applied ice and rest',
        'follow_up_required': True
    }

def test_initialization(safety_manager):
    """Test proper initialization of SafetyManager."""
    assert safety_manager.safety_config is not None
    assert isinstance(safety_manager.safety_config, dict)
    assert 'safety_protocols' in safety_manager.safety_config
    assert 'risk_thresholds' in safety_manager.safety_config
    assert 'emergency_procedures' in safety_manager.safety_config

def test_assess_activity_safety(safety_manager, mock_activity_data, mock_student_data):
    """Test activity safety assessment."""
    assessment = safety_manager.assess_activity_safety(mock_activity_data, mock_student_data)
    assert 'safety_score' in assessment
    assert 'risk_factors' in assessment
    assert 'recommendations' in assessment
    assert 'emergency_procedures' in assessment

def test_monitor_activity_safety(safety_manager, mock_activity_data):
    """Test activity safety monitoring."""
    monitoring = safety_manager.monitor_activity_safety(mock_activity_data)
    assert 'safety_status' in monitoring
    assert 'alerts' in monitoring
    assert 'metrics' in monitoring
    assert 'trends' in monitoring

def test_generate_safety_report(safety_manager, mock_activity_data):
    """Test safety report generation."""
    report = safety_manager.generate_safety_report(mock_activity_data)
    assert 'summary' in report
    assert 'risk_analysis' in report
    assert 'incident_history' in report
    assert 'recommendations' in report

def test_handle_safety_incident(safety_manager, mock_incident_data):
    """Test safety incident handling."""
    incident = safety_manager.handle_safety_incident(mock_incident_data)
    assert incident is not None
    assert incident['incident_id'] == mock_incident_data['incident_id']
    assert incident['status'] == 'handled'
    assert 'resolution' in incident

def test_analyze_safety_trends(safety_manager, mock_activity_data):
    """Test safety trend analysis."""
    trends = safety_manager.analyze_safety_trends(mock_activity_data)
    assert 'incident_trends' in trends
    assert 'risk_patterns' in trends
    assert 'improvement_areas' in trends
    assert 'predictions' in trends

def test_validate_equipment_safety(safety_manager):
    """Test equipment safety validation."""
    equipment = {
        'equipment_id': 'eq1',
        'type': 'treadmill',
        'last_inspection': datetime.now() - timedelta(days=30),
        'condition': 'good'
    }
    
    validation = safety_manager.validate_equipment_safety(equipment)
    assert 'safety_status' in validation
    assert 'inspection_needed' in validation
    assert 'maintenance_required' in validation

def test_check_environmental_safety(safety_manager):
    """Test environmental safety checking."""
    environment = {
        'location': 'gymnasium',
        'temperature': 22,
        'humidity': 50,
        'lighting': 'good',
        'floor_condition': 'dry'
    }
    
    safety_check = safety_manager.check_environmental_safety(environment)
    assert 'safety_status' in safety_check
    assert 'hazards' in safety_check
    assert 'recommendations' in safety_check

def test_manage_emergency_procedures(safety_manager):
    """Test emergency procedure management."""
    emergency = {
        'type': 'medical_emergency',
        'severity': 'high',
        'location': 'gymnasium',
        'affected_students': ['student1']
    }
    
    procedures = safety_manager.manage_emergency_procedures(emergency)
    assert 'action_steps' in procedures
    assert 'contact_list' in procedures
    assert 'evacuation_plan' in procedures
    assert 'follow_up_actions' in procedures

def test_track_safety_compliance(safety_manager, mock_activity_data):
    """Test safety compliance tracking."""
    compliance = safety_manager.track_safety_compliance(mock_activity_data)
    assert 'compliance_score' in compliance
    assert 'violations' in compliance
    assert 'improvement_areas' in compliance
    assert 'action_items' in compliance

def test_error_handling(safety_manager):
    """Test error handling in safety operations."""
    with pytest.raises(Exception):
        safety_manager.assess_activity_safety(None, None)
    
    with pytest.raises(Exception):
        safety_manager.handle_safety_incident(None)
    
    with pytest.raises(Exception):
        safety_manager.validate_equipment_safety(None)

def test_safety_configuration(safety_manager):
    """Test safety configuration functionality."""
    safety_manager.configure_safety(
        safety_protocols=['equipment_check', 'environment_check', 'emergency_drill'],
        risk_thresholds={
            'heart_rate': 180,
            'temperature': 30,
            'humidity': 80
        },
        emergency_procedures={
            'medical_emergency': ['call_911', 'administer_first_aid', 'notify_parents'],
            'fire': ['activate_alarm', 'evacuate', 'call_fire_department']
        }
    )
    
    assert 'equipment_check' in safety_manager.safety_config['safety_protocols']
    assert safety_manager.safety_config['risk_thresholds']['heart_rate'] == 180
    assert 'medical_emergency' in safety_manager.safety_config['emergency_procedures']

def test_safety_validation(safety_manager):
    """Test safety data validation."""
    valid_data = {
        'activity_id': 'act1',
        'student_id': 'student1',
        'heart_rate': 120,
        'temperature': 22
    }
    
    assert safety_manager._validate_safety_data(valid_data) is True
    
    invalid_data = valid_data.copy()
    invalid_data['heart_rate'] = 200  # Above threshold
    assert safety_manager._validate_safety_data(invalid_data) is False

def test_safety_notification(safety_manager, mock_activity_data):
    """Test safety notification functionality."""
    with patch('app.services.notification_service.send_notification') as mock_send:
        safety_manager.send_safety_notification(
            'High heart rate detected',
            'warning',
            mock_activity_data
        )
        mock_send.assert_called_once()

def test_safety_documentation(safety_manager, mock_incident_data):
    """Test safety documentation functionality."""
    with patch('reportlab.pdfgen.canvas.Canvas') as mock_canvas:
        safety_manager.document_safety_incident(mock_incident_data, 'incident_report.pdf')
        mock_canvas.assert_called_once() 