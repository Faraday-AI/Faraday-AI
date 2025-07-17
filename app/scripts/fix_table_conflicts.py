#!/usr/bin/env python3
"""
Script to fix table name conflicts by renaming tables to unique names.
"""

import os
import sys
import re
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Define table conflicts and their resolutions
TABLE_CONFLICTS = {
    # Rate limiting tables
    'rate_limits': {
        'app/models/security/rate_limit/rate_limit.py': 'rate_limits',  # Keep original
        'app/dashboard/models/security.py': 'dashboard_rate_limits'  # Already renamed
    },
    
    # Progress notes tables - all different purposes
    'progress_notes': {
        'app/models/health_fitness/progress/progress_tracking.py': 'health_fitness_progress_notes',
        'app/models/physical_education/progress/models.py': 'physical_education_progress_notes', 
        'app/models/physical_education/exercise/models.py': 'exercise_progress_notes'
    },
    
    # Dashboard widgets - need to check if truly different
    'dashboard_widgets': {
        'app/dashboard/models/dashboard_models.py': 'dashboard_widgets',  # Keep original
        'app/models/dashboard/widgets/widget.py': 'core_dashboard_widgets'  # Already different name
    },
    
    # Context tables - need to check if truly different
    'context_metrics': {
        'app/models/context/metrics/metrics.py': 'context_metrics',  # Keep original
        'app/models/gpt/context/models.py': 'gpt_context_metrics'  # Rename
    },
    
    'context_sharing': {
        'app/models/context/base/shared.py': 'context_sharing',  # Keep original
        'app/models/gpt/context/models.py': 'gpt_context_sharing'  # Rename
    },
    
    'context_summaries': {
        'app/models/context/base/summary.py': 'context_summaries',  # Keep original
        'app/models/gpt/context/models.py': 'gpt_context_summaries'  # Rename
    },
    
    'context_backups': {
        'app/models/context/base/summary.py': 'context_backups',  # Keep original
        'app/models/gpt/context/models.py': 'gpt_context_backups'  # Rename
    },
    
    'context_interactions': {
        'app/models/context/base/context.py': 'context_interactions',  # Keep original
        'app/models/gpt/context/models.py': 'gpt_context_interactions'  # Rename
    },
    
    # Security tables - need to check if truly different
    'security_policies': {
        'app/models/security/policy/security.py': 'security_policies',  # Keep original
        'app/dashboard/models/security.py': 'dashboard_security_policies'  # Rename
    },
    
    'ip_allowlist': {
        'app/models/security/policy/security.py': 'ip_allowlist',  # Keep original
        'app/dashboard/models/security.py': 'dashboard_ip_allowlist'  # Rename
    },
    
    'ip_blocklist': {
        'app/models/security/policy/security.py': 'ip_blocklist',  # Keep original
        'app/dashboard/models/security.py': 'dashboard_ip_blocklist'  # Rename
    },
    
    'sessions': {
        'app/models/security/policy/security.py': 'sessions',  # Keep original
        'app/dashboard/models/security.py': 'dashboard_sessions'  # Rename
    },
    
    # Equipment tables - need to check if truly different
    'equipment': {
        'app/models/skill_assessment/equipment/equipment.py': 'skill_assessment_equipment',
        'app/models/physical_education/safety/models.py': 'physical_education_safety_equipment',
        'app/models/physical_education/equipment/models.py': 'physical_education_equipment'
    },
    
    'equipment_maintenance': {
        'app/models/skill_assessment/equipment/equipment.py': 'skill_assessment_equipment_maintenance',
        'app/models/physical_education/safety/models.py': 'physical_education_safety_equipment_maintenance',
        'app/models/physical_education/equipment/models.py': 'physical_education_equipment_maintenance'
    },
    
    # Safety tables - need to check if truly different
    'safety_alerts': {
        'app/models/skill_assessment/safety/safety.py': 'skill_assessment_safety_alerts',
        'app/models/physical_education/safety/models.py': 'physical_education_safety_alerts'
    },
    
    'environmental_checks': {
        'app/models/skill_assessment/safety/safety.py': 'skill_assessment_environmental_checks',
        'app/models/physical_education/safety/models.py': 'physical_education_environmental_checks'
    },
    
    # Health tables - need to check if truly different
    'health_conditions': {
        'app/models/health_fitness/metrics/health.py': 'health_fitness_health_conditions',
        'app/models/physical_education/health/models.py': 'physical_education_health_conditions'
    },
    
    'health_alerts': {
        'app/models/health_fitness/metrics/health.py': 'health_fitness_health_alerts',
        'app/models/physical_education/health/models.py': 'physical_education_health_alerts'
    },
    
    'health_checks': {
        'app/models/health_fitness/metrics/health.py': 'health_fitness_health_checks',
        'app/models/physical_education/health/models.py': 'physical_education_health_checks'
    },
    
    # Fitness tables - need to check if truly different
    'fitness_metrics': {
        'app/models/health_fitness/metrics/health_metrics.py': 'health_fitness_metrics',
        'app/models/physical_education/fitness/models.py': 'physical_education_fitness_metrics'
    },
    
    'fitness_goals': {
        'app/models/health_fitness/goals/fitness_goals.py': 'health_fitness_goals',
        'app/models/physical_education/student/health.py': 'physical_education_student_fitness_goals',
        'app/models/physical_education/fitness/models.py': 'physical_education_fitness_goals'
    },
    
    'fitness_goal_progress': {
        'app/models/health_fitness/goals/fitness_goals.py': 'health_fitness_goal_progress',
        'app/models/physical_education/student/health.py': 'physical_education_student_fitness_goal_progress',
        'app/models/physical_education/fitness/models.py': 'physical_education_fitness_goal_progress'
    },
    
    # Workout tables - need to check if truly different
    'workouts': {
        'app/models/health_fitness/workouts/workout.py': 'health_fitness_workouts',
        'app/models/health_fitness/workouts/workout_models.py': 'health_fitness_workout_models',
        'app/models/physical_education/exercise/models.py': 'physical_education_exercise_workouts',
        'app/models/physical_education/workout/models.py': 'physical_education_workouts'
    },
    
    'workout_sessions': {
        'app/models/health_fitness/workouts/workout.py': 'health_fitness_workout_sessions',
        'app/models/physical_education/workout/models.py': 'physical_education_workout_sessions'
    },
    
    'workout_plans': {
        'app/models/health_fitness/workouts/workout.py': 'health_fitness_workout_plans',
        'app/models/physical_education/workout/models.py': 'physical_education_workout_plans'
    },
    
    'workout_plan_workouts': {
        'app/models/health_fitness/workouts/workout.py': 'health_fitness_workout_plan_workouts',
        'app/models/physical_education/workout/models.py': 'physical_education_workout_plan_workouts'
    },
    
    # Movement analysis tables - need to check if truly different
    'movement_analyses': {
        'app/models/movement_analysis/analysis/movement_analysis.py': 'movement_analysis_analyses',
        'app/models/physical_education/movement_analysis/models.py': 'physical_education_movement_analyses'
    },
    
    'movement_metrics': {
        'app/models/movement_analysis/analysis/movement_analysis.py': 'movement_analysis_metrics',
        'app/models/physical_education/movement_analysis/models.py': 'physical_education_movement_metrics'
    },
    
    'movement_patterns': {
        'app/models/movement_analysis/analysis/movement_analysis.py': 'movement_analysis_patterns',
        'app/models/physical_education/movement_analysis/models.py': 'physical_education_movement_patterns',
        'app/models/physical_education/movement_analysis/movement_models.py': 'physical_education_movement_pattern_models'
    },
    
    # Notification tables - need to check if truly different
    'notifications': {
        'app/models/context/notifications/notification.py': 'context_notifications',
        'app/models/resource_management/resource_notification_management.py': 'resource_management_notifications',
        'app/dashboard/models/notification.py': 'dashboard_notifications'
    },
    
    'notification_channels': {
        'app/models/context/notifications/notification.py': 'context_notification_channels',
        'app/models/resource_management/resource_notification_management.py': 'resource_management_notification_channels'
    },
    
    # Dashboard tables - need to check if truly different
    'dashboard_searches': {
        'app/models/dashboard/filters/filter.py': 'dashboard_filter_searches',
        'app/dashboard/models/dashboard.py': 'dashboard_searches'
    },
    
    'dashboard_exports': {
        'app/models/dashboard/sharing/share.py': 'dashboard_share_exports',
        'app/dashboard/models/dashboard.py': 'dashboard_exports'
    },
    
    'dashboard_themes': {
        'app/models/dashboard/themes/theme.py': 'dashboard_theme_configs',
        'app/dashboard/models/dashboard.py': 'dashboard_themes'
    },
    
    # Tool tables - need to check if truly different
    'tools': {
        'app/models/dashboard/models/tool_registry.py': 'dashboard_tool_registry',
        'app/dashboard/models/tool_registry.py': 'dashboard_tools'
    },
    
    # Competition tables - need to check if truly different
    'event_participants': {
        'app/models/competition/participants/event_participant.py': 'competition_event_participants',
        'app/models/competition/base/competition.py': 'competition_base_event_participants'
    },
    
    'competition_participants': {
        'app/models/competition/participants/participant.py': 'competition_participants',
        'app/models/competition/base/competition.py': 'competition_base_participants'
    },
    
    'competition_events': {
        'app/models/competition/events/event.py': 'competition_events',
        'app/models/competition/base/competition.py': 'competition_base_events'
    },
    
    # Skill assessment tables - need to check if truly different
    'skill_assessments': {
        'app/models/physical_education/skill_assessment/skill_assessment_models.py': 'physical_education_skill_assessments',
        'app/models/physical_education/assessment/models.py': 'physical_education_assessment_skill_assessments'
    },
    
    # Routine tables - need to check if truly different
    'routines': {
        'app/models/physical_education/routine/models.py': 'physical_education_routines',
        'app/models/physical_education/base/physical_education.py': 'physical_education_base_routines'
    },
    
    'routine_performance': {
        'app/models/physical_education/routine/routine_performance_models.py': 'physical_education_routine_performance',
        'app/models/physical_education/base/physical_education.py': 'physical_education_base_routine_performance'
    },
    
    # Health records tables - need to check if truly different
    'health_records': {
        'app/models/physical_education/student/models.py': 'physical_education_student_health_records',
        'app/models/physical_education/student/health.py': 'physical_education_student_health_health_records',
        'app/models/physical_education/student/student.py': 'physical_education_student_student_health_records'
    },
    
    # Resource tables - need to check if truly different
    'resource_usage': {
        'app/models/resource_management/resource_management.py': 'resource_management_usage',
        'app/models/resource_management/resource_notification_management.py': 'resource_management_notification_usage',
        'app/models/resource_management/usage/models.py': 'resource_management_usage_models'
    },
    
    'resource_sharing': {
        'app/models/resource_management/resource_management.py': 'resource_management_sharing',
        'app/models/resource_management/resource_notification_management.py': 'resource_management_notification_sharing',
        'app/models/resource_management/sharing/models.py': 'resource_management_sharing_models'
    },
    
    # Dashboard user tables - need to check if truly different
    'dashboard_users': {
        'app/dashboard/models.py': 'dashboard_users_legacy',
        'app/dashboard/models/user.py': 'dashboard_users'
    },
    
    # Tool usage log tables - need to check if truly different
    'tool_usage_logs': {
        'app/dashboard/models.py': 'dashboard_tool_usage_logs_legacy',
        'app/dashboard/models/tool_usage_log.py': 'dashboard_tool_usage_logs'
    },
    
    # Marketplace listing tables - need to check if truly different
    'marketplace_listings': {
        'app/dashboard/models.py': 'dashboard_marketplace_listings_legacy',
        'app/dashboard/models/marketplace_listing.py': 'dashboard_marketplace_listings'
    },
    
    # Category tables - need to check if truly different
    'categories': {
        'app/dashboard/models.py': 'dashboard_categories_legacy',
        'app/dashboard/models/category.py': 'dashboard_categories'
    },
    
    # Dashboard notification tables - need to check if truly different
    'dashboard_notifications': {
        'app/dashboard/models/notification_models.py': 'dashboard_notification_models',
        'app/dashboard/models/dashboard.py': 'dashboard_notifications'
    }
}

def fix_table_conflicts():
    """Fix table name conflicts by renaming tables."""
    # Get the Faraday-AI directory (parent of app directory)
    app_dir = Path(__file__).parent.parent.parent
    
    for table_name, file_mappings in TABLE_CONFLICTS.items():
        print(f"\n🔧 Fixing conflicts for table: {table_name}")
        
        for file_path, new_table_name in file_mappings.items():
            full_path = app_dir / file_path
            
            if not full_path.exists():
                print(f"   ⚠️  File not found: {file_path}")
                continue
                
            print(f"   📄 {file_path} -> {new_table_name}")
            
            # Read the file
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Replace the table name
            old_pattern = f"__tablename__ = \"{table_name}\""
            new_pattern = f"__tablename__ = \"{new_table_name}\""
            
            if old_pattern in content:
                content = content.replace(old_pattern, new_pattern)
                
                # Write back to file
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
                print(f"   ✅ Updated {file_path}")
            else:
                print(f"   ⚠️  Table name not found in {file_path}")

def main():
    print("🔧 Starting table conflict resolution...")
    fix_table_conflicts()
    print("\n✅ Table conflict resolution complete!")

if __name__ == "__main__":
    main() 