"""Relationship definitions for models to avoid circular imports."""

from sqlalchemy.orm import relationship

def setup_activity_relationships(Activity):
    """Set up relationships for the Activity model."""
    Activity.routines = relationship("app.models.routine.RoutineActivity", back_populates="activity", overlaps="activity,routines")
    Activity.risk_assessments = relationship("app.models.physical_education.safety.models.RiskAssessment", back_populates="activity", overlaps="activity,risk_assessments")
    Activity.safety_incidents = relationship("app.models.physical_education.safety.models.SafetyIncident", back_populates="activity", overlaps="activity,safety_incidents")
    Activity.activity_performances = relationship("app.models.physical_education.activity.models.StudentActivityPerformance", back_populates="activity", overlaps="activity,activity_performances")
    Activity.progressions = relationship("app.models.activity_adaptation.student.activity_student.ActivityProgression", back_populates="activity", overlaps="activity,progressions")
    Activity.activity_plans = relationship("app.models.physical_education.activity_plan.models.ActivityPlanActivity", back_populates="activity", overlaps="activity,plan")
    Activity.exercises = relationship("app.models.physical_education.exercise.models.Exercise", back_populates="activity", overlaps="activity,exercises", viewonly=True)
    Activity.adapted_exercises = relationship("app.models.activity_adaptation.exercise.exercise.AdaptedExercise", overlaps="activity,adapted_exercises", viewonly=True)
    Activity.movement_analyses = relationship("app.models.movement_analysis.analysis.movement_analysis.MovementAnalysis", back_populates="activity", overlaps="activity,movement_analyses")
    Activity.skill_assessments = relationship("app.models.assessment.SkillAssessment", back_populates="activity", overlaps="activity,skill_assessments")
    Activity.adaptations = relationship("app.models.physical_education.activity_adaptation.activity_adaptation.ActivityAdaptation", back_populates="activity", overlaps="activity,adaptations")
    Activity.student_adaptations = relationship("app.models.activity_adaptation.student.activity_student.ActivityAdaptation", back_populates="activity", overlaps="activity,student_adaptations")
    Activity.skill_progress = relationship("app.models.assessment.SkillProgress", back_populates="activity", overlaps="activity,skill_progress")
    Activity.assessment_metrics = relationship("app.models.assessment.AssessmentMetrics", back_populates="activity", cascade="all, delete-orphan", overlaps="activity,assessment_metrics")
    Activity.categories = relationship(
        "app.models.activity.ActivityCategory",
        secondary="activity_categories",
        back_populates="activities",
        overlaps="activity,category_associations,category"
    )
    Activity.category_associations = relationship(
        "app.models.activity.ActivityCategoryAssociation",
        back_populates="activity",
        overlaps="categories"
    )

def setup_student_relationships(Student):
    """Set up relationships for the Student model."""
    Student.safety_incidents = relationship("app.models.physical_education.safety.models.SafetyIncident", back_populates="student", cascade="all, delete-orphan", overlaps="student,safety_incidents")
    Student.safety_incident_bases = relationship("app.models.physical_education.safety.models.SafetyIncidentBase", back_populates="student", cascade="all, delete-orphan", overlaps="student,safety_incident_bases")
    Student.activity_performances = relationship("app.models.physical_education.activity.models.StudentActivityPerformance", back_populates="student", cascade="all, delete-orphan", overlaps="student,activity_performances")
    # Student.activity_preferences = relationship("app.models.physical_education.activity.models.StudentActivityPreference", back_populates="student", cascade="all, delete-orphan", overlaps="student,activity_preferences")  # Commented out - conflicts with ActivityPreference relationship
    Student.adaptation_progressions = relationship("app.models.activity_adaptation.student.activity_student.ActivityProgression", back_populates="student", cascade="all, delete-orphan", overlaps="student,adaptation_progressions")
    Student.activity_progressions = relationship("app.models.physical_education.activity.models.ActivityProgression", back_populates="student", cascade="all, delete-orphan", overlaps="student,activity_progressions")
    Student.student_activity_plans = relationship("app.models.physical_education.activity_plan.models.ActivityPlan", back_populates="student", cascade="all, delete-orphan", overlaps="student,student_activity_plans")
    Student.adapted_activity_plans = relationship("app.models.activity_adaptation.activity.activity.ActivityPlan", back_populates="student", cascade="all, delete-orphan", overlaps="student,adapted_activity_plans")
    Student.adaptations = relationship("app.models.physical_education.activity_adaptation.activity_adaptation.ActivityAdaptation", back_populates="student", cascade="all, delete-orphan", overlaps="student,adaptations")
    Student.classes = relationship("app.models.physical_education.class_.models.PhysicalEducationClass", 
                                 secondary="physical_education_class_students",
                                 lazy='joined',
                                 overlaps="class_students,students")
    Student.movement_analyses = relationship("app.models.movement_analysis.analysis.movement_analysis.MovementAnalysis", back_populates="student", cascade="all, delete-orphan", overlaps="student,movement_analyses")
    # Student.assessments = relationship("Assessment", back_populates="student", cascade="all, delete-orphan", overlaps="student,assessments")
    Student.skill_assessments = relationship("app.models.skill_assessment.assessment.assessment.SkillAssessment", back_populates="student", cascade="all, delete-orphan", overlaps="student,skill_assessments")
    Student.skill_progress = relationship("app.models.skill_assessment.assessment.assessment.SkillProgress", back_populates="student", cascade="all, delete-orphan", overlaps="student,skill_progress")
    Student.assessment_metrics = relationship("app.models.skill_assessment.assessment.assessment.AssessmentMetrics", back_populates="student", cascade="all, delete-orphan", overlaps="student,assessment_metrics")
    Student.routine_performances = relationship("app.models.physical_education.routine.models.RoutinePerformance", back_populates="student", cascade="all, delete-orphan", overlaps="student,routine_performances")
    Student.routine_progress = relationship("app.models.physical_education.routine.models.RoutineProgress", back_populates="student", cascade="all, delete-orphan", overlaps="student,routine_progress")
    Student.adapted_routine_performances = relationship("app.models.activity_adaptation.routine.routine.AdaptedRoutinePerformance", back_populates="student", cascade="all, delete-orphan", overlaps="student,adapted_routine_performances")
    Student.health_metrics = relationship("app.models.health_fitness.metrics.health.HealthMetric", back_populates="student", cascade="all, delete-orphan", overlaps="student,pe_health_metrics,student_health_metrics,fitness_health_metrics")
    Student.fitness_goals = relationship("app.models.health_fitness.goals.fitness_goals.FitnessGoal", back_populates="student", cascade="all, delete-orphan", overlaps="student,fitness_goals")
    Student.goal_recommendations = relationship("app.models.health_fitness.goals.fitness_goals.GoalRecommendation", back_populates="student", cascade="all, delete-orphan", overlaps="student,goal_recommendations")
    # Student.nutrition_plans = relationship("NutritionPlan", back_populates="student", cascade="all, delete-orphan", overlaps="student,nutrition_plans")
    Student.progress = relationship("Progress", back_populates="student", cascade="all, delete-orphan", overlaps="student,progress")
    Student.skill_assessment_assessments = relationship("app.models.skill_assessment.assessment.assessment.Assessment", 
                                                     # back_populates="student", 
                                                     cascade="all, delete-orphan", 
                                                     overlaps="student,skill_assessment_assessments,assessments")

def setup_safety_relationships(SafetyIncident):
    """Set up relationships for the SafetyIncident model."""
    SafetyIncident.activity = relationship("app.models.physical_education.activity.models.Activity", back_populates="safety_incidents", overlaps="activity,safety_incidents")
    SafetyIncident.student = relationship("app.models.student.Student", back_populates="safety_incidents", overlaps="student,safety_incidents")
    SafetyIncident.reporter = relationship("app.models.core.user.User", back_populates="reported_incidents", overlaps="user,reported_incidents")
    SafetyIncident.safety = relationship("app.models.physical_education.safety.models.SafetyProtocol", back_populates="incidents", overlaps="safety,incidents")

def setup_security_relationships(SecurityPolicy):
    """Set up relationships for the SecurityPolicy model."""
    SecurityPolicy.rules_rel = relationship("app.models.security.policy.security.SecurityRule", back_populates="policy", cascade="all, delete-orphan")
    SecurityPolicy.audits = relationship("app.models.security.policy.security.SecurityAudit", back_populates="policy", cascade="all, delete-orphan")

def setup_security_rule_relationships(SecurityRule):
    """Set up relationships for the SecurityRule model."""
    SecurityRule.policy = relationship("app.models.security.policy.security.SecurityPolicy", back_populates="rules_rel")
    SecurityRule.audits = relationship("app.models.security.policy.security.SecurityAudit", back_populates="rule", cascade="all, delete-orphan")

def setup_security_audit_relationships(SecurityAudit):
    """Set up relationships for the SecurityAudit model."""
    SecurityAudit.policy = relationship("app.models.security.policy.security.SecurityPolicy", back_populates="audits")
    SecurityAudit.rule = relationship("app.models.security.policy.security.SecurityRule", back_populates="audits")
    SecurityAudit.activity = relationship("app.models.physical_education.activity.models.Activity", back_populates="security_audits")
    SecurityAudit.student = relationship("app.models.student.Student", back_populates="security_audits")

def setup_security_incident_relationships(SecurityIncident):
    """Set up relationships for the SecurityIncident model."""
    SecurityIncident.activity = relationship("app.models.physical_education.activity.models.Activity", back_populates="security_incidents")
    SecurityIncident.student = relationship("app.models.student.Student", back_populates="security_incidents") 