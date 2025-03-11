from typing import Dict, List, Optional
from dataclasses import dataclass
import datetime

@dataclass
class StudentProfile:
    student_id: str
    name: str
    grade_level: int
    preferred_language: str
    current_courses: List[str]
    academic_performance: Dict[str, float]
    behavior_metrics: Dict[str, float]
    phone_privileges: Dict[str, bool]

class SchoolModeManager:
    """
    Core manager class for Faraday School Mode that coordinates all AI-powered
    education, security, and administrative features.
    """
    
    def __init__(self):
        self.active_students: Dict[str, StudentProfile] = {}
        self.active_sessions: Dict[str, datetime.datetime] = {}
        self.security_alerts: List[Dict] = []
        self.translation_requests: List[Dict] = []
        
    def register_student(self, student_profile: StudentProfile) -> bool:
        """Register a new student in the Faraday School Mode system"""
        if student_profile.student_id in self.active_students:
            return False
        self.active_students[student_profile.student_id] = student_profile
        return True
        
    def start_learning_session(self, student_id: str) -> Optional[Dict]:
        """Initialize an AI-powered learning session for a student"""
        if student_id not in self.active_students:
            return None
            
        student = self.active_students[student_id]
        self.active_sessions[student_id] = datetime.datetime.now()
        
        return {
            "student": student,
            "session_start": self.active_sessions[student_id],
            "ai_tutor_enabled": True,
            "translation_enabled": student.preferred_language != "English",
            "phone_restrictions": self.get_phone_restrictions(student_id)
        }
    
    def get_phone_restrictions(self, student_id: str) -> Dict[str, bool]:
        """Get current phone usage restrictions based on academic performance"""
        student = self.active_students.get(student_id)
        if not student:
            return {"all_apps_restricted": True}
            
        # Calculate restrictions based on grades and behavior
        gpa = sum(student.academic_performance.values()) / len(student.academic_performance)
        behavior_score = sum(student.behavior_metrics.values()) / len(student.behavior_metrics)
        
        return {
            "social_media_restricted": gpa < 3.0 or behavior_score < 0.7,
            "gaming_restricted": gpa < 2.5,
            "educational_apps_enabled": True,
            "emergency_calls_enabled": True
        }
    
    def process_security_alert(self, alert_type: str, location: str, severity: int) -> Dict:
        """Handle real-time security alerts and emergency responses"""
        alert = {
            "type": alert_type,
            "location": location,
            "severity": severity,
            "timestamp": datetime.datetime.now(),
            "status": "active"
        }
        self.security_alerts.append(alert)
        
        # Trigger appropriate response based on alert type and severity
        response = {
            "alert": alert,
            "required_actions": self._get_required_actions(alert_type, severity),
            "notification_targets": self._get_notification_targets(severity)
        }
        return response
    
    def _get_required_actions(self, alert_type: str, severity: int) -> List[str]:
        """Determine required actions based on security alert type and severity"""
        actions = []
        if severity >= 8:  # High severity
            actions.extend([
                "initiate_lockdown",
                "notify_emergency_services",
                "activate_emergency_protocols"
            ])
        elif severity >= 5:  # Medium severity
            actions.extend([
                "increase_security_monitoring",
                "notify_administrators",
                "prepare_containment_measures"
            ])
        else:  # Low severity
            actions.extend([
                "log_incident",
                "monitor_situation",
                "notify_relevant_staff"
            ])
        return actions
    
    def _get_notification_targets(self, severity: int) -> List[str]:
        """Determine who should be notified based on alert severity"""
        targets = ["school_security"]
        if severity >= 5:
            targets.extend(["administrators", "teachers"])
        if severity >= 8:
            targets.extend(["emergency_services", "district_office"])
        return targets
    
    def request_translation(self, content: str, from_lang: str, to_lang: str) -> Dict:
        """Request real-time translation for classroom content or parent communication"""
        translation_request = {
            "content": content,
            "from_language": from_lang,
            "to_language": to_lang,
            "timestamp": datetime.datetime.now(),
            "status": "pending"
        }
        self.translation_requests.append(translation_request)
        return translation_request 