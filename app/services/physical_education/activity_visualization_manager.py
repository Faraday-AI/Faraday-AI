from typing import Dict, List, Optional, Union
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os
from io import BytesIO
import base64
import json
from pathlib import Path
import imageio
try:
    import moviepy.editor as mpe
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False
    mpe = None
from plotly.subplots import make_subplots

class ActivityVisualizationManager:
    def __init__(self):
        self.visualization_types = [
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
        
        # Configure visualization settings
        self.visualization_config = {
            'style': 'seaborn',
            'color_palette': 'viridis',
            'font_size': 12,
            'figure_size': (12, 8),
            'accessibility': {
                'high_contrast': False,
                'screen_reader': True,
                'alt_text': True
            },
            'themes': {
                'default': {
                    'background': 'white',
                    'text': 'black',
                    'grid': 'lightgray'
                },
                'dark': {
                    'background': '#1f1f1f',
                    'text': 'white',
                    'grid': '#2f2f2f'
                },
                'high_contrast': {
                    'background': 'white',
                    'text': 'black',
                    'grid': '#000000'
                }
            },
            'current_theme': 'default'
        }
        
        # Set up export directory
        self.export_dir = "exports/visualizations"
        os.makedirs(self.export_dir, exist_ok=True)
        
        # Initialize drill-down state
        self.drill_down_state = {}
        
        # Apply initial theme
        self._apply_theme()

    def set_theme(self, theme_name: str) -> None:
        """Set the visualization theme."""
        if theme_name in self.visualization_config['themes']:
            self.visualization_config['current_theme'] = theme_name
            self._apply_theme()

    def set_accessibility(self, high_contrast: bool = False, 
                        screen_reader: bool = True,
                        alt_text: bool = True) -> None:
        """Configure accessibility settings."""
        self.visualization_config['accessibility'].update({
            'high_contrast': high_contrast,
            'screen_reader': screen_reader,
            'alt_text': alt_text
        })

    def _apply_theme(self) -> None:
        """Apply the current theme settings."""
        theme = self.visualization_config['themes'][self.visualization_config['current_theme']]
        plt.style.use('default')  # Use default style instead of seaborn
        plt.rcParams.update({
            'figure.facecolor': theme['background'],
            'axes.facecolor': theme['background'],
            'text.color': theme['text'],
            'axes.labelcolor': theme['text'],
            'xtick.color': theme['text'],
            'ytick.color': theme['text'],
            'grid.color': theme['grid']
        })

    def generate_visualizations(self, data: pd.DataFrame, student_id: str, 
                             visualization_types: Optional[List[str]] = None,
                             interactive: bool = True,
                             drill_down: bool = False) -> Dict[str, Union[str, Dict]]:
        """Generate multiple visualizations for a student with enhanced features."""
        if visualization_types is None:
            visualization_types = self.visualization_types
            
        visualizations = {}
        
        for viz_type in visualization_types:
            try:
                if viz_type == 'performance_trend':
                    fig = self._generate_performance_trend_plot(data, interactive, drill_down)
                elif viz_type == 'category_heatmap':
                    fig = self._generate_category_heatmap(data, interactive, drill_down)
                elif viz_type == 'activity_distribution':
                    fig = self._generate_activity_distribution_plot(data, interactive, drill_down)
                elif viz_type == 'improvement_trends':
                    fig = self._generate_improvement_trends_plot(data, interactive, drill_down)
                elif viz_type == 'skill_analysis':
                    fig = self._generate_skill_analysis_plot(data, interactive, drill_down)
                elif viz_type == 'sankey_diagram':
                    fig = self._generate_sankey_diagram(data, interactive, drill_down)
                elif viz_type == 'treemap':
                    fig = self._generate_treemap(data, interactive, drill_down)
                elif viz_type == 'sunburst_chart':
                    fig = self._generate_sunburst_chart(data, interactive, drill_down)
                elif viz_type == 'violin_plot':
                    fig = self._generate_violin_plot(data, interactive, drill_down)
                else:
                    continue
                
                # Add accessibility features
                if self.visualization_config['accessibility']['alt_text']:
                    self._add_accessibility_features(fig, viz_type)
                
                # Save visualization in multiple formats
                output_paths = self._save_visualization(fig, student_id, viz_type)
                visualizations[viz_type] = output_paths
                
            except Exception as e:
                print(f"Error generating {viz_type} visualization: {str(e)}")
                continue
                
        return visualizations

    def _generate_performance_trend_plot(self, data: pd.DataFrame, 
                                       interactive: bool,
                                       drill_down: bool) -> go.Figure:
        """Generate performance trend plot with drill-down capability."""
        if interactive:
            fig = px.line(data, x='date', y='score', 
                         color='activity_type',
                         title='Performance Trends Over Time',
                         labels={'score': 'Performance Score', 'date': 'Date'},
                         template='plotly_white')
            
            if drill_down:
                # Add drill-down buttons
                fig.update_layout(
                    updatemenus=[
                        dict(
                            type="buttons",
                            direction="right",
                            active=0,
                            x=0.57,
                            y=1.2,
                            buttons=list([
                                dict(
                                    label="All",
                                    method="update",
                                    args=[{"visible": [True] * len(data['activity_type'].unique())}]
                                ),
                                dict(
                                    label="By Category",
                                    method="update",
                                    args=[{"visible": [True if cat == data['category'].iloc[0] else False 
                                                     for cat in data['category']]}]
                                )
                            ]),
                        )
                    ]
                )
                
                # Add hover information
                fig.update_traces(
                    hovertemplate="<br>".join([
                        "Date: %{x}",
                        "Score: %{y}",
                        "Activity Type: %{text}",
                        "Category: %{customdata}"
                    ]),
                    customdata=data['category'],
                    text=data['activity_type']
                )
                
                # Add range slider
                fig.update_layout(
                    xaxis=dict(
                        rangeselector=dict(
                            buttons=list([
                                dict(count=1, label="1m", step="month", stepmode="backward"),
                                dict(count=6, label="6m", step="month", stepmode="backward"),
                                dict(count=1, label="YTD", step="year", stepmode="todate"),
                                dict(count=1, label="1y", step="year", stepmode="backward"),
                                dict(step="all")
                            ])
                        ),
                        rangeslider=dict(visible=True),
                        type="date"
                    )
                )
        else:
            plt.figure(figsize=self.visualization_config['figure_size'])
            sns.lineplot(data=data, x='date', y='score', hue='activity_type')
            plt.title('Performance Trends Over Time')
            plt.xlabel('Date')
            plt.ylabel('Performance Score')
            fig = plt.gcf()
            
        return fig

    def _generate_category_heatmap(self, data: pd.DataFrame, 
                                 interactive: bool,
                                 drill_down: bool) -> go.Figure:
        """Generate category performance heatmap with drill-down capability."""
        pivot_data = data.pivot_table(
            values='score',
            index='category',
            columns='date',
            aggfunc='mean'
        )
        
        if interactive:
            fig = px.imshow(pivot_data,
                          title='Category Performance Heatmap',
                          labels=dict(x='Date', y='Category', color='Score'),
                          template='plotly_white')
            
            if drill_down:
                # Add drill-down buttons
                fig.update_layout(
                    updatemenus=[
                        dict(
                            type="buttons",
                            direction="right",
                            active=0,
                            x=0.57,
                            y=1.2,
                            buttons=list([
                                dict(
                                    label="All Categories",
                                    method="update",
                                    args=[{"visible": [True] * len(pivot_data.index)}]
                                ),
                                dict(
                                    label="By Activity Type",
                                    method="update",
                                    args=[{"visible": [True if act == data['activity_type'].iloc[0] else False 
                                                     for act in data['activity_type']]}]
                                )
                            ]),
                        )
                    ]
                )
                
                # Add hover information
                fig.update_traces(
                    hovertemplate="<br>".join([
                        "Date: %{x}",
                        "Category: %{y}",
                        "Score: %{z}",
                        "Activity Type: %{customdata}"
                    ]),
                    customdata=data['activity_type']
                )
                
                # Add color scale selector
                fig.update_layout(
                    coloraxis=dict(
                        colorscale=[
                            [0, 'rgb(255,255,255)'],
                            [0.5, 'rgb(255,255,0)'],
                            [1, 'rgb(255,0,0)']
                        ],
                        colorbar=dict(
                            title='Score',
                            titleside='right',
                            ticks='outside'
                        )
                    )
                )
                
                # Add annotations for significant changes
                for i, row in enumerate(pivot_data.index):
                    for j, col in enumerate(pivot_data.columns):
                        if j > 0:
                            prev_score = pivot_data.iloc[i, j-1]
                            curr_score = pivot_data.iloc[i, j]
                            if abs(curr_score - prev_score) > 10:  # Significant change threshold
                                fig.add_annotation(
                                    x=col,
                                    y=row,
                                    text=f"{'+' if curr_score > prev_score else ''}{curr_score - prev_score:.1f}",
                                    showarrow=False,
                                    font=dict(
                                        size=10,
                                        color='black'
                                    )
                                )
        else:
            plt.figure(figsize=self.visualization_config['figure_size'])
            sns.heatmap(pivot_data, annot=True, cmap='viridis')
            plt.title('Category Performance Heatmap')
            fig = plt.gcf()
            
        return fig

    def _generate_activity_distribution_plot(self, data: pd.DataFrame, 
                                           interactive: bool,
                                           drill_down: bool) -> go.Figure:
        """Generate activity type distribution plot with drill-down capability."""
        if interactive:
            fig = px.pie(data, names='activity_type', values='count',
                        title='Activity Type Distribution',
                        template='plotly_white')
            
            if drill_down:
                # Add drill-down buttons
                fig.update_layout(
                    updatemenus=[
                        dict(
                            type="buttons",
                            direction="right",
                            active=0,
                            x=0.57,
                            y=1.2,
                            buttons=list([
                                dict(
                                    label="All Activities",
                                    method="update",
                                    args=[{"visible": [True] * len(data['activity_type'].unique())}]
                                ),
                                dict(
                                    label="By Category",
                                    method="update",
                                    args=[{"visible": [True if cat == data['category'].iloc[0] else False 
                                                     for cat in data['category']]}]
                                )
                            ]),
                        )
                    ]
                )
                
                # Add hover information
                fig.update_traces(
                    hovertemplate="<br>".join([
                        "Activity Type: %{label}",
                        "Count: %{value}",
                        "Percentage: %{percent}",
                        "Category: %{customdata}"
                    ]),
                    customdata=data['category'],
                    textinfo='label+percent',
                    textposition='inside'
                )
                
                # Add pull effect for emphasis
                pull_values = [0.1 if count == max(data['count']) else 0 
                             for count in data['count']]
                fig.update_traces(pull=pull_values)
                
                # Add annotations for total count
                fig.add_annotation(
                    text=f"Total Activities: {sum(data['count'])}",
                    x=0.5,
                    y=0.5,
                    showarrow=False,
                    font=dict(
                        size=14,
                        color='black'
                    )
                )
        else:
            plt.figure(figsize=self.visualization_config['figure_size'])
            data['activity_type'].value_counts().plot(kind='pie', autopct='%1.1f%%')
            plt.title('Activity Type Distribution')
            fig = plt.gcf()
            
        return fig

    def _generate_improvement_trends_plot(self, data: pd.DataFrame, 
                                        interactive: bool,
                                        drill_down: bool) -> go.Figure:
        """Generate improvement trends plot with drill-down capability."""
        if interactive:
            fig = px.bar(data, x='category', y='improvement',
                        color='activity_type',
                        title='Improvement Trends by Category',
                        labels={'improvement': 'Improvement Score', 'category': 'Category'},
                        template='plotly_white')
            
            if drill_down:
                # Add drill-down buttons
                fig.update_layout(
                    updatemenus=[
                        dict(
                            type="buttons",
                            direction="right",
                            active=0,
                            x=0.57,
                            y=1.2,
                            buttons=list([
                                dict(
                                    label="All Categories",
                                    method="update",
                                    args=[{"visible": [True] * len(data['category'].unique())}]
                                ),
                                dict(
                                    label="By Activity Type",
                                    method="update",
                                    args=[{"visible": [True if act == data['activity_type'].iloc[0] else False 
                                                     for act in data['activity_type']]}]
                                )
                            ]),
                        )
                    ]
                )
                
                # Add hover information
                fig.update_traces(
                    hovertemplate="<br>".join([
                        "Category: %{x}",
                        "Improvement: %{y}",
                        "Activity Type: %{text}",
                        "Baseline: %{customdata[0]}",
                        "Current: %{customdata[1]}"
                    ]),
                    text=data['activity_type'],
                    customdata=data[['baseline_score', 'current_score']].values
                )
                
                # Add reference line for average improvement
                avg_improvement = data['improvement'].mean()
                fig.add_hline(
                    y=avg_improvement,
                    line_dash="dash",
                    line_color="red",
                    annotation_text=f"Average Improvement: {avg_improvement:.1f}",
                    annotation_position="top right"
                )
                
                # Add trend line
                fig.add_trace(
                    go.Scatter(
                        x=data['category'],
                        y=data['improvement'].rolling(window=3).mean(),
                        mode='lines',
                        name='Trend',
                        line=dict(color='black', width=2, dash='dot')
                    )
                )
                
                # Add annotations for significant improvements
                for i, row in data.iterrows():
                    if row['improvement'] > avg_improvement * 1.5:  # 50% above average
                        fig.add_annotation(
                            x=row['category'],
                            y=row['improvement'],
                            text="↑",
                            showarrow=False,
                            font=dict(
                                size=14,
                                color='green'
                            )
                        )
        else:
            plt.figure(figsize=self.visualization_config['figure_size'])
            sns.barplot(data=data, x='category', y='improvement', hue='activity_type')
            plt.title('Improvement Trends by Category')
            plt.xlabel('Category')
            plt.ylabel('Improvement Score')
            fig = plt.gcf()
            
        return fig

    def _generate_skill_analysis_plot(self, data: pd.DataFrame, 
                                    interactive: bool,
                                    drill_down: bool) -> go.Figure:
        """Generate skill analysis plot with drill-down capability."""
        if interactive:
            fig = px.bar(data, x='score', y='skill',
                        color='category',
                        title='Skill Analysis',
                        labels={'score': 'Score', 'skill': 'Skill'},
                        template='plotly_white',
                        orientation='h')
            
            if drill_down:
                # Add drill-down buttons
                fig.update_layout(
                    updatemenus=[
                        dict(
                            type="buttons",
                            direction="right",
                            active=0,
                            x=0.57,
                            y=1.2,
                            buttons=list([
                                dict(
                                    label="All Skills",
                                    method="update",
                                    args=[{"visible": [True] * len(data['skill'].unique())}]
                                ),
                                dict(
                                    label="By Category",
                                    method="update",
                                    args=[{"visible": [True if cat == data['category'].iloc[0] else False 
                                                     for cat in data['category']]}]
                                )
                            ]),
                        )
                    ]
                )
                
                # Add hover information
                fig.update_traces(
                    hovertemplate="<br>".join([
                        "Skill: %{y}",
                        "Score: %{x}",
                        "Category: %{text}",
                        "Progress: %{customdata[0]}%",
                        "Target: %{customdata[1]}"
                    ]),
                    text=data['category'],
                    customdata=data[['progress', 'target_score']].values
                )
                
                # Add target line
                fig.add_vline(
                    x=data['target_score'].mean(),
                    line_dash="dash",
                    line_color="red",
                    annotation_text="Average Target",
                    annotation_position="top right"
                )
                
                # Add progress indicators
                for i, row in data.iterrows():
                    if row['progress'] >= 100:  # Skill mastered
                        fig.add_annotation(
                            x=row['score'],
                            y=row['skill'],
                            text="✓",
                            showarrow=False,
                            font=dict(
                                size=14,
                                color='green'
                            )
                        )
                    elif row['progress'] < 50:  # Needs attention
                        fig.add_annotation(
                            x=row['score'],
                            y=row['skill'],
                            text="!",
                            showarrow=False,
                            font=dict(
                                size=14,
                                color='red'
                            )
                        )
                
                # Add skill grouping
                fig.update_layout(
                    yaxis=dict(
                        categoryorder='array',
                        categoryarray=data.sort_values('category')['skill'].unique()
                    )
                )
        else:
            plt.figure(figsize=self.visualization_config['figure_size'])
            sns.barplot(data=data, x='score', y='skill', hue='category')
            plt.title('Skill Analysis')
            plt.xlabel('Score')
            plt.ylabel('Skill')
            fig = plt.gcf()
            
        return fig

    def _generate_sankey_diagram(self, data: pd.DataFrame, 
                               interactive: bool,
                               drill_down: bool) -> go.Figure:
        """Generate Sankey diagram with drill-down capability."""
        nodes = list(set(data['source'].unique()) | set(data['target'].unique()))
        node_indices = {node: i for i, node in enumerate(nodes)}
        
        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=nodes,
                color="blue"
            ),
            link=dict(
                source=[node_indices[src] for src in data['source']],
                target=[node_indices[tgt] for tgt in data['target']],
                value=data['value']
            )
        )])
        
        if drill_down:
            # Add drill-down buttons
            fig.update_layout(
                updatemenus=[
                    dict(
                        type="buttons",
                        direction="right",
                        active=0,
                        x=0.57,
                        y=1.2,
                        buttons=list([
                            dict(
                                label="All Flows",
                                method="update",
                                args=[{"visible": [True] * len(data['source'].unique())}]
                            ),
                            dict(
                                label="By Category",
                                method="update",
                                args=[{"visible": [True if cat == data['category'].iloc[0] else False 
                                                 for cat in data['category']]}]
                            )
                        ]),
                    )
                ]
            )
            
            # Add hover information
            fig.update_traces(
                hovertemplate="<br>".join([
                    "Source: %{source.label}",
                    "Target: %{target.label}",
                    "Value: %{value}",
                    "Category: %{customdata}"
                ]),
                customdata=data['category']
            )
            
            # Add node grouping
            node_colors = {}
            for node in nodes:
                if node in data['source'].values:
                    node_colors[node] = 'blue'
                elif node in data['target'].values:
                    node_colors[node] = 'green'
                else:
                    node_colors[node] = 'gray'
            
            fig.update_traces(
                node=dict(
                    color=[node_colors[node] for node in nodes]
                )
            )
            
            # Add flow annotations
            for i, row in data.iterrows():
                if row['value'] > data['value'].mean() * 1.5:  # Significant flow
                    fig.add_annotation(
                        x=0.5,
                        y=0.5,
                        text=f"Major Flow: {row['source']} → {row['target']}",
                        showarrow=False,
                        font=dict(
                            size=12,
                            color='black'
                        )
                    )
            
            # Add flow direction indicators
            fig.update_layout(
                annotations=[
                    dict(
                        x=0.1,
                        y=0.5,
                        text="← Flow Direction →",
                        showarrow=False,
                        font=dict(
                            size=12,
                            color='black'
                        )
                    )
                ]
            )
        
        fig.update_layout(title_text="Activity Flow Analysis", font_size=10)
        return fig

    def _generate_treemap(self, data: pd.DataFrame, 
                         interactive: bool,
                         drill_down: bool) -> go.Figure:
        """Generate treemap with drill-down capability."""
        fig = go.Figure(go.Treemap(
            labels=data['label'],
            parents=data['parent'],
            values=data['value'],
            marker=dict(
                colors=data['color'],
                colorscale='Viridis'
            )
        ))
        
        if drill_down:
            # Add drill-down buttons
            fig.update_layout(
                updatemenus=[
                    dict(
                        type="buttons",
                        direction="right",
                        active=0,
                        x=0.57,
                        y=1.2,
                        buttons=list([
                            dict(
                                label="All Levels",
                                method="update",
                                args=[{"visible": [True] * len(data['label'].unique())}]
                            ),
                            dict(
                                label="By Category",
                                method="update",
                                args=[{"visible": [True if cat == data['category'].iloc[0] else False 
                                                 for cat in data['category']]}]
                            )
                        ]),
                    )
                ]
            )
            
            # Add hover information
            fig.update_traces(
                hovertemplate="<br>".join([
                    "Label: %{label}",
                    "Value: %{value}",
                    "Parent: %{parent}",
                    "Category: %{customdata}"
                ]),
                customdata=data['category']
            )
            
            # Add color scale selector
            fig.update_layout(
                coloraxis=dict(
                    colorscale=[
                        [0, 'rgb(255,255,255)'],
                        [0.5, 'rgb(255,255,0)'],
                        [1, 'rgb(255,0,0)']
                    ],
                    colorbar=dict(
                        title='Value',
                        titleside='right',
                        ticks='outside'
                    )
                )
            )
            
            # Add annotations for significant values
            for i, row in data.iterrows():
                if row['value'] > data['value'].mean() * 2:  # Significant value
                    fig.add_annotation(
                        x=0.5,
                        y=0.5,
                        text=f"High Value: {row['label']}",
                        showarrow=False,
                        font=dict(
                            size=12,
                            color='black'
                        )
                    )
            
            # Add value percentage labels
            fig.update_traces(
                textinfo="label+value+percent parent+percent entry",
                textposition="middle center"
            )
            
            # Add custom hover text for parent nodes
            parent_nodes = data[data['parent'] == '']['label'].unique()
            for parent in parent_nodes:
                parent_value = data[data['label'] == parent]['value'].sum()
                fig.add_annotation(
                    x=0.5,
                    y=0.5,
                    text=f"Total: {parent_value}",
                    showarrow=False,
                    font=dict(
                        size=14,
                        color='black'
                    )
                )
        
        fig.update_layout(
            title="Activity Hierarchy",
            margin=dict(t=50, l=25, r=25, b=25)
        )
        
        return fig

    def _generate_sunburst_chart(self, data: pd.DataFrame, 
                               interactive: bool,
                               drill_down: bool) -> go.Figure:
        """Generate sunburst chart with drill-down capability."""
        fig = go.Figure(go.Sunburst(
            labels=data['label'],
            parents=data['parent'],
            values=data['value'],
            marker=dict(
                colors=data['color'],
                colorscale='Viridis'
            )
        ))
        
        if drill_down:
            # Add drill-down buttons
            fig.update_layout(
                updatemenus=[
                    dict(
                        type="buttons",
                        direction="right",
                        active=0,
                        x=0.57,
                        y=1.2,
                        buttons=list([
                            dict(
                                label="All Levels",
                                method="update",
                                args=[{"visible": [True] * len(data['label'].unique())}]
                            ),
                            dict(
                                label="By Category",
                                method="update",
                                args=[{"visible": [True if cat == data['category'].iloc[0] else False 
                                                 for cat in data['category']]}]
                            )
                        ]),
                    )
                ]
            )
            
            # Add hover information
            fig.update_traces(
                hovertemplate="<br>".join([
                    "Label: %{label}",
                    "Value: %{value}",
                    "Parent: %{parent}",
                    "Category: %{customdata}"
                ]),
                customdata=data['category']
            )
            
            # Add color scale selector
            fig.update_layout(
                coloraxis=dict(
                    colorscale=[
                        [0, 'rgb(255,255,255)'],
                        [0.5, 'rgb(255,255,0)'],
                        [1, 'rgb(255,0,0)']
                    ],
                    colorbar=dict(
                        title='Value',
                        titleside='right',
                        ticks='outside'
                    )
                )
            )
            
            # Add annotations for significant values
            for i, row in data.iterrows():
                if row['value'] > data['value'].mean() * 2:  # Significant value
                    fig.add_annotation(
                        x=0.5,
                        y=0.5,
                        text=f"High Value: {row['label']}",
                        showarrow=False,
                        font=dict(
                            size=12,
                            color='black'
                        )
                    )
            
            # Add value percentage labels
            fig.update_traces(
                textinfo="label+value+percent parent+percent entry",
                textposition="middle center"
            )
            
            # Add custom hover text for parent nodes
            parent_nodes = data[data['parent'] == '']['label'].unique()
            for parent in parent_nodes:
                parent_value = data[data['label'] == parent]['value'].sum()
                fig.add_annotation(
                    x=0.5,
                    y=0.5,
                    text=f"Total: {parent_value}",
                    showarrow=False,
                    font=dict(
                        size=14,
                        color='black'
                    )
                )
            
            # Add radial labels
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100]
                    )
                )
            )
        
        fig.update_layout(
            title="Activity Relationships",
            margin=dict(t=50, l=25, r=25, b=25)
        )
        
        return fig

    def _generate_violin_plot(self, data: pd.DataFrame, 
                            interactive: bool,
                            drill_down: bool) -> go.Figure:
        """Generate violin plot with drill-down capability."""
        fig = go.Figure()
        
        for category in data['category'].unique():
            category_data = data[data['category'] == category]
            fig.add_trace(go.Violin(
                y=category_data['score'],
                name=category,
                box_visible=True,
                meanline_visible=True
            ))
        
        if drill_down:
            # Add drill-down buttons
            fig.update_layout(
                updatemenus=[
                    dict(
                        type="buttons",
                        direction="right",
                        active=0,
                        x=0.57,
                        y=1.2,
                        buttons=list([
                            dict(
                                label="All Categories",
                                method="update",
                                args=[{"visible": [True] * len(data['category'].unique())}]
                            ),
                            dict(
                                label="By Activity Type",
                                method="update",
                                args=[{"visible": [True if act == data['activity_type'].iloc[0] else False 
                                                 for act in data['activity_type']]}]
                            )
                        ]),
                    )
                ]
            )
            
            # Add hover information
            fig.update_traces(
                hovertemplate="<br>".join([
                    "Category: %{name}",
                    "Score: %{y}",
                    "Activity Type: %{customdata}",
                    "Count: %{count}"
                ]),
                customdata=data['activity_type']
            )
            
            # Add reference lines
            mean_score = data['score'].mean()
            std_score = data['score'].std()
            
            fig.add_hline(
                y=mean_score,
                line_dash="dash",
                line_color="red",
                annotation_text="Mean Score",
                annotation_position="top right"
            )
            
            fig.add_hline(
                y=mean_score + std_score,
                line_dash="dot",
                line_color="blue",
                annotation_text="+1 SD",
                annotation_position="top right"
            )
            
            fig.add_hline(
                y=mean_score - std_score,
                line_dash="dot",
                line_color="blue",
                annotation_text="-1 SD",
                annotation_position="bottom right"
            )
            
            # Add annotations for outliers
            for category in data['category'].unique():
                category_data = data[data['category'] == category]
                q1 = category_data['score'].quantile(0.25)
                q3 = category_data['score'].quantile(0.75)
                iqr = q3 - q1
                outliers = category_data[
                    (category_data['score'] < q1 - 1.5 * iqr) |
                    (category_data['score'] > q3 + 1.5 * iqr)
                ]
                
                for _, outlier in outliers.iterrows():
                    fig.add_annotation(
                        x=category,
                        y=outlier['score'],
                        text="!",
                        showarrow=False,
                        font=dict(
                            size=14,
                            color='red'
                        )
                    )
            
            # Add distribution statistics
            for category in data['category'].unique():
                category_data = data[data['category'] == category]
                stats = {
                    'mean': category_data['score'].mean(),
                    'median': category_data['score'].median(),
                    'std': category_data['score'].std()
                }
                
                fig.add_annotation(
                    x=category,
                    y=stats['mean'],
                    text=f"μ={stats['mean']:.1f}\nσ={stats['std']:.1f}",
                    showarrow=False,
                    font=dict(
                        size=10,
                        color='black'
                    )
                )
        
        fig.update_layout(
            title="Performance Distribution by Category",
            yaxis_title="Score",
            showlegend=True
        )
        
        return fig

    def _add_accessibility_features(self, fig: go.Figure, viz_type: str) -> None:
        """Add accessibility features to the visualization."""
        if self.visualization_config['accessibility']['screen_reader']:
            fig.update_layout(
                title_text=f"{viz_type.replace('_', ' ').title()} - Screen Reader Friendly",
                title_x=0.5
            )
            
        if self.visualization_config['accessibility']['high_contrast']:
            fig.update_layout(
                paper_bgcolor='white',
                plot_bgcolor='white',
                font=dict(color='black')
            )

    def _save_visualization(self, fig: Union[go.Figure, plt.Figure], 
                          student_id: str, 
                          viz_type: str) -> Dict[str, str]:
        """Save visualization in multiple formats."""
        student_dir = os.path.join(self.export_dir, student_id)
        os.makedirs(student_dir, exist_ok=True)
        
        output_paths = {}
        
        # Save as HTML for interactive visualizations
        if isinstance(fig, go.Figure):
            html_path = os.path.join(student_dir, f"{viz_type}.html")
            fig.write_html(html_path)
            output_paths['html'] = html_path
            
            # Save as PNG
            png_path = os.path.join(student_dir, f"{viz_type}.png")
            fig.write_image(png_path)
            output_paths['png'] = png_path
            
            # Save as SVG
            svg_path = os.path.join(student_dir, f"{viz_type}.svg")
            fig.write_image(svg_path)
            output_paths['svg'] = svg_path
            
            # Save as PDF
            pdf_path = os.path.join(student_dir, f"{viz_type}.pdf")
            fig.write_image(pdf_path)
            output_paths['pdf'] = pdf_path
            
            # Save as GIF (for animated visualizations)
            if hasattr(fig, 'frames') and fig.frames:
                gif_path = os.path.join(student_dir, f"{viz_type}.gif")
                self._save_animation(fig, gif_path)
                output_paths['gif'] = gif_path
                
                # Save as MP4
                mp4_path = os.path.join(student_dir, f"{viz_type}.mp4")
                self._save_video(fig, mp4_path)
                output_paths['mp4'] = mp4_path
                
        else:  # Matplotlib figure
            # Save as PNG
            png_path = os.path.join(student_dir, f"{viz_type}.png")
            fig.savefig(png_path, dpi=300, bbox_inches='tight')
            output_paths['png'] = png_path
            
            # Save as PDF
            pdf_path = os.path.join(student_dir, f"{viz_type}.pdf")
            fig.savefig(pdf_path, bbox_inches='tight')
            output_paths['pdf'] = pdf_path
            
            # Save as SVG
            svg_path = os.path.join(student_dir, f"{viz_type}.svg")
            fig.savefig(svg_path, bbox_inches='tight')
            output_paths['svg'] = svg_path
            
        return output_paths

    def _save_animation(self, fig: go.Figure, output_path: str) -> None:
        """Save animation as GIF."""
        frames = []
        for frame in fig.frames:
            # Convert frame to image
            frame_fig = go.Figure(data=frame.data, layout=fig.layout)
            frame_img = frame_fig.to_image(format="png")
            frames.append(imageio.imread(BytesIO(frame_img)))
            
        imageio.mimsave(output_path, frames, duration=0.5)

    def _save_video(self, fig: go.Figure, output_path: str) -> None:
        """Save visualization as a video with fallback for when moviepy is not available."""
        if not MOVIEPY_AVAILABLE:
            # Fallback: Save as static image
            fig.write_image(output_path.replace('.mp4', '.png'))
            return
            
        try:
            # Convert figure to video using moviepy
            frames = []
            for frame in fig.frames:
                img = frame.data[0].image
                frames.append(img)
            
            clip = mpe.ImageSequenceClip(frames, fps=24)
            clip.write_videofile(output_path)
        except Exception as e:
            # Fallback to static image if video creation fails
            fig.write_image(output_path.replace('.mp4', '.png')) 