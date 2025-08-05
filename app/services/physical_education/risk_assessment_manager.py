from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
from sqlalchemy.orm import Session
from fastapi import Depends
from sqlalchemy import and_, or_

from app.models.physical_education.safety import RiskAssessment
from app.core.database import get_db
from app.core.monitoring import track_metrics

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

    async def check_health(self) -> Dict[str, Any]:
        """Check risk assessment manager health."""
        try:
            return {
                "status": "healthy",
                "message": "Risk assessment manager is operational",
                "timestamp": datetime.utcnow()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Risk assessment manager error: {str(e)}",
                "timestamp": datetime.utcnow()
            } 

    async def assess_activity_risk(
        self,
        activity_type: str,
        activity_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess risk for a specific activity."""
        try:
            risk_score = 0.0
            risk_factors = []
            
            # Assess based on activity type
            if activity_type in ["team_sports", "gymnastics"]:
                risk_score += 0.3
                risk_factors.append("high_impact")
            
            if activity_data.get("equipment_required"):
                risk_score += 0.2
                risk_factors.append("equipment_required")
            
            if activity_data.get("physical_contact"):
                risk_score += 0.4
                risk_factors.append("physical_contact")
            
            # Determine risk level
            if risk_score >= 0.7:
                risk_level = "high"
            elif risk_score >= 0.4:
                risk_level = "medium"
            else:
                risk_level = "low"
            
            return {
                "assessed": True,
                "activity_type": activity_type,
                "risk_score": risk_score,
                "risk_level": risk_level,
                "risk_factors": risk_factors
            }
        except Exception as e:
            self.logger.error(f"Error assessing activity risk: {str(e)}")
            return {"assessed": False, "error": str(e)}

    async def assess_student_risk(
        self,
        student_id: str,
        student_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess risk for a specific student."""
        try:
            risk_score = 0.0
            risk_factors = []
            
            # Assess based on student data
            if student_data.get("medical_conditions"):
                risk_score += 0.3
                risk_factors.append("medical_condition")
            
            if student_data.get("experience_level") == "beginner":
                risk_score += 0.2
                risk_factors.append("lack_of_experience")
            
            if student_data.get("age") < 10:
                risk_score += 0.1
                risk_factors.append("age_related")
            
            # Determine risk level
            if risk_score >= 0.5:
                risk_level = "high"
            elif risk_score >= 0.2:
                risk_level = "medium"
            else:
                risk_level = "low"
            
            return {
                "assessed": True,
                "student_id": student_id,
                "risk_score": risk_score,
                "risk_level": risk_level,
                "risk_factors": risk_factors
            }
        except Exception as e:
            self.logger.error(f"Error assessing student risk: {str(e)}")
            return {"assessed": False, "error": str(e)}

    async def assess_environmental_risk(
        self,
        environment_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess environmental risks."""
        try:
            risk_score = 0.0
            risk_factors = []
            
            # Assess environmental conditions
            if environment_data.get("surface_condition") == "slippery":
                risk_score += 0.4
                risk_factors.append("slippery_surface")
            
            if environment_data.get("lighting") == "poor":
                risk_score += 0.3
                risk_factors.append("poor_lighting")
            
            if environment_data.get("temperature") > 90:
                risk_score += 0.2
                risk_factors.append("extreme_temperature")
            
            # Determine risk level
            if risk_score >= 0.5:
                risk_level = "high"
            elif risk_score >= 0.2:
                risk_level = "medium"
            else:
                risk_level = "low"
            
            return {
                "assessed": True,
                "risk_score": risk_score,
                "risk_level": risk_level,
                "risk_factors": risk_factors
            }
        except Exception as e:
            self.logger.error(f"Error assessing environmental risk: {str(e)}")
            return {"assessed": False, "error": str(e)}

    async def assess_equipment_risk(
        self,
        equipment_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess equipment-related risks."""
        try:
            risk_score = 0.0
            risk_factors = []
            
            # Assess equipment condition
            if equipment_data.get("condition") == "damaged":
                risk_score += 0.5
                risk_factors.append("equipment_hazard")
            
            if equipment_data.get("maintenance_due"):
                risk_score += 0.3
                risk_factors.append("equipment_hazard")
            
            if equipment_data.get("age") > 5:
                risk_score += 0.2
                risk_factors.append("equipment_hazard")
            
            # Determine risk level
            if risk_score >= 0.5:
                risk_level = "high"
            elif risk_score >= 0.2:
                risk_level = "medium"
            else:
                risk_level = "low"
            
            return {
                "assessed": True,
                "risk_score": risk_score,
                "risk_level": risk_level,
                "risk_factors": risk_factors
            }
        except Exception as e:
            self.logger.error(f"Error assessing equipment risk: {str(e)}")
            return {"assessed": False, "error": str(e)}

    async def assess_group_risk(
        self,
        group_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess risks for a group of students."""
        try:
            risk_score = 0.0
            risk_factors = []
            
            # Assess group size
            group_size = group_data.get("size", 0)
            if group_size > 30:
                risk_score += 0.2
                risk_factors.append("crowded_space")
            
            # Assess group dynamics
            if group_data.get("experience_mix") == "mixed":
                risk_score += 0.1
                risk_factors.append("experience_variation")
            
            # Determine risk level
            if risk_score >= 0.3:
                risk_level = "medium"
            else:
                risk_level = "low"
            
            return {
                "assessed": True,
                "risk_score": risk_score,
                "risk_level": risk_level,
                "risk_factors": risk_factors
            }
        except Exception as e:
            self.logger.error(f"Error assessing group risk: {str(e)}")
            return {"assessed": False, "error": str(e)}

    async def generate_risk_report(
        self,
        assessment_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate a comprehensive risk report."""
        try:
            report = {
                "report_id": f"risk_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                "generated_at": datetime.utcnow().isoformat(),
                "overall_risk_level": "medium",
                "risk_summary": {
                    "activity_risks": assessment_data.get("activity_risks", []),
                    "environmental_risks": assessment_data.get("environmental_risks", []),
                    "student_risks": assessment_data.get("student_risks", [])
                },
                "recommendations": [
                    "Implement safety protocols",
                    "Provide proper supervision",
                    "Ensure equipment is in good condition"
                ]
            }
            
            return {
                "generated": True,
                "report": report
            }
        except Exception as e:
            self.logger.error(f"Error generating risk report: {str(e)}")
            return {"generated": False, "error": str(e)}

    async def calculate_risk_score(
        self,
        risk_factors: List[str]
    ) -> float:
        """Calculate overall risk score from risk factors."""
        try:
            risk_weights = {
                "high_impact": 0.3,
                "equipment_required": 0.2,
                "physical_contact": 0.4,
                "medical_condition": 0.3,
                "lack_of_experience": 0.2,
                "age_related": 0.1,
                "slippery_surface": 0.4,
                "poor_lighting": 0.3,
                "extreme_temperature": 0.2,
                "equipment_hazard": 0.5,
                "crowded_space": 0.2,
                "experience_variation": 0.1
            }
            
            total_score = 0.0
            for factor in risk_factors:
                total_score += risk_weights.get(factor, 0.1)
            
            return min(total_score, 1.0)  # Cap at 1.0
        except Exception as e:
            self.logger.error(f"Error calculating risk score: {str(e)}")
            return 0.0

    async def get_risk_thresholds(self) -> Dict[str, float]:
        """Get risk thresholds for different levels."""
        return {
            "low": 0.2,
            "medium": 0.5,
            "high": 0.7,
            "critical": 0.9
        }

    async def get_mitigation_strategies(
        self,
        risk_factors: List[str]
    ) -> List[str]:
        """Get mitigation strategies for given risk factors."""
        strategies = {
            "high_impact": ["Use proper technique", "Provide adequate padding"],
            "equipment_required": ["Inspect equipment", "Provide training"],
            "physical_contact": ["Establish clear rules", "Supervise closely"],
            "medical_condition": ["Consult medical professionals", "Adapt activities"],
            "lack_of_experience": ["Provide instruction", "Start with basics"],
            "slippery_surface": ["Clean surface", "Use appropriate footwear"],
            "poor_lighting": ["Improve lighting", "Schedule during daylight"],
            "equipment_hazard": ["Repair or replace equipment", "Regular maintenance"]
        }
        
        mitigation_list = []
        for factor in risk_factors:
            if factor in strategies:
                mitigation_list.extend(strategies[factor])
        
        return list(set(mitigation_list))  # Remove duplicates

    async def create_monitoring_plan(
        self,
        risk_level: str
    ) -> Dict[str, Any]:
        """Create a monitoring plan based on risk level."""
        try:
            monitoring_frequency = {
                "low": "weekly",
                "medium": "daily",
                "high": "continuous",
                "critical": "continuous"
            }
            
            plan = {
                "risk_level": risk_level,
                "monitoring_frequency": monitoring_frequency.get(risk_level, "daily"),
                "checkpoints": [
                    "Pre-activity safety check",
                    "During activity monitoring",
                    "Post-activity assessment"
                ],
                "alerts": risk_level in ["high", "critical"]
            }
            
            return {
                "created": True,
                "plan": plan
            }
        except Exception as e:
            self.logger.error(f"Error creating monitoring plan: {str(e)}")
            return {"created": False, "error": str(e)}

    async def generate_risk_documentation(
        self,
        assessment_id: str
    ) -> Dict[str, Any]:
        """Generate risk documentation for an assessment."""
        try:
            documentation = {
                "assessment_id": assessment_id,
                "documentation_id": f"doc_{assessment_id}_{datetime.utcnow().strftime('%Y%m%d')}",
                "created_at": datetime.utcnow().isoformat(),
                "sections": [
                    "Risk Assessment Summary",
                    "Risk Factors Analysis",
                    "Mitigation Strategies",
                    "Monitoring Plan",
                    "Emergency Procedures"
                ],
                "status": "completed"
            }
            
            return {
                "generated": True,
                "documentation": documentation
            } 
        except Exception as e:
            self.logger.error(f"Error generating risk documentation: {str(e)}")
            return {"generated": False, "error": str(e)} 