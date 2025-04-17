from typing import Dict, Any, List, Optional, Union
import logging
import os
from pathlib import Path
from sqlalchemy.orm import Session
from fastapi import Depends

from app.services.physical_education.models.skill_assessment.skill_assessment_models import (
    SkillAssessment as ActivityAssessment,
    AssessmentCriteria,
    AssessmentResult,
    AssessmentHistory
)
from app.services.physical_education.models.activity import Activity
from app.services.physical_education.models.student import Student
from app.core.database import get_db
from app.services.physical_education.models.skill_assessment.skill_assessment_models import SkillAssessmentModel as ActivityAssessmentModel
from app.services.physical_education.config.model_paths import get_model_path, ensure_model_directories

class ActivityAssessmentManager:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
        self.logger = logging.getLogger(__name__)
        
        # Initialize model paths
        ensure_model_directories()
        self.model_path = get_model_path('activity_assessment')
        self.config_path = get_model_path('activity_assessment', 'config_file')
        
        # Initialize assessment model
        self.assessment_model = ActivityAssessmentModel()
        
        # Configuration settings
        self.settings = {
            'max_assessments_per_activity': 3,
            'assessment_timeout': 1800,  # 30 minutes in seconds
            'min_performance_threshold': 0.5,
            'max_performance_threshold': 1.0,
            'default_assessment_duration': 10  # minutes
        }
        
        # Initialize assessment criteria
        self._init_assessment_criteria()
        
    def _init_assessment_criteria(self):
        """Initialize default assessment criteria."""
        self.assessment_criteria = {
            'technique': {
                'weight': 0.4,
                'sub_criteria': {
                    'form': 0.5,
                    'precision': 0.3,
                    'consistency': 0.2
                }
            },
            'performance': {
                'weight': 0.3,
                'sub_criteria': {
                    'speed': 0.4,
                    'endurance': 0.3,
                    'strength': 0.3
                }
            },
            'safety': {
                'weight': 0.2,
                'sub_criteria': {
                    'posture': 0.4,
                    'equipment_usage': 0.3,
                    'environment_awareness': 0.3
                }
            },
            'engagement': {
                'weight': 0.1,
                'sub_criteria': {
                    'focus': 0.4,
                    'effort': 0.3,
                    'persistence': 0.3
                }
            }
        }
        
    async def assess_activity(
        self,
        student_id: int,
        activity_id: int,
        assessment_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess a student's performance in an activity."""
        try:
            # Get student and activity
            student = self.db.query(Student).filter(Student.id == student_id).first()
            activity = self.db.query(Activity).filter(Activity.id == activity_id).first()
            
            if not student or not activity:
                raise ValueError("Student or activity not found")
            
            # Calculate overall score
            overall_score = self.assessment_model.calculate_score(
                assessment_data=assessment_data,
                criteria=self.assessment_criteria
            )
            
            # Create assessment record
            assessment = ActivityAssessment(
                student_id=student_id,
                activity_id=activity_id,
                overall_score=overall_score,
                assessment_data=assessment_data
            )
            
            self.db.add(assessment)
            self.db.commit()
            
            # Create result record
            result = AssessmentResult(
                assessment_id=assessment.id,
                student_id=student_id,
                activity_id=activity_id,
                score=overall_score,
                criteria_scores=self._calculate_criteria_scores(assessment_data)
            )
            
            self.db.add(result)
            self.db.commit()
            
            # Create history record
            history = AssessmentHistory(
                assessment_id=assessment.id,
                student_id=student_id,
                activity_id=activity_id,
                previous_score=None,  # TODO: Get previous score
                new_score=overall_score
            )
            
            self.db.add(history)
            self.db.commit()
            
            return {
                'success': True,
                'assessment_id': assessment.id,
                'student_id': student_id,
                'activity_id': activity_id,
                'overall_score': overall_score,
                'criteria_scores': result.criteria_scores
            }
            
        except Exception as e:
            self.logger.error(f"Error assessing activity: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'student_id': student_id,
                'activity_id': activity_id
            }
            
    def _calculate_criteria_scores(self, assessment_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate scores for each assessment criterion."""
        criteria_scores = {}
        
        for criterion, config in self.assessment_criteria.items():
            if criterion in assessment_data:
                criterion_score = 0
                for sub_criterion, weight in config['sub_criteria'].items():
                    if sub_criterion in assessment_data[criterion]:
                        criterion_score += assessment_data[criterion][sub_criterion] * weight
                criteria_scores[criterion] = criterion_score * config['weight']
                
        return criteria_scores
        
    async def get_assessment_history(
        self,
        student_id: int,
        activity_id: int
    ) -> Dict[str, Any]:
        """Get assessment history for a student and activity."""
        try:
            history = self.db.query(AssessmentHistory).filter(
                AssessmentHistory.student_id == student_id,
                AssessmentHistory.activity_id == activity_id
            ).order_by(AssessmentHistory.created_at.desc()).all()
            
            return {
                'success': True,
                'history': [
                    {
                        'id': record.id,
                        'assessment_id': record.assessment_id,
                        'previous_score': record.previous_score,
                        'new_score': record.new_score,
                        'created_at': record.created_at
                    }
                    for record in history
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Error getting assessment history: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
            
    async def get_assessment_summary(
        self,
        student_id: int,
        activity_id: int
    ) -> Dict[str, Any]:
        """Get a summary of assessment results for a student and activity."""
        try:
            results = self.db.query(AssessmentResult).filter(
                AssessmentResult.student_id == student_id,
                AssessmentResult.activity_id == activity_id
            ).order_by(AssessmentResult.created_at.desc()).all()
            
            if not results:
                return {
                    'success': True,
                    'summary': {
                        'total_assessments': 0,
                        'average_score': 0,
                        'highest_score': 0,
                        'lowest_score': 0,
                        'improvement_trend': 0
                    }
                }
                
            scores = [result.score for result in results]
            criteria_scores = {}
            
            for result in results:
                for criterion, score in result.criteria_scores.items():
                    if criterion not in criteria_scores:
                        criteria_scores[criterion] = []
                    criteria_scores[criterion].append(score)
                    
            return {
                'success': True,
                'summary': {
                    'total_assessments': len(results),
                    'average_score': sum(scores) / len(scores),
                    'highest_score': max(scores),
                    'lowest_score': min(scores),
                    'improvement_trend': self._calculate_improvement_trend(scores),
                    'criteria_averages': {
                        criterion: sum(scores) / len(scores)
                        for criterion, scores in criteria_scores.items()
                    }
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting assessment summary: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
            
    def _calculate_improvement_trend(self, scores: List[float]) -> float:
        """Calculate the improvement trend based on assessment scores."""
        if len(scores) < 2:
            return 0
            
        # Calculate the slope of the linear regression line
        x = list(range(len(scores)))
        y = scores
        
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(xi * yi for xi, yi in zip(x, y))
        sum_x2 = sum(xi * xi for xi in x)
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        
        return slope 