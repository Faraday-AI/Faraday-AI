"""
Activity Validation Manager

This module provides validation and verification for physical education activities.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)


class ActivityValidationManager:
    """Manages validation and verification for physical education activities."""
    
    def __init__(self, db: Session, activity_manager=None):
        """Initialize the validation manager.
        
        Args:
            db: Database session
            activity_manager: Activity manager instance
        """
        self.db = db
        self.activity_manager = activity_manager
        self.validation_rules = self._load_validation_rules()
        
    def _load_validation_rules(self) -> Dict[str, Any]:
        """Load validation rules for activities.
        
        Returns:
            Validation rules dictionary
        """
        return {
            "duration": {
                "min": 5,
                "max": 120,
                "unit": "minutes"
            },
            "participants": {
                "min": 1,
                "max": 50
            },
            "equipment": {
                "required": ["safety_equipment"],
                "optional": ["additional_equipment"]
            },
            "safety": {
                "required_checks": ["environment", "equipment", "participants"],
                "risk_threshold": 0.7
            }
        }
    
    async def validate_activity_data(self, activity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate activity data against rules.
        
        Args:
            activity_data: Activity data to validate
            
        Returns:
            Validation result
        """
        try:
            validation_results = {
                "validation_passed": True,
                "errors": [],
                "warnings": [],
                "validated_at": datetime.now()
            }
            
            # Validate duration
            duration = activity_data.get("duration", 0)
            if duration < self.validation_rules["duration"]["min"]:
                validation_results["errors"].append(f"Duration too short: {duration} minutes")
                validation_results["validation_passed"] = False
            elif duration > self.validation_rules["duration"]["max"]:
                validation_results["errors"].append(f"Duration too long: {duration} minutes")
                validation_results["validation_passed"] = False
            
            # Validate participants
            participants = activity_data.get("participants", 0)
            if participants < self.validation_rules["participants"]["min"]:
                validation_results["errors"].append(f"Too few participants: {participants}")
                validation_results["validation_passed"] = False
            elif participants > self.validation_rules["participants"]["max"]:
                validation_results["warnings"].append(f"Large group: {participants} participants")
            
            # Validate equipment
            equipment = activity_data.get("equipment", [])
            required_equipment = self.validation_rules["equipment"]["required"]
            for req in required_equipment:
                if req not in equipment:
                    validation_results["errors"].append(f"Missing required equipment: {req}")
                    validation_results["validation_passed"] = False
            
            return validation_results
        except Exception as e:
            logger.error(f"Error validating activity data: {e}")
            return {"validation_passed": False, "error": str(e)}
    
    async def validate_student_eligibility(self, student_id: str, activity_id: str) -> Dict[str, Any]:
        """Validate if a student is eligible for an activity.
        
        Args:
            student_id: Student identifier
            activity_id: Activity identifier
            
        Returns:
            Eligibility validation result
        """
        try:
            # Mock eligibility check
            eligibility_result = {
                "eligible": True,
                "student_id": student_id,
                "activity_id": activity_id,
                "checks_passed": ["age", "fitness_level", "medical_clearance"],
                "restrictions": [],
                "validated_at": datetime.now()
            }
            
            # Mock some restrictions
            if student_id == "restricted_student":
                eligibility_result["eligible"] = False
                eligibility_result["restrictions"] = ["medical_restriction"]
            
            return eligibility_result
        except Exception as e:
            logger.error(f"Error validating student eligibility: {e}")
            return {"eligible": False, "error": str(e)}
    
    async def validate_environment_conditions(self, activity_id: str, environment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate environment conditions for an activity.
        
        Args:
            activity_id: Activity identifier
            environment_data: Environment data
            
        Returns:
            Environment validation result
        """
        try:
            validation_result = {
                "environment_safe": True,
                "activity_id": activity_id,
                "checks_passed": [],
                "warnings": [],
                "validated_at": datetime.now()
            }
            
            # Check temperature
            temperature = environment_data.get("temperature", 20)
            if temperature < 10 or temperature > 35:
                validation_result["environment_safe"] = False
                validation_result["warnings"].append(f"Temperature outside safe range: {temperature}°C")
            else:
                validation_result["checks_passed"].append("temperature")
            
            # Check humidity
            humidity = environment_data.get("humidity", 50)
            if humidity > 80:
                validation_result["warnings"].append(f"High humidity: {humidity}%")
            else:
                validation_result["checks_passed"].append("humidity")
            
            # Check surface condition
            surface = environment_data.get("surface_condition", "unknown")
            if surface in ["wet", "icy", "unsafe"]:
                validation_result["environment_safe"] = False
                validation_result["warnings"].append(f"Unsafe surface condition: {surface}")
            else:
                validation_result["checks_passed"].append("surface_condition")
            
            return validation_result
        except Exception as e:
            logger.error(f"Error validating environment conditions: {e}")
            return {"environment_safe": False, "error": str(e)}
    
    async def validate_equipment_safety(self, activity_id: str, equipment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate equipment safety for an activity.
        
        Args:
            activity_id: Activity identifier
            equipment_data: Equipment data
            
        Returns:
            Equipment validation result
        """
        try:
            validation_result = {
                "equipment_safe": True,
                "activity_id": activity_id,
                "safe_equipment": [],
                "unsafe_equipment": [],
                "maintenance_needed": [],
                "validated_at": datetime.now()
            }
            
            for equipment_id, equipment_info in equipment_data.items():
                condition = equipment_info.get("condition", "unknown")
                last_inspected = equipment_info.get("last_inspected")
                
                if condition == "good":
                    validation_result["safe_equipment"].append(equipment_id)
                elif condition == "fair":
                    validation_result["maintenance_needed"].append(equipment_id)
                elif condition in ["poor", "damaged", "unsafe"]:
                    validation_result["equipment_safe"] = False
                    validation_result["unsafe_equipment"].append(equipment_id)
                
                # Check inspection date
                if last_inspected:
                    days_since_inspection = (datetime.now() - last_inspected).days
                    if days_since_inspection > 30:
                        validation_result["maintenance_needed"].append(f"{equipment_id}_inspection_overdue")
            
            return validation_result
        except Exception as e:
            logger.error(f"Error validating equipment safety: {e}")
            return {"equipment_safe": False, "error": str(e)}
    
    async def generate_validation_report(self, activity_id: str, validation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a comprehensive validation report.
        
        Args:
            activity_id: Activity identifier
            validation_data: All validation data
            
        Returns:
            Validation report
        """
        try:
            report = {
                "report_generated": True,
                "activity_id": activity_id,
                "overall_validation_passed": True,
                "summary": {
                    "total_checks": 0,
                    "passed_checks": 0,
                    "failed_checks": 0,
                    "warnings": 0
                },
                "details": validation_data,
                "recommendations": [],
                "generated_at": datetime.now()
            }
            
            # Calculate summary
            for check_type, result in validation_data.items():
                if isinstance(result, dict):
                    if result.get("validation_passed") is False or result.get("eligible") is False:
                        report["overall_validation_passed"] = False
                        report["summary"]["failed_checks"] += 1
                    else:
                        report["summary"]["passed_checks"] += 1
                    report["summary"]["total_checks"] += 1
                    
                    # Add warnings
                    warnings = result.get("warnings", [])
                    report["summary"]["warnings"] += len(warnings)
            
            # Generate recommendations
            if not report["overall_validation_passed"]:
                report["recommendations"].append("Address failed validation checks before proceeding")
            if report["summary"]["warnings"] > 0:
                report["recommendations"].append("Review and address warnings")
            
            return report
        except Exception as e:
            logger.error(f"Error generating validation report: {e}")
            return {"report_generated": False, "error": str(e)} 

    async def validate_activity_creation(
        self,
        activity_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate activity creation data."""
        try:
            validation_result = await self.validate_activity_data(activity_data)
            
            # Additional creation-specific validations
            if not activity_data.get("name"):
                validation_result["errors"].append("Activity name is required")
                validation_result["validation_passed"] = False
            
            if not activity_data.get("type"):
                validation_result["errors"].append("Activity type is required")
                validation_result["validation_passed"] = False
            
            return {
                "validated": validation_result["validation_passed"],
                "errors": validation_result["errors"],
                "warnings": validation_result["warnings"]
            }
        except Exception as e:
            logger.error(f"Error validating activity creation: {e}")
            return {"validated": False, "errors": [str(e)]}

    async def validate_activity_update(
        self,
        activity_id: str,
        update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate activity update data."""
        try:
            # Check if activity exists
            if not self.activity_manager:
                return {"validated": False, "errors": ["Activity manager not available"]}
            
            # Mock activity existence check
            activity_exists = True  # This would normally check the database
            
            if not activity_exists:
                return {"validated": False, "errors": ["Activity not found"]}
            
            validation_result = await self.validate_activity_data(update_data)
            
            return {
                "validated": validation_result["validation_passed"],
                "errors": validation_result["errors"],
                "warnings": validation_result["warnings"]
            }
        except Exception as e:
            logger.error(f"Error validating activity update: {e}")
            return {"validated": False, "errors": [str(e)]}

    async def validate_activity_schedule(
        self,
        activity_id: str,
        schedule_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate activity schedule."""
        try:
            validation_result = {
                "validated": True,
                "errors": [],
                "warnings": []
            }
            
            # Validate start time
            start_time = schedule_data.get("start_time")
            if not start_time:
                validation_result["errors"].append("Start time is required")
                validation_result["validated"] = False
            
            # Validate end time
            end_time = schedule_data.get("end_time")
            if not end_time:
                validation_result["errors"].append("End time is required")
                validation_result["validated"] = False
            
            # Validate time range
            if start_time and end_time:
                try:
                    start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                    
                    if end_dt <= start_dt:
                        validation_result["errors"].append("End time must be after start time")
                        validation_result["validated"] = False
                    
                    duration = (end_dt - start_dt).total_seconds() / 60  # minutes
                    if duration < self.validation_rules["duration"]["min"]:
                        validation_result["errors"].append(f"Duration too short: {duration} minutes")
                        validation_result["validated"] = False
                    elif duration > self.validation_rules["duration"]["max"]:
                        validation_result["warnings"].append(f"Duration long: {duration} minutes")
                        
                except ValueError:
                    validation_result["errors"].append("Invalid date format")
                    validation_result["validated"] = False
            
            return validation_result
        except Exception as e:
            logger.error(f"Error validating activity schedule: {e}")
            return {"validated": False, "errors": [str(e)]}

    async def validate_activity_participants(
        self,
        activity_id: str,
        participant_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate activity participants."""
        try:
            validation_result = {
                "validated": True,
                "errors": [],
                "warnings": []
            }
            
            # Get activity details (mock)
            activity = {"max_participants": 30, "min_participants": 5}
            
            # Validate participant count
            participant_count = participant_data.get("count", 0)
            if participant_count < activity["min_participants"]:
                validation_result["errors"].append(f"Too few participants: {participant_count}")
                validation_result["validated"] = False
            elif participant_count > activity["max_participants"]:
                validation_result["errors"].append(f"Too many participants: {participant_count}")
                validation_result["validated"] = False
            
            # Validate participant list
            participants = participant_data.get("participants", [])
            if len(participants) != participant_count:
                validation_result["errors"].append("Participant count mismatch")
                validation_result["validated"] = False
            
            # Validate individual participants
            for participant in participants:
                if not participant.get("id"):
                    validation_result["errors"].append("Participant ID is required")
                    validation_result["validated"] = False
                
                # Check eligibility
                eligibility = await self.validate_student_eligibility(participant["id"], activity_id)
                if not eligibility.get("eligible", False):
                    validation_result["errors"].append(f"Student {participant['id']} not eligible")
                    validation_result["validated"] = False
            
            return validation_result
        except Exception as e:
            logger.error(f"Error validating activity participants: {e}")
            return {"validated": False, "errors": [str(e)]} 