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
from app.models.resource_management.resource_management import (
    ResourceUsage, ResourceThreshold, ResourceOptimization, 
    OptimizationEvent, ResourceSharing
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
from app.models.resource_management.optimization import ResourceOptimizationThreshold, ResourceOptimizationRecommendation, ResourceOptimizationEvent

# Import User model after all other models to ensure proper registration order
from app.models.core.user import User

# Import seed functions
from .seed_users import seed_users
from .seed_subject_categories import seed_subject_categories
from .seed_lessons import seed_lessons
from .seed_activities import seed_activities
from .seed_students import seed_students
from .seed_classes import seed_classes
from .seed_class_students import seed_class_students
from .seed_routines import seed_routines
from .seed_exercises import seed_exercises
from .seed_risk_assessments import seed_risk_assessments
from .seed_routine_performance import seed_routine_performance
from .seed_performance_metrics import seed_performance_metrics
from .seed_student_activity_data import seed_student_activity_data
from .seed_safety_incidents import seed_safety_incidents
from .seed_safety_checks import seed_safety_checks
from .seed_equipment_checks import seed_equipment_checks
from .seed_environmental_checks import seed_environmental_checks
from .seed_activity_categories import seed_activity_categories
from .seed_activity_plans import seed_activity_plans
from .seed_activity_progressions import seed_activity_progressions
from .seed_activity_category_associations import seed_activity_category_associations
from .seed_movement_analysis import seed_movement_analysis
from .seed_activity_adaptations import seed_activity_adaptations
from .seed_assessment_criteria import seed_assessment_criteria
from .seed_skill_assessments import seed_skill_assessments
from .seed_user_preferences import seed_user_preferences
from .seed_memories import seed_memories
from .seed_assistant_profiles import seed_assistant_profiles
from .seed_skill_progress import seed_skill_progress

# Import the new comprehensive seeding scripts
from .seed_dashboard_system import seed_dashboard_system
from .seed_gpt_system import seed_gpt_system
from .seed_security_system import seed_security_system

def seed_database():
    """Seed the database with initial data."""
    print("Running seed data script...")
    try:
        # Ensure all tables are created first
        from app.models.shared_base import SharedBase
        
        # Import specific models to avoid conflicts - removed broad import
        # import app.models  # This was causing conflicts with dashboard models
        
        session = SessionLocal()
        try:
            # Step 1: Drop all tables and recreate them (simplified approach)
            print("Dropping and recreating tables...")
            try:
                # Get all table names first
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
                        'voice_templates', 'dashboard_users', 'dashboard_teams', 'dashboard_projects', 'teams', 'organization_projects',
                        'gpt_definitions', 'core_gpt_definitions', 'gpt_interaction_contexts', 'gpt_context_gpts', 'goals', 'activity_categories', 
                        'roles', 'permissions', 'dashboard_tools', 'shared_contexts', 'courses', 'rubrics', 'assignments', 'ai_suites', 'ai_tools',
                        'injury_preventions', 'injury_risk_factors', 'safety_guidelines', 'assistant_profiles', 'assistant_capabilities',
                        'subject_categories', 'lessons', 'performance_thresholds', 'equipment_base', 'equipment', 'gpt_subscription_plans', 'gpt_subscriptions', 'dashboard_gpt_subscriptions',
                        'gpt_usage_history', 'gpt_subscription_usage', 'gpt_subscription_billing', 'gpt_subscription_payments', 'gpt_subscription_invoices', 'gpt_subscription_refunds'
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
                # Core system tables
                seed_users(session)
                session.commit()
                
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
                
                # Student and class organization
                seed_students(session)
                session.commit()
                
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
                
                seed_safety_checks(session)
                session.commit()
                
                seed_equipment_checks(session)
                session.commit()
                
                seed_environmental_checks(session)
                session.commit()
                
                # Performance tracking
                seed_routines(session)
                session.commit()
                
                seed_routine_performance(session)
                session.commit()
                
                seed_performance_metrics(session)
                session.commit()
                
                seed_student_activity_data(session)
                session.commit()
                
                # Assessment and progress tracking
                seed_assessment_criteria(session)
                session.commit()
                
                seed_skill_assessments(session)
                session.commit()
                
                seed_skill_progress(session)
                session.commit()
                
                # NEW: Comprehensive system seeding
                print("\n" + "="*50)
                print("COMPREHENSIVE SYSTEM SEEDING")
                print("="*50)
                
                # Dashboard system
                seed_dashboard_system(session)
                session.commit()
                
                # GPT/AI system
                seed_gpt_system(session)
                session.commit()
                
                # Security system
                seed_security_system(session)
                session.commit()
                
                # Final count summary
                print("\n" + "="*50)
                print("FINAL SEEDING SUMMARY")
                print("="*50)
                
                # Count all major tables
                from app.models.shared_base import SharedBase
                inspector = inspect(engine)
                table_names = inspector.get_table_names()
                
                for table_name in sorted(table_names):
                    try:
                        count = session.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
                        print(f"{table_name}: {count} records")
                    except Exception as e:
                        print(f"{table_name}: Error counting - {e}")
                
                print("="*50)
                print("Database seeded successfully!")
                
            except Exception as e:
                print(f"Error seeding data: {str(e)}")
                session.rollback()
                raise
                
        finally:
            session.close()
            
    except Exception as e:
        print(f"Error in seed_database: {str(e)}")
        raise

if __name__ == "__main__":
    seed_database() 