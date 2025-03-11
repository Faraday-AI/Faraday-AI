from typing import List, Dict, Any, Optional
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
import openai
from app.core.config import get_settings
import logging
from datetime import datetime, timedelta
from functools import lru_cache

logger = logging.getLogger(__name__)
settings = get_settings()

class AIAnalytics:
    def __init__(self):
        self.openai_client = openai.Client(api_key=settings.OPENAI_API_KEY)
        self.scaler = StandardScaler()
        self._initialize_models()

    def _initialize_models(self):
        """Initialize ML models for different analytics tasks."""
        # Performance prediction model
        self.performance_model = tf.keras.Sequential([
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(32, activation='relu'),
            tf.keras.layers.Dense(1, activation='sigmoid')
        ])
        
        # Behavior analysis model
        self.behavior_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )

    async def predict_student_performance(
        self,
        student_data: Dict[str, Any],
        lesson_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Predict student performance and provide recommendations."""
        try:
            # Extract features from student data
            features = self._extract_performance_features(student_data, lesson_history)
            
            # Get AI insights
            prompt = f"""
            Analyze student performance potential for upcoming lessons based on:
            1. Previous performance: {student_data.get('previous_performance', 'N/A')}
            2. Learning style: {student_data.get('learning_style', 'N/A')}
            3. Engagement level: {student_data.get('engagement_level', 'N/A')}
            4. Recent progress: {student_data.get('recent_progress', 'N/A')}
            
            Provide:
            1. Performance prediction
            2. Learning recommendations
            3. Areas for improvement
            4. Suggested interventions
            5. Growth opportunities
            """
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[{"role": "system", "content": prompt}],
                temperature=0.7
            )
            
            # Combine ML prediction with AI insights
            ml_prediction = self.performance_model.predict(features)
            
            return {
                "prediction_score": float(ml_prediction[0]),
                "ai_analysis": response.choices[0].message.content,
                "confidence_level": self._calculate_confidence(ml_prediction, features),
                "recommendations": self._generate_recommendations(ml_prediction, response)
            }
        except Exception as e:
            logger.error(f"Error predicting student performance: {str(e)}")
            return {"error": str(e)}

    async def analyze_behavior_patterns(
        self,
        student_data: Dict[str, Any],
        classroom_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze student behavior patterns and engagement."""
        try:
            # Extract behavior features
            features = self._extract_behavior_features(student_data, classroom_data)
            
            # Get AI behavior analysis
            prompt = f"""
            Analyze student behavior patterns considering:
            1. Engagement metrics: {student_data.get('engagement_metrics', {})}
            2. Interaction patterns: {student_data.get('interaction_patterns', {})}
            3. Learning preferences: {student_data.get('learning_preferences', {})}
            4. Social dynamics: {student_data.get('social_dynamics', {})}
            
            Provide:
            1. Behavior pattern analysis
            2. Engagement recommendations
            3. Social-emotional insights
            4. Environmental adjustments
            5. Support strategies
            """
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[{"role": "system", "content": prompt}],
                temperature=0.7
            )
            
            # Combine ML analysis with AI insights
            behavior_prediction = self.behavior_model.predict_proba(features)
            
            return {
                "behavior_patterns": self._categorize_behavior(behavior_prediction),
                "ai_insights": response.choices[0].message.content,
                "engagement_metrics": self._analyze_engagement(student_data),
                "recommendations": self._generate_behavior_recommendations(response)
            }
        except Exception as e:
            logger.error(f"Error analyzing behavior patterns: {str(e)}")
            return {"error": str(e)}

    async def generate_progress_report(
        self,
        student_data: Dict[str, Any],
        time_period: str = "weekly"
    ) -> Dict[str, Any]:
        """Generate comprehensive progress reports with AI insights."""
        try:
            # Analyze progress data
            progress_data = self._analyze_progress_data(student_data, time_period)
            
            # Get AI analysis of progress
            prompt = f"""
            Generate a comprehensive progress report for the {time_period} period:
            1. Performance trends: {progress_data.get('trends', {})}
            2. Achievement highlights: {progress_data.get('highlights', {})}
            3. Growth areas: {progress_data.get('growth_areas', {})}
            4. Support needs: {progress_data.get('support_needs', {})}
            
            Include:
            1. Progress summary
            2. Key achievements
            3. Areas for improvement
            4. Next steps
            5. Parent/Guardian recommendations
            """
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[{"role": "system", "content": prompt}],
                temperature=0.7
            )
            
            return {
                "progress_metrics": progress_data,
                "ai_analysis": response.choices[0].message.content,
                "recommendations": self._generate_progress_recommendations(response),
                "visualizations": self._generate_progress_visualizations(progress_data)
            }
        except Exception as e:
            logger.error(f"Error generating progress report: {str(e)}")
            return {"error": str(e)}

    def _extract_performance_features(
        self,
        student_data: Dict[str, Any],
        lesson_history: List[Dict[str, Any]]
    ) -> np.ndarray:
        """Extract and normalize features for performance prediction."""
        features = []
        for metric in ['attendance', 'participation', 'homework_completion', 'assessment_scores']:
            features.append(student_data.get(metric, 0))
        return self.scaler.fit_transform(np.array(features).reshape(1, -1))

    def _extract_behavior_features(
        self,
        student_data: Dict[str, Any],
        classroom_data: Dict[str, Any]
    ) -> np.ndarray:
        """Extract and normalize features for behavior analysis."""
        features = []
        for metric in ['engagement_level', 'social_interaction', 'focus_duration', 'participation_quality']:
            features.append(student_data.get(metric, 0))
        return np.array(features).reshape(1, -1)

    def _calculate_confidence(
        self,
        prediction: np.ndarray,
        features: np.ndarray
    ) -> float:
        """Calculate confidence level for predictions."""
        return float(np.mean([abs(p) for p in prediction]))

    def _generate_recommendations(
        self,
        prediction: np.ndarray,
        ai_response: Any
    ) -> List[Dict[str, Any]]:
        """Generate actionable recommendations based on predictions and AI insights."""
        recommendations = []
        insights = ai_response.choices[0].message.content.split('\n')
        
        for insight in insights:
            if insight.strip():
                recommendations.append({
                    "type": "recommendation",
                    "content": insight,
                    "priority": self._calculate_priority(insight, prediction)
                })
        
        return recommendations

    def _analyze_progress_data(
        self,
        student_data: Dict[str, Any],
        time_period: str
    ) -> Dict[str, Any]:
        """Analyze student progress data for the specified time period."""
        # Calculate date range
        end_date = datetime.now()
        if time_period == "weekly":
            start_date = end_date - timedelta(days=7)
        elif time_period == "monthly":
            start_date = end_date - timedelta(days=30)
        else:
            start_date = end_date - timedelta(days=90)
            
        # Filter and analyze data
        filtered_data = self._filter_data_by_date_range(student_data, start_date, end_date)
        
        return {
            "trends": self._calculate_trends(filtered_data),
            "highlights": self._identify_highlights(filtered_data),
            "growth_areas": self._identify_growth_areas(filtered_data),
            "support_needs": self._identify_support_needs(filtered_data)
        }

    def _generate_progress_visualizations(
        self,
        progress_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate visualization data for progress reports."""
        return {
            "performance_trend": self._create_trend_data(progress_data['trends']),
            "growth_areas": self._create_radar_chart_data(progress_data['growth_areas']),
            "achievement_summary": self._create_summary_chart_data(progress_data['highlights'])
        }

    def _calculate_priority(self, insight: str, prediction: np.ndarray) -> str:
        """Calculate priority level for recommendations."""
        if "immediate" in insight.lower() or "critical" in insight.lower():
            return "high"
        elif "consider" in insight.lower() or "might" in insight.lower():
            return "medium"
        return "low"

    def _categorize_behavior(self, behavior_prediction: np.ndarray) -> Dict[str, Any]:
        """Categorize behavior patterns based on predictions."""
        categories = ['engagement', 'social_interaction', 'focus', 'participation']
        return {
            cat: float(pred) for cat, pred in zip(categories, behavior_prediction[0])
        }

    def _analyze_engagement(self, student_data: Dict[str, Any]) -> Dict[str, float]:
        """Analyze student engagement metrics."""
        metrics = ['participation', 'attention', 'interaction', 'initiative']
        return {
            metric: float(student_data.get(f'{metric}_score', 0))
            for metric in metrics
        }

    def _generate_behavior_recommendations(self, ai_response: Any) -> List[Dict[str, Any]]:
        """Generate behavior-specific recommendations."""
        insights = ai_response.choices[0].message.content.split('\n')
        return [
            {
                "area": "behavior",
                "recommendation": insight.strip(),
                "implementation": self._generate_implementation_steps(insight)
            }
            for insight in insights if insight.strip()
        ]

    def _generate_implementation_steps(self, insight: str) -> List[str]:
        """Generate specific implementation steps for recommendations."""
        return [
            f"Step 1: {insight.split(':')[0] if ':' in insight else 'Implement'} strategy",
            "Step 2: Monitor progress",
            "Step 3: Adjust as needed",
            "Step 4: Review and refine"
        ]

@lru_cache()
def get_ai_analytics_service() -> AIAnalytics:
    """Get cached AI analytics service instance."""
    return AIAnalytics() 