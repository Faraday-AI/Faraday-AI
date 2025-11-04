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
        Student.progress_goals = relationship("app.models.physical_education.progress.models.ProgressGoal", back_populates="student")
    
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

def setup_physical_education_goal_relationships():
    """Setup relationships for PhysicalEducationGoal model."""
    from app.models.physical_education.goal_setting import PhysicalEducationGoal
    from app.models.physical_education.student.models import Student
    from app.models.physical_education.activity.models import Activity
    
    if not hasattr(PhysicalEducationGoal, 'student'):
        PhysicalEducationGoal.student = relationship("app.models.physical_education.student.models.Student", back_populates="physical_education_goals", lazy='select')
    
    if not hasattr(PhysicalEducationGoal, 'activity'):
        PhysicalEducationGoal.activity = relationship("app.models.physical_education.activity.models.Activity", back_populates="physical_education_goals", lazy='select')
    
    # Add back_populates relationships on Student and Activity
    if not hasattr(Student, 'physical_education_goals'):
        Student.physical_education_goals = relationship("app.models.physical_education.goal_setting.PhysicalEducationGoal", back_populates="student", lazy='select')
    
    if not hasattr(Activity, 'physical_education_goals'):
        Activity.physical_education_goals = relationship("app.models.physical_education.goal_setting.PhysicalEducationGoal", back_populates="activity", lazy='select')

def setup_all_physical_education_relationships():
    """Setup all physical education relationships."""
    setup_student_progress_relationships()
    setup_progress_student_relationships()
    
    # Setup Activity progress relationships
    from app.models.physical_education.activity.models import Activity
    from app.models.physical_education.progress.models import ProgressGoal
    
    if not hasattr(Activity, 'progress_goals'):
        Activity.progress_goals = relationship("app.models.physical_education.progress.models.ProgressGoal", back_populates="activity")
    
    # Setup PhysicalEducationGoal relationships
    try:
        setup_physical_education_goal_relationships()
    except Exception:
        # If setup fails (e.g., model not imported), it's okay - relationship will be available after all models are loaded
        pass
    
    # Setup HealthMetric relationships (from health_metric.py)
    try:
        from app.models.physical_education.relationships import setup_health_metric_relationships
        setup_health_metric_relationships()
    except Exception:
        # If setup fails (e.g., model not imported), it's okay - relationship will be available after all models are loaded
        pass
    
    # Setup SkillAssessment relationships
    try:
        from app.models.physical_education.skill_assessment.skill_assessment_models import SkillAssessment, AssessmentCriteria, Skill
        from app.models.physical_education.student.models import Student
        
        if not hasattr(SkillAssessment, 'student'):
            # Use simple string reference "Student" - will be resolved after all models are loaded
            SkillAssessment.student = relationship('Student', back_populates='skill_assessments', lazy='select')
        
        if not hasattr(SkillAssessment, 'skill'):
            # Use fully qualified path to avoid ambiguity with other Skill classes
            SkillAssessment.skill = relationship('app.models.physical_education.skill_assessment.skill_assessment_models.Skill', back_populates='assessments', lazy='select')
        
        if not hasattr(SkillAssessment, 'assessment_criteria'):
            # Use fully qualified path to avoid ambiguity with other SkillAssessment classes
            SkillAssessment.assessment_criteria = relationship('app.models.physical_education.skill_assessment.skill_assessment_models.AssessmentCriteria', back_populates='assessment', lazy='select')
        
        if not hasattr(AssessmentCriteria, 'assessment'):
            # Use fully qualified path to avoid ambiguity with other SkillAssessment classes
            AssessmentCriteria.assessment = relationship('app.models.physical_education.skill_assessment.skill_assessment_models.SkillAssessment', back_populates='assessment_criteria', lazy='select')
        
        if not hasattr(Skill, 'assessments'):
            # Use fully qualified path to avoid ambiguity with other SkillAssessment classes
            Skill.assessments = relationship('app.models.physical_education.skill_assessment.skill_assessment_models.SkillAssessment', back_populates='skill', lazy='select')
        
        # Setup SkillLevel relationship
        from app.models.physical_education.skill_assessment.skill_assessment_models import SkillLevel
        if not hasattr(Skill, 'levels'):
            Skill.levels = relationship('app.models.physical_education.skill_assessment.skill_assessment_models.SkillLevel', back_populates='skill', lazy='select')
        
        if not hasattr(SkillLevel, 'skill'):
            SkillLevel.skill = relationship('app.models.physical_education.skill_assessment.skill_assessment_models.Skill', back_populates='levels', lazy='select')
    except Exception:
        # If setup fails (e.g., model not imported), it's okay - relationship will be available after all models are loaded
        pass 