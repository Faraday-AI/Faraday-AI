from typing import Dict, Any, List, Optional, Union
import logging
import os
from pathlib import Path
from sqlalchemy.orm import Session
from fastapi import Depends

from ..models.activity_adaptation.activity_adaptation_models import (
    ActivityAdaptation,
    AdaptationHistory,
    ActivityAdaptationModel
)
from ..models.activity import Activity
from ..models.student import Student
from app.core.database import get_db
from ..config.model_paths import get_model_path, ensure_model_directories

class ActivityAdaptationManager:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
        self.logger = logging.getLogger(__name__)
        
        # Initialize model paths
        ensure_model_directories()
        self.model_path = get_model_path('activity_adaptation')
        self.config_path = get_model_path('activity_adaptation', 'config_file')
        
        # Initialize adaptation model
        self.adaptation_model = ActivityAdaptationModel()
        
        # Configuration settings
        self.settings = {
            'max_adaptations_per_activity': 5,
            'adaptation_timeout': 3600,  # 1 hour in seconds
            'min_performance_threshold': 0.6,
            'max_performance_threshold': 0.9,
            'default_adaptation_duration': 15  # minutes
        }
        
        # Initialize adaptation rules
        self._init_adaptation_rules()
        
    def _init_adaptation_rules(self):
        """Initialize default adaptation rules."""
        self.adaptation_rules = {
            'difficulty': {
                'increase': {
                    'performance_threshold': 0.8,
                    'min_attempts': 3,
                    'max_increase': 2
                },
                'decrease': {
                    'performance_threshold': 0.4,
                    'min_attempts': 2,
                    'max_decrease': 2
                }
            },
            'duration': {
                'increase': {
                    'performance_threshold': 0.7,
                    'min_attempts': 3,
                    'max_increase': 10  # minutes
                },
                'decrease': {
                    'performance_threshold': 0.3,
                    'min_attempts': 2,
                    'max_decrease': 10  # minutes
                }
            }
        }
        
    async def suggest_adaptation(
        self,
        student_id: int,
        activity_id: int,
        current_performance: float
    ) -> Dict[str, Any]:
        """Suggest activity adaptations based on student performance."""
        try:
            # Get student and activity
            student = self.db.query(Student).filter(Student.id == student_id).first()
            activity = self.db.query(Activity).filter(Activity.id == activity_id).first()
            
            if not student or not activity:
                raise ValueError("Student or activity not found")
            
            # Get adaptation history
            history = self.db.query(AdaptationHistory).filter(
                AdaptationHistory.student_id == student_id,
                AdaptationHistory.activity_id == activity_id
            ).order_by(AdaptationHistory.created_at.desc()).first()
            
            # Generate adaptation suggestions
            suggestions = self.adaptation_model.predict_adaptation(
                student_id=student_id,
                activity_id=activity_id,
                current_performance=current_performance,
                history=history
            )
            
            return {
                'success': True,
                'suggestions': suggestions,
                'student_id': student_id,
                'activity_id': activity_id
            }
            
        except Exception as e:
            self.logger.error(f"Error suggesting adaptation: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'student_id': student_id,
                'activity_id': activity_id
            }
            
    async def apply_adaptation(
        self,
        student_id: int,
        activity_id: int,
        adaptation_type: str,
        adaptation_value: Any
    ) -> Dict[str, Any]:
        """Apply an adaptation to an activity for a student."""
        try:
            # Create adaptation record
            adaptation = ActivityAdaptation(
                student_id=student_id,
                activity_id=activity_id,
                adaptation_type=adaptation_type,
                adaptation_value=adaptation_value
            )
            
            self.db.add(adaptation)
            self.db.commit()
            
            # Create history record
            history = AdaptationHistory(
                student_id=student_id,
                activity_id=activity_id,
                adaptation_id=adaptation.id,
                previous_value=None,  # TODO: Get previous value
                new_value=adaptation_value
            )
            
            self.db.add(history)
            self.db.commit()
            
            return {
                'success': True,
                'adaptation_id': adaptation.id,
                'student_id': student_id,
                'activity_id': activity_id
            }
            
        except Exception as e:
            self.logger.error(f"Error applying adaptation: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'student_id': student_id,
                'activity_id': activity_id
            }
            
    async def get_adaptation_history(
        self,
        student_id: int,
        activity_id: int
    ) -> Dict[str, Any]:
        """Get adaptation history for a student and activity."""
        try:
            history = self.db.query(AdaptationHistory).filter(
                AdaptationHistory.student_id == student_id,
                AdaptationHistory.activity_id == activity_id
            ).order_by(AdaptationHistory.created_at.desc()).all()
            
            return {
                'success': True,
                'history': [
                    {
                        'id': record.id,
                        'adaptation_type': record.adaptation_type,
                        'previous_value': record.previous_value,
                        'new_value': record.new_value,
                        'created_at': record.created_at
                    }
                    for record in history
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Error getting adaptation history: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            } 