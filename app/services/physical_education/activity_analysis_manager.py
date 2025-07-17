"""Activity analysis manager for physical education."""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import pandas as pd
from sqlalchemy.orm import Session
from app.core.database import get_db

# Import models
from app.models.physical_education.activity.models import Activity
from app.models.physical_education.pe_enums.pe_types import (
    ActivityType,
    DifficultyLevel,
    EquipmentRequirement,
    ConfidenceLevel,
    PerformanceLevel,
    AnalysisType,
    AnalysisLevel,
    AnalysisStatus,
    AnalysisTrigger
)
from app.models.activity_adaptation.activity.activity import ActivityCategoryAssociation
from app.models.physical_education.activity.models import (
    StudentActivityPerformance,
    StudentActivityPreference
)
from app.models.physical_education.exercise.models import Exercise
from app.models.student import Student

class ActivityAnalysisManager:
    """Service for analyzing physical education activities."""
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ActivityAnalysisManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.logger = logging.getLogger("activity_analysis_manager")
        self.db = None
        
        # Analysis components
        self.analysis_history = []
        self.performance_benchmarks = {}
        self.injury_risk_factors = {}
        self.movement_patterns = {}
        self.feedback_history = {}
        self.progress_tracking = {}
        
        # Analysis metrics
        self.custom_metrics = {}
        self.environmental_factors = {}
        self.equipment_usage = {}
        self.fatigue_analysis = {}
        self.technique_variations = {}
        self.movement_consistency = {}
        self.biomechanical_analysis = {}
        self.energy_efficiency = {}
        self.symmetry_analysis = {}
        self.skill_level_assessment = {}
        self.recovery_analysis = {}
        self.adaptation_analysis = {}
        self.performance_prediction = {}
        
        # Caching and optimization
        self.analysis_cache = {}
        self.batch_cache = {}
        
        # Analysis configuration
        self.analysis_config = {
            'min_data_points': 5,
            'confidence_threshold': 0.8,
            'performance_window': 30,  # days
            'trend_window': 7,  # days
            'batch_size': 100
        }
    
    async def initialize(self):
        """Initialize the activity analysis manager."""
        try:
            # Get database session using context manager
            db_gen = get_db()
            self.db = await anext(db_gen)
            
            # Load analysis benchmarks
            await self.load_performance_benchmarks()
            
            self.logger.info("Activity Analysis Manager initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing Activity Analysis Manager: {str(e)}")
            raise
    
    async def cleanup(self):
        """Cleanup the activity analysis manager."""
        try:
            # Clear all data
            self.analysis_history.clear()
            self.performance_benchmarks.clear()
            self.injury_risk_factors.clear()
            self.movement_patterns.clear()
            self.feedback_history.clear()
            self.progress_tracking.clear()
            self.custom_metrics.clear()
            self.environmental_factors.clear()
            self.equipment_usage.clear()
            self.fatigue_analysis.clear()
            self.technique_variations.clear()
            self.movement_consistency.clear()
            self.biomechanical_analysis.clear()
            self.energy_efficiency.clear()
            self.symmetry_analysis.clear()
            self.skill_level_assessment.clear()
            self.recovery_analysis.clear()
            self.adaptation_analysis.clear()
            self.performance_prediction.clear()
            self.analysis_cache.clear()
            self.batch_cache.clear()
            
            # Reset service references
            self.db = None
            
            self.logger.info("Activity Analysis Manager cleaned up successfully")
        except Exception as e:
            self.logger.error(f"Error cleaning up Activity Analysis Manager: {str(e)}")
            raise

    async def analyze_student_performance(self, student_id: str, 
                                        start_date: Optional[datetime] = None,
                                        end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Analyze student's performance across activities."""
        # Get performance data
        performance_data = await self._get_performance_data(student_id, start_date, end_date)
        
        if len(performance_data) < self.analysis_config['min_data_points']:
            raise ValueError(f"Insufficient data points for analysis. Minimum required: {self.analysis_config['min_data_points']}")
        
        # Convert performance data to DataFrame for analysis
        df = pd.DataFrame(performance_data)
        
        # Calculate overall metrics
        overall_metrics = self._calculate_overall_metrics(df)
        
        # Calculate performance by type and category
        type_metrics = self._calculate_performance_by_type(df)
        category_metrics = self._calculate_performance_by_category(df)
        
        # Identify strengths and areas for improvement
        strengths = self._identify_strengths(df)
        improvements = self._identify_improvements(df)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            df,
            strengths,
            improvements
        )
        
        return {
            'student_id': student_id,
            'analysis_period': {
                'start_date': start_date.isoformat() if start_date else None,
                'end_date': end_date.isoformat() if end_date else None
            },
            'overall_metrics': overall_metrics,
            'type_metrics': type_metrics,
            'category_metrics': category_metrics,
            'strengths': strengths,
            'improvements': improvements,
            'recommendations': recommendations
        }

    async def _get_performance_data(self, student_id: str,
                                  start_date: Optional[datetime],
                                  end_date: Optional[datetime]) -> List[Dict[str, Any]]:
        """Retrieve and prepare performance data."""
        try:
            query = self.db.query(StudentActivityPerformance).filter(
                StudentActivityPerformance.student_id == student_id
            )
            
            if start_date:
                query = query.filter(StudentActivityPerformance.created_at >= start_date)
            if end_date:
                query = query.filter(StudentActivityPerformance.created_at <= end_date)
            
            performances = query.all()
            
            return [
                {
                    'id': perf.id,
                    'activity_id': perf.activity_id,
                    'score': perf.score,
                    'created_at': perf.created_at,
                    'activity_type': perf.activity.activity_type,
                    'difficulty': perf.activity.difficulty,
                    'completed': True  # Assuming recorded performances are completed
                }
                for perf in performances
            ]
        except Exception as e:
            self.logger.error(f"Error retrieving performance data: {str(e)}")
            return []

    def _calculate_overall_metrics(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate overall performance metrics."""
        metrics = {
            'average_score': float(data['score'].mean()),
            'median_score': float(data['score'].median()),
            'std_deviation': float(data['score'].std()),
            'min_score': float(data['score'].min()),
            'max_score': float(data['score'].max()),
            'total_activities': len(data),
            'completion_rate': float(data['completed'].mean()) if 'completed' in data else None,
            'consistency_score': self._calculate_consistency_score(data),
            'improvement_rate': self._calculate_improvement_rate(data)
        }
        
        return metrics

    def _calculate_performance_by_type(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate performance metrics by activity type."""
        type_metrics = {}
        
        for activity_type in data['activity_type'].unique():
            type_data = data[data['activity_type'] == activity_type]
            type_metrics[activity_type] = {
                'average_score': float(type_data['score'].mean()),
                'median_score': float(type_data['score'].median()),
                'std_deviation': float(type_data['score'].std()),
                'count': len(type_data),
                'completion_rate': float(type_data['completed'].mean()) if 'completed' in type_data else None,
                'trend': self._calculate_trend(type_data)
            }
            
        return type_metrics

    def _calculate_performance_by_category(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate performance metrics by category."""
        category_metrics = {}
        
        for category in data['category'].unique():
            category_data = data[data['category'] == category]
            category_metrics[category] = {
                'average_score': float(category_data['score'].mean()),
                'median_score': float(category_data['score'].median()),
                'std_deviation': float(category_data['score'].std()),
                'count': len(category_data),
                'completion_rate': float(category_data['completed'].mean()) if 'completed' in category_data else None,
                'trend': self._calculate_trend(category_data)
            }
            
        return category_metrics

    def _identify_strengths(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Identify student's strengths."""
        strengths = []
        
        # Analyze by activity type
        for activity_type in data['activity_type'].unique():
            type_data = data[data['activity_type'] == activity_type]
            if len(type_data) >= self.analysis_config['min_data_points']:
                avg_score = float(type_data['score'].mean())
                if avg_score >= self.analysis_config['confidence_threshold']:
                    strengths.append({
                        'type': 'activity_type',
                        'name': activity_type,
                        'score': avg_score,
                        'confidence': self._calculate_confidence(type_data['score'])
                    })
        
        # Analyze by category
        for category in data['category'].unique():
            category_data = data[data['category'] == category]
            if len(category_data) >= self.analysis_config['min_data_points']:
                avg_score = float(category_data['score'].mean())
                if avg_score >= self.analysis_config['confidence_threshold']:
                    strengths.append({
                        'type': 'category',
                        'name': category,
                        'score': avg_score,
                        'confidence': self._calculate_confidence(category_data['score'])
                    })
        
        return strengths

    def _identify_improvements(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Identify areas for improvement."""
        improvements = []
        
        # Analyze by activity type
        for activity_type in data['activity_type'].unique():
            type_data = data[data['activity_type'] == activity_type]
            if len(type_data) >= self.analysis_config['min_data_points']:
                trend = self._calculate_trend(type_data)
                if trend < 0:  # Negative trend indicates need for improvement
                    improvements.append({
                        'type': 'activity_type',
                        'name': activity_type,
                        'current_score': float(type_data['score'].mean()),
                        'trend': trend,
                        'suggestions': self._generate_improvement_suggestions(type_data)
                    })
        
        # Analyze by category
        for category in data['category'].unique():
            category_data = data[data['category'] == category]
            if len(category_data) >= self.analysis_config['min_data_points']:
                trend = self._calculate_trend(category_data)
                if trend < 0:  # Negative trend indicates need for improvement
                    improvements.append({
                        'type': 'category',
                        'name': category,
                        'current_score': float(category_data['score'].mean()),
                        'trend': trend,
                        'suggestions': self._generate_improvement_suggestions(category_data)
                    })
        
        return improvements

    def _generate_recommendations(self, data: pd.DataFrame,
                                strengths: List[Dict[str, Any]],
                                improvements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate personalized recommendations."""
        recommendations = []
        
        # Build on strengths
        for strength in strengths:
            recommendations.append({
                'type': 'build_on_strength',
                'area': strength['name'],
                'current_score': strength['score'],
                'suggestion': f"Continue practicing {strength['name']} to maintain high performance",
                'priority': 'high'
            })
        
        # Address improvements
        for improvement in improvements:
            recommendations.append({
                'type': 'address_improvement',
                'area': improvement['name'],
                'current_score': improvement['current_score'],
                'suggestion': improvement['suggestions'],
                'priority': 'medium'
            })
        
        # Balance recommendations
        recommendations.extend(self._generate_balanced_recommendations(data))
        
        return recommendations

    def _calculate_consistency_score(self, data: pd.DataFrame) -> float:
        """Calculate consistency score based on score variance."""
        if len(data) < 2:
            return 0.0
            
        scores = data['score'].values
        mean_score = np.mean(scores)
        std_dev = np.std(scores)
        
        # Normalize consistency score between 0 and 1
        consistency = 1 - (std_dev / mean_score if mean_score != 0 else 1)
        return max(0, min(1, consistency))

    def _calculate_improvement_rate(self, data: pd.DataFrame) -> float:
        """Calculate rate of improvement over time."""
        if len(data) < 2:
            return 0.0
            
        # Sort data by date
        sorted_data = data.sort_values('date')
        
        # Calculate improvement rate using linear regression
        X = np.array(range(len(sorted_data))).reshape(-1, 1)
        y = sorted_data['score'].values
        
        model = LinearRegression()
        model.fit(X, y)
        
        return model.coef_[0]

    def _calculate_trend(self, data: pd.DataFrame) -> float:
        """Calculate performance trend."""
        if len(data) < 2:
            return 0.0
            
        # Sort data by date
        sorted_data = data.sort_values('date')
        
        # Calculate trend using linear regression
        X = np.array(range(len(sorted_data))).reshape(-1, 1)
        y = sorted_data['score'].values
        
        model = LinearRegression()
        model.fit(X, y)
        
        return model.coef_[0]

    def _calculate_confidence(self, scores: pd.Series) -> float:
        """Calculate confidence interval for scores."""
        if len(scores) < 2:
            return 0.0
            
        mean = np.mean(scores)
        std_err = stats.sem(scores)
        confidence = stats.t.interval(
            self.analysis_config['confidence_level'],
            len(scores) - 1,
            loc=mean,
            scale=std_err
        )
        
        return (confidence[1] - confidence[0]) / 2

    def _generate_improvement_suggestions(self, data: pd.DataFrame) -> List[str]:
        """Generate specific suggestions for improvement."""
        suggestions = []
        
        # Analyze common patterns in low scores
        low_scores = data[data['score'] < data['score'].median()]
        if not low_scores.empty:
            # Add specific suggestions based on analysis
            suggestions.append("Focus on fundamental techniques")
            suggestions.append("Practice more frequently")
            suggestions.append("Seek additional guidance")
        
        return suggestions

    def _generate_balanced_recommendations(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Generate balanced recommendations across all areas."""
        recommendations = []
        
        # Ensure balanced development across categories
        category_counts = data['category'].value_counts()
        min_count = category_counts.min()
        
        for category in category_counts.index:
            if category_counts[category] > min_count * 1.5:  # 50% more than minimum
                recommendations.append({
                    'type': 'balance_development',
                    'area': category,
                    'suggestion': f"Consider spending more time on other categories to maintain balanced development",
                    'priority': 'low'
                }) 