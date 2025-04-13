from sqlalchemy import Column, Integer, String, Float, JSON, ForeignKey, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime
import joblib
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

class ActivityAdaptation(Base):
    """Model for storing activity adaptations."""
    __tablename__ = "activity_adaptations"

    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    adaptation_type = Column(String, nullable=False)
    adaptation_details = Column(JSON, nullable=False)
    reason = Column(Text, nullable=True)
    effectiveness_score = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    activity = relationship("Activity", back_populates="adaptations")
    student = relationship("Student", back_populates="activity_adaptations")

class AdaptationHistory(Base):
    """Model for tracking adaptation history."""
    __tablename__ = "adaptation_history"

    id = Column(Integer, primary_key=True, index=True)
    adaptation_id = Column(Integer, ForeignKey("activity_adaptations.id"), nullable=False)
    previous_state = Column(JSON, nullable=False)
    new_state = Column(JSON, nullable=False)
    change_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    adaptation = relationship("ActivityAdaptation", back_populates="history")

# Add relationship to ActivityAdaptation
ActivityAdaptation.history = relationship("AdaptationHistory", back_populates="adaptation")

class ActivityAdaptationModel:
    """Model for predicting activity adaptations."""
    def __init__(self):
        self.model = None
        self.metadata = None
        self.model_path = Path('models/activity_adaptation.joblib')
        self.metadata_path = Path('models/activity_adaptation_metadata.json')
        self._load_model()

    def _load_model(self):
        """Load the trained model and metadata."""
        try:
            if self.model_path.exists():
                self.model = joblib.load(str(self.model_path))
            else:
                raise FileNotFoundError(f"Model file not found at {self.model_path}")

            if self.metadata_path.exists():
                with open(self.metadata_path, 'r') as f:
                    self.metadata = json.load(f)
            else:
                raise FileNotFoundError(f"Metadata file not found at {self.metadata_path}")

        except Exception as e:
            # Log error but don't raise - allow for graceful fallback
            print(f"Error loading model: {str(e)}")
            self.model = None
            self.metadata = None

    def predict_adaptation(
        self,
        student_id: int,
        activity_id: int,
        current_performance: float,
        history: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Predict adaptations based on student and activity data."""
        try:
            if not self.model or not self.metadata:
                return {
                    'success': False,
                    'error': 'Model not loaded',
                    'fallback_suggestion': self._get_fallback_suggestion(current_performance)
                }

            # TODO: Implement feature preparation and prediction logic
            # For now, return a basic suggestion based on performance
            return self._get_fallback_suggestion(current_performance)

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'fallback_suggestion': self._get_fallback_suggestion(current_performance)
            }

    def _get_fallback_suggestion(self, performance: float) -> Dict[str, Any]:
        """Get fallback suggestions when model prediction fails."""
        if performance < 0.4:
            return {
                'success': True,
                'adaptation_type': 'difficulty',
                'suggestion': 'decrease',
                'confidence': 0.8,
                'reason': 'Low performance indicates need for simplified activity'
            }
        elif performance > 0.8:
            return {
                'success': True,
                'adaptation_type': 'difficulty',
                'suggestion': 'increase',
                'confidence': 0.8,
                'reason': 'High performance indicates readiness for more challenge'
            }
        else:
            return {
                'success': True,
                'adaptation_type': 'maintain',
                'suggestion': 'current',
                'confidence': 0.6,
                'reason': 'Current performance is within acceptable range'
            } 