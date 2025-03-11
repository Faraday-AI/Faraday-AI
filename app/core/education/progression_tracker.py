from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import json

@dataclass
class AcademicProfile:
    """Tracks a student's academic progression through their school career"""
    student_id: str
    current_grade: int
    enrollment_date: datetime
    academic_history: Dict  # Grade-by-grade performance
    learning_style: Dict
    career_interests: List[str]
    skill_development: Dict
    parent_oversight_level: str  # 'High' for K-5, 'Medium' for 6-8, 'Low' for 9-12

@dataclass
class LearningMilestone:
    """Records significant academic achievements and progress points"""
    milestone_id: str
    student_id: str
    grade_level: int
    subject: str
    achievement: str
    date_achieved: datetime
    ai_recommendations: Dict

class ProgressionTracker:
    """
    Manages long-term student progression tracking from elementary through high school,
    adapting AI support based on grade level and learning needs.
    """
    
    def __init__(self):
        self.student_profiles: Dict[str, AcademicProfile] = {}
        self.learning_milestones: Dict[str, List[LearningMilestone]] = {}
        self.grade_transition_history: Dict[str, List[Dict]] = {}
        
    def initialize_student(self, student_id: str, grade_level: int) -> AcademicProfile:
        """Initialize a new student profile with grade-appropriate settings"""
        profile = AcademicProfile(
            student_id=student_id,
            current_grade=grade_level,
            enrollment_date=datetime.now(),
            academic_history={},
            learning_style=self._get_initial_learning_style(grade_level),
            career_interests=[],
            skill_development={},
            parent_oversight_level=self._get_oversight_level(grade_level)
        )
        
        self.student_profiles[student_id] = profile
        return profile
    
    def _get_initial_learning_style(self, grade_level: int) -> Dict:
        """Define initial learning style preferences based on grade level"""
        if grade_level <= 5:  # Elementary
            return {
                "visual_learning": True,
                "interactive_content": True,
                "gamification_level": "high",
                "reading_assistance": True,
                "math_visualization": True,
                "parent_involvement": "high"
            }
        elif grade_level <= 8:  # Middle School
            return {
                "visual_learning": True,
                "interactive_content": True,
                "gamification_level": "medium",
                "reading_assistance": False,
                "math_visualization": True,
                "parent_involvement": "medium"
            }
        else:  # High School
            return {
                "visual_learning": True,
                "interactive_content": False,
                "gamification_level": "low",
                "reading_assistance": False,
                "math_visualization": False,
                "parent_involvement": "low"
            }
    
    def _get_oversight_level(self, grade_level: int) -> str:
        """Determine appropriate parent oversight level based on grade"""
        if grade_level <= 5:
            return "High"
        elif grade_level <= 8:
            return "Medium"
        return "Low"
    
    def record_milestone(self, student_id: str, subject: str, 
                        achievement: str, ai_recommendations: Dict) -> LearningMilestone:
        """Record a new learning milestone with AI-generated recommendations"""
        if student_id not in self.student_profiles:
            raise ValueError("Student not found")
            
        profile = self.student_profiles[student_id]
        
        milestone = LearningMilestone(
            milestone_id=f"{student_id}_{datetime.now().timestamp()}",
            student_id=student_id,
            grade_level=profile.current_grade,
            subject=subject,
            achievement=achievement,
            date_achieved=datetime.now(),
            ai_recommendations=ai_recommendations
        )
        
        if student_id not in self.learning_milestones:
            self.learning_milestones[student_id] = []
        self.learning_milestones[student_id].append(milestone)
        
        return milestone
    
    def update_grade_level(self, student_id: str, new_grade: int) -> Dict:
        """Handle grade level transitions and update learning parameters"""
        if student_id not in self.student_profiles:
            raise ValueError("Student not found")
            
        profile = self.student_profiles[student_id]
        old_grade = profile.current_grade
        
        # Record grade transition
        transition = {
            "from_grade": old_grade,
            "to_grade": new_grade,
            "date": datetime.now(),
            "learning_style_updates": self._get_initial_learning_style(new_grade)
        }
        
        if student_id not in self.grade_transition_history:
            self.grade_transition_history[student_id] = []
        self.grade_transition_history[student_id].append(transition)
        
        # Update profile
        profile.current_grade = new_grade
        profile.learning_style = transition["learning_style_updates"]
        profile.parent_oversight_level = self._get_oversight_level(new_grade)
        
        return {
            "profile": profile,
            "transition": transition,
            "ai_recommendations": self._get_transition_recommendations(old_grade, new_grade)
        }
    
    def _get_transition_recommendations(self, old_grade: int, new_grade: int) -> Dict:
        """Generate AI recommendations for grade level transitions"""
        recommendations = {
            "learning_adjustments": [],
            "study_habits": [],
            "parent_involvement": []
        }
        
        # Elementary to Middle School transition
        if old_grade == 5 and new_grade == 6:
            recommendations.update({
                "learning_adjustments": [
                    "Introduce more independent learning tasks",
                    "Reduce gamification elements",
                    "Focus on organizational skills"
                ],
                "study_habits": [
                    "Develop note-taking skills",
                    "Introduction to time management",
                    "Multiple subject homework planning"
                ],
                "parent_involvement": [
                    "Transition to weekly progress monitoring",
                    "Encourage independent problem-solving",
                    "Support organization system development"
                ]
            })
        
        # Middle to High School transition
        elif old_grade == 8 and new_grade == 9:
            recommendations.update({
                "learning_adjustments": [
                    "Focus on critical thinking skills",
                    "Introduce college prep elements",
                    "Develop research skills"
                ],
                "study_habits": [
                    "Long-term project planning",
                    "Advanced research techniques",
                    "Test preparation strategies"
                ],
                "parent_involvement": [
                    "Monthly progress reviews",
                    "College planning discussions",
                    "Career exploration support"
                ]
            })
        
        return recommendations
    
    def get_academic_summary(self, student_id: str) -> Dict:
        """Generate a comprehensive academic summary for the student"""
        if student_id not in self.student_profiles:
            raise ValueError("Student not found")
            
        profile = self.student_profiles[student_id]
        milestones = self.learning_milestones.get(student_id, [])
        transitions = self.grade_transition_history.get(student_id, [])
        
        return {
            "profile": profile,
            "current_grade": profile.current_grade,
            "years_enrolled": (datetime.now() - profile.enrollment_date).days / 365,
            "total_milestones": len(milestones),
            "recent_achievements": [m for m in milestones[-5:]] if milestones else [],
            "grade_transitions": transitions,
            "current_learning_style": profile.learning_style,
            "parent_oversight_level": profile.parent_oversight_level
        } 