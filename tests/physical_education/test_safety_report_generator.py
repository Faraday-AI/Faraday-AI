import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, AsyncMock
from app.services.physical_education.services.safety_report_generator import SafetyReportGenerator

@pytest.fixture
def report_generator():
    """Create SafetyReportGenerator instance for testing."""
    return SafetyReportGenerator()

@pytest.fixture
def sample_safety_data():
    """Create sample safety data for testing."""
    dates = pd.date_range(start='2024-01-01', end='2024-03-31', freq='D')
    np.random.seed(42)
    
    data = {
        'date': dates,
        'incident_type': np.random.choice(['Fall', 'Collision', 'Equipment', 'Weather', 'Other'], len(dates)),
        'severity': np.random.choice(['Low', 'Medium', 'High'], len(dates)),
        'location': np.random.choice(['Gym', 'Field', 'Track', 'Pool'], len(dates)),
        'activity': np.random.choice(['Running', 'Jumping', 'Swimming', 'Team Sports'], len(dates)),
        'weather_conditions': np.random.choice(['Clear', 'Rain', 'Wind', 'Hot'], len(dates)),
        'equipment_condition': np.random.choice(['Good', 'Fair', 'Poor'], len(dates))
    }
    return pd.DataFrame(data)

@pytest.fixture
def sample_incident_data():
    """Create sample incident data for testing."""
    incidents = [
        {
            'id': 'inc1',
            'date': datetime.now(),
            'type': 'Fall',
            'severity': 'Medium',
            'description': 'Student slipped on wet floor',
            'action_taken': 'First aid applied',
            'preventive_measures': 'Floor cleaned and warning signs posted'
        },
        {
            'id': 'inc2',
            'date': datetime.now() - timedelta(days=1),
            'type': 'Equipment',
            'severity': 'Low',
            'description': 'Broken equipment reported',
            'action_taken': 'Equipment replaced',
            'preventive_measures': 'Regular equipment checks scheduled'
        }
    ]
    return incidents

@pytest.mark.asyncio
async def test_generate_safety_report(report_generator, sample_safety_data):
    """Test generation of safety report."""
    report = await report_generator.generate_safety_report(
        safety_data=sample_safety_data,
        start_date='2024-01-01',
        end_date='2024-03-31'
    )
    
    assert report is not None
    assert 'summary' in report
    assert 'trends' in report
    assert 'recommendations' in report
    assert 'statistics' in report

@pytest.mark.asyncio
async def test_generate_incident_report(report_generator, sample_incident_data):
    """Test generation of incident report."""
    report = await report_generator.generate_incident_report(
        incidents=sample_incident_data,
        start_date='2024-01-01',
        end_date='2024-03-31'
    )
    
    assert report is not None
    assert 'incident_summary' in report
    assert 'trend_analysis' in report
    assert 'preventive_measures' in report
    assert 'action_items' in report

@pytest.mark.asyncio
async def test_generate_equipment_safety_report(report_generator):
    """Test generation of equipment safety report."""
    equipment_data = {
        'equipment_id': ['eq1', 'eq2', 'eq3'],
        'last_inspection': [datetime.now() - timedelta(days=30),
                          datetime.now() - timedelta(days=60),
                          datetime.now() - timedelta(days=90)],
        'condition': ['Good', 'Fair', 'Poor'],
        'maintenance_needed': [False, True, True]
    }
    
    report = await report_generator.generate_equipment_safety_report(
        equipment_data=pd.DataFrame(equipment_data)
    )
    
    assert report is not None
    assert 'equipment_status' in report
    assert 'maintenance_needs' in report
    assert 'inspection_schedule' in report

@pytest.mark.asyncio
async def test_generate_environmental_safety_report(report_generator):
    """Test generation of environmental safety report."""
    environmental_data = {
        'date': pd.date_range(start='2024-01-01', end='2024-01-31', freq='D'),
        'temperature': np.random.uniform(15, 35, 31),
        'humidity': np.random.uniform(30, 90, 31),
        'air_quality': np.random.choice(['Good', 'Moderate', 'Poor'], 31),
        'weather_conditions': np.random.choice(['Clear', 'Rain', 'Wind', 'Hot'], 31)
    }
    
    report = await report_generator.generate_environmental_safety_report(
        environmental_data=pd.DataFrame(environmental_data)
    )
    
    assert report is not None
    assert 'environmental_conditions' in report
    assert 'safety_concerns' in report
    assert 'recommendations' in report

@pytest.mark.asyncio
async def test_generate_student_safety_report(report_generator):
    """Test generation of student safety report."""
    student_data = {
        'student_id': ['s1', 's2', 's3'],
        'medical_conditions': ['None', 'Asthma', 'None'],
        'allergies': ['None', 'Peanuts', 'None'],
        'emergency_contacts': ['Parent1', 'Parent2', 'Parent3'],
        'last_medical_check': [datetime.now() - timedelta(days=30),
                             datetime.now() - timedelta(days=60),
                             datetime.now() - timedelta(days=90)]
    }
    
    report = await report_generator.generate_student_safety_report(
        student_data=pd.DataFrame(student_data)
    )
    
    assert report is not None
    assert 'student_profiles' in report
    assert 'medical_concerns' in report
    assert 'emergency_preparedness' in report

@pytest.mark.asyncio
async def test_generate_comprehensive_safety_report(report_generator, sample_safety_data, sample_incident_data):
    """Test generation of comprehensive safety report."""
    report = await report_generator.generate_comprehensive_safety_report(
        safety_data=sample_safety_data,
        incidents=sample_incident_data,
        start_date='2024-01-01',
        end_date='2024-03-31'
    )
    
    assert report is not None
    assert 'executive_summary' in report
    assert 'incident_analysis' in report
    assert 'risk_assessment' in report
    assert 'action_plan' in report
    assert 'appendices' in report

@pytest.mark.asyncio
async def test_export_safety_report(report_generator, sample_safety_data):
    """Test export of safety report to different formats."""
    report = await report_generator.generate_safety_report(
        safety_data=sample_safety_data,
        start_date='2024-01-01',
        end_date='2024-03-31'
    )
    
    # Test PDF export
    pdf_path = await report_generator.export_report(report, format='pdf')
    assert pdf_path is not None
    assert pdf_path.endswith('.pdf')
    
    # Test HTML export
    html_path = await report_generator.export_report(report, format='html')
    assert html_path is not None
    assert html_path.endswith('.html')
    
    # Test DOCX export
    docx_path = await report_generator.export_report(report, format='docx')
    assert docx_path is not None
    assert docx_path.endswith('.docx')

@pytest.mark.asyncio
async def test_error_handling(report_generator):
    """Test error handling in report generation."""
    # Test with invalid data
    with pytest.raises(ValueError):
        await report_generator.generate_safety_report(
            safety_data=None,
            start_date='2024-01-01',
            end_date='2024-03-31'
        )
    
    # Test with invalid date range
    with pytest.raises(ValueError):
        await report_generator.generate_safety_report(
            safety_data=pd.DataFrame(),
            start_date='2024-03-31',
            end_date='2024-01-01'
        )
    
    # Test with invalid export format
    with pytest.raises(ValueError):
        await report_generator.export_report({}, format='invalid')

@pytest.mark.asyncio
async def test_report_customization(report_generator, sample_safety_data):
    """Test customization options for reports."""
    # Test with custom template
    report = await report_generator.generate_safety_report(
        safety_data=sample_safety_data,
        start_date='2024-01-01',
        end_date='2024-03-31',
        template='custom'
    )
    assert report is not None
    
    # Test with custom sections
    report = await report_generator.generate_safety_report(
        safety_data=sample_safety_data,
        start_date='2024-01-01',
        end_date='2024-03-31',
        sections=['summary', 'trends']
    )
    assert report is not None
    assert 'summary' in report
    assert 'trends' in report
    assert 'recommendations' not in report

@pytest.mark.asyncio
async def test_report_validation(report_generator, sample_safety_data):
    """Test validation of generated reports."""
    report = await report_generator.generate_safety_report(
        safety_data=sample_safety_data,
        start_date='2024-01-01',
        end_date='2024-03-31'
    )
    
    validation_result = await report_generator.validate_report(report)
    assert validation_result['is_valid'] is True
    assert 'errors' in validation_result
    assert len(validation_result['errors']) == 0

@pytest.mark.asyncio
async def test_report_performance(report_generator, sample_safety_data):
    """Test performance of report generation."""
    import time
    
    start_time = time.time()
    await report_generator.generate_safety_report(
        safety_data=sample_safety_data,
        start_date='2024-01-01',
        end_date='2024-03-31'
    )
    end_time = time.time()
    
    # Report generation should take less than 5 seconds
    assert end_time - start_time < 5.0 