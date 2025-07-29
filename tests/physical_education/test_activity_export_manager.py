import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from app.services.physical_education.activity_export_manager import ActivityExportManager

@pytest.fixture
def export_manager():
    manager = ActivityExportManager()
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
def mock_analysis_data():
    return {
        'performance_metrics': {
            'average_score': 85.5,
            'max_score': 95.0,
            'min_score': 75.0
        },
        'trends': {
            'score_trend': 'increasing',
            'improvement_rate': 2.5
        },
        'recommendations': [
            'Focus on strength training',
            'Increase cardio duration'
        ]
    }

def test_initialization(export_manager):
    """Test proper initialization of ActivityExportManager."""
    assert export_manager.export_config is not None
    assert isinstance(export_manager.export_config, dict)
    assert 'formats' in export_manager.export_config
    assert 'compression' in export_manager.export_config
    assert 'batch_size' in export_manager.export_config

def test_export_activity_data_csv(export_manager, mock_activity_data):
    """Test exporting activity data to CSV format."""
    with patch('pandas.DataFrame.to_csv') as mock_to_csv:
        export_manager.export_activity_data(mock_activity_data, 'csv', 'activities.csv')
        mock_to_csv.assert_called_once()
        assert mock_to_csv.call_args[1]['index'] is False

def test_export_activity_data_excel(export_manager, mock_activity_data):
    """Test exporting activity data to Excel format."""
    with patch('pandas.DataFrame.to_excel') as mock_to_excel:
        export_manager.export_activity_data(mock_activity_data, 'excel', 'activities.xlsx')
        mock_to_excel.assert_called_once()
        assert mock_to_excel.call_args[1]['index'] is False

def test_export_activity_data_json(export_manager, mock_activity_data):
    """Test exporting activity data to JSON format."""
    with patch('pandas.DataFrame.to_json') as mock_to_json:
        export_manager.export_activity_data(mock_activity_data, 'json', 'activities.json')
        mock_to_json.assert_called_once()
        assert mock_to_json.call_args[1]['orient'] == 'records'

def test_export_analysis_report_pdf(export_manager, mock_analysis_data):
    """Test exporting analysis report to PDF format."""
    with patch('reportlab.pdfgen.canvas.Canvas') as mock_canvas:
        export_manager.export_analysis_report(mock_analysis_data, 'pdf', 'analysis.pdf')
        mock_canvas.assert_called_once()

def test_export_analysis_report_html(export_manager, mock_analysis_data):
    """Test exporting analysis report to HTML format."""
    with patch('jinja2.Template.render') as mock_render:
        export_manager.export_analysis_report(mock_analysis_data, 'html', 'analysis.html')
        mock_render.assert_called_once()

def test_export_analysis_report_docx(export_manager, mock_analysis_data):
    """Test exporting analysis report to DOCX format."""
    with patch('docx.Document') as mock_document:
        export_manager.export_analysis_report(mock_analysis_data, 'docx', 'analysis.docx')
        mock_document.assert_called_once()

def test_export_visualization_png(export_manager, mock_activity_data):
    """Test exporting visualization to PNG format."""
    with patch('matplotlib.pyplot.savefig') as mock_savefig:
        export_manager.export_visualization(mock_activity_data, 'png', 'visualization.png')
        mock_savefig.assert_called_once()

def test_export_visualization_svg(export_manager, mock_activity_data):
    """Test exporting visualization to SVG format."""
    with patch('matplotlib.pyplot.savefig') as mock_savefig:
        export_manager.export_visualization(mock_activity_data, 'svg', 'visualization.svg')
        mock_savefig.assert_called_once()

def test_export_progress_report(export_manager, mock_activity_data, mock_analysis_data):
    """Test exporting progress report."""
    with patch('reportlab.pdfgen.canvas.Canvas') as mock_canvas:
        export_manager.export_progress_report(mock_activity_data, mock_analysis_data, 'progress.pdf')
        mock_canvas.assert_called_once()

def test_export_achievement_certificate(export_manager, mock_activity_data):
    """Test exporting achievement certificate."""
    with patch('reportlab.pdfgen.canvas.Canvas') as mock_canvas:
        export_manager.export_achievement_certificate(mock_activity_data, 'certificate.pdf')
        mock_canvas.assert_called_once()

def test_export_health_report(export_manager, mock_activity_data):
    """Test exporting health report."""
    with patch('reportlab.pdfgen.canvas.Canvas') as mock_canvas:
        export_manager.export_health_report(mock_activity_data, 'health.pdf')
        mock_canvas.assert_called_once()

def test_export_compression(export_manager, mock_activity_data):
    """Test export compression functionality."""
    with patch('zipfile.ZipFile') as mock_zip:
        export_manager.export_activity_data(mock_activity_data, 'csv', 'activities.csv', compress=True)
        mock_zip.assert_called_once()

def test_batch_export(export_manager, mock_activity_data):
    """Test batch export functionality."""
    with patch('pandas.DataFrame.to_csv') as mock_to_csv:
        export_manager.batch_export([mock_activity_data], 'csv', 'batch_export')
        assert mock_to_csv.call_count == 1

def test_error_handling(export_manager, mock_activity_data):
    """Test error handling in export operations."""
    with pytest.raises(Exception):
        export_manager.export_activity_data(None, 'csv', 'test.csv')
    
    with pytest.raises(Exception):
        export_manager.export_activity_data(mock_activity_data, 'invalid_format', 'test.txt')
    
    with pytest.raises(Exception):
        export_manager.export_analysis_report(None, 'pdf', 'test.pdf')

def test_export_configuration(export_manager):
    """Test export configuration functionality."""
    export_manager.configure_export(
        formats=['csv', 'excel', 'pdf'],
        compression=True,
        batch_size=100,
        default_format='csv'
    )
    
    assert 'csv' in export_manager.export_config['formats']
    assert export_manager.export_config['compression'] is True
    assert export_manager.export_config['batch_size'] == 100
    assert export_manager.export_config['default_format'] == 'csv'

def test_export_validation(export_manager, mock_activity_data):
    """Test export data validation."""
    assert export_manager._validate_export_data(mock_activity_data) is True
    
    invalid_data = pd.DataFrame()
    assert export_manager._validate_export_data(invalid_data) is False

def test_export_path_handling(export_manager, mock_activity_data):
    """Test export path handling."""
    with patch('os.path.exists') as mock_exists, \
         patch('os.makedirs') as mock_makedirs:
        mock_exists.return_value = False
        export_manager.export_activity_data(mock_activity_data, 'csv', 'test/activities.csv')
        mock_makedirs.assert_called_once()

def test_export_performance(export_manager, mock_activity_data):
    """Test export performance with large datasets."""
    large_data = pd.concat([mock_activity_data] * 1000)
    
    with patch('pandas.DataFrame.to_csv') as mock_to_csv:
        export_manager.export_activity_data(large_data, 'csv', 'large_activities.csv')
        mock_to_csv.assert_called_once() 