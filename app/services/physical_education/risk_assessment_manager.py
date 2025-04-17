from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
from sqlalchemy.orm import Session
from fastapi import Depends

from app.services.physical_education.models.safety import RiskAssessment
from app.core.database import get_db

class RiskAssessmentManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.activity_types = [
            "warmup", "stretching", "cardio", "strength_training",
            "team_sports", "individual_sports", "gymnastics", "other"
        ]
        self.risk_levels = ["low", "medium", "high", "critical"]
        self.environmental_risks = [
            "slippery_surface", "uneven_ground", "poor_lighting",
            "extreme_temperature", "poor_air_quality", "crowded_space",
            "equipment_hazard", "other"
        ]
        self.student_risks = [
            "lack_of_experience", "physical_limitation", "medical_condition",
            "behavioral_issue", "age_related", "other"
        ]
        self.activity_risks = [
            "high_impact", "complex_movements", "equipment_required",
            "team_interaction", "physical_contact", "other"
        ]

    async def create_assessment(
        self,
        class_id: str,
        activity_type: str,
        environment: str,
        risk_level: str,
        environmental_risks: List[str],
        student_risks: List[str],
        activity_risks: List[str],
        mitigation_strategies: List[str],
        metadata: Optional[Dict[str, Any]] = None,
        db: Session = Depends(get_db)
    ) -> Dict[str, Any]:
        """Create a new risk assessment."""
        try:
            # Validate activity type
            if activity_type not in self.activity_types:
                raise ValueError(f"Invalid activity type. Must be one of: {self.activity_types}")
            
            # Validate risk level
            if risk_level not in self.risk_levels:
                raise ValueError(f"Invalid risk level. Must be one of: {self.risk_levels}")
            
            # Validate environmental risks
            for risk in environmental_risks:
                if risk not in self.environmental_risks:
                    raise ValueError(f"Invalid environmental risk: {risk}")
            
            # Validate student risks
            for risk in student_risks:
                if risk not in self.student_risks:
                    raise ValueError(f"Invalid student risk: {risk}")
            
            # Validate activity risks
            for risk in activity_risks:
                if risk not in self.activity_risks:
                    raise ValueError(f"Invalid activity risk: {risk}")
            
            assessment = RiskAssessment(
                class_id=class_id,
                activity_type=activity_type,
                environment=environment,
                date=datetime.utcnow(),
                risk_level=risk_level,
                environmental_risks=environmental_risks,
                student_risks=student_risks,
                activity_risks=activity_risks,
                mitigation_strategies=mitigation_strategies,
                metadata=metadata or {}
            )
            
            db.add(assessment)
            db.commit()
            db.refresh(assessment)
            
            return {
                "success": True,
                "message": "Risk assessment created successfully",
                "assessment_id": assessment.id
            }
            
        except Exception as e:
            self.logger.error(f"Error creating risk assessment: {str(e)}")
            if db:
                db.rollback()
            return {
                "success": False,
                "message": f"Error creating risk assessment: {str(e)}"
            }

    async def get_assessment(
        self,
        assessment_id: str,
        db: Session = Depends(get_db)
    ) -> Optional[RiskAssessment]:
        """Retrieve a specific risk assessment by ID."""
        try:
            return db.query(RiskAssessment).filter(RiskAssessment.id == assessment_id).first()
        except Exception as e:
            self.logger.error(f"Error retrieving risk assessment: {str(e)}")
            return None

    async def get_assessments(
        self,
        class_id: Optional[str] = None,
        activity_type: Optional[str] = None,
        risk_level: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        db: Session = Depends(get_db)
    ) -> List[RiskAssessment]:
        """Retrieve risk assessments with optional filters."""
        try:
            query = db.query(RiskAssessment)
            
            if class_id:
                query = query.filter(RiskAssessment.class_id == class_id)
            if activity_type:
                query = query.filter(RiskAssessment.activity_type == activity_type)
            if risk_level:
                query = query.filter(RiskAssessment.risk_level == risk_level)
            if start_date:
                query = query.filter(RiskAssessment.date >= start_date)
            if end_date:
                query = query.filter(RiskAssessment.date <= end_date)
            
            return query.all()
            
        except Exception as e:
            self.logger.error(f"Error retrieving risk assessments: {str(e)}")
            return []

    async def update_assessment(
        self,
        assessment_id: str,
        update_data: Dict[str, Any],
        db: Session = Depends(get_db)
    ) -> Dict[str, Any]:
        """Update an existing risk assessment."""
        try:
            assessment = db.query(RiskAssessment).filter(RiskAssessment.id == assessment_id).first()
            if not assessment:
                return {
                    "success": False,
                    "message": "Risk assessment not found"
                }
            
            # Validate and update fields
            for key, value in update_data.items():
                if hasattr(assessment, key):
                    if key == "activity_type" and value not in self.activity_types:
                        raise ValueError(f"Invalid activity type: {value}")
                    if key == "risk_level" and value not in self.risk_levels:
                        raise ValueError(f"Invalid risk level: {value}")
                    if key == "environmental_risks":
                        for risk in value:
                            if risk not in self.environmental_risks:
                                raise ValueError(f"Invalid environmental risk: {risk}")
                    if key == "student_risks":
                        for risk in value:
                            if risk not in self.student_risks:
                                raise ValueError(f"Invalid student risk: {risk}")
                    if key == "activity_risks":
                        for risk in value:
                            if risk not in self.activity_risks:
                                raise ValueError(f"Invalid activity risk: {risk}")
                    setattr(assessment, key, value)
            
            db.commit()
            db.refresh(assessment)
            
            return {
                "success": True,
                "message": "Risk assessment updated successfully"
            }
            
        except Exception as e:
            self.logger.error(f"Error updating risk assessment: {str(e)}")
            if db:
                db.rollback()
            return {
                "success": False,
                "message": f"Error updating risk assessment: {str(e)}"
            }

    async def delete_assessment(
        self,
        assessment_id: str,
        db: Session = Depends(get_db)
    ) -> Dict[str, Any]:
        """Delete a risk assessment."""
        try:
            assessment = db.query(RiskAssessment).filter(RiskAssessment.id == assessment_id).first()
            if not assessment:
                return {
                    "success": False,
                    "message": "Risk assessment not found"
                }
            
            db.delete(assessment)
            db.commit()
            
            return {
                "success": True,
                "message": "Risk assessment deleted successfully"
            }
            
        except Exception as e:
            self.logger.error(f"Error deleting risk assessment: {str(e)}")
            if db:
                db.rollback()
            return {
                "success": False,
                "message": f"Error deleting risk assessment: {str(e)}"
            }

    async def get_assessment_statistics(
        self,
        class_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        db: Session = Depends(get_db)
    ) -> Dict[str, Any]:
        """Get statistics about risk assessments."""
        try:
            query = db.query(RiskAssessment)
            if class_id:
                query = query.filter(RiskAssessment.class_id == class_id)
            if start_date:
                query = query.filter(RiskAssessment.date >= start_date)
            if end_date:
                query = query.filter(RiskAssessment.date <= end_date)
            
            assessments = query.all()
            
            stats = {
                "total": len(assessments),
                "by_activity": {},
                "by_risk_level": {},
                "common_risks": {
                    "environmental": {},
                    "student": {},
                    "activity": {}
                },
                "trends": {}
            }
            
            for assessment in assessments:
                # Count by activity type
                stats["by_activity"][assessment.activity_type] = \
                    stats["by_activity"].get(assessment.activity_type, 0) + 1
                
                # Count by risk level
                stats["by_risk_level"][assessment.risk_level] = \
                    stats["by_risk_level"].get(assessment.risk_level, 0) + 1
                
                # Count common risks
                for risk in assessment.environmental_risks:
                    stats["common_risks"]["environmental"][risk] = \
                        stats["common_risks"]["environmental"].get(risk, 0) + 1
                
                for risk in assessment.student_risks:
                    stats["common_risks"]["student"][risk] = \
                        stats["common_risks"]["student"].get(risk, 0) + 1
                
                for risk in assessment.activity_risks:
                    stats["common_risks"]["activity"][risk] = \
                        stats["common_risks"]["activity"].get(risk, 0) + 1
                
                # Calculate trends
                date_key = assessment.date.strftime("%Y-%m")
                stats["trends"][date_key] = stats["trends"].get(date_key, 0) + 1
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error calculating risk assessment statistics: {str(e)}")
            return {}

    async def bulk_update_assessments(
        self,
        updates: List[Dict[str, Any]],
        db: Session = Depends(get_db)
    ) -> Dict[str, int]:
        """Bulk update multiple risk assessments."""
        try:
            success_count = 0
            failure_count = 0
            
            for update in updates:
                try:
                    assessment_id = update.pop("id")
                    result = await self.update_assessment(assessment_id, update, db)
                    if result["success"]:
                        success_count += 1
                    else:
                        failure_count += 1
                except Exception as e:
                    self.logger.error(f"Error in bulk update: {str(e)}")
                    failure_count += 1
            
            return {
                "success": success_count,
                "failure": failure_count
            }
            
        except Exception as e:
            self.logger.error(f"Error in bulk update operation: {str(e)}")
            if db:
                db.rollback()
            return {
                "success": 0,
                "failure": len(updates)
            }

    async def bulk_delete_assessments(
        self,
        assessment_ids: List[str],
        db: Session = Depends(get_db)
    ) -> Dict[str, int]:
        """Bulk delete multiple risk assessments."""
        try:
            success_count = 0
            failure_count = 0
            
            for assessment_id in assessment_ids:
                try:
                    result = await self.delete_assessment(assessment_id, db)
                    if result["success"]:
                        success_count += 1
                    else:
                        failure_count += 1
                except Exception as e:
                    self.logger.error(f"Error in bulk delete: {str(e)}")
                    failure_count += 1
            
            return {
                "success": success_count,
                "failure": failure_count
            }
            
        except Exception as e:
            self.logger.error(f"Error in bulk delete operation: {str(e)}")
            if db:
                db.rollback()
            return {
                "success": 0,
                "failure": len(assessment_ids)
            } 