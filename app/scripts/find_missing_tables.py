#!/usr/bin/env python3
"""
Compare Previous 537 Tables vs Current Database
Identify which 18 tables are missing
"""
import os
import sys
from sqlalchemy import create_engine, text

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.core.database import DATABASE_URL

# Tables from previous run (537 tables)
previous_tables = {
    'access_control_permissions', 'access_control_role_permissions', 'access_control_roles',
    'access_control_user_roles', 'activities', 'activity_assessments', 'activity_categories',
    'activity_category_associations', 'activity_environmental_impacts', 'activity_injury_preventions',
    'activity_logs', 'activity_performances', 'activity_plan_activities', 'activity_plan_objectives',
    'activity_plans', 'activity_plans_planning', 'activity_preferences', 'activity_progressions',
    'activity_tracking', 'adaptation_activity_preferences', 'adapted_activities', 'adapted_activity_categories',
    'adapted_activity_plan_activities', 'adapted_activity_plans', 'adapted_exercises', 'adapted_performance_metrics',
    'adapted_routine_activities', 'adapted_routine_performances', 'adapted_routine_performances_backup',
    'adapted_routines', 'adapted_workout_exercises', 'adapted_workouts', 'ai_assistant_analytics',
    'ai_assistant_configs', 'ai_assistant_conversations', 'ai_assistant_feedback', 'ai_assistant_messages',
    'ai_assistant_templates', 'ai_assistant_usage', 'ai_lesson_suggestions', 'ai_suites', 'ai_tools',
    'analysis_movement_feedback', 'analytics_events', 'api_keys', 'assessment_categories', 'assessment_changes',
    'assessment_checklists', 'assessment_criteria', 'assessment_questions', 'assessment_rubrics',
    'assessment_standards', 'assessment_template_category_associations', 'assessment_template_sharing',
    'assessment_template_usage', 'assessment_templates', 'assignments', 'assistant_capabilities',
    'assistant_profiles', 'audit_logs', 'avatar_customizations', 'avatar_templates', 'avatars',
    'beta_avatars', 'beta_lesson_plan_activities', 'beta_teacher_preferences', 'beta_testing_feature_flags',
    'beta_testing_feedback', 'beta_testing_notifications', 'beta_testing_participants', 'beta_testing_programs',
    'beta_testing_reports', 'beta_testing_survey_responses', 'beta_testing_surveys', 'beta_testing_usage_analytics',
    'beta_widgets', 'cache_entries', 'cache_metrics', 'cache_policies', 'circuit_breaker_history',
    'circuit_breaker_metrics', 'circuit_breaker_policies', 'circuit_breakers', 'class_attendance', 'class_plans',
    'class_schedules', 'class_school_assignments', 'collection_resource_associations', 'collection_sharing',
    'comments', 'competition_base_event_participants', 'competition_base_events', 'competition_base_participants',
    'competitions', 'context_data', 'core_activities', 'core_dashboard_widgets', 'core_gpt_definitions',
    'core_gpt_performance', 'course_enrollments', 'courses', 'curriculum', 'curriculum_lessons',
    'curriculum_standard_association', 'curriculum_standards', 'curriculum_units', 'dashboard_analytics',
    'dashboard_api_keys', 'dashboard_audit_logs', 'dashboard_categories', 'dashboard_context_backups',
    'dashboard_context_gpts', 'dashboard_context_interactions', 'dashboard_context_metrics',
    'dashboard_context_optimizations', 'dashboard_context_summaries', 'dashboard_context_templates',
    'dashboard_context_validations', 'dashboard_feedback', 'dashboard_filter_configs', 'dashboard_filter_searches',
    'dashboard_filters', 'dashboard_gpt_contexts', 'dashboard_gpt_integrations', 'dashboard_gpt_subscriptions',
    'dashboard_gpt_usage_history', 'dashboard_ip_allowlist', 'dashboard_ip_blocklist', 'dashboard_marketplace_listings',
    'dashboard_notification_channels', 'dashboard_notification_models', 'dashboard_notification_preferences',
    'dashboard_optimization_events', 'dashboard_projects', 'dashboard_rate_limits', 'dashboard_resource_optimizations',
    'dashboard_resource_sharing', 'dashboard_resource_thresholds', 'dashboard_resource_usage',
    'dashboard_security_policies', 'dashboard_sessions', 'dashboard_share_configs', 'dashboard_share_exports',
    'dashboard_shared_contexts', 'dashboard_shares', 'dashboard_team_members', 'dashboard_teams',
    'dashboard_theme_configs', 'dashboard_tool_usage_logs', 'dashboard_tools', 'dashboard_users',
    'dashboard_widget_instances', 'dashboard_widgets', 'dashboards', 'department_members', 'departments',
    'drivers_ed_assessment_rubrics', 'drivers_ed_curriculum_units', 'drivers_ed_instructor_certifications',
    'drivers_ed_lesson_activities', 'drivers_ed_lesson_plans', 'drivers_ed_safety_incidents',
    'drivers_ed_safety_protocols', 'drivers_ed_student_progress', 'drivers_ed_vehicles',
    'educational_class_students', 'educational_classes', 'educational_resources', 'educational_teacher_availability',
    'educational_teacher_certifications', 'educational_teachers', 'emergency_contacts', 'environmental_alerts',
    'environmental_conditions', 'equipment', 'equipment_base', 'equipment_categories', 'equipment_checks',
    'equipment_conditions', 'equipment_maintenance', 'equipment_status', 'equipment_types', 'equipment_usage',
    'exercise_base', 'exercise_metrics', 'exercise_performances', 'exercise_progress', 'exercise_progress_notes',
    'exercise_progressions', 'exercise_routines', 'exercise_sets', 'exercise_techniques', 'exercise_variations',
    'exercise_videos', 'exercises', 'feedback', 'feedback_actions', 'feedback_attachments', 'feedback_categories',
    'feedback_comments', 'feedback_project_comments', 'feedback_project_members', 'feedback_project_resources',
    'feedback_project_tasks', 'feedback_projects', 'feedback_responses', 'feedback_user_tool_settings', 'filters',
    'fitness_assessments', 'fitness_goal_progress_detailed', 'fitness_goal_progress_general', 'fitness_goals',
    'fitness_health_metric_history', 'fitness_health_metrics', 'fitness_metric_history', 'fitness_metrics',
    'food_items', 'foods', 'general_assessment_criteria', 'general_assessment_history', 'general_assessments',
    'general_health_metric_history', 'general_health_metrics', 'general_skill_assessments', 'general_skill_progress',
    'goal_activities', 'goal_adjustments', 'goal_dependencies', 'goal_milestones', 'goal_recommendations', 'goals',
    'gpt_analytics', 'gpt_categories', 'gpt_context_backups', 'gpt_context_gpts', 'gpt_context_interactions',
    'gpt_context_metrics', 'gpt_context_sharing', 'gpt_context_summaries', 'gpt_definitions', 'gpt_feedback',
    'gpt_integrations', 'gpt_interaction_contexts', 'gpt_performance', 'gpt_sharing', 'gpt_subscription_billing',
    'gpt_subscription_invoices', 'gpt_subscription_payments', 'gpt_subscription_plans', 'gpt_subscription_refunds',
    'gpt_subscription_usage', 'gpt_subscriptions', 'gpt_usage', 'gpt_usage_history', 'gpt_versions', 'grade_levels',
    'grades', 'health_alerts', 'health_assessment_rubrics', 'health_checks', 'health_conditions',
    'health_curriculum_units', 'health_equipment', 'health_fitness_exercises', 'health_fitness_goal_progress',
    'health_fitness_goals', 'health_fitness_health_alerts', 'health_fitness_health_checks',
    'health_fitness_health_conditions', 'health_fitness_metric_thresholds', 'health_fitness_progress_notes',
    'health_fitness_workout_exercises', 'health_fitness_workout_plan_workouts', 'health_fitness_workout_plans',
    'health_fitness_workout_sessions', 'health_fitness_workouts', 'health_incidents', 'health_instructor_certifications',
    'health_lesson_activities', 'health_lesson_plans', 'health_metric_history', 'health_metric_thresholds',
    'health_metrics', 'health_safety_protocols', 'health_student_progress', 'injury_prevention_risk_assessments',
    'injury_preventions', 'injury_risk_assessments', 'injury_risk_factor_safety_guidelines', 'injury_risk_factors',
    'instructors', 'ip_allowlist', 'ip_blocklist', 'job', 'job_run_details', 'learning_path_steps',
    'lesson_plan_activities', 'lesson_plan_categories', 'lesson_plan_objectives', 'lesson_plan_sharing',
    'lesson_plan_templates', 'lesson_plan_usage', 'lesson_plans', 'lessons', 'maintenance_records',
    'meal_food_items', 'meal_plans', 'meals', 'medical_conditions', 'memory_interactions', 'message_board_posts',
    'message_boards', 'messages', 'movement_analysis_analyses', 'movement_analysis_metrics', 'movement_analysis_patterns',
    'movement_feedback', 'movement_sequences', 'nutrition_education', 'nutrition_goals', 'nutrition_logs',
    'nutrition_plans', 'nutrition_recommendations', 'optimization_events', 'organization_collaborations',
    'organization_feedback', 'organization_members', 'organization_projects', 'organization_resources',
    'organization_roles', 'organization_settings', 'organizations', 'pe_activity_adaptation_history',
    'pe_activity_adaptations', 'pe_activity_preferences', 'pe_adaptation_history', 'pe_lesson_plans',
    'performance_logs', 'performance_thresholds', 'permission_overrides', 'permissions',
    'physical_education_activity_adaptations', 'physical_education_attendance', 'physical_education_class_routines',
    'physical_education_class_students', 'physical_education_classes', 'physical_education_curriculum_units',
    'physical_education_environmental_checks', 'physical_education_equipment', 'physical_education_equipment_maintenance',
    'physical_education_meal_foods', 'physical_education_meals', 'physical_education_movement_analyses',
    'physical_education_movement_analysis', 'physical_education_movement_metrics',
    'physical_education_movement_pattern_models', 'physical_education_movement_patterns',
    'physical_education_nutrition_education', 'physical_education_nutrition_goals',
    'physical_education_nutrition_logs', 'physical_education_nutrition_plans',
    'physical_education_nutrition_recommendations', 'physical_education_routine_performance',
    'physical_education_routines', 'physical_education_safety_alerts',
    'physical_education_student_fitness_goal_progress', 'physical_education_student_fitness_goals',
    'physical_education_student_health_health_records', 'physical_education_student_student_health_records',
    'physical_education_teachers', 'physical_education_workout_exercises', 'physical_education_workouts',
    'planning_history', 'planning_metrics', 'policy_security_audits', 'prevention_assessments', 'prevention_measures',
    'progress', 'progress_goals', 'progress_metrics', 'progress_tracking', 'project_comments', 'project_feedback',
    'project_members', 'project_milestones', 'project_resources', 'project_roles', 'project_settings', 'project_tasks',
    'rate_limit_logs', 'rate_limit_metrics', 'rate_limit_policies', 'rate_limits', 'resource_alerts',
    'resource_categories', 'resource_category_associations', 'resource_collections', 'resource_downloads',
    'resource_events', 'resource_favorites', 'resource_management_sharing', 'resource_management_usage',
    'resource_optimization_events', 'resource_optimization_recommendations', 'resource_optimization_thresholds',
    'resource_optimizations', 'resource_reviews', 'resource_sharing', 'resource_thresholds', 'resource_usage',
    'risk_assessments', 'role_hierarchy', 'role_permissions', 'role_templates', 'roles', 'routine_activities',
    'routine_metrics', 'routine_performance_metrics', 'routine_performances', 'routine_progress', 'rubrics', 'safety',
    'safety_checklist_items', 'safety_checklists', 'safety_checks', 'safety_guidelines', 'safety_incident_base',
    'safety_incidents', 'safety_measures', 'safety_protocols', 'safety_reports', 'school_academic_years',
    'school_facilities', 'schools', 'security_audit_logs', 'security_audits', 'security_general_audit_logs',
    'security_incident_management', 'security_incidents', 'security_logs', 'security_policies', 'security_preferences',
    'security_rules', 'sessions', 'shared_contexts', 'skill_assessment_assessment_criteria',
    'skill_assessment_assessment_history', 'skill_assessment_assessment_metrics', 'skill_assessment_assessment_results',
    'skill_assessment_assessments', 'skill_assessment_environmental_checks', 'skill_assessment_equipment_checks',
    'skill_assessment_risk_assessments', 'skill_assessment_safety_alerts', 'skill_assessment_safety_checks',
    'skill_assessment_safety_incidents', 'skill_assessment_safety_protocols', 'skill_assessment_skill_assessments',
    'skill_progress', 'student_activity_adaptations', 'student_activity_performances', 'student_activity_progressions',
    'student_adaptation_history', 'student_avatar_customizations', 'student_exercise_progress', 'student_health',
    'student_health_fitness_goals', 'student_health_goal_progress', 'student_health_goal_recommendations',
    'student_health_skill_assessments', 'student_school_enrollments', 'student_workouts', 'students',
    'subject_assistant', 'subject_categories', 'subjects', 'teacher_achievement_progress', 'teacher_achievements',
    'teacher_activity_logs', 'teacher_availability', 'teacher_certification_base', 'teacher_certifications',
    'teacher_dashboard_layouts', 'teacher_goals', 'teacher_learning_paths', 'teacher_notifications',
    'teacher_preferences', 'teacher_qualifications', 'teacher_quick_actions', 'teacher_registrations',
    'teacher_schedules', 'teacher_school_assignments', 'teacher_specializations', 'teacher_statistics', 'teachers',
    'team_members', 'teams', 'template_category_associations', 'tool_assignments', 'tracking_history', 'tracking_metrics',
    'tracking_status', 'user_activities', 'user_avatar_customizations', 'user_avatars', 'user_behaviors',
    'user_comparisons', 'user_engagements', 'user_insights', 'user_management_preferences',
    'user_management_user_organizations', 'user_management_voice_preferences', 'user_memories', 'user_performances',
    'user_predictions', 'user_preference_categories', 'user_preference_template_assignments',
    'user_preference_templates', 'user_preferences', 'user_profiles', 'user_recommendations', 'user_roles',
    'user_sessions', 'user_tool_settings', 'user_tools', 'user_trends', 'users', 'voice_templates', 'voices',
    'webhooks', 'workout_exercises', 'workout_performances', 'workout_plan_workouts', 'workout_plans',
    'workout_sessions', 'workoutbase', 'workouts'
}

def find_missing_tables():
    """Compare previous 537 tables with current database."""
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """))
        
        current_tables = set(row[0] for row in result.fetchall())
    
    # Find missing tables
    missing = previous_tables - current_tables
    extra = current_tables - previous_tables
    
    print("=" * 60)
    print("COMPARING PREVIOUS (537) vs CURRENT DATABASE")
    print("=" * 60)
    print(f"\nPrevious run had: {len(previous_tables)} tables")
    print(f"Current database has: {len(current_tables)} tables")
    print(f"Difference: {len(current_tables) - len(previous_tables)} tables")
    
    if missing:
        print(f"\n❌ Tables in PREVIOUS run but NOT in CURRENT database ({len(missing)}):")
        for table in sorted(missing):
            print(f"   • {table}")
    else:
        print("\n✅ All previous tables exist in current database")
    
    if extra:
        print(f"\n➕ Tables in CURRENT database but NOT in PREVIOUS run ({len(extra)}):")
        for table in sorted(extra):
            print(f"   • {table}")
    
    # Check for drivers_ed and health_* tables
    drivers_ed_tables = [t for t in missing if 'drivers_ed' in t]
    health_tables = [t for t in missing if t.startswith('health_') and 'fitness' not in t and 'curriculum' not in t and 'equipment' not in t]
    
    if drivers_ed_tables:
        print(f"\n📚 Drivers Ed tables missing ({len(drivers_ed_tables)}):")
        for t in sorted(drivers_ed_tables):
            print(f"   • {t}")
    
    if health_tables:
        print(f"\n🏥 Health-only tables missing ({len(health_tables)}):")
        for t in sorted(health_tables):
            print(f"   • {t}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    try:
        find_missing_tables()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

