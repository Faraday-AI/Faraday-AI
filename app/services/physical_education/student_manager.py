import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
from app.core.monitoring import track_metrics
from app.services.physical_education.assessment_system import AssessmentSystem
from app.services.physical_education.lesson_planner import LessonPlanner

class StudentManager:
    """Service for managing student profiles, class rosters, and progress tracking."""
    
    def __init__(self):
        self.logger = logging.getLogger("student_manager")
        self.assessment_system = AssessmentSystem()
        self.lesson_planner = LessonPlanner()
        
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

    async def initialize(self):
        """Initialize the student manager."""
        try:
            # Initialize dependent services
            await self.assessment_system.initialize()
            await self.lesson_planner.initialize()
            
            # Load student data
            self.load_student_data()
            
            # Load class data
            self.load_class_data()
            
            self.logger.info("Student manager initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing student manager: {str(e)}")
            raise

    async def cleanup(self):
        """Cleanup student manager resources."""
        try:
            # Cleanup dependent services
            await self.assessment_system.cleanup()
            await self.lesson_planner.cleanup()
            
            # Save student data
            self.save_student_data()
            
            # Save class data
            self.save_class_data()
            
            self.logger.info("Student manager cleaned up successfully")
        except Exception as e:
            self.logger.error(f"Error cleaning up student manager: {str(e)}")
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

    @track_metrics
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

    @track_metrics
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

    @track_metrics
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
                raise ValueError("Class is full")
            
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

    @track_metrics
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
            
            # Record attendance
            if present:
                self.attendance_records[class_id][student_id].append(date)
            
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

    @track_metrics
    async def record_progress(self,
                            student_id: str,
                            class_id: str,
                            metrics: Dict[str, Any]) -> bool:
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
                "date": datetime.now().isoformat(),
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

    @track_metrics
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

    def save_student_data(self):
        """Save student data to persistent storage."""
        try:
            # TODO: Implement data persistence
            self.logger.info("Student data saved successfully")
        except Exception as e:
            self.logger.error(f"Error saving student data: {str(e)}")
            raise

    def save_class_data(self):
        """Save class data to persistent storage."""
        try:
            # TODO: Implement data persistence
            self.logger.info("Class data saved successfully")
        except Exception as e:
            self.logger.error(f"Error saving class data: {str(e)}")
            raise 