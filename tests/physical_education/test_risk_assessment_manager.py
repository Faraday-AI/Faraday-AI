import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, AsyncMock
from app.services.physical_education.services.risk_assessment_manager import RiskAssessmentManager

@pytest.fixture
def risk_manager():
    """Create RiskAssessmentManager instance for testing."""
    return RiskAssessmentManager()

@pytest.fixture
def sample_activity_data():
    """Create sample activity data for testing."""
    dates = pd.date_range(start='2024-01-01', end='2024-03-31', freq='D')
    np.random.seed(42)
    
    data = {
        'date': dates,
        'activity_type': np.random.choice(['Running', 'Jumping', 'Swimming', 'Team Sports'], len(dates)),
        'intensity': np.random.choice(['Low', 'Medium', 'High'], len(dates)),
        'duration_minutes': np.random.randint(30, 120, len(dates)),
        'participants': np.random.randint(10, 50, len(dates)),
        'weather_conditions': np.random.choice(['Clear', 'Rain', 'Wind', 'Hot'], len(dates)),
        'equipment_condition': np.random.choice(['Good', 'Fair', 'Poor'], len(dates))
    }
    return pd.DataFrame(data)

@pytest.fixture
def sample_student_data():
    """Create sample student data for testing."""
    students = [
        {
            'student_id': 's1',
            'age': 15,
            'fitness_level': 'Intermediate',
            'medical_conditions': ['None'],
            'allergies': ['None'],
            'previous_injuries': ['None']
        },
        {
            'student_id': 's2',
            'age': 16,
            'fitness_level': 'Advanced',
            'medical_conditions': ['Asthma'],
            'allergies': ['Peanuts'],
            'previous_injuries': ['Sprained ankle']
        }
    ]
    return students

@pytest.mark.asyncio
async def test_assess_activity_risk(risk_manager, sample_activity_data):
    """Test assessment of activity risk."""
    risk_assessment = await risk_manager.assess_activity_risk(
        activity_data=sample_activity_data,
        activity_type='Running',
        intensity='High'
    )
    
    assert risk_assessment is not None
    assert 'risk_level' in risk_assessment
    assert 'risk_factors' in risk_assessment
    assert 'mitigation_strategies' in risk_assessment
    assert 'recommendations' in risk_assessment

@pytest.mark.asyncio
async def test_assess_student_risk(risk_manager, sample_student_data):
    """Test assessment of student risk."""
    risk_assessment = await risk_manager.assess_student_risk(
        student_data=sample_student_data[0],
        activity_type='Running',
        intensity='High'
    )
    
    assert risk_assessment is not None
    assert 'risk_level' in risk_assessment
    assert 'medical_concerns' in risk_assessment
    assert 'activity_restrictions' in risk_assessment
    assert 'precautions' in risk_assessment

@pytest.mark.asyncio
async def test_assess_environmental_risk(risk_manager):
    """Test assessment of environmental risk."""
    environmental_data = {
        'temperature': 32,
        'humidity': 80,
        'air_quality': 'Moderate',
        'weather_conditions': 'Hot',
        'surface_condition': 'Dry'
    }
    
    risk_assessment = await risk_manager.assess_environmental_risk(
        environmental_data=environmental_data,
        activity_type='Running'
    )
    
    assert risk_assessment is not None
    assert 'risk_level' in risk_assessment
    assert 'environmental_factors' in risk_assessment
    assert 'safety_measures' in risk_assessment

@pytest.mark.asyncio
async def test_assess_equipment_risk(risk_manager):
    """Test assessment of equipment risk."""
    equipment_data = {
        'equipment_id': 'eq1',
        'type': 'Treadmill',
        'condition': 'Fair',
        'last_inspection': datetime.now() - timedelta(days=30),
        'maintenance_history': ['Regular maintenance', 'Belt replacement']
    }
    
    risk_assessment = await risk_manager.assess_equipment_risk(
        equipment_data=equipment_data,
        activity_type='Running'
    )
    
    assert risk_assessment is not None
    assert 'risk_level' in risk_assessment
    assert 'equipment_condition' in risk_assessment
    assert 'maintenance_needs' in risk_assessment
    assert 'safety_checks' in risk_assessment

@pytest.mark.asyncio
async def test_assess_group_risk(risk_manager, sample_student_data):
    """Test assessment of group risk."""
    risk_assessment = await risk_manager.assess_group_risk(
        students=sample_student_data,
        activity_type='Team Sports',
        intensity='Medium'
    )
    
    assert risk_assessment is not None
    assert 'group_risk_level' in risk_assessment
    assert 'individual_risks' in risk_assessment
    assert 'group_dynamics' in risk_assessment
    assert 'supervision_needs' in risk_assessment

@pytest.mark.asyncio
async def test_generate_risk_report(risk_manager, sample_activity_data, sample_student_data):
    """Test generation of comprehensive risk report."""
    risk_report = await risk_manager.generate_risk_report(
        activity_data=sample_activity_data,
        student_data=sample_student_data,
        activity_type='Running',
        intensity='High'
    )
    
    assert risk_report is not None
    assert 'activity_risk' in risk_report
    assert 'student_risks' in risk_report
    assert 'environmental_risk' in risk_report
    assert 'equipment_risk' in risk_report
    assert 'group_risk' in risk_report
    assert 'overall_risk_level' in risk_report
    assert 'recommendations' in risk_report

@pytest.mark.asyncio
async def test_update_risk_assessment(risk_manager, sample_activity_data):
    """Test updating risk assessment with new data."""
    initial_assessment = await risk_manager.assess_activity_risk(
        activity_data=sample_activity_data,
        activity_type='Running',
        intensity='High'
    )
    
    updated_assessment = await risk_manager.update_risk_assessment(
        current_assessment=initial_assessment,
        new_data={'weather_conditions': 'Rain'},
        activity_type='Running'
    )
    
    assert updated_assessment is not None
    assert updated_assessment != initial_assessment
    assert 'risk_level' in updated_assessment
    assert 'updated_factors' in updated_assessment

@pytest.mark.asyncio
async def test_error_handling(risk_manager):
    """Test error handling in risk assessment."""
    # Test with invalid activity type
    with pytest.raises(ValueError):
        await risk_manager.assess_activity_risk(
            activity_data=pd.DataFrame(),
            activity_type='Invalid',
            intensity='High'
        )
    
    # Test with invalid intensity
    with pytest.raises(ValueError):
        await risk_manager.assess_activity_risk(
            activity_data=pd.DataFrame(),
            activity_type='Running',
            intensity='Invalid'
        )
    
    # Test with missing data
    with pytest.raises(ValueError):
        await risk_manager.assess_student_risk(
            student_data={},
            activity_type='Running',
            intensity='High'
        )

@pytest.mark.asyncio
async def test_risk_calculation(risk_manager, sample_activity_data):
    """Test risk calculation methods."""
    risk_score = await risk_manager.calculate_risk_score(
        activity_data=sample_activity_data,
        activity_type='Running',
        intensity='High'
    )
    
    assert risk_score is not None
    assert isinstance(risk_score, (int, float))
    assert 0 <= risk_score <= 100

@pytest.mark.asyncio
async def test_risk_thresholds(risk_manager):
    """Test risk threshold validation."""
    thresholds = await risk_manager.get_risk_thresholds('Running')
    
    assert thresholds is not None
    assert 'low' in thresholds
    assert 'medium' in thresholds
    assert 'high' in thresholds
    assert thresholds['low'] < thresholds['medium'] < thresholds['high']

@pytest.mark.asyncio
async def test_risk_mitigation(risk_manager, sample_activity_data):
    """Test risk mitigation strategies."""
    mitigation = await risk_manager.get_mitigation_strategies(
        activity_data=sample_activity_data,
        activity_type='Running',
        risk_level='High'
    )
    
    assert mitigation is not None
    assert 'strategies' in mitigation
    assert 'implementation_steps' in mitigation
    assert 'monitoring_plan' in mitigation

@pytest.mark.asyncio
async def test_risk_monitoring(risk_manager, sample_activity_data):
    """Test risk monitoring functionality."""
    monitoring_plan = await risk_manager.create_monitoring_plan(
        activity_data=sample_activity_data,
        activity_type='Running',
        risk_level='High'
    )
    
    assert monitoring_plan is not None
    assert 'checkpoints' in monitoring_plan
    assert 'indicators' in monitoring_plan
    assert 'response_plan' in monitoring_plan

@pytest.mark.asyncio
async def test_risk_documentation(risk_manager, sample_activity_data):
    """Test risk documentation functionality."""
    documentation = await risk_manager.generate_risk_documentation(
        activity_data=sample_activity_data,
        activity_type='Running',
        intensity='High'
    )
    
    assert documentation is not None
    assert 'assessment_summary' in documentation
    assert 'risk_factors' in documentation
    assert 'mitigation_plan' in documentation
    assert 'monitoring_protocol' in documentation 