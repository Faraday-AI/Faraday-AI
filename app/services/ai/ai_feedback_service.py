from typing import Dict, List, Any, Optional
import logging
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class AIFeedbackService:
    def __init__(self):
        self.vectorizer = TfidfVectorizer()
        self.feedback_history: Dict[str, List[Dict[str, Any]]] = {}
        self.learning_patterns: Dict[str, Dict[str, Any]] = {}
        self.engagement_metrics: Dict[str, Dict[str, float]] = {}

    async def analyze_response(
        self,
        user_id: str,
        response_text: str,
        expected_concepts: List[str],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Analyze student response for understanding and misconceptions."""
        try:
            # Vectorize response and expected concepts
            combined_text = [response_text] + expected_concepts
            tfidf_matrix = self.vectorizer.fit_transform(combined_text)
            
            # Calculate similarity scores
            similarity_scores = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])
            
            # Identify key concepts present and missing
            concept_coverage = {
                concept: float(score)
                for concept, score in zip(expected_concepts, similarity_scores[0])
            }
            
            # Analyze writing style and clarity
            clarity_metrics = self._analyze_clarity(response_text)
            
            # Update learning patterns
            self._update_learning_patterns(user_id, concept_coverage, clarity_metrics)
            
            analysis = {
                "concept_coverage": concept_coverage,
                "clarity_metrics": clarity_metrics,
                "understanding_level": np.mean(list(concept_coverage.values())),
                "improvement_areas": [
                    concept for concept, score in concept_coverage.items()
                    if score < 0.7
                ],
                "strengths": [
                    concept for concept, score in concept_coverage.items()
                    if score >= 0.7
                ],
                "learning_patterns": self.learning_patterns.get(user_id, {})
            }
            
            # Store feedback in history
            self._store_feedback(user_id, analysis, metadata)
            
            return {
                "status": "success",
                "analysis": analysis
            }
        except Exception as e:
            logger.error(f"Error analyzing response: {str(e)}")
            return {"status": "error", "error": str(e)}

    def _analyze_clarity(self, text: str) -> Dict[str, float]:
        """Analyze writing clarity and structure."""
        words = text.split()
        sentences = text.split('.')
        
        return {
            "avg_word_length": np.mean([len(word) for word in words]),
            "avg_sentence_length": np.mean([len(sent.split()) for sent in sentences if sent.strip()]),
            "vocabulary_diversity": len(set(words)) / len(words) if words else 0,
            "structure_score": self._calculate_structure_score(text)
        }

    def _calculate_structure_score(self, text: str) -> float:
        """Calculate text structure and organization score."""
        paragraphs = text.split('\n\n')
        if not paragraphs:
            return 0.0
            
        scores = []
        for para in paragraphs:
            sentences = para.split('.')
            if not sentences:
                continue
                
            # Check for topic sentence
            has_topic = len(sentences[0].split()) >= 5 if sentences[0].strip() else False
            # Check for supporting details
            has_support = len(sentences) > 1
            # Check for conclusion
            has_conclusion = len(sentences[-1].split()) >= 5 if sentences[-1].strip() else False
            
            scores.append(sum([has_topic, has_support, has_conclusion]) / 3)
            
        return np.mean(scores) if scores else 0.0

    def _update_learning_patterns(
        self,
        user_id: str,
        concept_coverage: Dict[str, float],
        clarity_metrics: Dict[str, float]
    ) -> None:
        """Update user learning patterns based on new data."""
        if user_id not in self.learning_patterns:
            self.learning_patterns[user_id] = {
                "concept_mastery": {},
                "writing_style": {},
                "learning_velocity": {},
                "engagement_trends": {}
            }
            
        patterns = self.learning_patterns[user_id]
        
        # Update concept mastery
        for concept, score in concept_coverage.items():
            if concept not in patterns["concept_mastery"]:
                patterns["concept_mastery"][concept] = []
            patterns["concept_mastery"][concept].append(score)
            
        # Update writing style metrics
        for metric, value in clarity_metrics.items():
            if metric not in patterns["writing_style"]:
                patterns["writing_style"][metric] = []
            patterns["writing_style"][metric].append(value)
            
        # Calculate learning velocity
        for concept, scores in patterns["concept_mastery"].items():
            if len(scores) >= 2:
                velocity = (scores[-1] - scores[-2]) / 1.0  # Assuming 1 time unit between assessments
                if concept not in patterns["learning_velocity"]:
                    patterns["learning_velocity"][concept] = []
                patterns["learning_velocity"][concept].append(velocity)

    def _store_feedback(
        self,
        user_id: str,
        analysis: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Store feedback history for future reference."""
        if user_id not in self.feedback_history:
            self.feedback_history[user_id] = []
            
        feedback_entry = {
            "timestamp": datetime.utcnow(),
            "analysis": analysis,
            "metadata": metadata or {}
        }
        self.feedback_history[user_id].append(feedback_entry)

    async def get_learning_insights(
        self,
        user_id: str,
        time_period: Optional[timedelta] = None
    ) -> Dict[str, Any]:
        """Get comprehensive learning insights for a user."""
        try:
            if user_id not in self.learning_patterns:
                return {
                    "status": "error",
                    "error": "No learning patterns found for user"
                }
                
            patterns = self.learning_patterns[user_id]
            history = self.feedback_history.get(user_id, [])
            
            if time_period:
                cutoff = datetime.utcnow() - time_period
                history = [
                    entry for entry in history
                    if entry["timestamp"] >= cutoff
                ]
            
            # Calculate mastery trends
            mastery_trends = {}
            for concept, scores in patterns["concept_mastery"].items():
                if scores:
                    mastery_trends[concept] = {
                        "current": scores[-1],
                        "trend": np.mean(scores[-3:]) - np.mean(scores[:-3]) if len(scores) > 3 else 0,
                        "volatility": np.std(scores)
                    }
            
            # Calculate learning style insights
            style_insights = {}
            for metric, values in patterns["writing_style"].items():
                if values:
                    style_insights[metric] = {
                        "average": np.mean(values),
                        "trend": np.mean(values[-3:]) - np.mean(values[:-3]) if len(values) > 3 else 0,
                        "consistency": 1 - np.std(values) / np.mean(values) if np.mean(values) != 0 else 0
                    }
            
            # Generate recommendations
            recommendations = self._generate_recommendations(mastery_trends, style_insights)
            
            return {
                "status": "success",
                "insights": {
                    "mastery_trends": mastery_trends,
                    "style_insights": style_insights,
                    "learning_velocity": patterns["learning_velocity"],
                    "engagement_trends": patterns["engagement_trends"],
                    "recommendations": recommendations,
                    "analysis_period": {
                        "start": history[0]["timestamp"] if history else None,
                        "end": history[-1]["timestamp"] if history else None,
                        "total_entries": len(history)
                    }
                }
            }
        except Exception as e:
            logger.error(f"Error getting learning insights: {str(e)}")
            return {"status": "error", "error": str(e)}

    def _generate_recommendations(
        self,
        mastery_trends: Dict[str, Dict[str, float]],
        style_insights: Dict[str, Dict[str, float]]
    ) -> List[Dict[str, Any]]:
        """Generate personalized learning recommendations."""
        recommendations = []
        
        # Identify concepts needing attention
        for concept, data in mastery_trends.items():
            if data["current"] < 0.7:
                recommendations.append({
                    "type": "concept_focus",
                    "concept": concept,
                    "priority": "high" if data["current"] < 0.5 else "medium",
                    "reason": "Below target mastery level",
                    "suggestion": "Focus on fundamental principles and practice exercises"
                })
            elif data["volatility"] > 0.2:
                recommendations.append({
                    "type": "consistency",
                    "concept": concept,
                    "priority": "medium",
                    "reason": "High performance volatility",
                    "suggestion": "Regular review and practice to stabilize understanding"
                })
        
        # Writing style recommendations
        if style_insights.get("clarity_score", {}).get("average", 1) < 0.7:
            recommendations.append({
                "type": "writing_clarity",
                "priority": "high",
                "reason": "Below target clarity level",
                "suggestion": "Focus on clear topic sentences and supporting details"
            })
        
        return recommendations

    async def update_engagement_metrics(
        self,
        user_id: str,
        metrics: Dict[str, float]
    ) -> Dict[str, Any]:
        """Update user engagement metrics."""
        try:
            if user_id not in self.engagement_metrics:
                self.engagement_metrics[user_id] = {}
            
            current_time = datetime.utcnow()
            
            # Update metrics with timestamps
            for metric, value in metrics.items():
                if metric not in self.engagement_metrics[user_id]:
                    self.engagement_metrics[user_id][metric] = []
                    
                self.engagement_metrics[user_id][metric].append({
                    "value": value,
                    "timestamp": current_time
                })
            
            # Update learning patterns with engagement trends
            if user_id in self.learning_patterns:
                self.learning_patterns[user_id]["engagement_trends"] = {
                    metric: {
                        "current": entries[-1]["value"],
                        "trend": np.mean([e["value"] for e in entries[-3:]]) - 
                               np.mean([e["value"] for e in entries[:-3]])
                        if len(entries) > 3 else 0
                    }
                    for metric, entries in self.engagement_metrics[user_id].items()
                }
            
            return {
                "status": "success",
                "metrics": self.engagement_metrics[user_id]
            }
        except Exception as e:
            logger.error(f"Error updating engagement metrics: {str(e)}")
            return {"status": "error", "error": str(e)} 
