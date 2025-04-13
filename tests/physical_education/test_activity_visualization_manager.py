import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, AsyncMock
from app.services.physical_education.services.activity_visualization_manager import ActivityVisualizationManager
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import os
from pathlib import Path

@pytest.fixture
def visualization_manager():
    """Create ActivityVisualizationManager instance for testing."""
    return ActivityVisualizationManager()

@pytest.fixture
def sample_performance_data():
    """Create sample performance data for testing."""
    dates = pd.date_range(start='2024-01-01', end='2024-03-31', freq='D')
    np.random.seed(42)
    
    data = {
        'date': dates,
        'score': np.random.uniform(0, 100, len(dates)),
        'category': np.random.choice(['Cardio', 'Strength', 'Flexibility', 'Coordination'], len(dates)),
        'activity_type': np.random.choice(['Running', 'Jumping', 'Stretching', 'Balance'], len(dates)),
        'duration': np.random.randint(10, 60, len(dates)),
        'intensity': np.random.uniform(0.5, 1.0, len(dates))
    }
    return pd.DataFrame(data)

@pytest.fixture
def sample_skill_data():
    """Create sample skill data for testing."""
    skills = ['Dribbling', 'Shooting', 'Passing', 'Defense', 'Rebounding']
    categories = ['Ball Handling', 'Scoring', 'Team Play', 'Defense', 'Rebounding']
    
    data = {
        'skill': skills * 3,
        'score': np.random.uniform(0, 100, len(skills) * 3),
        'category': categories * 3,
        'target_score': np.random.uniform(70, 100, len(skills) * 3),
        'progress': np.random.uniform(-20, 20, len(skills) * 3)
    }
    return pd.DataFrame(data)

@pytest.mark.asyncio
async def test_generate_visualizations(visualization_manager, sample_performance_data):
    """Test visualization generation with different types."""
    student_id = "12345"
    visualizations = await visualization_manager.generate_visualizations(
        student_id=student_id,
        performance_data=sample_performance_data,
        skill_data=sample_skill_data,
        visualization_types=['performance_trend', 'category_heatmap', 'activity_distribution'],
        interactive=True,
        drill_down=True
    )
    
    assert isinstance(visualizations, list)
    assert len(visualizations) == 3
    for viz in visualizations:
        assert 'type' in viz
        assert 'data' in viz
        assert 'metadata' in viz

@pytest.mark.asyncio
async def test_performance_trend_plot(visualization_manager, sample_performance_data):
    """Test performance trend plot generation."""
    fig = visualization_manager._generate_performance_trend_plot(
        data=sample_performance_data,
        interactive=True,
        drill_down=True
    )
    
    assert fig is not None
    assert 'data' in fig
    assert 'layout' in fig
    assert 'updatemenus' in fig['layout']  # Check for drill-down buttons

@pytest.mark.asyncio
async def test_category_heatmap(visualization_manager, sample_performance_data):
    """Test category heatmap generation."""
    fig = visualization_manager._generate_category_heatmap(
        data=sample_performance_data,
        interactive=True,
        drill_down=True
    )
    
    assert fig is not None
    assert 'data' in fig
    assert 'layout' in fig
    assert 'updatemenus' in fig['layout']  # Check for drill-down buttons

@pytest.mark.asyncio
async def test_activity_distribution_plot(visualization_manager, sample_performance_data):
    """Test activity distribution plot generation."""
    fig = visualization_manager._generate_activity_distribution_plot(
        data=sample_performance_data,
        interactive=True,
        drill_down=True
    )
    
    assert fig is not None
    assert 'data' in fig
    assert 'layout' in fig
    assert 'updatemenus' in fig['layout']  # Check for drill-down buttons

@pytest.mark.asyncio
async def test_improvement_trends_plot(visualization_manager, sample_performance_data):
    """Test improvement trends plot generation."""
    fig = visualization_manager._generate_improvement_trends_plot(
        data=sample_performance_data,
        interactive=True,
        drill_down=True
    )
    
    assert fig is not None
    assert 'data' in fig
    assert 'layout' in fig
    assert 'updatemenus' in fig['layout']  # Check for drill-down buttons

@pytest.mark.asyncio
async def test_skill_analysis_plot(visualization_manager, sample_skill_data):
    """Test skill analysis plot generation."""
    fig = visualization_manager._generate_skill_analysis_plot(
        data=sample_skill_data,
        interactive=True,
        drill_down=True
    )
    
    assert fig is not None
    assert 'data' in fig
    assert 'layout' in fig
    assert 'updatemenus' in fig['layout']  # Check for drill-down buttons

@pytest.mark.asyncio
async def test_sankey_diagram(visualization_manager, sample_performance_data):
    """Test Sankey diagram generation."""
    fig = visualization_manager._generate_sankey_diagram(
        data=sample_performance_data,
        interactive=True,
        drill_down=True
    )
    
    assert fig is not None
    assert 'data' in fig
    assert 'layout' in fig
    assert 'updatemenus' in fig['layout']  # Check for drill-down buttons

@pytest.mark.asyncio
async def test_treemap(visualization_manager, sample_performance_data):
    """Test treemap generation."""
    fig = visualization_manager._generate_treemap(
        data=sample_performance_data,
        interactive=True,
        drill_down=True
    )
    
    assert fig is not None
    assert 'data' in fig
    assert 'layout' in fig
    assert 'updatemenus' in fig['layout']  # Check for drill-down buttons

@pytest.mark.asyncio
async def test_sunburst_chart(visualization_manager, sample_performance_data):
    """Test sunburst chart generation."""
    fig = visualization_manager._generate_sunburst_chart(
        data=sample_performance_data,
        interactive=True,
        drill_down=True
    )
    
    assert fig is not None
    assert 'data' in fig
    assert 'layout' in fig
    assert 'updatemenus' in fig['layout']  # Check for drill-down buttons

@pytest.mark.asyncio
async def test_violin_plot(visualization_manager, sample_performance_data):
    """Test violin plot generation."""
    fig = visualization_manager._generate_violin_plot(
        data=sample_performance_data,
        interactive=True,
        drill_down=True
    )
    
    assert fig is not None
    assert 'data' in fig
    assert 'layout' in fig
    assert 'updatemenus' in fig['layout']  # Check for drill-down buttons

@pytest.mark.asyncio
async def test_save_visualization(visualization_manager, sample_performance_data):
    """Test visualization saving functionality."""
    student_id = "12345"
    fig = visualization_manager._generate_performance_trend_plot(
        data=sample_performance_data,
        interactive=True,
        drill_down=True
    )
    
    visualization = {
        'type': 'performance_trend',
        'data': fig,
        'metadata': {
            'student_id': student_id,
            'timestamp': datetime.now().isoformat()
        }
    }
    
    output_path = await visualization_manager.save_visualization(
        visualization=visualization,
        student_id=student_id
    )
    
    assert output_path is not None
    assert isinstance(output_path, str)
    assert student_id in output_path
    assert 'performance_trend' in output_path

@pytest.mark.asyncio
async def test_theme_application(visualization_manager, sample_performance_data):
    """Test theme application to visualizations."""
    # Test with dark theme
    visualization_manager.theme = 'dark'
    fig = visualization_manager._generate_performance_trend_plot(
        data=sample_performance_data,
        interactive=True,
        drill_down=True
    )
    
    assert fig is not None
    assert 'layout' in fig
    assert 'plot_bgcolor' in fig['layout']
    assert fig['layout']['plot_bgcolor'] == '#1E1E1E'
    
    # Test with light theme
    visualization_manager.theme = 'light'
    fig = visualization_manager._generate_performance_trend_plot(
        data=sample_performance_data,
        interactive=True,
        drill_down=True
    )
    
    assert fig is not None
    assert 'layout' in fig
    assert 'plot_bgcolor' in fig['layout']
    assert fig['layout']['plot_bgcolor'] == '#FFFFFF'

@pytest.mark.asyncio
async def test_accessibility_features(visualization_manager, sample_performance_data):
    """Test accessibility features in visualizations."""
    visualization_manager.accessibility_settings = {
        'high_contrast': True,
        'screen_reader_compatible': True,
        'color_blind_friendly': True
    }
    
    fig = visualization_manager._generate_performance_trend_plot(
        data=sample_performance_data,
        interactive=True,
        drill_down=True
    )
    
    assert fig is not None
    assert 'layout' in fig
    assert 'accessibility' in fig['layout']
    assert fig['layout']['accessibility']['high_contrast'] is True
    assert fig['layout']['accessibility']['screen_reader_compatible'] is True
    assert fig['layout']['accessibility']['color_blind_friendly'] is True

@pytest.mark.asyncio
async def test_error_handling(visualization_manager):
    """Test error handling in visualization generation."""
    # Test with invalid data
    with pytest.raises(ValueError):
        await visualization_manager.generate_visualizations(
            student_id="12345",
            performance_data=None,
            skill_data=None,
            visualization_types=['invalid_type']
        )
    
    # Test with empty data
    with pytest.raises(ValueError):
        await visualization_manager.generate_visualizations(
            student_id="12345",
            performance_data=pd.DataFrame(),
            skill_data=pd.DataFrame(),
            visualization_types=['performance_trend']
        )
    
    # Test with invalid visualization type
    with pytest.raises(ValueError):
        await visualization_manager.generate_visualizations(
            student_id="12345",
            performance_data=sample_performance_data,
            skill_data=sample_skill_data,
            visualization_types=['invalid_type']
        )

def test_set_theme(visualization_manager):
    # Test setting valid theme
    visualization_manager.set_theme('dark')
    assert visualization_manager.visualization_config['current_theme'] == 'dark'
    
    # Test setting invalid theme
    with pytest.raises(KeyError):
        visualization_manager.set_theme('invalid_theme')

def test_set_accessibility(visualization_manager):
    # Test setting accessibility options
    visualization_manager.set_accessibility(
        high_contrast=True,
        screen_reader=False,
        alt_text=True
    )
    
    assert visualization_manager.visualization_config['accessibility']['high_contrast'] is True
    assert visualization_manager.visualization_config['accessibility']['screen_reader'] is False
    assert visualization_manager.visualization_config['accessibility']['alt_text'] is True

@patch('plotly.express.line')
def test_generate_performance_trend_plot(mock_line, visualization_manager, sample_performance_data):
    # Setup
    mock_fig = MagicMock(spec=go.Figure)
    mock_line.return_value = mock_fig
    
    # Test
    fig = visualization_manager._generate_performance_trend_plot(
        sample_performance_data,
        interactive=True,
        drill_down=True
    )
    
    # Verify
    assert fig == mock_fig
    mock_line.assert_called_once()

@patch('plotly.express.density_heatmap')
def test_generate_category_heatmap(mock_heatmap, visualization_manager, sample_performance_data):
    # Setup
    mock_fig = MagicMock(spec=go.Figure)
    mock_heatmap.return_value = mock_fig
    
    # Test
    fig = visualization_manager._generate_category_heatmap(
        sample_performance_data,
        interactive=True,
        drill_down=True
    )
    
    # Verify
    assert fig == mock_fig
    mock_heatmap.assert_called_once()

@patch('plotly.express.histogram')
def test_generate_activity_distribution_plot(mock_histogram, visualization_manager, sample_performance_data):
    # Setup
    mock_fig = MagicMock(spec=go.Figure)
    mock_histogram.return_value = mock_fig
    
    # Test
    fig = visualization_manager._generate_activity_distribution_plot(
        sample_performance_data,
        interactive=True,
        drill_down=True
    )
    
    # Verify
    assert fig == mock_fig
    mock_histogram.assert_called_once()

@patch('plotly.express.line')
def test_generate_improvement_trends_plot(mock_line, visualization_manager, sample_performance_data):
    # Setup
    mock_fig = MagicMock(spec=go.Figure)
    mock_line.return_value = mock_fig
    
    # Test
    fig = visualization_manager._generate_improvement_trends_plot(
        sample_performance_data,
        interactive=True,
        drill_down=True
    )
    
    # Verify
    assert fig == mock_fig
    mock_line.assert_called_once()

@patch('plotly.express.scatter')
def test_generate_skill_analysis_plot(mock_scatter, visualization_manager, sample_skill_data):
    # Setup
    mock_fig = MagicMock(spec=go.Figure)
    mock_scatter.return_value = mock_fig
    
    # Test
    fig = visualization_manager._generate_skill_analysis_plot(
        sample_skill_data,
        interactive=True,
        drill_down=True
    )
    
    # Verify
    assert fig == mock_fig
    mock_scatter.assert_called_once()

@patch('plotly.graph_objects.Figure')
def test_generate_sankey_diagram(mock_figure, visualization_manager, sample_performance_data):
    # Setup
    mock_fig = MagicMock(spec=go.Figure)
    mock_figure.return_value = mock_fig
    
    # Test
    fig = visualization_manager._generate_sankey_diagram(
        sample_performance_data,
        interactive=True,
        drill_down=True
    )
    
    # Verify
    assert fig == mock_fig
    mock_figure.assert_called_once()

@patch('plotly.express.treemap')
def test_generate_treemap(mock_treemap, visualization_manager, sample_performance_data):
    # Setup
    mock_fig = MagicMock(spec=go.Figure)
    mock_treemap.return_value = mock_fig
    
    # Test
    fig = visualization_manager._generate_treemap(
        sample_performance_data,
        interactive=True,
        drill_down=True
    )
    
    # Verify
    assert fig == mock_fig
    mock_treemap.assert_called_once()

@patch('plotly.express.sunburst')
def test_generate_sunburst_chart(mock_sunburst, visualization_manager, sample_performance_data):
    # Setup
    mock_fig = MagicMock(spec=go.Figure)
    mock_sunburst.return_value = mock_fig
    
    # Test
    fig = visualization_manager._generate_sunburst_chart(
        sample_performance_data,
        interactive=True,
        drill_down=True
    )
    
    # Verify
    assert fig == mock_fig
    mock_sunburst.assert_called_once()

@patch('plotly.express.violin')
def test_generate_violin_plot(mock_violin, visualization_manager, sample_performance_data):
    # Setup
    mock_fig = MagicMock(spec=go.Figure)
    mock_violin.return_value = mock_fig
    
    # Test
    fig = visualization_manager._generate_violin_plot(
        sample_performance_data,
        interactive=True,
        drill_down=True
    )
    
    # Verify
    assert fig == mock_fig
    mock_violin.assert_called_once()

@patch('plotly.graph_objects.Figure.update_layout')
def test_add_accessibility_features(mock_update_layout, visualization_manager):
    # Setup
    mock_fig = MagicMock(spec=go.Figure)
    
    # Test
    visualization_manager._add_accessibility_features(mock_fig, 'performance_trend')
    
    # Verify
    mock_update_layout.assert_called()

@patch('plotly.graph_objects.Figure.write_image')
@patch('plotly.graph_objects.Figure.write_html')
def test_save_visualization(mock_write_html, mock_write_image, visualization_manager):
    # Setup
    mock_fig = MagicMock(spec=go.Figure)
    student_id = 'test_student'
    viz_type = 'performance_trend'
    
    # Test
    output_paths = visualization_manager._save_visualization(mock_fig, student_id, viz_type)
    
    # Verify
    assert isinstance(output_paths, dict)
    mock_write_image.assert_called()
    mock_write_html.assert_called()

@patch('plotly.graph_objects.Figure.write_image')
def test_generate_visualizations(mock_write_image, visualization_manager, sample_performance_data):
    # Setup
    mock_fig = MagicMock(spec=go.Figure)
    mock_write_image.return_value = None
    
    # Test
    visualizations = visualization_manager.generate_visualizations(
        sample_performance_data,
        'test_student',
        visualization_types=['performance_trend'],
        interactive=True,
        drill_down=True
    )
    
    # Verify
    assert isinstance(visualizations, dict)
    assert 'performance_trend' in visualizations 