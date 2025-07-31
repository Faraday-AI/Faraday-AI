"""
Relationship Setup for Physical Education Models

This module handles setting up relationships after all models are loaded
to avoid circular import issues.
"""

from sqlalchemy.orm import relationship

def setup_student_progress_relationships():
    """Setup Student-Progress relationships after all models are loaded."""
    from app.models.physical_education.student.models import Student
    from app.models.physical_education.progress.models import ProgressGoal, Progress
    
    # Add relationships to Student model if they don't exist
    if not hasattr(Student, 'progress_goals'):
        Student.progress_goals = relationship("ProgressGoal", back_populates="student")
    
    if not hasattr(Student, 'progress'):
        Student.progress = relationship("Progress", back_populates="student")

def setup_progress_student_relationships():
    """Setup Progress-Student relationships after all models are loaded."""
    from app.models.physical_education.progress.models import ProgressGoal, Progress
    from app.models.physical_education.student.models import Student
    from app.models.physical_education.activity.models import Activity
    
    # Add relationships to ProgressGoal model if they don't exist
    if not hasattr(ProgressGoal, 'student'):
        ProgressGoal.student = relationship("Student", back_populates="progress_goals")
    
    if not hasattr(ProgressGoal, 'activity'):
        ProgressGoal.activity = relationship("Activity", back_populates="progress_goals")
    
    # Add relationships to Progress model if they don't exist
    if not hasattr(Progress, 'student'):
        Progress.student = relationship("Student", back_populates="progress")
    
    if not hasattr(Progress, 'activity'):
        Progress.activity = relationship("Activity")
    
    if not hasattr(Progress, 'metrics'):
        from app.models.physical_education.progress.models import ProgressMetric
        Progress.metrics = relationship("ProgressMetric", back_populates="progress")

def setup_all_physical_education_relationships():
    """Setup all physical education relationships."""
    setup_student_progress_relationships()
    setup_progress_student_relationships()
    
    # Setup Activity progress relationships
    from app.models.physical_education.activity.models import Activity
    from app.models.physical_education.progress.models import ProgressGoal
    
    if not hasattr(Activity, 'progress_goals'):
        Activity.progress_goals = relationship("ProgressGoal", back_populates="activity") 