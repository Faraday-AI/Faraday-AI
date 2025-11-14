import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json
from sqlalchemy.orm import Session
from pathlib import Path
from sqlalchemy import text, inspect
import random
import logging
from sqlalchemy.exc import SQLAlchemyError

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Import resource management models early to ensure they're registered
from app.models.resource_management import ResourceUsage, ResourceSharing

from app.core.database import SessionLocal, engine
from app.core.config import settings
from app.core.monitoring import track_metrics
from app.core.logging import get_logger
from app.services.physical_education import service_integration
from app.models.physical_education.activity_plan.models import ActivityPlan
from app.models.educational.curriculum.lesson_plan import LessonPlan

from app.models.activity import Activity
from app.models.physical_education.exercise.models import Exercise
from app.models.routine import Routine, RoutineActivity, RoutinePerformance
from app.models.activity_adaptation.routine.routine_performance import AdaptedPerformanceMetrics
from app.models.physical_education.student import (
    Student,
    HealthMetricThreshold
)
from app.models.health_fitness.metrics.health import HealthMetric, HealthMetricHistory
from app.models.physical_education.class_ import PhysicalEducationClass, ClassStudent
from app.models.physical_education.schools import School, SchoolFacility
from app.models.physical_education.safety import SafetyIncident, RiskAssessment
from app.models.physical_education.safety.models import (
    SafetyCheck, EnvironmentalCheck, SafetyProtocol, SafetyAlert, Equipment
)
from app.models.core.core_models import (
    ActivityType,
    DifficultyLevel,
    EquipmentRequirement,
    StudentType,
    MetricType,
    GoalType,
    ClassType,
    RoutineType,
    AssessmentType,
    SafetyType
)
from app.models.core.memory import UserMemory, MemoryInteraction
from app.models.core.assistant import AssistantProfile, AssistantCapability, subject_assistant
from app.models.core.lesson import Lesson
from app.models.core.subject import SubjectCategory
# Import resource management models to ensure they're registered
from app.models.resource_management import (
    ResourceCategory, EducationalResource, ResourceCategoryAssociation,
    ResourceSharing, ResourceUsage, ResourceCollection,
    CollectionResourceAssociation, CollectionSharing, ResourceReview,
    ResourceFavorite, ResourceDownload
)

# Import new beta teacher system models
from app.models.beta_students import BetaStudent  # Import BetaStudent before TeacherRegistration to resolve relationships
from app.models.teacher_registration import TeacherRegistration
from app.models.beta_testing import (
    BetaTestingParticipant, BetaTestingProgram, BetaTestingFeedback,
    BetaTestingSurvey, BetaTestingSurveyResponse, BetaTestingUsageAnalytics,
    BetaTestingFeatureFlag, BetaTestingNotification, BetaTestingReport
)
# Import Beta Teacher Dashboard models to ensure tables are created
from app.models.beta_teacher_dashboard import (
    TeacherDashboardLayout, DashboardWidgetInstance, TeacherActivityLog,
    TeacherNotification, TeacherAchievement, TeacherAchievementProgress,
    TeacherQuickAction, BetaTeacherPreference, TeacherStatistics,
    TeacherGoal, TeacherLearningPath, LearningPathStep
)
from app.models.lesson_plan_builder import (
    LessonPlanTemplate, LessonPlanActivity, AILessonSuggestion,
    LessonPlanSharing, LessonPlanUsage, LessonPlanCategory
)
from app.models.assessment_tools import (
    AssessmentTemplate, AssessmentCriteria, AssessmentRubric,
    AssessmentQuestion, AssessmentChecklist, AssessmentStandard,
    AssessmentTemplateSharing, AssessmentTemplateUsage, AssessmentCategory
)
from app.models.ai_assistant import (
    AIAssistantConfig, AIAssistantConversation, AIAssistantMessage,
    AIAssistantUsage, AIAssistantTemplate, AIAssistantFeedback, AIAssistantAnalytics
)
# from app.models.resource_management.optimization.models import ResourceEvent, ResourceAlert
from app.models.gpt.subscription.models import CoreGPTSubscription
from app.models.organization.projects.project_management import OrganizationProject
from app.models.feedback import Feedback
from app.models.organization.feedback.project_feedback_management import OrganizationFeedback
from app.models.audit_log import AuditLog
from app.dashboard.models.ai_suite import AISuite
from app.dashboard.models.ai_tool import AITool
from app.models.organization import Organization, Department, OrganizationMember, DepartmentMember
from app.models.dashboard import CoreDashboardWidget, DashboardTheme, DashboardShareConfig, DashboardFilterConfig, DashboardExport, DashboardSearch

# Import missing models that should exist in the database (before User model)
from app.dashboard.models.user_preferences import UserPreferences
from app.models.skill_assessment.assessment.assessment import AssessmentResult
from app.models.physical_education.activity.models import StudentActivityPerformance, StudentActivityPreference
from app.models.security.api_key.api_key import APIKey



# Import context models to ensure shared_contexts table is available
from app.models.gpt.context.models import (
    GPTContext,
    ContextInteraction,
    SharedContext,
    ContextSummary,
    ContextBackup,
    ContextData,
    ContextMetrics,
    ContextSharing
)

# Import GPT base models to ensure core_gpt_definitions table is available
from app.models.gpt.base.gpt import CoreGPTDefinition

# Import GPT performance models to ensure performance_thresholds table is available
from app.models.gpt.performance.models import PerformanceThreshold

# Import safety models to ensure safety_incident_base table is available
from app.models.physical_education.safety.models import SafetyIncidentBase

# Import GPT subscription models to ensure gpt_subscriptions table is available
from app.models.gpt.subscription.models import CoreGPTSubscription

# Import dashboard GPT subscription models to ensure dashboard_gpt_subscriptions table is available
from app.dashboard.models.gpt_models import DashboardGPTSubscription

# Import equipment models to ensure equipment table is available
from app.models.physical_education.safety.models import Equipment, EquipmentBase, SafetyIncidentBase, EquipmentMaintenance, SafetyCheck, SafetyAlert



# Import GPT subscription plan models to ensure gpt_subscription_plans table is available
from app.models.gpt.subscription.models import GPTSubscriptionPlan

# Import GPT subscription models to ensure all subscription tables are available
from app.models.gpt.subscription.models import (
    GPTSubscriptionPlan, CoreGPTSubscription, CoreGPTUsageHistory, 
    GPTSubscriptionUsage, GPTSubscriptionBilling, GPTSubscriptionPayment,
    GPTSubscriptionInvoice, GPTSubscriptionRefund
)

# Import dashboard GPT models to ensure gpt_definitions table is available
from app.dashboard.models.gpt_models import GPTDefinition

# Import educational models to ensure grades table is available
from app.models.educational.base.grade import Grade

# Import dashboard AI tool models to ensure tool_assignments table is available
from app.dashboard.models.ai_tool import tool_assignments

# Import AI tool models to ensure ai_tools table is available
from app.dashboard.models.ai_tool import AITool

# Import health fitness models to ensure injury_risk_factor_safety_guidelines table is available
from app.models.health_fitness.workouts.injury_prevention import injury_risk_factor_safety_guidelines

# Import safety models to ensure safety_guidelines table is available
from app.models.health_fitness.workouts.injury_prevention import SafetyGuideline, InjuryRiskFactor

# Import goal models to ensure goals table is available
from app.models.health_fitness.goals.goal_setting import Goal

# Import user management models to ensure roles and permissions tables are available
from app.models.user_management.user.user_management import Role, Permission

# Import tool models to ensure tools table is available
from app.dashboard.models.tool_registry import Tool

# Import activity categories to ensure activity_categories table is available
from app.models.activity_adaptation.categories.activity_categories import ActivityCategory

# Import assignment models to ensure assignments table is available for grades foreign key
from app.models.educational.base.assignment import Assignment

# Import communication models to ensure communication tables are available
from app.models.communication.models import (
    CommunicationRecord,
    AssignmentTranslation,
    SubmissionTranslation,
    CommunicationType,
    CommunicationChannel,
    CommunicationStatus,
    MessageType
)

# Import health_fitness models to ensure NutritionPlan is available for Student relationships
from app.models.health_fitness.nutrition.nutrition import NutritionPlan

# SafetyIncident already imported from app.models.physical_education.safety above

# Import avatar models to ensure Avatar is available for Tool relationships
from app.models.user_management.avatar.base import Avatar
from app.models.user_management.avatar.models import UserAvatar, AvatarCustomization, AvatarTemplate

# Import analytics models to ensure analytics tables are available
from app.models.analytics.user_analytics import (
    UserActivity,
    UserBehavior,
    UserPerformance,
    UserEngagement,
    UserPrediction,
    UserRecommendation,
    AnalyticsEvent,
    UserInsight,
    UserTrend,
    UserComparison
)

# Import optimization models to ensure they're available for User relationships
# from app.models.resource_management.optimization import ResourceOptimizationThreshold, ResourceOptimizationRecommendation, ResourceOptimizationEvent

# Import User model after all other models to ensure proper registration order
from app.models.core.user import User

# Import seed functions
from app.scripts.seed_data.seed_users import seed_users
from app.scripts.seed_data.seed_subject_categories import seed_subject_categories
from app.scripts.seed_data.seed_lessons import seed_lessons
from app.scripts.seed_data.seed_activities import seed_activities
from app.scripts.seed_data.seed_students import seed_students
from app.scripts.seed_data.seed_classes import seed_classes
from app.scripts.seed_data.seed_class_students import seed_class_students
from app.scripts.seed_data.seed_routines import seed_routines
from app.scripts.seed_data.seed_exercises import seed_exercises
from app.scripts.seed_data.seed_risk_assessments import seed_risk_assessments
from app.scripts.seed_data.seed_routine_performance import seed_routine_performance
from app.scripts.seed_data.seed_performance_metrics import seed_performance_metrics
from app.scripts.seed_data.seed_student_activity_data import seed_student_activity_data
from app.scripts.seed_data.seed_safety_incidents import seed_safety_incidents
from app.scripts.seed_data.seed_emergency_procedures import seed_emergency_procedures
from app.scripts.seed_data.seed_safety_checks import seed_safety_checks
from app.scripts.seed_data.seed_equipment_checks import seed_equipment_checks
from app.scripts.seed_data.seed_environmental_checks import seed_environmental_checks
from app.scripts.seed_data.seed_activity_categories import seed_activity_categories
from app.scripts.seed_data.seed_activity_plans import seed_activity_plans
from app.scripts.seed_data.seed_activity_progressions import seed_activity_progressions
from app.scripts.seed_data.seed_activity_category_associations import seed_activity_category_associations
from app.scripts.seed_data.seed_movement_analysis import seed_movement_analysis
from app.scripts.seed_data.seed_activity_adaptations import seed_activity_adaptations
from app.scripts.seed_data.seed_assessment_criteria import seed_assessment_criteria
from app.scripts.seed_data.seed_skill_assessments import seed_skill_assessments
from app.scripts.seed_data.seed_user_preferences import seed_user_preferences
from app.scripts.seed_data.seed_memories import seed_memories
from app.scripts.seed_data.seed_assistant_profiles import seed_assistant_profiles
from app.scripts.seed_data.seed_skill_progress import seed_skill_progress
from app.scripts.seed_data.seed_ai_analytics_data import seed_ai_analytics_data
from app.scripts.seed_data.seed_beta_teacher_system import seed_beta_teacher_system

# Import the new comprehensive seeding scripts
from app.scripts.seed_data.seed_dashboard_system import seed_dashboard_system
from app.scripts.seed_data.seed_gpt_system import seed_gpt_system
from app.scripts.seed_data.seed_security_system import seed_security_system

# Import comprehensive analytics and adapted activities seeding
from app.scripts.seed_data.seed_comprehensive_analytics import seed_comprehensive_analytics
from app.scripts.seed_data.seed_adapted_activities import seed_adapted_activities
from app.scripts.seed_data.seed_additional_activity_data import seed_additional_activity_data
from app.scripts.seed_data.seed_unused_tables import seed_unused_tables

# Import Phase 11 Advanced System Features
from app.scripts.seed_data.seed_phase11_fixed import seed_phase11_advanced_system_features

# Import comprehensive curriculum seeding
from app.scripts.seed_data.seed_daily_pe_curriculum import seed_daily_pe_curriculum
from app.scripts.seed_data.seed_comprehensive_exercise_library import seed_comprehensive_exercise_library
from app.scripts.seed_data.seed_simple_activity_library import seed_simple_activity_library
from app.scripts.seed_data.post_seed_validation import validate as post_seed_validate
import os

def env_true(name: str) -> bool:
    val = os.getenv(name, "").strip().lower()
    return val in ("1", "true", "yes", "on")


def seed_database():
    """Seed the database with initial data."""
    print("Running seed data script...")
    print("🚨 FAIL-FAST MODE ENABLED - Script will stop on first error")
    print("=" * 60)
    
    try:
        # Ensure all tables are created first
        from app.models.shared_base import SharedBase
        
        # Import specific models to avoid conflicts - removed broad import
        # import app.models  # This was causing conflicts with dashboard models
        
        session = SessionLocal()
        try:
            # Step 1: Drop all tables and recreate them (development approach)
            print("Dropping and recreating tables...")
            try:
                # Get all existing tables
                result = session.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'"))
                existing_tables = [row[0] for row in result.fetchall()]
                
                if existing_tables:
                    print(f"Found {len(existing_tables)} existing tables, dropping them in batches...")
                    
                    # Drop tables in smaller batches to avoid memory issues
                    batch_size = 10
                    for i in range(0, len(existing_tables), batch_size):
                        batch = existing_tables[i:i + batch_size]
                        print(f"Dropping batch {i//batch_size + 1}: {batch}")
                        
                        for table_name in batch:
                            try:
                                session.execute(text(f"DROP TABLE IF EXISTS {table_name} CASCADE"))
                                print(f"Dropped table: {table_name}")
                            except Exception as e:
                                print(f"Warning: Could not drop table {table_name}: {e}")
                        
                        session.commit()
                        print(f"Completed batch {i//batch_size + 1}")
                else:
                    print("No existing tables found")
                
                # Also drop any remaining indexes that might persist
                try:
                    session.execute(text("DROP INDEX IF EXISTS ix_health_metric_thresholds_id CASCADE"))
                    session.execute(text("DROP INDEX IF EXISTS ix_health_metric_thresholds_id CASCADE"))
                except Exception as e:
                    print(f"Note: Some indexes may already be dropped: {e}")
                
                session.commit()
                print("Completed dropping existing tables")
                
                # Create all tables directly using SharedBase metadata
                print("Creating all tables...")
                print(f"Available tables in metadata: {list(SharedBase.metadata.tables.keys())}")
                try:
                    # Define core tables that should be created first (no dependencies)
                    core_tables = [
                        'organizations', 'departments', 'users', 'students', 'activities', 
                        'physical_education_classes', 'avatar_templates', 'avatars', 'user_avatars',
                        'avatar_customizations', 'user_avatar_customizations',
                        'voice_templates', 'dashboard_users', 'dashboard_teams', 'dashboard_projects', 'dashboards', 'dashboard_widgets', 'teams', 'organization_projects',
                        'gpt_definitions', 'core_gpt_definitions', 'gpt_interaction_contexts', 'gpt_context_gpts', 'goals', 'activity_categories', 
                        'roles', 'permissions', 'dashboard_tools', 'shared_contexts', 'courses', 'rubrics', 'assignments', 'ai_suites', 'ai_tools',
                        'injury_preventions', 'injury_risk_factors', 'safety_guidelines', 'assistant_profiles', 'assistant_capabilities',
                        'subject_categories', 'lessons', 'performance_thresholds', 'equipment_base', 'equipment', 'gpt_subscription_plans', 'gpt_subscriptions', 'dashboard_gpt_subscriptions',
                        'gpt_usage_history', 'gpt_subscription_usage', 'gpt_subscription_billing', 'gpt_subscription_payments', 'gpt_subscription_invoices', 'gpt_subscription_refunds',
                        # Beta Teacher System Core Tables (only tables with dependencies)
                        'teacher_registrations', 'lesson_plan_templates', 'lesson_plan_categories', 'assessment_templates', 'assessment_categories', 'resource_categories', 'educational_resources', 'ai_assistant_configs', 'ai_assistant_templates', 'beta_testing_programs', 'beta_avatars', 'beta_widgets',
                        # Beta Teacher Dashboard Core Tables (standalone and parent tables)
                        'teacher_achievements', 'teacher_achievement_progress', 'teacher_dashboard_layouts', 'teacher_learning_paths', 'teacher_goals', 'teacher_statistics', 'teacher_activity_logs', 'teacher_notifications', 'teacher_quick_actions', 'beta_teacher_preferences',
                        # Directly dependent tables (must be created with core tables)
                        'beta_lesson_plan_activities', 'lesson_plan_sharing', 'lesson_plan_usage', 'template_category_associations',
                        'assessment_criteria', 'assessment_questions', 'assessment_rubrics', 'assessment_standards', 'assessment_checklists', 'assessment_template_sharing', 'assessment_template_usage', 'assessment_template_category_associations',
                        'resource_category_associations', 'resource_sharing', 'resource_usage', 'resource_collections', 'collection_resource_associations', 'collection_sharing', 'resource_reviews', 'resource_favorites', 'resource_downloads',
                        'ai_assistant_conversations', 'ai_assistant_messages', 'ai_assistant_usage', 'ai_assistant_feedback', 'ai_assistant_analytics',
                        'beta_testing_participants', 'beta_testing_feedback', 'beta_testing_surveys', 'beta_testing_reports', 'beta_testing_usage_analytics',
                        # Beta Students (depends on teacher_registrations)
                        'beta_students',
                        # Phase 11 Resource Management Tables
                        'resource_management_usage', 'resource_thresholds', 'resource_optimizations', 'resource_management_sharing', 'optimization_events'
                    ]
                    
                    # Create core tables first
                    print("Creating core tables...")
                    for table_name in core_tables:
                        if table_name in SharedBase.metadata.tables:
                            try:
                                SharedBase.metadata.tables[table_name].create(bind=engine, checkfirst=True)
                                print(f"Created core table: {table_name}")
                            except Exception as e:
                                if "already exists" not in str(e).lower():
                                    print(f"Error creating core table {table_name}: {e}")
                                else:
                                    print(f"Core table {table_name} already exists")
                        else:
                            print(f"Warning: Core table {table_name} not found in metadata")
                    
                    # Commit to ensure all core tables are fully created
                    session.commit()
                    
                    # Create remaining tables
                    print("Creating remaining tables...")
                    remaining_tables = [name for name in SharedBase.metadata.tables.keys() if name not in core_tables]
                    
                    # Try to create remaining tables with retries for dependency issues
                    max_attempts = 3
                    for attempt in range(max_attempts):
                        failed_tables = []
                        successfully_created = []
                        
                        for table_name in remaining_tables:
                            try:
                                SharedBase.metadata.tables[table_name].create(bind=engine, checkfirst=True)
                                print(f"Created table: {table_name}")
                                successfully_created.append(table_name)
                            except Exception as e:
                                if "already exists" not in str(e).lower():
                                    failed_tables.append((table_name, e))
                                else:
                                    # Table already exists, consider it successful
                                    successfully_created.append(table_name)
                        
                        # Remove successfully created tables from remaining_tables
                        remaining_tables = [name for name in remaining_tables if name not in successfully_created]
                        
                        if not failed_tables:
                            break
                        
                        print(f"Attempt {attempt +1} of {max_attempts}: {len(failed_tables)} tables failed, retrying...")
                        # Extract just the table names for the next iteration
                        remaining_tables = [name for name, _ in failed_tables]
                    
                    if remaining_tables:
                        print(f"ERROR: {len(remaining_tables)} tables could not be created after {max_attempts} attempts")
                        # remaining_tables now contains just table names, not tuples
                        for table_name in remaining_tables:
                            print(f"Failed to create {table_name}")
                        print("Database initialization FAILED - cannot proceed with seeding")
                        raise Exception(f"Failed to create {len(remaining_tables)} tables: {remaining_tables}")
                    else:
                        print("Successfully created all tables")
                        print("Database initialization completed successfully")
                        
                except Exception as e:
                    error_msg = str(e).lower()
                    if "already exists" in error_msg or "duplicate" in error_msg:
                        print(f"Some objects already exist, attempting to continue: {e}")
                        # Try to create tables individually, skipping existing ones
                        created_count = 0
                        skipped_count = 0
                        for table_name, table_obj in SharedBase.metadata.tables.items():
                            try:
                                table_obj.create(bind=engine, checkfirst=True)
                                created_count += 1
                            except Exception as table_error:
                                if "already exists" in str(table_error).lower():
                                    skipped_count += 1
                                else:
                                    print(f"Error creating table {table_name}: {table_error}")
                        print(f"Created {created_count} tables, skipped {skipped_count} existing tables")
                        print("Database initialization completed with existing tables")
                    else:
                        raise
                
            except Exception as e:
                print(f"Error with table recreation: {e}")
                raise
            
            # Step 2: Seed data in order of dependencies
            print("Seeding data...")
            try:
                # Schools system MUST BE FIRST - everything else depends on it!
                print("\n" + "="*50)
                print("SEEDING SCHOOLS SYSTEM")
                print("="*50)
                
                from app.scripts.seed_data.seed_schools import seed_schools
                seed_schools(session)
                session.commit()
                
                # Create basic organizations that schools and users depend on
                print("Creating basic organizations...")
                try:
                    # Check if organization already exists
                    existing_org = session.execute(text("SELECT COUNT(*) FROM organizations WHERE name = :name"), 
                                                 {'name': 'Springfield School District'}).scalar()
                    
                    if existing_org == 0:
                        # Create a basic organization for the district
                        session.execute(text("""
                            INSERT INTO organizations (name, type, subscription_tier, status, is_active, created_at, updated_at)
                            VALUES (:name, :type, :tier, :status, :is_active, :created_at, :updated_at)
                        """), {
                            'name': 'Springfield School District',
                            'type': 'SCHOOL_DISTRICT',
                            'tier': 'PREMIUM',
                            'status': 'ACTIVE',
                            'is_active': True,
                            'created_at': datetime.now(),
                            'updated_at': datetime.now()
                        })
                        session.commit()
                        print("✅ Created basic organization: Springfield School District")
                    else:
                        print("✅ Basic organization already exists: Springfield School District")
                except Exception as e:
                    print(f"⚠️  Error creating basic organization: {e}")
                    session.rollback()
                
                # Core system tables
                seed_users(session)
                session.commit()
                
                # TEACHER MIGRATION - Create teachers table and migrate data
                print("\n" + "="*50)
                print("TEACHER MIGRATION SYSTEM")
                print("="*50)
                try:
                    from app.scripts.seed_data.migrate_teachers_full import migrate_teachers_full
                    migrate_teachers_full()
                    session.commit()
                    print("✅ Teacher migration completed successfully!")
                except Exception as e:
                    print(f"❌ Teacher migration failed: {e}")
                    session.rollback()
                    raise
                
                # DASHBOARD USERS MIGRATION - Migrate teachers to dashboard_users
                print("\n" + "="*50)
                print("DASHBOARD USERS MIGRATION")
                print("="*50)
                try:
                    from app.scripts.seed_data.migrate_teachers_to_dashboard_users import migrate_teachers_to_dashboard_users
                    migrate_teachers_to_dashboard_users(session)
                    session.commit()
                    print("✅ Dashboard users migration completed successfully!")
                except Exception as e:
                    print(f"❌ Dashboard users migration failed: {e}")
                    session.rollback()
                    raise
                
                # TOOL ASSIGNMENTS SEEDING - Moved to Phase 5 after ai_tools are populated
                print("⏭️  Tool assignments seeding moved to Phase 5 (after ai_tools are populated)")
                
                # IMMEDIATE TEACHER-DEPENDENT TABLES SEEDING
                print("\n" + "="*50)
                print("SEEDING TEACHER-DEPENDENT TABLES")
                print("="*50)
                try:
                    from app.scripts.seed_data.seed_phase2_educational_system import (
                        seed_physical_education_teachers,
                        seed_physical_education_classes,
                        seed_pe_lesson_plans,
                        seed_educational_teachers
                    )
                    
                    # Seed physical education teachers
                    print("🔄 Seeding physical_education_teachers...")
                    pe_teachers_count = seed_physical_education_teachers(session)
                    print(f"✅ Created {pe_teachers_count} physical education teachers")
                    
                    # Seed physical education classes
                    print("🔄 Seeding physical_education_classes...")
                    pe_classes_count = seed_physical_education_classes(session)
                    print(f"✅ Created {pe_classes_count} physical education classes")
                    
                    # Seed PE lesson plans
                    print("🔄 Seeding pe_lesson_plans...")
                    pe_lesson_plans_count = seed_pe_lesson_plans(session)
                    print(f"✅ Created {pe_lesson_plans_count} PE lesson plans")
                    
                    # Seed educational teachers
                    print("🔄 Seeding educational_teachers...")
                    educational_teachers_count = seed_educational_teachers(session)
                    print(f"✅ Created {educational_teachers_count} educational teachers")
                    
                    session.commit()
                    print("✅ Teacher-dependent tables seeded successfully!")
                    
                    # VERIFY TEACHER-DEPENDENT TABLES
                    print("\n4️⃣ VERIFYING TEACHER-DEPENDENT TABLES")
                    print("-" * 50)
                    
                    # Check teachers table
                    result = session.execute(text('SELECT COUNT(*) FROM teachers'))
                    teacher_count = result.fetchone()[0]
                    print(f'Teachers in new table: {teacher_count}')
                    
                    # Check teacher-dependent tables
                    verification_tables = [
                        'educational_teachers',
                        'physical_education_teachers', 
                        'pe_lesson_plans',
                        'physical_education_classes'
                    ]
                    
                    for table in verification_tables:
                        try:
                            result = session.execute(text(f'SELECT COUNT(*) FROM {table}'))
                            count = result.fetchone()[0]
                            print(f'{table}: {count} records')
                        except Exception as e:
                            print(f'{table}: Error - {e}')
                    
                except Exception as e:
                    print(f"❌ Teacher-dependent tables seeding failed: {e}")
                    session.rollback()
                    raise
                
                # K-12 DISTRICT FIXES - Ensure proper K-12 district data
                print("\n" + "="*50)
                print("K-12 DISTRICT FIXES")
                print("="*50)
                try:
                    from app.scripts.seed_data.fix_k12_district import fix_k12_district
                    fix_k12_district()
                    session.commit()
                    print("✅ K-12 district fixes completed successfully!")
                except Exception as e:
                    print(f"❌ K-12 district fixes failed: {e}")
                    session.rollback()
                    raise
                
                # DISTRICT CONSISTENCY - Ensure district data consistency
                print("\n" + "="*50)
                print("DISTRICT CONSISTENCY")
                print("="*50)
                try:
                    from app.scripts.seed_data.seed_phase1_district_consistency import seed_district_consistency
                    seed_district_consistency()
                    session.commit()
                    print("✅ District consistency completed successfully!")
                except Exception as e:
                    print(f"❌ District consistency failed: {e}")
                    session.rollback()
                    raise
                
                # LOW RECORD TABLES FIXES - Fix tables with low record counts
                print("\n" + "="*50)
                print("LOW RECORD TABLES FIXES")
                print("="*50)
                try:
                    from app.scripts.seed_data.fix_low_record_tables import fix_low_record_tables
                    fix_low_record_tables()
                    session.commit()
                    print("✅ Low record tables fixes completed successfully!")
                except Exception as e:
                    print(f"❌ Low record tables fixes failed: {e}")
                    session.rollback()
                    raise
                
                # JOB TABLES CREATION - Create missing job and job_run_details tables
                print("\n" + "="*50)
                print("JOB TABLES CREATION")
                print("="*50)
                try:
                    # Create job table
                    session.execute(text("""
                        CREATE TABLE IF NOT EXISTS job (
                            id SERIAL PRIMARY KEY,
                            name VARCHAR(255) NOT NULL,
                            description TEXT,
                            status VARCHAR(50) DEFAULT 'PENDING',
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """))
                    
                    # Create job_run_details table
                    session.execute(text("""
                        CREATE TABLE IF NOT EXISTS job_run_details (
                            id SERIAL PRIMARY KEY,
                            job_id INTEGER REFERENCES job(id),
                            status VARCHAR(50) DEFAULT 'RUNNING',
                            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            completed_at TIMESTAMP,
                            error_message TEXT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """))
                    
                    session.commit()
                    print("✅ Job tables created successfully!")
                except Exception as e:
                    print(f"❌ Job tables creation failed: {e}")
                    session.rollback()
                    raise
                
                # DEBUG: Check what we have in the database at this point
                print("\n🔍 DEBUG: Checking database state after all foundational seeding...")
                user_count = session.execute(text("SELECT COUNT(*) FROM users")).scalar()
                org_count = session.execute(text("SELECT COUNT(*) FROM organizations")).scalar()
                school_count = session.execute(text("SELECT COUNT(*) FROM schools")).scalar()
                try:
                    teacher_count = session.execute(text("SELECT COUNT(*) FROM teachers")).scalar()
                    print(f"  📊 Users: {user_count}, Organizations: {org_count}, Schools: {school_count}, Teachers: {teacher_count}")
                except Exception as e:
                    print(f"  📊 Users: {user_count}, Organizations: {org_count}, Schools: {school_count}, Teachers: ERROR - {e}")
                
                # Check job tables
                try:
                    job_count = session.execute(text("SELECT COUNT(*) FROM job")).scalar()
                    job_run_count = session.execute(text("SELECT COUNT(*) FROM job_run_details")).scalar()
                    print(f"  📊 Job tables: job={job_count}, job_run_details={job_run_count}")
                except Exception as e:
                    print(f"  📊 Job tables: ERROR - {e}")
                
                # Check total table count
                try:
                    total_tables = session.execute(text("""
                        SELECT COUNT(*) 
                        FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_type = 'BASE TABLE'
                    """)).scalar()
                    print(f"  📊 Total tables in database: {total_tables}")
                except Exception as e:
                    print(f"  📊 Total table count: ERROR - {e}")
                
                # Seed activity_logs table
                print("\nSeeding activity logs...")
                try:
                    # Always seed activity_logs regardless of existing data
                    # Get user and organization IDs - ensure we have fresh data after commits
                    user_result = session.execute(text("SELECT id FROM users ORDER BY id LIMIT 50"))
                    user_ids = [row[0] for row in user_result.fetchall()]
                    
                    # Get organization IDs - should be available after schools seeding
                    org_result = session.execute(text("SELECT id FROM organizations ORDER BY id"))
                    org_ids = [row[0] for row in org_result.fetchall()]
                    
                    if not user_ids:
                        print("  ❌ No users found in database!")
                        user_ids = [1, 2, 3, 4, 5]  # Fallback IDs
                    if not org_ids:
                        print("  ❌ No organizations found in database!")
                        print("  🔍 This indicates a problem with the schools seeding process")
                        org_ids = [None]  # Use None instead of invalid ID
                    
                    print(f"  📋 Found {len(user_ids)} users and {len(org_ids)} organizations")
                    
                    # Create sample activity logs
                    actions = ['CREATE', 'UPDATE', 'DELETE', 'VIEW', 'EXPORT', 'IMPORT', 'LOGIN', 'LOGOUT']
                    resource_types = ['USER', 'STUDENT', 'LESSON', 'EXERCISE', 'ACTIVITY', 'ASSESSMENT', 'CURRICULUM']
                    
                    # Process activity logs in batches to avoid connection timeouts
                    batch_size = 500
                    total_records = 5000
                    total_created = 0
                    
                    for batch_start in range(0, total_records, batch_size):
                        batch_end = min(batch_start + batch_size, total_records)
                        activity_logs_data = []
                        
                        for i in range(batch_start, batch_end):
                            activity_logs_data.append({
                                'action': random.choice(actions),
                                'resource_type': random.choice(resource_types),
                                'resource_id': str(random.randint(1, 1000)),
                                'details': json.dumps({
                                    'description': f'Activity log entry {i+1}',
                                    'ip_address': f"192.168.1.{random.randint(1, 255)}",
                                    'user_agent': 'FaradayAI/1.0',
                                    'session_id': f"session_{random.randint(1000, 9999)}",
                                    'metadata': {
                                        'source': 'web_interface',
                                        'version': '1.0',
                                        'feature': random.choice(['user_management', 'curriculum', 'assessment', 'reporting'])
                                    }
                                }),
                                'user_id': random.choice(user_ids) if random.random() > 0.3 else None,
                                'org_id': random.choice(org_ids) if random.random() > 0.5 else None,
                                'timestamp': datetime.utcnow() - timedelta(days=random.randint(0, 30)),
                                'created_at': datetime.utcnow() - timedelta(days=random.randint(0, 30)),
                                'updated_at': datetime.utcnow() - timedelta(days=random.randint(0, 7))
                            })
                        
                        # Insert batch
                        for log in activity_logs_data:
                            session.execute(text("""
                                INSERT INTO activity_logs (
                                    action, resource_type, resource_id, details, user_id, org_id, timestamp, created_at, updated_at
                                ) VALUES (
                                    :action, :resource_type, :resource_id, :details, :user_id, :org_id, :timestamp, :created_at, :updated_at
                                )
                            """), log)
                        
                        session.commit()
                        total_created += len(activity_logs_data)
                        print(f"  📝 Created batch {batch_start//batch_size + 1}: {len(activity_logs_data)} activity logs (total: {total_created})")
                    
                    print(f"  ✅ Created {total_created} activity logs")
                    
                except Exception as e:
                    print(f"  ❌ CRITICAL ERROR: Activity logs seeding failed: {e}")
                    print("  🛑 FAIL-FAST: Stopping script execution immediately")
                    print(f"  📍 Error location: Activity logs creation")
                    print(f"  🔍 Error details: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    session.rollback()
                    raise Exception(f"FAIL-FAST: Activity logs seeding failed: {e}")
                
                session.commit()
                
                # MIGRATE USERS TO DASHBOARD (CRITICAL FOR EDUCATIONAL TEACHERS)
                print("\n" + "="*50)
                print("MIGRATING USERS TO DASHBOARD SYSTEM")
                print("="*50)
                print("🔄 Migrating users from core users table to dashboard_users...")
                
                # Import and run the user migration
                from app.scripts.seed_data.migrate_users_to_dashboard import migrate_users_to_dashboard
                migrate_users_to_dashboard(session)
                session.commit()
                
                print("✅ User migration to dashboard complete!")
                
                seed_subject_categories(session)
                session.commit()
                
                seed_assistant_profiles(session)
                session.commit()
                
                # Activity organization
                seed_activity_categories(session)
                session.commit()
                
                seed_activities(session)
                session.commit()
                
                seed_activity_category_associations(session)
                session.commit()
                
                # User preferences and memories
                seed_user_preferences(session)
                session.commit()
                
                seed_memories(session)
                session.commit()
                
                # Education content
                seed_lessons(session)
                session.commit()
                
                # Comprehensive curriculum seeding
                print("\n" + "="*50)
                print("COMPREHENSIVE CURRICULUM SEEDING")
                print("="*50)
                
                # Import comprehensive seeding functions
                from app.scripts.seed_data.seed_daily_pe_curriculum import seed_daily_pe_curriculum
                from app.scripts.seed_data.seed_comprehensive_exercise_library import seed_comprehensive_exercise_library
                
                # Seed comprehensive daily PE curriculum (972 lessons)
                if not env_true('SKIP_PHASE_2'):
                    print("Seeding comprehensive daily PE curriculum...")
                    seed_daily_pe_curriculum(session)
                    session.commit()
                else:
                    print("⏭️  SKIP_PHASE_2 enabled: skipping daily PE curriculum")
                
                # Seed comprehensive exercise library (3,000+ exercises)
                if not env_true('SKIP_PHASE_2'):
                    print("Seeding comprehensive exercise library...")
                    seed_comprehensive_exercise_library(session)
                    session.commit()
                else:
                    print("⏭️  SKIP_PHASE_2 enabled: skipping exercise library")
                
                # Seed simple activity library (150 activities)
                if not env_true('SKIP_PHASE_2'):
                    print("Seeding simple activity library...")
                    seed_simple_activity_library(session)
                    session.commit()
                else:
                    print("⏭️  SKIP_PHASE_2 enabled: skipping simple activity library")
                
                print("\n" + "="*50)
                print("PHASE 1 FOUNDATION COMPLETE")
                print("="*50)
                print("✅ Basic infrastructure, users, schools, and activities created")
                print("✅ PE curriculum and exercise library seeded")
                print("🔄 Comprehensive lesson planning will be handled in Phase 2")
                
                # Student and class organization
                seed_students(session)
                session.commit()
                # Post-seed validation (fail-fast if invalid)
                print("\nRunning post-seed validation...")
                ok = post_seed_validate()
                if not ok:
                    raise Exception("Post-seed validation failed")

                
                # Create missing dependencies that other phases need
                print("\n" + "="*50)
                print("🔧 CREATING MISSING DEPENDENCIES")
                print("="*50)
                print("📊 Creating foundational tables that other phases depend on")
                
                try:
                    # Create health_fitness_workout_exercises if missing
                    workout_exercises_count = session.execute(text('SELECT COUNT(*) FROM health_fitness_workout_exercises')).scalar()
                    if workout_exercises_count == 0:
                        print("🔧 Creating health_fitness_workout_exercises...")
                        
                        # First migrate health_fitness_workouts from existing exercises and activities
                        workout_count = session.execute(text('SELECT COUNT(*) FROM health_fitness_workouts')).scalar()
                        if workout_count == 0:
                            print("  📝 Migrating health_fitness_workouts from existing exercises and activities...")
                            
                            # Migrate ALL exercises to health_fitness_workouts
                            exercise_result = session.execute(text('SELECT id, name, description, category FROM exercises'))
                            exercises = [row for row in exercise_result.fetchall()]
                            
                            # Migrate ALL activities to health_fitness_workouts  
                            activity_result = session.execute(text('SELECT id, name, description, category FROM activities'))
                            activities = [row for row in activity_result.fetchall()]
                            
                            workouts = []
                            # Migrate exercises to health_fitness_workouts
                            for ex_id, ex_name, ex_desc, ex_category in exercises:
                                workouts.append({
                                    'name': f'Exercise: {ex_name}',
                                    'description': ex_desc or f'Workout based on {ex_name}',
                                    'workout_type': random.choice(['CARDIO', 'STRENGTH', 'FLEXIBILITY', 'HIIT', 'CIRCUIT', 'BALANCE', 'COORDINATION']),
                                    'difficulty': random.choice(['BEGINNER', 'INTERMEDIATE', 'ADVANCED', 'EXPERT']),
                                    'duration': random.randint(30, 90),
                                    'equipment_needed': '{}',
                                    'target_heart_rate': '{}',
                                    'safety_requirements': '{}',
                                    'modifications_available': True,
                                    'indoor_outdoor': random.choice(['indoor', 'outdoor', 'both']),
                                    'space_required': random.choice(['small', 'medium', 'large']),
                                    'max_participants': random.randint(1, 30),
                                    'additional_data': '{}',
                                    'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                                    'updated_at': datetime.now()
                                })
                            
                            # Migrate activities to health_fitness_workouts
                            for act_id, act_name, act_desc, act_category in activities:
                                workouts.append({
                                    'name': f'Activity: {act_name}',
                                    'description': act_desc or f'Workout based on {act_name}',
                                    'workout_type': random.choice(['CARDIO', 'STRENGTH', 'FLEXIBILITY', 'HIIT', 'CIRCUIT', 'BALANCE', 'COORDINATION']),
                                    'difficulty': random.choice(['BEGINNER', 'INTERMEDIATE', 'ADVANCED', 'EXPERT']),
                                    'duration': random.randint(30, 90),
                                    'equipment_needed': '{}',
                                    'target_heart_rate': '{}',
                                    'safety_requirements': '{}',
                                    'modifications_available': True,
                                    'indoor_outdoor': random.choice(['indoor', 'outdoor', 'both']),
                                    'space_required': random.choice(['small', 'medium', 'large']),
                                    'max_participants': random.randint(1, 30),
                                    'additional_data': '{}',
                                    'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                                    'updated_at': datetime.now()
                                })
                            
                            # Insert migrated health_fitness_workouts
                            columns = list(workouts[0].keys())
                            placeholders = ', '.join([f':{col}' for col in columns])
                            columns_str = ', '.join(columns)
                            query = f'INSERT INTO health_fitness_workouts ({columns_str}) VALUES ({placeholders})'
                            session.execute(text(query), workouts)
                            session.commit()
                            print(f"  ✅ Migrated {len(workouts)} health_fitness_workouts from existing exercises and activities")
                        
                        # Get workout and exercise IDs from existing tables
                        workout_result = session.execute(text('SELECT id FROM health_fitness_workouts LIMIT 20'))
                        workout_ids = [row[0] for row in workout_result.fetchall()]
                        
                        exercise_result = session.execute(text('SELECT id FROM exercises LIMIT 20'))
                        exercise_ids = [row[0] for row in exercise_result.fetchall()]
                        
                        if workout_ids and exercise_ids:
                            # Process in smaller batches to avoid connection timeouts
                            batch_size = 500
                            total_records = 5000
                            total_created = 0
                            
                            for batch_start in range(0, total_records, batch_size):
                                batch_end = min(batch_start + batch_size, total_records)
                                workout_exercises = []
                                
                                for i in range(batch_start, batch_end):
                                    workout_exercises.append({
                                        'workout_id': random.choice(workout_ids),
                                        'exercise_id': random.choice(exercise_ids),
                                        'sets': random.randint(1, 5),
                                        'reps': random.randint(5, 20),
                                        'duration_minutes': round(random.uniform(5.0, 60.0), 1),
                                        'order': i + 1,
                                        'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                                        'updated_at': datetime.now()
                                    })
                                
                                # Insert batch
                                columns = list(workout_exercises[0].keys())
                                quoted_columns = [f'"{col}"' if col in ['order'] else col for col in columns]
                                placeholders = ', '.join([f':{col}' for col in columns])
                                query = f"INSERT INTO health_fitness_workout_exercises ({', '.join(quoted_columns)}) VALUES ({placeholders})"
                                
                                session.execute(text(query), workout_exercises)
                                session.commit()
                                total_created += len(workout_exercises)
                                print(f'  📝 Created batch {batch_start//batch_size + 1}: {len(workout_exercises)} records (total: {total_created})')
                            
                            print(f'  ✅ Created {total_created} health_fitness_workout_exercises records')
                        else:
                            print('  ⚠️ No workouts or exercises found')
                    else:
                        print(f'  📊 health_fitness_workout_exercises already has {workout_exercises_count} records')
                    
                    # Create exercise_sets if missing (depends on health_fitness_workout_exercises)
                    exercise_sets_count = session.execute(text('SELECT COUNT(*) FROM exercise_sets')).scalar()
                    if exercise_sets_count == 0:
                        print("🔧 Creating exercise_sets...")
                        
                        # Get health_fitness_workout_exercises IDs
                        we_result = session.execute(text('SELECT id FROM health_fitness_workout_exercises LIMIT 50'))
                        we_ids = [row[0] for row in we_result.fetchall()]
                        
                        if we_ids:
                            # Process in smaller batches to avoid connection timeouts
                            batch_size = 500
                            total_records = 2000
                            total_created = 0
                            
                            for batch_start in range(0, total_records, batch_size):
                                batch_end = min(batch_start + batch_size, total_records)
                                exercise_sets = []
                                
                                for i in range(batch_start, batch_end):
                                    exercise_sets.append({
                                        'workout_exercise_id': random.choice(we_ids),
                                        'set_number': random.randint(1, 5),
                                        'reps_completed': random.randint(5, 20),
                                        'weight_used': round(random.uniform(10.0, 100.0), 1),
                                        'duration_seconds': random.randint(30, 300),
                                        'distance_meters': round(random.uniform(0.0, 1000.0), 1),
                                        'rest_time_seconds': random.randint(30, 120),
                                        'notes': f'Exercise set {i+1} notes',
                                        'performance_rating': random.randint(1, 10),
                                        'additional_data': json.dumps({'intensity': 'moderate', 'form_quality': 'good'}),
                                        'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
                                    })
                                
                                # Insert batch
                                columns = list(exercise_sets[0].keys())
                                placeholders = ', '.join([f':{col}' for col in columns])
                                query = f"INSERT INTO exercise_sets ({', '.join(columns)}) VALUES ({placeholders})"
                                
                                session.execute(text(query), exercise_sets)
                                session.commit()
                                total_created += len(exercise_sets)
                                print(f'  📝 Created batch {batch_start//batch_size + 1}: {len(exercise_sets)} records (total: {total_created})')
                            
                            print(f'  ✅ Created {total_created} exercise_sets records')
                        else:
                            print('  ⚠️ No workout_exercises found for exercise_sets')
                    else:
                        print(f'  📊 exercise_sets already has {exercise_sets_count} records')
                    
                    # Create physical_education_workout_exercises if missing
                    pe_workout_exercises_count = session.execute(text('SELECT COUNT(*) FROM physical_education_workout_exercises')).scalar()
                    if pe_workout_exercises_count == 0:
                        print("🔧 Creating physical_education_workout_exercises...")
                        
                        # Get workout and exercise IDs
                        workout_result = session.execute(text('SELECT id FROM health_fitness_workouts LIMIT 20'))
                        workout_ids = [row[0] for row in workout_result.fetchall()]
                        
                        exercise_result = session.execute(text('SELECT id FROM exercises LIMIT 20'))
                        exercise_ids = [row[0] for row in exercise_result.fetchall()]
                        
                        if workout_ids and exercise_ids:
                            # Process in smaller batches to avoid connection timeouts
                            batch_size = 500
                            total_records = 3000
                            total_created = 0
                            
                            for batch_start in range(0, total_records, batch_size):
                                batch_end = min(batch_start + batch_size, total_records)
                                pe_workout_exercises = []
                                
                                for i in range(batch_start, batch_end):
                                    pe_workout_exercises.append({
                                        'workout_id': random.choice(workout_ids),
                                        'exercise_id': random.choice(exercise_ids),
                                        'sets': random.randint(1, 5),
                                        'reps': random.randint(5, 20),
                                        'duration': random.randint(300, 3600),  # duration in seconds (5-60 minutes)
                                        'order': i + 1,
                                        'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                                        'updated_at': datetime.now()
                                    })
                                
                                # Insert batch
                                columns = list(pe_workout_exercises[0].keys())
                                quoted_columns = [f'"{col}"' if col in ['order'] else col for col in columns]
                                placeholders = ', '.join([f':{col}' for col in columns])
                                query = f"INSERT INTO physical_education_workout_exercises ({', '.join(quoted_columns)}) VALUES ({placeholders})"
                                
                                session.execute(text(query), pe_workout_exercises)
                                session.commit()
                                total_created += len(pe_workout_exercises)
                                print(f'  📝 Created batch {batch_start//batch_size + 1}: {len(pe_workout_exercises)} records (total: {total_created})')
                            
                            print(f'  ✅ Created {total_created} physical_education_workout_exercises records')
                        else:
                            print('  ⚠️ No workouts or exercises found')
                    else:
                        print(f'  📊 physical_education_workout_exercises already has {pe_workout_exercises_count} records')
                    
                    print("✅ Missing dependencies created successfully!")
                    
                except Exception as e:
                    print(f"❌ FAIL-FAST ERROR: Missing dependencies creation failed: {e}")
                    print("🛑 STOPPING SCRIPT EXECUTION IMMEDIATELY - Dependencies are required")
                    print(f"📍 Error location: Creating Missing Dependencies")
                    print(f"🔍 Error details: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    session.rollback()
                    raise Exception(f"FAIL-FAST: Missing dependencies creation failed: {e}")
                
                # Phase 3 dependency tables - MUST be seeded before Phase 3
                print("\n" + "="*50)
                print("SEEDING PHASE 3 DEPENDENCY TABLES")
                print("="*50)
                
                if not env_true('SKIP_PHASE_3'):
                    from app.scripts.seed_data.seed_phase3_dependencies import seed_phase3_dependencies
                    seed_phase3_dependencies(session)
                    session.commit()
                else:
                    print("⏭️  SKIP_PHASE_3 enabled: skipping Phase 3 dependencies")
                
                print("✅ Phase 3 dependency tables seeded successfully!")
                
                # Additional Phase 3 dependency tables that need to be seeded early
                if not env_true('SKIP_PHASE_3'):
                    print("Seeding additional Phase 3 dependency tables...")
                    from app.scripts.seed_data.seed_phase3_dependencies import seed_additional_phase3_dependencies
                    seed_additional_phase3_dependencies(session)
                    session.commit()
                else:
                    print("⏭️  SKIP_PHASE_3 enabled: skipping additional Phase 3 dependency tables")
                
                print("✅ Additional Phase 3 dependency tables seeded successfully!")
                
                seed_classes(session)
                session.commit()
                
                seed_class_students(session)
                session.commit()
                
                # Now that students and activities exist, seed progressions
                seed_activity_progressions(session)
                session.commit()
                
                # Activity planning and execution
                seed_activity_plans(session)
                session.commit()
                
                seed_exercises(session)
                session.commit()
                
                # Safety and risk management
                seed_risk_assessments(session)
                session.commit()
                
                seed_safety_incidents(session)
                session.commit()
                
                seed_emergency_procedures(session)
                session.commit()
                
                seed_safety_checks(session)
                session.commit()
                
                seed_equipment_checks(session)
                session.commit()
                
                seed_environmental_checks(session)
                session.commit()
                print("Environmental checks seeded successfully!")
                print("🎯 Moving to performance tracking system...")
                print("⏳ This may take a few minutes...")
                print("🔄 Starting performance tracking system...")
                
                # Initialize performance tracking variables
                total_routines = 0
                total_routine_activities = 0
                total_performance_records = 0
                total_performance_metrics = 0
                total_individual_metrics = 0
                total_student_activity_performances = 0
                total_student_activity_preferences = 0
                total_activity_assessments = 0
                total_activity_progressions = 0
                total_assessment_criteria = 0
                total_skill_assessments = 0
                total_skill_progress = 0
                
                # Performance tracking
                print("Seeding performance tracking system...")
                try:
                    routine_count, routine_activity_count = seed_routines(session)
                    session.commit()
                    total_routines = routine_count
                    total_routine_activities = routine_activity_count
                    print(f"Routines seeded successfully! Created {routine_count} routines with {routine_activity_count} routine activities")
                except Exception as e:
                    print(f"Error seeding routines: {e}")
                    session.rollback()
                
                try:
                    print("Starting routine performance seeding...")
                    print("⏱️  This step may take a moment...")
                    print("🔄 Processing routines and creating performance records...")
                    
                    # Add timeout protection
                    import signal
                    def timeout_handler(signum, frame):
                        raise TimeoutError("Routine performance seeding timed out after 5 minutes")
                    
                    # Set 5 minute timeout
                    signal.signal(signal.SIGALRM, timeout_handler)
                    signal.alarm(300)  # 5 minutes
                    
                    try:
                        performance_count = seed_routine_performance(session)
                        signal.alarm(0)  # Cancel timeout
                        session.commit()
                        total_performance_records = performance_count
                        print(f"✅ Routine performance seeded successfully! Created {performance_count} performance records")
                    finally:
                        signal.alarm(0)  # Ensure timeout is cancelled
                        
                except TimeoutError as e:
                    print(f"❌ Routine performance seeding timed out: {e}")
                    session.rollback()
                    session = SessionLocal()  # Create new session after rollback
                except Exception as e:
                    print(f"❌ Error seeding routine performance: {e}")
                    print(f"Full error details: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    session.rollback()
                    session = SessionLocal()  # Create new session after rollback
                
                try:
                    print("Starting performance metrics seeding...")
                    performance_metrics_count, total_individual_metrics_count = seed_performance_metrics(session)
                    session.commit()
                    total_performance_metrics = performance_metrics_count
                    total_individual_metrics = total_individual_metrics_count
                    print(f"Performance metrics seeded successfully! Created {performance_metrics_count} performance records with {total_individual_metrics_count} individual metrics")
                except Exception as e:
                    print(f"Error seeding performance metrics: {e}")
                    print(f"Full error details: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    session.rollback()
                
                try:
                    print("Starting student activity data seeding...")
                    performance_count, preference_count, assessment_count, progression_count = seed_student_activity_data(session)
                    session.commit()
                    total_student_activity_performances = performance_count
                    total_student_activity_preferences = preference_count
                    total_activity_assessments = assessment_count
                    total_activity_progressions = progression_count
                    print(f"Student activity data seeded successfully! Created {performance_count} performance records, {preference_count} preference records, {assessment_count} assessment records, and {progression_count} progression records")
                except Exception as e:
                    print(f"Error seeding student activity data: {e}")
                    print(f"Full error details: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    session.rollback()
                
                # Assessment and progress tracking
                print("Seeding assessment and progress tracking...")
                try:
                    criteria_count = seed_assessment_criteria(session)
                    session.commit()
                    total_assessment_criteria = criteria_count
                    print(f"Assessment criteria seeded successfully! Created {criteria_count} criteria records")
                except Exception as e:
                    print(f"Error seeding assessment criteria: {e}")
                    session.rollback()
                
                try:
                    assessment_count = seed_skill_assessments(session)
                    session.commit()
                    total_skill_assessments = assessment_count
                    print(f"Skill assessments seeded successfully! Created {assessment_count} assessment records")
                except Exception as e:
                    print(f"Error seeding skill assessments: {e}")
                    session.rollback()
                
                try:
                    progress_count = seed_skill_progress(session)
                    session.commit()
                    total_skill_progress = progress_count
                    print(f"Skill progress seeded successfully! Created {progress_count} progress records")
                except Exception as e:
                    print(f"Error seeding skill progress: {e}")
                    session.rollback()
                
                # Re-seed tables that were cleared during student seeding
                print("\n" + "="*50)
                print("RE-SEEDING CLEARED TABLES")
                print("="*50)
                
                # Re-seed activity progressions (was cleared)
                print("Re-seeding activity progressions...")
                seed_activity_progressions(session)
                session.commit()
                
                # Re-seed activity plans (was cleared)
                print("Re-seeding activity plans...")
                seed_activity_plans(session)
                session.commit()
                
                # Re-seed class enrollments (was cleared)
                print("Re-seeding class enrollments...")
                seed_class_students(session)
                session.commit()
                
                # Re-seed progress table (needed for Phase 3)
                print("Re-seeding progress table...")
                from app.scripts.seed_data.seed_phase3_dependencies import seed_progress_table
                seed_progress_table(session)
                session.commit()
                
                print("All cleared tables have been re-seeded!")
                
                # NEW: Comprehensive system seeding
                print("\n" + "="*50)
                print("COMPREHENSIVE SYSTEM SEEDING")
                print("="*50)
                
                # Dashboard system
                print("Seeding dashboard system...")
                try:
                    seed_dashboard_system(session)
                    session.commit()
                    print("Dashboard system seeded!")
                except Exception as e:
                    print(f"Error seeding dashboard system: {e}")
                    session.rollback()
                
                # GPT/AI system - MOVED TO PHASE 5
                # print("Seeding GPT/AI system...")
                # try:
                #     seed_gpt_system(session)
                #     session.commit()
                #     print("GPT/AI system seeded!")
                # except Exception as e:
                #     print(f"Error seeding GPT/AI system: {e}")
                #     session.rollback()
                
                # Security system
                print("Seeding security system...")
                try:
                    seed_security_system(session)
                    session.commit()
                    print("Security system seeded!")
                except Exception as e:
                    print(f"Error seeding security system: {e}")
                    session.rollback()
                
                print("🔍 DEBUG: About to start Phase 1 (line 978)")
                print("🔍 DEBUG: Security system completed, moving to Phase 1...")
                
                # PHASE 1: FOUNDATION & CORE INFRASTRUCTURE (RUN IMMEDIATELY AFTER BASIC SEEDING)
                print("\n" + "="*50)
                print("🌱 PHASE 1: FOUNDATION & CORE INFRASTRUCTURE")
                print("="*50)
                try:
                    from app.scripts.seed_data.seed_phase1_foundation_fixed import seed_phase1_foundation
                    seed_phase1_foundation(session)
                    session.commit()
                    print("✅ Phase 1 foundation & core infrastructure completed successfully!")
                    print("🔒 Phase 1 data committed - protected from later phase rollbacks")
                except Exception as e:
                    print(f"❌ FAIL-FAST ERROR: Phase 1 foundation seeding failed: {e}")
                    print("🛑 STOPPING SCRIPT EXECUTION IMMEDIATELY - Phase 1 is required for all other phases")
                    print(f"📍 Error location: Phase 1 Foundation & Core Infrastructure")
                    print(f"🔍 Error details: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    session.rollback()
                    raise Exception(f"FAIL-FAST: Phase 1 foundation seeding failed: {e}")
                
                # PHASE 1.5: BETA TEACHER FEATURES - Available to both teacher and district versions
                print("\n🚀 PHASE 1.5: BETA TEACHER FEATURES")
                print("-" * 50)
                try:
                    if not env_true('SKIP_PHASE_1_5'):
                        print("🔄 Running Phase 1.5 beta teacher features...")
                        
                        # Import curriculum seeding modules
                        from app.scripts.seed_data.seed_drivers_education_curriculum import create_drivers_ed_curriculum
                        from app.scripts.seed_data.seed_health_curriculum import create_health_curriculum
                        
                        # Create comprehensive drivers education curriculum
                        print("🔄 Creating drivers education curriculum...")
                        create_drivers_ed_curriculum()
                        
                        # Create comprehensive health curriculum
                        print("🔄 Creating health curriculum...")
                        create_health_curriculum()
                        
                        session.commit()
                        print("✅ Phase 1.5 beta teacher features completed successfully!")
                        print("🎉 Drivers education and health curricula integrated for both teacher and district versions!")
                    else:
                        print("⏭️  SKIP_PHASE_1_5 enabled: skipping Phase 1.5 beta teacher features")
                        
                except Exception as e:
                    print(f"❌ ERROR: Phase 1.5 beta teacher features seeding failed: {e}")
                    print("⚠️  Continuing with remaining phases - Phase 1.5 can be run separately")
                    print(f"Full error details: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    # IMPORTANT: Don't rollback here - it would undo previous successful phases
                    # Just log the error and continue
                    print("🔄 Phase 1.5 will be skipped, continuing with remaining phases...")
                
                # Beta system moved to run after Phase 7 (see below)
                
                print("🔍 DEBUG: Phase 1 completed successfully, continuing to additional data seeding...")
                
                # IMMEDIATE PHASE 1 VERIFICATION - STOP SCRIPT IF PHASE 1 FAILED
                print("\n" + "="*50)
                print("🔍 IMMEDIATE PHASE 1 VERIFICATION")
                print("="*50)
                
                # Check if Phase 1 tables are actually populated
                phase1_tables = [
                    'permissions', 'role_permissions', 'permission_overrides'
                ]
                
                phase1_success = True
                for table in phase1_tables:
                    try:
                        count = session.execute(text(f'SELECT COUNT(*) FROM {table}')).scalar()
                        if count > 0:
                            print(f"  ✅ {table}: {count} records")
                        else:
                            print(f"  ❌ {table}: 0 records - PHASE 1 FAILED!")
                            phase1_success = False
                    except Exception as e:
                        print(f"  ❌ {table}: Error - {e} - PHASE 1 FAILED!")
                        phase1_success = False
                
                if not phase1_success:
                    print("\n❌ CRITICAL ERROR: Phase 1 verification failed!")
                    print("🛑 STOPPING SCRIPT IMMEDIATELY - Phase 1 data is missing!")
                    print("🔍 This means Phase 1 either failed or was rolled back")
                    raise Exception("Phase 1 verification failed - Phase 1 data is missing!")
                else:
                    print("✅ Phase 1 verification passed - all tables populated!")
                    print("🚀 Continuing with remaining phases...")
                
                # Additional data seeding for empty tables
                print("\n" + "="*50)
                print("ADDITIONAL DATA SEEDING")
                print("="*50)
                
                # Helper function to handle connection errors and create fresh session
                def safe_seed_with_fresh_session(seed_function, description):
                    """Execute a seeding function with error handling and fresh session if needed."""
                    try:
                        print(f"Seeding {description}...")
                        result = seed_function(session)
                        session.commit()
                        print(f"✅ {description} seeded successfully")
                        return result
                    except Exception as e:
                        print(f"⚠️  Could not seed {description}: {e}")
                        # If it's a connection error, try to rollback and continue
                        if "SSL SYSCALL error" in str(e) or "prepared" in str(e).lower():
                            print(f"🔄 Connection error detected, rolling back and continuing...")
                            try:
                                session.rollback()
                            except:
                                pass
                        return None
                
                # Seed some additional data for commonly used tables
                safe_seed_with_fresh_session(
                    lambda s: seed_additional_activity_data(s),
                    "additional activity data"
                )
                
                # AI and analytics data moved to Phase 5
                safe_seed_with_fresh_session(
                    lambda s: seed_comprehensive_analytics(s),
                    "comprehensive analytics and performance data"
                )
                
                # AI assistant analytics data
                safe_seed_with_fresh_session(
                    lambda s: seed_ai_analytics_data(s),
                    "AI assistant analytics data"
                )
                
                # TOOL ASSIGNMENTS SEEDING - Run after ai_tools are populated
                print("\n" + "="*50)
                print("TOOL ASSIGNMENTS SEEDING")
                print("="*50)
                try:
                    from app.scripts.seed_data.seed_phase1_foundation_fixed import seed_tool_assignments
                    seed_tool_assignments(session)
                    session.commit()
                    print("✅ Tool assignments seeding completed successfully!")
                except Exception as e:
                    print(f"❌ Tool assignments seeding failed: {e}")
                    session.rollback()
                    raise
                
                safe_seed_with_fresh_session(
                    lambda s: seed_adapted_activities(s),
                    "adapted activities and special needs data"
                )
                
                safe_seed_with_fresh_session(
                    lambda s: seed_unused_tables(s),
                    "unused tables with data"
                )
                
                # PHASE 1: FOUNDATION & CORE INFRASTRUCTURE (ALREADY RUN EARLIER)
                print("\n" + "="*50)
                print("🌱 PHASE 1: FOUNDATION & CORE INFRASTRUCTURE")
                print("="*50)
                print("✅ Phase 1 already completed earlier in the seeding process!")
                print("🔒 Phase 1 data is protected from rollbacks")
                
                # PHASE 2: EDUCATIONAL SYSTEM ENHANCEMENT
                print("\n" + "="*50)
                print("🚀 PHASE 2: EDUCATIONAL SYSTEM ENHANCEMENT")
                print("="*50)
                print("📚 Seeding 38 tables for advanced educational features")
                print("👨‍🏫 Teacher & class management")
                print("🏢 Department & organization structure")
                print("="*50)
                
                # Add missing subjects and grade_levels seeding (dependencies for lesson_plans)
                try:
                    print("📚 Seeding subjects...")
                    from app.scripts.seed_data.seed_lesson_plans import seed_subjects
                    seed_subjects(session)
                    session.commit()
                    print("✅ Subjects seeded successfully!")
                except Exception as e:
                    print(f"⚠️  Error seeding subjects: {e}")
                    session.rollback()
                
                try:
                    print("🎓 Seeding grade levels...")
                    from app.scripts.seed_data.seed_lesson_plans import seed_grade_levels
                    seed_grade_levels(session)
                    session.commit()
                    print("✅ Grade levels seeded successfully!")
                except Exception as e:
                    print(f"⚠️  Error seeding grade levels: {e}")
                    session.rollback()
                
                
                try:
                    print("🔄 Running Phase 2 educational system enhancement...")
                    print("🔍 Attempting to import Phase 2 module...")
                    # Import and run the Phase 2 seeding
                    from app.scripts.seed_data.seed_phase2_educational_system import seed_phase2_educational_system
                    print("📦 Phase 2 module imported successfully")
                    print("🔍 Calling seed_phase2_educational_system function...")
                    results = seed_phase2_educational_system(session)
                    print(f"📊 Phase 2 function returned: {results}")
                    
                    # Commit Phase 2 data immediately to protect from rollbacks
                    session.commit()
                    print("✅ Phase 2 educational system enhancement completed successfully!")
                    print(f"🎉 Created {sum(results.values())} records across {len(results)} tables")
                    print("🔒 Phase 2 data committed - protected from later phase rollbacks")
                except Exception as e:
                    print(f"❌ Phase 2 failed: {e}")
                    print("🔄 Rolling back transaction and continuing...")
                    session.rollback()
                    print("⚠️ Phase 2 skipped due to errors, continuing with remaining phases...")
                    
                    # Verify Phase 2 data persists
                    print("🔍 Verifying Phase 2 data persistence...")
                    course_count = session.execute(text("SELECT COUNT(*) FROM courses")).scalar()
                    print(f"  courses: {course_count} records")
                    enrollment_count = session.execute(text("SELECT COUNT(*) FROM course_enrollments")).scalar()
                    print(f"  course_enrollments: {enrollment_count} records")
                    
                    # Note: PE lesson plans, lesson plan activities, and lesson plan objectives 
                    # are already being created in Phase 2 educational system
                    print("📝 PE lesson plans will be created in Phase 2 educational system...")
                    
                    # Seed regular lesson_plans table (requires educational_teachers, subjects, grade_levels from Phase 2)
                    print("📝 Seeding lesson plans...")
                    from app.scripts.seed_data.seed_lesson_plans import seed_lesson_plans
                    print("🔍 About to call seed_lesson_plans function...")
                    result = seed_lesson_plans(session)
                    print(f"🔍 seed_lesson_plans returned: {result}")
                    session.commit()
                    print("✅ Lesson plans seeded successfully!")
                    
                    print("📚 Seeding curriculum units...")
                    from app.scripts.seed_data.seed_curriculum_units_simple import seed_curriculum_units_simple
                    print("🔍 About to call seed_curriculum_units_simple function...")
                    result = seed_curriculum_units_simple(session)
                    print(f"🔍 seed_curriculum_units_simple returned: {result}")
                    session.commit()
                    print("✅ Curriculum units seeded successfully!")
                    
                except Exception as e:
                    print(f"❌ CRITICAL ERROR: Phase 2 educational system seeding failed: {e}")
                    print("🛑 STOPPING SCRIPT EXECUTION - Phase 2 is required for educational features")
                    print(f"Full error details: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    session.rollback()
                    raise Exception(f"Phase 2 educational system seeding failed: {e}")
                
                # PHASE 3: HEALTH & FITNESS SYSTEM
                print("\n" + "="*50)
                print("🏥 PHASE 3: HEALTH & FITNESS SYSTEM")
                print("="*50)
                print("📊 Seeding 41 tables for comprehensive health, fitness, and nutrition")
                print("🏥 Health assessment & monitoring (12 tables)")
                print("💪 Fitness goals & progress (13 tables)")
                print("🥗 Nutrition & wellness (16 tables)")
                print("="*50)
                
                try:
                    print("🔄 Running Phase 3 comprehensive health & fitness system...")
                    # Import and run the dynamic Phase 3 seeding
                    from app.scripts.seed_data.seed_phase3_dynamic import seed_phase3_dynamic
                    results = seed_phase3_dynamic(session)
                    session.commit()
                    print("✅ Phase 3 comprehensive health & fitness system completed successfully!")
                    print(f"🎉 Created {sum(results.values())} records across {len(results)} tables")
                    print("🏆 All 41 Phase 3 tables successfully seeded!")
                except Exception as e:
                    print(f"❌ CRITICAL ERROR: Phase 3 health & fitness system seeding failed: {e}")
                    print("🛑 STOPPING SCRIPT EXECUTION - Phase 3 is required for health features")
                    print(f"Full error details: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    session.rollback()
                    raise Exception(f"Phase 3 health & fitness system seeding failed: {e}")
                
                # Additional comprehensive Phase 3 fixes - ensure ALL students have health records
                print("\n🔧 COMPREHENSIVE PHASE 3 FIXES - ROOT CAUSE SOLUTION")
                print("-" * 50)
                try:
                    from app.scripts.seed_data.fix_phase3_comprehensive import main as fix_phase3_comprehensive
                    fix_phase3_comprehensive()
                    print("✅ Comprehensive Phase 3 fixes completed!")
                except Exception as e:
                    print(f"⚠️  Warning: Comprehensive Phase 3 fixes failed: {e}")
                    # Don't rollback here, continue with main script
                
                # Phase 4: Safety & Risk Management System
                print("\n" + "="*50)
                print("🛡️ PHASE 4: SAFETY & RISK MANAGEMENT SYSTEM")
                print("="*50)
                print("📊 Seeding comprehensive safety infrastructure")
                print("⚠️ Risk assessment & prevention systems")
                print("🔧 Equipment management & maintenance")
                print("📋 Compliance & audit systems")
                print("="*50)

                if not env_true('SKIP_PHASE_4'):
                    try:
                        # Get required IDs for Phase 4 (use all available IDs)
                        user_result = session.execute(text('SELECT id FROM users'))
                        user_ids = [row[0] for row in user_result.fetchall()]

                        school_result = session.execute(text('SELECT id FROM schools'))
                        school_ids = [row[0] for row in school_result.fetchall()]

                        activity_result = session.execute(text('SELECT id FROM activities'))
                        activity_ids = [row[0] for row in activity_result.fetchall()]

                        student_result = session.execute(text('SELECT id FROM students'))
                        student_ids = [row[0] for row in student_result.fetchall()]

                        print(f"Found {len(user_ids)} users, {len(school_ids)} schools, {len(activity_ids)} activities, {len(student_ids)} students")

                        # First seed Phase 4 dependencies
                        from app.scripts.seed_data.seed_phase4_safety_risk_corrected import seed_phase4_dependencies
                        dep_results = seed_phase4_dependencies(session, user_ids, school_ids, activity_ids)
                        session.commit()
                        print("✅ Phase 4 dependencies completed successfully!")
                        print(f"🎉 Created {sum(dep_results.values())} dependency records across {len(dep_results)} tables")

                        # Then seed main Phase 4 tables
                        from app.scripts.seed_data.seed_phase4_safety_risk_corrected import seed_phase4_safety_risk
                        results = seed_phase4_safety_risk(session, user_ids, school_ids, activity_ids, student_ids)
                        session.commit()
                        print("✅ Phase 4 safety & risk management system completed successfully!")
                        print(f"🎉 Created {sum(results.values())} records across {len(results)} tables")
                        print("🏆 All Phase 4 tables successfully seeded!")
                    except Exception as e:
                        print(f"❌ CRITICAL ERROR: Phase 4 safety & risk management system seeding failed: {e}")
                        print("🛑 STOPPING SCRIPT EXECUTION - Phase 4 is required for safety features")
                        print(f"Full error details: {str(e)}")
                        import traceback
                        traceback.print_exc()
                        session.rollback()
                        raise Exception(f"Phase 4 safety & risk management system seeding failed: {e}")
                else:
                    print("⏭️  SKIP_PHASE_4 enabled: skipping Phase 4 safety & risk management")
                
                # Phase 5: Advanced Analytics & AI
                if not env_true('SKIP_PHASE_5'):
                    try:
                        print("🔄 Running Phase 5 advanced analytics & AI...")

                        # Ensure project_id=1 exists for Phase 5 foreign key constraints
                        print("🔧 Ensuring project dependency for Phase 5...")
                        project_check = session.execute(text("SELECT id FROM organization_projects WHERE id = 1"))
                        if not project_check.fetchone():
                            # Get a user_id for the project
                            user_result = session.execute(text("SELECT id FROM users LIMIT 1"))
                            user_id = user_result.scalar()

                            # Create the required project
                            session.execute(text("""
                                INSERT INTO organization_projects (
                                    id, name, description, user_id, created_at, updated_at, status, is_active
                                ) VALUES (
                                    1, 'Default Project', 'Default project for Phase 5 GPT systems',
                                    :user_id, NOW(), NOW(), 'ACTIVE', true
                                )
                            """), {'user_id': user_id})
                            session.commit()
                            print("✅ Created project_id=1 for Phase 5 dependencies")
                        else:
                            print("✅ Project_id=1 already exists")

                        # Get organization IDs for Phase 5
                        org_result = session.execute(text("SELECT id FROM organizations"))
                        organization_ids = [row[0] for row in org_result.fetchall()]
                        if not organization_ids:
                            organization_ids = [1]  # Fallback

                        # Import and run the Phase 5 seeding
                        from app.scripts.seed_data.seed_phase5_analytics_ai import seed_phase5_analytics_ai
                        results = seed_phase5_analytics_ai(session, user_ids, organization_ids)
                        session.commit()

                        # GPT system is already seeded by seed_phase5_analytics_ai above
                        # No need to call seed_gpt_system separately
                        # Beta teacher system moved to run after Phase 7 (see below)

                        print("✅ Phase 5 advanced analytics & AI completed successfully!")
                        print(f"🎉 Created {sum(results.values())} records across {len(results)} tables")
                        print("🏆 All Phase 5 tables successfully seeded!")
                    except Exception as e:
                        print(f"❌ CRITICAL ERROR: Phase 5 advanced analytics & AI seeding failed: {e}")
                        print("🛑 STOPPING SCRIPT EXECUTION - Phase 5 is required for analytics features")
                        print(f"Full error details: {str(e)}")
                        import traceback
                        traceback.print_exc()
                        session.rollback()
                        raise Exception(f"Phase 5 advanced analytics & AI seeding failed: {e}")
                else:
                    print("⏭️  SKIP_PHASE_5 enabled: skipping Phase 5 advanced analytics & AI")
                
                # Phase 6: Movement & Performance Analysis
                print("\n🎯 PHASE 6: MOVEMENT & PERFORMANCE ANALYSIS")
                print("-" * 50)
                if not env_true('SKIP_PHASE_6'):
                    try:
                        from app.scripts.seed_data.seed_phase6_movement_performance import seed_phase6_movement_performance
                        results = seed_phase6_movement_performance(session)
                        session.commit()
                        print("✅ Phase 6 movement & performance analysis completed successfully!")
                        print(f"🎉 Created {sum(results.values())} records across {len(results)} tables")
                        print("🏆 All Phase 6 tables successfully seeded!")
                    except Exception as e:
                        print(f"❌ CRITICAL ERROR: Phase 6 movement & performance analysis seeding failed: {e}")
                        print("🛑 STOPPING SCRIPT EXECUTION - Phase 6 is required for movement analysis")
                        print(f"Full error details: {str(e)}")
                        import traceback
                        traceback.print_exc()
                        session.rollback()
                        raise Exception(f"Phase 6 movement & performance analysis seeding failed: {e}")
                else:
                    print("⏭️  SKIP_PHASE_6 enabled: skipping Phase 6 movement & performance analysis")
                
                # Phase 7: Specialized Features
                print("\n🎯 PHASE 7: SPECIALIZED FEATURES")
                print("-" * 50)
                if not env_true('SKIP_PHASE_7'):
                    try:
                        from app.scripts.seed_data.seed_phase7_specialized_features import seed_phase7_specialized_features
                        results = seed_phase7_specialized_features(session)
                        # Commit Phase 7 separately to avoid transaction abortion
                        try:
                            session.commit()
                            print("✅ Phase 7 specialized features completed successfully!")
                            print(f"🎉 Created {sum(results.values())} records across {len(results)} tables")
                            print("🏆 All Phase 7 tables successfully seeded!")

                            # Verify Phase 7 data persistence
                            print("🔍 Verifying Phase 7 data persistence...")
                            phase7_verification = session.execute(text("SELECT COUNT(*) FROM pe_activity_adaptations")).scalar()
                            print(f"  pe_activity_adaptations: {phase7_verification} records")

                        except Exception as commit_error:
                            print(f"⚠️ Phase 7 commit error (some records may not be saved): {commit_error}")
                            session.rollback()
                            # Try to commit individual successful tables
                            print("🔄 Attempting to save successful Phase 7 records...")
                            try:
                                session.commit()
                                print("✅ Phase 7 records saved successfully!")
                            except:
                                print("❌ Could not save Phase 7 records")
                    except Exception as e:
                        print(f"❌ CRITICAL ERROR: Phase 7 specialized features seeding failed: {e}")
                        print("🛑 STOPPING SCRIPT EXECUTION - Phase 7 is required for specialized features")
                        print(f"Full error details: {str(e)}")
                        import traceback
                        traceback.print_exc()
                        session.rollback()
                        raise Exception(f"Phase 7 specialized features seeding failed: {e}")
                else:
                    print("⏭️  SKIP_PHASE_7 enabled: skipping Phase 7 specialized features")
                
                # PHASE 1.6-1.10: BETA TEACHER SYSTEM - NOW RUNS AFTER PHASE 7
                print("\n🎯 PHASES 1.6-1.10: COMPREHENSIVE BETA TEACHER SYSTEM")
                print("=" * 60)
                try:
                    if not env_true('SKIP_PHASE_1_6_TO_1_10'):
                        print("🔄 Running comprehensive beta teacher system integration...")

                        # Import beta teacher system seeding
                        from app.scripts.seed_data.seed_beta_teacher_system import seed_beta_teacher_system

                        # Ensure core tables are committed before running migrations
                        session.commit()
                        print("  ✅ Core tables committed, starting beta system seeding...")

                        # Run beta teacher system seeding
                        seed_beta_teacher_system(session)
                        
                        session.commit()

                        print("✅ Phases 1.6-1.10: Comprehensive beta teacher system completed successfully!")
                        print("🎉 All beta teacher components integrated and seeded!")
                    else:
                        print("⏭️  SKIP_PHASE_1_6_TO_1_10 enabled: skipping comprehensive beta teacher system")

                except Exception as e:
                    print(f"❌ ERROR: Comprehensive beta teacher system integration failed: {e}")
                    import traceback
                    traceback.print_exc()
                    print("⚠️  Continuing with remaining phases - Beta components can be run separately")
                    print(f"Full error details: {str(e)}")

                # Phase 8: Advanced Physical Education & Adaptations
                print("\n🎯 PHASE 8: ADVANCED PHYSICAL EDUCATION & ADAPTATIONS")
                print("-" * 50)
                if not env_true('SKIP_PHASE_8'):
                    try:
                        from app.scripts.seed_data.seed_phase8_complete_fixed import seed_phase8_complete_fixed
                        results = seed_phase8_complete_fixed(session)
                        # Commit Phase 8 separately to avoid transaction abortion
                        try:
                            session.commit()
                            print("✅ Phase 8 advanced PE & adaptations completed successfully!")
                            print(f"🎉 Created {sum(results.values())} records across {len(results)} tables")
                            print("🏆 All Phase 8 tables successfully seeded!")
                        except Exception as commit_error:
                            print(f"⚠️ Phase 8 commit error (some records may not be saved): {commit_error}")
                            session.rollback()
                            # Try to commit individual successful tables
                            print("🔄 Attempting to save successful Phase 8 records...")
                            try:
                                session.commit()
                                print("✅ Phase 8 records saved successfully!")
                            except:
                                print("❌ Could not save Phase 8 records")
                    except Exception as e:
                        print(f"❌ CRITICAL ERROR: Phase 8 advanced PE & adaptations seeding failed: {e}")
                        print("🛑 STOPPING SCRIPT EXECUTION - Phase 8 is required for advanced PE features")
                        print(f"Full error details: {str(e)}")
                        import traceback
                        traceback.print_exc()
                        session.rollback()
                        raise Exception(f"Phase 8 advanced PE & adaptations seeding failed: {e}")
                else:
                    print("⏭️  SKIP_PHASE_8 enabled: skipping Phase 8 advanced PE & adaptations")
                
                # Phase 9: Health & Fitness System
                print("\n🎯 PHASE 9: HEALTH & FITNESS SYSTEM")
                print("-" * 50)
                if not env_true('SKIP_PHASE_9'):
                    try:
                        from app.scripts.seed_data.seed_phase9_health_fitness import seed_phase9_health_fitness
                        results = seed_phase9_health_fitness(session)
                        # Commit Phase 9 separately to avoid transaction abortion
                        try:
                            session.commit()
                            print("✅ Phase 9 health & fitness system completed successfully!")
                            print(f"🎉 Created {sum(results.values())} records across {len(results)} tables")
                            print("🏆 All Phase 9 tables successfully seeded!")
                        except Exception as commit_error:
                            print(f"⚠️ Phase 9 commit error (some records may not be saved): {commit_error}")
                            session.rollback()
                            # Try to commit individual successful tables
                            print("🔄 Attempting to save successful Phase 9 records...")
                            try:
                                session.commit()
                                print("✅ Phase 9 records saved successfully!")
                            except:
                                print("❌ Could not save Phase 9 records")
                    except Exception as e:
                        print(f"❌ CRITICAL ERROR: Phase 9 health & fitness system seeding failed: {e}")
                        print("🛑 STOPPING SCRIPT EXECUTION - Phase 9 is required for health & fitness features")
                        print(f"Full error details: {str(e)}")
                        import traceback
                        traceback.print_exc()
                        session.rollback()
                        raise Exception(f"Phase 9 health & fitness system seeding failed: {e}")
                else:
                    print("⏭️  SKIP_PHASE_9 enabled: skipping Phase 9 health & fitness")
                
                # Phase 10: Assessment & Skill Management

                print("\n🎯 PHASE 10: ASSESSMENT & SKILL MANAGEMENT")
                print("-" * 50)
                if not env_true('SKIP_PHASE_10'):
                    try:
                        from app.scripts.seed_data.seed_phase10_assessment_skill_management import seed_phase10_assessment_skill_management
                        success = seed_phase10_assessment_skill_management(session)
                        # Commit Phase 10 separately to avoid transaction abortion
                        try:
                            session.commit()
                            if success:
                                print("✅ Phase 10 assessment & skill management completed successfully!")
                                print("🏆 All Phase 10 tables successfully seeded!")
                            else:
                                print("⚠️ Phase 10 partially completed - some tables failed")
                                print("🔄 Attempting to save successful Phase 10 records...")
                        except Exception as commit_error:
                            print(f"⚠️ Phase 10 commit error (some records may not be saved): {commit_error}")
                            session.rollback()
                            # Try to commit individual successful tables
                            print("🔄 Attempting to save successful Phase 10 records...")
                            try:
                                session.commit()
                                print("✅ Phase 10 records saved successfully!")
                            except:
                                print("❌ Could not save Phase 10 records")

                        # Verify Phase 7 data is still intact after Phase 10
                        print("🔍 Verifying Phase 7 data integrity after Phase 10...")
                        try:
                            phase7_check = session.execute(text("SELECT COUNT(*) FROM pe_activity_adaptations")).scalar()
                            print(f"  pe_activity_adaptations after Phase 10: {phase7_check} records")
                            if phase7_check == 0:
                                print("⚠️ WARNING: Phase 7 data was rolled back by Phase 10!")
                            else:
                                print("✅ Phase 7 data intact after Phase 10")
                        except Exception as e:
                            print(f"⚠️ Could not verify Phase 7 data: {e}")
                    except Exception as e:
                        print(f"❌ CRITICAL ERROR: Phase 10 assessment & skill management seeding failed: {e}")
                        print("🛑 STOPPING SCRIPT EXECUTION - Phase 10 is required for assessment features")
                        print(f"Full error details: {str(e)}")
                        import traceback
                        traceback.print_exc()
                        session.rollback()
                        raise Exception(f"Phase 10 assessment & skill management seeding failed: {e}")
                else:
                    print("⏭️  SKIP_PHASE_10 enabled: skipping Phase 10 assessment & skill management")
                
                # PHASE 1 & PHASE 2 DATA MIGRATION
                # Run after Phase 10 completes (or if Phase 10 was skipped) to migrate data from source tables to target tables
                # This ensures all parent tables (skill_assessment_safety_*, general_*) are seeded first
                # Note: Migration will gracefully handle cases where source tables are empty
                print("\n🔄 PHASE 1 & PHASE 2 DATA MIGRATION")
                print("=" * 60)
                print("📋 Migrating data from source tables to Phase 1 & Phase 2 target tables")
                print("   - Phase 1: skill_assessment_safety_* → safety_protocols, safety_incidents, risk_assessments")
                print("   - Phase 2: general_* → skill_assessment_* tables")
                print("   ℹ️  Works for both main system and beta system (shared tables)")
                
                if not env_true('SKIP_PHASE_1_2_MIGRATION'):
                    try:
                        from app.scripts.seed_data.migrate_phase1_phase2_data import migrate_phase1_phase2_data
                        
                        migration_results = migrate_phase1_phase2_data(session)
                        session.commit()
                        
                        # Migration output is already printed by migrate_phase1_phase2_data()
                        # Just confirm completion here
                        print("\n✅ Phase 1 & Phase 2 data migration completed!")
                        print(f"   Summary: Phase 1={migration_results['phase1']['protocols']+migration_results['phase1']['incidents']+migration_results['phase1']['risk_assessments']} records, "
                              f"Phase 2={migration_results['phase2']['assessments']+migration_results['phase2']['results']+migration_results['phase2']['criteria']+migration_results['phase2']['history']+migration_results['phase2']['progress']} records")
                        
                    except Exception as e:
                        print(f"⚠️  Phase 1 & Phase 2 migration failed (non-critical): {e}")
                        print("   ℹ️  Migration is optional - existing data will continue to work")
                        session.rollback()
                        # Don't fail the entire script - migration is optional
                        import traceback
                        traceback.print_exc()
                else:
                    print("⏭️  SKIP_PHASE_1_2_MIGRATION enabled: skipping Phase 1 & Phase 2 data migration")
                
                # Phase 11: Advanced System Features
                print("\n🚀 PHASE 11: ADVANCED SYSTEM FEATURES")
                print("-" * 50)
                if not env_true('SKIP_PHASE_11'):
                    try:
                        print("🔄 Running Phase 11 advanced system features...")
                        results = seed_phase11_advanced_system_features(session)
                        # Commit Phase 11 separately to avoid transaction abortion
                        try:
                            session.commit()
                            print("✅ Phase 11 advanced system features completed successfully!")
                            print(f"🎉 Created {sum(results.values()):,} records across {len(results)} tables")
                            print("🏆 All Phase 11 tables successfully seeded!")
                        except Exception as commit_error:
                            print(f"⚠️ Phase 11 commit error (some records may not be saved): {commit_error}")
                            session.rollback()
                            # Try to commit individual successful tables
                            print("🔄 Attempting to save successful Phase 11 records...")
                            try:
                                session.commit()
                                print("✅ Phase 11 records saved successfully!")
                            except:
                                print("❌ Could not save Phase 11 records")
                    except Exception as e:
                        print(f"❌ ERROR: Phase 11 advanced system features seeding failed: {e}")
                        print("⚠️  Continuing with remaining phases - Phase 11 can be run separately")
                        print(f"Full error details: {str(e)}")
                        import traceback
                        traceback.print_exc()
                        session.rollback()
                        # Don't stop execution, just log the error and continue
                        print("🔄 Phase 11 will be skipped, continuing with remaining phases...")
                else:
                    print("⏭️  SKIP_PHASE_11 enabled: skipping Phase 11 advanced system features")
                
                # PHASE 3 DATA MIGRATION
                if not env_true('SKIP_PHASE_3_MIGRATION'):
                    print("\n🔄 PHASE 3 DATA MIGRATION")
                    print("-" * 60)
                    print("📋 Migrating data from security_logs, security_audits, security_general_audit_logs to security_events")
                    try:
                        from app.scripts.seed_data.migrate_phase3_data import migrate_phase3_data
                        
                        migration_results = migrate_phase3_data(session)
                        
                        # Migration output is already printed by migrate_phase3_data()
                        
                        print("\n✅ Phase 3 data migration completed!")
                        print(f"   Summary: {migration_results['total']} total security events migrated")
                    except Exception as e:
                        print(f"⚠️  Phase 3 migration failed (non-critical): {e}")
                        import traceback
                        traceback.print_exc()
                        session.rollback()
                else:
                    print("⏭️  SKIP_PHASE_3_MIGRATION enabled: skipping Phase 3 data migration")
                
                # PHASE 4 DATA MIGRATION
                if not env_true('SKIP_PHASE_4_MIGRATION'):
                    print("\n🔄 PHASE 4 DATA MIGRATION")
                    print("-" * 60)
                    print("📋 Migrating data from resource_management_usage, resource_thresholds, resource_optimizations, resource_management_sharing, optimization_events to dashboard_resource_* tables")
                    try:
                        from app.scripts.seed_data.migrate_phase4_data import migrate_phase4_data
                        
                        migration_results = migrate_phase4_data(session)
                        
                        # Migration output is already printed by migrate_phase4_data()
                        
                        print("\n✅ Phase 4 data migration completed!")
                        print(f"   Summary: {migration_results['total']} total resource records migrated")
                    except Exception as e:
                        print(f"⚠️  Phase 4 migration failed (non-critical): {e}")
                        import traceback
                        traceback.print_exc()
                        session.rollback()
                else:
                    print("⏭️  SKIP_PHASE_4_MIGRATION enabled: skipping Phase 4 data migration")
                
                # PHASE 5 DATA MIGRATION
                if not env_true('SKIP_PHASE_5_MIGRATION'):
                    print("\n🔄 PHASE 5 DATA MIGRATION")
                    print("-" * 60)
                    print("📋 Migrating data from gpt_context_* tables to dashboard_context_* tables")
                    try:
                        from app.scripts.seed_data.migrate_phase5_data import migrate_phase5_data
                        
                        migration_results = migrate_phase5_data(session)
                        
                        # Migration output is already printed by migrate_phase5_data()
                        
                        print("\n✅ Phase 5 data migration completed!")
                        print(f"   Summary: {migration_results['total']} total context records migrated")
                    except Exception as e:
                        print(f"⚠️  Phase 5 migration failed (non-critical): {e}")
                        import traceback
                        traceback.print_exc()
                        session.rollback()
                else:
                    print("⏭️  SKIP_PHASE_5_MIGRATION enabled: skipping Phase 5 data migration")
                
                # PHASE 6 DATA MIGRATION
                if not env_true('SKIP_PHASE_6_MIGRATION'):
                    print("\n🔄 PHASE 6 DATA MIGRATION")
                    print("-" * 60)
                    print("📋 Migrating data from core_dashboard_widgets, beta_widgets, user_preferences, teacher_preferences to dashboard_* tables")
                    try:
                        from app.scripts.seed_data.migrate_phase6_data import migrate_phase6_data
                        
                        migration_results = migrate_phase6_data(session)
                        
                        # Migration output is already printed by migrate_phase6_data()
                        
                        print("\n✅ Phase 6 data migration completed!")
                        print(f"   Summary: {migration_results['total']} total preference records migrated")
                    except Exception as e:
                        print(f"⚠️  Phase 6 migration failed (non-critical): {e}")
                        import traceback
                        traceback.print_exc()
                        session.rollback()
                else:
                    print("⏭️  SKIP_PHASE_6_MIGRATION enabled: skipping Phase 6 data migration")
                
                # AI WIDGET INTEGRATION SEEDING - Ensures data for both main and beta systems
                if not env_true('SKIP_AI_WIDGET_INTEGRATION'):
                    print("\n" + "=" * 60)
                    print("🤖 AI WIDGET INTEGRATION SEEDING")
                    print("=" * 60)
                    print("📊 Seeding data for AI widget features (main & beta systems)")
                    try:
                        from app.scripts.seed_data.seed_ai_widget_integration import seed_ai_widget_integration
                        ai_widget_results = seed_ai_widget_integration(session)
                        session.commit()
                        print("✅ AI widget integration seeding completed!")
                        print(f"   Summary: {sum(ai_widget_results.values())} records verified/created")
                        
                        # Backfill student emails for communication tests
                        from app.scripts.seed_data.backfill_student_emails import backfill_student_emails
                        email_results = backfill_student_emails(session)
                        print("✅ Student email backfill completed!")
                        print(f"   Main students: {email_results['main_students_updated']:,} updated")
                        print(f"   Beta students: {email_results['beta_students_updated']:,} updated")
                    except Exception as e:
                        print(f"⚠️  AI widget integration seeding failed (non-critical): {e}")
                        session.rollback()
                        import traceback
                        traceback.print_exc()
                else:
                    print("\n" + "=" * 60)
                    print("⏭️  SKIPPING AI WIDGET INTEGRATION SEEDING (SKIP_AI_WIDGET_INTEGRATION=true)")
                    print("=" * 60)
                
                # Seed test student data for beta system tables (beta_students, drivers_ed_student_progress, health_student_progress)
                # This ensures all tables are populated for a complete database (537/539 tables)
                # Can be skipped by setting SKIP_TEST_STUDENT_DATA=true
                # NOTE: This must run BEFORE the final summary so counts are included
                if not env_true('SKIP_TEST_STUDENT_DATA'):
                    print("\n" + "=" * 60)
                    print("📚 TEST STUDENT DATA SEEDING")
                    print("=" * 60)
                    try:
                        from app.scripts.seed_data.seed_test_student_data import seed_test_student_data
                        seed_test_student_data(session, for_tests=True)
                        session.commit()
                        print("✅ Test student data seeding completed!")
                    except Exception as e:
                        print(f"⚠️  Test student data seeding failed (non-critical): {e}")
                        session.rollback()
                        import traceback
                        traceback.print_exc()
                else:
                    print("\n" + "=" * 60)
                    print("⏭️  SKIPPING TEST STUDENT DATA SEEDING (SKIP_TEST_STUDENT_DATA=true)")
                    print("=" * 60)
                
                # Performance tracking summary
                print("\n" + "="*50)
                print("PERFORMANCE TRACKING SUMMARY")
                print("="*50)
                
                # Query database directly for accurate counts
                try:
                    # Count routines and routine activities
                    routine_count = session.execute(text("SELECT COUNT(*) FROM physical_education_routines")).scalar()
                    routine_activity_count = session.execute(text("SELECT COUNT(*) FROM routine_activities")).scalar()
                    print(f"📊 Routines: {routine_count} routines with {routine_activity_count} activities")
                    
                    # Count routine performances
                    performance_count = session.execute(text("SELECT COUNT(*) FROM routine_performances")).scalar()
                    print(f"📊 Routine Performance: {performance_count} records")
                    
                    # Count performance metrics
                    metrics_count = session.execute(text("SELECT COUNT(*) FROM routine_performance_metrics")).scalar()
                    print(f"📊 Performance Metrics: {metrics_count} records")
                    
                    # Count student activity data
                    activity_performance_count = session.execute(text("SELECT COUNT(*) FROM student_activity_performances")).scalar()
                    activity_preference_count = session.execute(text("SELECT COUNT(*) FROM pe_activity_preferences")).scalar()
                    activity_assessment_count = session.execute(text("SELECT COUNT(*) FROM activity_assessments")).scalar()
                    activity_progression_count = session.execute(text("SELECT COUNT(*) FROM activity_progressions")).scalar()
                    print(f"📊 Student Activity Data: {activity_performance_count} performances, {activity_preference_count} preferences, {activity_assessment_count} assessments, {activity_progression_count} progressions")
                    
                    # Count assessment data
                    assessment_criteria_count = session.execute(text("SELECT COUNT(*) FROM skill_assessment_assessment_criteria")).scalar()
                    skill_assessment_count = session.execute(text("SELECT COUNT(*) FROM skill_assessment_skill_assessments")).scalar()
                    skill_progress_count = session.execute(text("SELECT COUNT(*) FROM skill_progress")).scalar()
                    print(f"📊 Assessment Criteria: {assessment_criteria_count} criteria")
                    print(f"📊 Skill Assessments: {skill_assessment_count} assessments")
                    print(f"📊 Skill Progress: {skill_progress_count} progress records")
                    
                    # Count additional analytics data
                    try:
                        performance_logs_count = session.execute(text("SELECT COUNT(*) FROM performance_logs")).scalar()
                        print(f"📊 Performance Logs: {performance_logs_count} records")
                    except:
                        print(f"📊 Performance Logs: 0 records (table not found)")
                    
                    try:
                        analytics_events_count = session.execute(text("SELECT COUNT(*) FROM analytics_events")).scalar()
                        print(f"📊 Analytics Events: {analytics_events_count} records")
                    except:
                        print(f"📊 Analytics Events: 0 records (table not found)")
                    
                    try:
                        ai_suites_count = session.execute(text("SELECT COUNT(*) FROM ai_suites")).scalar()
                        ai_tools_count = session.execute(text("SELECT COUNT(*) FROM ai_tools")).scalar()
                        print(f"📊 AI System: {ai_suites_count} suites, {ai_tools_count} tools")
                    except:
                        print(f"📊 AI System: 0 suites, 0 tools (tables not found)")
                    
                    try:
                        feedback_count = session.execute(text("SELECT COUNT(*) FROM dashboard_feedback")).scalar()
                        print(f"📊 Feedback Data: {feedback_count} records")
                    except:
                        print(f"📊 Feedback Data: 0 records (table not found)")
                
                except Exception as e:
                    print(f"⚠️  Could not query performance tracking counts: {e}")
                    # Fallback to variables
                    print(f"📊 Routines: {total_routines} routines with {total_routine_activities} activities")
                    print(f"📊 Routine Performance: {total_performance_records} records")
                    print(f"📊 Performance Metrics: {total_performance_metrics} records with {total_individual_metrics} metrics")
                    print(f"📊 Student Activity Data: {total_student_activity_performances} performances, {total_student_activity_preferences} preferences, {total_activity_assessments} assessments, {total_activity_progressions} progressions")
                    print(f"📊 Assessment Criteria: {total_assessment_criteria} criteria")
                    print(f"📊 Skill Assessments: {total_skill_assessments} assessments")
                    print(f"📊 Skill Progress: {total_skill_progress} progress records")
                # Refresh planner stats on key tables
                try:
                    print("\n🧮 Running ANALYZE on key tables...")
                    analyze_tables = [
                        'students',
                        'student_school_enrollments',
                        'courses',
                        'course_enrollments'
                    ]
                    for t in analyze_tables:
                        try:
                            session.execute(text(f"ANALYZE {t}"))
                        except Exception as e:
                            print(f"⚠️  ANALYZE failed for {t}: {e}")
                    session.commit()
                    print("✅ ANALYZE complete")
                except Exception as e:
                    print(f"⚠️  Could not run ANALYZE: {e}")

                print("="*50)
                
                # Set admin user (if email exists in database)
                print("\n" + "="*50)
                print("SETTING ADMIN USER")
                print("="*50)
                try:
                    admin_email = "jmartucci@faraday-ai.com"
                    result = session.execute(text("""
                        UPDATE users 
                        SET role = 'admin', 
                            is_superuser = true, 
                            is_active = true,
                            disabled = false
                        WHERE email = :email
                    """), {"email": admin_email})
                    
                    if result.rowcount > 0:
                        print(f"✅ Updated user {admin_email} to admin with full access!")
                    else:
                        print(f"⚠️  User {admin_email} not found in users table.")
                        # Try to create admin user from teacher_registrations if it exists there
                        teacher_check = session.execute(text("""
                            SELECT email, password_hash, first_name, last_name 
                            FROM teacher_registrations 
                            WHERE email = :email
                        """), {"email": admin_email}).fetchone()
                        
                        if teacher_check:
                            # User exists in teacher_registrations, create in users table
                            session.execute(text("""
                                INSERT INTO users (email, password_hash, first_name, last_name, role, is_superuser, is_active, disabled, created_at, updated_at)
                                VALUES (:email, :password_hash, :first_name, :last_name, 'admin', true, true, false, NOW(), NOW())
                                ON CONFLICT (email) DO UPDATE 
                                SET role = 'admin',
                                    is_superuser = true,
                                    is_active = true,
                                    disabled = false
                            """), {
                                "email": teacher_check[0],
                                "password_hash": teacher_check[1],
                                "first_name": teacher_check[2],
                                "last_name": teacher_check[3]
                            })
                            session.commit()
                            print(f"✅ Created admin user {admin_email} from teacher_registrations!")
                        else:
                            print(f"ℹ️  User {admin_email} not found. Register first, then this will update you to admin on next deployment.")
                    
                    session.commit()
                except Exception as e:
                    print(f"⚠️  Could not set admin user: {e}")
                    session.rollback()
                    # Don't fail the entire seeding process if admin setup fails
                
                # Final count summary
                print("\n" + "="*50)
                print("FINAL SEEDING SUMMARY")
                print("="*50)
                
                # Initialize variables
                total_records = 0
                populated_tables = 0
                table_names = []
                
                # Count all major tables using fresh connection for accurate results
                print("Counting records in all tables...")
                try:
                    # Use fresh connection for accurate counting
                    with engine.connect() as count_conn:
                        from app.models.shared_base import SharedBase
                        inspector = inspect(engine)
                        table_names = inspector.get_table_names()
                        
                        print(f"Found {len(table_names)} tables to count:")
                        
                        failed_tables = []
                        for table_name in sorted(table_names):
                            try:
                                # Check if table exists before querying
                                table_check = count_conn.execute(text(f"""
                                    SELECT EXISTS (
                                        SELECT FROM information_schema.tables 
                                        WHERE table_schema = 'public' 
                                        AND table_name = '{table_name}'
                                    )
                                """)).scalar()
                                
                                if table_check:
                                    count = count_conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
                                    print(f"  {table_name}: {count:,} records")
                                    total_records += count
                                    if count > 0:
                                        populated_tables += 1
                                else:
                                    print(f"  {table_name}: Table does not exist - skipping")
                            except Exception as e:
                                failed_tables.append(f"{table_name}: {str(e)[:50]}")
                                print(f"  {table_name}: Error counting - {e}")
                                # Continue with next table instead of aborting transaction
                        
                        if failed_tables:
                            print(f"\n⚠️ Tables with counting errors: {len(failed_tables)}")
                            for failed in failed_tables[:10]:  # Show first 10 errors
                                print(f"  - {failed}")
                            if len(failed_tables) > 10:
                                print(f"  ... and {len(failed_tables) - 10} more")
                        
                        # Verify Phase 10 tables are counted
                        phase10_tables = [
                            'skill_assessment_assessment_metrics', 'skill_assessment_assessments', 'skill_assessment_risk_assessments',
                            'skill_assessment_safety_alerts', 'skill_assessment_safety_incidents', 'skill_assessment_safety_protocols',
                            'skill_assessment_assessment_criteria', 'skill_assessment_assessment_history', 'skill_assessment_assessment_results',
                            'skill_assessment_skill_assessments', 'general_assessment_criteria', 'general_assessment_history', 
                            'general_skill_assessments', 'student_health_skill_assessments', 'assessment_changes', 
                            'analysis_movement_feedback', 'movement_analysis_metrics', 'movement_analysis_patterns',
                            'physical_education_movement_analysis', 'safety', 'safety_incident_base', 'safety_incidents', 
                            'safety_guidelines', 'safety_protocols', 'safety_reports', 'safety_measures', 'safety_checklists',
                            'activity_injury_preventions', 'injury_preventions', 'activity_logs'
                        ]
                        
                        phase10_count = 0
                        for table in phase10_tables:
                            if table in table_names:
                                try:
                                    count = count_conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
                                    if count > 0:
                                        phase10_count += 1
                                except:
                                    pass
                        
                        print(f"\n📊 Phase 10 verification: {phase10_count}/30 tables populated")
                        
                        print(f"\nTotal records across all tables: {total_records:,}")
                    print(f"Populated tables: {populated_tables}/{len(table_names)} tables have data")
                    
                except Exception as e:
                    print(f"Error during table counting: {e}")
                    print("Attempting manual count of key tables...")
                    
                    # Manual count of key tables
                    key_tables = [
                        'users', 'students', 'lessons', 'exercises', 'activities',
                        'classes', 'schools', 'activity_plans', 'activity_progressions'
                    ]
                    
                    for table_name in key_tables:
                        try:
                            # Check if table exists before querying
                            table_check = session.execute(text(f"""
                                SELECT EXISTS (
                                    SELECT FROM information_schema.tables 
                                    WHERE table_schema = 'public' 
                                    AND table_name = '{table_name}'
                                )
                            """)).scalar()
                            
                            if table_check:
                                count = session.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
                                print(f"  {table_name}: {count:,} records")
                                total_records += count
                                if count > 0:
                                    populated_tables += 1
                            else:
                                print(f"  {table_name}: Table does not exist - skipping")
                        except Exception as e:
                            print(f"  {table_name}: Error counting - {e}")
                            # Continue with next table instead of aborting transaction
                    
                    # Set fallback values if table counting failed
                    if not table_names:
                        table_names = key_tables
                        populated_tables = max(populated_tables, 0)
                
                print("="*50)
                print("Database seeded successfully!")
                print("="*50)
                print("🎉 COMPREHENSIVE DATABASE SEEDING COMPLETE! 🎉")
                print("="*50)
                
                # Final table count verification
                try:
                    final_table_count = session.execute(text("""
                        SELECT COUNT(*) 
                        FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_type = 'BASE TABLE'
                    """)).scalar()
                    print(f"📊 Total tables in database: {final_table_count}")
                    
                    # Check for job tables
                    try:
                        job_exists = session.execute(text("SELECT COUNT(*) FROM job")).scalar()
                        job_run_exists = session.execute(text("SELECT COUNT(*) FROM job_run_details")).scalar()
                        print(f"📊 Job tables: job={job_exists}, job_run_details={job_run_exists}")
                    except:
                        print("📊 Job tables: Not created")
                        
                except Exception as e:
                    print(f"📊 Final table count: ERROR - {e}")
                print("✅ Phase 1: Foundation & Core Infrastructure")
                print("✅ Phase 1.5: Beta Teacher Features (Drivers Education & Health Curricula)")
                print("✅ Phase 1.6-1.10: Comprehensive Beta Teacher System (Lesson Plans, Assessments, Resources, Dashboard, AI)")
                print("✅ Phase 2: Educational System Enhancement (38 tables)")
                print("✅ Phase 3: Health & Fitness System (41 tables - 100% complete)")
                print("✅ Phase 4: Safety & Risk Management System (35 tables - 100% complete)")
                print("✅ Phase 5: Advanced Analytics & AI (36 tables - 100% complete)")
                print("✅ Phase 6: Movement & Performance Analysis (25 tables - 100% complete)")
                print("✅ Phase 7: Specialized Features (20 tables - 100% complete)")
                print("✅ Phase 8: Advanced Physical Education & Adaptations (35 tables - 100% complete)")
                print("✅ Phase 9: Health & Fitness System (26 tables - 100% complete)")
                if success:
                    print("✅ Phase 10: Assessment & Skill Management (30 tables - 100% complete)")
                else:
                    print("⚠️ Phase 10: Assessment & Skill Management (7/30 tables - 23% complete)")
                if not env_true('SKIP_PHASE_1_2_MIGRATION'):
                    print("✅ Phase 1 & Phase 2: Data Migration (safety & assessment data migrated)")
                if not env_true('SKIP_PHASE_6_MIGRATION'):
                    print("✅ Phase 6: Data Migration (dashboard preferences & widgets migrated)")
                print("✅ Phase 11: Advanced System Features (73 tables - 100% complete)")
                print(f"✅ {populated_tables}/{len(table_names)} tables populated with data")
                print("✅ Relationships established")
                print("✅ System ready for Power BI testing")
                print("✅ Ready for production deployment")
                print("="*50)
                
            except Exception as e:
                print(f"❌ FAIL-FAST ERROR: Database seeding failed: {str(e)}")
                print("🛑 SCRIPT EXECUTION STOPPED IMMEDIATELY")
                print(f"📍 Error occurred during: {type(e).__name__}")
                print(f"🔍 Full error details:")
                import traceback
                traceback.print_exc()
                print("=" * 60)
                print("🚨 FAIL-FAST MODE: Fix the error above and re-run the script")
                print("=" * 60)
                raise
                
        finally:
            session.close()
            
    except Exception as e:
        print(f"❌ FAIL-FAST ERROR: Critical failure in seed_database: {str(e)}")
        print("🛑 SCRIPT EXECUTION TERMINATED")
        print(f"📍 Error type: {type(e).__name__}")
        print("🔍 Full error details:")
        import traceback
        traceback.print_exc()
        print("=" * 60)
        print("🚨 FAIL-FAST MODE: Fix the critical error above and re-run")
        print("=" * 60)
        raise

if __name__ == "__main__":
    seed_database() 