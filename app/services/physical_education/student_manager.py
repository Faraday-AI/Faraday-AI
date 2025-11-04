import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
from app.core.monitoring import track_metrics
from app.services.physical_education import service_integration
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.physical_education.student import (
    Student,
    StudentHealthFitnessGoal,
    StudentHealthGoalProgress,
    StudentHealthGoalRecommendation,
    StudentHealthProfile
)
from app.models.health_fitness.metrics.health import HealthMetric
from app.models.physical_education.pe_enums.pe_types import (
    Gender,
    FitnessLevel,
    GoalType,
    GoalStatus,
    GoalCategory,
    GoalTimeframe
)
from app.models.core.core_models import (
    MetricType,
    MeasurementUnit
)

class StudentManager:
    """Service for managing student profiles, class rosters, and progress tracking."""
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(StudentManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, db_session: Optional[Session] = None):
        # For singleton, we need to check if this is a new instance or existing
        if not hasattr(self, 'logger'):
            # This is a new instance, initialize everything
            self.logger = logging.getLogger("student_manager")
            self.assessment_system = None
            self.lesson_planner = None
            
            # Student data structures
            self.students: Dict[str, Dict[str, Any]] = {}
            self.classes: Dict[str, Dict[str, Any]] = {}
            self.attendance_records: Dict[str, Dict[str, List[datetime]]] = {}
            self.progress_records: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}
            
            # Settings
            self.settings = {
                "max_class_size": 30,
                "min_attendance_required": 0.8,  # 80% attendance required
                "progress_update_frequency": 7,  # days
                "assessment_frequency": 14,  # days
                "skill_levels": ["beginner", "intermediate", "advanced"],
                "medical_conditions": [
                    "asthma",
                    "diabetes",
                    "epilepsy",
                    "heart_condition",
                    "allergies",
                    "other"
                ]
            }
            
            # Progress tracking metrics
            self.progress_metrics = {
                "fitness": [
                    "cardiovascular_endurance",
                    "muscular_strength",
                    "flexibility",
                    "body_composition"
                ],
                "skills": [
                    "locomotor_skills",
                    "non_locomotor_skills",
                    "manipulative_skills"
                ],
                "social": [
                    "teamwork",
                    "sportsmanship",
                    "leadership",
                    "communication"
                ]
            }
        
        # Always update the database session for existing instances
        if db_session is not None:
            self.db = db_session
    
    async def initialize(self):
        """Initialize the student manager."""
        try:
            self.db = next(get_db())
            self.assessment_system = service_integration.get_service('assessment_system')
            self.lesson_planner = service_integration.get_service('lesson_planner')
            self.logger.info("Student Manager initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing Student Manager: {str(e)}")
            raise
    
    async def cleanup(self):
        """Cleanup the student manager."""
        try:
            self.db = None
            self.assessment_system = None
            self.lesson_planner = None
            self.logger.info("Student Manager cleaned up successfully")
        except Exception as e:
            self.logger.error(f"Error cleaning up Student Manager: {str(e)}")
            raise

    def load_student_data(self):
        """Load student data from persistent storage."""
        try:
            # TODO: Implement data loading from persistent storage
            self.logger.info("Student data loaded successfully")
        except Exception as e:
            self.logger.error(f"Error loading student data: {str(e)}")
            raise

    def load_class_data(self):
        """Load class data from persistent storage."""
        try:
            # TODO: Implement data loading from persistent storage
            self.logger.info("Class data loaded successfully")
        except Exception as e:
            self.logger.error(f"Error loading class data: {str(e)}")
            raise

    @track_metrics("create_student_profile")
    async def get_student_profile(self, student_id: str) -> Dict[str, Any]:
        """Get a student profile by ID."""
        try:
            if student_id not in self.students:
                raise ValueError(f"Student {student_id} does not exist")
            return self.students[student_id]
        except Exception as e:
            self.logger.error(f"Error getting student profile: {str(e)}")
            raise

    async def get_class_info(self, class_id: str) -> Dict[str, Any]:
        """Get class information by ID."""
        try:
            if class_id not in self.classes:
                raise ValueError(f"Class {class_id} does not exist")
            return self.classes[class_id]
        except Exception as e:
            self.logger.error(f"Error getting class info: {str(e)}")
            raise

    async def create_student_profile(self,
                                   student_id: str,
                                   first_name: str,
                                   last_name: str,
                                   grade_level: str,
                                   date_of_birth: datetime,
                                   medical_conditions: List[str] = None,
                                   emergency_contact: Dict[str, str] = None) -> Dict[str, Any]:
        """Create a new student profile."""
        try:
            # Validate parameters
            self.validate_student_parameters(
                student_id,
                first_name,
                last_name,
                grade_level,
                date_of_birth,
                medical_conditions,
                emergency_contact
            )
            
            # Create student profile
            student_profile = {
                "student_id": student_id,
                "first_name": first_name,
                "last_name": last_name,
                "grade_level": grade_level,
                "date_of_birth": date_of_birth.isoformat(),
                "medical_conditions": medical_conditions or [],
                "emergency_contact": emergency_contact or {},
                "skill_level": "beginner",
                "attendance_rate": 1.0,
                "current_classes": [],
                "progress_history": [],
                "assessments": [],
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat()
            }
            
            # Add to students dictionary
            self.students[student_id] = student_profile
            
            return student_profile
            
        except Exception as e:
            self.logger.error(f"Error creating student profile: {str(e)}")
            raise

    def validate_student_parameters(self,
                                  student_id: str,
                                  first_name: str,
                                  last_name: str,
                                  grade_level: str,
                                  date_of_birth: datetime,
                                  medical_conditions: List[str],
                                  emergency_contact: Dict[str, str]):
        """Validate student profile parameters."""
        try:
            # Validate student ID
            if student_id in self.students:
                raise ValueError(f"Student ID {student_id} already exists")
            
            # Validate names
            if not first_name or not last_name:
                raise ValueError("First and last names are required")
            
            # Validate grade level
            if grade_level not in self.lesson_planner.curriculum_standards["state"]["grade_levels"]:
                raise ValueError(f"Invalid grade level: {grade_level}")
            
            # Validate date of birth
            if date_of_birth > datetime.now():
                raise ValueError("Date of birth cannot be in the future")
            
            # Validate medical conditions
            if medical_conditions:
                for condition in medical_conditions:
                    if condition not in self.settings["medical_conditions"]:
                        raise ValueError(f"Invalid medical condition: {condition}")
            
            # Validate emergency contact
            if emergency_contact:
                required_fields = ["name", "relationship", "phone"]
                if not all(field in emergency_contact for field in required_fields):
                    raise ValueError("Emergency contact missing required fields")
            
        except Exception as e:
            self.logger.error(f"Error validating student parameters: {str(e)}")
            raise

    @track_metrics("create_class")
    async def create_class(self,
                          class_id: str,
                          name: str,
                          grade_level: str,
                          max_size: int,
                          schedule: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new class."""
        try:
            # Validate parameters
            self.validate_class_parameters(class_id, name, grade_level, max_size, schedule)
            
            # Create class
            new_class = {
                "class_id": class_id,
                "name": name,
                "grade_level": grade_level,
                "max_size": max_size,
                "current_size": 0,
                "schedule": schedule,
                "students": [],
                "attendance_records": {},
                "progress_records": {},
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat()
            }
            
            # Add to classes dictionary
            self.classes[class_id] = new_class
            
            return new_class
            
        except Exception as e:
            self.logger.error(f"Error creating class: {str(e)}")
            raise

    def validate_class_parameters(self,
                                class_id: str,
                                name: str,
                                grade_level: str,
                                max_size: int,
                                schedule: Dict[str, Any]):
        """Validate class parameters."""
        try:
            # Validate class ID
            if class_id in self.classes:
                raise ValueError(f"Class ID {class_id} already exists")
            
            # Validate name
            if not name:
                raise ValueError("Class name is required")
            
            # Validate grade level
            if grade_level not in self.lesson_planner.curriculum_standards["state"]["grade_levels"]:
                raise ValueError(f"Invalid grade level: {grade_level}")
            
            # Validate max size
            if max_size > self.settings["max_class_size"]:
                raise ValueError(f"Max class size cannot exceed {self.settings['max_class_size']}")
            
            # Validate schedule
            required_fields = ["days", "start_time", "end_time", "location"]
            if not all(field in schedule for field in required_fields):
                raise ValueError("Schedule missing required fields")
            
        except Exception as e:
            self.logger.error(f"Error validating class parameters: {str(e)}")
            raise

    @track_metrics("enroll_student")
    async def enroll_student(self, student_id: str, class_id: str) -> bool:
        """Enroll a student in a class."""
        try:
            # Validate student and class exist
            if student_id not in self.students:
                raise ValueError(f"Student {student_id} does not exist")
            if class_id not in self.classes:
                raise ValueError(f"Class {class_id} does not exist")
            
            # Check class size
            if self.classes[class_id]["current_size"] >= self.classes[class_id]["max_size"]:
                return False  # Class is full, return False instead of raising exception
            
            # Add student to class
            if student_id not in self.classes[class_id]["students"]:
                self.classes[class_id]["students"].append(student_id)
                self.classes[class_id]["current_size"] += 1
                
                # Add class to student's current classes
                if class_id not in self.students[student_id]["current_classes"]:
                    self.students[student_id]["current_classes"].append(class_id)
                
                # Initialize attendance and progress records
                self.initialize_student_records(student_id, class_id)
                
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error enrolling student: {str(e)}")
            raise

    def initialize_student_records(self, student_id: str, class_id: str):
        """Initialize attendance and progress records for a student in a class."""
        try:
            # Initialize attendance records
            if class_id not in self.attendance_records:
                self.attendance_records[class_id] = {}
            self.attendance_records[class_id][student_id] = []
            
            # Initialize progress records
            if class_id not in self.progress_records:
                self.progress_records[class_id] = {}
            self.progress_records[class_id][student_id] = []
            
        except Exception as e:
            self.logger.error(f"Error initializing student records: {str(e)}")
            raise

    @track_metrics("record_attendance")
    async def record_attendance(self,
                              class_id: str,
                              student_id: str,
                              date: datetime,
                              present: bool) -> bool:
        """Record student attendance for a class."""
        try:
            # Validate parameters
            if class_id not in self.classes:
                raise ValueError(f"Class {class_id} does not exist")
            if student_id not in self.students:
                raise ValueError(f"Student {student_id} does not exist")
            if student_id not in self.classes[class_id]["students"]:
                raise ValueError(f"Student {student_id} is not enrolled in class {class_id}")
            
            # Record attendance - store both present and absent records
            if present:
                self.attendance_records[class_id][student_id].append(date)
            else:
                # For absent records, we need to ensure the structure exists
                if class_id not in self.attendance_records:
                    self.attendance_records[class_id] = {}
                if student_id not in self.attendance_records[class_id]:
                    self.attendance_records[class_id][student_id] = []
                # Store absent date with a marker to distinguish from present
                self.attendance_records[class_id][student_id].append(f"absent_{date}")
            
            # Update attendance rate
            self.update_attendance_rate(student_id, class_id)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error recording attendance: {str(e)}")
            raise

    def update_attendance_rate(self, student_id: str, class_id: str):
        """Update student's attendance rate for a class."""
        try:
            # Calculate attendance rate
            total_classes = len(self.classes[class_id]["schedule"]["days"])
            attended_classes = len(self.attendance_records[class_id][student_id])
            attendance_rate = attended_classes / total_classes
            
            # Update student's attendance rate
            self.students[student_id]["attendance_rate"] = attendance_rate
            
        except Exception as e:
            self.logger.error(f"Error updating attendance rate: {str(e)}")
            raise

    @track_metrics("record_progress")
    async def record_progress(self,
                            student_id: str,
                            class_id: str,
                            metrics: Dict[str, Any],
                            date: Optional[datetime] = None) -> bool:
        """Record student progress for a class."""
        try:
            # Validate parameters
            if class_id not in self.classes:
                raise ValueError(f"Class {class_id} does not exist")
            if student_id not in self.students:
                raise ValueError(f"Student {student_id} does not exist")
            if student_id not in self.classes[class_id]["students"]:
                raise ValueError(f"Student {student_id} is not enrolled in class {class_id}")
            
            # Validate metrics
            self.validate_progress_metrics(metrics)
            
            # Create progress record
            progress_record = {
                "date": (date or datetime.now()).isoformat(),
                "metrics": metrics,
                "class_id": class_id
            }
            
            # Add to progress records
            self.progress_records[class_id][student_id].append(progress_record)
            
            # Update student's progress history
            self.students[student_id]["progress_history"].append(progress_record)
            
            # Update skill level if necessary
            await self.update_skill_level(student_id, class_id)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error recording progress: {str(e)}")
            raise

    def validate_progress_metrics(self, metrics: Dict[str, Any]):
        """Validate progress metrics."""
        try:
            # Check for required categories
            for category in self.progress_metrics:
                if category not in metrics:
                    raise ValueError(f"Missing progress category: {category}")
                
                # Check for required metrics in each category
                for metric in self.progress_metrics[category]:
                    if metric not in metrics[category]:
                        raise ValueError(f"Missing progress metric: {metric}")
                    
                    # Validate metric value
                    if not isinstance(metrics[category][metric], (int, float)):
                        raise ValueError(f"Invalid metric value for {metric}")
                    
        except Exception as e:
            self.logger.error(f"Error validating progress metrics: {str(e)}")
            raise

    async def update_skill_level(self, student_id: str, class_id: str):
        """Update student's skill level based on progress."""
        try:
            # Get student's progress records
            progress_records = self.progress_records[class_id][student_id]
            
            if not progress_records:
                return
            
            # Get latest progress record
            latest_progress = progress_records[-1]
            
            # Calculate overall progress
            overall_progress = self.calculate_overall_progress(latest_progress["metrics"])
            
            # Determine new skill level
            new_skill_level = self.determine_skill_level(overall_progress)
            
            # Update student's skill level
            self.students[student_id]["skill_level"] = new_skill_level
            
        except Exception as e:
            self.logger.error(f"Error updating skill level: {str(e)}")
            raise

    def calculate_overall_progress(self, metrics: Dict[str, Any]) -> float:
        """Calculate overall progress from metrics."""
        try:
            total_progress = 0
            total_metrics = 0
            
            # Calculate average progress across all categories and metrics
            for category in self.progress_metrics:
                for metric in self.progress_metrics[category]:
                    if metric in metrics[category]:
                        total_progress += metrics[category][metric]
                        total_metrics += 1
            
            return total_progress / total_metrics if total_metrics > 0 else 0
            
        except Exception as e:
            self.logger.error(f"Error calculating overall progress: {str(e)}")
            return 0

    def determine_skill_level(self, progress: float) -> str:
        """Determine skill level based on progress score."""
        try:
            if progress >= 0.8:
                return "advanced"
            elif progress >= 0.5:
                return "intermediate"
            else:
                return "beginner"
        except Exception as e:
            self.logger.error(f"Error determining skill level: {str(e)}")
            return "beginner"

    @track_metrics("generate_progress_report")
    async def generate_progress_report(self,
                                     student_id: str,
                                     class_id: str,
                                     start_date: datetime,
                                     end_date: datetime) -> Dict[str, Any]:
        """Generate a progress report for a student in a class."""
        try:
            # Validate parameters
            if class_id not in self.classes:
                raise ValueError(f"Class {class_id} does not exist")
            if student_id not in self.students:
                raise ValueError(f"Student {student_id} does not exist")
            if student_id not in self.classes[class_id]["students"]:
                raise ValueError(f"Student {student_id} is not enrolled in class {class_id}")
            
            # Get relevant progress records
            progress_records = [
                record for record in self.progress_records[class_id][student_id]
                if start_date <= datetime.fromisoformat(record["date"]) <= end_date
            ]
            
            # Calculate attendance
            attendance_records = [
                date for date in self.attendance_records[class_id][student_id]
                if start_date <= date <= end_date
            ]
            
            # Generate report
            report = {
                "student_id": student_id,
                "class_id": class_id,
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                },
                "attendance": {
                    "total_classes": len(self.classes[class_id]["schedule"]["days"]),
                    "attended": len(attendance_records),
                    "rate": len(attendance_records) / len(self.classes[class_id]["schedule"]["days"])
                },
                "progress_summary": self.calculate_progress_summary(progress_records),
                "skill_level": self.students[student_id]["skill_level"],
                "recommendations": await self.generate_recommendations(student_id, class_id, progress_records),
                "generated_at": datetime.now().isoformat()
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating progress report: {str(e)}")
            raise

    def calculate_progress_summary(self, progress_records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate progress summary from records."""
        try:
            summary = {
                "overall": 0,
                "categories": {}
            }
            
            if not progress_records:
                return summary
            
            # Calculate progress for each category
            for category in self.progress_metrics:
                category_progress = 0
                total_metrics = 0
                
                for record in progress_records:
                    if category in record["metrics"]:
                        for metric in self.progress_metrics[category]:
                            if metric in record["metrics"][category]:
                                category_progress += record["metrics"][category][metric]
                                total_metrics += 1
                
                summary["categories"][category] = (
                    category_progress / total_metrics if total_metrics > 0 else 0
                )
            
            # Calculate overall progress
            summary["overall"] = sum(summary["categories"].values()) / len(summary["categories"])
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error calculating progress summary: {str(e)}")
            return {"overall": 0, "categories": {}}

    async def generate_recommendations(self,
                                     student_id: str,
                                     class_id: str,
                                     progress_records: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on student progress."""
        try:
            recommendations = []
            
            # Get student's current skill level
            skill_level = self.students[student_id]["skill_level"]
            
            # Get latest progress record
            if progress_records:
                latest_progress = progress_records[-1]
                
                # Generate recommendations based on progress
                for category in self.progress_metrics:
                    category_progress = sum(
                        latest_progress["metrics"][category].values()
                    ) / len(latest_progress["metrics"][category])
                    
                    if category_progress < 0.5:
                        recommendations.append(
                            f"Focus on improving {category} skills through targeted exercises"
                        )
                    elif category_progress > 0.8:
                        recommendations.append(
                            f"Consider more challenging {category} activities"
                        )
            
            # Add skill-level specific recommendations
            if skill_level == "beginner":
                recommendations.append("Focus on mastering basic movements and techniques")
            elif skill_level == "intermediate":
                recommendations.append("Work on refining techniques and increasing complexity")
            else:
                recommendations.append("Challenge yourself with advanced variations and combinations")
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {str(e)}")
            return []

    def save_student_data(self, student_id: str, filename: str):
        """Save student data to persistent storage."""
        try:
            import json
            f = open(filename, 'w')
            json.dump(self.students[student_id], f, indent=4)
            f.close()
            self.logger.info(f"Student data for {student_id} saved to {filename}")
        except Exception as e:
            self.logger.error(f"Error saving student data: {str(e)}")
            raise

    def save_class_data(self, class_id: str, filename: str):
        """Save class data to persistent storage."""
        try:
            import json
            f = open(filename, 'w')
            json.dump(self.classes[class_id], f, indent=4)
            f.close()
            self.logger.info(f"Class data for {class_id} saved to {filename}")
        except Exception as e:
            self.logger.error(f"Error saving class data: {str(e)}")
            raise

    async def create_student_goal(
        self,
        student_id: int,
        goal_type: str,
        target_value: float,
        timeframe: str = "medium_term",
        description: str = None
    ) -> Dict[str, Any]:
        """Create a new goal for a student.
        
        NOTE: StudentHealthFitnessGoal requires student_health.id (StudentHealthProfile),
        not students.id. This method will create/get the StudentHealthProfile first.
        """
        try:
            if not self.db:
                return {
                    "goal_created": False,
                    "error": "Database session not initialized"
                }
            
            # Get the Student record to extract name/DOB for StudentHealthProfile
            student = self.db.query(Student).filter(Student.id == student_id).first()
            if not student:
                return {
                    "goal_created": False,
                    "error": f"Student {student_id} not found"
                }
            
            # Find or create StudentHealthProfile
            # The foreign key is student_health.id, not students.id
            # Use text query to avoid relationship mapping issues
            from sqlalchemy import text
            student_health_result = self.db.execute(
                text("""
                    SELECT id FROM student_health 
                    WHERE student_id = :student_id
                    LIMIT 1
                """),
                {
                    "student_id": student.id
                }
            ).fetchone()
            
            if student_health_result:
                student_health_id = student_health_result[0]
            else:
                # Create StudentHealthProfile if it doesn't exist using raw SQL
                # NOTE: student_health table has a student_id column that references students.id
                result = self.db.execute(
                    text("""
                        INSERT INTO student_health (student_id, first_name, last_name, date_of_birth, grade_level, created_at, updated_at)
                        VALUES (:student_id, :first_name, :last_name, :date_of_birth, :grade_level, :created_at, :updated_at)
                        RETURNING id
                    """),
                    {
                        "student_id": student.id,  # Link to students.id
                        "first_name": student.first_name,
                        "last_name": student.last_name,
                        "date_of_birth": student.date_of_birth,
                        "grade_level": getattr(student, 'grade_level', None),
                        "created_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                )
                student_health_id = result.scalar()
                self.db.flush()  # Use flush for SAVEPOINT transactions
            
            # Create a new health fitness goal using student_health.id
            goal = StudentHealthFitnessGoal(
                student_id=student_health_id,  # Use student_health.id, not students.id
                goal_type=GoalType(goal_type),
                category=GoalCategory.ENDURANCE,  # Add the required category field
                target_value=target_value,
                timeframe=GoalTimeframe(timeframe),
                description=description or f"Goal for {goal_type}",
                target_date=datetime.utcnow() + timedelta(days=30),  # Add required target_date
                status=GoalStatus.NOT_STARTED,
                created_at=datetime.utcnow()
            )
            
            self.db.add(goal)
            self.db.flush()  # Use flush for SAVEPOINT transactions
            self.db.refresh(goal)
            
            self.logger.info(f"Created goal {goal.id} for student_health {student_health_id} (student {student_id})")
            
            return {
                "goal_created": True,
                "goal_id": goal.id,
                "goal_type": goal_type,
                "target_value": target_value,
                "status": goal.status.value
            }
        except Exception as e:
            self.logger.error(f"Error creating student goal: {str(e)}")
            return {
                "goal_created": False,
                "error": str(e)
            }

    async def update_student_progress(
        self,
        student_id: int,
        activity_id: int,
        progress_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update student progress for an activity."""
        try:
            # Calculate overall progress score
            progress_score = 0.0
            if "skill_improvement" in progress_data:
                progress_score += progress_data["skill_improvement"] * 0.6
            if "fitness_gain" in progress_data:
                progress_score += progress_data["fitness_gain"] * 0.4
            
            # Update student's overall progress
            student = self.db.query(Student).filter(Student.id == student_id).first()
            if student:
                # Update student's progress metrics
                if hasattr(student, 'overall_progress'):
                    student.overall_progress = min(100.0, (student.overall_progress or 0) + progress_score)
                
                self.db.commit()
            
            self.logger.info(f"Updated progress for student {student_id} in activity {activity_id}")
            
            return {
                "progress_updated": True,
                "student_id": student_id,
                "activity_id": activity_id,
                "progress_score": progress_score,
                "updated_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error updating student progress: {str(e)}")
            return {
                "progress_updated": False,
                "error": str(e)
            }
    
    def add_student_to_class(self, student_id: int, class_id: int):
        """Add a student to a class using database IDs."""
        try:
            if not self.db:
                raise ValueError("Database session not available")
            
            # Check if student and class exist
            from app.models.physical_education.student.models import Student
            from app.models.physical_education.class_.models import PhysicalEducationClass, ClassStudent
            from app.models.physical_education.pe_enums.pe_types import ClassStatus
            
            student = self.db.query(Student).filter(Student.id == student_id).first()
            if not student:
                raise ValueError(f"Student {student_id} not found")
            
            class_ = self.db.query(PhysicalEducationClass).filter(PhysicalEducationClass.id == class_id).first()
            if not class_:
                raise ValueError(f"Class {class_id} not found")
            
            # Check if student is already enrolled
            existing_enrollment = self.db.query(ClassStudent).filter(
                ClassStudent.student_id == student_id,
                ClassStudent.class_id == class_id
            ).first()
            
            if existing_enrollment:
                raise ValueError(f"Student {student_id} is already enrolled in class {class_id}")
            
            # Check class capacity
            current_enrollment_count = self.db.query(ClassStudent).filter(
                ClassStudent.class_id == class_id
            ).count()
            
            if class_.max_students and current_enrollment_count >= class_.max_students:
                raise ValueError(f"Class {class_id} is at maximum capacity ({class_.max_students} students)")
            
            # Create enrollment record
            enrollment = ClassStudent(
                student_id=student_id,
                class_id=class_id,
                status=ClassStatus.ACTIVE
            )
            
            self.db.add(enrollment)
            self.db.commit()
            
            self.logger.info(f"Student {student_id} added to class {class_id}")
        except Exception as e:
            self.logger.error(f"Error adding student to class: {str(e)}")
            if self.db:
                self.db.rollback()
            raise

    def remove_student_from_class(self, student_id: int, class_id: int):
        """Remove a student from a class using database IDs."""
        try:
            if not self.db:
                raise ValueError("Database session not available")
            
            # Check if student and class exist
            from app.models.physical_education.student.models import Student
            from app.models.physical_education.class_.models import PhysicalEducationClass, ClassStudent
            
            student = self.db.query(Student).filter(Student.id == student_id).first()
            if not student:
                raise ValueError(f"Student {student_id} not found")
            
            class_ = self.db.query(PhysicalEducationClass).filter(PhysicalEducationClass.id == class_id).first()
            if not class_:
                raise ValueError(f"Class {class_id} not found")
            
            # Find and remove enrollment record
            enrollment = self.db.query(ClassStudent).filter(
                ClassStudent.student_id == student_id,
                ClassStudent.class_id == class_id
            ).first()
            
            if not enrollment:
                raise ValueError(f"Student {student_id} is not enrolled in class {class_id}")
            
            self.db.delete(enrollment)
            self.db.commit()
            
            self.logger.info(f"Student {student_id} removed from class {class_id}")
        except Exception as e:
            self.logger.error(f"Error removing student from class: {str(e)}")
            if self.db:
                self.db.rollback()
            raise

    def get_student_classes(self, student_id: int):
        """Get all classes for a student using database ID."""
        try:
            if not self.db:
                raise ValueError("Database session not available")
            
            # Check if student exists
            from app.models.physical_education.student.models import Student
            from app.models.physical_education.class_.models import ClassStudent, PhysicalEducationClass
            
            student = self.db.query(Student).filter(Student.id == student_id).first()
            if not student:
                raise ValueError(f"Student {student_id} not found")
            
            # Get all classes the student is enrolled in
            enrollments = self.db.query(ClassStudent).filter(
                ClassStudent.student_id == student_id
            ).all()
            
            class_ids = [enrollment.class_id for enrollment in enrollments]
            classes = self.db.query(PhysicalEducationClass).filter(
                PhysicalEducationClass.id.in_(class_ids)
            ).all()
            
            self.logger.info(f"Retrieved {len(classes)} classes for student {student_id}")
            return classes
        except Exception as e:
            self.logger.error(f"Error getting student classes: {str(e)}")
            raise

    def get_class_students(self, class_id: int):
        """Get all students in a class using database ID."""
        try:
            if not self.db:
                raise ValueError("Database session not available")
            
            # Check if class exists
            from app.models.physical_education.class_.models import PhysicalEducationClass, ClassStudent
            from app.models.physical_education.student.models import Student
            
            class_ = self.db.query(PhysicalEducationClass).filter(PhysicalEducationClass.id == class_id).first()
            if not class_:
                raise ValueError(f"Class {class_id} not found")
            
            # Get all students enrolled in the class
            enrollments = self.db.query(ClassStudent).filter(
                ClassStudent.class_id == class_id
            ).all()
            
            student_ids = [enrollment.student_id for enrollment in enrollments]
            students = self.db.query(Student).filter(
                Student.id.in_(student_ids)
            ).all()
            
            self.logger.info(f"Retrieved {len(students)} students for class {class_id}")
            return students
        except Exception as e:
            self.logger.error(f"Error getting class students: {str(e)}")
            raise

    @classmethod
    def reset_instance(cls):
        """Reset the singleton instance for testing purposes."""
        cls._instance = None
    
    def clear_data(self):
        """Clear in-memory data structures for testing purposes."""
        self.students.clear()
        self.classes.clear()
        self.attendance_records.clear()
        self.progress_records.clear() 