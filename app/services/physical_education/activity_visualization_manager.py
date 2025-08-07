"""Activity visualization manager for physical education."""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from app.core.database import get_db

# Import models
from app.models.activity import (
    Activity
)
from app.models.activity_adaptation.categories.activity_categories import ActivityCategoryAssociation
from app.models.student import Student
from app.models.physical_education.pe_enums.pe_types import (
    ActivityType,
    DifficultyLevel,
    EquipmentRequirement,
    ChartType,
    ColorScheme,
    InteractionMode,
    VisualizationType,
    VisualizationLevel,
    VisualizationStatus,
    VisualizationTrigger
)
from app.models.physical_education.activity.models import (
    StudentActivityPerformance,
    StudentActivityPreference
)

class ActivityVisualizationManager:
    """Service for generating visualizations of physical education activities."""
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ActivityVisualizationManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.logger = logging.getLogger("activity_visualization_manager")
        self.db = None
        
        # Visualization settings
        self.settings = {
            "default_theme": "plotly_white",
            "color_schemes": {
                "default": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"],
                "pastel": ["#fbb4ae", "#b3cde3", "#ccebc5", "#decbe4", "#fed9a6"],
                "contrast": ["#e41a1c", "#377eb8", "#4daf4a", "#984ea3", "#ff7f00"]
            },
            "chart_types": {
                "performance": "line",
                "comparison": "bar",
                "distribution": "histogram",
                "correlation": "scatter",
                "progress": "area"
            },
            "default_dimensions": {
                "width": 800,
                "height": 500
            },
            "animation_settings": {
                "enabled": True,
                "duration": 500,
                "easing": "cubic-in-out"
            },
            "accessibility": {
                "high_contrast": False,
                "screen_reader": False,
                "keyboard_navigation": False
            }
        }
        
        # Visualization components
        self.visualization_history = []
        self.chart_templates = {}
        self.custom_layouts = {}
        self.interaction_handlers = {}
        self.export_formats = {}
        
        # Caching and optimization
        self.visualization_cache = {}
        self.template_cache = {}
    
    async def initialize(self):
        """Initialize the visualization manager."""
        try:
            self.db = next(get_db())
            
            # Load chart templates
            await self.load_chart_templates()
            
            # Initialize visualization components
            self.initialize_visualization_components()
            
            self.logger.info("Activity Visualization Manager initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing Activity Visualization Manager: {str(e)}")
            raise
    
    async def cleanup(self):
        """Cleanup the visualization manager."""
        try:
            # Clear all data
            self.visualization_history.clear()
            self.chart_templates.clear()
            self.custom_layouts.clear()
            self.interaction_handlers.clear()
            self.export_formats.clear()
            self.visualization_cache.clear()
            self.template_cache.clear()
            
            # Reset settings to defaults
            self.settings['default_theme'] = 'light'
            self.settings['accessibility'] = {
                "high_contrast": False,
                "screen_reader": False,
                "keyboard_navigation": False
            }
            
            # Reset service references
            self.db = None
            
            self.logger.info("Activity Visualization Manager cleaned up successfully")
        except Exception as e:
            self.logger.error(f"Error cleaning up Activity Visualization Manager: {str(e)}")
            raise

    async def load_chart_templates(self):
        """Load chart templates for different visualization types."""
        try:
            self.chart_templates = {
                "performance": {
                    "layout": {
                        "title": "Performance Over Time",
                        "xaxis_title": "Date",
                        "yaxis_title": "Performance Score",
                        "showlegend": True,
                        "hovermode": "x unified"
                    },
                    "traces": {
                        "score": {
                            "type": "scatter",
                            "mode": "lines+markers",
                            "line": {"width": 2},
                            "marker": {"size": 6}
                        },
                        "trend": {
                            "type": "scatter",
                            "mode": "lines",
                            "line": {"dash": "dash", "width": 1}
                        }
                    }
                },
                "comparison": {
                    "layout": {
                        "title": "Performance Comparison",
                        "barmode": "group",
                        "xaxis_title": "Category",
                        "yaxis_title": "Score",
                        "showlegend": True
                    },
                    "traces": {
                        "bars": {
                            "type": "bar",
                            "marker": {"opacity": 0.8}
                        }
                    }
                },
                "distribution": {
                    "layout": {
                        "title": "Score Distribution",
                        "xaxis_title": "Score",
                        "yaxis_title": "Count",
                        "bargap": 0.1
                    },
                    "traces": {
                        "histogram": {
                            "type": "histogram",
                            "marker": {"opacity": 0.7}
                        }
                    }
                }
            }
            
            self.logger.info("Chart templates loaded successfully")
        except Exception as e:
            self.logger.error(f"Error loading chart templates: {str(e)}")
            raise

    def initialize_visualization_components(self):
        """Initialize visualization components."""
        try:
            # Initialize custom layouts
            self.custom_layouts = {
                "dashboard": {
                    "grid": {"rows": 2, "columns": 2, "pattern": "independent"},
                    "spacing": {"vertical": 0.1, "horizontal": 0.1},
                    "dimensions": {"width": 1200, "height": 800}
                },
                "report": {
                    "grid": {"rows": 3, "columns": 1, "pattern": "vertical"},
                    "spacing": {"vertical": 0.2, "horizontal": 0},
                    "dimensions": {"width": 800, "height": 1200}
                }
            }
            
            # Initialize interaction handlers
            self.interaction_handlers = {
                "zoom": self._handle_zoom,
                "pan": self._handle_pan,
                "select": self._handle_select,
                "hover": self._handle_hover
            }
            
            # Initialize export formats
            self.export_formats = {
                "png": {"dpi": 300, "scale": 2},
                "svg": {"include_plotlyjs": False, "include_mathjax": False},
                "html": {"include_plotlyjs": True, "full_html": True},
                "json": {"pretty_print": True}
            }
            
            self.logger.info("Visualization components initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing visualization components: {str(e)}")
            raise

    async def generate_performance_visualization(
        self,
        student_id: str,
        activity_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        interactive: bool = True
    ) -> Dict[str, Any]:
        """Generate performance visualization for a student."""
        try:
            # Get performance data
            performance_data = await self._get_performance_data(
                student_id, activity_type, start_date, end_date
            )
            
            if interactive:
                # Create interactive visualization using plotly
                fig = self._create_interactive_performance_plot(performance_data)
                
                return {
                    'html': fig.to_html(full_html=False),
                    'data': performance_data.to_dict('records')
                }
            else:
                # Create static visualization
                fig = self._create_static_performance_plot(performance_data)
                
                # Convert to base64
                return self._convert_figure_to_base64(fig)
            
        except Exception as e:
            self.logger.error(f"Error generating performance visualization: {str(e)}")
            raise

    async def generate_comparison_visualization(
        self,
        student_ids: List[str],
        activity_type: Optional[str] = None,
        metric: str = "average_score",
        interactive: bool = True
    ) -> Dict[str, Any]:
        """Generate comparison visualization for multiple students."""
        try:
            # Get comparison data
            comparison_data = await self._get_comparison_data(
                student_ids, activity_type, metric
            )
            
            if interactive:
                # Create interactive visualization using plotly
                fig = self._create_interactive_comparison_plot(comparison_data)
                
                return {
                    'html': fig.to_html(full_html=False),
                    'data': comparison_data.to_dict('records')
                }
            else:
                # Create static visualization
                fig = self._create_static_comparison_plot(comparison_data)
                
                # Convert to base64
                return self._convert_figure_to_base64(fig)
            
        except Exception as e:
            self.logger.error(f"Error generating comparison visualization: {str(e)}")
            raise

    async def generate_progress_visualization(
        self,
        student_id: str,
        metrics: List[str],
        time_range: str = "1M",
        interactive: bool = True
    ) -> Dict[str, Any]:
        """Generate progress visualization showing multiple metrics."""
        try:
            # Get progress data
            progress_data = await self._get_progress_data(
                student_id, metrics, time_range
            )
            
            if interactive:
                # Create interactive visualization using plotly
                fig = self._create_interactive_progress_plot(progress_data)
                
                return {
                    'html': fig.to_html(full_html=False),
                    'data': progress_data.to_dict('records')
                }
            else:
                # Create static visualization
                fig = self._create_static_progress_plot(progress_data)
                
                # Convert to base64
                return self._convert_figure_to_base64(fig)
            
        except Exception as e:
            self.logger.error(f"Error generating progress visualization: {str(e)}")
            raise

    async def generate_distribution_visualization(
        self,
        metric: str,
        group_by: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        interactive: bool = True
    ) -> Dict[str, Any]:
        """Generate distribution visualization for a metric."""
        try:
            # Get distribution data
            distribution_data = await self._get_distribution_data(
                metric, group_by, filters
            )
            
            if interactive:
                # Create interactive visualization using plotly
                fig = self._create_interactive_distribution_plot(distribution_data)
                
                return {
                    'html': fig.to_html(full_html=False),
                    'data': distribution_data.to_dict('records')
                }
            else:
                # Create static visualization
                fig = self._create_static_distribution_plot(distribution_data)
                
                # Convert to base64
                return self._convert_figure_to_base64(fig)
            
        except Exception as e:
            self.logger.error(f"Error generating distribution visualization: {str(e)}")
            raise

    def _create_interactive_performance_plot(self, data: pd.DataFrame) -> go.Figure:
        """Create interactive performance plot using plotly."""
        try:
            template = self.chart_templates["performance"]
            
            fig = go.Figure()
            
            # Add score trace
            fig.add_trace(
                go.Scatter(
                    x=data['date'],
                    y=data['score'],
                    name='Performance Score',
                    **template['traces']['score']
                )
            )
            
            # Add trend line
            trend_data = self._calculate_trend_line(data)
            fig.add_trace(
                go.Scatter(
                    x=trend_data['date'],
                    y=trend_data['trend'],
                    name='Trend',
                    **template['traces']['trend']
                )
            )
            
            # Update layout
            fig.update_layout(**template['layout'])
            
            return fig
            
        except Exception as e:
            self.logger.error(f"Error creating interactive performance plot: {str(e)}")
            raise

    def _create_interactive_comparison_plot(self, data: pd.DataFrame) -> go.Figure:
        """Create interactive comparison plot using plotly."""
        try:
            template = self.chart_templates["comparison"]
            
            fig = go.Figure()
            
            # Add bar traces for each category
            for category in data['category'].unique():
                category_data = data[data['category'] == category]
                fig.add_trace(
                    go.Bar(
                        x=category_data['student_id'],
                        y=category_data['score'],
                        name=category,
                        **template['traces']['bars']
                    )
                )
            
            # Update layout
            fig.update_layout(**template['layout'])
            
            return fig
            
        except Exception as e:
            self.logger.error(f"Error creating interactive comparison plot: {str(e)}")
            raise

    def _create_interactive_progress_plot(self, data: pd.DataFrame) -> go.Figure:
        """Create interactive progress plot using plotly."""
        try:
            fig = go.Figure()
            
            # Add line for each metric
            for metric in data.columns:
                if metric != 'date':
                    fig.add_trace(
                        go.Scatter(
                            x=data['date'],
                            y=data[metric],
                            name=metric,
                            mode='lines+markers'
                        )
                    )
            
            # Update layout
            fig.update_layout(
                title="Progress Over Time",
                xaxis_title="Date",
                yaxis_title="Score",
                showlegend=True,
                hovermode='x unified'
            )
            
            return fig
            
        except Exception as e:
            self.logger.error(f"Error creating interactive progress plot: {str(e)}")
            raise

    def _create_interactive_distribution_plot(self, data: pd.DataFrame) -> go.Figure:
        """Create interactive distribution plot using plotly."""
        try:
            template = self.chart_templates["distribution"]
            
            fig = go.Figure()
            
            # Add histogram trace
            fig.add_trace(
                go.Histogram(
                    x=data['value'],
                    **template['traces']['histogram']
                )
            )
            
            # Update layout
            fig.update_layout(**template['layout'])
            
            return fig
            
        except Exception as e:
            self.logger.error(f"Error creating interactive distribution plot: {str(e)}")
            raise

    def _calculate_trend_line(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate trend line for performance data."""
        try:
            # Fit linear regression
            x = np.arange(len(data))
            y = data['score'].values
            z = np.polyfit(x, y, 1)
            p = np.poly1d(z)
            
            return pd.DataFrame({
                'date': data['date'],
                'trend': p(x)
            })
            
        except Exception as e:
            self.logger.error(f"Error calculating trend line: {str(e)}")
            raise

    def _convert_figure_to_base64(self, fig: Any) -> str:
        """Convert matplotlib figure to base64 string."""
        try:
            import io
            import base64
            
            # Save figure to bytes buffer
            buf = io.BytesIO()
            fig.savefig(buf, format='png', dpi=300, bbox_inches='tight')
            buf.seek(0)
            
            # Convert to base64
            image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
            
            return f"data:image/png;base64,{image_base64}"
            
        except Exception as e:
            self.logger.error(f"Error converting figure to base64: {str(e)}")
            raise

    def _handle_zoom(self, event_data: Dict[str, Any]) -> None:
        """Handle zoom interaction events."""
        pass  # To be implemented

    def _handle_pan(self, event_data: Dict[str, Any]) -> None:
        """Handle pan interaction events."""
        pass  # To be implemented

    def _handle_select(self, event_data: Dict[str, Any]) -> None:
        """Handle selection interaction events."""
        pass  # To be implemented

    def _handle_hover(self, event_data: Dict[str, Any]) -> None:
        """Handle hover interaction events."""
        pass  # To be implemented

    def generate_visualizations(
        self,
        student_id: str,
        performance_data: pd.DataFrame,
        skill_data: pd.DataFrame,
        visualization_types: List[str],
        interactive: bool = True,
        drill_down: bool = False
    ) -> List[Dict[str, Any]]:
        """Generate multiple visualizations based on the specified types."""
        visualizations = []
        for viz_type in visualization_types:
            if viz_type == 'performance_trend':
                fig = self._generate_performance_trend_plot(performance_data, interactive, drill_down)
            elif viz_type == 'category_heatmap':
                fig = self._generate_category_heatmap(performance_data, interactive, drill_down)
            elif viz_type == 'activity_distribution':
                fig = self._generate_activity_distribution_plot(performance_data, interactive, drill_down)
            elif viz_type == 'improvement_trends':
                fig = self._generate_improvement_trends_plot(performance_data, interactive, drill_down)
            elif viz_type == 'skill_analysis':
                fig = self._generate_skill_analysis_plot(skill_data, interactive, drill_down)
            elif viz_type == 'sankey_diagram':
                fig = self._generate_sankey_diagram(performance_data, interactive, drill_down)
            elif viz_type == 'treemap':
                fig = self._generate_treemap(performance_data, interactive, drill_down)
            elif viz_type == 'sunburst_chart':
                fig = self._generate_sunburst_chart(performance_data, interactive, drill_down)
            elif viz_type == 'violin_plot':
                fig = self._generate_violin_plot(performance_data, interactive, drill_down)
            else:
                raise ValueError(f"Unsupported visualization type: {viz_type}")
            
            visualizations.append({
                'type': viz_type,
                'data': fig,
                'metadata': {
                    'student_id': student_id,
                    'interactive': interactive,
                    'drill_down': drill_down
                }
            })
        
        return visualizations

    def _generate_performance_trend_plot(
        self,
        data: pd.DataFrame,
        interactive: bool = True,
        drill_down: bool = False,
        theme: Optional[str] = None
    ) -> go.Figure:
        """Generate performance trend plot."""
        if data is None:
            raise ValueError("Data cannot be None")
        if data.empty:
            raise ValueError("Empty data")
            
        # Check if required columns exist
        required_columns = ['date', 'score']
        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
            
        # Validate data types
        try:
            # Check if date column can be converted to datetime
            pd.to_datetime(data['date'])
        except (ValueError, TypeError):
            raise ValueError("Invalid data types")
            
        try:
            # Check if score column can be converted to numeric
            pd.to_numeric(data['score'])
        except (ValueError, TypeError):
            raise ValueError("Invalid data types")
            
        fig = px.line(
            data,
            x='date',
            y='score',
            color='category' if 'category' in data.columns else None,
            title='Performance Trend',
            template=theme or self.settings['default_theme']
        )
        
        if drill_down:
            fig.update_layout(
                updatemenus=[
                    dict(
                        type="buttons",
                        direction="right",
                        x=0.7,
                        y=1.2,
                        showactive=True,
                        buttons=list([
                            dict(
                                args=[{"visible": [True, False]}],
                                label="All",
                                method="update"
                            ),
                            dict(
                                args=[{"visible": [False, True]}],
                                label="By Category",
                                method="update"
                            )
                        ])
                    )
                ]
            )
        
        return fig

    def _generate_category_heatmap(
        self,
        data: pd.DataFrame,
        interactive: bool = True,
        drill_down: bool = False,
        theme: Optional[str] = None
    ) -> go.Figure:
        """Generate category heatmap."""
        fig = px.density_heatmap(
            data,
            x='category',
            y='activity_type',
            z='score',
            title='Category Heatmap',
            template=theme or self.settings['default_theme']
        )
        return fig

    def _generate_activity_distribution_plot(
        self,
        data: pd.DataFrame,
        interactive: bool = True,
        drill_down: bool = False,
        theme: Optional[str] = None
    ) -> go.Figure:
        """Generate activity distribution plot."""
        fig = px.histogram(
            data,
            x='score',
            color='category',
            title='Activity Distribution',
            template=theme or self.settings['default_theme']
        )
        return fig

    def _generate_improvement_trends_plot(
        self,
        data: pd.DataFrame,
        interactive: bool = True,
        drill_down: bool = False,
        theme: Optional[str] = None
    ) -> go.Figure:
        """Generate improvement trends plot."""
        fig = px.scatter(
            data,
            x='date',
            y='score',
            color='category',
            title='Improvement Trends',
            template=theme or self.settings['default_theme']
        )
        return fig

    def _generate_skill_analysis_plot(
        self,
        data: pd.DataFrame,
        interactive: bool = True,
        drill_down: bool = False,
        theme: Optional[str] = None
    ) -> go.Figure:
        """Generate skill analysis plot."""
        fig = px.scatter(
            data,
            x='score',
            y='target_score',
            color='category',
            title='Skill Analysis',
            template=theme or self.settings['default_theme']
        )
        return fig

    def _generate_sankey_diagram(
        self,
        data: pd.DataFrame,
        interactive: bool = True,
        drill_down: bool = False,
        theme: Optional[str] = None
    ) -> go.Figure:
        """Generate Sankey diagram."""
        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=["Category", "Activity Type", "Score Range"],
                color="blue"
            ),
            link=dict(
                source=[0, 0, 1, 1],
                target=[1, 1, 2, 2],
                value=[8, 4, 2, 8]
            )
        )])
        
        fig.update_layout(
            title_text="Activity Flow",
            template=theme or self.settings['default_theme']
        )
        return fig

    def _generate_treemap(
        self,
        data: pd.DataFrame,
        interactive: bool = True,
        drill_down: bool = False,
        theme: Optional[str] = None
    ) -> go.Figure:
        """Generate treemap."""
        fig = px.treemap(
            data,
            path=['category', 'activity_type'],
            values='score',
            title='Activity Treemap',
            template=theme or self.settings['default_theme']
        )
        return fig

    def _generate_sunburst_chart(
        self,
        data: pd.DataFrame,
        interactive: bool = True,
        drill_down: bool = False,
        theme: Optional[str] = None
    ) -> go.Figure:
        """Generate sunburst chart."""
        fig = px.sunburst(
            data,
            path=['category', 'activity_type'],
            values='score',
            title='Activity Sunburst',
            template=theme or self.settings['default_theme']
        )
        return fig

    def _generate_violin_plot(
        self,
        data: pd.DataFrame,
        interactive: bool = True,
        drill_down: bool = False,
        theme: Optional[str] = None
    ) -> go.Figure:
        """Generate violin plot."""
        fig = px.violin(
            data,
            x='category',
            y='score',
            title='Score Distribution by Category',
            template=theme or self.settings['default_theme']
        )
        return fig

    def save_visualization(self, fig: go.Figure, output_path: str, fmt: str = 'png') -> None:
        """Save visualization to file."""
        if fig is None:
            raise ValueError("Cannot save None figure")
            
        if not hasattr(fig, 'write_image'):
            raise ValueError("Invalid figure object")
            
        if fmt == 'png':
            fig.write_image(output_path)
        elif fmt == 'html':
            fig.write_html(output_path)
        elif fmt == 'json':
            fig.write_json(output_path)
        else:
            raise ValueError(f"Unsupported format: {fmt}")

    def set_theme(self, theme: str) -> None:
        """Set the visualization theme."""
        if theme not in ['light', 'dark', 'custom']:
            raise ValueError(f"Unsupported theme: {theme}")
        self.settings['default_theme'] = theme

    def set_accessibility(self, options: Dict[str, bool]) -> None:
        """Set accessibility options."""
        if options is None:
            raise ValueError("Options cannot be None")
        if not isinstance(options, dict):
            raise ValueError("Options must be a dictionary")
        if not options:  # Empty dict
            raise ValueError("Options cannot be empty")
            
        for key, value in options.items():
            if key not in self.settings['accessibility']:
                raise ValueError(f"Unsupported accessibility option: {key}")
            if not isinstance(value, bool):
                raise ValueError(f"Accessibility option {key} must be a boolean")
            self.settings['accessibility'][key] = value

    def _add_accessibility_features(self, fig: go.Figure) -> None:
        """Add accessibility features to the figure."""
        fig.update_layout(
            title=dict(
                text="Interactive Visualization",
                font=dict(size=16)
            ),
            xaxis=dict(
                title=dict(
                    text="X Axis",
                    font=dict(size=14)
                )
            ),
            yaxis=dict(
                title=dict(
                    text="Y Axis",
                    font=dict(size=14)
                )
            ),
            showlegend=True,
            hovermode='closest',
            font=dict(
                family="Arial, sans-serif",
                size=12,
                color="black"
            )
        ) 