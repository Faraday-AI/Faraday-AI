import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from app.services.physical_education.services.assessment_system import AssessmentSystem

@pytest.fixture
def assessment_system():
    system = AssessmentSystem()
    yield system

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
def mock_assessment_data():
    return {
        'assessment_id': 'assess1',
        'student_id': 'student1',
        'type': 'fitness_test',
        'date': datetime.now(),
        'components': {
            'endurance': {
                'score': 85,
                'max_score': 100,
                'metrics': ['distance', 'time', 'heart_rate']
            },
            'strength': {
                'score': 75,
                'max_score': 100,
                'metrics': ['reps', 'weight', 'form']
            },
            'flexibility': {
                'score': 90,
                'max_score': 100,
                'metrics': ['range', 'form', 'balance']
            }
        },
        'overall_score': 83.3,
        'notes': 'Good performance overall, needs improvement in strength'
    }

def test_initialization(assessment_system):
    """Test proper initialization of AssessmentSystem."""
    assert assessment_system.assessment_config is not None
    assert isinstance(assessment_system.assessment_config, dict)
    assert 'assessment_types' in assessment_system.assessment_config
    assert 'scoring_rules' in assessment_system.assessment_config
    assert 'grading_criteria' in assessment_system.assessment_config

def test_create_assessment(assessment_system, mock_assessment_data):
    """Test assessment creation functionality."""
    assessment = assessment_system.create_assessment(mock_assessment_data)
    assert assessment is not None
    assert assessment['assessment_id'] == mock_assessment_data['assessment_id']
    assert assessment['student_id'] == mock_assessment_data['student_id']
    assert assessment['type'] == mock_assessment_data['type']

def test_update_assessment(assessment_system, mock_assessment_data):
    """Test assessment update functionality."""
    assessment = assessment_system.create_assessment(mock_assessment_data)
    
    updated_data = mock_assessment_data.copy()
    updated_data['components']['strength']['score'] = 80
    updated_data['overall_score'] = 85.0
    
    updated_assessment = assessment_system.update_assessment(
        assessment['assessment_id'],
        updated_data
    )
    assert updated_assessment['components']['strength']['score'] == 80
    assert updated_assessment['overall_score'] == 85.0

def test_delete_assessment(assessment_system, mock_assessment_data):
    """Test assessment deletion functionality."""
    assessment = assessment_system.create_assessment(mock_assessment_data)
    
    result = assessment_system.delete_assessment(assessment['assessment_id'])
    assert result is True
    
    with pytest.raises(Exception):
        assessment_system.get_assessment(assessment['assessment_id'])

def test_get_assessment(assessment_system, mock_assessment_data):
    """Test assessment retrieval functionality."""
    assessment = assessment_system.create_assessment(mock_assessment_data)
    
    retrieved_assessment = assessment_system.get_assessment(assessment['assessment_id'])
    assert retrieved_assessment['assessment_id'] == assessment['assessment_id']
    assert retrieved_assessment['student_id'] == assessment['student_id']

def test_list_assessments(assessment_system, mock_assessment_data):
    """Test assessment listing functionality."""
    assessment1 = assessment_system.create_assessment(mock_assessment_data)
    assessment2_data = mock_assessment_data.copy()
    assessment2_data['assessment_id'] = 'assess2'
    assessment2 = assessment_system.create_assessment(assessment2_data)
    
    assessments = assessment_system.list_assessments()
    assert len(assessments) == 2
    
    filtered_assessments = assessment_system.list_assessments(student_id='student1')
    assert len(filtered_assessments) == 2

def test_calculate_assessment_score(assessment_system, mock_assessment_data):
    """Test assessment score calculation."""
    assessment = assessment_system.create_assessment(mock_assessment_data)
    score = assessment_system.calculate_assessment_score(assessment)
    assert score is not None
    assert isinstance(score, float)
    assert 0 <= score <= 100

def test_generate_assessment_report(assessment_system, mock_assessment_data):
    """Test assessment report generation."""
    assessment = assessment_system.create_assessment(mock_assessment_data)
    report = assessment_system.generate_assessment_report(assessment)
    assert 'summary' in report
    assert 'component_scores' in report
    assert 'strengths' in report
    assert 'areas_for_improvement' in report
    assert 'recommendations' in report

def test_analyze_assessment_trends(assessment_system, mock_assessment_data):
    """Test assessment trend analysis."""
    assessment1 = assessment_system.create_assessment(mock_assessment_data)
    assessment2_data = mock_assessment_data.copy()
    assessment2_data['assessment_id'] = 'assess2'
    assessment2_data['date'] = datetime.now() + timedelta(days=30)
    assessment2 = assessment_system.create_assessment(assessment2_data)
    
    trends = assessment_system.analyze_assessment_trends('student1')
    assert 'progress' in trends
    assert 'improvement_areas' in trends
    assert 'consistency' in trends
    assert 'predictions' in trends

def test_compare_assessments(assessment_system, mock_assessment_data):
    """Test assessment comparison functionality."""
    assessment1 = assessment_system.create_assessment(mock_assessment_data)
    assessment2_data = mock_assessment_data.copy()
    assessment2_data['assessment_id'] = 'assess2'
    assessment2_data['components']['strength']['score'] = 85
    assessment2 = assessment_system.create_assessment(assessment2_data)
    
    comparison = assessment_system.compare_assessments(
        assessment1['assessment_id'],
        assessment2['assessment_id']
    )
    assert 'score_differences' in comparison
    assert 'improvements' in comparison
    assert 'regressions' in comparison
    assert 'overall_change' in comparison

def test_generate_assessment_recommendations(assessment_system, mock_assessment_data):
    """Test assessment recommendation generation."""
    assessment = assessment_system.create_assessment(mock_assessment_data)
    recommendations = assessment_system.generate_assessment_recommendations(assessment)
    assert 'training_recommendations' in recommendations
    assert 'diet_recommendations' in recommendations
    assert 'recovery_recommendations' in recommendations
    assert 'goal_suggestions' in recommendations

def test_validate_assessment_data(assessment_system):
    """Test assessment data validation."""
    valid_data = {
        'assessment_id': 'assess1',
        'student_id': 'student1',
        'type': 'fitness_test',
        'components': {
            'endurance': {'score': 85, 'max_score': 100}
        }
    }
    
    assert assessment_system._validate_assessment_data(valid_data) is True
    
    invalid_data = valid_data.copy()
    invalid_data['components']['endurance']['score'] = 150  # Score above maximum
    assert assessment_system._validate_assessment_data(invalid_data) is False

def test_error_handling(assessment_system):
    """Test error handling in assessment operations."""
    with pytest.raises(Exception):
        assessment_system.create_assessment(None)
    
    with pytest.raises(Exception):
        assessment_system.update_assessment('nonexistent_id', {})
    
    with pytest.raises(Exception):
        assessment_system.delete_assessment('nonexistent_id')
    
    with pytest.raises(Exception):
        assessment_system.get_assessment('nonexistent_id')

def test_assessment_configuration(assessment_system):
    """Test assessment configuration functionality."""
    assessment_system.configure_assessment(
        assessment_types=['fitness_test', 'skill_test', 'performance_test'],
        scoring_rules={
            'weighted_average': True,
            'component_weights': {'endurance': 0.4, 'strength': 0.3, 'flexibility': 0.3}
        },
        grading_criteria={
            'A': 90,
            'B': 80,
            'C': 70,
            'D': 60
        }
    )
    
    assert 'fitness_test' in assessment_system.assessment_config['assessment_types']
    assert assessment_system.assessment_config['scoring_rules']['weighted_average'] is True
    assert assessment_system.assessment_config['grading_criteria']['A'] == 90

def test_assessment_export(assessment_system, mock_assessment_data):
    """Test assessment export functionality."""
    assessment = assessment_system.create_assessment(mock_assessment_data)
    
    with patch('pandas.DataFrame.to_csv') as mock_to_csv:
        assessment_system.export_assessment(assessment, 'csv', 'assessment.csv')
        mock_to_csv.assert_called_once()
    
    with patch('reportlab.pdfgen.canvas.Canvas') as mock_canvas:
        assessment_system.export_assessment(assessment, 'pdf', 'assessment.pdf')
        mock_canvas.assert_called_once()

def test_assessment_import(assessment_system):
    """Test assessment import functionality."""
    mock_data = pd.DataFrame({
        'assessment_id': ['assess1', 'assess2'],
        'student_id': ['student1', 'student1'],
        'type': ['fitness_test', 'skill_test'],
        'score': [85, 90]
    })
    
    with patch('pandas.read_csv', return_value=mock_data):
        result = assessment_system.import_assessments('dummy_path.csv')
        assert len(result['successful']) == 2
        assert len(result['failed']) == 0

def test_assessment_notification(assessment_system, mock_assessment_data):
    """Test assessment notification functionality."""
    assessment = assessment_system.create_assessment(mock_assessment_data)
    
    with patch('app.services.notification_service.send_notification') as mock_send:
        assessment_system.send_assessment_notification(assessment)
        mock_send.assert_called_once() 