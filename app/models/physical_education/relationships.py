"""
Model Relationships

This module defines the relationships between physical education models.
"""

from sqlalchemy.orm import relationship

def setup_student_relationships(Student):
    """Setup relationships for the Student model."""
    # Set up all relationships but with different names to avoid conflicts with StudentProfile
    Student.class_students = relationship('ClassStudent', back_populates='student', lazy='joined', overlaps="classes")
    Student.assessments = relationship('app.models.physical_education.assessment.models.Assessment', back_populates='student', lazy='joined')
    Student.progress = relationship('Progress', back_populates='student', lazy='joined')
    # Student.nutrition_plans = relationship('NutritionPlan', back_populates='student', lazy='joined')
    Student.safety_incidents = relationship('SafetyIncident', back_populates='student', lazy='joined')
    Student.attendance_records = relationship('app.models.physical_education.student.models.StudentAttendance', back_populates='student', lazy='joined')
    
    # Add relationships for the FitnessGoal model that references Student
    Student.student_fitness_goals = relationship('app.models.health_fitness.goals.fitness_goals.FitnessGoal', back_populates='student', lazy='joined', overlaps='student,fitness_goals')
    Student.goal_recommendations = relationship('app.models.health_fitness.goals.fitness_goals.GoalRecommendation', back_populates='student', lazy='joined', overlaps='student,goal_recommendations')
    Student.fitness_goal_progress = relationship('app.models.health_fitness.goals.fitness_goals.FitnessGoalProgress', back_populates='student', lazy='joined', overlaps='student,fitness_goal_progress')

def setup_assessment_relationships(Assessment):
    """Setup relationships for the Assessment model."""
    Assessment.student = relationship('Student', 
                                   back_populates='assessments')

def setup_progress_relationships(Progress):
    """Setup relationships for the Progress model."""
    Progress.student = relationship('Student', back_populates='progress')
    Progress.activity = relationship('Activity', back_populates='progress_records')
    Progress.milestones = relationship('ProgressMilestone', back_populates='progress', cascade='all, delete-orphan')
    Progress.goals = relationship('app.models.physical_education.progress.models.ProgressGoal', back_populates='progress', cascade='all, delete-orphan')
    Progress.notes = relationship('ProgressNote', back_populates='progress', cascade='all, delete-orphan')
    Progress.assessments = relationship('ProgressAssessment', back_populates='progress', cascade='all, delete-orphan')

def setup_student_health_profile_relationships(StudentHealthProfile):
    """Setup relationships for the StudentHealthProfile model."""
    # Only include relationships that are actually needed for StudentHealthProfile
    # These are the relationships that are already defined in the StudentHealthProfile model
    pass  # No additional relationships needed beyond what's already defined in the model 