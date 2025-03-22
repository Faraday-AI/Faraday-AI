from typing import Dict, List, Optional
import numpy as np
from sklearn.neighbors import NearestNeighbors
from pydantic import BaseModel

class ContentFeatures(BaseModel):
    complexity_score: float
    length: int
    technical_terms: int
    prerequisites_count: int
    interaction_required: float

class DifficultyPredictor:
    def __init__(self):
        self.model = NearestNeighbors(n_neighbors=5, algorithm='ball_tree')
        self.difficulty_levels = []
        self.feature_vectors = []
        self.is_trained = False
        
    def _extract_features(self, content: str) -> ContentFeatures:
        """Extract numerical features from content"""
        # Simple feature extraction
        complexity_score = len(set(content.split())) / len(content.split()) if content else 0
        length = len(content)
        technical_terms = sum(1 for word in content.split() if len(word) > 8)  # Simple heuristic
        prerequisites_count = content.lower().count('require') + content.lower().count('prerequisite')
        interaction_required = float(
            ('practice' in content.lower() or 
             'exercise' in content.lower() or 
             'try' in content.lower())
        )
        
        return ContentFeatures(
            complexity_score=complexity_score,
            length=length,
            technical_terms=technical_terms,
            prerequisites_count=prerequisites_count,
            interaction_required=interaction_required
        )
    
    def _normalize_features(self, features: List[ContentFeatures]) -> np.ndarray:
        """Normalize feature vectors"""
        feature_matrix = np.array([
            [f.complexity_score, f.length, f.technical_terms, 
             f.prerequisites_count, f.interaction_required]
            for f in features
        ])
        
        # Min-max normalization
        if feature_matrix.shape[0] > 0:
            feature_mins = feature_matrix.min(axis=0)
            feature_maxs = feature_matrix.max(axis=0)
            normalized = np.zeros_like(feature_matrix)
            for i in range(feature_matrix.shape[1]):
                if feature_maxs[i] > feature_mins[i]:
                    normalized[:, i] = (feature_matrix[:, i] - feature_mins[i]) / (feature_maxs[i] - feature_mins[i])
            return normalized
        return feature_matrix
    
    def train(self, content_samples: List[str], difficulty_levels: List[float]) -> None:
        """Train the difficulty predictor with sample content"""
        if len(content_samples) != len(difficulty_levels):
            raise ValueError("Number of samples must match number of difficulty levels")
            
        features = [self._extract_features(content) for content in content_samples]
        normalized_features = self._normalize_features(features)
        
        if normalized_features.shape[0] > 0:
            self.model.fit(normalized_features)
            self.difficulty_levels = difficulty_levels
            self.feature_vectors = normalized_features
            self.is_trained = True
    
    def predict_difficulty(self, content: str) -> float:
        """Predict difficulty level for new content"""
        if not self.is_trained:
            raise RuntimeError("Model must be trained before making predictions")
            
        features = self._extract_features(content)
        normalized = self._normalize_features([features])
        
        if normalized.shape[0] > 0:
            distances, indices = self.model.kneighbors(normalized)
            # Weight predictions by inverse distance
            weights = 1 / (distances + 1e-6)  # Add small epsilon to avoid division by zero
            weighted_difficulties = np.array([self.difficulty_levels[i] for i in indices[0]]) * weights[0]
            return float(weighted_difficulties.sum() / weights.sum())
        return 0.5  # Default middle difficulty if normalization fails
    
    def get_similar_content(self, content: str, n: int = 5) -> List[int]:
        """Get indices of similar content based on features"""
        if not self.is_trained:
            raise RuntimeError("Model must be trained before finding similar content")
            
        features = self._extract_features(content)
        normalized = self._normalize_features([features])
        
        if normalized.shape[0] > 0:
            distances, indices = self.model.kneighbors(normalized, n_neighbors=min(n, len(self.difficulty_levels)))
            return indices[0].tolist()
        return [] 
