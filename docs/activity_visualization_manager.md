# Activity Visualization Manager Documentation

## Overview
The `ActivityVisualizationManager` is a specialized service for generating and managing visualizations of student activity data in physical education. It provides a comprehensive suite of visualization tools with support for interactive features, accessibility options, and multiple export formats.

## Features

### Visualization Types
1. **Performance Trend Plot**
   - Tracks student performance over time
   - Interactive drill-down by activity type
   - Moving average and trend lines
   - Annotations for significant improvements

2. **Category Heatmap**
   - Visualizes activity distribution across categories
   - Color-coded intensity representation
   - Interactive filtering by date range
   - Hover information for detailed metrics

3. **Activity Distribution Plot**
   - Shows distribution of activities by type
   - Stacked bar representation
   - Interactive category filtering
   - Percentage breakdowns

4. **Improvement Trends Plot**
   - Tracks improvement rates over time
   - Category-specific trend analysis
   - Reference lines for average improvement
   - Annotations for significant changes

5. **Skill Analysis Plot**
   - Visualizes skill mastery levels
   - Target vs. current performance
   - Category grouping
   - Progress indicators

6. **Sankey Diagram**
   - Shows flow between activity categories
   - Interactive node filtering
   - Flow value annotations
   - Directional indicators

7. **Treemap**
   - Hierarchical view of activities
   - Size-based value representation
   - Interactive drill-down
   - Color scale selectors

8. **Sunburst Chart**
   - Circular hierarchical visualization
   - Multi-level category representation
   - Interactive sector selection
   - Value percentage labels

9. **Violin Plot**
   - Distribution analysis by category
   - Box plot overlay
   - Outlier detection
   - Statistical annotations

### Interactive Features
- Drill-down capabilities for all visualizations
- Category and activity type filtering
- Hover information with detailed metrics
- Custom color schemes and scales
- Theme support (light/dark modes)

### Accessibility Features
- High contrast mode
- Color blind friendly palettes
- Adjustable font sizes
- Screen reader compatibility
- Keyboard navigation support

### Export Options
- PNG (static images)
- SVG (vector graphics)
- PDF (document format)
- HTML (interactive web format)
- JSON (data format)
- PPTX (PowerPoint presentations)
- DOCX (Word documents)
- XLSX (Excel spreadsheets)
- CSV (comma-separated values)
- LaTeX (academic papers)
- Markdown (documentation)
- GIF (animated visualizations)
- MP4 (video format)

## Usage

### Initialization
```python
from app.services.physical_education.services.activity_visualization_manager import ActivityVisualizationManager

# Create instance with default settings
visualization_manager = ActivityVisualizationManager()

# Create instance with custom settings
visualization_manager = ActivityVisualizationManager(
    visualization_types=['performance_trend', 'category_heatmap'],
    config={
        'theme': 'dark',
        'accessibility': {
            'high_contrast': True,
            'color_blind_friendly': True,
            'font_size': 'large'
        }
    }
)
```

### Generating Visualizations
```python
# Generate multiple visualizations
visualizations = await visualization_manager.generate_visualizations(
    student_id="12345",
    performance_data=performance_df,
    skill_data=skill_df,
    visualization_types=['performance_trend', 'category_heatmap'],
    interactive=True,
    drill_down=True
)

# Generate single visualization
fig = visualization_manager._generate_performance_trend_plot(
    data=performance_df,
    interactive=True,
    drill_down=True
)
```

### Saving Visualizations
```python
# Save visualization to file
output_path = await visualization_manager.save_visualization(
    visualization={
        'type': 'performance_trend',
        'data': fig,
        'metadata': {
            'student_id': '12345',
            'timestamp': datetime.now().isoformat()
        }
    },
    student_id='12345'
)
```

## Configuration

### Theme Settings
```python
# Set theme
visualization_manager.theme = 'dark'  # or 'light'

# Custom theme colors
visualization_manager.theme_colors = {
    'background': '#1E1E1E',
    'text': '#FFFFFF',
    'grid': '#2D2D2D',
    'accent': '#007ACC'
}
```

### Accessibility Settings
```python
# Configure accessibility
visualization_manager.accessibility_settings = {
    'high_contrast': True,
    'color_blind_friendly': True,
    'font_size': 'large',  # 'small', 'medium', 'large'
    'screen_reader_compatible': True
}
```

## Data Requirements

### Performance Data
Required columns:
- `date`: datetime
- `score`: float
- `category`: str
- `activity_type`: str
- `duration`: int
- `intensity`: float

### Skill Data
Required columns:
- `skill`: str
- `score`: float
- `category`: str
- `target_score`: float
- `progress`: float

## Error Handling
The manager includes comprehensive error handling for:
- Invalid data formats
- Missing required columns
- Unsupported visualization types
- Export format errors
- File system errors

## Testing
Comprehensive test suite available in `tests/test_activity_visualization_manager.py`:
- Unit tests for all visualization types
- Theme and accessibility testing
- Error handling tests
- Export functionality tests

## Best Practices
1. Always validate input data before visualization
2. Use appropriate visualization types for data characteristics
3. Enable accessibility features for inclusive design
4. Consider performance impact of interactive features
5. Regularly update visualization configurations
6. Monitor export file sizes for large datasets

## Limitations
1. Large datasets may impact performance
2. Some export formats have size limitations
3. Complex visualizations may not be suitable for all screen sizes
4. Animation exports require significant processing time

## Future Enhancements
1. Real-time data streaming support
2. Custom visualization templates
3. Advanced statistical analysis integration
4. Machine learning-based visualization recommendations
5. Collaborative visualization features
6. Enhanced export format support

## Support
For issues or feature requests, please contact the development team or create an issue in the repository. 