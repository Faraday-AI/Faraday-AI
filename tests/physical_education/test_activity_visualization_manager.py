import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, AsyncMock
from app.services.physical_education.activity_visualization_manager import ActivityVisualizationManager
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import os
from pathlib import Path
import psutil
import gc
import time

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

@pytest.mark.psycopg
def test_generate_visualizations(visualization_manager, sample_performance_data, sample_skill_data):
    """Test generating multiple visualizations."""
    visualization_types = [
        'performance_trend',
        'category_heatmap',
        'activity_distribution',
        'improvement_trends',
        'skill_analysis',
        'sankey_diagram',
        'treemap',
        'sunburst_chart',
        'violin_plot'
    ]
    
    visualizations = visualization_manager.generate_visualizations(
        student_id="test_student",
        performance_data=sample_performance_data,
        skill_data=sample_skill_data,
        visualization_types=visualization_types,
        interactive=True,
        drill_down=True
    )
    
    assert len(visualizations) == len(visualization_types)
    for viz in visualizations:
        assert viz['type'] in visualization_types
        assert 'data' in viz
        assert 'metadata' in viz
        assert viz['metadata']['student_id'] == "test_student"
        assert viz['metadata']['interactive'] is True
        assert viz['metadata']['drill_down'] is True

@pytest.mark.psycopg
@patch('plotly.express.line')
def test_generate_performance_trend_plot(mock_line, visualization_manager, sample_performance_data):
    """Test performance trend plot generation with mocked line function."""
    # Setup
    mock_fig = MagicMock()
    mock_line.return_value = mock_fig
    
    # Test
    fig = visualization_manager._generate_performance_trend_plot(
        data=sample_performance_data,
        interactive=True,
        drill_down=True,
        theme='plotly_white'
    )
    
    # Verify
    mock_line.assert_called_once()
    assert fig == mock_fig

@pytest.mark.psycopg
@patch('plotly.express.density_heatmap')
def test_generate_category_heatmap(mock_heatmap, visualization_manager, sample_performance_data):
    """Test category heatmap generation with mocked heatmap function."""
    # Setup
    mock_fig = MagicMock()
    mock_heatmap.return_value = mock_fig
    
    # Test
    fig = visualization_manager._generate_category_heatmap(
        data=sample_performance_data,
        interactive=True,
        drill_down=True,
        theme='plotly_white'
    )
    
    # Verify
    mock_heatmap.assert_called_once()
    assert fig == mock_fig

@pytest.mark.psycopg
@patch('plotly.express.histogram')
def test_generate_activity_distribution_plot(mock_histogram, visualization_manager, sample_performance_data):
    """Test activity distribution plot generation with mocked histogram function."""
    # Setup
    mock_fig = MagicMock()
    mock_histogram.return_value = mock_fig
    
    # Test
    fig = visualization_manager._generate_activity_distribution_plot(
        data=sample_performance_data,
        interactive=True,
        drill_down=True,
        theme='plotly_white'
    )
    
    # Verify
    mock_histogram.assert_called_once()
    assert fig == mock_fig

@pytest.mark.psycopg
@patch('plotly.express.scatter')
def test_generate_improvement_trends_plot(mock_scatter, visualization_manager, sample_performance_data):
    """Test improvement trends plot generation with mocked scatter function."""
    # Setup
    mock_fig = MagicMock()
    mock_scatter.return_value = mock_fig
    
    # Test
    fig = visualization_manager._generate_improvement_trends_plot(
        data=sample_performance_data,
        interactive=True,
        drill_down=True,
        theme='plotly_white'
    )
    
    # Verify
    mock_scatter.assert_called_once()
    assert fig == mock_fig

@pytest.mark.psycopg
@patch('plotly.express.scatter')
def test_generate_skill_analysis_plot(mock_scatter, visualization_manager, sample_skill_data):
    """Test skill analysis plot generation with mocked scatter function."""
    # Setup
    mock_fig = MagicMock()
    mock_scatter.return_value = mock_fig
    
    # Test
    fig = visualization_manager._generate_skill_analysis_plot(
        data=sample_skill_data,
        interactive=True,
        drill_down=True,
        theme='plotly_white'
    )
    
    # Verify
    mock_scatter.assert_called_once()
    assert fig == mock_fig

@pytest.mark.psycopg
@patch('plotly.graph_objects.Figure')
def test_generate_sankey_diagram(mock_figure, visualization_manager, sample_performance_data):
    """Test Sankey diagram generation with mocked Figure class."""
    # Setup
    mock_fig = MagicMock()
    mock_figure.return_value = mock_fig
    
    # Test
    fig = visualization_manager._generate_sankey_diagram(
        data=sample_performance_data,
        interactive=True,
        drill_down=True,
        theme='plotly_white'
    )
    
    # Verify
    mock_figure.assert_called_once()
    assert fig == mock_fig

@pytest.mark.psycopg
@patch('plotly.express.treemap')
def test_generate_treemap(mock_treemap, visualization_manager, sample_performance_data):
    """Test treemap generation with mocked treemap function."""
    # Setup
    mock_fig = MagicMock()
    mock_treemap.return_value = mock_fig
    
    # Test
    fig = visualization_manager._generate_treemap(
        data=sample_performance_data,
        interactive=True,
        drill_down=True,
        theme='plotly_white'
    )
    
    # Verify
    mock_treemap.assert_called_once()
    assert fig == mock_fig

@pytest.mark.psycopg
@patch('plotly.express.sunburst')
def test_generate_sunburst_chart(mock_sunburst, visualization_manager, sample_performance_data):
    """Test sunburst chart generation with mocked sunburst function."""
    # Setup
    mock_fig = MagicMock()
    mock_sunburst.return_value = mock_fig
    
    # Test
    fig = visualization_manager._generate_sunburst_chart(
        data=sample_performance_data,
        interactive=True,
        drill_down=True,
        theme='plotly_white'
    )
    
    # Verify
    mock_sunburst.assert_called_once()
    assert fig == mock_fig

@pytest.mark.psycopg
@patch('plotly.express.violin')
def test_generate_violin_plot(mock_violin, visualization_manager, sample_performance_data):
    """Test violin plot generation with mocked violin function."""
    # Setup
    mock_fig = MagicMock()
    mock_violin.return_value = mock_fig
    
    # Test
    fig = visualization_manager._generate_violin_plot(
        data=sample_performance_data,
        interactive=True,
        drill_down=True,
        theme='plotly_white'
    )
    
    # Verify
    mock_violin.assert_called_once()
    assert fig == mock_fig

@pytest.mark.psycopg
def test_save_visualization(visualization_manager):
    """Test visualization saving functionality."""
    # Setup
    fig = go.Figure()
    
    # Test saving to different formats
    format_map = {
        'png': 'write_image',
        'html': 'write_html',
        'json': 'write_json'
    }
    
    for fmt, method_name in format_map.items():
        output_path = f"test_output/test_viz.{fmt}"
        with patch.object(fig, method_name) as mock_write:
            visualization_manager.save_visualization(fig, output_path, fmt)
            mock_write.assert_called_once_with(output_path)

@pytest.mark.psycopg
def test_theme_application(visualization_manager, sample_performance_data):
    """Test theme application to visualizations."""
    themes = ['plotly_white', 'plotly_dark', 'simple_white']
    
    for theme in themes:
        fig = visualization_manager._generate_performance_trend_plot(
            data=sample_performance_data,
            interactive=True,
            drill_down=True,
            theme=theme
        )
        
        # Verify theme is applied by checking the template property
        assert fig.layout.template is not None
        assert hasattr(fig.layout.template, 'layout')

@pytest.mark.psycopg
def test_accessibility_features(visualization_manager, sample_performance_data):
    """Test accessibility features in visualizations."""
    # Set accessibility options
    visualization_manager.set_accessibility({
        'keyboard_navigation': True,
        'screen_reader': True,
        'high_contrast': True
    })
    
    fig = visualization_manager._generate_performance_trend_plot(
        data=sample_performance_data,
        interactive=True,
        drill_down=True
    )
    
    # Add accessibility features
    visualization_manager._add_accessibility_features(fig)
    
    # Verify accessibility features through layout properties
    assert fig is not None
    assert fig.layout.title is not None
    assert fig.layout.title.text == "Interactive Visualization"
    assert fig.layout.xaxis.title is not None
    assert fig.layout.yaxis.title is not None
    assert fig.layout.showlegend is True
    assert fig.layout.hovermode == 'closest'
    assert fig.layout.font.family == "Arial, sans-serif"

@pytest.mark.psycopg
def test_error_handling(visualization_manager):
    """Test error handling in visualization generation."""
    # Test with invalid data
    with pytest.raises(ValueError):
        visualization_manager._generate_performance_trend_plot(
            data=None,
            interactive=True
        )
    
    # Test with empty data
    with pytest.raises(ValueError):
        visualization_manager._generate_performance_trend_plot(
            data=pd.DataFrame(),
            interactive=True
        )
    
    # Test with invalid visualization type
    with pytest.raises(ValueError):
        visualization_manager.generate_visualizations(
            student_id="12345",
            performance_data=pd.DataFrame(),
            skill_data=pd.DataFrame(),
            visualization_types=['invalid_type'],
            interactive=True
        )

def test_set_theme(visualization_manager):
    # Test setting valid theme
    visualization_manager.set_theme('dark')
    assert visualization_manager.settings['default_theme'] == 'dark'
    
    # Test setting invalid theme
    with pytest.raises(ValueError):
        visualization_manager.set_theme('invalid_theme')

def test_set_accessibility(visualization_manager):
    # Test setting accessibility options
    options = {
        'high_contrast': True,
        'screen_reader': True,
        'keyboard_navigation': True
    }
    visualization_manager.set_accessibility(options)
    assert visualization_manager.settings['accessibility'] == options
    
    # Test setting invalid options
    with pytest.raises(ValueError):
        visualization_manager.set_accessibility({'invalid_option': True})

@pytest.mark.psycopg
@patch('plotly.graph_objects.Figure.update_layout')
def test_add_accessibility_features(mock_update_layout, visualization_manager):
    """Test adding accessibility features to a figure."""
    # Setup
    fig = go.Figure()
    visualization_manager.set_accessibility({
        'keyboard_navigation': True,
        'screen_reader': True,
        'high_contrast': True
    })
    
    # Test
    visualization_manager._add_accessibility_features(fig)
    
    # Verify
    mock_update_layout.assert_called_once()
    call_args = mock_update_layout.call_args[1]
    assert 'title' in call_args
    assert 'xaxis' in call_args
    assert 'yaxis' in call_args
    assert 'showlegend' in call_args
    assert 'hovermode' in call_args
    assert 'font' in call_args
    
    # Verify specific values
    assert call_args['title']['text'] == "Interactive Visualization"
    assert call_args['title']['font']['size'] == 16
    assert call_args['xaxis']['title']['text'] == "X Axis"
    assert call_args['yaxis']['title']['text'] == "Y Axis"
    assert call_args['showlegend'] is True
    assert call_args['hovermode'] == 'closest'
    assert call_args['font']['family'] == "Arial, sans-serif"

@pytest.mark.psycopg
def test_save_visualization_error_cases(visualization_manager):
    """Test error cases for save_visualization."""
    fig = go.Figure()
    
    # Test invalid format
    with pytest.raises(ValueError, match="Unsupported format"):
        visualization_manager.save_visualization(fig, "test.png", "invalid_format")
    
    # Test invalid path
    with pytest.raises(ValueError):
        visualization_manager.save_visualization(fig, "", "png")
    
    # Test None figure
    with pytest.raises(ValueError):
        visualization_manager.save_visualization(None, "test.png", "png")
    
    # Test invalid figure type
    with pytest.raises(ValueError):
        visualization_manager.save_visualization("not_a_figure", "test.png", "png")

@pytest.mark.psycopg
def test_save_visualization_path_handling(visualization_manager):
    """Test saving visualization with different path formats."""
    fig = go.Figure()
    paths = [
        "test.png",
        "subdir/test.png",
        "/absolute/path/test.png",
        "test with spaces.png",
        "test.with.dots.png",
        "test-123.png"
    ]
    
    for path in paths:
        with patch.object(fig, 'write_image') as mock_write:
            visualization_manager.save_visualization(fig, path, "png")
            mock_write.assert_called_once_with(path)
            mock_write.reset_mock()

@pytest.mark.psycopg
def test_theme_validation(visualization_manager):
    """Test theme validation with various inputs."""
    # Test valid themes
    valid_themes = ['light', 'dark', 'custom']
    for theme in valid_themes:
        visualization_manager.set_theme(theme)
        assert visualization_manager.settings['default_theme'] == theme
    
    # Test invalid themes
    invalid_themes = ['invalid', '', None, 123, True, [], {}]
    for theme in invalid_themes:
        with pytest.raises(ValueError, match="Unsupported theme"):
            visualization_manager.set_theme(theme)

@pytest.mark.psycopg
def test_accessibility_options_validation(visualization_manager):
    """Test accessibility options validation."""
    # Test valid options
    valid_options = {
        'keyboard_navigation': True,
        'screen_reader': True,
        'high_contrast': True
    }
    visualization_manager.set_accessibility(valid_options)
    assert visualization_manager.settings['accessibility'] == valid_options
    
    # Test invalid options
    invalid_options = [
        {'invalid_option': True},
        {'keyboard_navigation': 'not_a_boolean'},
        None,
        [],
        {},
        {'keyboard_navigation': None},
        {'screen_reader': 123},
        {'high_contrast': 'yes'}
    ]
    for options in invalid_options:
        with pytest.raises(ValueError):
            visualization_manager.set_accessibility(options)

@pytest.mark.psycopg
def test_data_validation(visualization_manager):
    """Test data validation for various scenarios."""
    # Test empty DataFrame
    empty_df = pd.DataFrame()
    with pytest.raises(ValueError, match="Empty data"):
        visualization_manager._generate_performance_trend_plot(
            data=empty_df,
            interactive=True
        )
    
    # Test None data
    with pytest.raises(ValueError, match="Data cannot be None"):
        visualization_manager._generate_performance_trend_plot(
            data=None,
            interactive=True
        )
    
    # Test missing required columns
    incomplete_df = pd.DataFrame({'date': [1, 2, 3]})  # Missing 'score' column
    with pytest.raises(ValueError, match="Missing required columns"):
        visualization_manager._generate_performance_trend_plot(
            data=incomplete_df,
            interactive=True
        )
    
    # Test invalid data types
    invalid_df = pd.DataFrame({
        'date': ['not_a_date', 'also_not_a_date'],
        'score': ['not_a_number', 'also_not_a_number']
    })
    with pytest.raises(ValueError, match="Invalid data types"):
        visualization_manager._generate_performance_trend_plot(
            data=invalid_df,
            interactive=True
        )

@pytest.mark.psycopg
def test_singleton_pattern(visualization_manager):
    """Test that ActivityVisualizationManager follows singleton pattern."""
    # Create multiple instances
    manager2 = ActivityVisualizationManager()
    manager3 = ActivityVisualizationManager()
    
    # Verify they are the same instance
    assert visualization_manager is manager2
    assert visualization_manager is manager3
    assert manager2 is manager3
    
    # Verify settings are shared
    visualization_manager.set_theme('dark')
    assert manager2.settings['default_theme'] == 'dark'
    assert manager3.settings['default_theme'] == 'dark'

@pytest.mark.asyncio
async def test_cleanup(visualization_manager):
    """Test cleanup method."""
    # Setup some state
    visualization_manager.set_theme('dark')
    visualization_manager.set_accessibility({
        'keyboard_navigation': True,
        'screen_reader': True,
        'high_contrast': True
    })
    
    # Perform cleanup
    await visualization_manager.cleanup()
    
    # Verify cleanup
    assert visualization_manager.settings['default_theme'] == 'light'  # Default theme
    assert visualization_manager.settings['accessibility'] == {
        'keyboard_navigation': False,
        'screen_reader': False,
        'high_contrast': False
    }

@pytest.mark.performance
def test_large_dataset_performance(visualization_manager):
    """Test performance with large datasets."""
    # Create large dataset
    dates = pd.date_range(start='2020-01-01', end='2024-12-31', freq='D')
    np.random.seed(42)
    
    large_data = {
        'date': dates,
        'score': np.random.uniform(0, 100, len(dates)),
        'category': np.random.choice(['Cardio', 'Strength', 'Flexibility', 'Coordination'], len(dates)),
        'activity_type': np.random.choice(['Running', 'Jumping', 'Stretching', 'Balance'], len(dates)),
        'duration': np.random.randint(10, 60, len(dates)),
        'intensity': np.random.uniform(0.5, 1.0, len(dates))
    }
    large_df = pd.DataFrame(large_data)
    
    # Measure performance
    start_time = time.time()
    
    # Generate visualizations
    visualizations = visualization_manager.generate_visualizations(
        student_id="test_student",
        performance_data=large_df,
        skill_data=sample_skill_data,
        visualization_types=['performance_trend'],
        interactive=True
    )
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    # Assert reasonable performance
    assert execution_time < 5.0  # Should complete within 5 seconds
    assert len(visualizations) == 1

@pytest.mark.memory
def test_memory_usage(visualization_manager):
    """Test memory usage during visualization generation."""
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss
    
    # Generate multiple visualizations
    for _ in range(10):
        fig = visualization_manager._generate_performance_trend_plot(
            data=sample_performance_data,
            interactive=True
        )
        # Force garbage collection
        gc.collect()
    
    final_memory = process.memory_info().rss
    memory_increase = final_memory - initial_memory
    
    # Assert reasonable memory usage
    assert memory_increase < 100 * 1024 * 1024  # Less than 100MB increase

@pytest.mark.integration
def test_file_system_operations(visualization_manager, tmp_path):
    """Test file system operations with temporary directory."""
    fig = go.Figure()
    
    # Test saving to temporary directory
    test_dir = tmp_path / "test_output"
    test_dir.mkdir()
    
    # Test different formats
    formats = ['png', 'html', 'json']
    for fmt in formats:
        output_path = test_dir / f"test_viz.{fmt}"
        visualization_manager.save_visualization(fig, str(output_path), fmt)
        assert output_path.exists()
        assert output_path.stat().st_size > 0 