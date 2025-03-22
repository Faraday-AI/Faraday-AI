from typing import Dict, List, Any, Optional
import logging
import numpy as np
from datetime import datetime
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

logger = logging.getLogger(__name__)

class AdaptiveLearningService:
    def __init__(self):
        self.learning_styles = [
            "visual", "auditory", "reading", "kinesthetic",
            "social", "solitary", "logical", "verbal"
        ]
        self.difficulty_levels = ["beginner", "intermediate", "advanced", "expert"]
        self.content_types = ["text", "video", "interactive", "quiz", "project"]
        self.user_profiles: Dict[str, Dict[str, Any]] = {}
        self.content_effectiveness: Dict[str, Dict[str, float]] = {}
        self.learning_clusters = None
        self.scaler = StandardScaler()

    async def create_user_profile(
        self,
        user_id: str,
        initial_assessment: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create or update user learning profile."""
        try:
            profile = {
                "learning_style_weights": self._calculate_style_weights(initial_assessment),
                "difficulty_level": self._determine_initial_level(initial_assessment),
                "content_preferences": self._analyze_content_preferences(initial_assessment),
                "knowledge_gaps": self._identify_knowledge_gaps(initial_assessment),
                "learning_pace": self._estimate_learning_pace(initial_assessment),
                "created_at": datetime.utcnow(),
                "last_updated": datetime.utcnow()
            }
            
            self.user_profiles[user_id] = profile
            
            # Update learning clusters
            self._update_learning_clusters()
            
            return {
                "status": "success",
                "profile": profile
            }
        except Exception as e:
            logger.error(f"Error creating user profile: {str(e)}")
            return {"status": "error", "error": str(e)}

    def _calculate_style_weights(
        self,
        assessment: Dict[str, Any]
    ) -> Dict[str, float]:
        """Calculate weights for different learning styles."""
        weights = {}
        responses = assessment.get("style_responses", {})
        
        for style in self.learning_styles:
            # Calculate base weight from direct responses
            base_weight = responses.get(style, 0.5)
            
            # Adjust weight based on historical performance
            if "performance_history" in assessment:
                style_performance = [
                    entry["score"] for entry in assessment["performance_history"]
                    if entry["learning_style"] == style
                ]
                if style_performance:
                    performance_weight = np.mean(style_performance)
                    base_weight = 0.7 * base_weight + 0.3 * performance_weight
            
            weights[style] = max(0.0, min(1.0, base_weight))
            
        return weights

    def _determine_initial_level(
        self,
        assessment: Dict[str, Any]
    ) -> str:
        """Determine initial difficulty level."""
        scores = assessment.get("topic_scores", {})
        if not scores:
            return "beginner"
            
        avg_score = np.mean(list(scores.values()))
        
        if avg_score >= 0.8:
            return "expert"
        elif avg_score >= 0.6:
            return "advanced"
        elif avg_score >= 0.4:
            return "intermediate"
        else:
            return "beginner"

    def _analyze_content_preferences(
        self,
        assessment: Dict[str, Any]
    ) -> Dict[str, float]:
        """Analyze preferred content types."""
        preferences = {}
        
        # Start with explicit preferences
        explicit_prefs = assessment.get("content_preferences", {})
        for content_type in self.content_types:
            preferences[content_type] = explicit_prefs.get(content_type, 0.5)
        
        # Adjust based on engagement history
        if "engagement_history" in assessment:
            for entry in assessment["engagement_history"]:
                content_type = entry["content_type"]
                if content_type in preferences:
                    # Weighted average of completion rate and satisfaction
                    effectiveness = (
                        0.6 * entry.get("completion_rate", 0) +
                        0.4 * entry.get("satisfaction", 0)
                    )
                    preferences[content_type] = (
                        0.7 * preferences[content_type] +
                        0.3 * effectiveness
                    )
        
        return preferences

    def _identify_knowledge_gaps(
        self,
        assessment: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Identify knowledge gaps from assessment."""
        gaps = []
        scores = assessment.get("topic_scores", {})
        prerequisites = assessment.get("topic_prerequisites", {})
        
        for topic, score in scores.items():
            if score < 0.7:  # Below mastery threshold
                gap = {
                    "topic": topic,
                    "current_level": score,
                    "priority": "high" if score < 0.5 else "medium",
                    "prerequisites": prerequisites.get(topic, [])
                }
                gaps.append(gap)
                
        return sorted(gaps, key=lambda x: x["current_level"])

    def _estimate_learning_pace(
        self,
        assessment: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Estimate user's learning pace."""
        history = assessment.get("learning_history", [])
        if not history:
            return {"pace": "medium", "consistency": 0.5}
            
        # Calculate time to mastery for different topics
        mastery_times = []
        for entry in history:
            if entry.get("mastered", False):
                time_to_mastery = entry.get("time_to_mastery", 0)
                mastery_times.append(time_to_mastery)
        
        if not mastery_times:
            return {"pace": "medium", "consistency": 0.5}
            
        avg_time = np.mean(mastery_times)
        consistency = 1 - (np.std(mastery_times) / avg_time if avg_time > 0 else 0)
        
        # Determine pace category
        if avg_time <= 0.7 * np.median(mastery_times):
            pace = "fast"
        elif avg_time >= 1.3 * np.median(mastery_times):
            pace = "slow"
        else:
            pace = "medium"
            
        return {
            "pace": pace,
            "consistency": consistency,
            "avg_time_to_mastery": avg_time
        }

    async def generate_personalized_content(
        self,
        user_id: str,
        topic: str,
        content_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate personalized learning content."""
        try:
            if user_id not in self.user_profiles:
                return {
                    "status": "error",
                    "error": "User profile not found"
                }
            
            profile = self.user_profiles[user_id]
            
            # Select optimal content type if not specified
            if not content_type:
                content_type = self._select_optimal_content_type(profile, topic)
            
            # Adjust difficulty level
            difficulty = self._adjust_difficulty(profile, topic)
            
            # Generate content parameters
            content_params = {
                "topic": topic,
                "difficulty": difficulty,
                "learning_style": self._get_dominant_style(profile),
                "content_type": content_type,
                "pace": profile["learning_pace"]["pace"],
                "adaptations": self._generate_adaptations(profile, topic)
            }
            
            # Record content generation for effectiveness tracking
            self._record_content_generation(user_id, content_params)
            
            return {
                "status": "success",
                "content_params": content_params
            }
        except Exception as e:
            logger.error(f"Error generating personalized content: {str(e)}")
            return {"status": "error", "error": str(e)}

    def _select_optimal_content_type(
        self,
        profile: Dict[str, Any],
        topic: str
    ) -> str:
        """Select the most effective content type."""
        preferences = profile["content_preferences"]
        effectiveness = self.content_effectiveness.get(topic, {})
        
        scores = {}
        for content_type in self.content_types:
            base_score = preferences.get(content_type, 0.5)
            effect_score = effectiveness.get(content_type, 0.5)
            scores[content_type] = 0.6 * base_score + 0.4 * effect_score
            
        return max(scores.items(), key=lambda x: x[1])[0]

    def _adjust_difficulty(
        self,
        profile: Dict[str, Any],
        topic: str
    ) -> str:
        """Adjust difficulty level based on progress."""
        current_level = profile["difficulty_level"]
        level_idx = self.difficulty_levels.index(current_level)
        
        # Check for topic-specific adjustments
        if "knowledge_gaps" in profile:
            topic_gaps = [
                gap for gap in profile["knowledge_gaps"]
                if gap["topic"] == topic
            ]
            if topic_gaps:
                gap = topic_gaps[0]
                if gap["priority"] == "high":
                    level_idx = max(0, level_idx - 1)
                
        return self.difficulty_levels[level_idx]

    def _get_dominant_style(
        self,
        profile: Dict[str, Any]
    ) -> str:
        """Get the user's dominant learning style."""
        weights = profile["learning_style_weights"]
        return max(weights.items(), key=lambda x: x[1])[0]

    def _generate_adaptations(
        self,
        profile: Dict[str, Any],
        topic: str
    ) -> List[Dict[str, Any]]:
        """Generate content adaptations based on user profile."""
        adaptations = []
        
        # Pace adaptations
        if profile["learning_pace"]["pace"] == "slow":
            adaptations.append({
                "type": "pace",
                "action": "include_additional_examples",
                "reason": "Provide more practice opportunities"
            })
        
        # Style adaptations
        dominant_style = self._get_dominant_style(profile)
        adaptations.append({
            "type": "style",
            "action": f"optimize_for_{dominant_style}",
            "reason": f"Match {dominant_style} learning style"
        })
        
        # Knowledge gap adaptations
        for gap in profile.get("knowledge_gaps", []):
            if gap["topic"] == topic:
                adaptations.append({
                    "type": "remedial",
                    "action": "include_prerequisite_review",
                    "prerequisites": gap["prerequisites"],
                    "reason": "Address knowledge gap"
                })
                
        return adaptations

    def _record_content_generation(
        self,
        user_id: str,
        content_params: Dict[str, Any]
    ) -> None:
        """Record content generation for effectiveness tracking."""
        topic = content_params["topic"]
        content_type = content_params["content_type"]
        
        if topic not in self.content_effectiveness:
            self.content_effectiveness[topic] = {}
            
        if content_type not in self.content_effectiveness[topic]:
            self.content_effectiveness[topic][content_type] = 0.5

    async def update_learning_effectiveness(
        self,
        user_id: str,
        topic: str,
        content_type: str,
        effectiveness_metrics: Dict[str, float]
    ) -> Dict[str, Any]:
        """Update content effectiveness based on learning outcomes."""
        try:
            if topic not in self.content_effectiveness:
                self.content_effectiveness[topic] = {}
                
            current_effectiveness = self.content_effectiveness[topic].get(content_type, 0.5)
            
            # Calculate new effectiveness score
            completion_rate = effectiveness_metrics.get("completion_rate", 0)
            engagement = effectiveness_metrics.get("engagement", 0)
            assessment_score = effectiveness_metrics.get("assessment_score", 0)
            
            new_effectiveness = (
                0.4 * assessment_score +
                0.3 * completion_rate +
                0.3 * engagement
            )
            
            # Update with moving average
            updated_effectiveness = (
                0.7 * current_effectiveness +
                0.3 * new_effectiveness
            )
            
            self.content_effectiveness[topic][content_type] = updated_effectiveness
            
            # Update user profile if needed
            if user_id in self.user_profiles:
                profile = self.user_profiles[user_id]
                profile["last_updated"] = datetime.utcnow()
                
                # Update content preferences
                if "content_preferences" in profile:
                    current_pref = profile["content_preferences"].get(content_type, 0.5)
                    profile["content_preferences"][content_type] = (
                        0.8 * current_pref +
                        0.2 * new_effectiveness
                    )
            
            return {
                "status": "success",
                "updated_effectiveness": updated_effectiveness
            }
        except Exception as e:
            logger.error(f"Error updating learning effectiveness: {str(e)}")
            return {"status": "error", "error": str(e)}

    def _update_learning_clusters(self) -> None:
        """Update learning style clusters for personalization."""
        if len(self.user_profiles) < 3:  # Need minimum samples for clustering
            return
            
        try:
            # Prepare data for clustering
            features = []
            user_ids = []
            
            for user_id, profile in self.user_profiles.items():
                style_weights = [
                    profile["learning_style_weights"].get(style, 0)
                    for style in self.learning_styles
                ]
                features.append(style_weights)
                user_ids.append(user_id)
                
            # Normalize features
            X = self.scaler.fit_transform(features)
            
            # Perform clustering
            n_clusters = min(3, len(self.user_profiles))
            self.learning_clusters = KMeans(
                n_clusters=n_clusters,
                random_state=42
            ).fit(X)
            
            # Update profiles with cluster assignments
            for user_id, cluster_id in zip(user_ids, self.learning_clusters.labels_):
                self.user_profiles[user_id]["learning_cluster"] = int(cluster_id)
                
        except Exception as e:
            logger.error(f"Error updating learning clusters: {str(e)}")
            self.learning_clusters = None 
