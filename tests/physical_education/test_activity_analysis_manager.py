import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from app.services.physical_education.services.activity_analysis_manager import ActivityAnalysisManager

@pytest.fixture
def analysis_manager():
    manager = ActivityAnalysisManager()
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

def test_initialization(analysis_manager):
    """Test proper initialization of ActivityAnalysisManager."""
    assert analysis_manager.analysis_config is not None
    assert isinstance(analysis_manager.analysis_config, dict)
    assert 'metrics' in analysis_manager.analysis_config
    assert 'thresholds' in analysis_manager.analysis_config
    assert 'analysis_methods' in analysis_manager.analysis_config

def test_analyze_activity_performance(analysis_manager, mock_activity_data):
    """Test activity performance analysis."""
    analysis = analysis_manager.analyze_activity_performance(mock_activity_data)
    assert 'performance_metrics' in analysis
    assert 'trends' in analysis
    assert 'improvement_areas' in analysis
    assert 'recommendations' in analysis

def test_analyze_activity_patterns(analysis_manager, mock_activity_data):
    """Test activity pattern analysis."""
    patterns = analysis_manager.analyze_activity_patterns(mock_activity_data)
    assert 'frequency_distribution' in patterns
    assert 'time_patterns' in patterns
    assert 'category_distribution' in patterns
    assert 'correlations' in patterns

def test_analyze_student_progress(analysis_manager, mock_activity_data, mock_student_data):
    """Test student progress analysis."""
    progress = analysis_manager.analyze_student_progress(mock_activity_data, mock_student_data)
    assert 'progress_metrics' in progress
    assert 'improvement_rate' in progress
    assert 'goal_achievement' in progress
    assert 'consistency' in progress

def test_analyze_activity_effectiveness(analysis_manager, mock_activity_data):
    """Test activity effectiveness analysis."""
    effectiveness = analysis_manager.analyze_activity_effectiveness(mock_activity_data)
    assert 'effectiveness_score' in effectiveness
    assert 'impact_metrics' in effectiveness
    assert 'efficiency_metrics' in effectiveness
    assert 'recommendations' in effectiveness

def test_analyze_activity_safety(analysis_manager, mock_activity_data):
    """Test activity safety analysis."""
    safety = analysis_manager.analyze_activity_safety(mock_activity_data)
    assert 'risk_assessment' in safety
    assert 'safety_metrics' in safety
    assert 'warning_signs' in safety
    assert 'preventive_measures' in safety

def test_analyze_activity_engagement(analysis_manager, mock_activity_data):
    """Test activity engagement analysis."""
    engagement = analysis_manager.analyze_activity_engagement(mock_activity_data)
    assert 'engagement_score' in engagement
    assert 'participation_metrics' in engagement
    assert 'motivation_indicators' in engagement
    assert 'improvement_suggestions' in engagement

def test_analyze_activity_goals(analysis_manager, mock_activity_data, mock_student_data):
    """Test activity goal analysis."""
    goals = analysis_manager.analyze_activity_goals(mock_activity_data, mock_student_data)
    assert 'goal_progress' in goals
    assert 'achievement_rate' in goals
    assert 'remaining_goals' in goals
    assert 'goal_recommendations' in goals

def test_analyze_activity_skills(analysis_manager, mock_activity_data):
    """Test activity skill analysis."""
    skills = analysis_manager.analyze_activity_skills(mock_activity_data)
    assert 'skill_levels' in skills
    assert 'skill_progress' in skills
    assert 'skill_gaps' in skills
    assert 'skill_recommendations' in skills

def test_analyze_activity_health(analysis_manager, mock_activity_data):
    """Test activity health analysis."""
    health = analysis_manager.analyze_activity_health(mock_activity_data)
    assert 'health_metrics' in health
    assert 'fitness_level' in health
    assert 'health_risks' in health
    assert 'health_recommendations' in health

def test_analyze_activity_teamwork(analysis_manager, mock_activity_data):
    """Test activity teamwork analysis."""
    teamwork = analysis_manager.analyze_activity_teamwork(mock_activity_data)
    assert 'teamwork_score' in teamwork
    assert 'collaboration_metrics' in teamwork
    assert 'leadership_indicators' in teamwork
    assert 'teamwork_recommendations' in teamwork

def test_analyze_activity_adaptability(analysis_manager, mock_activity_data):
    """Test activity adaptability analysis."""
    adaptability = analysis_manager.analyze_activity_adaptability(mock_activity_data)
    assert 'adaptability_score' in adaptability
    assert 'flexibility_metrics' in adaptability
    assert 'response_patterns' in adaptability
    assert 'adaptability_recommendations' in adaptability

def test_analyze_activity_creativity(analysis_manager, mock_activity_data):
    """Test activity creativity analysis."""
    creativity = analysis_manager.analyze_activity_creativity(mock_activity_data)
    assert 'creativity_score' in creativity
    assert 'innovation_metrics' in creativity
    assert 'problem_solving' in creativity
    assert 'creativity_recommendations' in creativity

def test_analyze_activity_resilience(analysis_manager, mock_activity_data):
    """Test activity resilience analysis."""
    resilience = analysis_manager.analyze_activity_resilience(mock_activity_data)
    assert 'resilience_score' in resilience
    assert 'recovery_metrics' in resilience
    assert 'stress_response' in resilience
    assert 'resilience_recommendations' in resilience

def test_analyze_activity_leadership(analysis_manager, mock_activity_data):
    """Test activity leadership analysis."""
    leadership = analysis_manager.analyze_activity_leadership(mock_activity_data)
    assert 'leadership_score' in leadership
    assert 'leadership_metrics' in leadership
    assert 'influence_patterns' in leadership
    assert 'leadership_recommendations' in leadership

def test_analyze_activity_sportsmanship(analysis_manager, mock_activity_data):
    """Test activity sportsmanship analysis."""
    sportsmanship = analysis_manager.analyze_activity_sportsmanship(mock_activity_data)
    assert 'sportsmanship_score' in sportsmanship
    assert 'fair_play_metrics' in sportsmanship
    assert 'attitude_indicators' in sportsmanship
    assert 'sportsmanship_recommendations' in sportsmanship

def test_error_handling(analysis_manager):
    """Test error handling in analysis operations."""
    with pytest.raises(Exception):
        analysis_manager.analyze_activity_performance(None)
    
    with pytest.raises(Exception):
        analysis_manager.analyze_activity_patterns(pd.DataFrame())
    
    with pytest.raises(Exception):
        analysis_manager.analyze_student_progress(None, None)

def test_analysis_configuration(analysis_manager):
    """Test analysis configuration functionality."""
    analysis_manager.configure_analysis(
        metrics=['performance', 'safety', 'engagement'],
        thresholds={
            'performance': 70,
            'safety': 80,
            'engagement': 75
        },
        analysis_methods=['trend_analysis', 'pattern_recognition', 'predictive_modeling']
    )
    
    assert 'performance' in analysis_manager.analysis_config['metrics']
    assert analysis_manager.analysis_config['thresholds']['performance'] == 70
    assert 'trend_analysis' in analysis_manager.analysis_config['analysis_methods']

def test_analysis_export(analysis_manager, mock_activity_data):
    """Test analysis export functionality."""
    analysis = analysis_manager.analyze_activity_performance(mock_activity_data)
    
    with patch('pandas.DataFrame.to_csv') as mock_to_csv:
        analysis_manager.export_analysis(analysis, 'csv', 'analysis.csv')
        mock_to_csv.assert_called_once()
    
    with patch('reportlab.pdfgen.canvas.Canvas') as mock_canvas:
        analysis_manager.export_analysis(analysis, 'pdf', 'analysis.pdf')
        mock_canvas.assert_called_once()

def test_analysis_visualization(analysis_manager, mock_activity_data):
    """Test analysis visualization functionality."""
    analysis = analysis_manager.analyze_activity_performance(mock_activity_data)
    
    with patch('matplotlib.pyplot.figure') as mock_figure:
        visualization = analysis_manager.visualize_analysis(analysis)
        mock_figure.assert_called_once()
        assert visualization is not None 