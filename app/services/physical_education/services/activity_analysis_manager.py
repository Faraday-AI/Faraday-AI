from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import logging

class ActivityAnalysisManager:
    def __init__(self):
        self.analysis_config = {
            'min_data_points': 5,
            'confidence_level': 0.95,
            'trend_window': 7,  # days
            'improvement_threshold': 0.1,  # 10% improvement
            'consistency_threshold': 0.8,  # 80% consistency
            'max_gap_days': 30  # maximum gap between data points
        }
        
        # Initialize logging
        self.logger = logging.getLogger(__name__)

    async def analyze_student_performance(self, student_id: str, 
                                        start_date: Optional[datetime] = None,
                                        end_date: Optional[datetime] = None) -> Dict:
        """Analyze student's performance across activities."""
        # Get performance data
        performance_data = await self._get_performance_data(student_id, start_date, end_date)
        
        if len(performance_data) < self.analysis_config['min_data_points']:
            raise ValueError(f"Insufficient data points for analysis. Minimum required: {self.analysis_config['min_data_points']}")
        
        # Calculate overall metrics
        overall_metrics = self._calculate_overall_metrics(performance_data)
        
        # Calculate performance by type and category
        type_metrics = self._calculate_performance_by_type(performance_data)
        category_metrics = self._calculate_performance_by_category(performance_data)
        
        # Identify strengths and areas for improvement
        strengths = self._identify_strengths(performance_data)
        improvements = self._identify_improvements(performance_data)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            performance_data,
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
                                  end_date: Optional[datetime]) -> pd.DataFrame:
        """Retrieve and prepare performance data."""
        # This is a placeholder for actual data retrieval
        # In practice, this would query the database
        return pd.DataFrame()

    def _calculate_overall_metrics(self, data: pd.DataFrame) -> Dict:
        """Calculate overall performance metrics."""
        metrics = {
            'average_score': data['score'].mean(),
            'median_score': data['score'].median(),
            'std_deviation': data['score'].std(),
            'min_score': data['score'].min(),
            'max_score': data['score'].max(),
            'total_activities': len(data),
            'completion_rate': data['completed'].mean() if 'completed' in data else None,
            'consistency_score': self._calculate_consistency_score(data),
            'improvement_rate': self._calculate_improvement_rate(data)
        }
        
        return metrics

    def _calculate_performance_by_type(self, data: pd.DataFrame) -> Dict:
        """Calculate performance metrics by activity type."""
        type_metrics = {}
        
        for activity_type in data['activity_type'].unique():
            type_data = data[data['activity_type'] == activity_type]
            type_metrics[activity_type] = {
                'average_score': type_data['score'].mean(),
                'median_score': type_data['score'].median(),
                'std_deviation': type_data['score'].std(),
                'count': len(type_data),
                'completion_rate': type_data['completed'].mean() if 'completed' in type_data else None,
                'trend': self._calculate_trend(type_data)
            }
            
        return type_metrics

    def _calculate_performance_by_category(self, data: pd.DataFrame) -> Dict:
        """Calculate performance metrics by category."""
        category_metrics = {}
        
        for category in data['category'].unique():
            category_data = data[data['category'] == category]
            category_metrics[category] = {
                'average_score': category_data['score'].mean(),
                'median_score': category_data['score'].median(),
                'std_deviation': category_data['score'].std(),
                'count': len(category_data),
                'completion_rate': category_data['completed'].mean() if 'completed' in category_data else None,
                'trend': self._calculate_trend(category_data)
            }
            
        return category_metrics

    def _identify_strengths(self, data: pd.DataFrame) -> List[Dict]:
        """Identify student's strengths."""
        strengths = []
        
        # Analyze by activity type
        for activity_type in data['activity_type'].unique():
            type_data = data[data['activity_type'] == activity_type]
            if len(type_data) >= self.analysis_config['min_data_points']:
                avg_score = type_data['score'].mean()
                if avg_score >= self.analysis_config['consistency_threshold']:
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
                avg_score = category_data['score'].mean()
                if avg_score >= self.analysis_config['consistency_threshold']:
                    strengths.append({
                        'type': 'category',
                        'name': category,
                        'score': avg_score,
                        'confidence': self._calculate_confidence(category_data['score'])
                    })
        
        return strengths

    def _identify_improvements(self, data: pd.DataFrame) -> List[Dict]:
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
                        'current_score': type_data['score'].mean(),
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
                        'current_score': category_data['score'].mean(),
                        'trend': trend,
                        'suggestions': self._generate_improvement_suggestions(category_data)
                    })
        
        return improvements

    def _generate_recommendations(self, data: pd.DataFrame,
                                strengths: List[Dict],
                                improvements: List[Dict]) -> List[Dict]:
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

    def _generate_balanced_recommendations(self, data: pd.DataFrame) -> List[Dict]:
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
        
        return recommendations 