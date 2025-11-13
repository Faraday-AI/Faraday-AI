from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import logging
from sqlalchemy.orm import Session
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller
from io import BytesIO
import base64
import json
import csv
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from jinja2 import Template
import xlsxwriter

from .safety_incident_manager import SafetyIncidentManager
from .risk_assessment_manager import RiskAssessmentManager
from .equipment_manager import EquipmentManager

class SafetyReportGenerator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.incident_manager = SafetyIncidentManager()
        self.risk_manager = RiskAssessmentManager()
        self.equipment_manager = EquipmentManager()
        
        # Default report configuration
        self.report_config = {
            "title": "Safety Report",
            "company_name": "Faraday AI",
            "logo_url": None,
            "color_scheme": {
                "primary": "#2c3e50",
                "secondary": "#34495e",
                "accent": "#3498db",
                "background": "#ffffff",
                "text": "#333333",
                "success": "#2ecc71",
                "warning": "#f1c40f",
                "danger": "#e74c3c"
            },
            "font_family": "Arial",
            "font_sizes": {
                "title": 24,
                "heading": 18,
                "subheading": 16,
                "body": 12
            },
            "include_summary": True,
            "include_statistics": True,
            "include_visualizations": True,
            "include_recommendations": True,
            "section_order": [
                "summary",
                "statistics",
                "statistical_analysis",
                "visualizations",
                "recommendations"
            ],
            "theme": "default",
            "custom_css": "",
            "custom_js": ""
        }
        
        # Available themes
        self.themes = {
            "default": {
                "primary": "#2c3e50",
                "secondary": "#34495e",
                "accent": "#3498db",
                "background": "#ffffff",
                "text": "#333333"
            },
            "dark": {
                "primary": "#ecf0f1",
                "secondary": "#bdc3c7",
                "accent": "#3498db",
                "background": "#2c3e50",
                "text": "#ecf0f1"
            },
            "modern": {
                "primary": "#1abc9c",
                "secondary": "#16a085",
                "accent": "#3498db",
                "background": "#f9f9f9",
                "text": "#2c3e50"
            }
        }
        
        # HTML template for reports
        self.html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>{{ title }}</title>
            <style>
                body { 
                    font-family: {{ font_family }}, sans-serif; 
                    margin: 20px;
                    color: {{ color_scheme.primary }};
                }
                h1 { 
                    color: {{ color_scheme.primary }};
                    border-bottom: 2px solid {{ color_scheme.accent }};
                    padding-bottom: 10px;
                }
                h2 { 
                    color: {{ color_scheme.secondary }};
                    margin-top: 20px;
                }
                .header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 20px;
                }
                .logo {
                    max-height: 50px;
                }
                .chart { 
                    margin: 20px 0;
                    border: 1px solid #ddd;
                    padding: 10px;
                    border-radius: 5px;
                }
                .recommendation { 
                    background: #f8f9fa; 
                    padding: 15px;
                    margin: 10px 0;
                    border-left: 4px solid {{ color_scheme.accent }};
                    border-radius: 3px;
                }
                .statistics { 
                    margin: 20px 0;
                    background: #f8f9fa;
                    padding: 15px;
                    border-radius: 5px;
                }
                table { 
                    border-collapse: collapse; 
                    width: 100%;
                    margin: 10px 0;
                }
                th, td { 
                    border: 1px solid #ddd; 
                    padding: 8px; 
                    text-align: left;
                }
                th { 
                    background-color: {{ color_scheme.secondary }};
                    color: white;
                }
                .summary {
                    background: #f8f9fa;
                    padding: 15px;
                    margin: 20px 0;
                    border-radius: 5px;
                }
                .footer {
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 1px solid #ddd;
                    text-align: center;
                    color: #666;
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{{ title }}</h1>
                {% if logo_url %}
                <img src="{{ logo_url }}" alt="Logo" class="logo">
                {% endif %}
            </div>
            {% if include_summary %}
            <div class="summary">
                <h2>Executive Summary</h2>
                {{ summary | safe }}
            </div>
            {% endif %}
            {% for section in sections %}
            <h2>{{ section.title }}</h2>
            {{ section.content | safe }}
            {% endfor %}
            <div class="footer">
                <p>Generated by {{ company_name }} on {{ date }}</p>
            </div>
        </body>
        </html>
        """

    def configure_report(self, config: Dict[str, Any]) -> None:
        """Configure report appearance and content."""
        if "theme" in config and config["theme"] in self.themes:
            config["color_scheme"] = self.themes[config["theme"]]
        self.report_config.update(config)

    async def generate_safety_report(
        self,
        class_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        format: str = "pdf",
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """Generate a comprehensive safety report."""
        try:
            # Get db session if not provided (for service-to-service calls)
            if db is None:
                from app.core.database import get_db
                db = next(get_db())
            
            # Get statistics from all managers
            # Note: class_id parameter needs to be converted to activity_id if needed
            incident_stats = await self.incident_manager.get_incident_statistics(
                student_id=None, activity_id=class_id if class_id else None, start_date=start_date, end_date=end_date, db=db
            )
            risk_stats = await self.risk_manager.get_assessment_statistics(
                class_id=class_id, start_date=start_date, end_date=end_date, db=db
            )
            equipment_stats = await self.equipment_manager.get_equipment_statistics(
                class_id=class_id, start_date=start_date, end_date=end_date, db=db
            )
            
            # Perform advanced statistical analysis
            statistical_analysis = await self._perform_statistical_analysis(
                incident_stats, risk_stats, equipment_stats
            )
            
            # Generate visualizations (pass statistical_analysis for advanced visualizations)
            visualizations = await self._generate_visualizations(
                incident_stats, risk_stats, equipment_stats, statistical_analysis
            )
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(
                incident_stats, risk_stats, equipment_stats
            )
            
            # Generate executive summary
            summary = await self._generate_summary(
                incident_stats, risk_stats, equipment_stats,
                statistical_analysis
            )
            
            # Prepare report data
            report_data = {
                "statistics": {
                    "incidents": incident_stats,
                    "risk_assessments": risk_stats,
                    "equipment": equipment_stats
                },
                "statistical_analysis": statistical_analysis,
                "visualizations": visualizations,
                "recommendations": recommendations,
                "summary": summary or "No safety data found for the specified date range."
            }
            
            # Generate report in requested format
            if format.lower() == "pdf":
                pdf_content = await self._convert_to_pdf(report_data)
                return {
                    "generated": True,
                    "format": "pdf",
                    "content": pdf_content,
                    **report_data  # Include report data
                }
            elif format.lower() == "html":
                html_content = await self._convert_to_html(report_data)
                return {
                    "generated": True,
                    "format": "html",
                    "content": html_content,
                    **report_data  # Include report data
                }
            elif format.lower() == "excel":
                excel_content = await self._convert_to_excel(report_data)
                return {
                    "generated": True,
                    "format": "excel",
                    "content": excel_content,
                    **report_data  # Include report data
                }
            else:
                return report_data
            
        except Exception as e:
            self.logger.error(f"Error generating safety report: {str(e)}")
            # Return minimal report structure instead of empty dict
            return {
                "summary": f"Error generating report: {str(e)}",
                "statistics": {"incidents": {}, "risk_assessments": {}, "equipment": {}},
                "statistical_analysis": {},
                "visualizations": {},
                "recommendations": [],
                "trends": {}
            }
        finally:
            plt.close('all')

    async def _perform_statistical_analysis(
        self,
        incident_stats: Dict[str, Any],
        risk_stats: Dict[str, Any],
        equipment_stats: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform advanced statistical analysis on the data."""
        analysis = {}
        
        # Incident analysis
        if "trends" in incident_stats and incident_stats["trends"]:
            # Calculate trend statistics
            dates = sorted(incident_stats["trends"].keys())
            values = [incident_stats["trends"][date] for date in dates]
            
            # Linear regression for trend prediction - only if we have sufficient data
            # LinearRegression requires at least 1 sample
            if len(values) > 0 and len(set(values)) > 1:  # Need at least 2 distinct values for meaningful regression
                try:
                    X = np.array(range(len(values))).reshape(-1, 1)
                    y = np.array(values)
                    # Double-check shape before fitting
                    if X.shape[0] > 0 and y.shape[0] > 0 and X.shape[0] == y.shape[0]:
                        model = LinearRegression()
                        model.fit(X, y)
                        analysis["incident_trend"] = {
                            "slope": float(model.coef_[0]),
                            "intercept": float(model.intercept_),
                            "r_squared": float(model.score(X, y))
                        }
                except Exception as e:
                    self.logger.warning(f"Linear regression failed: {str(e)}")
            
            # Calculate correlation with risk levels
            if "by_risk_level" in risk_stats and risk_stats["by_risk_level"]:
                risk_values = list(risk_stats["by_risk_level"].values())
                if len(risk_values) == len(values) and len(values) > 0:
                    try:
                        correlation = stats.pearsonr(values, risk_values)
                        analysis["risk_incident_correlation"] = {
                            "correlation": float(correlation[0]),
                            "p_value": float(correlation[1])
                        }
                    except Exception as e:
                        self.logger.warning(f"Correlation calculation failed: {str(e)}")
        
        # Equipment analysis
        if "by_age" in equipment_stats and "by_maintenance" in equipment_stats:
            age_data = list(equipment_stats["by_age"].values()) if equipment_stats.get("by_age") else []
            maintenance_data = list(equipment_stats["by_maintenance"].values()) if equipment_stats.get("by_maintenance") else []
            
            # Only calculate correlation if we have data
            if len(age_data) > 0 and len(maintenance_data) > 0 and len(age_data) == len(maintenance_data):
                try:
                    correlation = stats.pearsonr(age_data, maintenance_data)
                    analysis["equipment_correlation"] = {
                        "correlation": float(correlation[0]),
                        "p_value": float(correlation[1])
                    }
                except Exception as e:
                    self.logger.warning(f"Equipment correlation calculation failed: {str(e)}")
        
        # Time series analysis
        if "trends" in incident_stats and incident_stats["trends"]:
            dates = sorted(incident_stats["trends"].keys())
            values = [incident_stats["trends"][date] for date in dates]
            
            # Only perform time series analysis if we have sufficient data
            if len(values) > 7:  # Need at least 7 days for weekly seasonality
                try:
                    series = pd.Series(values, index=pd.to_datetime(dates))
                    decomposition = seasonal_decompose(series, period=7)  # Weekly seasonality
                    analysis["seasonal_decomposition"] = {
                        "trend": decomposition.trend.tolist(),
                        "seasonal": decomposition.seasonal.tolist(),
                        "residual": decomposition.resid.tolist()
                    }
                    
                    # Stationarity test
                    adf_result = adfuller(values)
                    analysis["stationarity"] = {
                        "adf_statistic": float(adf_result[0]),
                        "p_value": float(adf_result[1]),
                        "critical_values": {k: float(v) for k, v in adf_result[4].items()}
                    }
                except Exception as e:
                    self.logger.warning(f"Time series analysis failed: {str(e)}")
        
        # Clustering analysis
        if "by_type" in incident_stats and "by_severity" in incident_stats:
            types = list(incident_stats["by_type"].keys()) if incident_stats.get("by_type") else []
            severities = list(incident_stats["by_severity"].keys()) if incident_stats.get("by_severity") else []
            
            # Only perform clustering if we have data
            if len(types) > 0 and len(severities) > 0:
                try:
                    # Prepare data for clustering
                    data = np.zeros((len(types), len(severities)))
                    
                    for i, type_name in enumerate(types):
                        for j, severity in enumerate(severities):
                            type_data = incident_stats["by_type"][type_name]
                            if isinstance(type_data, dict):
                                data[i, j] = type_data.get(severity, 0)
                            else:
                                data[i, j] = 0
                    
                    # Only perform clustering if we have sufficient data points
                    if data.sum() > 0 and len(types) >= 2:
                        # Normalize data
                        scaler = StandardScaler()
                        normalized_data = scaler.fit_transform(data)
                        
                        # Perform clustering (use min of n_clusters or number of types)
                        n_clusters = min(3, len(types))
                        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
                        clusters = kmeans.fit_predict(normalized_data)
                        
                        analysis["incident_clusters"] = {
                            "cluster_centers": kmeans.cluster_centers_.tolist(),
                            "labels": clusters.tolist(),
                            "inertia": float(kmeans.inertia_)
                        }
                except Exception as e:
                    self.logger.warning(f"Clustering analysis failed: {str(e)}")
        
        return analysis

    async def _generate_visualizations(
        self,
        incident_stats: Dict[str, Any],
        risk_stats: Dict[str, Any],
        equipment_stats: Dict[str, Any],
        statistical_analysis: Optional[Dict[str, Any]] = None
    ) -> Dict[str, str]:
        """Generate visualizations for the report."""
        visualizations = {}
        
        # Incident severity pie chart - only if we have data
        if "by_severity" in incident_stats and incident_stats["by_severity"] and len(incident_stats["by_severity"]) > 0:
            try:
                plt.figure(figsize=(10, 6))
                values = list(incident_stats["by_severity"].values())
                labels = list(incident_stats["by_severity"].keys())
                if values and sum(values) > 0:  # Only plot if there's actual data
                    plt.pie(values, labels=labels, autopct='%1.1f%%')
                plt.title("Incident Severity Distribution")
                buf = BytesIO()
                plt.savefig(buf, format='png')
                buf.seek(0)
                visualizations["incident_severity"] = base64.b64encode(buf.getvalue()).decode('utf-8')
                plt.close()
            except Exception as e:
                self.logger.warning(f"Incident severity visualization failed: {str(e)}")
                plt.close()
        
        # Risk level bar chart
        if "by_risk_level" in risk_stats and risk_stats["by_risk_level"]:
            try:
                plt.figure(figsize=(10, 6))
                plt.bar(
                    list(risk_stats["by_risk_level"].keys()),
                    list(risk_stats["by_risk_level"].values())
                )
                plt.title("Risk Level Distribution")
                buf = BytesIO()
                plt.savefig(buf, format='png')
                buf.seek(0)
                visualizations["risk_levels"] = base64.b64encode(buf.getvalue()).decode('utf-8')
                plt.close()
            except Exception as e:
                self.logger.warning(f"Risk level visualization failed: {str(e)}")
        
        # Equipment maintenance status
        if "by_maintenance" in equipment_stats and equipment_stats["by_maintenance"]:
            try:
                plt.figure(figsize=(10, 6))
                equipment_data = {}
                for check in equipment_stats["by_maintenance"].items():
                    equipment_data[check[0]] = check[1]
                plt.pie(
                    list(equipment_data.values()),
                    labels=list(equipment_data.keys()),
                    autopct='%1.1f%%'
                )
                plt.title("Equipment Maintenance Status")
                buf = BytesIO()
                plt.savefig(buf, format='png')
                buf.seek(0)
                visualizations["equipment_maintenance"] = base64.b64encode(buf.getvalue()).decode('utf-8')
                plt.close()
            except Exception as e:
                self.logger.warning(f"Equipment maintenance visualization failed: {str(e)}")
        
        # Incident trends over time - only if we have data
        if "trends" in incident_stats and incident_stats["trends"] and len(incident_stats["trends"]) > 0:
            try:
                plt.figure(figsize=(12, 6))
                dates = sorted(incident_stats["trends"].keys())
                values = [incident_stats["trends"][date] for date in dates]
                if values and len(values) > 0:  # Only plot if we have data points
                    plt.plot(dates, values, marker='o')
                plt.title("Incident Trends Over Time")
                plt.xticks(rotation=45)
                plt.grid(True)
                buf = BytesIO()
                plt.savefig(buf, format='png')
                buf.seek(0)
                visualizations["incident_trends"] = base64.b64encode(buf.getvalue()).decode('utf-8')
                plt.close()
            except Exception as e:
                self.logger.warning(f"Incident trends visualization failed: {str(e)}")
                plt.close()
        
        # Risk correlation heatmap - only if we have data
        if "common_risks" in risk_stats and risk_stats["common_risks"]:
            try:
                plt.figure(figsize=(10, 8))
                risk_data = pd.DataFrame(risk_stats["common_risks"])
                if not risk_data.empty and risk_data.size > 0:  # Check if dataframe has data
                    sns.heatmap(risk_data, annot=True, cmap="YlOrRd")
                plt.title("Risk Correlation Heatmap")
                buf = BytesIO()
                plt.savefig(buf, format='png')
                buf.seek(0)
                visualizations["risk_correlation"] = base64.b64encode(buf.getvalue()).decode('utf-8')
                plt.close()
            except Exception as e:
                self.logger.warning(f"Risk correlation visualization failed: {str(e)}")
                plt.close()
        
        # Equipment age vs maintenance status scatter plot
        if "by_age" in equipment_stats and "by_maintenance" in equipment_stats:
            plt.figure(figsize=(10, 6))
            age_data = equipment_stats["by_age"]
            maintenance_data = equipment_stats["by_maintenance"]
            plt.scatter(list(age_data.keys()), list(maintenance_data.values()))
            plt.title("Equipment Age vs Maintenance Status")
            plt.xlabel("Age Status")
            plt.ylabel("Maintenance Status Count")
            buf = BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            visualizations["equipment_age_maintenance"] = base64.b64encode(buf.getvalue()).decode('utf-8')
            plt.close()
        
        # Stacked bar chart for incident types by severity
        if "by_type" in incident_stats and "by_severity" in incident_stats:
            plt.figure(figsize=(12, 6))
            types = list(incident_stats["by_type"].keys())
            severities = list(incident_stats["by_severity"].keys())
            data = np.zeros((len(types), len(severities)))
            
            for i, type_name in enumerate(types):
                for j, severity in enumerate(severities):
                    data[i, j] = incident_stats["by_type"][type_name].get(severity, 0)
            
            bottom = np.zeros(len(types))
            for j, severity in enumerate(severities):
                plt.bar(types, data[:, j], bottom=bottom, label=severity)
                bottom += data[:, j]
            
            plt.title("Incident Types by Severity")
            plt.legend()
            plt.xticks(rotation=45)
            buf = BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            visualizations["incident_type_severity"] = base64.b64encode(buf.getvalue()).decode('utf-8')
            plt.close()
        
        # Radar chart for risk assessment categories
        if "by_category" in risk_stats:
            plt.figure(figsize=(8, 8))
            categories = list(risk_stats["by_category"].keys())
            values = list(risk_stats["by_category"].values())
            
            angles = np.linspace(0, 2*np.pi, len(categories), endpoint=False)
            values = np.concatenate((values, [values[0]]))
            angles = np.concatenate((angles, [angles[0]]))
            
            ax = plt.subplot(111, polar=True)
            ax.plot(angles, values)
            ax.fill(angles, values, alpha=0.25)
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(categories)
            plt.title("Risk Assessment Categories")
            buf = BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            visualizations["risk_categories"] = base64.b64encode(buf.getvalue()).decode('utf-8')
            plt.close()
        
        # Box plot for equipment maintenance times
        if "maintenance_times" in equipment_stats:
            plt.figure(figsize=(10, 6))
            data = [equipment_stats["maintenance_times"][status] 
                   for status in equipment_stats["maintenance_times"].keys()]
            plt.boxplot(data, labels=list(equipment_stats["maintenance_times"].keys()))
            plt.title("Equipment Maintenance Times")
            plt.ylabel("Days")
            buf = BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            visualizations["maintenance_times"] = base64.b64encode(buf.getvalue()).decode('utf-8')
            plt.close()
        
        # Scatter plot for incident severity vs response time
        if "response_times" in incident_stats and "by_severity" in incident_stats:
            plt.figure(figsize=(10, 6))
            severities = list(incident_stats["by_severity"].keys())
            response_times = [incident_stats["response_times"].get(s, 0) for s in severities]
            plt.scatter(severities, response_times, s=100, alpha=0.6)
            plt.title("Incident Severity vs Response Time")
            plt.xlabel("Severity")
            plt.ylabel("Average Response Time (minutes)")
            buf = BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            visualizations["severity_response"] = base64.b64encode(buf.getvalue()).decode('utf-8')
            plt.close()
        
        # Bubble chart for risk assessment impact
        if "by_risk_level" in risk_stats and "impact_scores" in risk_stats:
            plt.figure(figsize=(10, 6))
            risk_levels = list(risk_stats["by_risk_level"].keys())
            frequencies = list(risk_stats["by_risk_level"].values())
            impacts = [risk_stats["impact_scores"].get(l, 0) for l in risk_levels]
            
            # Scale bubble sizes
            sizes = [f * 100 for f in frequencies]
            
            plt.scatter(risk_levels, impacts, s=sizes, alpha=0.6)
            plt.title("Risk Level vs Impact (Bubble Size = Frequency)")
            plt.xlabel("Risk Level")
            plt.ylabel("Impact Score")
            buf = BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            visualizations["risk_impact"] = base64.b64encode(buf.getvalue()).decode('utf-8')
            plt.close()
        
        # Time series decomposition plot - now available via parameter
        if statistical_analysis and "seasonal_decomposition" in statistical_analysis:
            try:
                decomposition = statistical_analysis["seasonal_decomposition"]
                plt.figure(figsize=(12, 8))
                
                # Plot original, trend, seasonal, and residual
                dates = sorted(incident_stats.get("trends", {}).keys()) if "trends" in incident_stats else []
                if dates and len(decomposition.get("trend", [])) > 0:
                    plt.subplot(4, 1, 1)
                    plt.plot(dates, [incident_stats["trends"][d] for d in dates], label="Original")
                    plt.title("Time Series Decomposition")
                    plt.legend()
                    
                    plt.subplot(4, 1, 2)
                    plt.plot(dates[:len(decomposition["trend"])], decomposition["trend"], label="Trend")
                    plt.legend()
                    
                    plt.subplot(4, 1, 3)
                    plt.plot(dates[:len(decomposition["seasonal"])], decomposition["seasonal"], label="Seasonal")
                    plt.legend()
                    
                    plt.subplot(4, 1, 4)
                    plt.plot(dates[:len(decomposition["residual"])], decomposition["residual"], label="Residual")
                    plt.legend()
                    
                    plt.tight_layout()
                    buf = BytesIO()
                    plt.savefig(buf, format='png')
                    buf.seek(0)
                    visualizations["time_series_decomposition"] = base64.b64encode(buf.getvalue()).decode('utf-8')
                    plt.close()
            except Exception as e:
                self.logger.warning(f"Time series decomposition visualization failed: {str(e)}")
                plt.close()
        
        # Cluster visualization - now available via parameter
        if statistical_analysis and "incident_clusters" in statistical_analysis:
            try:
                clusters = statistical_analysis["incident_clusters"]
                if "cluster_centers" in clusters and "labels" in clusters:
                    plt.figure(figsize=(10, 6))
                    
                    # Plot cluster centers
                    centers = np.array(clusters["cluster_centers"])
                    labels = clusters["labels"]
                    
                    if len(centers) > 0 and centers.shape[1] >= 2:
                        # Plot clusters
                        for i, center in enumerate(centers):
                            cluster_points = [j for j, label in enumerate(labels) if label == i]
                            if cluster_points:
                                plt.scatter(
                                    [centers[i, 0]] * len(cluster_points),
                                    [centers[i, 1]] * len(cluster_points),
                                    label=f"Cluster {i}",
                                    alpha=0.6
                                )
                        
                        plt.title("Incident Clustering Analysis")
                        plt.xlabel("Feature 1")
                        plt.ylabel("Feature 2")
                        plt.legend()
                        buf = BytesIO()
                        plt.savefig(buf, format='png')
                        buf.seek(0)
                        visualizations["incident_clusters"] = base64.b64encode(buf.getvalue()).decode('utf-8')
                        plt.close()
            except Exception as e:
                self.logger.warning(f"Cluster visualization failed: {str(e)}")
                plt.close()
        
        return visualizations

    async def _generate_recommendations(
        self,
        incident_stats: Dict[str, Any],
        risk_stats: Dict[str, Any],
        equipment_stats: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations based on safety statistics."""
        recommendations = []
        
        # Incident-based recommendations
        total_incidents = incident_stats.get("total", 0)
        if total_incidents > 10:
            recommendations.append(
                "High number of incidents detected. Review and strengthen safety protocols."
            )
        elif total_incidents > 5:
            recommendations.append(
                "Moderate number of incidents. Consider additional safety measures."
            )
        
        # Check incident severity distribution
        by_severity = incident_stats.get("by_severity", {})
        if by_severity.get("high", 0) > 0 or by_severity.get("critical", 0) > 0:
            recommendations.append(
                "High or critical severity incidents detected. Immediate action required."
            )
        
        # Risk assessment recommendations
        total_risks = risk_stats.get("total", 0)
        by_risk_level = risk_stats.get("by_risk_level", {})
        if by_risk_level.get("high", 0) > 0:
            recommendations.append(
                "High risk assessments identified. Review activities and implement mitigation strategies."
            )
        
        # Equipment recommendations
        if equipment_stats:
            maintenance_due = equipment_stats.get("maintenance_due", 0)
            if maintenance_due > 0:
                recommendations.append(
                    f"{maintenance_due} equipment items need maintenance. Schedule inspections."
                )
            
            damaged_count = equipment_stats.get("damaged_count", 0)
            if damaged_count > 0:
                recommendations.append(
                    f"{damaged_count} damaged equipment items found. Replace or repair immediately."
                )
        
        # Default recommendations if no specific issues found
        if not recommendations:
            recommendations.append("Continue maintaining current safety standards.")
            recommendations.append("Schedule regular safety protocol reviews.")
            recommendations.append("Maintain regular equipment inspections.")
        
        return recommendations

    async def _generate_summary(
        self,
        incident_stats: Dict[str, Any],
        risk_stats: Dict[str, Any],
        equipment_stats: Dict[str, Any],
        statistical_analysis: Dict[str, Any]
    ) -> str:
        """Generate an executive summary of the report."""
        summary = []
        
        # Overall safety status
        total_incidents = incident_stats.get("total", 0)
        total_risks = risk_stats.get("total", 0)
        summary.append(f"During the reporting period, there were {total_incidents} safety incidents "
                      f"and {total_risks} risk assessments conducted.")
        
        # Trend analysis
        if "incident_trend" in statistical_analysis:
            trend = statistical_analysis["incident_trend"]
            if trend["slope"] > 0:
                summary.append("The number of incidents shows an increasing trend.")
            elif trend["slope"] < 0:
                summary.append("The number of incidents shows a decreasing trend.")
            else:
                summary.append("The number of incidents remains stable.")
        
        # Risk correlation
        if "risk_incident_correlation" in statistical_analysis:
            correlation = statistical_analysis["risk_incident_correlation"]
            if correlation["p_value"] < 0.05:
                if correlation["correlation"] > 0:
                    summary.append("There is a significant positive correlation between risk levels and incidents.")
                else:
                    summary.append("There is a significant negative correlation between risk levels and incidents.")
        
        # Equipment status
        if "by_maintenance" in equipment_stats:
            maintenance_issues = sum(
                count for status, count in equipment_stats["by_maintenance"].items()
                if status in ["needs_repair", "needs_replacement"]
            )
            if maintenance_issues > 0:
                summary.append(f"{maintenance_issues} pieces of equipment require maintenance attention.")
        
        return "<br>".join(summary)

    async def _convert_to_pdf(self, report_data: Dict[str, Any]) -> bytes:
        """Convert report data to PDF format."""
        try:
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []
            
            # Add header with logo if configured
            if self.report_config["logo_url"]:
                story.append(Image(self.report_config["logo_url"], width=100, height=50))
            
            # Add title
            story.append(Paragraph(self.report_config["title"], styles["Title"]))
            story.append(Spacer(1, 12))
            
            # Add summary if configured
            if self.report_config["include_summary"]:
                story.append(Paragraph("Executive Summary", styles["Heading1"]))
                story.append(Paragraph(report_data["summary"], styles["Normal"]))
                story.append(Spacer(1, 12))
            
            # Add statistics if configured
            if self.report_config["include_statistics"]:
                story.append(Paragraph("Statistics", styles["Heading1"]))
                for category, data in report_data["statistics"].items():
                    story.append(Paragraph(category, styles["Heading2"]))
                    for key, value in data.items():
                        if isinstance(value, dict):
                            story.append(Paragraph(f"{key}:", styles["Normal"]))
                            for subkey, subvalue in value.items():
                                story.append(Paragraph(f"  {subkey}: {subvalue}", styles["Normal"]))
                        else:
                            story.append(Paragraph(f"{key}: {value}", styles["Normal"]))
                    story.append(Spacer(1, 12))
            
            # Add statistical analysis
            story.append(Paragraph("Statistical Analysis", styles["Heading1"]))
            for category, analysis in report_data["statistical_analysis"].items():
                story.append(Paragraph(category, styles["Heading2"]))
                for key, value in analysis.items():
                    story.append(Paragraph(f"{key}: {value}", styles["Normal"]))
                story.append(Spacer(1, 6))
            
            # Add visualizations if configured
            if self.report_config["include_visualizations"] and report_data.get("visualizations"):
                story.append(Paragraph("Visualizations", styles["Heading1"]))
                for title, img_data in report_data["visualizations"].items():
                    try:
                        # Try to decode base64 image data
                        if isinstance(img_data, str):
                            img_bytes = base64.b64decode(img_data)
                            img = Image(BytesIO(img_bytes))
                            img.drawHeight = 200
                            img.drawWidth = 400
                            story.append(img)
                            story.append(Spacer(1, 12))
                    except Exception as e:
                        # Skip if image decode fails
                        self.logger.warning(f"Could not add visualization {title}: {str(e)}")
                        continue
            
            # Add recommendations if configured
            if self.report_config["include_recommendations"]:
                story.append(Paragraph("Recommendations", styles["Heading1"]))
                for rec in report_data["recommendations"]:
                    story.append(Paragraph(rec, styles["Normal"]))
                    story.append(Spacer(1, 6))
            
            # Add footer
            story.append(Spacer(1, 20))
            story.append(Paragraph(
                f"Generated by {self.report_config['company_name']} on {datetime.now().strftime('%Y-%m-%d')}",
                styles["Italic"]
            ))
            
            doc.build(story)
            return buffer.getvalue()
            
        except Exception as e:
            self.logger.error(f"Error converting to PDF: {str(e)}")
            return b""

    async def _convert_to_html(self, report_data: Dict[str, Any]) -> str:
        """Convert report data to HTML format."""
        try:
            sections = []
            
            # Generate sections in configured order
            for section_name in self.report_config["section_order"]:
                if section_name == "summary" and self.report_config["include_summary"]:
                    sections.append({
                        "title": "Executive Summary",
                        "content": f"<div class='summary'>{report_data['summary']}</div>"
                    })
                elif section_name == "statistics" and self.report_config["include_statistics"]:
                    # Statistics section...
                    pass
                elif section_name == "statistical_analysis":
                    # Statistical analysis section...
                    pass
                elif section_name == "visualizations" and self.report_config["include_visualizations"]:
                    # Visualizations section...
                    pass
                elif section_name == "recommendations" and self.report_config["include_recommendations"]:
                    # Recommendations section...
                    pass
            
            # Render template with configuration
            template = Template(self.html_template)
            return template.render(
                title=self.report_config["title"],
                company_name=self.report_config["company_name"],
                logo_url=self.report_config["logo_url"],
                color_scheme=self.report_config["color_scheme"],
                font_family=self.report_config["font_family"],
                font_sizes=self.report_config["font_sizes"],
                include_summary=self.report_config["include_summary"],
                sections=sections,
                date=datetime.now().strftime("%Y-%m-%d"),
                custom_css=self.report_config["custom_css"],
                custom_js=self.report_config["custom_js"]
            )
            
        except Exception as e:
            self.logger.error(f"Error converting to HTML: {str(e)}")
            return ""

    async def _convert_to_excel(self, report_data: Dict[str, Any]) -> bytes:
        """Convert report data to Excel format."""
        try:
            buffer = BytesIO()
            workbook = xlsxwriter.Workbook(buffer)
            
            # Add summary sheet
            summary_sheet = workbook.add_worksheet("Summary")
            summary_sheet.write(0, 0, "Executive Summary")
            summary_sheet.write(1, 0, report_data["summary"])
            
            # Add statistics sheets
            for category, data in report_data["statistics"].items():
                sheet = workbook.add_worksheet(category)
                row = 0
                for key, value in data.items():
                    if isinstance(value, dict):
                        sheet.write(row, 0, key)
                        row += 1
                        for subkey, subvalue in value.items():
                            sheet.write(row, 1, subkey)
                            sheet.write(row, 2, subvalue)
                            row += 1
                    else:
                        sheet.write(row, 0, key)
                        sheet.write(row, 1, value)
                        row += 1
            
            # Add statistical analysis sheet
            analysis_sheet = workbook.add_worksheet("Statistical Analysis")
            row = 0
            for category, analysis in report_data["statistical_analysis"].items():
                analysis_sheet.write(row, 0, category)
                row += 1
                for key, value in analysis.items():
                    analysis_sheet.write(row, 1, key)
                    analysis_sheet.write(row, 2, value)
                    row += 1
            
            # Add recommendations sheet
            rec_sheet = workbook.add_worksheet("Recommendations")
            for i, rec in enumerate(report_data["recommendations"]):
                rec_sheet.write(i, 0, rec)
            
            # Add metadata sheet
            meta_sheet = workbook.add_worksheet("Metadata")
            meta_sheet.write(0, 0, "Generated by")
            meta_sheet.write(0, 1, self.report_config["company_name"])
            meta_sheet.write(1, 0, "Generated on")
            meta_sheet.write(1, 1, datetime.now().strftime("%Y-%m-%d"))
            
            workbook.close()
            return buffer.getvalue()
            
        except Exception as e:
            self.logger.error(f"Error converting to Excel: {str(e)}")
            return b""

    async def generate_incident_report(
        self,
        incident_id: str,
        format: str = "pdf"
    ) -> Dict[str, Any]:
        """Generate a detailed report for a specific incident."""
        try:
            incident = await self.incident_manager.get_incident(incident_id)
            if not incident:
                return {
                    "success": False,
                    "message": "Incident not found"
                }
            
            # Get related data
            risk_assessments = await self.risk_manager.get_assessments(
                class_id=incident.class_id,
                start_date=incident.date,
                end_date=incident.date
            )
            
            equipment_checks = await self.equipment_manager.get_equipment_checks(
                class_id=incident.class_id,
                start_date=incident.date,
                end_date=incident.date
            )
            
            # Prepare report data
            report_data = {
                "incident": incident.__dict__,
                "related_risk_assessments": [assess.__dict__ for assess in risk_assessments],
                "related_equipment_checks": [check.__dict__ for check in equipment_checks],
                "recommendations": await self._generate_incident_recommendations(
                    incident, risk_assessments, equipment_checks
                )
            }
            
            if format.lower() == "pdf":
                return await self._convert_incident_to_pdf(report_data)
            elif format.lower() == "html":
                return await self._convert_incident_to_html(report_data)
            elif format.lower() == "excel":
                return await self._convert_incident_to_excel(report_data)
            else:
                return report_data
            
        except Exception as e:
            self.logger.error(f"Error generating incident report: {str(e)}")
            return {}

    async def _generate_incident_recommendations(
        self,
        incident: Any,
        risk_assessments: List[Any],
        equipment_checks: List[Any]
    ) -> List[str]:
        """Generate recommendations for a specific incident."""
        recommendations = []
        
        # Analyze incident details
        if incident.severity in ["high", "critical"]:
            recommendations.append(
                "High severity incident. Review and update safety protocols."
            )
        
        # Analyze related risk assessments
        for assessment in risk_assessments:
            if assessment.risk_level == "high":
                recommendations.append(
                    f"High risk assessment for {assessment.activity_type}. "
                    "Consider additional safety measures."
                )
        
        # Analyze equipment checks
        for check in equipment_checks:
            if check.maintenance_status in ["needs_repair", "needs_replacement"]:
                recommendations.append(
                    f"Equipment {check.equipment_id} needs attention. "
                    "Schedule maintenance or replacement."
                )
        
        return recommendations

    async def _convert_incident_to_pdf(self, report_data: Dict[str, Any]) -> bytes:
        """Convert incident report data to PDF format."""
        try:
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []
            
            # Add title
            story.append(Paragraph("Incident Report", styles["Title"]))
            story.append(Spacer(1, 12))
            
            # Add incident details
            story.append(Paragraph("Incident Details", styles["Heading1"]))
            for key, value in report_data["incident"].items():
                if key not in ["_sa_instance_state"]:
                    story.append(Paragraph(f"{key}: {value}", styles["Normal"]))
            story.append(Spacer(1, 12))
            
            # Add related risk assessments
            story.append(Paragraph("Related Risk Assessments", styles["Heading1"]))
            for assessment in report_data["related_risk_assessments"]:
                story.append(Paragraph("Assessment", styles["Heading2"]))
                for key, value in assessment.items():
                    if key not in ["_sa_instance_state"]:
                        story.append(Paragraph(f"{key}: {value}", styles["Normal"]))
                story.append(Spacer(1, 6))
            
            # Add related equipment checks
            story.append(Paragraph("Related Equipment Checks", styles["Heading1"]))
            for check in report_data["related_equipment_checks"]:
                story.append(Paragraph("Equipment Check", styles["Heading2"]))
                for key, value in check.items():
                    if key not in ["_sa_instance_state"]:
                        story.append(Paragraph(f"{key}: {value}", styles["Normal"]))
                story.append(Spacer(1, 6))
            
            # Add recommendations
            story.append(Paragraph("Recommendations", styles["Heading1"]))
            for rec in report_data["recommendations"]:
                story.append(Paragraph(rec, styles["Normal"]))
                story.append(Spacer(1, 6))
            
            doc.build(story)
            return buffer.getvalue()
            
        except Exception as e:
            self.logger.error(f"Error converting incident to PDF: {str(e)}")
            return b""

    async def _convert_incident_to_html(self, report_data: Dict[str, Any]) -> str:
        """Convert incident report data to HTML format."""
        try:
            sections = []
            
            # Add incident details section
            incident_html = "<div class='incident-details'>"
            for key, value in report_data["incident"].items():
                if key not in ["_sa_instance_state"]:
                    incident_html += f"<p><strong>{key}:</strong> {value}</p>"
            incident_html += "</div>"
            sections.append({"title": "Incident Details", "content": incident_html})
            
            # Add risk assessments section
            risk_html = "<div class='risk-assessments'>"
            for assessment in report_data["related_risk_assessments"]:
                risk_html += "<div class='assessment'>"
                for key, value in assessment.items():
                    if key not in ["_sa_instance_state"]:
                        risk_html += f"<p><strong>{key}:</strong> {value}</p>"
                risk_html += "</div>"
            risk_html += "</div>"
            sections.append({"title": "Related Risk Assessments", "content": risk_html})
            
            # Add equipment checks section
            equipment_html = "<div class='equipment-checks'>"
            for check in report_data["related_equipment_checks"]:
                equipment_html += "<div class='check'>"
                for key, value in check.items():
                    if key not in ["_sa_instance_state"]:
                        equipment_html += f"<p><strong>{key}:</strong> {value}</p>"
                equipment_html += "</div>"
            equipment_html += "</div>"
            sections.append({"title": "Related Equipment Checks", "content": equipment_html})
            
            # Add recommendations section
            rec_html = "<div class='recommendations'>"
            for rec in report_data["recommendations"]:
                rec_html += f"<div class='recommendation'>{rec}</div>"
            rec_html += "</div>"
            sections.append({"title": "Recommendations", "content": rec_html})
            
            # Render template
            template = Template(self.html_template)
            return template.render(title="Incident Report", sections=sections)
            
        except Exception as e:
            self.logger.error(f"Error converting incident to HTML: {str(e)}")
            return ""

    async def _convert_incident_to_excel(self, report_data: Dict[str, Any]) -> bytes:
        """Convert incident report data to Excel format."""
        try:
            buffer = BytesIO()
            workbook = xlsxwriter.Workbook(buffer)
            
            # Add incident details sheet
            incident_sheet = workbook.add_worksheet("Incident Details")
            row = 0
            for key, value in report_data["incident"].items():
                if key not in ["_sa_instance_state"]:
                    incident_sheet.write(row, 0, key)
                    incident_sheet.write(row, 1, str(value))
                    row += 1
            
            # Add risk assessments sheet
            risk_sheet = workbook.add_worksheet("Risk Assessments")
            row = 0
            for assessment in report_data["related_risk_assessments"]:
                for key, value in assessment.items():
                    if key not in ["_sa_instance_state"]:
                        risk_sheet.write(row, 0, key)
                        risk_sheet.write(row, 1, str(value))
                        row += 1
                row += 1
            
            # Add equipment checks sheet
            equipment_sheet = workbook.add_worksheet("Equipment Checks")
            row = 0
            for check in report_data["related_equipment_checks"]:
                for key, value in check.items():
                    if key not in ["_sa_instance_state"]:
                        equipment_sheet.write(row, 0, key)
                        equipment_sheet.write(row, 1, str(value))
                        row += 1
                row += 1
            
            # Add recommendations sheet
            rec_sheet = workbook.add_worksheet("Recommendations")
            for i, rec in enumerate(report_data["recommendations"]):
                rec_sheet.write(i, 0, rec)
            
            workbook.close()
            return buffer.getvalue()
            
        except Exception as e:
            self.logger.error(f"Error converting incident to Excel: {str(e)}")
            return b"" 

    async def generate_equipment_safety_report(
        self,
        equipment_data: Dict[str, Any],
        format: str = "pdf"
    ) -> Dict[str, Any]:
        """Generate equipment safety report."""
        try:
            report_id = f"equipment_safety_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            # Mock equipment safety data
            equipment_stats = {
                "total_equipment": equipment_data.get("total_count", 0),
                "inspected_equipment": equipment_data.get("inspected_count", 0),
                "maintenance_due": equipment_data.get("maintenance_due", 0),
                "damaged_equipment": equipment_data.get("damaged_count", 0),
                "safety_score": 0.85
            }
            
            report_data = {
                "report_id": report_id,
                "report_type": "equipment_safety",
                "generated_at": datetime.utcnow().isoformat(),
                "equipment_stats": equipment_stats,
                "recommendations": [
                    "Schedule regular equipment inspections",
                    "Replace damaged equipment",
                    "Update maintenance schedule"
                ]
            }
            
            if format.lower() == "pdf":
                report_content = await self._convert_to_pdf(report_data)
                return {
                    "generated": True,
                    "report_id": report_id,
                    "format": format,
                    "content": report_content
                }
            elif format.lower() == "html":
                report_content = await self._convert_to_html(report_data)
                return {
                    "generated": True,
                    "report_id": report_id,
                    "format": format,
                    "content": report_content
                }
            elif format.lower() == "json":
                # Return the report data directly as JSON structure
                return report_data
            else:
                return {"generated": False, "error": f"Unsupported format: {format}"}
        except Exception as e:
            self.logger.error(f"Error generating equipment safety report: {str(e)}")
            return {"generated": False, "error": str(e)}

    async def generate_environmental_safety_report(
        self,
        environment_data: Dict[str, Any],
        format: str = "pdf"
    ) -> Dict[str, Any]:
        """Generate environmental safety report."""
        try:
            report_id = f"environmental_safety_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            # Mock environmental safety data
            environmental_stats = {
                "facility_condition": environment_data.get("condition", "good"),
                "lighting_quality": environment_data.get("lighting", "adequate"),
                "surface_condition": environment_data.get("surface", "safe"),
                "temperature": environment_data.get("temperature", "comfortable"),
                "air_quality": environment_data.get("air_quality", "good"),
                "safety_score": 0.78
            }
            
            report_data = {
                "report_id": report_id,
                "report_type": "environmental_safety",
                "generated_at": datetime.utcnow().isoformat(),
                "environmental_stats": environmental_stats,
                "recommendations": [
                    "Improve lighting in designated areas",
                    "Maintain proper temperature control",
                    "Regular facility inspections"
                ]
            }
            
            if format.lower() == "pdf":
                report_content = await self._convert_to_pdf(report_data)
                return {
                    "generated": True,
                    "report_id": report_id,
                    "format": format,
                    "content": report_content
                }
            elif format.lower() == "html":
                report_content = await self._convert_to_html(report_data)
                return {
                    "generated": True,
                    "report_id": report_id,
                    "format": format,
                    "content": report_content
                }
            elif format.lower() == "json":
                # Return the report data directly as JSON structure
                return report_data
            else:
                return {"generated": False, "error": f"Unsupported format: {format}"}
        except Exception as e:
            self.logger.error(f"Error generating environmental safety report: {str(e)}")
            return {"generated": False, "error": str(e)}

    async def generate_student_safety_report(
        self,
        student_data: Dict[str, Any],
        format: str = "pdf"
    ) -> Dict[str, Any]:
        """Generate student safety report."""
        try:
            report_id = f"student_safety_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            # Mock student safety data
            student_stats = {
                "total_students": student_data.get("total_count", 0),
                "students_with_medical_conditions": student_data.get("medical_conditions", 0),
                "students_requiring_special_attention": student_data.get("special_attention", 0),
                "safety_incidents": student_data.get("incidents", 0),
                "safety_score": 0.92
            }
            
            report_data = {
                "report_id": report_id,
                "report_type": "student_safety",
                "generated_at": datetime.utcnow().isoformat(),
                "student_stats": student_stats,
                "recommendations": [
                    "Review medical conditions regularly",
                    "Provide additional supervision where needed",
                    "Implement safety training programs"
                ]
            }
            
            if format.lower() == "pdf":
                report_content = await self._convert_to_pdf(report_data)
                return {
                    "generated": True,
                    "report_id": report_id,
                    "format": format,
                    "content": report_content
                }
            elif format.lower() == "html":
                report_content = await self._convert_to_html(report_data)
                return {
                    "generated": True,
                    "report_id": report_id,
                    "format": format,
                    "content": report_content
                }
            elif format.lower() == "json":
                # Return the report data directly as JSON structure
                return report_data
            else:
                return {"generated": False, "error": f"Unsupported format: {format}"}
        except Exception as e:
            self.logger.error(f"Error generating student safety report: {str(e)}")
            return {"generated": False, "error": str(e)}

    async def generate_comprehensive_safety_report(
        self,
        comprehensive_data: Dict[str, Any],
        format: str = "pdf"
    ) -> Dict[str, Any]:
        """Generate comprehensive safety report."""
        try:
            report_id = f"comprehensive_safety_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            # Mock comprehensive safety data
            comprehensive_stats = {
                "overall_safety_score": 0.85,
                "equipment_safety": 0.88,
                "environmental_safety": 0.82,
                "student_safety": 0.90,
                "incident_rate": 0.05,
                "risk_level": "low"
            }
            
            report_data = {
                "report_id": report_id,
                "report_type": "comprehensive_safety",
                "generated_at": datetime.utcnow().isoformat(),
                "comprehensive_stats": comprehensive_stats,
                "sections": [
                    "Equipment Safety Analysis",
                    "Environmental Safety Assessment",
                    "Student Safety Overview",
                    "Incident Analysis",
                    "Risk Assessment",
                    "Recommendations"
                ],
                "recommendations": [
                    "Maintain current safety protocols",
                    "Continue regular inspections",
                    "Monitor incident trends",
                    "Update safety training materials"
                ]
            }
            
            if format.lower() == "pdf":
                report_content = await self._convert_to_pdf(report_data)
                return {
                    "generated": True,
                    "report_id": report_id,
                    "format": format,
                    "content": report_content
                }
            elif format.lower() == "html":
                report_content = await self._convert_to_html(report_data)
                return {
                    "generated": True,
                    "report_id": report_id,
                    "format": format,
                    "content": report_content
                }
            elif format.lower() == "json":
                # Return the report data directly as JSON structure
                return report_data
            else:
                return {"generated": False, "error": f"Unsupported format: {format}"}
        except Exception as e:
            self.logger.error(f"Error generating comprehensive safety report: {str(e)}")
            return {"generated": False, "error": str(e)} 