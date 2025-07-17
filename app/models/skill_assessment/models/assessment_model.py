"""Assessment model class for calculating assessment scores."""
import logging
import joblib
from pathlib import Path
from typing import Dict, Any, Optional

class SkillAssessmentModel:
    """Model for predicting and calculating assessment scores."""
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.model = None
        self.metadata = None
        self.model_path = Path('app/models/physical_education/assessment/skill_assessment.joblib')
        self.metadata_path = Path('app/models/physical_education/assessment/skill_assessment_metadata.json')
        self._load_model()

    def _load_model(self):
        """Load the trained model if available."""
        try:
            if self.model_path.exists():
                self.model = joblib.load(str(self.model_path))
            else:
                self.logger.warning(f"Model file not found at {self.model_path}")
        except Exception as e:
            self.logger.error(f"Error loading model: {str(e)}")
            self.model = None

    def calculate_score(
        self,
        assessment_data: Dict[str, Any],
        criteria: Dict[str, Any]
    ) -> float:
        """Calculate overall assessment score based on criteria."""
        try:
            overall_score = 0.0
            for criterion, config in criteria.items():
                if criterion in assessment_data:
                    criterion_score = 0.0
                    for sub_criterion, weight in config['sub_criteria'].items():
                        if sub_criterion in assessment_data[criterion]:
                            criterion_score += assessment_data[criterion][sub_criterion] * weight
                    overall_score += criterion_score * config['weight']
            return min(max(overall_score, 0.0), 1.0)
        except Exception as e:
            self.logger.error(f"Error calculating score: {str(e)}")
            return 0.0 