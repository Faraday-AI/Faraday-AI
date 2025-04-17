import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
from app.core.monitoring import track_metrics
from app.services.physical_education.student_manager import StudentManager
from app.services.physical_education.lesson_planner import LessonPlanner
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.core.database import get_db
from app.services.physical_education.models.safety import (
    SafetyIncident, RiskAssessment, SafetyCheck, 
    EquipmentCheck, EnvironmentalCheck
)

class SafetyManager:
    """Service for managing safety protocols, risk assessment, and emergency procedures."""
    
    def __init__(self):
        self.logger = logging.getLogger("safety_manager")
        self.student_manager = StudentManager()
        self.lesson_planner = LessonPlanner()
        
        # Safety protocols
        self.safety_protocols = {
            "general": {
                "supervision": {
                    "min_ratio": 1/15,  # 1 supervisor per 15 students
                    "qualifications": ["First Aid", "CPR", "AED"],
                    "responsibilities": [
                        "Monitor student activities",
                        "Enforce safety rules",
                        "Respond to emergencies"
                    ]
                },
                "equipment": {
                    "inspection_frequency": 7,  # days
                    "maintenance_requirements": [
                        "Regular cleaning",
                        "Periodic inspection",
                        "Immediate repair of damaged items"
                    ]
                },
                "environment": {
                    "space_requirements": {
                        "indoor": 35,  # square feet per student
                        "outdoor": 100  # square feet per student
                    },
                    "surface_requirements": [
                        "Non-slip",
                        "Impact-absorbing",
                        "Well-maintained"
                    ]
                }
            },
            "activities": {
                "warmup": {
                    "duration": 10,  # minutes
                    "requirements": [
                        "Proper stretching",
                        "Gradual intensity increase",
                        "Hydration check"
                    ]
                },
                "main_activity": {
                    "requirements": [
                        "Proper technique demonstration",
                        "Progressive skill development",
                        "Adequate rest periods"
                    ]
                },
                "cooldown": {
                    "duration": 5,  # minutes
                    "requirements": [
                        "Proper stretching",
                        "Hydration",
                        "Cool-down exercises"
                    ]
                }
            }
        }
        
        # Risk factors
        self.risk_factors = {
            "environmental": [
                "temperature",
                "humidity",
                "air_quality",
                "surface_conditions",
                "lighting",
                "equipment_condition"
            ],
            "student": [
                "medical_conditions",
                "skill_level",
                "fatigue",
                "hydration",
                "previous_injuries"
            ],
            "activity": [
                "intensity",
                "complexity",
                "equipment_usage",
                "contact_level",
                "duration"
            ]
        }
        
        # Emergency procedures
        self.emergency_procedures = {
            "medical_emergency": {
                "steps": [
                    "Assess situation",
                    "Call emergency services",
                    "Administer first aid",
                    "Contact emergency contacts",
                    "Document incident"
                ],
                "required_equipment": [
                    "First aid kit",
                    "AED",
                    "Emergency contact list",
                    "Incident report forms"
                ]
            },
            "environmental_emergency": {
                "steps": [
                    "Assess danger",
                    "Evacuate if necessary",
                    "Secure equipment",
                    "Contact administration",
                    "Document incident"
                ],
                "required_equipment": [
                    "Emergency evacuation plan",
                    "Weather monitoring tools",
                    "Communication devices"
                ]
            },
            "equipment_failure": {
                "steps": [
                    "Stop activity",
                    "Remove damaged equipment",
                    "Assess for injuries",
                    "Report incident",
                    "Document details"
                ],
                "required_equipment": [
                    "Backup equipment",
                    "Maintenance tools",
                    "Incident report forms"
                ]
            }
        }
        
        # Incident tracking
        self.incidents: Dict[str, List[Dict[str, Any]]] = {}
        self.risk_assessments: Dict[str, Dict[str, Any]] = {}
        self.safety_checks: Dict[str, List[Dict[str, Any]]] = {}

    async def initialize(self):
        """Initialize the safety manager."""
        try:
            # Initialize dependent services
            await self.student_manager.initialize()
            await self.lesson_planner.initialize()
            
            # Load safety data
            self.load_safety_data()
            
            self.logger.info("Safety manager initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing safety manager: {str(e)}")
            raise

    async def cleanup(self):
        """Cleanup safety manager resources."""
        try:
            # Cleanup dependent services
            await self.student_manager.cleanup()
            await self.lesson_planner.cleanup()
            
            # Save safety data
            self.save_safety_data()
            
            self.logger.info("Safety manager cleaned up successfully")
        except Exception as e:
            self.logger.error(f"Error cleaning up safety manager: {str(e)}")
            raise

    def load_safety_data(self):
        """Load safety data from persistent storage."""
        try:
            # TODO: Implement data loading from persistent storage
            self.logger.info("Safety data loaded successfully")
        except Exception as e:
            self.logger.error(f"Error loading safety data: {str(e)}")
            raise

    @track_metrics
    async def conduct_risk_assessment(self,
                                    class_id: str,
                                    activity_type: str,
                                    environment: str) -> Dict[str, Any]:
        """Conduct a risk assessment for a class activity."""
        try:
            # Validate parameters
            self.validate_risk_assessment_parameters(class_id, activity_type, environment)
            
            # Get class information
            class_info = self.student_manager.classes[class_id]
            
            # Get student information
            students = [
                self.student_manager.students[student_id]
                for student_id in class_info["students"]
            ]
            
            # Assess environmental risks
            environmental_risks = self.assess_environmental_risks(environment)
            
            # Assess student risks
            student_risks = self.assess_student_risks(students)
            
            # Assess activity risks
            activity_risks = self.assess_activity_risks(activity_type)
            
            # Calculate overall risk level
            risk_level = self.calculate_risk_level(
                environmental_risks,
                student_risks,
                activity_risks
            )
            
            # Generate risk assessment report
            assessment = {
                "class_id": class_id,
                "activity_type": activity_type,
                "environment": environment,
                "date": datetime.now().isoformat(),
                "risk_level": risk_level,
                "environmental_risks": environmental_risks,
                "student_risks": student_risks,
                "activity_risks": activity_risks,
                "mitigation_strategies": self.generate_mitigation_strategies(
                    risk_level,
                    environmental_risks,
                    student_risks,
                    activity_risks
                )
            }
            
            # Store assessment
            self.risk_assessments[class_id] = assessment
            
            return assessment
            
        except Exception as e:
            self.logger.error(f"Error conducting risk assessment: {str(e)}")
            raise

    def validate_risk_assessment_parameters(self,
                                          class_id: str,
                                          activity_type: str,
                                          environment: str):
        """Validate risk assessment parameters."""
        try:
            # Validate class ID
            if class_id not in self.student_manager.classes:
                raise ValueError(f"Class {class_id} does not exist")
            
            # Validate activity type
            if activity_type not in self.safety_protocols["activities"]:
                raise ValueError(f"Invalid activity type: {activity_type}")
            
            # Validate environment
            if environment not in ["indoor", "outdoor"]:
                raise ValueError("Environment must be 'indoor' or 'outdoor'")
            
        except Exception as e:
            self.logger.error(f"Error validating risk assessment parameters: {str(e)}")
            raise

    def assess_environmental_risks(self, environment: str) -> Dict[str, Any]:
        """Assess environmental risks."""
        try:
            risks = {
                "temperature": 0,
                "humidity": 0,
                "air_quality": 0,
                "surface_conditions": 0,
                "lighting": 0,
                "equipment_condition": 0
            }
            
            # Get current environmental conditions
            current_conditions = self.get_current_environmental_conditions(environment)
            
            # Assess temperature risk
            if current_conditions["temperature"] < 15 or current_conditions["temperature"] > 30:
                risks["temperature"] = 0.8
            elif current_conditions["temperature"] < 18 or current_conditions["temperature"] > 27:
                risks["temperature"] = 0.5
            
            # Assess humidity risk
            if current_conditions["humidity"] < 30 or current_conditions["humidity"] > 70:
                risks["humidity"] = 0.8
            elif current_conditions["humidity"] < 40 or current_conditions["humidity"] > 60:
                risks["humidity"] = 0.5
            
            # Assess air quality risk
            if current_conditions["air_quality"] < 50:
                risks["air_quality"] = 0.8
            elif current_conditions["air_quality"] < 70:
                risks["air_quality"] = 0.5
            
            # Assess surface conditions risk
            if not current_conditions["surface_conditions"]["is_safe"]:
                risks["surface_conditions"] = 0.8
            elif current_conditions["surface_conditions"]["needs_attention"]:
                risks["surface_conditions"] = 0.5
            
            # Assess lighting risk
            if current_conditions["lighting"] < 300:  # lux
                risks["lighting"] = 0.8
            elif current_conditions["lighting"] < 500:
                risks["lighting"] = 0.5
            
            # Assess equipment condition risk
            if not current_conditions["equipment_condition"]["is_safe"]:
                risks["equipment_condition"] = 0.8
            elif current_conditions["equipment_condition"]["needs_attention"]:
                risks["equipment_condition"] = 0.5
            
            return risks
            
        except Exception as e:
            self.logger.error(f"Error assessing environmental risks: {str(e)}")
            return {}

    def get_current_environmental_conditions(self, environment: str) -> Dict[str, Any]:
        """Get current environmental conditions."""
        try:
            # TODO: Replace with actual sensor data or API calls
            return {
                "temperature": 22,  # Celsius
                "humidity": 50,  # Percentage
                "air_quality": 80,  # AQI
                "surface_conditions": {
                    "is_safe": True,
                    "needs_attention": False
                },
                "lighting": 600,  # lux
                "equipment_condition": {
                    "is_safe": True,
                    "needs_attention": False
                }
            }
        except Exception as e:
            self.logger.error(f"Error getting environmental conditions: {str(e)}")
            return {}

    def assess_student_risks(self, students: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess student-related risks."""
        try:
            risks = {
                "medical_conditions": 0,
                "skill_level": 0,
                "fatigue": 0,
                "hydration": 0,
                "previous_injuries": 0
            }
            
            # Assess risks based on student profiles
            for student in students:
                # Medical conditions
                if student["medical_conditions"]:
                    risks["medical_conditions"] += 1
                
                # Skill level
                if student["skill_level"] == "beginner":
                    risks["skill_level"] += 1
                
                # Previous injuries
                if "previous_injuries" in student and student["previous_injuries"]:
                    risks["previous_injuries"] += 1
            
            # Normalize risk scores
            for risk in risks:
                risks[risk] = min(1, risks[risk] / len(students))
            
            return risks
            
        except Exception as e:
            self.logger.error(f"Error assessing student risks: {str(e)}")
            return {}

    def assess_activity_risks(self, activity_type: str) -> Dict[str, Any]:
        """Assess activity-related risks."""
        try:
            risks = {
                "intensity": 0,
                "complexity": 0,
                "equipment_usage": 0,
                "contact_level": 0,
                "duration": 0
            }
            
            # Get activity requirements
            activity_requirements = self.safety_protocols["activities"][activity_type]
            
            # Assess risks based on activity requirements
            if "duration" in activity_requirements:
                risks["duration"] = min(1, activity_requirements["duration"] / 60)
            
            if "requirements" in activity_requirements:
                if "Proper technique demonstration" in activity_requirements["requirements"]:
                    risks["complexity"] += 0.2
                if "Progressive skill development" in activity_requirements["requirements"]:
                    risks["intensity"] += 0.2
            
            return risks
            
        except Exception as e:
            self.logger.error(f"Error assessing activity risks: {str(e)}")
            return {}

    def calculate_risk_level(self,
                           environmental_risks: Dict[str, Any],
                           student_risks: Dict[str, Any],
                           activity_risks: Dict[str, Any]) -> str:
        """Calculate overall risk level."""
        try:
            # Calculate average risk scores
            env_score = sum(environmental_risks.values()) / len(environmental_risks)
            student_score = sum(student_risks.values()) / len(student_risks)
            activity_score = sum(activity_risks.values()) / len(activity_risks)
            
            # Calculate overall score
            overall_score = (env_score + student_score + activity_score) / 3
            
            # Determine risk level
            if overall_score >= 0.7:
                return "high"
            elif overall_score >= 0.4:
                return "medium"
            else:
                return "low"
            
        except Exception as e:
            self.logger.error(f"Error calculating risk level: {str(e)}")
            return "unknown"

    def generate_mitigation_strategies(self,
                                     risk_level: str,
                                     environmental_risks: Dict[str, Any],
                                     student_risks: Dict[str, Any],
                                     activity_risks: Dict[str, Any]) -> List[str]:
        """Generate risk mitigation strategies."""
        try:
            strategies = []
            
            # Add general strategies based on risk level
            if risk_level == "high":
                strategies.extend([
                    "Increase supervision ratio",
                    "Implement additional safety measures",
                    "Consider alternative activities"
                ])
            elif risk_level == "medium":
                strategies.extend([
                    "Review safety protocols",
                    "Ensure proper equipment",
                    "Monitor student conditions"
                ])
            
            # Add specific strategies for environmental risks
            for risk, score in environmental_risks.items():
                if score > 0.5:
                    strategies.append(f"Address {risk} concerns")
            
            # Add specific strategies for student risks
            for risk, score in student_risks.items():
                if score > 0.5:
                    strategies.append(f"Implement {risk} accommodations")
            
            # Add specific strategies for activity risks
            for risk, score in activity_risks.items():
                if score > 0.5:
                    strategies.append(f"Modify {risk} parameters")
            
            return strategies
            
        except Exception as e:
            self.logger.error(f"Error generating mitigation strategies: {str(e)}")
            return []

    @track_metrics
    async def record_incident(self,
                            class_id: str,
                            incident_type: str,
                            description: str,
                            severity: str,
                            affected_students: List[str],
                            actions_taken: List[str]) -> Dict[str, Any]:
        """Record a safety incident."""
        try:
            # Validate parameters
            self.validate_incident_parameters(
                class_id,
                incident_type,
                severity,
                affected_students
            )
            
            # Create incident record
            incident = {
                "class_id": class_id,
                "incident_type": incident_type,
                "description": description,
                "severity": severity,
                "affected_students": affected_students,
                "actions_taken": actions_taken,
                "date": datetime.now().isoformat(),
                "status": "open"
            }
            
            # Add to incidents
            if class_id not in self.incidents:
                self.incidents[class_id] = []
            self.incidents[class_id].append(incident)
            
            # Update student records
            await self.update_student_safety_records(affected_students, incident)
            
            return incident
            
        except Exception as e:
            self.logger.error(f"Error recording incident: {str(e)}")
            raise

    def validate_incident_parameters(self,
                                   class_id: str,
                                   incident_type: str,
                                   severity: str,
                                   affected_students: List[str]):
        """Validate incident parameters."""
        try:
            # Validate class ID
            if class_id not in self.student_manager.classes:
                raise ValueError(f"Class {class_id} does not exist")
            
            # Validate incident type
            if incident_type not in self.emergency_procedures:
                raise ValueError(f"Invalid incident type: {incident_type}")
            
            # Validate severity
            if severity not in ["low", "medium", "high"]:
                raise ValueError("Severity must be 'low', 'medium', or 'high'")
            
            # Validate affected students
            for student_id in affected_students:
                if student_id not in self.student_manager.students:
                    raise ValueError(f"Student {student_id} does not exist")
                if student_id not in self.student_manager.classes[class_id]["students"]:
                    raise ValueError(f"Student {student_id} is not enrolled in class {class_id}")
            
        except Exception as e:
            self.logger.error(f"Error validating incident parameters: {str(e)}")
            raise

    async def update_student_safety_records(self,
                                          affected_students: List[str],
                                          incident: Dict[str, Any]):
        """Update student safety records after an incident."""
        try:
            for student_id in affected_students:
                if "safety_incidents" not in self.student_manager.students[student_id]:
                    self.student_manager.students[student_id]["safety_incidents"] = []
                
                self.student_manager.students[student_id]["safety_incidents"].append(incident)
                
                # Update risk assessment if necessary
                if incident["severity"] == "high":
                    await self.conduct_risk_assessment(
                        incident["class_id"],
                        "main_activity",  # Default to main activity
                        "indoor"  # Default to indoor
                    )
            
        except Exception as e:
            self.logger.error(f"Error updating student safety records: {str(e)}")
            raise

    @track_metrics
    async def conduct_safety_check(self,
                                 class_id: str,
                                 check_type: str) -> Dict[str, Any]:
        """Conduct a safety check for a class."""
        try:
            # Validate parameters
            if class_id not in self.student_manager.classes:
                raise ValueError(f"Class {class_id} does not exist")
            if check_type not in ["pre-class", "during-class", "post-class"]:
                raise ValueError("Invalid check type")
            
            # Get class information
            class_info = self.student_manager.classes[class_id]
            
            # Conduct check based on type
            if check_type == "pre-class":
                check_results = self.conduct_pre_class_check(class_info)
            elif check_type == "during-class":
                check_results = self.conduct_during_class_check(class_info)
            else:
                check_results = self.conduct_post_class_check(class_info)
            
            # Create check record
            check_record = {
                "class_id": class_id,
                "check_type": check_type,
                "date": datetime.now().isoformat(),
                "results": check_results,
                "status": "passed" if all(check_results.values()) else "failed"
            }
            
            # Add to safety checks
            if class_id not in self.safety_checks:
                self.safety_checks[class_id] = []
            self.safety_checks[class_id].append(check_record)
            
            return check_record
            
        except Exception as e:
            self.logger.error(f"Error conducting safety check: {str(e)}")
            raise

    def conduct_pre_class_check(self, class_info: Dict[str, Any]) -> Dict[str, bool]:
        """Conduct pre-class safety check."""
        try:
            results = {
                "supervision": self.check_supervision(class_info),
                "equipment": self.check_equipment(class_info),
                "environment": self.check_environment(class_info),
                "emergency_procedures": self.check_emergency_procedures(class_info)
            }
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error conducting pre-class check: {str(e)}")
            return {}

    def conduct_during_class_check(self, class_info: Dict[str, Any]) -> Dict[str, bool]:
        """Conduct during-class safety check."""
        try:
            results = {
                "student_conditions": self.check_student_conditions(class_info),
                "activity_safety": self.check_activity_safety(class_info),
                "environment": self.check_environment(class_info)
            }
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error conducting during-class check: {str(e)}")
            return {}

    def conduct_post_class_check(self, class_info: Dict[str, Any]) -> Dict[str, bool]:
        """Conduct post-class safety check."""
        try:
            results = {
                "equipment": self.check_equipment(class_info),
                "environment": self.check_environment(class_info),
                "incident_reporting": self.check_incident_reporting(class_info)
            }
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error conducting post-class check: {str(e)}")
            return {}

    def check_supervision(self, class_info: Dict[str, Any]) -> bool:
        """Check supervision requirements."""
        try:
            # Calculate supervision ratio
            ratio = 1 / class_info["current_size"]
            
            # Check against minimum ratio
            return ratio >= self.safety_protocols["general"]["supervision"]["min_ratio"]
            
        except Exception as e:
            self.logger.error(f"Error checking supervision: {str(e)}")
            return False

    def check_equipment(self, class_info: Dict[str, Any]) -> bool:
        """Check equipment safety."""
        try:
            # Get equipment list for the class
            equipment_list = class_info.get("equipment", [])
            
            # Check each piece of equipment
            for equipment in equipment_list:
                # Check maintenance status
                if not self.check_equipment_maintenance(equipment):
                    return False
                
                # Check for damage
                if self.check_equipment_damage(equipment):
                    return False
                
                # Check age
                if not self.check_equipment_age(equipment):
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking equipment: {str(e)}")
            return False

    def check_equipment_maintenance(self, equipment: Dict[str, Any]) -> bool:
        """Check equipment maintenance status."""
        try:
            last_maintenance = equipment.get("last_maintenance")
            if not last_maintenance:
                return False
            
            maintenance_frequency = self.safety_protocols["general"]["equipment"]["inspection_frequency"]
            days_since_maintenance = (datetime.now() - datetime.fromisoformat(last_maintenance)).days
            
            return days_since_maintenance <= maintenance_frequency
            
        except Exception as e:
            self.logger.error(f"Error checking equipment maintenance: {str(e)}")
            return False

    def check_equipment_damage(self, equipment: Dict[str, Any]) -> bool:
        """Check for equipment damage."""
        try:
            return equipment.get("is_damaged", False)
        except Exception as e:
            self.logger.error(f"Error checking equipment damage: {str(e)}")
            return True

    def check_equipment_age(self, equipment: Dict[str, Any]) -> bool:
        """Check equipment age."""
        try:
            purchase_date = equipment.get("purchase_date")
            if not purchase_date:
                return False
            
            max_age = equipment.get("max_age_years", 5)
            age_years = (datetime.now() - datetime.fromisoformat(purchase_date)).days / 365
            
            return age_years <= max_age
            
        except Exception as e:
            self.logger.error(f"Error checking equipment age: {str(e)}")
            return False

    def check_environment(self, class_info: Dict[str, Any]) -> bool:
        """Check environment safety."""
        try:
            # Check space requirements
            if not self.check_space_requirements(class_info):
                return False
            
            # Check surface conditions
            if not self.check_surface_conditions(class_info):
                return False
            
            # Check emergency exits
            if not self.check_emergency_exits(class_info):
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking environment: {str(e)}")
            return False

    def check_space_requirements(self, class_info: Dict[str, Any]) -> bool:
        """Check space requirements."""
        try:
            environment = class_info.get("environment", "indoor")
            space_per_student = self.safety_protocols["general"]["environment"]["space_requirements"][environment]
            total_space = class_info.get("total_space", 0)
            required_space = class_info["current_size"] * space_per_student
            
            return total_space >= required_space
            
        except Exception as e:
            self.logger.error(f"Error checking space requirements: {str(e)}")
            return False

    def check_surface_conditions(self, class_info: Dict[str, Any]) -> bool:
        """Check surface conditions."""
        try:
            surface_conditions = class_info.get("surface_conditions", {})
            
            # Check each requirement
            for requirement in self.safety_protocols["general"]["environment"]["surface_requirements"]:
                if not surface_conditions.get(requirement.lower().replace(" ", "_"), False):
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking surface conditions: {str(e)}")
            return False

    def check_emergency_exits(self, class_info: Dict[str, Any]) -> bool:
        """Check emergency exits."""
        try:
            exits = class_info.get("emergency_exits", [])
            return len(exits) >= 2 and all(exit["is_clear"] for exit in exits)
        except Exception as e:
            self.logger.error(f"Error checking emergency exits: {str(e)}")
            return False

    def check_emergency_procedures(self, class_info: Dict[str, Any]) -> bool:
        """Check emergency procedures."""
        try:
            # Check emergency equipment
            if not self.check_emergency_equipment(class_info):
                return False
            
            # Check emergency contacts
            if not self.check_emergency_contacts(class_info):
                return False
            
            # Check evacuation plan
            if not self.check_evacuation_plan(class_info):
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking emergency procedures: {str(e)}")
            return False

    def check_emergency_equipment(self, class_info: Dict[str, Any]) -> bool:
        """Check emergency equipment."""
        try:
            equipment = class_info.get("emergency_equipment", {})
            
            # Check for required equipment
            for procedure in self.emergency_procedures.values():
                for required_item in procedure["required_equipment"]:
                    if not equipment.get(required_item, False):
                        return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking emergency equipment: {str(e)}")
            return False

    def check_emergency_contacts(self, class_info: Dict[str, Any]) -> bool:
        """Check emergency contacts."""
        try:
            contacts = class_info.get("emergency_contacts", {})
            return all(contacts.get(contact_type) for contact_type in ["police", "ambulance", "fire"])
        except Exception as e:
            self.logger.error(f"Error checking emergency contacts: {str(e)}")
            return False

    def check_evacuation_plan(self, class_info: Dict[str, Any]) -> bool:
        """Check evacuation plan."""
        try:
            plan = class_info.get("evacuation_plan", {})
            return all([
                plan.get("assembly_point"),
                plan.get("primary_route"),
                plan.get("secondary_route"),
                plan.get("emergency_meeting_point")
            ])
        except Exception as e:
            self.logger.error(f"Error checking evacuation plan: {str(e)}")
            return False

    def check_student_conditions(self, class_info: Dict[str, Any]) -> bool:
        """Check student conditions."""
        try:
            students = [
                self.student_manager.students[student_id]
                for student_id in class_info["students"]
            ]
            
            # Check each student's condition
            for student in students:
                if not self.check_individual_student_condition(student):
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking student conditions: {str(e)}")
            return False

    def check_individual_student_condition(self, student: Dict[str, Any]) -> bool:
        """Check individual student condition."""
        try:
            # Check medical conditions
            if student.get("medical_conditions"):
                if not student.get("medical_clearance"):
                    return False
            
            # Check hydration
            if not student.get("is_hydrated", True):
                return False
            
            # Check fatigue
            if student.get("fatigue_level", 0) > 0.7:  # 70% fatigue threshold
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking individual student condition: {str(e)}")
            return False

    def check_activity_safety(self, class_info: Dict[str, Any]) -> bool:
        """Check activity safety."""
        try:
            current_activity = class_info.get("current_activity")
            if not current_activity:
                return True
            
            # Check activity requirements
            activity_requirements = self.safety_protocols["activities"].get(current_activity, {})
            if not activity_requirements:
                return True
            
            # Check duration
            if "duration" in activity_requirements:
                current_duration = class_info.get("activity_duration", 0)
                if current_duration > activity_requirements["duration"]:
                    return False
            
            # Check requirements
            if "requirements" in activity_requirements:
                for requirement in activity_requirements["requirements"]:
                    if not class_info.get(f"requirement_{requirement.lower().replace(' ', '_')}", False):
                        return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking activity safety: {str(e)}")
            return False

    def check_incident_reporting(self, class_info: Dict[str, Any]) -> bool:
        """Check incident reporting."""
        try:
            # Check if all incidents are reported
            incidents = self.incidents.get(class_info["class_id"], [])
            for incident in incidents:
                if incident["status"] == "open" and not incident.get("reported"):
                    return False
            
            # Check if all required documentation is present
            for incident in incidents:
                if not all(key in incident for key in ["description", "actions_taken", "severity"]):
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking incident reporting: {str(e)}")
            return False

    async def save_safety_data(self, data: Dict[str, Any]) -> bool:
        """Save safety data to the database."""
        try:
            db = next(get_db())
            
            # Save incident if present
            if "incident" in data:
                incident = SafetyIncident(
                    class_id=data["class_id"],
                    incident_type=data["incident"]["type"],
                    description=data["incident"]["description"],
                    severity=data["incident"]["severity"],
                    affected_students=data["incident"]["affected_students"],
                    actions_taken=data["incident"]["actions_taken"],
                    status=data["incident"].get("status", "open"),
                    reported=data["incident"].get("reported", False),
                    metadata=data["incident"].get("metadata", {})
                )
                db.add(incident)
            
            # Save risk assessment if present
            if "risk_assessment" in data:
                assessment = RiskAssessment(
                    class_id=data["class_id"],
                    activity_type=data["risk_assessment"]["activity_type"],
                    environment=data["risk_assessment"]["environment"],
                    risk_level=data["risk_assessment"]["risk_level"],
                    environmental_risks=data["risk_assessment"]["environmental_risks"],
                    student_risks=data["risk_assessment"]["student_risks"],
                    activity_risks=data["risk_assessment"]["activity_risks"],
                    mitigation_strategies=data["risk_assessment"]["mitigation_strategies"],
                    metadata=data["risk_assessment"].get("metadata", {})
                )
                db.add(assessment)
            
            # Save safety checks if present
            if "safety_checks" in data:
                for check in data["safety_checks"]:
                    safety_check = SafetyCheck(
                        class_id=data["class_id"],
                        check_type=check["type"],
                        results=check["results"],
                        status=check["status"],
                        metadata=check.get("metadata", {})
                    )
                    db.add(safety_check)
            
            # Save equipment checks if present
            if "equipment_checks" in data:
                for check in data["equipment_checks"]:
                    equipment_check = EquipmentCheck(
                        class_id=data["class_id"],
                        equipment_id=check["equipment_id"],
                        maintenance_status=check["maintenance_status"],
                        damage_status=check["damage_status"],
                        age_status=check["age_status"],
                        last_maintenance=check.get("last_maintenance"),
                        purchase_date=check.get("purchase_date"),
                        max_age_years=check.get("max_age_years"),
                        metadata=check.get("metadata", {})
                    )
                    db.add(equipment_check)
            
            # Save environmental checks if present
            if "environmental_checks" in data:
                for check in data["environmental_checks"]:
                    environmental_check = EnvironmentalCheck(
                        class_id=data["class_id"],
                        temperature=check.get("temperature"),
                        humidity=check.get("humidity"),
                        air_quality=check.get("air_quality"),
                        surface_conditions=check.get("surface_conditions", {}),
                        lighting=check.get("lighting"),
                        equipment_condition=check.get("equipment_condition", {}),
                        metadata=check.get("metadata", {})
                    )
                    db.add(environmental_check)
            
            db.commit()
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving safety data: {str(e)}")
            if db:
                db.rollback()
            return False
        finally:
            if db:
                db.close()

    def validate_safety_data(self, data: Dict[str, Any]) -> tuple[bool, str]:
        """Validate safety data before saving."""
        try:
            # Validate class_id
            if "class_id" not in data:
                return False, "Missing required field: class_id"
            
            # Validate incident data if present
            if "incident" in data:
                incident = data["incident"]
                required_fields = ["type", "description", "severity", "affected_students", "actions_taken"]
                for field in required_fields:
                    if field not in incident:
                        return False, f"Missing required field in incident: {field}"
                
                if not isinstance(incident["affected_students"], list):
                    return False, "affected_students must be a list"
                
                if incident["severity"] not in ["low", "medium", "high", "critical"]:
                    return False, "Invalid severity level"
            
            # Validate risk assessment if present
            if "risk_assessment" in data:
                assessment = data["risk_assessment"]
                required_fields = ["activity_type", "environment", "risk_level", 
                                 "environmental_risks", "student_risks", "activity_risks"]
                for field in required_fields:
                    if field not in assessment:
                        return False, f"Missing required field in risk assessment: {field}"
                
                if assessment["risk_level"] not in ["low", "medium", "high"]:
                    return False, "Invalid risk level"
            
            # Validate safety checks if present
            if "safety_checks" in data:
                for check in data["safety_checks"]:
                    required_fields = ["type", "results", "status"]
                    for field in required_fields:
                        if field not in check:
                            return False, f"Missing required field in safety check: {field}"
            
            # Validate equipment checks if present
            if "equipment_checks" in data:
                for check in data["equipment_checks"]:
                    required_fields = ["equipment_id", "maintenance_status", "damage_status", "age_status"]
                    for field in required_fields:
                        if field not in check:
                            return False, f"Missing required field in equipment check: {field}"
            
            return True, "Validation successful"
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"

    async def get_safety_incidents(
        self, 
        class_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        severity: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve safety incidents with optional filters."""
        try:
            db = next(get_db())
            query = db.query(SafetyIncident)
            
            if class_id:
                query = query.filter(SafetyIncident.class_id == class_id)
            if start_date:
                query = query.filter(SafetyIncident.date >= start_date)
            if end_date:
                query = query.filter(SafetyIncident.date <= end_date)
            if severity:
                query = query.filter(SafetyIncident.severity == severity)
            
            incidents = query.all()
            return [incident.to_dict() for incident in incidents]
            
        except Exception as e:
            self.logger.error(f"Error retrieving safety incidents: {str(e)}")
            return []
        finally:
            if db:
                db.close()

    async def get_risk_assessments(
        self,
        class_id: Optional[str] = None,
        activity_type: Optional[str] = None,
        risk_level: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve risk assessments with optional filters."""
        try:
            db = next(get_db())
            query = db.query(RiskAssessment)
            
            if class_id:
                query = query.filter(RiskAssessment.class_id == class_id)
            if activity_type:
                query = query.filter(RiskAssessment.activity_type == activity_type)
            if risk_level:
                query = query.filter(RiskAssessment.risk_level == risk_level)
            
            assessments = query.all()
            return [assessment.to_dict() for assessment in assessments]
            
        except Exception as e:
            self.logger.error(f"Error retrieving risk assessments: {str(e)}")
            return []
        finally:
            if db:
                db.close()

    async def get_safety_checks(
        self,
        class_id: Optional[str] = None,
        check_type: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve safety checks with optional filters."""
        try:
            db = next(get_db())
            query = db.query(SafetyCheck)
            
            if class_id:
                query = query.filter(SafetyCheck.class_id == class_id)
            if check_type:
                query = query.filter(SafetyCheck.check_type == check_type)
            if status:
                query = query.filter(SafetyCheck.status == status)
            
            checks = query.all()
            return [check.to_dict() for check in checks]
            
        except Exception as e:
            self.logger.error(f"Error retrieving safety checks: {str(e)}")
            return []
        finally:
            if db:
                db.close()

    async def update_safety_incident(
        self,
        incident_id: int,
        update_data: Dict[str, Any]
    ) -> bool:
        """Update an existing safety incident."""
        try:
            db = next(get_db())
            incident = db.query(SafetyIncident).filter(SafetyIncident.id == incident_id).first()
            
            if not incident:
                self.logger.error(f"Incident not found: {incident_id}")
                return False
            
            for key, value in update_data.items():
                if hasattr(incident, key):
                    setattr(incident, key, value)
            
            db.commit()
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating safety incident: {str(e)}")
            if db:
                db.rollback()
            return False
        finally:
            if db:
                db.close()

    async def update_risk_assessment(
        self,
        assessment_id: int,
        update_data: Dict[str, Any]
    ) -> bool:
        """Update an existing risk assessment."""
        try:
            db = next(get_db())
            assessment = db.query(RiskAssessment).filter(RiskAssessment.id == assessment_id).first()
            
            if not assessment:
                self.logger.error(f"Risk assessment not found: {assessment_id}")
                return False
            
            for key, value in update_data.items():
                if hasattr(assessment, key):
                    setattr(assessment, key, value)
            
            db.commit()
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating risk assessment: {str(e)}")
            if db:
                db.rollback()
            return False
        finally:
            if db:
                db.close()

    async def update_safety_check(
        self,
        check_id: int,
        update_data: Dict[str, Any]
    ) -> bool:
        """Update an existing safety check."""
        try:
            db = next(get_db())
            check = db.query(SafetyCheck).filter(SafetyCheck.id == check_id).first()
            
            if not check:
                self.logger.error(f"Safety check not found: {check_id}")
                return False
            
            for key, value in update_data.items():
                if hasattr(check, key):
                    setattr(check, key, value)
            
            db.commit()
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating safety check: {str(e)}")
            if db:
                db.rollback()
            return False
        finally:
            if db:
                db.close()

    async def get_equipment_checks(
        self,
        class_id: Optional[str] = None,
        equipment_id: Optional[str] = None,
        maintenance_status: Optional[str] = None,
        damage_status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve equipment checks with optional filters."""
        try:
            db = next(get_db())
            query = db.query(EquipmentCheck)
            
            if class_id:
                query = query.filter(EquipmentCheck.class_id == class_id)
            if equipment_id:
                query = query.filter(EquipmentCheck.equipment_id == equipment_id)
            if maintenance_status:
                query = query.filter(EquipmentCheck.maintenance_status == maintenance_status)
            if damage_status:
                query = query.filter(EquipmentCheck.damage_status == damage_status)
            
            checks = query.all()
            return [check.to_dict() for check in checks]
            
        except Exception as e:
            self.logger.error(f"Error retrieving equipment checks: {str(e)}")
            return []
        finally:
            if db:
                db.close()

    async def get_environmental_checks(
        self,
        class_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve environmental checks with optional filters."""
        try:
            db = next(get_db())
            query = db.query(EnvironmentalCheck)
            
            if class_id:
                query = query.filter(EnvironmentalCheck.class_id == class_id)
            if start_date:
                query = query.filter(EnvironmentalCheck.check_date >= start_date)
            if end_date:
                query = query.filter(EnvironmentalCheck.check_date <= end_date)
            
            checks = query.all()
            return [check.to_dict() for check in checks]
            
        except Exception as e:
            self.logger.error(f"Error retrieving environmental checks: {str(e)}")
            return []
        finally:
            if db:
                db.close()

    async def bulk_update_safety_incidents(
        self,
        updates: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """Bulk update multiple safety incidents."""
        try:
            db = next(get_db())
            success_count = 0
            failure_count = 0
            
            for update in updates:
                incident_id = update.get("id")
                update_data = update.get("data", {})
                
                if not incident_id or not update_data:
                    failure_count += 1
                    continue
                
                incident = db.query(SafetyIncident).filter(SafetyIncident.id == incident_id).first()
                
                if not incident:
                    failure_count += 1
                    continue
                
                for key, value in update_data.items():
                    if hasattr(incident, key):
                        setattr(incident, key, value)
                
                success_count += 1
            
            db.commit()
            return {"success": success_count, "failure": failure_count}
            
        except Exception as e:
            self.logger.error(f"Error in bulk update of safety incidents: {str(e)}")
            if db:
                db.rollback()
            return {"success": 0, "failure": len(updates)}
        finally:
            if db:
                db.close()

    async def bulk_update_risk_assessments(
        self,
        updates: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """Bulk update multiple risk assessments."""
        try:
            db = next(get_db())
            success_count = 0
            failure_count = 0
            
            for update in updates:
                assessment_id = update.get("id")
                update_data = update.get("data", {})
                
                if not assessment_id or not update_data:
                    failure_count += 1
                    continue
                
                assessment = db.query(RiskAssessment).filter(RiskAssessment.id == assessment_id).first()
                
                if not assessment:
                    failure_count += 1
                    continue
                
                for key, value in update_data.items():
                    if hasattr(assessment, key):
                        setattr(assessment, key, value)
                
                success_count += 1
            
            db.commit()
            return {"success": success_count, "failure": failure_count}
            
        except Exception as e:
            self.logger.error(f"Error in bulk update of risk assessments: {str(e)}")
            if db:
                db.rollback()
            return {"success": 0, "failure": len(updates)}
        finally:
            if db:
                db.close()

    async def delete_safety_incident(self, incident_id: int) -> bool:
        """Delete a safety incident."""
        try:
            db = next(get_db())
            incident = db.query(SafetyIncident).filter(SafetyIncident.id == incident_id).first()
            
            if not incident:
                self.logger.error(f"Incident not found: {incident_id}")
                return False
            
            db.delete(incident)
            db.commit()
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting safety incident: {str(e)}")
            if db:
                db.rollback()
            return False
        finally:
            if db:
                db.close()

    async def delete_risk_assessment(self, assessment_id: int) -> bool:
        """Delete a risk assessment."""
        try:
            db = next(get_db())
            assessment = db.query(RiskAssessment).filter(RiskAssessment.id == assessment_id).first()
            
            if not assessment:
                self.logger.error(f"Risk assessment not found: {assessment_id}")
                return False
            
            db.delete(assessment)
            db.commit()
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting risk assessment: {str(e)}")
            if db:
                db.rollback()
            return False
        finally:
            if db:
                db.close()

    async def delete_safety_check(self, check_id: int) -> bool:
        """Delete a safety check."""
        try:
            db = next(get_db())
            check = db.query(SafetyCheck).filter(SafetyCheck.id == check_id).first()
            
            if not check:
                self.logger.error(f"Safety check not found: {check_id}")
                return False
            
            db.delete(check)
            db.commit()
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting safety check: {str(e)}")
            if db:
                db.rollback()
            return False
        finally:
            if db:
                db.close()

    async def delete_equipment_check(self, check_id: int) -> bool:
        """Delete an equipment check."""
        try:
            db = next(get_db())
            check = db.query(EquipmentCheck).filter(EquipmentCheck.id == check_id).first()
            
            if not check:
                self.logger.error(f"Equipment check not found: {check_id}")
                return False
            
            db.delete(check)
            db.commit()
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting equipment check: {str(e)}")
            if db:
                db.rollback()
            return False
        finally:
            if db:
                db.close()

    async def delete_environmental_check(self, check_id: int) -> bool:
        """Delete an environmental check."""
        try:
            db = next(get_db())
            check = db.query(EnvironmentalCheck).filter(EnvironmentalCheck.id == check_id).first()
            
            if not check:
                self.logger.error(f"Environmental check not found: {check_id}")
                return False
            
            db.delete(check)
            db.commit()
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting environmental check: {str(e)}")
            if db:
                db.rollback()
            return False
        finally:
            if db:
                db.close()

    async def bulk_delete_safety_incidents(
        self,
        incident_ids: List[int]
    ) -> Dict[str, int]:
        """Bulk delete multiple safety incidents."""
        try:
            db = next(get_db())
            success_count = 0
            failure_count = 0
            
            for incident_id in incident_ids:
                incident = db.query(SafetyIncident).filter(SafetyIncident.id == incident_id).first()
                
                if not incident:
                    failure_count += 1
                    continue
                
                db.delete(incident)
                success_count += 1
            
            db.commit()
            return {"success": success_count, "failure": failure_count}
            
        except Exception as e:
            self.logger.error(f"Error in bulk deletion of safety incidents: {str(e)}")
            if db:
                db.rollback()
            return {"success": 0, "failure": len(incident_ids)}
        finally:
            if db:
                db.close()

    async def bulk_delete_risk_assessments(
        self,
        assessment_ids: List[int]
    ) -> Dict[str, int]:
        """Bulk delete multiple risk assessments."""
        try:
            db = next(get_db())
            success_count = 0
            failure_count = 0
            
            for assessment_id in assessment_ids:
                assessment = db.query(RiskAssessment).filter(RiskAssessment.id == assessment_id).first()
                
                if not assessment:
                    failure_count += 1
                    continue
                
                db.delete(assessment)
                success_count += 1
            
            db.commit()
            return {"success": success_count, "failure": failure_count}
            
        except Exception as e:
            self.logger.error(f"Error in bulk deletion of risk assessments: {str(e)}")
            if db:
                db.rollback()
            return {"success": 0, "failure": len(assessment_ids)}
        finally:
            if db:
                db.close()

    async def get_safety_statistics(
        self,
        class_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get aggregated safety statistics."""
        try:
            db = next(get_db())
            stats = {
                "incidents": {
                    "total": 0,
                    "by_severity": {},
                    "by_type": {},
                    "trend": []
                },
                "risk_assessments": {
                    "total": 0,
                    "by_level": {},
                    "by_activity": {},
                    "trend": []
                },
                "safety_checks": {
                    "total": 0,
                    "by_status": {},
                    "by_type": {},
                    "trend": []
                }
            }
            
            # Get base query
            query = db.query(SafetyIncident)
            if class_id:
                query = query.filter(SafetyIncident.class_id == class_id)
            if start_date:
                query = query.filter(SafetyIncident.date >= start_date)
            if end_date:
                query = query.filter(SafetyIncident.date <= end_date)
            
            # Calculate incident statistics
            incidents = query.all()
            stats["incidents"]["total"] = len(incidents)
            for incident in incidents:
                stats["incidents"]["by_severity"][incident.severity] = \
                    stats["incidents"]["by_severity"].get(incident.severity, 0) + 1
                stats["incidents"]["by_type"][incident.incident_type] = \
                    stats["incidents"]["by_type"].get(incident.incident_type, 0) + 1
            
            # Calculate risk assessment statistics
            query = db.query(RiskAssessment)
            if class_id:
                query = query.filter(RiskAssessment.class_id == class_id)
            if start_date:
                query = query.filter(RiskAssessment.date >= start_date)
            if end_date:
                query = query.filter(RiskAssessment.date <= end_date)
            
            assessments = query.all()
            stats["risk_assessments"]["total"] = len(assessments)
            for assessment in assessments:
                stats["risk_assessments"]["by_level"][assessment.risk_level] = \
                    stats["risk_assessments"]["by_level"].get(assessment.risk_level, 0) + 1
                stats["risk_assessments"]["by_activity"][assessment.activity_type] = \
                    stats["risk_assessments"]["by_activity"].get(assessment.activity_type, 0) + 1
            
            # Calculate safety check statistics
            query = db.query(SafetyCheck)
            if class_id:
                query = query.filter(SafetyCheck.class_id == class_id)
            if start_date:
                query = query.filter(SafetyCheck.date >= start_date)
            if end_date:
                query = query.filter(SafetyCheck.date <= end_date)
            
            checks = query.all()
            stats["safety_checks"]["total"] = len(checks)
            for check in checks:
                stats["safety_checks"]["by_status"][check.status] = \
                    stats["safety_checks"]["by_status"].get(check.status, 0) + 1
                stats["safety_checks"]["by_type"][check.check_type] = \
                    stats["safety_checks"]["by_type"].get(check.check_type, 0) + 1
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error calculating safety statistics: {str(e)}")
            return {}
        finally:
            if db:
                db.close()

    async def export_safety_data(
        self,
        format: str = "json",
        class_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Export safety data in specified format."""
        try:
            db = next(get_db())
            export_data = {
                "incidents": [],
                "risk_assessments": [],
                "safety_checks": [],
                "equipment_checks": [],
                "environmental_checks": []
            }
            
            # Export incidents
            query = db.query(SafetyIncident)
            if class_id:
                query = query.filter(SafetyIncident.class_id == class_id)
            if start_date:
                query = query.filter(SafetyIncident.date >= start_date)
            if end_date:
                query = query.filter(SafetyIncident.date <= end_date)
            export_data["incidents"] = [incident.to_dict() for incident in query.all()]
            
            # Export risk assessments
            query = db.query(RiskAssessment)
            if class_id:
                query = query.filter(RiskAssessment.class_id == class_id)
            if start_date:
                query = query.filter(RiskAssessment.date >= start_date)
            if end_date:
                query = query.filter(RiskAssessment.date <= end_date)
            export_data["risk_assessments"] = [assessment.to_dict() for assessment in query.all()]
            
            # Export safety checks
            query = db.query(SafetyCheck)
            if class_id:
                query = query.filter(SafetyCheck.class_id == class_id)
            if start_date:
                query = query.filter(SafetyCheck.date >= start_date)
            if end_date:
                query = query.filter(SafetyCheck.date <= end_date)
            export_data["safety_checks"] = [check.to_dict() for check in query.all()]
            
            # Export equipment checks
            query = db.query(EquipmentCheck)
            if class_id:
                query = query.filter(EquipmentCheck.class_id == class_id)
            if start_date:
                query = query.filter(EquipmentCheck.check_date >= start_date)
            if end_date:
                query = query.filter(EquipmentCheck.check_date <= end_date)
            export_data["equipment_checks"] = [check.to_dict() for check in query.all()]
            
            # Export environmental checks
            query = db.query(EnvironmentalCheck)
            if class_id:
                query = query.filter(EnvironmentalCheck.class_id == class_id)
            if start_date:
                query = query.filter(EnvironmentalCheck.check_date >= start_date)
            if end_date:
                query = query.filter(EnvironmentalCheck.check_date <= end_date)
            export_data["environmental_checks"] = [check.to_dict() for check in query.all()]
            
            if format.lower() == "csv":
                return self._convert_to_csv(export_data)
            elif format.lower() == "excel":
                return self._convert_to_excel(export_data)
            else:
                return export_data
            
        except Exception as e:
            self.logger.error(f"Error exporting safety data: {str(e)}")
            return {}
        finally:
            if db:
                db.close()

    def _convert_to_csv(self, data: Dict[str, Any]) -> Dict[str, str]:
        """Convert data to CSV format."""
        try:
            csv_data = {}
            for key, items in data.items():
                if not items:
                    csv_data[key] = ""
                    continue
                
                headers = list(items[0].keys())
                rows = [headers]
                for item in items:
                    rows.append([str(item.get(header, "")) for header in headers])
                
                csv_data[key] = "\n".join([",".join(row) for row in rows])
            
            return csv_data
            
        except Exception as e:
            self.logger.error(f"Error converting to CSV: {str(e)}")
            return {}

    def _convert_to_excel(self, data: Dict[str, Any]) -> Dict[str, bytes]:
        """Convert data to Excel format."""
        try:
            import pandas as pd
            from io import BytesIO
            
            excel_data = {}
            for key, items in data.items():
                if not items:
                    excel_data[key] = b""
                    continue
                
                df = pd.DataFrame(items)
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name=key, index=False)
                excel_data[key] = output.getvalue()
            
            return excel_data
            
        except Exception as e:
            self.logger.error(f"Error converting to Excel: {str(e)}")
            return {}

    async def get_advanced_statistics(
        self,
        class_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get advanced safety statistics and analysis."""
        try:
            db = next(get_db())
            stats = {
                "incident_analysis": {
                    "severity_trends": {},
                    "type_correlation": {},
                    "time_patterns": {},
                    "risk_factors": {}
                },
                "risk_analysis": {
                    "activity_risk_profiles": {},
                    "environmental_impact": {},
                    "mitigation_effectiveness": {},
                    "risk_trends": {}
                },
                "equipment_analysis": {
                    "maintenance_patterns": {},
                    "failure_rates": {},
                    "replacement_needs": {},
                    "cost_analysis": {}
                }
            }
            
            # Analyze incident patterns
            query = db.query(SafetyIncident)
            if class_id:
                query = query.filter(SafetyIncident.class_id == class_id)
            if start_date:
                query = query.filter(SafetyIncident.date >= start_date)
            if end_date:
                query = query.filter(SafetyIncident.date <= end_date)
            
            incidents = query.all()
            for incident in incidents:
                # Calculate severity trends
                date_key = incident.date.strftime("%Y-%m")
                stats["incident_analysis"]["severity_trends"][date_key] = \
                    stats["incident_analysis"]["severity_trends"].get(date_key, {})
                stats["incident_analysis"]["severity_trends"][date_key][incident.severity] = \
                    stats["incident_analysis"]["severity_trends"][date_key].get(incident.severity, 0) + 1
                
                # Calculate type correlations
                stats["incident_analysis"]["type_correlation"][incident.incident_type] = \
                    stats["incident_analysis"]["type_correlation"].get(incident.incident_type, {})
                for other_incident in incidents:
                    if other_incident.id != incident.id:
                        stats["incident_analysis"]["type_correlation"][incident.incident_type][other_incident.incident_type] = \
                            stats["incident_analysis"]["type_correlation"][incident.incident_type].get(other_incident.incident_type, 0) + 1
            
            # Analyze risk patterns
            query = db.query(RiskAssessment)
            if class_id:
                query = query.filter(RiskAssessment.class_id == class_id)
            if start_date:
                query = query.filter(RiskAssessment.date >= start_date)
            if end_date:
                query = query.filter(RiskAssessment.date <= end_date)
            
            assessments = query.all()
            for assessment in assessments:
                # Calculate activity risk profiles
                stats["risk_analysis"]["activity_risk_profiles"][assessment.activity_type] = \
                    stats["risk_analysis"]["activity_risk_profiles"].get(assessment.activity_type, {})
                stats["risk_analysis"]["activity_risk_profiles"][assessment.activity_type][assessment.risk_level] = \
                    stats["risk_analysis"]["activity_risk_profiles"][assessment.activity_type].get(assessment.risk_level, 0) + 1
                
                # Calculate environmental impact
                for risk in assessment.environmental_risks:
                    stats["risk_analysis"]["environmental_impact"][risk] = \
                        stats["risk_analysis"]["environmental_impact"].get(risk, 0) + 1
            
            # Analyze equipment patterns
            query = db.query(EquipmentCheck)
            if class_id:
                query = query.filter(EquipmentCheck.class_id == class_id)
            if start_date:
                query = query.filter(EquipmentCheck.check_date >= start_date)
            if end_date:
                query = query.filter(EquipmentCheck.check_date <= end_date)
            
            equipment_checks = query.all()
            for check in equipment_checks:
                # Calculate maintenance patterns
                stats["equipment_analysis"]["maintenance_patterns"][check.equipment_id] = \
                    stats["equipment_analysis"]["maintenance_patterns"].get(check.equipment_id, {})
                stats["equipment_analysis"]["maintenance_patterns"][check.equipment_id][check.maintenance_status] = \
                    stats["equipment_analysis"]["maintenance_patterns"][check.equipment_id].get(check.maintenance_status, 0) + 1
                
                # Calculate failure rates
                if check.damage_status == "needs_repair":
                    stats["equipment_analysis"]["failure_rates"][check.equipment_id] = \
                        stats["equipment_analysis"]["failure_rates"].get(check.equipment_id, 0) + 1
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error calculating advanced statistics: {str(e)}")
            return {}
        finally:
            if db:
                db.close()

    async def generate_safety_report(
        self,
        class_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        format: str = "pdf"
    ) -> Dict[str, Any]:
        """Generate a comprehensive safety report with visualizations."""
        try:
            import matplotlib.pyplot as plt
            from io import BytesIO
            import base64
            
            # Get statistics
            stats = await self.get_safety_statistics(class_id, start_date, end_date)
            advanced_stats = await self.get_advanced_statistics(class_id, start_date, end_date)
            
            # Generate visualizations
            visualizations = {}
            
            # Incident severity pie chart
            plt.figure(figsize=(10, 6))
            plt.pie(
                list(stats["incidents"]["by_severity"].values()),
                labels=list(stats["incidents"]["by_severity"].keys()),
                autopct='%1.1f%%'
            )
            plt.title("Incident Severity Distribution")
            buf = BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            visualizations["incident_severity"] = base64.b64encode(buf.getvalue()).decode('utf-8')
            plt.close()
            
            # Risk level bar chart
            plt.figure(figsize=(10, 6))
            plt.bar(
                list(stats["risk_assessments"]["by_level"].keys()),
                list(stats["risk_assessments"]["by_level"].values())
            )
            plt.title("Risk Level Distribution")
            buf = BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            visualizations["risk_levels"] = base64.b64encode(buf.getvalue()).decode('utf-8')
            plt.close()
            
            # Equipment maintenance status
            plt.figure(figsize=(10, 6))
            equipment_data = {}
            for check in advanced_stats["equipment_analysis"]["maintenance_patterns"].values():
                for status, count in check.items():
                    equipment_data[status] = equipment_data.get(status, 0) + count
            plt.pie(
                list(equipment_data.values()),
                labels=list(equipment_data.keys()),
                autopct='%1.1f%%'
            )
            plt.title("Equipment Maintenance Status")
            buf = BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            visualizations["equipment_maintenance"] = base64.b64encode(buf.getvalue()).decode('utf-8')
            plt.close()
            
            # Prepare report data
            report_data = {
                "statistics": stats,
                "advanced_statistics": advanced_stats,
                "visualizations": visualizations,
                "recommendations": self._generate_recommendations(stats, advanced_stats)
            }
            
            if format.lower() == "pdf":
                return self._convert_to_pdf(report_data)
            else:
                return report_data
            
        except Exception as e:
            self.logger.error(f"Error generating safety report: {str(e)}")
            return {}
        finally:
            plt.close('all')

    def _generate_recommendations(
        self,
        stats: Dict[str, Any],
        advanced_stats: Dict[str, Any]
    ) -> List[str]:
        """Generate safety recommendations based on statistics."""
        recommendations = []
        
        # Analyze incident patterns
        if stats["incidents"]["total"] > 0:
            most_common_severity = max(
                stats["incidents"]["by_severity"].items(),
                key=lambda x: x[1]
            )[0]
            if most_common_severity in ["high", "critical"]:
                recommendations.append(
                    f"High severity incidents are most common. Review and strengthen safety protocols."
                )
        
        # Analyze risk assessment patterns
        if stats["risk_assessments"]["total"] > 0:
            most_common_risk = max(
                stats["risk_assessments"]["by_level"].items(),
                key=lambda x: x[1]
            )[0]
            if most_common_risk == "high":
                recommendations.append(
                    "High risk activities are frequent. Consider additional safety measures or alternative activities."
                )
        
        # Analyze equipment patterns
        if advanced_stats["equipment_analysis"]["failure_rates"]:
            high_failure_equipment = [
                eq_id for eq_id, count in advanced_stats["equipment_analysis"]["failure_rates"].items()
                if count > 3
            ]
            if high_failure_equipment:
                recommendations.append(
                    f"Equipment with high failure rates: {', '.join(high_failure_equipment)}. Consider replacement."
                )
        
        return recommendations

    def _convert_to_pdf(self, report_data: Dict[str, Any]) -> bytes:
        """Convert report data to PDF format."""
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
            from reportlab.lib.styles import getSampleStyleSheet
            from io import BytesIO
            import base64
            
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []
            
            # Add title
            story.append(Paragraph("Safety Report", styles["Title"]))
            story.append(Spacer(1, 12))
            
            # Add statistics
            story.append(Paragraph("Statistics", styles["Heading1"]))
            for category, data in report_data["statistics"].items():
                story.append(Paragraph(category, styles["Normal"]))
                for key, value in data.items():
                    if isinstance(value, dict):
                        story.append(Paragraph(f"{key}:", styles["Normal"]))
                        for subkey, subvalue in value.items():
                            story.append(Paragraph(f"  {subkey}: {subvalue}", styles["Normal"]))
                    else:
                        story.append(Paragraph(f"{key}: {value}", styles["Normal"]))
                story.append(Spacer(1, 12))
            
            # Add visualizations
            story.append(Paragraph("Visualizations", styles["Heading1"]))
            for title, img_data in report_data["visualizations"].items():
                img = Image(BytesIO(base64.b64decode(img_data)))
                img.drawHeight = 200
                img.drawWidth = 400
                story.append(img)
                story.append(Spacer(1, 12))
            
            # Add recommendations
            story.append(Paragraph("Recommendations", styles["Heading1"]))
            for rec in report_data["recommendations"]:
                story.append(Paragraph(rec, styles["Normal"]))
                story.append(Spacer(1, 6))
            
            doc.build(story)
            return buffer.getvalue()
            
        except Exception as e:
            self.logger.error(f"Error converting to PDF: {str(e)}")
            return b""

    async def import_safety_data(
        self,
        data: Dict[str, Any],
        format: str = "json"
    ) -> Dict[str, int]:
        """Import safety data from external source."""
        try:
            db = next(get_db())
            success_count = 0
            failure_count = 0
            
            # Validate and process incidents
            if "incidents" in data:
                for incident_data in data["incidents"]:
                    try:
                        incident = SafetyIncident(**incident_data)
                        db.add(incident)
                        success_count += 1
                    except Exception as e:
                        self.logger.error(f"Error importing incident: {str(e)}")
                        failure_count += 1
            
            # Validate and process risk assessments
            if "risk_assessments" in data:
                for assessment_data in data["risk_assessments"]:
                    try:
                        assessment = RiskAssessment(**assessment_data)
                        db.add(assessment)
                        success_count += 1
                    except Exception as e:
                        self.logger.error(f"Error importing risk assessment: {str(e)}")
                        failure_count += 1
            
            # Validate and process safety checks
            if "safety_checks" in data:
                for check_data in data["safety_checks"]:
                    try:
                        check = SafetyCheck(**check_data)
                        db.add(check)
                        success_count += 1
                    except Exception as e:
                        self.logger.error(f"Error importing safety check: {str(e)}")
                        failure_count += 1
            
            # Validate and process equipment checks
            if "equipment_checks" in data:
                for check_data in data["equipment_checks"]:
                    try:
                        check = EquipmentCheck(**check_data)
                        db.add(check)
                        success_count += 1
                    except Exception as e:
                        self.logger.error(f"Error importing equipment check: {str(e)}")
                        failure_count += 1
            
            # Validate and process environmental checks
            if "environmental_checks" in data:
                for check_data in data["environmental_checks"]:
                    try:
                        check = EnvironmentalCheck(**check_data)
                        db.add(check)
                        success_count += 1
                    except Exception as e:
                        self.logger.error(f"Error importing environmental check: {str(e)}")
                        failure_count += 1
            
            db.commit()
            return {"success": success_count, "failure": failure_count}
            
        except Exception as e:
            self.logger.error(f"Error importing safety data: {str(e)}")
            if db:
                db.rollback()
            return {"success": 0, "failure": 0}
        finally:
            if db:
                db.close() 