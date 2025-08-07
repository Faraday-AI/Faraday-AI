import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
from app.core.monitoring import track_metrics
from app.services.physical_education import service_integration
from sqlalchemy.orm import Session
from app.core.database import get_db

class LessonPlanner:
    """Service for managing physical education lesson plans and curriculum."""
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(LessonPlanner, cls).__new__(cls)
        return cls._instance
    
    @classmethod
    def reset_instance(cls):
        """Reset the singleton instance for testing."""
        cls._instance = None
    
    def __init__(self):
        self.logger = logging.getLogger("lesson_planner")
        self.db = None
        self.assessment_system = None
        
        # Lesson planning settings
        self.settings = {
            "lesson_duration": 45,  # minutes
            "max_students_per_group": 6,
            "warmup_duration": 10,  # minutes
            "cooldown_duration": 5,  # minutes
            "equipment_requirements": {
                "minimal": ["cones", "whistle"],
                "basic": ["balls", "jump ropes", "mats"],
                "full": ["gymnastics equipment", "track equipment", "team sports equipment"]
            }
        }
        
        # Curriculum standards
        self.curriculum_standards = {
            "national": {
                "fitness": ["cardiovascular", "strength", "flexibility", "endurance"],
                "skills": ["locomotor", "non-locomotor", "manipulative"],
                "concepts": ["spatial awareness", "body awareness", "rhythm", "coordination"]
            },
            "state": {
                "grade_levels": ["K-2", "3-5", "6-8", "9-12"],
                "objectives": {
                    "K-2": ["basic movement", "coordination", "social skills"],
                    "3-5": ["skill development", "teamwork", "fitness basics"],
                    "6-8": ["advanced skills", "strategy", "fitness principles"],
                    "9-12": ["specialized skills", "lifetime fitness", "leadership"]
                }
            }
        }
        
        # Activity database
        self.activities = {
            "warmup": {
                "dynamic_stretching": {
                    "duration": 5,
                }
            }
        }
        
        # Lesson templates
        self.lesson_templates = {
            "fitness": {
                "warmup": "dynamic_stretching",
                "main_activity": "fitness_circuit",
                "cooldown": "static_stretching"
            },
            "skills": {
                "warmup": "dynamic_stretching",
                "main_activity": "individual_skills",
                "cooldown": "static_stretching"
            },
            "team_sports": {
                "warmup": "dynamic_stretching",
                "main_activity": "team_game",
                "cooldown": "static_stretching"
            }
        }
        
        # Template file path
        self.template_file = "lesson_templates.json"
    
    async def initialize(self):
        """Initialize the lesson planner."""
        try:
            self.db = next(get_db())
            
            # Only get assessment_system if not already set (for testing)
            if self.assessment_system is None:
                self.assessment_system = service_integration.get_service("assessment_system")
            elif hasattr(self.assessment_system, 'initialize'):
                await self.assessment_system.initialize()
            
            # Load required data
            self.load_lesson_templates()
            self.initialize_activity_database()
            
            self.logger.info("Lesson Planner initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing Lesson Planner: {str(e)}")
            raise
    
    async def cleanup(self):
        """Cleanup the lesson planner."""
        try:
            self.db = None
            self.assessment_system = None
            
            # Clear all data
            self.activities = {}
            self.settings = {}
            self.curriculum_standards = {}
            
            self.logger.info("Lesson Planner cleaned up successfully")
        except Exception as e:
            self.logger.error(f"Error cleaning up Lesson Planner: {str(e)}")
            raise

    def load_lesson_templates(self):
        """Load lesson plan templates."""
        try:
            import json
            with open(self.template_file, 'r') as f:
                self.lesson_templates = json.load(f)
            self.logger.info("Lesson templates loaded successfully")
        except FileNotFoundError:
            # Keep the default templates set in __init__
            self.logger.info("Lesson templates file not found, using defaults")
        except Exception as e:
            self.logger.error(f"Error loading lesson templates: {str(e)}")
            raise

    def initialize_activity_database(self):
        """Initialize the activity database."""
        try:
            # TODO: Load activities from persistent storage
            self.logger.info("Activity database initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing activity database: {str(e)}")
            raise

    @track_metrics("create_lesson_plan")
    async def create_lesson_plan(self, 
                               grade_level: str,
                               focus_area: str,
                               skill_level: str,
                               class_size: int,
                               available_equipment: List[str]) -> Dict[str, Any]:
        """Create a lesson plan based on specified parameters."""
        try:
            # Validate parameters
            self.validate_parameters(grade_level, focus_area, skill_level, class_size, available_equipment)
            
            # Select appropriate template
            template = self.select_template(focus_area)
            
            # Generate activities
            activities = await self.generate_activities(
                template,
                grade_level,
                skill_level,
                class_size,
                available_equipment
            )
            
            # Create lesson plan
            lesson_plan = {
                "grade_level": grade_level,
                "focus_area": focus_area,
                "skill_level": skill_level,
                "class_size": class_size,
                "duration": self.settings["lesson_duration"],
                "activities": activities,
                "equipment_needed": self.determine_equipment_needs(activities),
                "objectives": self.generate_objectives(grade_level, focus_area),
                "assessment_criteria": self.generate_assessment_criteria(focus_area),
                "safety_considerations": self.generate_safety_considerations(activities),
                "modifications": self.generate_activity_modifications(activities[0], grade_level, skill_level, class_size),
                "created_at": datetime.now().isoformat()
            }
            
            return lesson_plan
            
        except Exception as e:
            self.logger.error(f"Error creating lesson plan: {str(e)}")
            raise

    def validate_parameters(self, grade_level: str, focus_area: str, skill_level: str, class_size: int, available_equipment: List[str]):
        """Validate lesson plan parameters."""
        try:
            # Validate grade level
            if grade_level not in self.curriculum_standards["state"]["grade_levels"]:
                raise ValueError(f"Invalid grade level: {grade_level}")
            
            # Validate focus area - check against valid focus areas in select_template
            valid_focus_areas = ["fitness", "skills", "technique", "skill_development", "teamwork", "sports", "team_sports"]
            if focus_area not in valid_focus_areas:
                raise ValueError(f"Invalid focus area: {focus_area}")
            
            # Validate skill level
            if skill_level not in self.assessment_system.settings["skill_levels"]:
                raise ValueError(f"Invalid skill level: {skill_level}")
            
            # Validate class size
            if class_size < 1:
                raise ValueError("Class size must be positive")
            
            # Validate equipment
            if not all(equipment in self.settings["equipment_requirements"]["minimal"] for equipment in available_equipment):
                raise ValueError("Insufficient equipment available")
            
        except Exception as e:
            self.logger.error(f"Error validating parameters: {str(e)}")
            raise

    def select_template(self, focus_area: str) -> Dict[str, str]:
        """Select appropriate lesson template based on focus area."""
        try:
            # Validate focus area
            valid_focus_areas = ["fitness", "skills", "technique", "skill_development", "teamwork", "sports", "team_sports"]
            if focus_area not in valid_focus_areas:
                raise ValueError(f"Invalid focus area: {focus_area}")
            
            if focus_area in ["skills", "technique", "skill_development"]:
                return self.lesson_templates["skills"]
            elif focus_area in ["teamwork", "sports", "team_sports"]:
                return self.lesson_templates["team_sports"]
            else:
                return self.lesson_templates["fitness"]
        except Exception as e:
            self.logger.error(f"Error selecting template: {str(e)}")
            raise

    async def generate_activities(self,
                                template: Dict[str, str],
                                grade_level: str,
                                skill_level: str,
                                class_size: int,
                                available_equipment: List[str]) -> List[Dict[str, Any]]:
        """Generate activities for the lesson plan."""
        try:
            activities = []
            
            # Add warmup activity
            warmup = self.select_activity(
                "warmup",
                template["warmup"],
                grade_level,
                skill_level,
                class_size,
                available_equipment
            )
            activities.append(warmup)
            
            # Add main activity
            main_activity = self.select_activity(
                "main_activities",
                template["main_activity"],
                grade_level,
                skill_level,
                class_size,
                available_equipment
            )
            activities.append(main_activity)
            
            # Add cooldown activity
            cooldown = self.select_activity(
                "cooldown",
                template["cooldown"],
                grade_level,
                skill_level,
                class_size,
                available_equipment
            )
            activities.append(cooldown)
            
            return activities
            
        except Exception as e:
            self.logger.error(f"Error generating activities: {str(e)}")
            raise

    def select_activity(self,
                       category: str,
                       activity_type: str,
                       grade_level: str,
                       skill_level: str,
                       class_size: int,
                       available_equipment: List[str]) -> Dict[str, Any]:
        """Select an appropriate activity based on parameters."""
        try:
            # Get available activities in category
            category_activities = self.activities[category]
            
            # Filter by activity type
            type_activities = {
                k: v for k, v in category_activities.items()
                if activity_type in k or k in activity_type
            }
            
            # Filter by equipment requirements
            equipment_activities = {
                k: v for k, v in type_activities.items()
                if self.check_equipment_requirements(v["equipment"], available_equipment)
            }
            
            # Select activity based on skill level and class size
            selected_activity = self.choose_activity(equipment_activities, skill_level, class_size)
            
            # Add name field for the activity
            selected_activity["name"] = activity_type
            
            # Add modifications for grade level and skill level
            selected_activity["modifications"] = self.generate_activity_modifications(
                selected_activity,
                grade_level,
                skill_level,
                class_size
            )
            
            return selected_activity
            
        except Exception as e:
            self.logger.error(f"Error selecting activity: {str(e)}")
            raise

    def check_equipment_requirements(self, required_equipment: str, available_equipment: List[str]) -> bool:
        """Check if required equipment is available."""
        try:
            # Map equipment levels to required equipment
            equipment_mapping = {
                "minimal": ["cones", "whistle"],
                "basic": ["cones", "balls", "jump ropes"],
                "full": ["cones", "whistle", "balls", "jump ropes", "mats", "gymnastics equipment"]
            }
            
            required = equipment_mapping.get(required_equipment, ["cones", "whistle"])
            return all(item in available_equipment for item in required)
        except Exception as e:
            self.logger.error(f"Error checking equipment requirements: {str(e)}")
            return False

    def choose_activity(self, activities: Dict[str, Any], skill_level: str, class_size: int) -> Dict[str, Any]:
        """Choose the most appropriate activity based on skill level and class size."""
        try:
            # TODO: Implement activity selection algorithm
            return list(activities.values())[0]
        except Exception as e:
            self.logger.error(f"Error choosing activity: {str(e)}")
            raise

    def generate_activity_modifications(self,
                                     activity: Dict[str, Any],
                                     grade_level: str,
                                     skill_level: str,
                                     class_size: int) -> Dict[str, Any]:
        """Generate modifications for an activity based on parameters."""
        try:
            modifications = {
                "modifications": {
                    "simplified": [],
                    "advanced": []
                },
                "group_size": self.calculate_group_size(class_size),
                "equipment_modifications": self.generate_equipment_modifications(activity["equipment"])
            }
            
            # Add skill-level specific modifications
            if skill_level == "beginner":
                modifications["modifications"]["simplified"].extend([
                    "Reduce complexity",
                    "Focus on basic movements",
                    "Provide more demonstrations"
                ])
            elif skill_level == "advanced":
                modifications["modifications"]["advanced"].extend([
                    "Increase complexity",
                    "Add competitive elements",
                    "Focus on technique refinement"
                ])
            
            # Add grade-level specific modifications
            if grade_level in ["K-2", "3-5"]:
                modifications["modifications"]["simplified"].extend([
                    "Use simpler language",
                    "Provide more visual cues",
                    "Increase supervision"
                ])
            
            return modifications
            
        except Exception as e:
            self.logger.error(f"Error generating activity modifications: {str(e)}")
            raise

    def calculate_group_size(self, class_size: int) -> int:
        """Calculate appropriate group size for activities."""
        try:
            max_group_size = self.settings["max_students_per_group"]
            
            # If class size is smaller than max group size, return class size
            if class_size <= max_group_size:
                return class_size
            
            # Calculate optimal group size
            return max(1, min(max_group_size, class_size // 2))
        except Exception as e:
            self.logger.error(f"Error calculating group size: {str(e)}")
            return self.settings["max_students_per_group"]

    def generate_equipment_modifications(self, required_equipment: str) -> List[str]:
        """Generate equipment modifications and alternatives."""
        try:
            modifications = []
            
            # Add equipment alternatives
            if required_equipment == "full":
                modifications.append("Use basic equipment with modified rules")
            elif required_equipment == "basic":
                modifications.append("Use minimal equipment with creative adaptations")
                modifications.append("Use lighter balls")
                modifications.append("Substitute equipment with available alternatives")
            elif required_equipment == "minimal":
                modifications.append("Use body weight exercises")
                modifications.append("Create equipment from available materials")
            
            return modifications
            
        except Exception as e:
            self.logger.error(f"Error generating equipment modifications: {str(e)}")
            return []

    def determine_equipment_needs(self, activities: List[Dict[str, Any]]) -> List[str]:
        """Determine equipment needs for the lesson plan."""
        try:
            equipment_needs = set()
            
            for activity in activities:
                if "equipment" in activity:
                    equipment_needs.update(self.settings["equipment_requirements"][activity["equipment"]])
            
            return list(equipment_needs)
            
        except Exception as e:
            self.logger.error(f"Error determining equipment needs: {str(e)}")
            return []

    def generate_objectives(self, grade_level: str, focus_area: str) -> List[str]:
        """Generate learning objectives based on grade level and focus area."""
        try:
            objectives = []
            
            # Add grade-level objectives
            objectives.extend(self.curriculum_standards["state"]["objectives"][grade_level])
            
            # Add focus area objectives
            objectives.extend(self.curriculum_standards["national"][focus_area])
            
            return objectives
            
        except Exception as e:
            self.logger.error(f"Error generating objectives: {str(e)}")
            return []

    def generate_assessment_criteria(self, focus_area: str) -> Dict[str, Any]:
        """Generate assessment criteria for the lesson plan."""
        try:
            criteria = {
                "technique": [],
                "participation": [],
                "improvement": []
            }
            
            # Add focus area specific criteria if available
            if hasattr(self.assessment_system, 'assessment_criteria') and focus_area in self.assessment_system.assessment_criteria:
                criteria["technique"].extend(
                    self.assessment_system.assessment_criteria[focus_area]["technique"]
                )
            
            # Add general criteria
            criteria["participation"].extend([
                "Active engagement",
                "Following instructions",
                "Teamwork"
            ])
            
            criteria["improvement"].extend([
                "Skill development",
                "Effort",
                "Progress"
            ])
            
            return {"criteria": criteria}
            
        except Exception as e:
            self.logger.error(f"Error generating assessment criteria: {str(e)}")
            return {"criteria": {}}

    def generate_safety_considerations(self, activities: List[Dict[str, Any]]) -> List[str]:
        """Generate safety considerations for the lesson plan."""
        try:
            safety_considerations = [
                "Proper warmup and cooldown",
                "Adequate supervision",
                "Clear instructions",
                "Ensure adequate spacing"
            ]
            
            # Add activity-specific safety considerations
            for activity in activities:
                if "safety" in activity:
                    safety_considerations.extend(activity["safety"])
            
            return safety_considerations
            
        except Exception as e:
            self.logger.error(f"Error generating safety considerations: {str(e)}")
            return []

    def save_lesson_templates(self):
        """Save lesson templates to persistent storage."""
        try:
            import json
            with open(self.template_file, 'w') as f:
                json.dump(self.lesson_templates, f, indent=2)
            self.logger.info("Lesson templates saved successfully")
        except Exception as e:
            self.logger.error(f"Error saving lesson templates: {str(e)}")
            raise 