"""
Phase 5: Advanced Analytics & AI
Seeds GPT & AI Integration and Dashboard Analytics tables
"""

import random
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
from sqlalchemy.orm import Session
from sqlalchemy import text

# Global variables removed - using parameter passing instead


def seed_phase5_analytics_ai(session: Session, user_ids: List[int] = None, organization_ids: List[int] = None) -> Dict[str, int]:
    """
    Complete Phase 5 Advanced Analytics & AI
    Seeds GPT & AI Integration and Dashboard Analytics tables
    """
    print("="*70)
    print("🤖 PHASE 5: ADVANCED ANALYTICS & AI")
    print("="*70)
    print("📊 Seeding GPT & AI Integration systems")
    print("📈 Dashboard Analytics & Performance tracking")
    print("🔧 Resource optimization & management")
    print("="*70)
    
    results = {}
    
    # Get reference data
    if not user_ids:
        user_ids = get_table_ids(session, "users")
    if not organization_ids:
        organization_ids = get_table_ids(session, "organizations")
    
    # Get project IDs dynamically (these are auto-generated in previous phases)
    project_ids = get_table_ids(session, "dashboard_projects")
    if not project_ids:
        project_ids = [1, 2, 3]  # Fallback if no projects exist
    
    print(f"  📊 Found {len(user_ids)} users, {len(organization_ids)} organizations, {len(project_ids)} projects")
    
    # 5.1 GPT & AI Integration (18 tables)
    print("\n🤖 GPT & AI INTEGRATION (18 tables)")
    print("-" * 50)
    results.update(seed_gpt_ai_integration(session, user_ids, organization_ids, project_ids))
    
    # 5.2 Dashboard Analytics (17 tables)
    print("\n📈 DASHBOARD ANALYTICS (17 tables)")
    print("-" * 50)
    # Get context IDs from the GPT integration results
    context_ids = get_table_ids(session, "gpt_interaction_contexts")
    if not context_ids:
        print("  ⚠️ No context IDs found, creating fallback")
        context_ids = [1, 2, 3, 4, 5]
    
    # Seed AI and analytics data (moved from Phase 1) - do this after GPT integration
    print("  🔧 Seeding AI and analytics data...")
    try:
        from app.scripts.seed_data.seed_ai_analytics_data import seed_ai_analytics_data
        ai_analytics_count = seed_ai_analytics_data(session)
        session.commit()
        print(f"  ✅ AI and analytics data seeded: {ai_analytics_count} records")
        results['ai_analytics'] = ai_analytics_count
    except Exception as e:
        print(f"  ⚠️ Could not seed AI and analytics data: {e}")
        results['ai_analytics'] = 0
    
    results.update(seed_dashboard_analytics(session, user_ids, organization_ids, project_ids, context_ids))
    
    # Final status check
    print("\n📊 FINAL PHASE 5 STATUS CHECK")
    print("-" * 50)
    
    phase5_tables = [
        # GPT & AI Integration
        'gpt_analytics', 'gpt_categories', 'gpt_context_backups', 'gpt_context_gpts',
        'gpt_context_interactions', 'gpt_context_metrics', 'gpt_context_sharing',
        'gpt_context_summaries', 'gpt_definitions', 'gpt_feedback', 'gpt_integrations',
        'gpt_interaction_contexts', 'gpt_performance', 'gpt_sharing', 'gpt_usage',
        'gpt_usage_history', 'gpt_versions', 'core_gpt_definitions', 'core_gpt_performance',
        # Dashboard Analytics
        'dashboard_context_backups', 'dashboard_context_gpts', 'dashboard_context_interactions',
        'dashboard_context_metrics', 'dashboard_context_optimizations', 'dashboard_context_summaries',
        'dashboard_context_templates', 'dashboard_context_validations', 'dashboard_gpt_contexts',
        'dashboard_gpt_integrations', 'dashboard_gpt_subscriptions', 'dashboard_gpt_usage_history',
        'dashboard_optimization_events', 'dashboard_resource_optimizations', 'dashboard_resource_sharing',
        'dashboard_resource_thresholds', 'dashboard_resource_usage'
    ]
    
    for table in phase5_tables:
        try:
            count_result = session.execute(text(f'SELECT COUNT(*) FROM {table}'))
            count = count_result.scalar()
            status = '✅' if count > 0 else '⚠️'
            print(f"  {status} {table}: {count} records")
        except Exception as e:
            print(f"  ❌ {table}: ERROR - {e}")
    
    total_records = sum(results.values())
    # Count tables that either have records or were skipped (already had data)
    completed_tables = 0
    for table in phase5_tables:
        if results.get(table, 0) > 0:  # Has new records
            completed_tables += 1
        else:
            # Check if table already had data (was skipped)
            try:
                count_result = session.execute(text(f'SELECT COUNT(*) FROM {table}'))
                existing_count = count_result.scalar()
                if existing_count > 0:
                    completed_tables += 1
            except:
                pass  # Table doesn't exist or has errors
    
    completion_percentage = (completed_tables / len(phase5_tables)) * 100
    print(f"\n🎉 PHASE 5 COMPLETION: {completed_tables}/{len(phase5_tables)} ({completion_percentage:.1f}%)")
    print(f"🏆 PHASE 5 ADVANCED ANALYTICS & AI: {completion_percentage:.1f}% COMPLETE! 🏆")
    print(f"🎯 {completed_tables} out of {len(phase5_tables)} tables successfully seeded with {total_records:,} total records!")
    
    return results

def get_table_ids(session: Session, table_name: str) -> List[int]:
    """Get existing IDs from a table"""
    try:
        result = session.execute(text(f"SELECT id FROM {table_name}"))
        return [row[0] for row in result.fetchall()]
    except:
        return list(range(1, 101))  # Fallback range

def get_plan_ids_or_create_default(session: Session) -> List[int]:
    """Get plan IDs from gpt_subscription_plans or create default if table doesn't exist"""
    try:
        result = session.execute(text("SELECT id FROM gpt_subscription_plans LIMIT 10"))
        plan_ids = [row[0] for row in result.fetchall()]
        if plan_ids:
            return plan_ids
        else:
            # If table exists but is empty, create a default plan
            session.execute(text("""
                INSERT INTO gpt_subscription_plans (name, description, price, currency, billing_cycle,
                                                 monthly_token_limit, monthly_request_limit, 
                                                 max_contexts, max_gpt_definitions, features,
                                                 api_access, priority_support, custom_integrations,
                                                 is_active, is_public, status, metadata)
                VALUES ('Default Plan', 'Default subscription plan for development', 
                       29.99, 'USD', 'MONTHLY', 5000, 500, 10, 5, '{"basic_features": true}',
                       true, false, false, true, true, 'ACTIVE', '{"created_by": "system"}')
                ON CONFLICT DO NOTHING
            """))
            session.commit()
            # Get the newly created plan ID
            result = session.execute(text("SELECT id FROM gpt_subscription_plans LIMIT 1"))
            plan_ids = [row[0] for row in result.fetchall()]
            return plan_ids if plan_ids else [1]
    except Exception as e:
        print(f"  ⚠️ Could not access gpt_subscription_plans: {e}")
        # Fallback to using plan_id = 1
        return [1]

def seed_gpt_ai_integration(session: Session, user_ids: List[int], organization_ids: List[int], project_ids: List[int]) -> Dict[str, int]:
    """Seed GPT & AI Integration tables"""
    results = {}
    
    # First, create base GPT definitions and subscriptions
    print("  🔧 Creating base GPT definitions...")
    gpt_definitions_data = []
    for i in range(25):
        gpt_definitions_data.append({
            'name': f'GPT Model {i+1}',
            'model_type': random.choice(['gpt-4', 'gpt-3.5-turbo', 'claude-3', 'gemini-pro']),
            'version': f'v{random.randint(1, 3)}.{random.randint(0, 9)}.{random.randint(0, 9)}',
            'description': f'Advanced AI model for educational applications {i+1}',
            'category': random.choice(['STUDENT', 'TEACHER', 'ADMIN', 'PARENT', 'ADDITIONAL']),
            'type': random.choice(['MATH_TUTOR', 'LANGUAGE_ARTS_TEACHER', 'SCIENCE_TEACHER', 'PHYSICAL_ED_TEACHER', 'ASSESSMENT_GRADING']),
            'max_tokens': random.randint(1000, 4000),
            'temperature': round(random.uniform(0.1, 1.0), 2),
            'top_p': round(random.uniform(0.1, 1.0), 2),
            'frequency_penalty': round(random.uniform(0.0, 1.0), 2),
            'presence_penalty': round(random.uniform(0.0, 1.0), 2),
            'capabilities': json.dumps(['text_generation', 'question_answering', 'code_assistance']),
            'limitations': json.dumps(['context_length', 'real_time_data']),
            'context_window': random.randint(2000, 8000),
            'total_requests': random.randint(0, 1000),
            'total_tokens': random.randint(0, 100000),
            'last_used': datetime.now() - timedelta(days=random.randint(1, 30)),
            'is_active': random.choice([True, False]),
            'is_public': random.choice([True, False]),
            'user_id': random.choice(user_ids),
            'project_id': 1,  # Use valid project ID 1
            'organization_id': random.choice(organization_ids),
            'meta_data': json.dumps({'created_by': 'system', 'tags': ['education', 'ai']}),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 90)),
            'updated_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    try:
        session.execute(text("""
            INSERT INTO gpt_definitions (name, model_type, version, description, category, type,
                                       max_tokens, temperature, top_p, frequency_penalty, presence_penalty,
                                       capabilities, limitations, context_window, total_requests, total_tokens,
                                       last_used, is_active, is_public, user_id, project_id, organization_id,
                                       meta_data, created_at, updated_at)
            VALUES (:name, :model_type, :version, :description, :category, :type,
                    :max_tokens, :temperature, :top_p, :frequency_penalty, :presence_penalty,
                    :capabilities, :limitations, :context_window, :total_requests, :total_tokens,
                    :last_used, :is_active, :is_public, :user_id, :project_id, :organization_id,
                    :meta_data, :created_at, :updated_at)
        """), gpt_definitions_data)
        results['gpt_definitions'] = len(gpt_definitions_data)
        print(f"  ✅ gpt_definitions: {len(gpt_definitions_data)} records")
    except Exception as e:
        print(f"  ⚠️ gpt_definitions: {e}")
        results['gpt_definitions'] = 0
    
    # Core GPT Definitions (must be seeded before getting IDs for foreign keys)
    print("  🔧 Creating core GPT definitions...")
    core_gpt_definitions_data = []
    for i in range(30):
        core_gpt_definitions_data.append({
            'name': f'Core GPT Model {i+1}',
            'model_type': random.choice(['gpt-4', 'gpt-3.5-turbo', 'claude-3', 'gemini-pro']),
            'version': f'v{random.randint(1, 5)}.{random.randint(0, 9)}.{random.randint(0, 9)}',
            'description': f'Core AI model for educational applications {i+1}',
            'max_tokens': random.randint(1000, 4000),
            'temperature': round(random.uniform(0.1, 1.0), 2),
            'top_p': round(random.uniform(0.1, 1.0), 2),
            'frequency_penalty': round(random.uniform(0.0, 1.0), 2),
            'presence_penalty': round(random.uniform(0.0, 1.0), 2),
            'capabilities': json.dumps(['text_generation', 'question_answering', 'code_assistance']),
            'limitations': json.dumps(['context_length', 'real_time_data']),
            'context_window': random.randint(1000, 4000),
            'total_requests': random.randint(0, 10000),
            'total_tokens': random.randint(0, 1000000),
            'last_used': datetime.now() - timedelta(days=random.randint(1, 60)),
            'is_active': random.choice([True, False]),
            'is_public': random.choice([True, False]),
            'user_id': random.choice(user_ids),
            'project_id': 1,  # Use valid project ID 1
            'organization_id': random.choice(organization_ids),
            'status': random.choice(['ACTIVE', 'INACTIVE', 'PENDING']),
            'metadata': json.dumps({'source': 'core_system'})
        })
    
    try:
        session.execute(text("""
            INSERT INTO core_gpt_definitions (name, model_type, version, description, max_tokens, temperature, top_p, frequency_penalty, presence_penalty, capabilities, limitations, context_window, total_requests, total_tokens, last_used, is_active, is_public, user_id, project_id, organization_id, status, metadata)
            VALUES (:name, :model_type, :version, :description, :max_tokens, :temperature, :top_p, :frequency_penalty, :presence_penalty, :capabilities, :limitations, :context_window, :total_requests, :total_tokens, :last_used, :is_active, :is_public, :user_id, :project_id, :organization_id, :status, :metadata)
        """), core_gpt_definitions_data)
        results['core_gpt_definitions'] = len(core_gpt_definitions_data)
        print(f"  ✅ core_gpt_definitions: {len(core_gpt_definitions_data)} records")
    except Exception as e:
        print(f"  ⚠️ core_gpt_definitions: {e}")
        results['core_gpt_definitions'] = 0
        session.rollback()
    session.commit()
    
    # Get GPT definition IDs for foreign keys - use gpt_definitions for dashboard_gpt_subscriptions
    gpt_definition_ids = get_table_ids(session, "gpt_definitions")
    print(f"  📋 Found {len(gpt_definition_ids)} GPT definition IDs")
    
    # Get plan IDs dynamically
    plan_ids = get_plan_ids_or_create_default(session)
    print(f"  📋 Found {len(plan_ids)} plan IDs")
    
    # Create GPT subscriptions
    print("  🔧 Creating GPT subscriptions...")
    gpt_subscriptions_data = []
    for i in range(15):
        gpt_subscriptions_data.append({
            'user_id': random.choice(user_ids),
            'plan_id': random.choice(plan_ids),  # Use actual plan IDs from database
            'subscription_type': random.choice(['basic', 'premium', 'enterprise']),
            'start_date': datetime.now() - timedelta(days=random.randint(1, 60)),
            'end_date': datetime.now() + timedelta(days=random.randint(30, 365)) if random.choice([True, False]) else None,
            'auto_renew': random.choice([True, False]),
            'monthly_token_limit': random.randint(1000, 10000),
            'monthly_request_limit': random.randint(100, 1000),
            'current_month_tokens': random.randint(0, 5000),
            'current_month_requests': random.randint(0, 500),
            'billing_cycle': random.choice(['monthly', 'yearly', 'quarterly']),
            'price': round(random.uniform(9.99, 99.99), 2),
            'currency': random.choice(['USD', 'EUR', 'GBP']),
            'status': random.choice(['ACTIVE', 'INACTIVE', 'PENDING', 'CANCELLED']),
            'is_active': random.choice([True, False]),
            'metadata': json.dumps({'created_by': 'system', 'features': ['gpt-4', 'analytics']})
        })
    
    try:
        session.execute(text("""
            INSERT INTO gpt_subscriptions (user_id, plan_id, subscription_type, start_date, end_date,
                                         auto_renew, monthly_token_limit, monthly_request_limit,
                                         current_month_tokens, current_month_requests, billing_cycle,
                                         price, currency, status, is_active, metadata)
            VALUES (:user_id, :plan_id, :subscription_type, :start_date, :end_date,
                    :auto_renew, :monthly_token_limit, :monthly_request_limit,
                    :current_month_tokens, :current_month_requests, :billing_cycle,
                    :price, :currency, :status, :is_active, :metadata)
        """), gpt_subscriptions_data)
        results['gpt_subscriptions'] = len(gpt_subscriptions_data)
        print(f"  ✅ gpt_subscriptions: {len(gpt_subscriptions_data)} records")
    except Exception as e:
        print(f"  ⚠️ gpt_subscriptions: {e}")
        results['gpt_subscriptions'] = 0
    
    # Get subscription IDs for foreign keys - ensure we have valid IDs
    subscription_ids = get_table_ids(session, "gpt_subscriptions")
    if not subscription_ids:
        print("  ⚠️ No subscription IDs found, creating fallback")
        subscription_ids = [1, 2, 3, 4, 5]  # Use fallback IDs that exist
    print(f"  📋 Found {len(subscription_ids)} subscription IDs")
    
    # Create dashboard_gpt_subscriptions early so other tables can use the IDs
    print("  🔧 Creating dashboard_gpt_subscriptions early...")
    dashboard_subscription_ids = get_table_ids(session, "dashboard_gpt_subscriptions")
    if not dashboard_subscription_ids:
        print("  ⚠️ No dashboard_gpt_subscriptions found, creating them...")
        # Create dashboard_gpt_subscriptions here
        dashboard_subscriptions_data = []
        # Create subscriptions to match teacher count (32)
        teacher_count = len(user_ids)  # Should be 32 teachers
        print(f"  📊 Creating {teacher_count} dashboard subscriptions to match teacher count")
        for i in range(teacher_count):
            dashboard_subscriptions_data.append({
                'user_id': random.choice(user_ids),
                'organization_id': random.choice(organization_ids) if organization_ids else None,
                'gpt_definition_id': random.choice(gpt_definition_ids) if gpt_definition_ids else 1,
                'name': f'Dashboard Subscription {i+1}',
                'description': f'Dashboard GPT subscription {i+1}',
                'model': random.choice(['gpt-4', 'gpt-3.5-turbo', 'claude-3']),
                'configuration': json.dumps({'temperature': 0.7, 'max_tokens': 2000}),
                'is_active': random.choice([True, False]),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 15))
            })
        
        try:
            session.execute(text("""
                INSERT INTO dashboard_gpt_subscriptions (user_id, organization_id, gpt_definition_id, name, description, model, configuration, is_active, created_at, updated_at)
                VALUES (:user_id, :organization_id, :gpt_definition_id, :name, :description, :model, :configuration, :is_active, :created_at, :updated_at)
            """), dashboard_subscriptions_data)
            session.commit()
            print(f"  ✅ dashboard_gpt_subscriptions: {len(dashboard_subscriptions_data)} records")
        except Exception as e:
            print(f"  ⚠️ dashboard_gpt_subscriptions: {e}")
            session.rollback()
        
        # Get the newly created IDs
        dashboard_subscription_ids = get_table_ids(session, "dashboard_gpt_subscriptions")
    
    print(f"  📋 Found {len(dashboard_subscription_ids)} dashboard subscription IDs")
    
    # Store the dashboard_subscription_ids for use in other functions
    # (No longer using global variables)
    
    
    # Get dashboard_gpt_subscriptions IDs for gpt_analytics (different table)
    dashboard_subscription_ids = get_table_ids(session, "dashboard_gpt_subscriptions")
    if not dashboard_subscription_ids:
        print("  ⚠️ No dashboard_gpt_subscriptions found, creating some first...")
        # Create fallback IDs that will be used later
        dashboard_subscription_ids = [1, 2, 3, 4, 5]
        # Create dashboard_gpt_subscriptions records (32 to match 32 users)
        dashboard_subscriptions_data = []
        for i in range(32):
            dashboard_subscriptions_data.append({
                'user_id': random.choice(user_ids),
                'organization_id': random.choice(organization_ids),
                'gpt_definition_id': random.choice(gpt_definition_ids),
                'name': f'Dashboard Subscription {i+1}',
                'description': f'Dashboard GPT subscription {i+1}',
                'model': random.choice(['gpt-4', 'gpt-3.5-turbo', 'claude-3', 'gemini-pro']),
                'configuration': json.dumps({'temperature': 0.7, 'max_tokens': 2000}),
                'is_active': random.choice([True, False]),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 60)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 30))
            })
        
        try:
            session.execute(text("""
                INSERT INTO dashboard_gpt_subscriptions (user_id, organization_id, gpt_definition_id, name, description, model, configuration, is_active, created_at, updated_at)
                VALUES (:user_id, :organization_id, :gpt_definition_id, :name, :description, :model, :configuration, :is_active, :created_at, :updated_at)
            """), dashboard_subscriptions_data)
            session.commit()
            print(f"  ✅ Created {len(dashboard_subscriptions_data)} dashboard_gpt_subscriptions records")
            
            # Get the newly created IDs
            dashboard_subscription_ids = get_table_ids(session, "dashboard_gpt_subscriptions")
        except Exception as e:
            print(f"  ⚠️ Failed to create dashboard_gpt_subscriptions: {e}")
            dashboard_subscription_ids = [1]
    
    # GPT Analytics
    print("  🔧 Creating GPT analytics...")
    gpt_analytics_data = []
    for i in range(200):
        gpt_analytics_data.append({
            'user_id': random.choice(user_ids),
            'organization_id': random.choice(organization_ids),
            'subscription_id': random.choice(dashboard_subscription_ids),
            'metric_name': random.choice(['tokens_used', 'response_time', 'accuracy', 'user_satisfaction']),
            'metric_value': round(random.uniform(0.1, 100.0), 2),
            'timestamp': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    try:
        session.execute(text("""
            INSERT INTO gpt_analytics (user_id, organization_id, subscription_id, metric_name, metric_value, timestamp)
            VALUES (:user_id, :organization_id, :subscription_id, :metric_name, :metric_value, :timestamp)
        """), gpt_analytics_data)
        results['gpt_analytics'] = len(gpt_analytics_data)
        print(f"  ✅ gpt_analytics: {len(gpt_analytics_data)} records")
    except Exception as e:
        print(f"  ⚠️ gpt_analytics: {e}")
        results['gpt_analytics'] = 0
    
    # GPT Categories
    print("  🔧 Creating GPT categories...")
    # Check if table already has data
    try:
        result = session.execute(text("SELECT COUNT(*) FROM gpt_categories"))
        existing_count = result.scalar()
        if existing_count > 0:
            print(f"  ⚠️ gpt_categories already has {existing_count} records, skipping...")
            results['gpt_categories'] = existing_count
            gpt_categories_data = []
        else:
            # Get valid category IDs from dashboard_categories
            category_ids = get_table_ids(session, "dashboard_categories")
            if not category_ids:
                print("  ⚠️ No category IDs found, creating fallback")
                category_ids = [1]
            
            # Create unique combinations to avoid duplicate key violations
            gpt_categories_data = []
            used_combinations = set()
            for i in range(25):
                while True:
                    gpt_id = random.choice(dashboard_subscription_ids) if dashboard_subscription_ids else 1  # Use dashboard_subscription_ids
                    category_id = random.choice(category_ids)
                    combination = (gpt_id, category_id)
                    if combination not in used_combinations:
                        used_combinations.add(combination)
                        gpt_categories_data.append({
                            'gpt_id': gpt_id,
                            'category_id': category_id
                        })
                        break
    except Exception as e:
        print(f"  ⚠️ Error checking gpt_categories: {e}")
        gpt_categories_data = []
    
    if gpt_categories_data:
        try:
            session.execute(text("""
                INSERT INTO gpt_categories (gpt_id, category_id)
                VALUES (:gpt_id, :category_id)
            """), gpt_categories_data)
            results['gpt_categories'] = len(gpt_categories_data)
            print(f"  ✅ gpt_categories: {len(gpt_categories_data)} records")
        except Exception as e:
            print(f"  ⚠️ gpt_categories: {e}")
            results['gpt_categories'] = 0
    else:
        print("  ⚠️ gpt_categories: Skipped (already has data)")
    
    # GPT Interaction Contexts
    print("  🔧 Creating GPT interaction contexts...")
    # Use valid GPT definition IDs from gpt_definitions
    # Use gpt_definitions IDs for primary_gpt_id (not dashboard_subscription_ids)
    valid_gpt_definition_ids = get_table_ids(session, "gpt_definitions")
    if not valid_gpt_definition_ids:
        print("  ⚠️ No valid GPT definition IDs found, creating fallback")
        valid_gpt_definition_ids = [1]
    
    gpt_interaction_contexts_data = []
    for i in range(80):
        gpt_interaction_contexts_data.append({
            'user_id': random.choice(user_ids),
            'primary_gpt_id': random.choice(valid_gpt_definition_ids),
            'name': f'Context {i+1}',
            'description': f'Interaction context for user {i+1}',
            'context_type': random.choice(['CONVERSATION', 'PROJECT', 'SESSION', 'TASK', 'WORKFLOW']),
            'context_data': json.dumps({'topic': f'topic_{i+1}', 'priority': 'high'}),
            'max_tokens': random.randint(1000, 4000),
            'token_count': random.randint(100, 2000),
            'priority': random.randint(1, 10),
            'closed_at': datetime.now() - timedelta(days=random.randint(1, 30)) if random.choice([True, False]) else None,
            'settings': json.dumps({'temperature': 0.7, 'max_tokens': 2000}),
            'context_metadata': json.dumps({'created_by': 'system'}),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 60)),
            'updated_at': datetime.now() - timedelta(days=random.randint(1, 30)),
            'last_accessed_at': datetime.now() - timedelta(days=random.randint(1, 7)),
            'archived_at': None,
            'deleted_at': None,
            'scheduled_deletion_at': None,
            'retention_period': random.randint(30, 365),
            'status': random.choice(['ACTIVE', 'INACTIVE', 'PENDING', 'SCHEDULED', 'COMPLETED', 'CANCELLED', 'ON_HOLD']),
            'is_active': random.choice([True, False]),
            'metadata': json.dumps({'tags': ['education', 'ai']})
        })
    
        try:
            session.execute(text("""
                INSERT INTO gpt_interaction_contexts (user_id, primary_gpt_id, name, description, context_type,
                                                    context_data, max_tokens, token_count, priority, closed_at,
                                                    settings, context_metadata, created_at, updated_at,
                                                    last_accessed_at, archived_at, deleted_at, scheduled_deletion_at,
                                                    retention_period, status, is_active, metadata)
                VALUES (:user_id, :primary_gpt_id, :name, :description, :context_type,
                        :context_data, :max_tokens, :token_count, :priority, :closed_at,
                        :settings, :context_metadata, :created_at, :updated_at,
                        :last_accessed_at, :archived_at, :deleted_at, :scheduled_deletion_at,
                        :retention_period, :status, :is_active, :metadata)
            """), gpt_interaction_contexts_data)
            session.commit()  # Commit after successful insert
            results['gpt_interaction_contexts'] = len(gpt_interaction_contexts_data)
            print(f"  ✅ gpt_interaction_contexts: {len(gpt_interaction_contexts_data)} records")
        except Exception as e:
            print(f"  ⚠️ gpt_interaction_contexts: {e}")
            session.rollback()  # Rollback on error
            results['gpt_interaction_contexts'] = 0
    
    # Get context IDs for foreign keys - ensure we have valid IDs
    context_ids = get_table_ids(session, "gpt_interaction_contexts")
    if not context_ids:
        print("  ⚠️ No context IDs found, creating fallback")
        context_ids = [1, 2, 3, 4, 5]  # Use fallback IDs that exist
    print(f"  📋 Found {len(context_ids)} context IDs")
    
    # Store the context_ids for use in other functions
    context_ids_global = context_ids
    
    # GPT Context Interactions
    print("  🔧 Creating GPT context interactions...")
    gpt_context_interactions_data = []
    for i in range(400):
        gpt_context_interactions_data.append({
            'context_id': random.choice(context_ids),
            'gpt_id': random.choice(gpt_definition_ids),
            'interaction_type': random.choice(['MESSAGE', 'QUERY', 'RESPONSE', 'ACTION', 'COMMAND']),
            'content': json.dumps({'message': f'Interaction {i+1}', 'type': 'text'}),
            'role': random.choice(['user', 'assistant', 'system']),
            'token_count': random.randint(10, 500),
            'processing_time': round(random.uniform(0.1, 5.0), 2),
            'processed_at': datetime.now() - timedelta(days=random.randint(1, 30)),
            'user_id': random.choice(user_ids),
            'project_id': 1,  # Use valid project ID 1
            'organization_id': random.choice(organization_ids),
            'metadata': json.dumps({'session_id': f'session_{i+1}'})
        })
    
    try:
        session.execute(text("""
            INSERT INTO gpt_context_interactions (context_id, gpt_id, interaction_type, content, role,
                                                token_count, processing_time, processed_at, user_id,
                                                project_id, organization_id, metadata)
            VALUES (:context_id, :gpt_id, :interaction_type, :content, :role,
                    :token_count, :processing_time, :processed_at, :user_id,
                    :project_id, :organization_id, :metadata)
        """), gpt_context_interactions_data)
        results['gpt_context_interactions'] = len(gpt_context_interactions_data)
        print(f"  ✅ gpt_context_interactions: {len(gpt_context_interactions_data)} records")
    except Exception as e:
        print(f"  ⚠️ gpt_context_interactions: {e}")
        results['gpt_context_interactions'] = 0
    
    # Continue with remaining GPT tables...
    # GPT Context Backups
    print("  🔧 Creating GPT context backups...")
    gpt_context_backups_data = []
    for i in range(150):
        gpt_context_backups_data.append({
            'context_id': random.choice(context_ids),
            'backup_content': json.dumps({'context': f'Backup {i+1}', 'data': 'backup_data'}),
            'backup_type': random.choice(['full', 'incremental', 'differential']),
            'backup_reason': random.choice(['scheduled', 'manual', 'error_recovery']),
            'backup_metadata': json.dumps({'size': random.randint(100, 10000)}),
            'error_message': None,
            'is_restored': random.choice([True, False]),
            'restored_at': datetime.now() - timedelta(days=random.randint(1, 30)) if random.choice([True, False]) else None,
            'user_id': random.choice(user_ids),
            'project_id': 1,  # Use valid project ID 1
            'organization_id': random.choice(organization_ids),
            'status': random.choice(['ACTIVE', 'INACTIVE', 'PENDING', 'SCHEDULED', 'COMPLETED', 'CANCELLED', 'ON_HOLD']),
            'is_active': random.choice([True, False]),
            'metadata': json.dumps({'backup_version': f'v{i+1}'})
        })
    
    try:
        session.execute(text("""
            INSERT INTO gpt_context_backups (context_id, backup_content, backup_type, backup_reason,
                                           backup_metadata, error_message, is_restored, restored_at,
                                           user_id, project_id, organization_id, status, is_active, metadata)
            VALUES (:context_id, :backup_content, :backup_type, :backup_reason,
                    :backup_metadata, :error_message, :is_restored, :restored_at,
                    :user_id, :project_id, :organization_id, :status, :is_active, :metadata)
        """), gpt_context_backups_data)
        results['gpt_context_backups'] = len(gpt_context_backups_data)
        print(f"  ✅ gpt_context_backups: {len(gpt_context_backups_data)} records")
    except Exception as e:
        print(f"  ⚠️ gpt_context_backups: {e}")
        results['gpt_context_backups'] = 0
    session.commit()
    
    # GPT Context GPTs
    print("  🔧 Creating GPT context GPTs...")
    gpt_context_gpts_data = []
    for i in range(100):
        gpt_context_gpts_data.append({
            'context_id': random.choice(context_ids),
            'gpt_id': random.choice(gpt_definition_ids)
        })
    
    try:
        session.execute(text("""
            INSERT INTO gpt_context_gpts (context_id, gpt_id)
            VALUES (:context_id, :gpt_id)
        """), gpt_context_gpts_data)
        results['gpt_context_gpts'] = len(gpt_context_gpts_data)
        print(f"  ✅ gpt_context_gpts: {len(gpt_context_gpts_data)} records")
    except Exception as e:
        print(f"  ⚠️ gpt_context_gpts: {e}")
        results['gpt_context_gpts'] = 0
        session.rollback()
    session.commit()
    
    # GPT Context Metrics
    print("  🔧 Creating GPT context metrics...")
    gpt_context_metrics_data = []
    for i in range(200):
        gpt_context_metrics_data.append({
            'context_id': random.choice(context_ids),
            'metric_type': random.choice(['tokens_used', 'response_time', 'accuracy', 'user_satisfaction']),
            'value': round(random.uniform(0.1, 100.0), 2),
            'timestamp': datetime.now() - timedelta(days=random.randint(1, 30)),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
            'updated_at': datetime.now() - timedelta(days=random.randint(1, 15)),
            'status': random.choice(['ACTIVE', 'INACTIVE', 'PENDING']),
            'is_active': random.choice([True, False])
        })
    
    try:
        session.execute(text("""
            INSERT INTO gpt_context_metrics (context_id, metric_type, value, timestamp, created_at, updated_at, status, is_active)
            VALUES (:context_id, :metric_type, :value, :timestamp, :created_at, :updated_at, :status, :is_active)
        """), gpt_context_metrics_data)
        results['gpt_context_metrics'] = len(gpt_context_metrics_data)
        print(f"  ✅ gpt_context_metrics: {len(gpt_context_metrics_data)} records")
    except Exception as e:
        print(f"  ⚠️ gpt_context_metrics: {e}")
        results['gpt_context_metrics'] = 0
        session.rollback()
    session.commit()
    
    # GPT Context Sharing
    print("  🔧 Creating GPT context sharing...")
    gpt_context_sharing_data = []
    for i in range(80):
        gpt_context_sharing_data.append({
            'context_id': random.choice(context_ids),
            'shared_with_user_id': random.choice(user_ids),
            'permissions': json.dumps({'level': random.choice(['READ', 'WRITE', 'ADMIN']), 'can_edit': random.choice([True, False])}),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
            'updated_at': datetime.now() - timedelta(days=random.randint(1, 15)),
            'status': random.choice(['ACTIVE', 'INACTIVE', 'PENDING']),
            'is_active': random.choice([True, False])
        })
    
    try:
        session.execute(text("""
            INSERT INTO gpt_context_sharing (context_id, shared_with_user_id, permissions, created_at, updated_at, status, is_active)
            VALUES (:context_id, :shared_with_user_id, :permissions, :created_at, :updated_at, :status, :is_active)
        """), gpt_context_sharing_data)
        results['gpt_context_sharing'] = len(gpt_context_sharing_data)
        print(f"  ✅ gpt_context_sharing: {len(gpt_context_sharing_data)} records")
    except Exception as e:
        print(f"  ⚠️ gpt_context_sharing: {e}")
        results['gpt_context_sharing'] = 0
        session.rollback()
    session.commit()
    
    # GPT Context Summaries
    print("  🔧 Creating GPT context summaries...")
    gpt_context_summaries_data = []
    for i in range(60):
        gpt_context_summaries_data.append({
            'context_id': random.choice(context_ids),
            'summary': f'Summary of context {i+1} interactions and key points',
            'key_points': json.dumps(['point1', 'point2', 'point3']),
            'sentiment': random.choice(['positive', 'negative', 'neutral']),
            'topics': json.dumps(['topic1', 'topic2']),
            'token_count': random.randint(100, 1000),
            'summary_type': random.choice(['AUTOMATIC', 'MANUAL', 'AI_GENERATED']),
            'confidence_score': round(random.uniform(0.1, 1.0), 2),
            'user_id': random.choice(user_ids),
            'project_id': 1,  # Use valid project ID 1
            'organization_id': random.choice(organization_ids),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
            'updated_at': datetime.now() - timedelta(days=random.randint(1, 15)),
            'status': random.choice(['ACTIVE', 'INACTIVE', 'PENDING']),
            'is_active': random.choice([True, False])
        })
    
    try:
        session.execute(text("""
            INSERT INTO gpt_context_summaries (context_id, summary, key_points, sentiment, topics, token_count, summary_type, confidence_score, user_id, project_id, organization_id, created_at, updated_at, status, is_active)
            VALUES (:context_id, :summary, :key_points, :sentiment, :topics, :token_count, :summary_type, :confidence_score, :user_id, :project_id, :organization_id, :created_at, :updated_at, :status, :is_active)
        """), gpt_context_summaries_data)
        results['gpt_context_summaries'] = len(gpt_context_summaries_data)
        print(f"  ✅ gpt_context_summaries: {len(gpt_context_summaries_data)} records")
    except Exception as e:
        print(f"  ⚠️ gpt_context_summaries: {e}")
        results['gpt_context_summaries'] = 0
        session.rollback()
    session.commit()
    
    # GPT Feedback
    print("  🔧 Creating GPT feedback...")
    # Use the dashboard subscription IDs that were created earlier
    gpt_feedback_data = []
    for i in range(120):
        gpt_feedback_data.append({
            'user_id': random.choice(user_ids),
            'organization_id': random.choice(organization_ids) if random.choice([True, False]) else None,
            'subscription_id': random.choice(dashboard_subscription_ids) if dashboard_subscription_ids else 1,
            'rating': random.randint(1, 5),
            'comment': f'User feedback for GPT interaction {i+1}',
            'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    try:
        session.execute(text("""
            INSERT INTO gpt_feedback (user_id, organization_id, subscription_id, rating, comment, created_at)
            VALUES (:user_id, :organization_id, :subscription_id, :rating, :comment, :created_at)
        """), gpt_feedback_data)
        results['gpt_feedback'] = len(gpt_feedback_data)
        print(f"  ✅ gpt_feedback: {len(gpt_feedback_data)} records")
    except Exception as e:
        print(f"  ⚠️ gpt_feedback: {e}")
        results['gpt_feedback'] = 0
        session.rollback()
    session.commit()
    
    # GPT Integrations
    print("  🔧 Creating GPT integrations...")
    # Get gpt_definitions IDs
    core_gpt_definition_ids = get_table_ids(session, "gpt_definitions")
    if not core_gpt_definition_ids:
        print("  ⚠️ No core GPT definition IDs found, creating fallback")
        core_gpt_definition_ids = [1]
    
    gpt_integrations_data = []
    for i in range(50):
        gpt_integrations_data.append({
            'gpt_id': random.choice(core_gpt_definition_ids),
            'integration_type': random.choice(['API', 'WEBHOOK', 'PLUGIN', 'EXTENSION']),
            'name': f'Integration {i+1}',
            'description': f'Integration description {i+1}',
            'configuration': json.dumps({'endpoint': f'https://api.example.com/integration_{i+1}', 'auth_type': 'bearer'}),
            'user_id': random.choice(user_ids),
            'project_id': 1,  # Use valid project ID 1
            'organization_id': random.choice(organization_ids),
            'status': random.choice(['ACTIVE', 'INACTIVE', 'PENDING']),
            'is_active': random.choice([True, False])
        })
    
    try:
        session.execute(text("""
            INSERT INTO gpt_integrations (gpt_id, integration_type, name, description, configuration, user_id, project_id, organization_id, status, is_active)
            VALUES (:gpt_id, :integration_type, :name, :description, :configuration, :user_id, :project_id, :organization_id, :status, :is_active)
        """), gpt_integrations_data)
        results['gpt_integrations'] = len(gpt_integrations_data)
        print(f"  ✅ gpt_integrations: {len(gpt_integrations_data)} records")
    except Exception as e:
        print(f"  ⚠️ gpt_integrations: {e}")
        results['gpt_integrations'] = 0
        session.rollback()
    session.commit()
    
    # GPT Performance
    print("  🔧 Creating GPT performance...")
    # Use valid model IDs from gpt_definitions
    model_ids = get_table_ids(session, "gpt_definitions")
    if not model_ids:
        print("  ⚠️ No model IDs found, creating fallback")
        model_ids = [1]
    
    # Use the dashboard subscription IDs that were created earlier
    gpt_performance_data = []
    for i in range(30):
        gpt_performance_data.append({
            'subscription_id': random.choice(dashboard_subscription_ids) if dashboard_subscription_ids else 1,
            'model_id': random.choice(model_ids),
            'user_id': random.choice(user_ids),
            'metrics': json.dumps({
                'response_time': round(random.uniform(0.1, 5.0), 2),
                'accuracy': round(random.uniform(0.1, 100.0), 2),
                'tokens_per_second': round(random.uniform(1.0, 100.0), 2)
            }),
            'timestamp': datetime.now() - timedelta(days=random.randint(1, 30)),
            'response_time': round(random.uniform(0.1, 5.0), 2),
            'error_rate': round(random.uniform(0.0, 10.0), 2),
            'usage_count': random.randint(1, 1000)
        })
    
    try:
        session.execute(text("""
            INSERT INTO gpt_performance (subscription_id, model_id, user_id, metrics, timestamp, response_time, error_rate, usage_count)
            VALUES (:subscription_id, :model_id, :user_id, :metrics, :timestamp, :response_time, :error_rate, :usage_count)
        """), gpt_performance_data)
        results['gpt_performance'] = len(gpt_performance_data)
        print(f"  ✅ gpt_performance: {len(gpt_performance_data)} records")
    except Exception as e:
        print(f"  ⚠️ gpt_performance: {e}")
        results['gpt_performance'] = 0
        session.rollback()
    session.commit()
    
    # GPT Sharing
    print("  🔧 Creating GPT sharing...")
    # Check if table already has data
    try:
        result = session.execute(text("SELECT COUNT(*) FROM gpt_sharing"))
        existing_count = result.scalar()
        if existing_count > 0:
            print(f"  ⚠️ gpt_sharing already has {existing_count} records, skipping...")
            results['gpt_sharing'] = existing_count
            gpt_sharing_data = []
        else:
            # Create unique combinations to avoid duplicate key violations
            gpt_sharing_data = []
            used_combinations = set()
            
            # Use the dashboard subscription IDs that were created earlier
            # Calculate maximum possible unique combinations
            max_combinations = len(dashboard_subscription_ids) * len(user_ids) if dashboard_subscription_ids else len(user_ids)
            target_records = min(90, max_combinations)  # Don't exceed possible combinations
            
            print(f"  📊 Available combinations: {max_combinations}, creating: {target_records}")
            
            for i in range(target_records):
                attempts = 0
                max_attempts = 100  # Safety counter to prevent infinite loops
                
                while attempts < max_attempts:
                    subscription_id = random.choice(dashboard_subscription_ids) if dashboard_subscription_ids else 1
                    user_id = random.choice(user_ids)
                    combination = (subscription_id, user_id)
                    if combination not in used_combinations:
                        used_combinations.add(combination)
                        gpt_sharing_data.append({
                            'subscription_id': subscription_id,
                            'user_id': user_id,
                            'permissions': json.dumps({
                                'level': random.choice(['READ', 'WRITE', 'ADMIN']),
                                'can_edit': random.choice([True, False])
                            }),
                            'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                            'expires_at': datetime.now() + timedelta(days=random.randint(1, 90)) if random.choice([True, False]) else None
                        })
                        break
                    attempts += 1
                
                if attempts >= max_attempts:
                    print(f"  ⚠️ Could not find unique combination after {max_attempts} attempts, stopping at {i} records")
                    break
    except Exception as e:
        print(f"  ⚠️ Error checking gpt_sharing: {e}")
        gpt_sharing_data = []
    
    if gpt_sharing_data:
        try:
            session.execute(text("""
                INSERT INTO gpt_sharing (subscription_id, user_id, permissions, created_at, expires_at)
                VALUES (:subscription_id, :user_id, :permissions, :created_at, :expires_at)
            """), gpt_sharing_data)
            results['gpt_sharing'] = len(gpt_sharing_data)
            print(f"  ✅ gpt_sharing: {len(gpt_sharing_data)} records")
        except Exception as e:
            print(f"  ⚠️ gpt_sharing: {e}")
            results['gpt_sharing'] = 0
    else:
        print("  ⚠️ gpt_sharing: Skipped (already has data)")
        session.rollback()
    session.commit()
    
    # GPT Usage
    print("  🔧 Creating GPT usage...")
    # Use the dashboard subscription IDs that were created earlier
    gpt_usage_data = []
    for i in range(50):
        gpt_usage_data.append({
            'user_id': random.choice(user_ids),
            'organization_id': random.choice(organization_ids) if random.choice([True, False]) else None,
            'subscription_id': random.choice(dashboard_subscription_ids) if dashboard_subscription_ids else 1,
            'tokens_used': random.randint(10, 1000),
            'cost': round(random.uniform(0.01, 10.0), 2),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    try:
        session.execute(text("""
            INSERT INTO gpt_usage (user_id, organization_id, subscription_id, tokens_used, cost, created_at)
            VALUES (:user_id, :organization_id, :subscription_id, :tokens_used, :cost, :created_at)
        """), gpt_usage_data)
        results['gpt_usage'] = len(gpt_usage_data)
        print(f"  ✅ gpt_usage: {len(gpt_usage_data)} records")
    except Exception as e:
        print(f"  ⚠️ gpt_usage: {e}")
        results['gpt_usage'] = 0
        session.rollback()
    session.commit()
    
    # GPT Usage History
    print("  🔧 Creating GPT usage history...")
    # Use the gpt_subscriptions IDs (not dashboard_gpt_subscriptions)
    # Check if we have valid subscription IDs
    if not subscription_ids:
        print("  ⚠️ No gpt_subscriptions IDs found, creating fallback")
        subscription_ids = [1, 2, 3, 4, 5]
    
    gpt_usage_history_data = []
    for i in range(80):
        gpt_usage_history_data.append({
            'subscription_id': random.choice(subscription_ids),
            'interaction_type': random.choice(['QUERY', 'RESPONSE', 'CONTEXT_CREATE', 'CONTEXT_UPDATE']),
            'details': json.dumps({
                'tokens_consumed': random.randint(5, 500),
                'session_id': f'session_{i+1}',
                'ip_address': '192.168.1.1'
            }),
            'timestamp': datetime.now() - timedelta(days=random.randint(1, 30)),
            'metadata': json.dumps({
                'action_type': random.choice(['QUERY', 'RESPONSE', 'CONTEXT_CREATE', 'CONTEXT_UPDATE']),
                'user_id': random.choice(user_ids)
            })
        })
    
    try:
        session.execute(text("""
            INSERT INTO gpt_usage_history (subscription_id, interaction_type, details, timestamp, metadata)
            VALUES (:subscription_id, :interaction_type, :details, :timestamp, :metadata)
        """), gpt_usage_history_data)
        results['gpt_usage_history'] = len(gpt_usage_history_data)
        print(f"  ✅ gpt_usage_history: {len(gpt_usage_history_data)} records")
    except Exception as e:
        print(f"  ⚠️ gpt_usage_history: {e}")
        results['gpt_usage_history'] = 0
        session.rollback()
    session.commit()
    
    # GPT Versions
    print("  🔧 Creating GPT versions...")
    # Use the dashboard subscription IDs that were created earlier
    gpt_versions_data = []
    for i in range(40):
        gpt_versions_data.append({
            'subscription_id': random.choice(dashboard_subscription_ids) if dashboard_subscription_ids else 1,
            'version': f'v{random.randint(1, 5)}.{random.randint(0, 9)}.{random.randint(0, 9)}',
            'status': random.choice(['ACTIVE', 'INACTIVE', 'PENDING']),
            'settings': json.dumps({
                'temperature': round(random.uniform(0.1, 1.0), 2),
                'max_tokens': random.randint(100, 4000)
            }),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 60)),
            'is_active': random.choice([True, False])
        })
    
    try:
        session.execute(text("""
            INSERT INTO gpt_versions (subscription_id, version, status, settings, created_at, is_active)
            VALUES (:subscription_id, :version, :status, :settings, :created_at, :is_active)
        """), gpt_versions_data)
        results['gpt_versions'] = len(gpt_versions_data)
        print(f"  ✅ gpt_versions: {len(gpt_versions_data)} records")
    except Exception as e:
        print(f"  ⚠️ gpt_versions: {e}")
        results['gpt_versions'] = 0
        session.rollback()
    session.commit()
    
    # Core GPT Definitions (Additional - renamed to avoid conflicts)
    print("  🔧 Creating additional core GPT definitions...")
    core_gpt_definitions_additional_data = []
    for i in range(30):
        core_gpt_definitions_additional_data.append({
            'name': f'Core GPT Model Additional {i+1}',
            'model_type': random.choice(['gpt-4', 'gpt-3.5-turbo', 'claude-3', 'gemini-pro']),
            'version': f'v{random.randint(1, 5)}.{random.randint(0, 9)}.{random.randint(0, 9)}',
            'description': f'Core AI model backup for educational applications {i+1}',
            'max_tokens': random.randint(1000, 4000),
            'temperature': round(random.uniform(0.1, 1.0), 2),
            'top_p': round(random.uniform(0.1, 1.0), 2),
            'frequency_penalty': round(random.uniform(0.0, 2.0), 2),
            'presence_penalty': round(random.uniform(0.0, 2.0), 2),
            'capabilities': json.dumps(['text_generation', 'question_answering', 'code_assistance']),
            'limitations': json.dumps(['context_length', 'rate_limits']),
            'context_window': random.randint(1000, 4000),
            'total_requests': random.randint(0, 10000),
            'total_tokens': random.randint(0, 1000000),
            'last_used': datetime.now() - timedelta(days=random.randint(1, 60)),
            'is_active': random.choice([True, False]),
            'is_public': random.choice([True, False]),
            'user_id': random.choice(user_ids),
            'project_id': 1,  # Use valid project ID 1
            'organization_id': random.choice(organization_ids),
            'status': random.choice(['ACTIVE', 'INACTIVE', 'PENDING']),
            'metadata': json.dumps({'source': 'core_system_backup'})
        })
    
    try:
        session.execute(text("""
            INSERT INTO core_gpt_definitions (name, model_type, version, description, max_tokens, temperature, top_p, frequency_penalty, presence_penalty, capabilities, limitations, context_window, total_requests, total_tokens, last_used, is_active, is_public, user_id, project_id, organization_id, status, metadata)
            VALUES (:name, :model_type, :version, :description, :max_tokens, :temperature, :top_p, :frequency_penalty, :presence_penalty, :capabilities, :limitations, :context_window, :total_requests, :total_tokens, :last_used, :is_active, :is_public, :user_id, :project_id, :organization_id, :status, :metadata)
        """), core_gpt_definitions_additional_data)
        results['core_gpt_definitions_additional'] = len(core_gpt_definitions_additional_data)
        print(f"  ✅ core_gpt_definitions_additional: {len(core_gpt_definitions_additional_data)} records")
    except Exception as e:
        print(f"  ⚠️ core_gpt_definitions_additional: {e}")
        results['core_gpt_definitions_additional'] = 0
        session.rollback()
    session.commit()
    
    # Core GPT Performance
    print("  🔧 Creating core GPT performance...")
    # Get valid model IDs from gpt_definitions
    core_model_ids = get_table_ids(session, "gpt_definitions")
    if not core_model_ids:
        print("  ⚠️ No core GPT definition IDs found, using fallback")
        core_model_ids = [1]
    
    core_gpt_performance_data = []
    for i in range(20):
        core_gpt_performance_data.append({
            'model_id': random.choice(core_model_ids),  # Use valid model ID from core_gpt_definitions
            'user_id': random.choice(user_ids),
            'threshold_id': None,  # Remove threshold_id reference
            'metric_type': random.choice(['response_time', 'accuracy', 'throughput', 'reliability']),
            'metric_value': round(random.uniform(0.1, 100.0), 2),
            'recorded_at': datetime.now() - timedelta(days=random.randint(1, 30)),
            'performance_metadata': json.dumps({
                'context': 'core_system',
                'environment': 'production'
            }),
            'metadata': json.dumps({
                'source': 'core_system',
                'version': '1.0'
            })
        })
    
    try:
        session.execute(text("""
            INSERT INTO core_gpt_performance (model_id, user_id, threshold_id, metric_type, metric_value, recorded_at, performance_metadata, metadata)
            VALUES (:model_id, :user_id, :threshold_id, :metric_type, :metric_value, :recorded_at, :performance_metadata, :metadata)
        """), core_gpt_performance_data)
        results['core_gpt_performance'] = len(core_gpt_performance_data)
        print(f"  ✅ core_gpt_performance: {len(core_gpt_performance_data)} records")
    except Exception as e:
        print(f"  ⚠️ core_gpt_performance: {e}")
        results['core_gpt_performance'] = 0
        session.rollback()
    session.commit()
    
    return results

def seed_dashboard_analytics(session: Session, user_ids: List[int], organization_ids: List[int], project_ids: List[int], context_ids: List[int] = None) -> Dict[str, int]:
    """Seed Dashboard Analytics tables"""
    results = {}
    
    # Use provided context_ids or get them from the database
    if not context_ids:
        context_ids = get_table_ids(session, "gpt_interaction_contexts")
        if not context_ids:
            print("  ⚠️ No context IDs found, creating fallback")
            context_ids = [1, 2, 3, 4, 5]
    
    # Get reference data - use gpt_definitions (which has 25 records)
    gpt_definition_ids = get_table_ids(session, "gpt_definitions")
    # Don't get subscription_ids and context_ids yet - they will be created in this function
    subscription_ids = []
    context_ids = []
    
    # Create dashboard_gpt_subscriptions table if it doesn't exist
    print("  🔧 Creating dashboard_gpt_subscriptions...")
    dashboard_subscription_ids = get_table_ids(session, "dashboard_gpt_subscriptions")
    if not dashboard_subscription_ids:
        print("  ⚠️ No dashboard_gpt_subscriptions found, creating them...")
        dashboard_subscriptions_data = []
        # Create subscriptions to match teacher count (32)
        teacher_count = len(user_ids)  # Should be 32 teachers
        print(f"  📊 Creating {teacher_count} dashboard subscriptions to match teacher count")
        for i in range(teacher_count):
            dashboard_subscriptions_data.append({
                'user_id': random.choice(user_ids),
                'organization_id': random.choice(organization_ids) if organization_ids else None,
                'gpt_definition_id': random.choice(gpt_definition_ids) if gpt_definition_ids else 1,
                'name': f'GPT Subscription {i + 1}',
                'description': f'Description for GPT subscription {i + 1}',
                'model': random.choice(['gpt-4', 'gpt-3.5-turbo', 'claude-3']),
                'configuration': json.dumps({"temperature": 0.7, "max_tokens": 2000}),
                'is_active': random.choice([True, False]),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 10))
            })
        
        try:
            session.execute(text("""
                INSERT INTO dashboard_gpt_subscriptions (user_id, organization_id, gpt_definition_id, name, description, model, configuration, is_active, created_at, updated_at)
                VALUES (:user_id, :organization_id, :gpt_definition_id, :name, :description, :model, :configuration, :is_active, :created_at, :updated_at)
            """), dashboard_subscriptions_data)
            session.commit()
            results['dashboard_gpt_subscriptions'] = len(dashboard_subscriptions_data)
            print(f"  ✅ dashboard_gpt_subscriptions: {len(dashboard_subscriptions_data)} records")
            dashboard_subscription_ids = get_table_ids(session, "dashboard_gpt_subscriptions")
            subscription_ids = dashboard_subscription_ids
        except Exception as e:
            print(f"  ⚠️ dashboard_gpt_subscriptions: {e}")
            results['dashboard_gpt_subscriptions'] = 0
            dashboard_subscription_ids = [1, 2, 3]  # Fallback IDs
            subscription_ids = dashboard_subscription_ids
    else:
        print(f"  ⚠️ dashboard_gpt_subscriptions already has {len(dashboard_subscription_ids)} records, skipping...")
        results['dashboard_gpt_subscriptions'] = len(dashboard_subscription_ids)
        subscription_ids = dashboard_subscription_ids
    
    # Create dashboard_categories first (needed for gpt_categories foreign key)
    print("  🔧 Creating dashboard categories...")
    dashboard_categories_data = []
    for i in range(15):
        dashboard_categories_data.append({
            'name': f'Category {i+1}',
            'description': f'Dashboard category {i+1} for GPT classification',
            'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    try:
        session.execute(text("""
            INSERT INTO dashboard_categories (name, description, created_at)
            VALUES (:name, :description, :created_at)
        """), dashboard_categories_data)
        print(f"  ✅ dashboard_categories: {len(dashboard_categories_data)} records")
    except Exception as e:
        print(f"  ⚠️ dashboard_categories: {e}")
        session.rollback()
    session.commit()
    
    # Ensure we have valid IDs
    if not gpt_definition_ids:
        print("  ⚠️ No GPT definition IDs found, creating fallback")
        gpt_definition_ids = [1]
    if not subscription_ids:
        print("  ⚠️ No subscription IDs found, creating fallback")
        subscription_ids = [1]
    if not context_ids:
        print("  ⚠️ No context IDs found, creating fallback")
        context_ids = [1]
    
    # Dashboard Context Templates
    print("  🔧 Creating dashboard context templates...")
    dashboard_context_templates_data = []
    for i in range(40):
        dashboard_context_templates_data.append({
            'name': f'Template {i+1}',
            'description': f'Dashboard context template {i+1}',
            'category': random.choice(['education', 'analytics', 'reporting']),
            'configuration': json.dumps({'template_type': 'dashboard', 'version': '1.0'}),
            'meta_data': json.dumps({'created_by': 'system'}),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 60)),
            'updated_at': datetime.now() - timedelta(days=random.randint(1, 30)),
            'created_by': random.choice(user_ids)
        })
    
    try:
        session.execute(text("""
            INSERT INTO dashboard_context_templates (name, description, category, configuration, meta_data, created_at, updated_at, created_by)
            VALUES (:name, :description, :category, :configuration, :meta_data, :created_at, :updated_at, :created_by)
        """), dashboard_context_templates_data)
        results['dashboard_context_templates'] = len(dashboard_context_templates_data)
        print(f"  ✅ dashboard_context_templates: {len(dashboard_context_templates_data)} records")
    except Exception as e:
        print(f"  ⚠️ dashboard_context_templates: {e}")
        results['dashboard_context_templates'] = 0
    
    # Dashboard GPT Contexts
    print("  🔧 Creating dashboard GPT contexts...")
    dashboard_gpt_contexts_data = []
    for i in range(50):
        dashboard_gpt_contexts_data.append({
            'user_id': random.choice(user_ids),
            'primary_gpt_id': random.choice(gpt_definition_ids) if gpt_definition_ids else 1,
            'name': f'Dashboard Context {i+1}',
            'description': f'Dashboard GPT context {i+1}',
            'context_data': json.dumps({'dashboard_id': f'dash_{i+1}', 'widgets': ['chart', 'table']}),
            'is_active': random.choice([True, False]),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 60)),
            'updated_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    try:
        session.execute(text("""
            INSERT INTO dashboard_gpt_contexts (user_id, primary_gpt_id, name, description, context_data, is_active, created_at, updated_at)
            VALUES (:user_id, :primary_gpt_id, :name, :description, :context_data, :is_active, :created_at, :updated_at)
        """), dashboard_gpt_contexts_data)
        session.commit()
        results['dashboard_gpt_contexts'] = len(dashboard_gpt_contexts_data)
        print(f"  ✅ dashboard_gpt_contexts: {len(dashboard_gpt_contexts_data)} records")
        context_ids = get_table_ids(session, "dashboard_gpt_contexts")
    except Exception as e:
        print(f"  ⚠️ dashboard_gpt_contexts: {e}")
        results['dashboard_gpt_contexts'] = 0
    
    # Dashboard Resource Usage
    print("  🔧 Creating dashboard resource usage...")
    dashboard_resource_usage_data = []
    for i in range(100):
        dashboard_resource_usage_data.append({
            'resource_id': f'resource_{i+1}',
            'resource_type': random.choice(['API', 'CACHE', 'CPU', 'DATABASE', 'GPU', 'MEMORY', 'NETWORK', 'STORAGE']),
            'metric_type': random.choice(['COST', 'EFFICIENCY', 'ERROR_RATE', 'LATENCY', 'THROUGHPUT', 'USAGE']),
            'value': round(random.uniform(0.1, 100.0), 2),
            'unit': random.choice(['MB', 'GB', 'ms', 'req/s', '%']),
            'timestamp': datetime.now() - timedelta(days=random.randint(1, 30)),
            'meta_data': json.dumps({'source': 'dashboard', 'version': '1.0'}),
            'user_id': random.choice(user_ids),
            'project_id': 1,  # Use valid project ID 1
            'organization_id': random.choice(organization_ids)
        })
    
    try:
        session.execute(text("""
            INSERT INTO dashboard_resource_usage (resource_id, resource_type, metric_type, value, unit, timestamp, meta_data, user_id, project_id, organization_id)
            VALUES (:resource_id, :resource_type, :metric_type, :value, :unit, :timestamp, :meta_data, :user_id, :project_id, :organization_id)
        """), dashboard_resource_usage_data)
        results['dashboard_resource_usage'] = len(dashboard_resource_usage_data)
        print(f"  ✅ dashboard_resource_usage: {len(dashboard_resource_usage_data)} records")
    except Exception as e:
        print(f"  ⚠️ dashboard_resource_usage: {e}")
        results['dashboard_resource_usage'] = 0
        session.rollback()
    session.commit()
    
    # Dashboard Context Backups
    print("  🔧 Creating dashboard context backups...")
    # Use context_ids from dashboard_gpt_contexts that we already created
    if not context_ids:
        print("  ⚠️ No context IDs found, creating fallback")
        context_ids = [1]
    
    dashboard_context_backups_data = []
    for i in range(80):
        dashboard_context_backups_data.append({
            'context_id': random.choice(context_ids),
            'backup_data': json.dumps({'context': f'Dashboard Backup {i+1}', 'data': 'backup_data'}),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    try:
        session.execute(text("""
            INSERT INTO dashboard_context_backups (context_id, backup_data, created_at)
            VALUES (:context_id, :backup_data, :created_at)
        """), dashboard_context_backups_data)
        results['dashboard_context_backups'] = len(dashboard_context_backups_data)
        print(f"  ✅ dashboard_context_backups: {len(dashboard_context_backups_data)} records")
    except Exception as e:
        print(f"  ⚠️ dashboard_context_backups: {e}")
        results['dashboard_context_backups'] = 0
        session.rollback()
    session.commit()
    
    # Dashboard Context GPTs
    print("  🔧 Creating dashboard context GPTs...")
    dashboard_context_gpts_data = []
    for i in range(60):
        dashboard_context_gpts_data.append({
            'context_id': random.choice(context_ids),
            'gpt_id': random.choice(gpt_definition_ids)  # Use gpt_definitions
        })
    
    try:
        session.execute(text("""
            INSERT INTO dashboard_context_gpts (context_id, gpt_id)
            VALUES (:context_id, :gpt_id)
        """), dashboard_context_gpts_data)
        results['dashboard_context_gpts'] = len(dashboard_context_gpts_data)
        print(f"  ✅ dashboard_context_gpts: {len(dashboard_context_gpts_data)} records")
    except Exception as e:
        print(f"  ⚠️ dashboard_context_gpts: {e}")
        results['dashboard_context_gpts'] = 0
        session.rollback()
    session.commit()
    
    # Dashboard Context Interactions
    print("  🔧 Creating dashboard context interactions...")
    dashboard_context_interactions_data = []
    for i in range(200):
        dashboard_context_interactions_data.append({
            'context_id': random.choice(context_ids),
            'gpt_id': random.choice(gpt_definition_ids),  # Use gpt_definitions
            'interaction_type': random.choice(['QUERY', 'RESPONSE', 'CONTEXT_CREATE', 'CONTEXT_UPDATE']),
            'content': json.dumps({'query': f'Interaction {i+1}', 'response': f'Response {i+1}'}),
            'meta_data': json.dumps({'source': 'dashboard', 'version': '1.0'}),
            'timestamp': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    try:
        session.execute(text("""
            INSERT INTO dashboard_context_interactions (context_id, gpt_id, interaction_type, content, meta_data, timestamp)
            VALUES (:context_id, :gpt_id, :interaction_type, :content, :meta_data, :timestamp)
        """), dashboard_context_interactions_data)
        results['dashboard_context_interactions'] = len(dashboard_context_interactions_data)
        print(f"  ✅ dashboard_context_interactions: {len(dashboard_context_interactions_data)} records")
    except Exception as e:
        print(f"  ⚠️ dashboard_context_interactions: {e}")
        results['dashboard_context_interactions'] = 0
        session.rollback()
    session.commit()
    
    # Dashboard Context Metrics
    print("  🔧 Creating dashboard context metrics...")
    dashboard_context_metrics_data = []
    for i in range(150):
        dashboard_context_metrics_data.append({
            'context_id': random.choice(context_ids),
            'metric_type': random.choice(['tokens_used', 'response_time', 'accuracy', 'user_satisfaction']),
            'metric_data': json.dumps({'value': round(random.uniform(0.1, 100.0), 2), 'unit': 'percentage'}),
            'timestamp': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    try:
        session.execute(text("""
            INSERT INTO dashboard_context_metrics (context_id, metric_type, metric_data, timestamp)
            VALUES (:context_id, :metric_type, :metric_data, :timestamp)
        """), dashboard_context_metrics_data)
        results['dashboard_context_metrics'] = len(dashboard_context_metrics_data)
        print(f"  ✅ dashboard_context_metrics: {len(dashboard_context_metrics_data)} records")
    except Exception as e:
        print(f"  ⚠️ dashboard_context_metrics: {e}")
        results['dashboard_context_metrics'] = 0
        session.rollback()
    session.commit()
    
    # Dashboard Context Optimizations
    print("  🔧 Creating dashboard context optimizations...")
    dashboard_context_optimizations_data = []
    for i in range(40):
        dashboard_context_optimizations_data.append({
            'context_id': random.choice(context_ids),
            'optimization_target': random.choice(['PERFORMANCE', 'MEMORY', 'SPEED', 'ACCURACY']),
            'optimization_plan': json.dumps({'type': 'performance', 'value': round(random.uniform(0.1, 1.0), 2)}),
            'optimization_result': json.dumps({'success': random.choice([True, False]), 'improvement': round(random.uniform(0.1, 0.5), 2)}),
            'metrics_before': json.dumps({'baseline': round(random.uniform(50, 80), 2)}),
            'metrics_after': json.dumps({'optimized': round(random.uniform(80, 95), 2)}),
            'timestamp': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    try:
        session.execute(text("""
            INSERT INTO dashboard_context_optimizations (context_id, optimization_target, optimization_plan, optimization_result, metrics_before, metrics_after, timestamp)
            VALUES (:context_id, :optimization_target, :optimization_plan, :optimization_result, :metrics_before, :metrics_after, :timestamp)
        """), dashboard_context_optimizations_data)
        results['dashboard_context_optimizations'] = len(dashboard_context_optimizations_data)
        print(f"  ✅ dashboard_context_optimizations: {len(dashboard_context_optimizations_data)} records")
    except Exception as e:
        print(f"  ⚠️ dashboard_context_optimizations: {e}")
        results['dashboard_context_optimizations'] = 0
        session.rollback()
    session.commit()
    
    # Dashboard Context Summaries
    print("  🔧 Creating dashboard context summaries...")
    dashboard_context_summaries_data = []
    for i in range(50):
        dashboard_context_summaries_data.append({
            'context_id': random.choice(context_ids),
            'summary': json.dumps({'text': f'Dashboard context summary {i+1}', 'key_points': ['point1', 'point2', 'point3']}),
            'meta_data': json.dumps({'source': 'dashboard', 'version': '1.0'}),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    try:
        session.execute(text("""
            INSERT INTO dashboard_context_summaries (context_id, summary, meta_data, created_at)
            VALUES (:context_id, :summary, :meta_data, :created_at)
        """), dashboard_context_summaries_data)
        results['dashboard_context_summaries'] = len(dashboard_context_summaries_data)
        print(f"  ✅ dashboard_context_summaries: {len(dashboard_context_summaries_data)} records")
    except Exception as e:
        print(f"  ⚠️ dashboard_context_summaries: {e}")
        results['dashboard_context_summaries'] = 0
        session.rollback()
    session.commit()
    
    # Dashboard Context Validations
    print("  🔧 Creating dashboard context validations...")
    dashboard_context_validations_data = []
    for i in range(30):
        dashboard_context_validations_data.append({
            'context_id': random.choice(context_ids),
            'validation_type': random.choice(['SYNTAX', 'LOGIC', 'COMPLETENESS', 'ACCURACY']),
            'is_valid': random.choice([True, False]),
            'issues': json.dumps([f'Issue {i+1}', f'Issue {i+2}']),
            'warnings': json.dumps([f'Warning {i+1}', f'Warning {i+2}']),
            'details': json.dumps({'source': 'dashboard', 'version': '1.0'}),
            'timestamp': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    try:
        session.execute(text("""
            INSERT INTO dashboard_context_validations (context_id, validation_type, is_valid, issues, warnings, details, timestamp)
            VALUES (:context_id, :validation_type, :is_valid, :issues, :warnings, :details, :timestamp)
        """), dashboard_context_validations_data)
        results['dashboard_context_validations'] = len(dashboard_context_validations_data)
        print(f"  ✅ dashboard_context_validations: {len(dashboard_context_validations_data)} records")
    except Exception as e:
        print(f"  ⚠️ dashboard_context_validations: {e}")
        results['dashboard_context_validations'] = 0
        session.rollback()
    session.commit()
    
    # Dashboard GPT Integrations
    print("  🔧 Creating dashboard GPT integrations...")
    dashboard_gpt_integrations_data = []
    for i in range(25):
        dashboard_gpt_integrations_data.append({
            'user_id': random.choice(user_ids),
            'organization_id': random.choice(organization_ids),
            'name': f'Integration {i+1}',
            'description': f'Integration description {i+1}',
            'integration_type': random.choice(['API', 'WEBHOOK', 'PLUGIN', 'EXTENSION']),
            'configuration': json.dumps({'endpoint': f'https://api.example.com/integration_{i+1}'}),
            'is_active': random.choice([True, False]),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
            'updated_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    try:
        session.execute(text("""
            INSERT INTO dashboard_gpt_integrations (user_id, organization_id, name, description, integration_type, configuration, is_active, created_at, updated_at)
            VALUES (:user_id, :organization_id, :name, :description, :integration_type, :configuration, :is_active, :created_at, :updated_at)
        """), dashboard_gpt_integrations_data)
        results['dashboard_gpt_integrations'] = len(dashboard_gpt_integrations_data)
        print(f"  ✅ dashboard_gpt_integrations: {len(dashboard_gpt_integrations_data)} records")
    except Exception as e:
        print(f"  ⚠️ dashboard_gpt_integrations: {e}")
        results['dashboard_gpt_integrations'] = 0
        session.rollback()
    session.commit()
    
    # Dashboard GPT Usage History
    print("  🔧 Creating dashboard GPT usage history...")
    dashboard_gpt_usage_history_data = []
    for i in range(30):
        dashboard_gpt_usage_history_data.append({
            'subscription_id': random.choice(dashboard_subscription_ids),
            'interaction_type': random.choice(['QUERY', 'RESPONSE', 'CONTEXT_CREATE', 'CONTEXT_UPDATE']),
            'details': json.dumps({'tokens': random.randint(10, 1000), 'cost': round(random.uniform(0.01, 10.0), 2)}),
            'timestamp': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    try:
        session.execute(text("""
            INSERT INTO dashboard_gpt_usage_history (subscription_id, interaction_type, details, timestamp)
            VALUES (:subscription_id, :interaction_type, :details, :timestamp)
        """), dashboard_gpt_usage_history_data)
        results['dashboard_gpt_usage_history'] = len(dashboard_gpt_usage_history_data)
        print(f"  ✅ dashboard_gpt_usage_history: {len(dashboard_gpt_usage_history_data)} records")
    except Exception as e:
        print(f"  ⚠️ dashboard_gpt_usage_history: {e}")
        results['dashboard_gpt_usage_history'] = 0
        session.rollback()
    session.commit()
    
    # Dashboard Optimization Events
    print("  🔧 Creating dashboard optimization events...")
    dashboard_optimization_events_data = []
    for i in range(100):
        dashboard_optimization_events_data.append({
            'event_type': random.choice(['PERFORMANCE_OPTIMIZATION', 'MEMORY_OPTIMIZATION', 'SPEED_OPTIMIZATION']),
            'status': random.choice(['DETECTED', 'IN_PROGRESS', 'RESOLVED', 'FAILED']),
            'severity': random.choice(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']),
            'resource_id': f'resource_{i+1}',
            'resource_type': random.choice(['CPU', 'MEMORY', 'STORAGE', 'NETWORK', 'GPU', 'API', 'DATABASE', 'CACHE']),
            'metric_type': random.choice(['USAGE', 'THROUGHPUT', 'EFFICIENCY']),
            'description': f'Optimization event {i+1}',
            'action_taken': f'Action {i+1}',
            'action_result': random.choice(['SUCCESS', 'FAILED', 'PARTIAL']),
            'detected_at': datetime.now() - timedelta(days=random.randint(1, 30)),
            'resolved_at': datetime.now() - timedelta(days=random.randint(1, 15)) if random.choice([True, False]) else None,
            'user_id': random.choice(user_ids),
            'project_id': 1,
            'organization_id': random.choice(organization_ids),
            'meta_data': json.dumps({'source': 'dashboard', 'version': '1.0'})
        })
    
    try:
        session.execute(text("""
            INSERT INTO dashboard_optimization_events (event_type, status, severity, resource_id, resource_type, metric_type, description, action_taken, action_result, detected_at, resolved_at, user_id, project_id, organization_id, meta_data)
            VALUES (:event_type, :status, :severity, :resource_id, :resource_type, :metric_type, :description, :action_taken, :action_result, :detected_at, :resolved_at, :user_id, :project_id, :organization_id, :meta_data)
        """), dashboard_optimization_events_data)
        results['dashboard_optimization_events'] = len(dashboard_optimization_events_data)
        print(f"  ✅ dashboard_optimization_events: {len(dashboard_optimization_events_data)} records")
    except Exception as e:
        print(f"  ⚠️ dashboard_optimization_events: {e}")
        results['dashboard_optimization_events'] = 0
        session.rollback()
    session.commit()
    
    # Dashboard Resource Optimizations
    print("  🔧 Creating dashboard resource optimizations...")
    dashboard_resource_optimizations_data = []
    for i in range(60):
        dashboard_resource_optimizations_data.append({
            'resource_type': random.choice(['CPU', 'MEMORY', 'STORAGE', 'NETWORK', 'GPU', 'API', 'DATABASE', 'CACHE']),
            'metric_type': random.choice(['USAGE', 'THROUGHPUT', 'EFFICIENCY']),
            'current_value': round(random.uniform(50, 90), 2),
            'recommended_value': round(random.uniform(60, 95), 2),
            'potential_savings': round(random.uniform(5, 25), 2),
            'confidence_score': round(random.uniform(0.7, 0.95), 2),
            'recommendation': f'Optimization recommendation {i+1}',
            'status': random.choice(['PENDING', 'APPLIED', 'REJECTED']),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
            'applied_at': datetime.now() - timedelta(days=random.randint(1, 15)) if random.choice([True, False]) else None,
            'meta_data': json.dumps({'source': 'dashboard', 'version': '1.0'}),
            'user_id': random.choice(user_ids),
            'project_id': 1,
            'organization_id': random.choice(organization_ids)
        })
    
    try:
        session.execute(text("""
            INSERT INTO dashboard_resource_optimizations (resource_type, metric_type, current_value, recommended_value, potential_savings, confidence_score, recommendation, status, created_at, applied_at, meta_data, user_id, project_id, organization_id)
            VALUES (:resource_type, :metric_type, :current_value, :recommended_value, :potential_savings, :confidence_score, :recommendation, :status, :created_at, :applied_at, :meta_data, :user_id, :project_id, :organization_id)
        """), dashboard_resource_optimizations_data)
        results['dashboard_resource_optimizations'] = len(dashboard_resource_optimizations_data)
        print(f"  ✅ dashboard_resource_optimizations: {len(dashboard_resource_optimizations_data)} records")
    except Exception as e:
        print(f"  ⚠️ dashboard_resource_optimizations: {e}")
        results['dashboard_resource_optimizations'] = 0
        session.rollback()
    session.commit()
    
    # Dashboard Resource Sharing
    print("  🔧 Creating dashboard resource sharing...")
    dashboard_resource_sharing_data = []
    for i in range(40):
        dashboard_resource_sharing_data.append({
            'resource_id': f'resource_{random.randint(1, 100)}',
            'resource_type': random.choice(['CPU', 'MEMORY', 'STORAGE', 'NETWORK', 'GPU', 'API', 'DATABASE', 'CACHE']),
            'is_shared': random.choice([True, False]),
            'sharing_type': random.choice(['USER', 'PROJECT', 'ORGANIZATION']),
            'sharing_permissions': json.dumps({'level': random.choice(['READ', 'WRITE', 'ADMIN'])}),
            'sharing_scope': random.choice(['PRIVATE', 'PUBLIC', 'RESTRICTED']),
            'shared_at': datetime.now() - timedelta(days=random.randint(1, 30)),
            'expires_at': datetime.now() + timedelta(days=random.randint(1, 90)) if random.choice([True, False]) else None,
            'owner_id': random.choice(user_ids),
            'shared_with_user_id': random.choice(user_ids),
            'shared_with_project_id': 1,
            'shared_with_organization_id': random.choice(organization_ids),
            'meta_data': json.dumps({'source': 'dashboard', 'version': '1.0'})
        })
    
    try:
        session.execute(text("""
            INSERT INTO dashboard_resource_sharing (resource_id, resource_type, is_shared, sharing_type, sharing_permissions, sharing_scope, shared_at, expires_at, owner_id, shared_with_user_id, shared_with_project_id, shared_with_organization_id, meta_data)
            VALUES (:resource_id, :resource_type, :is_shared, :sharing_type, :sharing_permissions, :sharing_scope, :shared_at, :expires_at, :owner_id, :shared_with_user_id, :shared_with_project_id, :shared_with_organization_id, :meta_data)
        """), dashboard_resource_sharing_data)
        results['dashboard_resource_sharing'] = len(dashboard_resource_sharing_data)
        print(f"  ✅ dashboard_resource_sharing: {len(dashboard_resource_sharing_data)} records")
    except Exception as e:
        print(f"  ⚠️ dashboard_resource_sharing: {e}")
        results['dashboard_resource_sharing'] = 0
        session.rollback()
    session.commit()
    
    # Dashboard Resource Thresholds
    print("  🔧 Creating dashboard resource thresholds...")
    dashboard_resource_thresholds_data = []
    for i in range(20):
        dashboard_resource_thresholds_data.append({
            'resource_type': random.choice(['CPU', 'MEMORY', 'STORAGE', 'NETWORK', 'GPU', 'API', 'DATABASE', 'CACHE']),
            'metric_type': random.choice(['USAGE', 'THROUGHPUT', 'EFFICIENCY']),
            'threshold_value': round(random.uniform(0.1, 100.0), 2),
            'threshold_type': random.choice(['WARNING', 'CRITICAL', 'INFO']),
            'action': random.choice(['ALERT', 'AUTO_SCALE', 'NOTIFY', 'SHUTDOWN']),
            'meta_data': json.dumps({'source': 'dashboard', 'version': '1.0'}),
            'user_id': random.choice(user_ids),
            'project_id': 1,
            'organization_id': random.choice(organization_ids)
        })
    
    try:
        session.execute(text("""
            INSERT INTO dashboard_resource_thresholds (resource_type, metric_type, threshold_value, threshold_type, action, meta_data, user_id, project_id, organization_id)
            VALUES (:resource_type, :metric_type, :threshold_value, :threshold_type, :action, :meta_data, :user_id, :project_id, :organization_id)
        """), dashboard_resource_thresholds_data)
        results['dashboard_resource_thresholds'] = len(dashboard_resource_thresholds_data)
        print(f"  ✅ dashboard_resource_thresholds: {len(dashboard_resource_thresholds_data)} records")
    except Exception as e:
        print(f"  ⚠️ dashboard_resource_thresholds: {e}")
        results['dashboard_resource_thresholds'] = 0
        session.rollback()
    session.commit()
    
    return results
