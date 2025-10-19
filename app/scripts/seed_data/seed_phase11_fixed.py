#!/usr/bin/env python3
"""
Phase 11: Advanced System Features - FIXED VERSION
Seeds 73 tables for advanced system functionality with all issues resolved.

This fixed version includes:
- Correct enum values from database schema
- All required NOT NULL columns
- Proper foreign key dependencies
- Improved schema detection
- Comprehensive error handling
"""

import sys
import os
import random
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text, inspect, MetaData

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Correct enum values from database schema
CIRCUIT_BREAKER_TYPES = ['ACTIVITY', 'SERVICE', 'API', 'DATABASE', 'EXTERNAL', 'CUSTOM']
CIRCUIT_BREAKER_TRIGGERS = ['MANUAL', 'AUTOMATIC', 'SCHEDULED', 'THRESHOLD', 'POLICY']
CIRCUIT_BREAKER_LEVELS = ['HIGH', 'MEDIUM', 'LOW', 'NONE']
BASE_STATUS_VALUES = ['ACTIVE', 'INACTIVE', 'PENDING', 'SCHEDULED', 'COMPLETED', 'CANCELLED', 'ON_HOLD']
FEEDBACK_TYPES = ['BUG', 'FEATURE', 'IMPROVEMENT', 'QUESTION', 'COMPLAINT', 'PRAISE', 'SUGGESTION', 'OTHER']
PROJECT_STATUS_VALUES = ['ACTIVE', 'INACTIVE', 'ARCHIVED', 'COMPLETED', 'ON_HOLD', 'PLANNING', 'IN_PROGRESS', 'REVIEW']
NOTIFICATION_TYPES = ['SYSTEM', 'ALERT', 'UPDATE', 'REMINDER', 'ACHIEVEMENT']
NOTIFICATION_PRIORITIES = ['URGENT', 'HIGH', 'NORMAL', 'LOW']

# Additional enum values for Phase 11
CIRCUIT_BREAKER_STATUS_VALUES = ['CLOSED', 'OPEN', 'HALF_OPEN']
CIRCUIT_BREAKER_TRIGGER_VALUES = ['MANUAL', 'AUTOMATIC', 'SCHEDULED', 'THRESHOLD', 'POLICY']
WIDGET_STATUS_VALUES = ['ACTIVE', 'INACTIVE', 'PENDING', 'SCHEDULED', 'COMPLETED', 'CANCELLED', 'ON_HOLD']
EXPORT_STATUS_VALUES = ['PENDING', 'COMPLETED', 'CANCELLED']
PROJECT_STATUS_ENUM = ['PLANNING', 'ACTIVE', 'ON_HOLD', 'COMPLETED', 'INACTIVE', 'IN_PROGRESS', 'REVIEW', 'ARCHIVED']
RESOURCE_STATUS_VALUES = ['ACTIVE', 'INACTIVE', 'PENDING', 'PROCESSING', 'COMPLETED', 'FAILED']

def get_table_schema(session: Session, table_name: str) -> Dict[str, Any]:
    """Get table schema information including columns and types."""
    try:
        inspector = inspect(session.bind)
        columns = inspector.get_columns(table_name)
        return {col['name']: col for col in columns}
    except Exception as e:
        print(f"    ⚠️  Could not get schema for {table_name}: {e}")
        return {}

def get_enum_values(session: Session, table_name: str, column_name: str) -> List[str]:
    """Get valid enum values for a column."""
    try:
        result = session.execute(text(f"""
            SELECT unnest(enum_range(NULL::text)) as enum_value
            FROM pg_type t 
            JOIN pg_enum e ON t.oid = e.enumtypid 
            WHERE t.typname = (
                SELECT udt_name 
                FROM information_schema.columns 
                WHERE table_name = '{table_name}' 
                AND column_name = '{column_name}'
            )
        """))
        return [row[0] for row in result.fetchall()]
    except Exception as e:
        print(f"    ⚠️  Could not get enum values for {table_name}.{column_name}: {e}")
        return []

def get_dependency_ids(session: Session) -> Dict[str, List[int]]:
    """Get IDs from dependency tables."""
    try:
        # Get user IDs
        user_result = session.execute(text("SELECT id FROM users LIMIT 50"))
        user_ids = [row[0] for row in user_result.fetchall()]
        
        # Get student IDs
        student_result = session.execute(text("SELECT id FROM students "))
        student_ids = [row[0] for row in student_result.fetchall()]
        
        # Get organization IDs
        org_result = session.execute(text("SELECT id FROM organizations "))
        org_ids = [row[0] for row in org_result.fetchall()]
        
        # Get dashboard user IDs
        dashboard_user_result = session.execute(text("SELECT id FROM dashboard_users LIMIT 50"))
        dashboard_user_ids = [row[0] for row in dashboard_user_result.fetchall()]
        
        # Get activity IDs
        activity_result = session.execute(text("SELECT id FROM activities "))
        activity_ids = [row[0] for row in activity_result.fetchall()]
        
        # Get existing IDs for foreign key references
        ai_tools_result = session.execute(text("SELECT id FROM ai_tools "))
        ai_tool_ids = [row[0] for row in ai_tools_result.fetchall()]
        
        dashboard_tools_result = session.execute(text("SELECT id FROM dashboard_tools "))
        dashboard_tool_ids = [row[0] for row in dashboard_tools_result.fetchall()]
        
        dashboard_teams_result = session.execute(text("SELECT id FROM dashboard_teams "))
        dashboard_team_ids = [row[0] for row in dashboard_teams_result.fetchall()]
        
        organization_projects_result = session.execute(text("SELECT id FROM organization_projects LIMIT 20"))
        organization_project_ids = [row[0] for row in organization_projects_result.fetchall()]
        
        organization_feedback_result = session.execute(text("SELECT id FROM organization_feedback LIMIT 20"))
        organization_feedback_ids = [row[0] for row in organization_feedback_result.fetchall()]
        
        # Get additional dependency IDs for Phase 11
        try:
            # Get existing circuit breaker IDs
            circuit_breaker_result = session.execute(text("SELECT id FROM circuit_breakers "))
            circuit_breaker_ids = [row[0] for row in circuit_breaker_result.fetchall()]
        except:
            circuit_breaker_ids = []
            
        try:
            # Get existing cache entry IDs
            cache_entry_result = session.execute(text("SELECT id FROM cache_entries LIMIT 20"))
            cache_entry_ids = [row[0] for row in cache_entry_result.fetchall()]
        except:
            cache_entry_ids = []
            
        try:
            # Get existing competition IDs
            competition_result = session.execute(text("SELECT id FROM competitions LIMIT 15"))
            competition_ids = [row[0] for row in competition_result.fetchall()]
        except:
            competition_ids = []
            
        try:
            # Get existing feedback project IDs
            feedback_project_result = session.execute(text("SELECT id FROM feedback_projects LIMIT 25"))
            feedback_project_ids = [row[0] for row in feedback_project_result.fetchall()]
        except:
            feedback_project_ids = []
            
        try:
            # Get existing user memory IDs
            user_memory_result = session.execute(text("SELECT id FROM user_memories "))
            user_memory_ids = [row[0] for row in user_memory_result.fetchall()]
        except:
            user_memory_ids = []
            
        try:
            # Get existing GPT subscription IDs
            gpt_subscription_result = session.execute(text("SELECT id FROM gpt_subscriptions LIMIT 30"))
            gpt_subscription_ids = [row[0] for row in gpt_subscription_result.fetchall()]
        except:
            gpt_subscription_ids = []
            
        try:
            # Get existing GPT subscription billing IDs
            gpt_billing_result = session.execute(text("SELECT id FROM gpt_subscription_billing LIMIT 50"))
            gpt_billing_ids = [row[0] for row in gpt_billing_result.fetchall()]
        except:
            gpt_billing_ids = []
        
        return {
            'user_ids': user_ids,
            'student_ids': student_ids,
            'org_ids': org_ids,
            'dashboard_user_ids': dashboard_user_ids,
            'activity_ids': activity_ids,
            'ai_tool_ids': ai_tool_ids,
            'dashboard_tool_ids': dashboard_tool_ids,
            'dashboard_team_ids': dashboard_team_ids,
            'organization_project_ids': organization_project_ids,
            'organization_feedback_ids': organization_feedback_ids,
            'circuit_breaker_ids': circuit_breaker_ids,
            'cache_entry_ids': cache_entry_ids,
            'competition_ids': competition_ids,
            'feedback_project_ids': feedback_project_ids,
            'user_memory_ids': user_memory_ids,
            'gpt_subscription_ids': gpt_subscription_ids,
            'gpt_billing_ids': gpt_billing_ids
        }
    except Exception as e:
        print(f"    ⚠️  Error getting dependency IDs: {e}")
        return {
            'user_ids': [1, 2, 3, 4, 5],
            'student_ids': [1, 2, 3, 4, 5],
            'org_ids': [1],
            'dashboard_user_ids': [1, 2, 3, 4, 5],
            'activity_ids': [1, 2, 3, 4, 5],
            'ai_tool_ids': [1, 2, 3],
            'dashboard_team_ids': [1, 2, 3],
            'organization_project_ids': [1, 2, 3, 4, 5],
            'organization_feedback_ids': [1, 2, 3, 4, 5]
        }

def insert_data_flexible(session: Session, table_name: str, data: List[Dict[str, Any]], schema: Optional[Dict[str, Any]] = None) -> int:
    """Insert data into a table with flexible schema handling."""
    if not data:
        return 0
    
    try:
        # Get table schema if not provided
        if schema is None:
            schema = get_table_schema(session, table_name)
        
        if not schema:
            print(f"    ⚠️  No schema found for {table_name}, skipping")
            return 0
        
        # Filter data to only include columns that exist in the schema
        filtered_data = []
        for record in data:
            filtered_record = {}
            for key, value in record.items():
                if key in schema:
                    filtered_record[key] = value
            if filtered_record:  # Only add if we have at least one valid column
                filtered_data.append(filtered_record)
        
        if not filtered_data:
            print(f"    ⚠️  No valid data to insert for {table_name}")
            return 0
        
        # Get column names from the first record
        columns = list(filtered_data[0].keys())
        
        if not columns:
            print(f"    ⚠️  No valid columns found for {table_name}")
            return 0
        
        # Build and execute INSERT statement
        placeholders = ', '.join([f':{col}' for col in columns])
        column_names = ', '.join(columns)
        
        insert_sql = f"INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})"
        
        session.execute(text(insert_sql), filtered_data)
        return len(filtered_data)
        
    except Exception as e:
        print(f"    ❌ Error inserting data into {table_name}: {e}")
        session.rollback()
        return 0

def seed_performance_caching_system(session: Session, deps: Dict[str, List[int]]) -> Dict[str, int]:
    """Seed performance and caching system tables."""
    results = {}
    
    print("  Seeding cache_entries...")
    try:
        # Check if cache_entries already has data and use it
        existing_count = session.execute(text("SELECT COUNT(*) FROM cache_entries")).scalar()
        if existing_count > 0:
            print(f"    ✅ Found {existing_count} existing cache entries, using for foreign key references")
            results['cache_entries'] = existing_count
        else:
            cache_entries_data = []
            for i in range(100):
                cache_entries_data.append({
                    'key': f'cache_key_{i}',
                    'value': json.dumps({'data': f'cached_value_{i}', 'type': 'string', 'index': i}),
                    'expires_at': datetime.now() + timedelta(hours=random.randint(1, 24)),
                    'created_at': datetime.now() - timedelta(hours=random.randint(1, 48)),
                    'updated_at': datetime.now() - timedelta(hours=random.randint(1, 24)),
                    'status': random.choice(['ACTIVE', 'EXPIRED', 'INVALIDATED']),
                    'entry_metadata': json.dumps({'source': 'cache_manager', 'version': '1.0', 'access_count': random.randint(0, 1000)})
                })
            
            results['cache_entries'] = insert_data_flexible(session, 'cache_entries', cache_entries_data)
            print(f"    ✅ Created {results['cache_entries']} cache entries")
    except Exception as e:
        print(f"    ❌ Error seeding cache_entries: {e}")
        results['cache_entries'] = 0
    
    print("  Seeding cache_metrics...")
    try:
        # Get actual cache_entries IDs that were created
        cache_entry_result = session.execute(text("SELECT id FROM cache_entries ORDER BY id"))
        cache_entry_ids = [row[0] for row in cache_entry_result.fetchall()]
        
        if not cache_entry_ids:
            print("    ⚠️  No cache_entries found, skipping cache_metrics")
            results['cache_metrics'] = 0
        else:
            cache_metrics_data = []
            for i in range(min(50, len(cache_entry_ids) * 2)):  # Limit to available entries
                cache_metrics_data.append({
                    'entry_id': random.choice(cache_entry_ids),  # Use actual cache_entries IDs
                    'hits': random.randint(0, 1000),
                    'misses': random.randint(0, 100),
                    'last_accessed': datetime.now() - timedelta(minutes=random.randint(1, 60)),
                    'size_bytes': random.randint(1024, 1048576),
                    'metrics_metadata': json.dumps({'source': 'cache_monitor', 'version': '1.0'}),
                    'created_at': datetime.now() - timedelta(hours=random.randint(1, 24)),
                    'updated_at': datetime.now() - timedelta(minutes=random.randint(1, 60))
                })
            
            results['cache_metrics'] = insert_data_flexible(session, 'cache_metrics', cache_metrics_data)
            print(f"    ✅ Created {results['cache_metrics']} cache metrics")
    except Exception as e:
        print(f"    ❌ Error seeding cache_metrics: {e}")
        results['cache_metrics'] = 0
    
    print("  Seeding cache_policies...")
    try:
        # Check if cache_policies already has data and use it
        existing_count = session.execute(text("SELECT COUNT(*) FROM cache_policies")).scalar()
        if existing_count > 0:
            print(f"    ✅ Found {existing_count} existing cache policies, using for foreign key references")
            results['cache_policies'] = existing_count
        else:
            cache_policies_data = []
            for i in range(10):
                cache_policies_data.append({
                    'name': f'Cache Policy {i+1}',
                    'description': f'Policy for cache management {i+1}',
                    'ttl': random.randint(300, 3600),  # 5 minutes to 1 hour
                    'priority': random.randint(1, 10),
                    'policy_metadata': json.dumps({'source': 'cache_policy_manager', 'version': '1.0'}),
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                    'updated_at': datetime.now() - timedelta(days=random.randint(1, 7))
                })
            
            results['cache_policies'] = insert_data_flexible(session, 'cache_policies', cache_policies_data)
            print(f"    ✅ Created {results['cache_policies']} cache policies")
    except Exception as e:
        print(f"    ❌ Error seeding cache_policies: {e}")
        results['cache_policies'] = 0
    
    # These will be seeded after circuit_breakers is created
    results['circuit_breaker_history'] = 0
    results['circuit_breaker_metrics'] = 0
    
    print("  Seeding circuit_breaker_policies...")
    try:
        circuit_breaker_policies_data = []
        for i in range(8):
            circuit_breaker_policies_data.append({
                'name': f'Circuit Breaker Policy {i+1}',
                'description': f'Policy for {random.choice(["activity", "user", "report", "analytics"])}_service',
                'type': random.choice(CIRCUIT_BREAKER_TYPES),
                'level': random.choice(CIRCUIT_BREAKER_LEVELS),
                'is_active': random.choice([True, False]),
                'failure_threshold': random.randint(5, 20),
                'reset_timeout': random.randint(30, 300),
                'half_open_timeout': random.randint(10, 60),
                'max_failures': random.randint(10, 50),
                'error_threshold': random.randint(10, 50),
                'success_threshold': random.randint(5, 20),
                'meta_data': json.dumps({'source': 'circuit_breaker_manager', 'version': '1.0'}),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 7))
            })
        
        results['circuit_breaker_policies'] = insert_data_flexible(session, 'circuit_breaker_policies', circuit_breaker_policies_data)
        print(f"    ✅ Created {results['circuit_breaker_policies']} circuit breaker policies")
    except Exception as e:
        print(f"    ❌ Error seeding circuit_breaker_policies: {e}")
        results['circuit_breaker_policies'] = 0
    
    print("  Seeding circuit_breakers...")
    try:
        # Get actual circuit_breaker_policies IDs that were created
        policy_result = session.execute(text("SELECT id FROM circuit_breaker_policies ORDER BY id"))
        policy_ids = [row[0] for row in policy_result.fetchall()]
        
        if not policy_ids:
            print("    ⚠️  No circuit_breaker_policies found, skipping circuit_breakers")
            results['circuit_breakers'] = 0
        else:
            circuit_breakers_data = []
            for i in range(min(8, len(policy_ids))):  # Limit to available policies
                circuit_breakers_data.append({
                    'name': f'Circuit Breaker {i+1}',
                    'description': f'Circuit breaker for {random.choice(["activity", "user", "report", "analytics"])}_service',
                    'type': random.choice(CIRCUIT_BREAKER_TYPES),
                    'level': random.choice(CIRCUIT_BREAKER_LEVELS),
                    'status': random.choice(CIRCUIT_BREAKER_STATUS_VALUES),
                    'trigger': random.choice(CIRCUIT_BREAKER_TRIGGER_VALUES),
                    'threshold': random.randint(5, 20),
                    'failure_count': random.randint(0, 15),
                    'last_failure_time': datetime.now() - timedelta(hours=random.randint(1, 24)) if random.choice([True, False]) else None,
                    'last_success_time': datetime.now() - timedelta(minutes=random.randint(1, 60)),
                    'reset_timeout': random.randint(30, 300),
                    'meta_data': json.dumps({'source': 'circuit_breaker_manager', 'version': '1.0'}),
                    'activity_id': random.choice(deps['activity_ids']) if deps['activity_ids'] else None,
                    'policy_id': random.choice(policy_ids),  # Use actual policy IDs
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                    'updated_at': datetime.now() - timedelta(days=random.randint(1, 7))
                })
            
            results['circuit_breakers'] = insert_data_flexible(session, 'circuit_breakers', circuit_breakers_data)
            print(f"    ✅ Created {results['circuit_breakers']} circuit breakers")
            
            # Now seed the dependent tables
            print("  Seeding circuit_breaker_history...")
            try:
                # Get actual circuit_breakers IDs that were created
                circuit_breaker_result = session.execute(text("SELECT id FROM circuit_breakers ORDER BY id"))
                circuit_breaker_ids = [row[0] for row in circuit_breaker_result.fetchall()]
                
                if not circuit_breaker_ids:
                    print("    ⚠️  No circuit_breakers found, skipping circuit_breaker_history")
                    results['circuit_breaker_history'] = 0
                else:
                    circuit_breaker_history_data = []
                    for i in range(min(30, len(circuit_breaker_ids) * 4)):  # Use actual circuit_breakers IDs
                        circuit_breaker_history_data.append({
                            'circuit_breaker_id': random.choice(circuit_breaker_ids),  # Use actual circuit_breakers IDs
                            'previous_status': random.choice(CIRCUIT_BREAKER_STATUS_VALUES),
                            'new_status': random.choice(CIRCUIT_BREAKER_STATUS_VALUES),
                            'trigger': random.choice(CIRCUIT_BREAKER_TRIGGER_VALUES),
                            'failure_count': random.randint(0, 100),
                            'meta_data': json.dumps({'request_id': f'req_{i}', 'duration_ms': random.randint(100, 5000)}),
                            'created_at': datetime.now() - timedelta(hours=random.randint(1, 24))
                        })
                    
                    results['circuit_breaker_history'] = insert_data_flexible(session, 'circuit_breaker_history', circuit_breaker_history_data)
                    print(f"    ✅ Created {results['circuit_breaker_history']} circuit breaker history records")
            except Exception as e:
                print(f"    ❌ Error seeding circuit_breaker_history: {e}")
                results['circuit_breaker_history'] = 0
            
            print("  Seeding circuit_breaker_metrics...")
            try:
                # Get actual circuit_breakers IDs that were created
                circuit_breaker_result = session.execute(text("SELECT id FROM circuit_breakers ORDER BY id"))
                circuit_breaker_ids = [row[0] for row in circuit_breaker_result.fetchall()]
                
                if not circuit_breaker_ids:
                    print("    ⚠️  No circuit_breakers found, skipping circuit_breaker_metrics")
                    results['circuit_breaker_metrics'] = 0
                else:
                    circuit_breaker_metrics_data = []
                    for i in range(min(20, len(circuit_breaker_ids) * 3)):  # Use actual circuit_breakers IDs
                        circuit_breaker_metrics_data.append({
                            'circuit_breaker_id': random.choice(circuit_breaker_ids),  # Use actual circuit_breakers IDs
                            'total_requests': random.randint(1000, 10000),
                            'successful_requests': random.randint(800, 9500),
                            'failed_requests': random.randint(50, 500),
                            'total_latency': random.uniform(1000, 10000),
                            'average_latency': random.uniform(50, 500),
                            'max_latency': random.uniform(1000, 5000),
                            'min_latency': random.uniform(10, 100),
                            'error_rate': random.uniform(0.1, 10.0),
                            'success_rate': random.uniform(90.0, 99.9),
                            'last_updated': datetime.now() - timedelta(minutes=random.randint(1, 60)),
                            'meta_data': json.dumps({'window_size_minutes': 60})
                        })
                    
                    results['circuit_breaker_metrics'] = insert_data_flexible(session, 'circuit_breaker_metrics', circuit_breaker_metrics_data)
                    print(f"    ✅ Created {results['circuit_breaker_metrics']} circuit breaker metrics")
            except Exception as e:
                print(f"    ❌ Error seeding circuit_breaker_metrics: {e}")
                results['circuit_breaker_metrics'] = 0
    except Exception as e:
        print(f"    ❌ Error seeding circuit_breakers: {e}")
        results['circuit_breakers'] = 0
    
    return results

def seed_dashboard_ui_enhancement(session: Session, deps: Dict[str, List[int]]) -> Dict[str, int]:
    """Seed dashboard and UI enhancement tables."""
    results = {}
    
    print("  Seeding core_dashboard_widgets...")
    try:
        core_dashboard_widgets_data = []
        for i in range(25):
            core_dashboard_widgets_data.append({
                'widget_type': random.choice(['metric', 'chart', 'table', 'list', 'card']),
                'name': f'Widget {i+1}',
                'configuration': json.dumps({
                    'title': f'Dashboard Widget {i+1}',
                    'data_source': random.choice(['activities', 'users', 'analytics', 'reports']),
                    'refresh_interval': random.randint(30, 300)
                }),
                'position': json.dumps({'x': random.randint(0, 10), 'y': random.randint(0, 10)}),
                'size': json.dumps({'width': random.randint(2, 4), 'height': random.randint(2, 4)}),
                'user_id': random.choice(deps['dashboard_user_ids']) if deps['dashboard_user_ids'] else random.choice(deps['user_ids']),
                'status': random.choice(WIDGET_STATUS_VALUES),
                'is_active': random.choice([True, False]),
                'metadata': json.dumps({'source': 'dashboard_builder', 'version': '1.0'})
            })
        
        results['core_dashboard_widgets'] = insert_data_flexible(session, 'core_dashboard_widgets', core_dashboard_widgets_data)
        print(f"    ✅ Created {results['core_dashboard_widgets']} core dashboard widgets")
    except Exception as e:
        print(f"    ❌ Error seeding core_dashboard_widgets: {e}")
        results['core_dashboard_widgets'] = 0
    
    print("  Seeding dashboard_api_keys...")
    try:
        dashboard_api_keys_data = []
        for i in range(15):
            dashboard_api_keys_data.append({
                'key_id': f'key_{i+1}_{random.randint(1000, 9999)}',
                'user_id': random.choice(deps['dashboard_user_ids']) if deps['dashboard_user_ids'] else random.choice(deps['user_ids']),
                'name': f'API Key {i+1}',
                'description': f'API key for dashboard access {i+1}',
                'hashed_secret': f'hashed_secret_{i+1}_{random.randint(10000, 99999)}',
                'permissions': json.dumps(['read', 'write', 'admin']),
                'expires_at': datetime.now() + timedelta(days=random.randint(30, 365)),
                'revoked_at': None,
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 7))
            })
        
        results['dashboard_api_keys'] = insert_data_flexible(session, 'dashboard_api_keys', dashboard_api_keys_data)
        print(f"    ✅ Created {results['dashboard_api_keys']} dashboard API keys")
    except Exception as e:
        print(f"    ❌ Error seeding dashboard_api_keys: {e}")
        results['dashboard_api_keys'] = 0
    
    print("  Seeding dashboard_audit_logs...")
    try:
        dashboard_audit_logs_data = []
        for i in range(100):
            dashboard_audit_logs_data.append({
                'user_id': random.choice(deps['dashboard_user_ids']) if deps['dashboard_user_ids'] else random.choice(deps['user_ids']),
                'action': random.choice(['CREATE', 'READ', 'UPDATE', 'DELETE', 'LOGIN', 'LOGOUT']),
                'resource_type': random.choice(['dashboard', 'widget', 'user', 'settings']),
                'resource_id': random.randint(1, 100),
                'ip_address': f'192.168.1.{random.randint(1, 254)}',
                'user_agent': f'Browser_{random.randint(1, 10)}',
                'details': json.dumps({'action_details': f'Audit log {i+1}'}),
                'created_at': datetime.now() - timedelta(hours=random.randint(1, 168))
            })
        
        results['dashboard_audit_logs'] = insert_data_flexible(session, 'dashboard_audit_logs', dashboard_audit_logs_data)
        print(f"    ✅ Created {results['dashboard_audit_logs']} dashboard audit logs")
    except Exception as e:
        print(f"    ❌ Error seeding dashboard_audit_logs: {e}")
        results['dashboard_audit_logs'] = 0
    
    print("  Seeding dashboard_filter_searches...")
    try:
        dashboard_filter_searches_data = []
        for i in range(20):
            dashboard_filter_searches_data.append({
                'query': f'search_query_{i+1}',  # Required NOT NULL field
                'filters': json.dumps({
                    'date_range': f'{random.randint(1, 30)} days',
                    'category': random.choice(['students', 'activities', 'reports', 'analytics']),
                    'status': random.choice(['active', 'pending', 'completed'])
                }),
                'results_count': random.randint(10, 1000),
                'user_id': random.choice(deps['dashboard_user_ids']) if deps['dashboard_user_ids'] else random.choice(deps['user_ids']),
                'status': random.choice(BASE_STATUS_VALUES),
                'is_active': random.choice([True, False]),
                'metadata': json.dumps({'source': 'search_engine', 'version': '1.0'})
            })
        
        results['dashboard_filter_searches'] = insert_data_flexible(session, 'dashboard_filter_searches', dashboard_filter_searches_data)
        print(f"    ✅ Created {results['dashboard_filter_searches']} dashboard filter searches")
    except Exception as e:
        print(f"    ❌ Error seeding dashboard_filter_searches: {e}")
        results['dashboard_filter_searches'] = 0
    
    print("  Seeding dashboard_ip_allowlist...")
    try:
        dashboard_ip_allowlist_data = []
        for i in range(20):
            dashboard_ip_allowlist_data.append({
                'ip_address': f'192.168.{random.randint(1, 255)}.{random.randint(1, 255)}',
                'description': f'Allowed IP {i+1}',
                'is_active': random.choice([True, False]),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 7))
            })
        
        results['dashboard_ip_allowlist'] = insert_data_flexible(session, 'dashboard_ip_allowlist', dashboard_ip_allowlist_data)
        print(f"    ✅ Created {results['dashboard_ip_allowlist']} dashboard IP allowlist entries")
    except Exception as e:
        print(f"    ❌ Error seeding dashboard_ip_allowlist: {e}")
        results['dashboard_ip_allowlist'] = 0
    
    print("  Seeding dashboard_ip_blocklist...")
    try:
        dashboard_ip_blocklist_data = []
        for i in range(10):
            dashboard_ip_blocklist_data.append({
                'ip_address': f'10.0.{random.randint(1, 255)}.{random.randint(1, 255)}',
                'reason': f'Blocked IP {i+1} - {random.choice(["suspicious", "abuse", "spam"])}',
                'is_active': random.choice([True, False]),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 7))
            })
        
        results['dashboard_ip_blocklist'] = insert_data_flexible(session, 'dashboard_ip_blocklist', dashboard_ip_blocklist_data)
        print(f"    ✅ Created {results['dashboard_ip_blocklist']} dashboard IP blocklist entries")
    except Exception as e:
        print(f"    ❌ Error seeding dashboard_ip_blocklist: {e}")
        results['dashboard_ip_blocklist'] = 0
    
    print("  Seeding dashboard_marketplace_listings...")
    try:
        dashboard_marketplace_listings_data = []
        for i in range(15):
            dashboard_marketplace_listings_data.append({
                'tool_id': random.choice(deps['ai_tool_ids']) if deps['ai_tool_ids'] else 1,  # Required NOT NULL field
                'title': f'Marketplace Item {i+1}',  # Required NOT NULL field
                'description': f'Description for marketplace item {i+1}',
                'features': json.dumps(['feature1', 'feature2', 'feature3']),
                'pricing_details': json.dumps({'price': random.randint(10, 100), 'currency': 'USD'}),
                'category': random.choice(['INTEGRATION', 'ANALYTICS', 'REPORTING', 'UTILITY']),
                'tags': json.dumps(['tag1', 'tag2', 'tag3']),
                'preview_url': f'https://example.com/preview/{i+1}',
                'documentation_url': f'https://example.com/docs/{i+1}',
                'is_featured': random.choice([True, False]),
                'is_public': random.choice([True, False]),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 7))
            })
        
        results['dashboard_marketplace_listings'] = insert_data_flexible(session, 'dashboard_marketplace_listings', dashboard_marketplace_listings_data)
        print(f"    ✅ Created {results['dashboard_marketplace_listings']} dashboard marketplace listings")
    except Exception as e:
        print(f"    ❌ Error seeding dashboard_marketplace_listings: {e}")
        results['dashboard_marketplace_listings'] = 0
    
    # This will be seeded after dashboard_notification_models is created
    results['dashboard_notification_channels'] = 0
    
    print("  Seeding dashboard_notification_models...")
    try:
        dashboard_notification_models_data = []
        for i in range(15):
            dashboard_notification_models_data.append({
                'user_id': random.choice(deps['dashboard_user_ids']) if deps['dashboard_user_ids'] else random.choice(deps['user_ids']),  # Required NOT NULL field
                'type': random.choice(NOTIFICATION_TYPES),  # Required NOT NULL field
                'title': f'Notification Title {i+1}',  # Required NOT NULL field
                'message': f'Notification message content {i+1}',  # Required NOT NULL field
                'data': json.dumps({'template': f'Template {i+1}', 'variables': ['var1', 'var2', 'var3']}),
                'priority': random.choice(NOTIFICATION_PRIORITIES),
                'status': random.choice(['PENDING', 'SENT', 'FAILED', 'DELIVERED']),
                'is_active': random.choice([True, False]),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'read_at': datetime.now() - timedelta(days=random.randint(1, 7)) if random.choice([True, False]) else None,
                'expires_at': datetime.now() + timedelta(days=random.randint(1, 30)),
                'metadata': json.dumps({'source': 'notification_builder', 'version': '1.0'})
            })
        
        results['dashboard_notification_models'] = insert_data_flexible(session, 'dashboard_notification_models', dashboard_notification_models_data)
        print(f"    ✅ Created {results['dashboard_notification_models']} dashboard notification models")
        
        # Now seed the dependent table
        print("  Seeding dashboard_notification_channels...")
        try:
            # Get actual dashboard_notification_models IDs that were created
            notification_result = session.execute(text("SELECT id FROM dashboard_notification_models ORDER BY id"))
            notification_ids = [row[0] for row in notification_result.fetchall()]
            
            if not notification_ids:
                print("    ⚠️  No dashboard_notification_models found, skipping dashboard_notification_channels")
                results['dashboard_notification_channels'] = 0
            else:
                dashboard_notification_channels_data = []
                for i in range(min(20, len(notification_ids) * 2)):  # Use actual notification IDs
                    dashboard_notification_channels_data.append({
                        'notification_id': random.choice(notification_ids),  # Use actual notification IDs
                        'channel': random.choice(['EMAIL', 'SMS', 'PUSH', 'WEBSOCKET', 'IN_APP']),  # Required NOT NULL field
                        'status': random.choice(['PENDING', 'SENT', 'FAILED', 'DELIVERED']),
                        'sent_at': datetime.now() - timedelta(hours=random.randint(1, 24)) if random.choice([True, False]) else None,
                        'error': f'Error message {i+1}' if random.choice([True, False]) else None,
                        'retry_count': random.randint(0, 3),
                        'last_retry': datetime.now() - timedelta(hours=random.randint(1, 12)) if random.choice([True, False]) else None,
                        'is_active': random.choice([True, False]),
                        'metadata': json.dumps({'source': 'notification_service', 'version': '1.0'})
                    })
                
                results['dashboard_notification_channels'] = insert_data_flexible(session, 'dashboard_notification_channels', dashboard_notification_channels_data)
                print(f"    ✅ Created {results['dashboard_notification_channels']} dashboard notification channels")
        except Exception as e:
            print(f"    ❌ Error seeding dashboard_notification_channels: {e}")
            results['dashboard_notification_channels'] = 0
    except Exception as e:
        print(f"    ❌ Error seeding dashboard_notification_models: {e}")
        results['dashboard_notification_models'] = 0
    
    print("  Seeding dashboard_rate_limits...")
    try:
        # Get actual dashboard_api_keys IDs that were created
        api_key_result = session.execute(text("SELECT id FROM dashboard_api_keys ORDER BY id"))
        api_key_ids = [row[0] for row in api_key_result.fetchall()]
        
        if not api_key_ids:
            print("    ⚠️  No dashboard_api_keys found, skipping dashboard_rate_limits")
            results['dashboard_rate_limits'] = 0
        else:
            dashboard_rate_limits_data = []
            for i in range(min(12, len(api_key_ids) * 2)):  # Limit to available API keys
                dashboard_rate_limits_data.append({
                    'endpoint': f'/api/v1/{random.choice(["users", "activities", "reports", "analytics"])}',
                    'requests_per_minute': random.randint(10, 100),  # Required NOT NULL field
                    'burst_size': random.randint(5, 50),
                    'user_id': random.choice(deps['dashboard_user_ids']) if deps['dashboard_user_ids'] else random.choice(deps['user_ids']),
                    'api_key_id': random.choice(api_key_ids),  # Use actual API key IDs
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                    'updated_at': datetime.now() - timedelta(days=random.randint(1, 7))
                })
            
            results['dashboard_rate_limits'] = insert_data_flexible(session, 'dashboard_rate_limits', dashboard_rate_limits_data)
            print(f"    ✅ Created {results['dashboard_rate_limits']} dashboard rate limits")
    except Exception as e:
        print(f"    ❌ Error seeding dashboard_rate_limits: {e}")
        results['dashboard_rate_limits'] = 0
    
    print("  Seeding dashboard_security_policies...")
    try:
        dashboard_security_policies_data = []
        for i in range(10):
            dashboard_security_policies_data.append({
                'name': f'Security Policy {i+1}',  # Required NOT NULL field
                'policy_type': random.choice(['AUTHENTICATION', 'AUTHORIZATION', 'DATA_PROTECTION', 'ACCESS_CONTROL']),
                'rules': json.dumps({
                    'min_password_length': random.randint(8, 16),
                    'require_2fa': random.choice([True, False]),
                    'session_timeout': random.randint(30, 300)
                }),
                'description': f'Description for security policy {i+1}',
                'enabled': random.choice([True, False]),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 7))
            })
        
        results['dashboard_security_policies'] = insert_data_flexible(session, 'dashboard_security_policies', dashboard_security_policies_data)
        print(f"    ✅ Created {results['dashboard_security_policies']} dashboard security policies")
    except Exception as e:
        print(f"    ❌ Error seeding dashboard_security_policies: {e}")
        results['dashboard_security_policies'] = 0
    
    print("  Seeding dashboard_sessions...")
    try:
        dashboard_sessions_data = []
        for i in range(50):
            dashboard_sessions_data.append({
                'user_id': random.choice(deps['dashboard_user_ids']) if deps['dashboard_user_ids'] else random.choice(deps['user_ids']),
                'session_token': f'session_token_{i+1}_{random.randint(10000, 99999)}',
                'ip_address': f'192.168.1.{random.randint(1, 254)}',
                'user_agent': f'Browser_{random.randint(1, 10)}',
                'is_active': random.choice([True, False]),
                'expires_at': datetime.now() + timedelta(hours=random.randint(1, 24)),
                'created_at': datetime.now() - timedelta(hours=random.randint(1, 48)),
                'updated_at': datetime.now() - timedelta(hours=random.randint(1, 24))
            })
        
        results['dashboard_sessions'] = insert_data_flexible(session, 'dashboard_sessions', dashboard_sessions_data)
        print(f"    ✅ Created {results['dashboard_sessions']} dashboard sessions")
    except Exception as e:
        print(f"    ❌ Error seeding dashboard_sessions: {e}")
        results['dashboard_sessions'] = 0
    
    print("  Seeding dashboard_share_configs...")
    try:
        dashboard_share_configs_data = []
        for i in range(15):
            dashboard_share_configs_data.append({
                'share_type': random.choice(['PUBLIC', 'PRIVATE', 'RESTRICTED']),
                'permissions': json.dumps(['read', 'write', 'admin']),
                'expires_at': datetime.now() + timedelta(days=random.randint(1, 365)),
                'status': random.choice(BASE_STATUS_VALUES),  # Required NOT NULL field
                'is_active': random.choice([True, False]),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 7)),
                'metadata': json.dumps({'source': 'share_manager', 'version': '1.0'})
            })
        
        results['dashboard_share_configs'] = insert_data_flexible(session, 'dashboard_share_configs', dashboard_share_configs_data)
        print(f"    ✅ Created {results['dashboard_share_configs']} dashboard share configs")
    except Exception as e:
        print(f"    ❌ Error seeding dashboard_share_configs: {e}")
        results['dashboard_share_configs'] = 0
    
    print("  Seeding dashboard_share_exports...")
    try:
        dashboard_share_exports_data = []
        for i in range(20):
            dashboard_share_exports_data.append({
                'format': random.choice(['PDF', 'CSV', 'JSON', 'EXCEL']),  # Required NOT NULL field
                'status': random.choice(EXPORT_STATUS_VALUES),
                'configuration': json.dumps({'export_type': 'dashboard', 'include_data': True, 'format_options': {}}),  # Required NOT NULL field
                'file_path': f'/exports/export_{i+1}.{random.choice(["pdf", "csv", "json", "xlsx"])}',
                'file_size': random.randint(1024, 10485760),
                'download_count': random.randint(0, 100),
                'expires_at': datetime.now() + timedelta(days=random.randint(1, 30)),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 7))
            })
        
        results['dashboard_share_exports'] = insert_data_flexible(session, 'dashboard_share_exports', dashboard_share_exports_data)
        print(f"    ✅ Created {results['dashboard_share_exports']} dashboard share exports")
    except Exception as e:
        print(f"    ❌ Error seeding dashboard_share_exports: {e}")
        results['dashboard_share_exports'] = 0
    
    print("  Seeding dashboard_shared_contexts...")
    try:
        # Get actual dashboard_gpt_contexts IDs that exist
        context_result = session.execute(text("SELECT id FROM dashboard_gpt_contexts ORDER BY id"))
        context_ids = [row[0] for row in context_result.fetchall()]
        
        if not context_ids:
            print("    ⚠️  No dashboard_gpt_contexts found, skipping dashboard_shared_contexts")
            results['dashboard_shared_contexts'] = 0
        else:
            dashboard_shared_contexts_data = []
            for i in range(min(25, len(context_ids) * 3)):  # Limit to available contexts
                dashboard_shared_contexts_data.append({
                    'context_id': random.choice(context_ids),  # Use actual context IDs
                    'source_gpt_id': random.randint(1, 10),  # Required NOT NULL field
                    'target_gpt_id': random.randint(1, 10),  # Required NOT NULL field
                    'shared_data': json.dumps({'context_type': 'DASHBOARD', 'permissions': ['read', 'write', 'admin'], 'is_public': random.choice([True, False])}),  # Required NOT NULL field
                    'meta_data': json.dumps({'source': 'context_manager', 'version': '1.0'}),
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
                })
            
            results['dashboard_shared_contexts'] = insert_data_flexible(session, 'dashboard_shared_contexts', dashboard_shared_contexts_data)
            print(f"    ✅ Created {results['dashboard_shared_contexts']} dashboard shared contexts")
    except Exception as e:
        print(f"    ❌ Error seeding dashboard_shared_contexts: {e}")
        results['dashboard_shared_contexts'] = 0
    
    print("  Seeding dashboard_team_members...")
    try:
        # Get existing team-user combinations to avoid duplicates
        existing_result = session.execute(text("SELECT team_id, user_id FROM dashboard_team_members"))
        existing_combinations = set((row[0], row[1]) for row in existing_result.fetchall())
        
        dashboard_team_members_data = []
        # Create unique combinations to avoid duplicate key violations
        team_user_combinations = set()
        for i in range(30):
            team_id = random.choice(deps['dashboard_team_ids']) if deps['dashboard_team_ids'] else random.randint(1, 3)
            user_id = random.choice(deps['dashboard_user_ids']) if deps['dashboard_user_ids'] else random.randint(1, 32)
            
            # Ensure unique combination (not in existing or already generated)
            attempts = 0
            while (team_id, user_id) in existing_combinations or (team_id, user_id) in team_user_combinations:
                team_id = random.choice(deps['dashboard_team_ids']) if deps['dashboard_team_ids'] else random.randint(1, 3)
                user_id = random.choice(deps['dashboard_user_ids']) if deps['dashboard_user_ids'] else random.randint(1, 32)
                attempts += 1
                if attempts > 100:  # Prevent infinite loop
                    break
            
            if attempts <= 100:  # Only add if we found a unique combination
                team_user_combinations.add((team_id, user_id))
                
                dashboard_team_members_data.append({
                    'team_id': team_id,
                    'user_id': user_id,
                    'role': random.choice(['OWNER', 'ADMIN', 'MEMBER', 'VIEWER']),
                    'joined_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                    'is_active': random.choice([True, False]),
                    'permissions': json.dumps(['read', 'write', 'admin']),
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                    'updated_at': datetime.now() - timedelta(days=random.randint(1, 30))
                })
        
        results['dashboard_team_members'] = insert_data_flexible(session, 'dashboard_team_members', dashboard_team_members_data)
        print(f"    ✅ Created {results['dashboard_team_members']} dashboard team members")
    except Exception as e:
        print(f"    ❌ Error seeding dashboard_team_members: {e}")
        results['dashboard_team_members'] = 0
    
    print("  Seeding dashboard_tool_usage_logs...")
    try:
        dashboard_tool_usage_logs_data = []
        for i in range(100):
            dashboard_tool_usage_logs_data.append({
                'user_id': random.choice(deps['dashboard_user_ids']) if deps['dashboard_user_ids'] else random.choice(deps['user_ids']),
                'tool_id': random.choice(deps['ai_tool_ids']) if deps['ai_tool_ids'] else 1,  # Use existing tool IDs
                'action': random.choice(['CREATE', 'READ', 'UPDATE', 'DELETE', 'EXPORT', 'IMPORT']),
                'timestamp': datetime.now() - timedelta(hours=random.randint(1, 168)),
                'duration_ms': random.randint(100, 5000),
                'success': random.choice([True, False]),
                'error_message': f'Error message {i+1}' if random.choice([True, False]) else None,
                'metadata': json.dumps({'source': 'tool_usage_tracker', 'version': '1.0'})
            })
        
        results['dashboard_tool_usage_logs'] = insert_data_flexible(session, 'dashboard_tool_usage_logs', dashboard_tool_usage_logs_data)
        print(f"    ✅ Created {results['dashboard_tool_usage_logs']} dashboard tool usage logs")
    except Exception as e:
        print(f"    ❌ Error seeding dashboard_tool_usage_logs: {e}")
        results['dashboard_tool_usage_logs'] = 0
    
    return results

def seed_competition_events_system(session: Session, deps: Dict[str, List[int]]) -> Dict[str, int]:
    """Seed Competition & Events System (4 tables)."""
    results = {}
    
    print("  Seeding competitions...")
    try:
        competitions_data = []
        for i in range(15):
            competitions_data.append({
                'name': f'Competition {i+1}',
                'description': f'Description for competition {i+1}',
                'competition_type': random.choice(['INDIVIDUAL', 'TEAM', 'MIXED']),
                'sport_type': random.choice(['BASKETBALL', 'SOCCER', 'TRACK', 'SWIMMING', 'TENNIS', 'VOLLEYBALL']),  # Required NOT NULL field
                'location': f'Location {i+1}',  # Required NOT NULL field
                'organizer': f'Organizer {i+1}',  # Required NOT NULL field
                'status': random.choice(['SCHEDULED', 'ACTIVE', 'COMPLETED', 'CANCELLED']),  # Required NOT NULL field
                'start_date': datetime.now() + timedelta(days=random.randint(1, 60)),
                'end_date': datetime.now() + timedelta(days=random.randint(61, 120)),
                'max_teams': random.randint(4, 32),
                'max_team_size': random.randint(2, 8),
                'registration_fee': round(random.uniform(0.0, 100.0), 2),
                'prize_pool': round(random.uniform(100.0, 5000.0), 2),
                'is_active': random.choice([True, False]),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 7))
            })
        
        results['competitions'] = insert_data_flexible(session, 'competitions', competitions_data)
        print(f"    ✅ Created {results['competitions']} competitions")
    except Exception as e:
        print(f"    ❌ Error seeding competitions: {e}")
        results['competitions'] = 0
    
    print("  Seeding competition_base_events...")
    try:
        # Get actual competition IDs
        competition_result = session.execute(text("SELECT id FROM competitions LIMIT 15"))
        competition_ids = [row[0] for row in competition_result.fetchall()]
        
        if not competition_ids:
            print("    ⚠️  No competitions found, skipping competition_base_events")
            results['competition_base_events'] = 0
        else:
            competition_base_events_data = []
            for i in range(20):
                competition_base_events_data.append({
                    'competition_id': random.choice(competition_ids),  # Use actual competition IDs
                'event_type': random.choice(['SPORTS', 'ACADEMIC', 'ARTS', 'STEM', 'FITNESS']),
                'start_time': datetime.now() + timedelta(days=random.randint(1, 90)),
                'end_time': datetime.now() + timedelta(days=random.randint(91, 180)),
                'location': f'Location {i+1}',
                'description': f'Description for competition event {i+1}',
                'rules': json.dumps({'max_attempts': 3, 'time_limit': 60}),
                'scoring_criteria': json.dumps({'points': 100, 'bonus': 10}),
                'max_participants': random.randint(10, 100),
                'equipment_needed': json.dumps(['equipment1', 'equipment2']),
                'staff_needed': json.dumps(['referee', 'judge']),
                'venue_setup': json.dumps({'setup': 'standard'}),
                'results': None,
                'rankings': None,
                'notes': f'Event notes {i+1}',
                'name': f'Competition Event {i+1}',
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 7)),
                'last_accessed_at': datetime.now() - timedelta(hours=random.randint(1, 24)),
                'archived_at': None,
                'deleted_at': None,
                'scheduled_deletion_at': None,
                'retention_period': random.randint(30, 365),
                'status': random.choice(BASE_STATUS_VALUES),  # Use correct enum values
                'is_active': random.choice([True, False]),
                'metadata': json.dumps({'source': 'competition_manager', 'version': '1.0'})
            })
            
            results['competition_base_events'] = insert_data_flexible(session, 'competition_base_events', competition_base_events_data)
            print(f"    ✅ Created {results['competition_base_events']} competition base events")
    except Exception as e:
        print(f"    ❌ Error seeding competition_base_events: {e}")
        results['competition_base_events'] = 0
    
    print("  Seeding competition_base_participants...")
    try:
        # Get actual competition IDs
        competition_result = session.execute(text("SELECT id FROM competitions LIMIT 15"))
        competition_ids = [row[0] for row in competition_result.fetchall()]
        
        if not competition_ids:
            print("    ⚠️  No competitions found, skipping competition_base_participants")
            results['competition_base_participants'] = 0
        else:
            competition_base_participants_data = []
            for i in range(100):
                competition_base_participants_data.append({
                    'competition_id': random.choice(competition_ids),  # Use actual competition IDs
                'student_id': random.choice(deps['student_ids']) if deps['student_ids'] else random.randint(1, 100),
                'event_id': random.randint(1, 20),  # Assuming 20 events from above
                'registration_date': datetime.now() - timedelta(days=random.randint(1, 30)),
                'status': random.choice(BASE_STATUS_VALUES),
                'team_name': f'Team {i+1}' if random.random() < 0.3 else None,
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 7))
            })
            
            results['competition_base_participants'] = insert_data_flexible(session, 'competition_base_participants', competition_base_participants_data)
            print(f"    ✅ Created {results['competition_base_participants']} competition base participants")
    except Exception as e:
        print(f"    ❌ Error seeding competition_base_participants: {e}")
        results['competition_base_participants'] = 0
    
    print("  Seeding competition_base_event_participants...")
    try:
        # Get actual event and participant IDs
        event_result = session.execute(text("SELECT id FROM competition_base_events LIMIT 20"))
        event_ids = [row[0] for row in event_result.fetchall()]
        
        participant_result = session.execute(text("SELECT id FROM competition_base_participants "))
        participant_ids = [row[0] for row in participant_result.fetchall()]
        
        if not event_ids or not participant_ids:
            print("    ⚠️  No events or participants found, skipping competition_base_event_participants")
            results['competition_base_event_participants'] = 0
        else:
            competition_base_event_participants_data = []
            for i in range(80):
                competition_base_event_participants_data.append({
                    'event_id': random.choice(event_ids),  # Use actual event IDs
                    'participant_id': random.choice(participant_ids),  # Use actual participant IDs
                    'score': round(random.uniform(0.0, 100.0), 2) if random.random() < 0.7 else None,
                    'rank': random.randint(1, 50) if random.random() < 0.5 else None,
                    'participation_date': datetime.now() - timedelta(days=random.randint(1, 30)),
                    'notes': f'Participation notes {i+1}' if random.random() < 0.3 else None,
                    'status': random.choice(BASE_STATUS_VALUES),  # Required NOT NULL field
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),  # Required NOT NULL field
                    'updated_at': datetime.now() - timedelta(days=random.randint(1, 7))  # Required NOT NULL field
                })
            
            results['competition_base_event_participants'] = insert_data_flexible(session, 'competition_base_event_participants', competition_base_event_participants_data)
            print(f"    ✅ Created {results['competition_base_event_participants']} competition base event participants")
    except Exception as e:
        print(f"    ❌ Error seeding competition_base_event_participants: {e}")
        results['competition_base_event_participants'] = 0
    
    return results

def seed_project_management_system(session: Session, deps: Dict[str, List[int]]) -> Dict[str, int]:
    """Seed Project Management System (13 tables)."""
    results = {}
    
    print("  Seeding feedback_projects...")
    try:
        feedback_projects_data = []
        for i in range(25):
            feedback_projects_data.append({
                'name': f'Feedback Project {i+1}',
                'description': f'Description for feedback project {i+1}',
                'project_type': random.choice(['PERSONAL', 'TEAM', 'ORGANIZATION', 'TEMPLATE', 'RESEARCH', 'DEVELOPMENT', 'PRODUCTION']),  # Required NOT NULL field
                'status': random.choice(PROJECT_STATUS_ENUM),
                'priority': random.choice(['LOW', 'MEDIUM', 'HIGH', 'URGENT']),
                'owner_id': random.choice(deps['user_ids']) if deps['user_ids'] else random.randint(1, 32),  # Required NOT NULL field
                'start_date': datetime.now() - timedelta(days=random.randint(1, 30)),
                'end_date': datetime.now() + timedelta(days=random.randint(1, 90)),
                'created_by': random.choice(deps['user_ids']) if deps['user_ids'] else random.randint(1, 32),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 7))
            })
        
        results['feedback_projects'] = insert_data_flexible(session, 'feedback_projects', feedback_projects_data)
        print(f"    ✅ Created {results['feedback_projects']} feedback projects")
    except Exception as e:
        print(f"    ❌ Error seeding feedback_projects: {e}")
        results['feedback_projects'] = 0
    
    print("  Seeding project_comments...")
    try:
        # Get actual organization project IDs (project_comments references organization_projects)
        project_result = session.execute(text("SELECT id FROM organization_projects LIMIT 25"))
        project_ids = [row[0] for row in project_result.fetchall()]
        
        if not project_ids:
            print("    ⚠️  No organization projects found, skipping project_comments")
            results['project_comments'] = 0
        else:
            project_comments_data = []
            for i in range(150):
                project_comments_data.append({
                    'project_id': random.choice(project_ids),  # Use actual organization project IDs
                    'user_id': random.choice(deps['user_ids']) if deps['user_ids'] else random.randint(1, 32),
                    'content': f'Project comment {i+1}',
                    'is_internal': random.choice([True, False]),
                    'status': random.choice(BASE_STATUS_VALUES),  # Required NOT NULL field
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                    'updated_at': datetime.now() - timedelta(days=random.randint(1, 7))
                })
            
            results['project_comments'] = insert_data_flexible(session, 'project_comments', project_comments_data)
            print(f"    ✅ Created {results['project_comments']} project comments")
    except Exception as e:
        print(f"    ❌ Error seeding project_comments: {e}")
        results['project_comments'] = 0
    
    print("  Seeding project_feedback...")
    try:
        # Get actual feedback project IDs
        project_result = session.execute(text("SELECT id FROM feedback_projects LIMIT 25"))
        project_ids = [row[0] for row in project_result.fetchall()]
        
        if not project_ids:
            print("    ⚠️  No feedback projects found, skipping project_feedback")
            results['project_feedback'] = 0
        else:
            project_feedback_data = []
            for i in range(100):
                project_feedback_data.append({
                    'project_id': random.choice(project_ids),  # Use actual organization project IDs
                'user_id': random.choice(deps['user_ids']) if deps['user_ids'] else random.randint(1, 32),
                'title': f'Feedback Title {i+1}',  # Required NOT NULL field
                'content': f'Project feedback content {i+1}',  # Required NOT NULL field
                'rating': random.randint(1, 5),
                'feedback_text': f'Project feedback {i+1}',
                'feedback_type': random.choice(FEEDBACK_TYPES),
                'is_public': random.choice([True, False]),
                'status': random.choice(['OPEN', 'IN_PROGRESS', 'RESOLVED', 'CLOSED']),  # Required NOT NULL field
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
            })
            
            results['project_feedback'] = insert_data_flexible(session, 'project_feedback', project_feedback_data)
            print(f"    ✅ Created {results['project_feedback']} project feedback records")
    except Exception as e:
        print(f"    ❌ Error seeding project_feedback: {e}")
        results['project_feedback'] = 0
    
    print("  Seeding project_members...")
    try:
        # Get actual organization project IDs (not feedback_projects)
        project_result = session.execute(text("SELECT id FROM organization_projects LIMIT 25"))
        project_ids = [row[0] for row in project_result.fetchall()]
        
        if not project_ids:
            print("    ⚠️  No organization projects found, skipping project_members")
            results['project_members'] = 0
        else:
            project_members_data = []
            for i in range(80):
                project_members_data.append({
                    'project_id': random.choice(project_ids),  # Use actual organization project IDs
                    'user_id': random.choice(deps['user_ids']) if deps['user_ids'] else random.randint(1, 32),
                    'role': random.choice(['MEMBER', 'ADMIN', 'OWNER', 'VIEWER']),
                    'joined_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                    'is_active': random.choice([True, False]),
                    'status': random.choice(BASE_STATUS_VALUES),  # Required NOT NULL field
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),  # Required NOT NULL field
                    'updated_at': datetime.now() - timedelta(days=random.randint(1, 7))  # Required NOT NULL field
                })
            
            results['project_members'] = insert_data_flexible(session, 'project_members', project_members_data)
            print(f"    ✅ Created {results['project_members']} project members")
    except Exception as e:
        print(f"    ❌ Error seeding project_members: {e}")
        results['project_members'] = 0
    
    print("  Seeding project_resources...")
    try:
        # Get actual organization project IDs (not feedback_projects)
        project_result = session.execute(text("SELECT id FROM organization_projects LIMIT 25"))
        project_ids = [row[0] for row in project_result.fetchall()]
        
        if not project_ids:
            print("    ⚠️  No organization projects found, skipping project_resources")
            results['project_resources'] = 0
        else:
            project_resources_data = []
            for i in range(60):
                project_resources_data.append({
                    'project_id': random.choice(project_ids),  # Use actual organization project IDs
                'name': f'Resource {i+1}',  # Required NOT NULL field
                'type': random.choice(['DOCUMENT', 'IMAGE', 'VIDEO', 'AUDIO', 'CODE', 'OTHER']),  # Required NOT NULL field
                'url': f'https://example.com/resource/{i+1}',
                'file_size': random.randint(1024, 10485760),
                'uploaded_by': random.choice(deps['user_ids']) if deps['user_ids'] else random.randint(1, 32),
                'status': random.choice(BASE_STATUS_VALUES),  # Required NOT NULL field
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 7))  # Required NOT NULL field
            })
            
            results['project_resources'] = insert_data_flexible(session, 'project_resources', project_resources_data)
            print(f"    ✅ Created {results['project_resources']} project resources")
    except Exception as e:
        print(f"    ❌ Error seeding project_resources: {e}")
        results['project_resources'] = 0
    
    print("  Seeding project_tasks...")
    try:
        # Get actual organization project IDs (not feedback_projects)
        project_result = session.execute(text("SELECT id FROM organization_projects LIMIT 25"))
        project_ids = [row[0] for row in project_result.fetchall()]
        
        if not project_ids:
            print("    ⚠️  No organization projects found, skipping project_tasks")
            results['project_tasks'] = 0
        else:
            project_tasks_data = []
            for i in range(200):
                project_tasks_data.append({
                    'project_id': random.choice(project_ids),  # Use actual organization project IDs
                'name': f'Task {i+1}',  # Required NOT NULL field
                'description': f'Description for task {i+1}',
                'status': random.choice(BASE_STATUS_VALUES),
                'priority': random.choice(['LOW', 'MEDIUM', 'HIGH', 'URGENT']),
                'assigned_to': random.choice(deps['user_ids']) if deps['user_ids'] else random.randint(1, 32),
                'due_date': datetime.now() + timedelta(days=random.randint(1, 30)),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 7))
            })
            
            results['project_tasks'] = insert_data_flexible(session, 'project_tasks', project_tasks_data)
            print(f"    ✅ Created {results['project_tasks']} project tasks")
    except Exception as e:
        print(f"    ❌ Error seeding project_tasks: {e}")
        results['project_tasks'] = 0
    
    print("  Seeding project_milestones...")
    try:
        # Get actual feedback project IDs (project_milestones references feedback_projects)
        project_result = session.execute(text("SELECT id FROM feedback_projects LIMIT 25"))
        project_ids = [row[0] for row in project_result.fetchall()]
        
        if not project_ids:
            print("    ⚠️  No feedback projects found, skipping project_milestones")
            results['project_milestones'] = 0
        else:
            project_milestones_data = []
            for i in range(50):
                project_milestones_data.append({
                    'project_id': random.choice(project_ids),  # Use actual feedback project IDs
                'title': f'Milestone {i+1}',  # Required NOT NULL field
                'description': f'Description for milestone {i+1}',
                'due_date': datetime.now() + timedelta(days=random.randint(1, 60)),
                'status': random.choice(BASE_STATUS_VALUES),  # Use correct enum values
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 7))
            })
            
            results['project_milestones'] = insert_data_flexible(session, 'project_milestones', project_milestones_data)
            print(f"    ✅ Created {results['project_milestones']} project milestones")
    except Exception as e:
        print(f"    ❌ Error seeding project_milestones: {e}")
        results['project_milestones'] = 0
    
    print("  Seeding feedback_categories...")
    try:
        feedback_categories_data = []
        for i in range(10):
            feedback_categories_data.append({
                'name': f'Category {i+1}',
                'description': f'Description for feedback category {i+1}',
                'is_active': random.choice([True, False]),
                'status': random.choice(BASE_STATUS_VALUES),  # Required NOT NULL field
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
            })
        
        results['feedback_categories'] = insert_data_flexible(session, 'feedback_categories', feedback_categories_data)
        print(f"    ✅ Created {results['feedback_categories']} feedback categories")
    except Exception as e:
        print(f"    ❌ Error seeding feedback_categories: {e}")
        results['feedback_categories'] = 0
    
    print("  Seeding feedback_comments...")
    try:
        # Get actual organization_feedback IDs
        feedback_result = session.execute(text("SELECT id FROM organization_feedback LIMIT 20"))
        feedback_ids = [row[0] for row in feedback_result.fetchall()]
        
        if not feedback_ids:
            print("    ⚠️  No organization_feedback found, skipping feedback_comments")
            results['feedback_comments'] = 0
        else:
            feedback_comments_data = []
            for i in range(120):
                feedback_comments_data.append({
                    'feedback_id': random.choice(feedback_ids),  # Use actual organization_feedback IDs
                    'user_id': random.choice(deps['user_ids']) if deps['user_ids'] else random.randint(1, 32),
                    'content': f'Feedback comment {i+1}',
                    'is_internal': random.choice([True, False]),
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
                })
            
            results['feedback_comments'] = insert_data_flexible(session, 'feedback_comments', feedback_comments_data)
            print(f"    ✅ Created {results['feedback_comments']} feedback comments")
    except Exception as e:
        print(f"    ❌ Error seeding feedback_comments: {e}")
        results['feedback_comments'] = 0
    
    print("  Seeding feedback_attachments...")
    try:
        # Get actual organization_feedback IDs
        feedback_result = session.execute(text("SELECT id FROM organization_feedback LIMIT 20"))
        feedback_ids = [row[0] for row in feedback_result.fetchall()]
        
        if not feedback_ids:
            print("    ⚠️  No organization_feedback found, skipping feedback_attachments")
            results['feedback_attachments'] = 0
        else:
            feedback_attachments_data = []
            for i in range(80):
                feedback_attachments_data.append({
                    'feedback_id': random.choice(feedback_ids),  # Use actual organization_feedback IDs
                    'file_name': f'attachment_{i+1}.pdf',
                    'file_url': f'https://example.com/attachments/attachment_{i+1}.pdf',  # Required NOT NULL field
                    'file_size': random.randint(1024, 10485760),
                    'file_type': random.choice(['PDF', 'DOC', 'IMAGE', 'VIDEO', 'OTHER']),  # Required NOT NULL field
                    'uploaded_by': random.choice(deps['user_ids']) if deps['user_ids'] else random.randint(1, 32),
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
                })
            
            results['feedback_attachments'] = insert_data_flexible(session, 'feedback_attachments', feedback_attachments_data)
            print(f"    ✅ Created {results['feedback_attachments']} feedback attachments")
    except Exception as e:
        print(f"    ❌ Error seeding feedback_attachments: {e}")
        results['feedback_attachments'] = 0
    
    print("  Seeding feedback_responses...")
    try:
        # Get actual organization_feedback IDs
        feedback_result = session.execute(text("SELECT id FROM organization_feedback LIMIT 20"))
        feedback_ids = [row[0] for row in feedback_result.fetchall()]
        
        if not feedback_ids:
            print("    ⚠️  No organization_feedback found, skipping feedback_responses")
            results['feedback_responses'] = 0
        else:
            feedback_responses_data = []
            for i in range(90):
                feedback_responses_data.append({
                    'feedback_id': random.choice(feedback_ids),  # Use actual organization_feedback IDs
                    'user_id': random.choice(deps['user_ids']) if deps['user_ids'] else random.randint(1, 32),  # Required NOT NULL field
                    'content': f'Response to feedback {i+1}',  # Required NOT NULL field
                    'status': random.choice(BASE_STATUS_VALUES),  # Required NOT NULL field
                    'responded_by': random.choice(deps['user_ids']) if deps['user_ids'] else random.randint(1, 32),
                    'response_text': f'Response to feedback {i+1}',
                    'is_public': random.choice([True, False]),
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
                })
            
            results['feedback_responses'] = insert_data_flexible(session, 'feedback_responses', feedback_responses_data)
            print(f"    ✅ Created {results['feedback_responses']} feedback responses")
    except Exception as e:
        print(f"    ❌ Error seeding feedback_responses: {e}")
        results['feedback_responses'] = 0
    
    print("  Seeding feedback_actions...")
    try:
        # Get actual organization_feedback IDs
        feedback_result = session.execute(text("SELECT id FROM organization_feedback LIMIT 20"))
        feedback_ids = [row[0] for row in feedback_result.fetchall()]
        
        if not feedback_ids:
            print("    ⚠️  No organization_feedback found, skipping feedback_actions")
            results['feedback_actions'] = 0
        else:
            feedback_actions_data = []
            for i in range(70):
                feedback_actions_data.append({
                    'feedback_id': random.choice(feedback_ids),  # Use actual organization_feedback IDs
                    'user_id': random.choice(deps['user_ids']) if deps['user_ids'] else random.randint(1, 32),  # Required NOT NULL field
                    'action_type': random.choice(['ACKNOWLEDGED', 'INVESTIGATING', 'FIXED', 'WONT_FIX', 'DUPLICATE']),
                    'status': random.choice(BASE_STATUS_VALUES),  # Required NOT NULL field
                    'action_description': f'Action taken for feedback {i+1}',
                    'taken_by': random.choice(deps['user_ids']) if deps['user_ids'] else random.randint(1, 32),
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
                })
            
            results['feedback_actions'] = insert_data_flexible(session, 'feedback_actions', feedback_actions_data)
            print(f"    ✅ Created {results['feedback_actions']} feedback actions")
    except Exception as e:
        print(f"    ❌ Error seeding feedback_actions: {e}")
        results['feedback_actions'] = 0
    
    return results

def seed_resource_management_system(session: Session, deps: Dict[str, List[int]]) -> Dict[str, int]:
    """Seed Resource Management System (9 tables)."""
    results = {}
    
    print("  Seeding resource_management_usage...")
    try:
        resource_management_usage_data = []
        for i in range(100):
            resource_management_usage_data.append({
                'resource_id': random.randint(1, 100),  # Required NOT NULL field
                'resource_type': random.choice(['CPU', 'MEMORY', 'STORAGE', 'NETWORK', 'DATABASE']),  # Required NOT NULL field
                'metric_type': random.choice(['USAGE', 'THROUGHPUT', 'LATENCY', 'ERROR_RATE', 'COST', 'EFFICIENCY']),  # Required NOT NULL field
                'value': round(random.uniform(0.0, 100.0), 2),  # Required NOT NULL field
                'unit': random.choice(['PERCENT', 'BYTES', 'SECONDS', 'REQUESTS', 'COUNT']),  # Required NOT NULL field
                'timestamp': datetime.now() - timedelta(hours=random.randint(1, 24)),  # Required NOT NULL field
                'usage_percentage': round(random.uniform(0.0, 100.0), 2),
                'threshold_percentage': round(random.uniform(70.0, 95.0), 2),
                'is_alert_triggered': random.choice([True, False]),
                'recorded_at': datetime.now() - timedelta(hours=random.randint(1, 24)),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
            })
        
        results['resource_management_usage'] = insert_data_flexible(session, 'resource_management_usage', resource_management_usage_data)
        print(f"    ✅ Created {results['resource_management_usage']} resource management usage records")
    except Exception as e:
        print(f"    ❌ Error seeding resource_management_usage: {e}")
        results['resource_management_usage'] = 0
    
    print("  Seeding resource_thresholds...")
    try:
        resource_thresholds_data = []
        for i in range(20):
            resource_thresholds_data.append({
                'resource_type': random.choice(['CPU', 'MEMORY', 'STORAGE', 'NETWORK', 'DATABASE']),  # Required NOT NULL field
                'metric_type': random.choice(['USAGE', 'THROUGHPUT', 'LATENCY', 'ERROR_RATE', 'COST', 'EFFICIENCY']),  # Required NOT NULL field
                'threshold_value': round(random.uniform(0.5, 0.95), 2),  # Required NOT NULL field
                'threshold_type': random.choice(['WARNING', 'CRITICAL', 'INFO']),  # Required NOT NULL field
                'action': random.choice(['ALERT', 'SCALE_UP', 'SCALE_DOWN', 'RESTART', 'NOTIFY']),  # Required NOT NULL field
                'status': random.choice(BASE_STATUS_VALUES),  # Required NOT NULL field
                'warning_threshold': round(random.uniform(60.0, 80.0), 2),
                'critical_threshold': round(random.uniform(80.0, 95.0), 2),
                'is_active': random.choice([True, False]),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 7))
            })
        
        results['resource_thresholds'] = insert_data_flexible(session, 'resource_thresholds', resource_thresholds_data)
        print(f"    ✅ Created {results['resource_thresholds']} resource thresholds")
    except Exception as e:
        print(f"    ❌ Error seeding resource_thresholds: {e}")
        results['resource_thresholds'] = 0
    
    print("  Seeding resource_optimizations...")
    try:
        resource_optimizations_data = []
        for i in range(50):
            resource_type = random.choice(['CPU', 'MEMORY', 'STORAGE', 'NETWORK', 'DATABASE'])
            metric_type = random.choice(['USAGE', 'THROUGHPUT', 'LATENCY', 'ERROR_RATE', 'COST', 'EFFICIENCY'])
            resource_optimizations_data.append({
                'resource_type': resource_type,  # Required NOT NULL field
                'metric_type': metric_type,  # Required NOT NULL field
                'current_value': round(random.uniform(0.0, 100.0), 2),  # Required NOT NULL field
                'recommended_value': round(random.uniform(0.0, 100.0), 2),  # Required NOT NULL field
                'recommendation': f'Optimization recommendation for {resource_type} {metric_type}',  # Required NOT NULL field
                'status': random.choice(BASE_STATUS_VALUES),  # Required NOT NULL field
                'optimization_type': random.choice(['AUTO_SCALE', 'CACHE', 'COMPRESSION', 'CLEANUP', 'TUNING']),
                'description': f'Optimization for {random.choice(["CPU", "MEMORY", "STORAGE", "NETWORK", "DATABASE"])}',
                'impact_percentage': round(random.uniform(5.0, 50.0), 2),
                'is_applied': random.choice([True, False]),
                'applied_at': datetime.now() - timedelta(days=random.randint(1, 30)) if random.choice([True, False]) else None,
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
            })
        
        results['resource_optimizations'] = insert_data_flexible(session, 'resource_optimizations', resource_optimizations_data)
        print(f"    ✅ Created {results['resource_optimizations']} resource optimizations")
    except Exception as e:
        print(f"    ❌ Error seeding resource_optimizations: {e}")
        results['resource_optimizations'] = 0
    
    print("  Seeding resource_management_sharing...")
    try:
        resource_management_sharing_data = []
        for i in range(40):
            resource_management_sharing_data.append({
                'resource_id': random.randint(1, 100),
                'owner_id': random.choice(deps['user_ids']) if deps['user_ids'] else random.randint(1, 32),  # Required NOT NULL field
                'resource_type': random.choice(['CPU', 'MEMORY', 'STORAGE', 'NETWORK', 'DATABASE']),  # Required NOT NULL field
                'sharing_type': random.choice(['PUBLIC', 'PRIVATE', 'ORGANIZATION', 'TEAM']),  # Required NOT NULL field
                'sharing_permissions': json.dumps(['read', 'write']),  # Required NOT NULL field
                'sharing_scope': random.choice(['GLOBAL', 'ORGANIZATION', 'TEAM', 'USER']),  # Required NOT NULL field
                'shared_with_user_id': random.choice(deps['user_ids']) if deps['user_ids'] else random.randint(1, 32),
                'permission_level': random.choice(['READ', 'WRITE', 'ADMIN']),
                'status': random.choice(BASE_STATUS_VALUES),  # Required NOT NULL field
                'shared_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'expires_at': datetime.now() + timedelta(days=random.randint(1, 365)) if random.choice([True, False]) else None,
                'is_active': random.choice([True, False])
            })
        
        results['resource_management_sharing'] = insert_data_flexible(session, 'resource_management_sharing', resource_management_sharing_data)
        print(f"    ✅ Created {results['resource_management_sharing']} resource management sharing records")
    except Exception as e:
        print(f"    ❌ Error seeding resource_management_sharing: {e}")
        results['resource_management_sharing'] = 0
    
    print("  Seeding optimization_events...")
    try:
        optimization_events_data = []
        for i in range(80):
            optimization_events_data.append({
                'resource_id': random.randint(1, 100),  # Required NOT NULL field
                'event_type': random.choice(['AUTO_SCALE', 'CACHE_HIT', 'CACHE_MISS', 'CLEANUP', 'TUNING']),
                'resource_type': random.choice(['CPU', 'MEMORY', 'STORAGE', 'NETWORK', 'DATABASE']),
                'metric_type': random.choice(['USAGE', 'THROUGHPUT', 'LATENCY', 'ERROR_RATE', 'COST', 'EFFICIENCY']),  # Required NOT NULL field
                'severity': random.choice(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']),  # Required NOT NULL field
                'status': random.choice(BASE_STATUS_VALUES),  # Required NOT NULL field
                'description': f'Optimization event {i+1}',
                'impact_value': round(random.uniform(0.1, 100.0), 2),
                'is_successful': random.choice([True, False]),
                'created_at': datetime.now() - timedelta(hours=random.randint(1, 24))
            })
        
        results['optimization_events'] = insert_data_flexible(session, 'optimization_events', optimization_events_data)
        print(f"    ✅ Created {results['optimization_events']} optimization events")
    except Exception as e:
        print(f"    ❌ Error seeding optimization_events: {e}")
        results['optimization_events'] = 0
    
    print("  Seeding resource_optimization_thresholds...")
    try:
        resource_optimization_thresholds_data = []
        for i in range(15):
            resource_optimization_thresholds_data.append({
                'resource_type': random.choice(['CPU', 'MEMORY', 'STORAGE', 'NETWORK', 'DATABASE']),  # Required NOT NULL field
                'metric_type': random.choice(['USAGE', 'THROUGHPUT', 'LATENCY', 'ERROR_RATE', 'COST', 'EFFICIENCY']),  # Required NOT NULL field
                'threshold_value': round(random.uniform(0.5, 0.95), 2),  # Required NOT NULL field
                'threshold_type': random.choice(['WARNING', 'CRITICAL', 'INFO']),  # Required NOT NULL field
                'action': random.choice(['ALERT', 'SCALE_UP', 'SCALE_DOWN', 'RESTART', 'NOTIFY']),  # Required NOT NULL field
                'status': random.choice(BASE_STATUS_VALUES),  # Required NOT NULL field
                'optimization_threshold': round(random.uniform(50.0, 90.0), 2),
                'auto_optimize': random.choice([True, False]),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 7))
            })
        
        results['resource_optimization_thresholds'] = insert_data_flexible(session, 'resource_optimization_thresholds', resource_optimization_thresholds_data)
        print(f"    ✅ Created {results['resource_optimization_thresholds']} resource optimization thresholds")
    except Exception as e:
        print(f"    ❌ Error seeding resource_optimization_thresholds: {e}")
        results['resource_optimization_thresholds'] = 0
    
    print("  Seeding resource_optimization_recommendations...")
    try:
        resource_optimization_recommendations_data = []
        for i in range(60):
            resource_type = random.choice(['CPU', 'MEMORY', 'STORAGE', 'NETWORK', 'DATABASE'])
            metric_type = random.choice(['USAGE', 'THROUGHPUT', 'LATENCY', 'ERROR_RATE', 'COST', 'EFFICIENCY'])
            resource_optimization_recommendations_data.append({
                'resource_type': resource_type,  # Required NOT NULL field
                'metric_type': metric_type,  # Required NOT NULL field
                'current_value': round(random.uniform(0.0, 100.0), 2),  # Required NOT NULL field
                'recommended_value': round(random.uniform(0.0, 100.0), 2),  # Required NOT NULL field
                'recommendation': f'Optimization recommendation for {resource_type} {metric_type}',  # Required NOT NULL field
                'status': random.choice(BASE_STATUS_VALUES),  # Required NOT NULL field
                'recommendation_type': random.choice(['SCALE_UP', 'SCALE_DOWN', 'CACHE', 'CLEANUP', 'TUNING']),
                'description': f'Optimization recommendation {i+1}',
                'priority': random.choice(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']),
                'estimated_impact': round(random.uniform(5.0, 50.0), 2),
                'is_implemented': random.choice([True, False]),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
            })
        
        results['resource_optimization_recommendations'] = insert_data_flexible(session, 'resource_optimization_recommendations', resource_optimization_recommendations_data)
        print(f"    ✅ Created {results['resource_optimization_recommendations']} resource optimization recommendations")
    except Exception as e:
        print(f"    ❌ Error seeding resource_optimization_recommendations: {e}")
        results['resource_optimization_recommendations'] = 0
    
    print("  Seeding resource_optimization_events...")
    try:
        resource_optimization_events_data = []
        for i in range(70):
            resource_optimization_events_data.append({
                'resource_id': random.randint(1, 100), # Required NOT NULL field
                'resource_type': random.choice(['CPU', 'MEMORY', 'STORAGE', 'NETWORK', 'DATABASE']),
                'metric_type': random.choice(['USAGE', 'THROUGHPUT', 'LATENCY', 'ERROR_RATE', 'COST', 'EFFICIENCY']),  # Required NOT NULL field
                'event_type': random.choice(['OPTIMIZATION_STARTED', 'OPTIMIZATION_COMPLETED', 'OPTIMIZATION_FAILED']),
                'severity': random.choice(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']),  # Required NOT NULL field
                'description': f'Resource optimization event {i+1}',
                'status': random.choice(BASE_STATUS_VALUES),  # Use correct enum values
                'created_at': datetime.now() - timedelta(hours=random.randint(1, 24))
            })
        
        results['resource_optimization_events'] = insert_data_flexible(session, 'resource_optimization_events', resource_optimization_events_data)
        print(f"    ✅ Created {results['resource_optimization_events']} resource optimization events")
    except Exception as e:
        print(f"    ❌ Error seeding resource_optimization_events: {e}")
        results['resource_optimization_events'] = 0
    
    print("  Seeding resource_events...")
    try:
        resource_events_data = []
        for i in range(90):
            resource_events_data.append({
                'resource_id': random.randint(1, 100),  # Required NOT NULL field
                'resource_type': random.choice(['CPU', 'MEMORY', 'STORAGE', 'NETWORK', 'DATABASE']),
                'metric_type': random.choice(['USAGE', 'THROUGHPUT', 'LATENCY', 'ERROR_RATE', 'COST', 'EFFICIENCY']), # Required NOT NULL field
                'event_type': random.choice(['THRESHOLD_EXCEEDED', 'THRESHOLD_RECOVERED', 'OPTIMIZATION_APPLIED']),
                'status': random.choice(BASE_STATUS_VALUES),  # Required NOT NULL field
                'description': f'Resource event {i+1}',
                'severity': random.choice(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']),
                'created_at': datetime.now() - timedelta(hours=random.randint(1, 24))
            })
        
        results['resource_events'] = insert_data_flexible(session, 'resource_events', resource_events_data)
        print(f"    ✅ Created {results['resource_events']} resource events")
    except Exception as e:
        print(f"    ❌ Error seeding resource_events: {e}")
        results['resource_events'] = 0
    
    # Additional missing tables from original Phase 11
    print("  Seeding feedback_project_comments...")
    try:
        # Get actual feedback project IDs
        project_result = session.execute(text("SELECT id FROM feedback_projects LIMIT 25"))
        project_ids = [row[0] for row in project_result.fetchall()]
        
        if not project_ids:
            print("    ⚠️  No feedback projects found, skipping feedback_project_comments")
            results['feedback_project_comments'] = 0
        else:
            feedback_project_comments_data = []
            for i in range(100):
                feedback_project_comments_data.append({
                    'project_id': random.choice(project_ids),  # Use actual feedback project IDs
                    'user_id': random.choice(deps['user_ids']) if deps['user_ids'] else random.randint(1, 32),
                    'content': f'Feedback project comment {i+1}',  # Required NOT NULL field
                    'comment': f'Feedback project comment {i+1}',
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
                })
            
            results['feedback_project_comments'] = insert_data_flexible(session, 'feedback_project_comments', feedback_project_comments_data)
            print(f"    ✅ Created {results['feedback_project_comments']} feedback project comments")
    except Exception as e:
        print(f"    ❌ Error seeding feedback_project_comments: {e}")
        results['feedback_project_comments'] = 0
    
    print("  Seeding feedback_project_members...")
    try:
        # Get actual feedback project IDs
        project_result = session.execute(text("SELECT id FROM feedback_projects LIMIT 25"))
        project_ids = [row[0] for row in project_result.fetchall()]
        
        if not project_ids:
            print("    ⚠️  No feedback projects found, skipping feedback_project_members")
            results['feedback_project_members'] = 0
        else:
            feedback_project_members_data = []
            for i in range(60):
                feedback_project_members_data.append({
                    'project_id': random.choice(project_ids),  # Use actual feedback project IDs
                    'user_id': random.choice(deps['user_ids']) if deps['user_ids'] else random.randint(1, 32),
                    'role': random.choice(['MEMBER', 'ADMIN', 'OWNER', 'VIEWER']),
                    'status': random.choice(BASE_STATUS_VALUES),  # Required NOT NULL field
                    'joined_at': datetime.now() - timedelta(days=random.randint(1, 30))
                })
            
            results['feedback_project_members'] = insert_data_flexible(session, 'feedback_project_members', feedback_project_members_data)
            print(f"    ✅ Created {results['feedback_project_members']} feedback project members")
    except Exception as e:
        print(f"    ❌ Error seeding feedback_project_members: {e}")
        results['feedback_project_members'] = 0
    
    print("  Seeding feedback_project_resources...")
    try:
        # Get actual feedback project IDs
        project_result = session.execute(text("SELECT id FROM feedback_projects LIMIT 25"))
        project_ids = [row[0] for row in project_result.fetchall()]
        
        if not project_ids:
            print("    ⚠️  No feedback projects found, skipping feedback_project_resources")
            results['feedback_project_resources'] = 0
        else:
            feedback_project_resources_data = []
            for i in range(80):
                feedback_project_resources_data.append({
                    'project_id': random.choice(project_ids),  # Use actual feedback project IDs
                    'name': f'Feedback Resource {i+1}',  # Required NOT NULL field
                    'resource_name': f'Feedback Resource {i+1}',
                    'resource_type': random.choice(['DOCUMENT', 'IMAGE', 'VIDEO', 'AUDIO', 'LINK']),
                    'status': random.choice(BASE_STATUS_VALUES),  # Required NOT NULL field
                    'resource_url': f'https://example.com/resource_{i+1}',
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
                })
            
            results['feedback_project_resources'] = insert_data_flexible(session, 'feedback_project_resources', feedback_project_resources_data)
            print(f"    ✅ Created {results['feedback_project_resources']} feedback project resources")
    except Exception as e:
        print(f"    ❌ Error seeding feedback_project_resources: {e}")
        results['feedback_project_resources'] = 0
    
    print("  Seeding feedback_project_tasks...")
    try:
        # Get actual feedback project IDs
        project_result = session.execute(text("SELECT id FROM feedback_projects LIMIT 25"))
        project_ids = [row[0] for row in project_result.fetchall()]
        
        if not project_ids:
            print("    ⚠️  No feedback projects found, skipping feedback_project_tasks")
            results['feedback_project_tasks'] = 0
        else:
            feedback_project_tasks_data = []
            for i in range(120):
                feedback_project_tasks_data.append({
                    'project_id': random.choice(project_ids),  # Use actual feedback project IDs
                    'title': f'Feedback Task {i+1}',  # Required NOT NULL field
                    'task_name': f'Feedback Task {i+1}',
                    'description': f'Description for feedback task {i+1}',
                    'assigned_to': random.choice(deps['user_ids']) if deps['user_ids'] else random.randint(1, 32),
                    'status': random.choice(BASE_STATUS_VALUES),
                    'due_date': datetime.now() + timedelta(days=random.randint(1, 30)),
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
                })
            
            results['feedback_project_tasks'] = insert_data_flexible(session, 'feedback_project_tasks', feedback_project_tasks_data)
            print(f"    ✅ Created {results['feedback_project_tasks']} feedback project tasks")
    except Exception as e:
        print(f"    ❌ Error seeding feedback_project_tasks: {e}")
        results['feedback_project_tasks'] = 0
    
    print("  Seeding project_roles...")
    try:
        # Get actual organization project IDs
        project_result = session.execute(text("SELECT id FROM organization_projects LIMIT 25"))
        project_ids = [row[0] for row in project_result.fetchall()]
        
        if not project_ids:
            print("    ⚠️  No organization projects found, skipping project_roles")
            results['project_roles'] = 0
        else:
            project_roles_data = []
            for i in range(20):
                project_roles_data.append({
                    'project_id': random.choice(project_ids),  # Use actual organization project IDs
                    'name': f'Project Role {i+1}',
                    'description': f'Description for project role {i+1}',
                    'permissions': json.dumps(['read', 'write', 'admin']),
                    'status': random.choice(BASE_STATUS_VALUES),  # Required NOT NULL field
                    'updated_at': datetime.now() - timedelta(days=random.randint(1, 7)),  # Required NOT NULL field
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
                })
            
            results['project_roles'] = insert_data_flexible(session, 'project_roles', project_roles_data)
            print(f"    ✅ Created {results['project_roles']} project roles")
    except Exception as e:
        print(f"    ❌ Error seeding project_roles: {e}")
        results['project_roles'] = 0
    
    print("  Seeding project_settings...")
    try:
        # Get actual organization project IDs
        project_result = session.execute(text("SELECT id FROM organization_projects LIMIT 25"))
        project_ids = [row[0] for row in project_result.fetchall()]
        
        if not project_ids:
            print("    ⚠️  No organization projects found, skipping project_settings")
            results['project_settings'] = 0
        else:
            # Check existing project settings to avoid unique constraint violations
            existing_result = session.execute(text("SELECT project_id FROM project_settings"))
            existing_project_ids = {row[0] for row in existing_result.fetchall()}
            
            project_settings_data = []
            attempts = 0
            max_attempts = 100  # Prevent infinite loop
            
            while len(project_settings_data) < 25 and attempts < max_attempts:
                project_id = random.choice(project_ids)
                # Skip if this project already has settings
                if project_id not in existing_project_ids:
                    project_settings_data.append({
                        'project_id': project_id,  # Use actual organization project IDs
                        'setting_key': random.choice(['notifications', 'privacy', 'collaboration', 'reporting']),
                        'setting_value': json.dumps({'enabled': True, 'frequency': 'daily'}),
                        'status': random.choice(BASE_STATUS_VALUES),  # Required NOT NULL field
                        'updated_at': datetime.now() - timedelta(days=random.randint(1, 7)),  # Required NOT NULL field
                        'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
                    })
                    # Add to existing set to avoid duplicates in this batch
                    existing_project_ids.add(project_id)
                attempts += 1
            
            if project_settings_data:
                results['project_settings'] = insert_data_flexible(session, 'project_settings', project_settings_data)
                print(f"    ✅ Created {results['project_settings']} project settings")
            else:
                # Count existing project settings as successful
                existing_count = session.execute(text("SELECT COUNT(*) FROM project_settings")).scalar()
                results['project_settings'] = existing_count
                print(f"    ✅ Found {existing_count} existing project settings, using for foreign key references")
    except Exception as e:
        print(f"    ❌ Error seeding project_settings: {e}")
        results['project_settings'] = 0
    
    print("  Seeding resource_alerts...")
    try:
        resource_alerts_data = []
        for i in range(50):
            resource_alerts_data.append({
                'alert_type': random.choice(['CPU_HIGH', 'MEMORY_LOW', 'DISK_FULL', 'NETWORK_SLOW', 'SERVICE_DOWN']),
                'severity': random.choice(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']),
                'description': f'Resource alert {i+1}',  # Required NOT NULL field
                'message': f'Resource alert {i+1}',
                'status': random.choice(BASE_STATUS_VALUES),  # Required NOT NULL field
                'organization_id': random.choice(deps['org_ids']) if deps['org_ids'] else 1,
                'user_id': random.choice(deps['user_ids']) if deps['user_ids'] else random.randint(1, 32),
                'created_at': datetime.now() - timedelta(hours=random.randint(1, 24))
            })
        
        results['resource_alerts'] = insert_data_flexible(session, 'resource_alerts', resource_alerts_data)
        print(f"    ✅ Created {results['resource_alerts']} resource alerts")
    except Exception as e:
        print(f"    ❌ Error seeding resource_alerts: {e}")
        results['resource_alerts'] = 0

    return results

def seed_communication_feedback_system(session: Session, deps: Dict[str, List[int]]) -> Dict[str, int]:
    """Seed Communication & Feedback System (8 tables)."""
    results = {}
    
    print("  Seeding comments...")
    try:
        # Get actual dashboard project IDs (comments references dashboard_projects)
        project_result = session.execute(text("SELECT id FROM dashboard_projects LIMIT 25"))
        project_ids = [row[0] for row in project_result.fetchall()]
        
        if not project_ids:
            print("    ⚠️  No dashboard projects found, skipping comments")
            results['comments'] = 0
        else:
            comments_data = []
            for i in range(200):
                comments_data.append({
                    'project_id': random.choice(project_ids),  # Use actual dashboard project IDs
                    'user_id': random.choice(deps['user_ids']) if deps['user_ids'] else random.randint(1, 32),  # Required NOT NULL field
                    'content': f'Comment content {i+1}',
                    'author_id': random.choice(deps['user_ids']) if deps['user_ids'] else random.randint(1, 32),
                    'parent_id': random.randint(1, 200) if random.random() < 0.3 else None,
                    'is_approved': random.choice([True, False]),
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                    'updated_at': datetime.now() - timedelta(days=random.randint(1, 7))
                })
        
        results['comments'] = insert_data_flexible(session, 'comments', comments_data)
        print(f"    ✅ Created {results['comments']} comments")
    except Exception as e:
        print(f"    ❌ Error seeding comments: {e}")
        results['comments'] = 0
    
    print("  Seeding messages...")
    try:
        messages_data = []
        for i in range(300):
            messages_data.append({
                'sender_id': random.choice(deps['user_ids']) if deps['user_ids'] else random.randint(1, 32),
                'recipient_id': random.choice(deps['user_ids']) if deps['user_ids'] else random.randint(1, 32),
                'subject': f'Message subject {i+1}',
                'content': f'Message content {i+1}',
                'message_type': random.choice(['EMAIL', 'SMS', 'PUSH', 'IN_APP']),
                'is_read': random.choice([True, False]),
                'sent_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
            })
        
        results['messages'] = insert_data_flexible(session, 'messages', messages_data)
        print(f"    ✅ Created {results['messages']} messages")
    except Exception as e:
        print(f"    ❌ Error seeding messages: {e}")
        results['messages'] = 0
    
    print("  Seeding message_boards...")
    try:
        message_boards_data = []
        for i in range(10):
            message_boards_data.append({
                'name': f'Message Board {i+1}',
                'description': f'Description for message board {i+1}',
                'is_public': random.choice([True, False]),
                'created_by': random.choice(deps['user_ids']) if deps['user_ids'] else random.randint(1, 32),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
            })
        
        results['message_boards'] = insert_data_flexible(session, 'message_boards', message_boards_data)
        print(f"    ✅ Created {results['message_boards']} message boards")
    except Exception as e:
        print(f"    ❌ Error seeding message_boards: {e}")
        results['message_boards'] = 0
    
    print("  Seeding message_board_posts...")
    try:
        # Get actual message_boards IDs
        board_result = session.execute(text("SELECT id FROM message_boards "))
        board_ids = [row[0] for row in board_result.fetchall()]
        
        if not board_ids:
            print("    ⚠️  No message_boards found, skipping message_board_posts")
            results['message_board_posts'] = 0
        else:
            message_board_posts_data = []
            for i in range(150):
                message_board_posts_data.append({
                    'board_id': random.choice(board_ids),  # Use actual message_boards IDs
                    'author_id': random.choice(deps['user_ids']) if deps['user_ids'] else random.randint(1, 32),
                    'title': f'Post title {i+1}',
                    'content': f'Post content {i+1}',
                    'is_pinned': random.choice([True, False]),
                    'is_locked': random.choice([True, False]),
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                    'updated_at': datetime.now() - timedelta(days=random.randint(1, 7))
                })
            
            results['message_board_posts'] = insert_data_flexible(session, 'message_board_posts', message_board_posts_data)
            print(f"    ✅ Created {results['message_board_posts']} message board posts")
    except Exception as e:
        print(f"    ❌ Error seeding message_board_posts: {e}")
        results['message_board_posts'] = 0
    
    print("  Seeding feedback...")
    try:
        feedback_data = []
        for i in range(250):
            feedback_data.append({
                'feedback_type': random.choice(FEEDBACK_TYPES),
                'content': json.dumps({'text': f'Feedback content {i+1}', 'type': 'feedback'}),
                'rating': random.randint(1, 5),
                'priority': random.choice(['LOW', 'MEDIUM', 'HIGH', 'URGENT']),
                'user_id': random.choice(deps['user_ids']) if deps['user_ids'] else random.randint(1, 32),
                'gpt_id': random.randint(1, 10),
                'status': random.choice(BASE_STATUS_VALUES),
                'is_active': random.choice([True, False]),
                'metadata': json.dumps({'source': 'feedback_system', 'version': '1.0', 'type': 'feedback'}),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
            })
        
        results['feedback'] = insert_data_flexible(session, 'feedback', feedback_data)
        print(f"    ✅ Created {results['feedback']} feedback records")
    except Exception as e:
        print(f"    ❌ Error seeding feedback: {e}")
        results['feedback'] = 0
    
    print("  Seeding feedback_user_tool_settings...")
    try:
        # Check if feedback_user_tool_settings already has data and use it
        existing_count = session.execute(text("SELECT COUNT(*) FROM feedback_user_tool_settings")).scalar()
        if existing_count > 0:
            print(f"    ✅ Found {existing_count} existing feedback user tool settings, using for foreign key references")
            results['feedback_user_tool_settings'] = existing_count
        else:
            # Get existing combinations to avoid duplicates
            existing_combinations = set()
            existing_result = session.execute(text("SELECT user_id, tool_id FROM feedback_user_tool_settings"))
            for row in existing_result.fetchall():
                existing_combinations.add((row[0], row[1]))
            
            feedback_user_tool_settings_data = []
            user_ids = deps['user_ids'] if deps['user_ids'] else list(range(1, 33))
            tool_ids = deps['dashboard_tool_ids'] if deps['dashboard_tool_ids'] else list(range(1, 11))
            
            for i in range(50):
                user_id = random.choice(user_ids)
                tool_id = random.choice(tool_ids)
                
                # Skip if combination already exists
                if (user_id, tool_id) in existing_combinations:
                    continue
                    
                feedback_user_tool_settings_data.append({
                    'user_id': user_id,
                    'tool_id': tool_id,
                    'notification_enabled': random.choice([True, False]),
                    'auto_response': random.choice([True, False]),
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                    'updated_at': datetime.now() - timedelta(days=random.randint(1, 7))
                })
                existing_combinations.add((user_id, tool_id))
            
            if feedback_user_tool_settings_data:
                results['feedback_user_tool_settings'] = insert_data_flexible(session, 'feedback_user_tool_settings', feedback_user_tool_settings_data)
                print(f"    ✅ Created {results['feedback_user_tool_settings']} feedback user tool settings")
            else:
                results['feedback_user_tool_settings'] = 0
                print(f"    ⚠️ No new feedback user tool settings created (all combinations already exist)")
    except Exception as e:
        print(f"    ❌ Error seeding feedback_user_tool_settings: {e}")
        results['feedback_user_tool_settings'] = 0
    
    print("  Seeding skill_assessment_risk_assessments...")
    try:
        skill_assessment_risk_assessments_data = []
        for i in range(80):
            skill_assessment_risk_assessments_data.append({
                'assessment_id': random.randint(1, 50),
                'activity_id': random.randint(1, 50),  # Required NOT NULL field
                'risk_level': random.choice(['LOW', 'MEDIUM', 'HIGH']),
                'factors': json.dumps(['factor1', 'factor2', 'factor3']),  # Required NOT NULL field
                'mitigation_measures': json.dumps(['measure1', 'measure2', 'measure3']),  # Required NOT NULL field
                'mitigation_plan': f'Mitigation plan for assessment {i+1}',
                'assessed_by': random.choice(deps['user_ids']) if deps['user_ids'] else random.randint(1, 32),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 7))  # Required NOT NULL field
            })
        
        results['skill_assessment_risk_assessments'] = insert_data_flexible(session, 'skill_assessment_risk_assessments', skill_assessment_risk_assessments_data)
        print(f"    ✅ Created {results['skill_assessment_risk_assessments']} skill assessment risk assessments")
    except Exception as e:
        print(f"    ❌ Error seeding skill_assessment_risk_assessments: {e}")
        results['skill_assessment_risk_assessments'] = 0
    
    print("  Seeding safety...")
    try:
        safety_data = []
        for i in range(60):
            safety_data.append({
                'activity_id': random.randint(1, 50),  # Required NOT NULL field
                'risk_level': random.choice(['LOW', 'MEDIUM', 'HIGH']),  # Required NOT NULL field
                'incident_type': random.choice(['INJURY', 'EQUIPMENT_FAILURE', 'ENVIRONMENTAL', 'BEHAVIORAL']),
                'description': f'Safety incident {i+1}',
                'severity': random.choice(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']),
                'reported_by': random.choice(deps['user_ids']) if deps['user_ids'] else random.randint(1, 32),
                'status': random.choice(['REPORTED', 'INVESTIGATING', 'RESOLVED', 'CLOSED']),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 7))  # Required NOT NULL field
            })
        
        results['safety'] = insert_data_flexible(session, 'safety', safety_data)
        print(f"    ✅ Created {results['safety']} safety records")
    except Exception as e:
        print(f"    ❌ Error seeding safety: {e}")
        results['safety'] = 0
    
    return results

def seed_core_system_integration(session: Session, deps: Dict[str, List[int]]) -> Dict[str, int]:
    """Seed Core System Integration (3 tables)."""
    results = {}
    
    print("  Seeding core_activities...")
    try:
        core_activities_data = []
        for i in range(50):
            core_activities_data.append({
                'name': f'Core Activity {i+1}',
                'description': f'Description for core activity {i+1}',
                'type': random.choice(['WARM_UP', 'COOL_DOWN', 'STRETCHING', 'STRENGTH_TRAINING', 'CARDIO', 'FLEXIBILITY', 'BALANCE', 'COORDINATION', 'TEAM_SPORTS', 'INDIVIDUAL_SPORTS', 'RACKET_SPORTS', 'WATER_SPORTS', 'WINTER_SPORTS', 'COMBAT_SPORTS', 'HIIT', 'CROSSFIT', 'YOGA', 'PILATES', 'DANCE', 'MARTIAL_ARTS', 'GAMES', 'PLAY', 'OUTDOOR', 'ADVENTURE', 'RECREATIONAL', 'SKILL_DEVELOPMENT', 'TECHNIQUE_PRACTICE', 'DRILLS', 'EXERCISES', 'ASSESSMENTS', 'REHABILITATION', 'PREHABILITATION', 'THERAPEUTIC', 'RECOVERY', 'REGENERATION', 'MOBILITY', 'STABILITY', 'POSTURE', 'MOVEMENT', 'SKILL', 'TECHNIQUE', 'MAINTENANCE', 'PREVENTION', 'CORRECTION', 'ADAPTATION', 'PROGRESSION', 'REGRESSION', 'MODIFICATION', 'VARIATION', 'ALTERNATIVE', 'SUBSTITUTE', 'OTHER']),  # Required NOT NULL field
                'activity_type': random.choice(['WARM_UP', 'COOL_DOWN', 'STRETCHING', 'STRENGTH_TRAINING', 'CARDIO', 'FLEXIBILITY', 'BALANCE', 'COORDINATION', 'TEAM_SPORTS', 'INDIVIDUAL_SPORTS', 'RACKET_SPORTS', 'WATER_SPORTS', 'WINTER_SPORTS', 'COMBAT_SPORTS', 'HIIT', 'CROSSFIT', 'YOGA', 'PILATES', 'DANCE', 'MARTIAL_ARTS', 'GAMES', 'PLAY', 'OUTDOOR', 'ADVENTURE', 'RECREATIONAL', 'SKILL_DEVELOPMENT', 'TECHNIQUE_PRACTICE', 'DRILLS', 'EXERCISES', 'ASSESSMENTS', 'REHABILITATION', 'PREHABILITATION', 'THERAPEUTIC', 'RECOVERY', 'REGENERATION', 'MOBILITY', 'STABILITY', 'POSTURE', 'MOVEMENT', 'SKILL', 'TECHNIQUE', 'MAINTENANCE', 'PREVENTION', 'CORRECTION', 'ADAPTATION', 'PROGRESSION', 'REGRESSION', 'MODIFICATION', 'VARIATION', 'ALTERNATIVE', 'SUBSTITUTE', 'OTHER']),
                'difficulty_level': random.choice(['BEGINNER', 'INTERMEDIATE', 'ADVANCED', 'EXPERT']),
                'duration_minutes': random.randint(15, 120),
                'is_active': random.choice([True, False]),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
            })
        
        results['core_activities'] = insert_data_flexible(session, 'core_activities', core_activities_data)
        print(f"    ✅ Created {results['core_activities']} core activities")
    except Exception as e:
        print(f"    ❌ Error seeding core_activities: {e}")
        results['core_activities'] = 0
    
    print("  Seeding subject_assistant...")
    try:
        # Get actual subject_category and assistant_profile IDs
        subject_category_result = session.execute(text("SELECT id FROM subject_categories "))
        subject_category_ids = [row[0] for row in subject_category_result.fetchall()]
        
        assistant_profile_result = session.execute(text("SELECT id FROM assistant_profiles "))
        assistant_profile_ids = [row[0] for row in assistant_profile_result.fetchall()]
        
        if not subject_category_ids or not assistant_profile_ids:
            print("    ⚠️  No subject categories or assistant profiles found, skipping subject_assistant")
            results['subject_assistant'] = 0
        else:
            subject_assistant_data = []
            for i in range(30):
                subject_assistant_data.append({
                    'subject_category_id': random.choice(subject_category_ids),  # Use actual subject category IDs
                    'assistant_profile_id': random.choice(assistant_profile_ids)  # Use actual assistant profile IDs
                })
            
            results['subject_assistant'] = insert_data_flexible(session, 'subject_assistant', subject_assistant_data)
            print(f"    ✅ Created {results['subject_assistant']} subject assistants")
    except Exception as e:
        print(f"    ❌ Error seeding subject_assistant: {e}")
        results['subject_assistant'] = 0
    
    print("  Seeding context_data...")
    try:
        context_data_records = []
        for i in range(100):
            data_type = random.choice(['JSON', 'TEXT', 'BINARY', 'STRUCTURED'])
            content = json.dumps({'text': f'Context content {i+1}', 'type': data_type})
            
            context_data_records.append({
                'context_id': random.randint(1, 1000),  # Required NOT NULL field
                'gpt_id': random.randint(1, 10),  # Required NOT NULL field
                'data_type': data_type,  # Required NOT NULL field
                'content': content,  # Required NOT NULL field
                'context_type': random.choice(['USER_SESSION', 'ACTIVITY', 'ASSESSMENT', 'FEEDBACK']),
                'data_key': f'context_key_{i+1}',
                'data_value': json.dumps({'value': f'context_value_{i+1}', 'metadata': {'source': 'system'}}),
                'status': random.choice(BASE_STATUS_VALUES),  # Required NOT NULL field
                'expires_at': datetime.now() + timedelta(hours=random.randint(1, 24)),
                'created_at': datetime.now() - timedelta(hours=random.randint(1, 24)),
                'updated_at': datetime.now() - timedelta(hours=random.randint(1, 12))  # Required NOT NULL field
            })
        
        results['context_data'] = insert_data_flexible(session, 'context_data', context_data_records)
        print(f"    ✅ Created {results['context_data']} context data records")
    except Exception as e:
        print(f"    ❌ Error seeding context_data: {e}")
        results['context_data'] = 0
    
    return results

def seed_billing_subscription_system(session: Session, deps: Dict[str, List[int]]) -> Dict[str, int]:
    """Seed Billing & Subscription System (6 tables)."""
    results = {}
    
    print("  Seeding gpt_subscription_plans...")
    try:
        gpt_subscription_plans_data = []
        for i in range(5):
            gpt_subscription_plans_data.append({
                'name': f'Plan {i+1}',
                'description': f'Description for subscription plan {i+1}',
                'price': round(random.uniform(9.99, 99.99), 2),
                'currency': 'USD',  # Required NOT NULL field
                'billing_cycle': random.choice(['MONTHLY', 'QUARTERLY', 'YEARLY']),
                'features': json.dumps(['feature1', 'feature2', 'feature3']),
                'status': random.choice(BASE_STATUS_VALUES),  # Required NOT NULL field
                'is_active': random.choice([True, False]),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
            })
        
        results['gpt_subscription_plans'] = insert_data_flexible(session, 'gpt_subscription_plans', gpt_subscription_plans_data)
        print(f"    ✅ Created {results['gpt_subscription_plans']} GPT subscription plans")
    except Exception as e:
        print(f"    ❌ Error seeding gpt_subscription_plans: {e}")
        results['gpt_subscription_plans'] = 0
    
    print("  Seeding gpt_subscriptions...")
    try:
        # Get actual plan IDs
        plan_result = session.execute(text("SELECT id FROM gpt_subscription_plans LIMIT 5"))
        plan_ids = [row[0] for row in plan_result.fetchall()]
        
        if not plan_ids:
            print("    ⚠️  No subscription plans found, skipping gpt_subscriptions")
            results['gpt_subscriptions'] = 0
        else:
            gpt_subscriptions_data = []
            for i in range(30):
                gpt_subscriptions_data.append({
                    'user_id': random.choice(deps['user_ids']) if deps['user_ids'] else random.randint(1, 32),
                    'plan_id': random.choice(plan_ids),  # Use actual plan IDs
                'subscription_type': random.choice(['BASIC', 'PREMIUM', 'ENTERPRISE', 'TRIAL']),  # Required NOT NULL field
                'billing_cycle': random.choice(['MONTHLY', 'QUARTERLY', 'YEARLY']),  # Required NOT NULL field
                'price': round(random.uniform(9.99, 99.99), 2),  # Required NOT NULL field
                'currency': 'USD',  # Required NOT NULL field
                'status': random.choice(BASE_STATUS_VALUES),
                'start_date': datetime.now() - timedelta(days=random.randint(1, 30)),
                'end_date': datetime.now() + timedelta(days=random.randint(1, 365)),
                'auto_renew': random.choice([True, False]),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
            })
            
            results['gpt_subscriptions'] = insert_data_flexible(session, 'gpt_subscriptions', gpt_subscriptions_data)
            print(f"    ✅ Created {results['gpt_subscriptions']} GPT subscriptions")
    except Exception as e:
        print(f"    ❌ Error seeding gpt_subscriptions: {e}")
        results['gpt_subscriptions'] = 0
    
    print("  Seeding gpt_subscription_billing...")
    try:
        # Get actual GPT subscription IDs
        subscription_result = session.execute(text("SELECT id FROM gpt_subscriptions LIMIT 30"))
        subscription_ids = [row[0] for row in subscription_result.fetchall()]
        
        if not subscription_ids:
            print("    ⚠️  No gpt_subscriptions found, skipping gpt_subscription_billing")
            results['gpt_subscription_billing'] = 0
        else:
            gpt_subscription_billing_data = []
            for i in range(50):
                gpt_subscription_billing_data.append({
                    'subscription_id': random.choice(subscription_ids),  # Use actual subscription IDs
                    'billing_cycle_start': datetime.now() - timedelta(days=random.randint(1, 30)),  # Required NOT NULL field
                    'billing_cycle_end': datetime.now() + timedelta(days=random.randint(1, 30)),  # Required NOT NULL field
                    'base_amount': round(random.uniform(9.99, 99.99), 2),  # Required NOT NULL field
                    'amount': round(random.uniform(9.99, 99.99), 2),
                    'currency': 'USD',  # Required NOT NULL field
                    'due_date': datetime.now() + timedelta(days=random.randint(1, 30)),  # Required NOT NULL field
                    'billing_date': datetime.now() - timedelta(days=random.randint(1, 30)),
                    'status': random.choice(['PENDING', 'PAID', 'FAILED', 'REFUNDED']),
                    'payment_method': random.choice(['CREDIT_CARD', 'PAYPAL', 'BANK_TRANSFER']),
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
                })
            
            results['gpt_subscription_billing'] = insert_data_flexible(session, 'gpt_subscription_billing', gpt_subscription_billing_data)
            print(f"    ✅ Created {results['gpt_subscription_billing']} GPT subscription billing records")
    except Exception as e:
        print(f"    ❌ Error seeding gpt_subscription_billing: {e}")
        results['gpt_subscription_billing'] = 0
    
    print("  Seeding gpt_subscription_usage...")
    try:
        # Get actual GPT subscription IDs
        subscription_result = session.execute(text("SELECT id FROM gpt_subscriptions LIMIT 30"))
        subscription_ids = [row[0] for row in subscription_result.fetchall()]
        
        if not subscription_ids:
            print("    ⚠️  No gpt_subscriptions found, skipping gpt_subscription_usage")
            results['gpt_subscription_usage'] = 0
        else:
            gpt_subscription_usage_data = []
            for i in range(100):
                gpt_subscription_usage_data.append({
                    'subscription_id': random.choice(subscription_ids),  # Use actual subscription IDs
                    'billing_period_start': datetime.now() - timedelta(days=random.randint(1, 30)),  # Required NOT NULL field
                    'billing_period_end': datetime.now() + timedelta(days=random.randint(1, 30)),  # Required NOT NULL field
                    'usage_type': random.choice(['API_CALLS', 'STORAGE', 'BANDWIDTH', 'FEATURES']),
                    'usage_amount': random.randint(1, 1000),
                    'currency': 'USD',  # Required NOT NULL field
                    'usage_date': datetime.now() - timedelta(days=random.randint(1, 30)),
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
                })
            
            results['gpt_subscription_usage'] = insert_data_flexible(session, 'gpt_subscription_usage', gpt_subscription_usage_data)
            print(f"    ✅ Created {results['gpt_subscription_usage']} GPT subscription usage records")
    except Exception as e:
        print(f"    ❌ Error seeding gpt_subscription_usage: {e}")
        results['gpt_subscription_usage'] = 0
    
    print("  Seeding gpt_subscription_payments...")
    try:
        # Get actual GPT subscription billing IDs and subscription IDs
        billing_result = session.execute(text("SELECT id FROM gpt_subscription_billing LIMIT 50"))
        billing_ids = [row[0] for row in billing_result.fetchall()]
        
        subscription_result = session.execute(text("SELECT id FROM gpt_subscriptions LIMIT 30"))
        subscription_ids = [row[0] for row in subscription_result.fetchall()]
        
        if not billing_ids or not subscription_ids:
            print("    ⚠️  No gpt_subscription_billing or gpt_subscriptions found, skipping gpt_subscription_payments")
            results['gpt_subscription_payments'] = 0
        else:
            gpt_subscription_payments_data = []
            for i in range(40):
                gpt_subscription_payments_data.append({
                    'subscription_id': random.choice(subscription_ids),  # Use actual subscription IDs
                    'billing_cycle_id': random.choice(billing_ids),  # Use actual billing cycle IDs
                    'amount': round(random.uniform(9.99, 99.99), 2),
                    'currency': 'USD',  # Required NOT NULL field
                    'payment_method': random.choice(['CREDIT_CARD', 'PAYPAL', 'BANK_TRANSFER', 'STRIPE']),  # Required NOT NULL field
                    'payment_date': datetime.now() - timedelta(days=random.randint(1, 30)),
                    'status': random.choice(['PENDING', 'COMPLETED', 'FAILED', 'REFUNDED']),
                    'transaction_id': f'txn_{i+1}_{random.randint(1000, 9999)}',
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
                })
            
            results['gpt_subscription_payments'] = insert_data_flexible(session, 'gpt_subscription_payments', gpt_subscription_payments_data)
            print(f"    ✅ Created {results['gpt_subscription_payments']} GPT subscription payments")
    except Exception as e:
        print(f"    ❌ Error seeding gpt_subscription_payments: {e}")
        results['gpt_subscription_payments'] = 0
    
    print("  Seeding gpt_subscription_invoices...")
    try:
        # Get actual GPT subscription billing IDs and subscription IDs
        billing_result = session.execute(text("SELECT id FROM gpt_subscription_billing LIMIT 50"))
        billing_ids = [row[0] for row in billing_result.fetchall()]
        
        subscription_result = session.execute(text("SELECT id FROM gpt_subscriptions LIMIT 30"))
        subscription_ids = [row[0] for row in subscription_result.fetchall()]
        
        if not billing_ids or not subscription_ids:
            print("    ⚠️  No gpt_subscription_billing or gpt_subscriptions found, skipping gpt_subscription_invoices")
            results['gpt_subscription_invoices'] = 0
        else:
            # Get existing invoice numbers to avoid duplicates
            existing_invoices = session.execute(text("SELECT invoice_number FROM gpt_subscription_invoices")).fetchall()
            existing_invoice_numbers = {row[0] for row in existing_invoices}
            
            gpt_subscription_invoices_data = []
            invoice_counter = 1
            for i in range(35):
                # Generate unique invoice number
                while f'INV-{invoice_counter:06d}' in existing_invoice_numbers:
                    invoice_counter += 1
                
                invoice_number = f'INV-{invoice_counter:06d}'
                existing_invoice_numbers.add(invoice_number)
                invoice_counter += 1
                
                gpt_subscription_invoices_data.append({
                    'subscription_id': random.choice(subscription_ids),  # Use actual subscription IDs
                    'billing_cycle_id': random.choice(billing_ids),  # Use actual billing cycle IDs
                    'invoice_number': invoice_number,
                    'invoice_date': datetime.now() - timedelta(days=random.randint(1, 30)),  # Required NOT NULL field
                    'subtotal': round(random.uniform(9.99, 99.99), 2),  # Required NOT NULL field
                    'total_amount': round(random.uniform(9.99, 99.99), 2),  # Required NOT NULL field
                    'currency': 'USD',  # Required NOT NULL field
                    'amount': round(random.uniform(9.99, 99.99), 2),
                    'due_date': datetime.now() + timedelta(days=random.randint(1, 30)),
                    'status': random.choice(['DRAFT', 'SENT', 'PAID', 'OVERDUE']),
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
                })
            
        results['gpt_subscription_invoices'] = insert_data_flexible(session, 'gpt_subscription_invoices', gpt_subscription_invoices_data)
        print(f"    ✅ Created {results['gpt_subscription_invoices']} GPT subscription invoices")
    except Exception as e:
        print(f"    ❌ Error seeding gpt_subscription_invoices: {e}")
        results['gpt_subscription_invoices'] = 0
    
    print("  Seeding gpt_subscription_refunds...")
    try:
        # Get actual GPT subscription and payment IDs
        subscription_result = session.execute(text("SELECT id FROM gpt_subscriptions LIMIT 30"))
        subscription_ids = [row[0] for row in subscription_result.fetchall()]
        
        payment_result = session.execute(text("SELECT id FROM gpt_subscription_payments LIMIT 50"))
        payment_ids = [row[0] for row in payment_result.fetchall()]
        
        if not subscription_ids or not payment_ids:
            print("    ⚠️  No gpt_subscriptions or payments found, skipping gpt_subscription_refunds")
            results['gpt_subscription_refunds'] = 0
        else:
            gpt_subscription_refunds_data = []
            for i in range(10):
                gpt_subscription_refunds_data.append({
                    'subscription_id': random.choice(subscription_ids),  # Use actual subscription IDs
                    'payment_id': random.choice(payment_ids),  # Use actual payment IDs
                    'refund_amount': round(random.uniform(5.00, 50.00), 2),
                    'currency': 'USD',  # Required NOT NULL field
                    'refund_type': random.choice(['FULL', 'PARTIAL', 'CREDIT']),  # Required NOT NULL field
                    'reason': random.choice(['CANCELLATION', 'DISPUTE', 'ERROR', 'CUSTOMER_REQUEST']),  # Required NOT NULL field
                    'refund_reason': random.choice(['CANCELLATION', 'DISPUTE', 'ERROR', 'CUSTOMER_REQUEST']),
                    'requested_at': datetime.now() - timedelta(days=random.randint(1, 30)),  # Required NOT NULL field
                    'refund_date': datetime.now() - timedelta(days=random.randint(1, 30)),
                    'status': random.choice(['PENDING', 'COMPLETED', 'FAILED', 'CANCELLED']),
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
                })
            
            results['gpt_subscription_refunds'] = insert_data_flexible(session, 'gpt_subscription_refunds', gpt_subscription_refunds_data)
            print(f"    ✅ Created {results['gpt_subscription_refunds']} GPT subscription refunds")
    except Exception as e:
        print(f"    ❌ Error seeding gpt_subscription_refunds: {e}")
        results['gpt_subscription_refunds'] = 0
    
    return results

def seed_additional_user_management(session: Session, deps: Dict[str, List[int]]) -> Dict[str, int]:
    """Seed Additional User Management (4 tables)."""
    results = {}
    
    print("  Seeding user_memories...")
    try:
        user_memories_data = []
        for i in range(100):
            user_memories_data.append({
                'user_id': random.choice(deps['user_ids']) if deps['user_ids'] else random.randint(1, 32),
                'memory_type': random.choice(['PREFERENCE', 'BEHAVIOR', 'INTERACTION', 'ACHIEVEMENT']),
                'content': f'Memory content {i+1}',
                'importance': random.randint(1, 10),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
            })
        
        results['user_memories'] = insert_data_flexible(session, 'user_memories', user_memories_data)
        print(f"    ✅ Created {results['user_memories']} user memories")
    except Exception as e:
        print(f"    ❌ Error seeding user_memories: {e}")
        results['user_memories'] = 0
    
    print("  Seeding memory_interactions...")
    try:
        # Get actual user_memories IDs
        memory_result = session.execute(text("SELECT id FROM user_memories "))
        memory_ids = [row[0] for row in memory_result.fetchall()]
        
        if not memory_ids:
            print("    ⚠️  No user_memories found, skipping memory_interactions")
            results['memory_interactions'] = 0
        else:
            memory_interactions_data = []
            for i in range(80):
                memory_interactions_data.append({
                    'memory_id': random.choice(memory_ids),  # Use actual user_memories IDs
                    'interaction_type': random.choice(['VIEW', 'UPDATE', 'DELETE', 'SHARE']),
                    'user_id': random.choice(deps['user_ids']) if deps['user_ids'] else random.randint(1, 32),
                    'created_at': datetime.now() - timedelta(hours=random.randint(1, 24))
                })
            
            results['memory_interactions'] = insert_data_flexible(session, 'memory_interactions', memory_interactions_data)
            print(f"    ✅ Created {results['memory_interactions']} memory interactions")
    except Exception as e:
        print(f"    ❌ Error seeding memory_interactions: {e}")
        results['memory_interactions'] = 0
    
    print("  Seeding instructors...")
    try:
        # Check if instructors already has data and use it
        existing_count = session.execute(text("SELECT COUNT(*) FROM instructors")).scalar()
        if existing_count > 0:
            print(f"    ✅ Found {existing_count} existing instructors, using for foreign key references")
            results['instructors'] = existing_count
        else:
            instructors_data = []
            for i in range(25):
                instructors_data.append({
                    'name': f'Instructor {i+1}',
                    'email': f'instructor{i+1}@example.com',
                    'specialization': random.choice(['PHYSICAL_EDUCATION', 'HEALTH', 'NUTRITION', 'SPORTS']),
                    'certification_level': random.choice(['BASIC', 'INTERMEDIATE', 'ADVANCED', 'EXPERT']),
                    'hire_date': datetime.now() - timedelta(days=random.randint(30, 365)),  # Required NOT NULL field
                    'status': random.choice(['ACTIVE', 'INACTIVE', 'ON_LEAVE', 'TERMINATED']),  # Required NOT NULL field
                    'is_active': random.choice([True, False]),
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                    'updated_at': datetime.now() - timedelta(days=random.randint(1, 7))  # Required NOT NULL field
                })
            
            results['instructors'] = insert_data_flexible(session, 'instructors', instructors_data)
            print(f"    ✅ Created {results['instructors']} instructors")
    except Exception as e:
        print(f"    ❌ Error seeding instructors: {e}")
        results['instructors'] = 0
    
    print("  Seeding grades...")
    try:
        grades_data = []
        for i in range(200):
            grades_data.append({
                'student_id': random.choice(deps['user_ids']) if deps['user_ids'] else random.randint(1, 32),  # Use user_ids instead of student_ids
                'activity_id': random.randint(1, 50),
                'grade': round(random.uniform(0.0, 100.0), 2),
                'grade_type': random.choice(['PARTICIPATION', 'SKILL', 'KNOWLEDGE', 'OVERALL']),
                'comments': f'Grade comments {i+1}',
                'graded_by': random.choice(deps['user_ids']) if deps['user_ids'] else random.randint(1, 32),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
            })
        
        results['grades'] = insert_data_flexible(session, 'grades', grades_data)
        print(f"    ✅ Created {results['grades']} grades")
    except Exception as e:
        print(f"    ❌ Error seeding grades: {e}")
        results['grades'] = 0
    
    print("  Seeding teacher_certification_base...")
    try:
        # Get actual physical education teachers IDs
        teacher_result = session.execute(text("SELECT id FROM physical_education_teachers LIMIT 20"))
        teacher_ids = [row[0] for row in teacher_result.fetchall()]
        
        if not teacher_ids:
            print("    ⚠️  No physical education teachers found, skipping teacher_certification_base")
            results['teacher_certification_base'] = 0
        else:
            teacher_certification_base_data = []
            for i in range(20):
                teacher_certification_base_data.append({
                    'teacher_id': random.choice(teacher_ids),  # Use actual teacher IDs
                    'type': random.choice(['PHYSICAL_EDUCATION']),  # Use only valid enum values
                    'name': f'Certification {i+1}',  # Required NOT NULL field
                    'certification_name': f'Certification {i+1}',
                    'certification_type': random.choice(['PHYSICAL_EDUCATION']),  # Use only valid enum values
                    'issuing_organization': f'Organization {i+1}',
                    'issue_date': datetime.now() - timedelta(days=random.randint(30, 365)),
                    'expiry_date': datetime.now() + timedelta(days=random.randint(365, 1095)),
                    'status': random.choice(['ACTIVE', 'EXPIRED', 'PENDING', 'SUSPENDED']),
                    'updated_at': datetime.now() - timedelta(days=random.randint(1, 7)),  # Required NOT NULL field
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
                })
            
            results['teacher_certification_base'] = insert_data_flexible(session, 'teacher_certification_base', teacher_certification_base_data)
            print(f"    ✅ Created {results['teacher_certification_base']} teacher certification base records")
    except Exception as e:
        print(f"    ❌ Error seeding teacher_certification_base: {e}")
        results['teacher_certification_base'] = 0
    
    print("  Seeding tool_assignments...")
    try:
        # Get actual dashboard tool and user IDs
        tool_result = session.execute(text("SELECT id FROM dashboard_tools LIMIT 20"))
        tool_ids = [row[0] for row in tool_result.fetchall()]
        
        dashboard_user_result = session.execute(text("SELECT id FROM dashboard_users LIMIT 20"))
        dashboard_user_ids = [row[0] for row in dashboard_user_result.fetchall()]
        
        if not tool_ids or not dashboard_user_ids:
            print("    ⚠️  No dashboard tools or users found, skipping tool_assignments")
            results['tool_assignments'] = 0
        else:
            # Check existing tool assignments to avoid unique constraint violations
            existing_result = session.execute(text("SELECT tool_id, user_id FROM tool_assignments"))
            existing_assignments = {(row[0], row[1]) for row in existing_result.fetchall()}
            
            tool_assignments_data = []
            attempts = 0
            max_attempts = 200  # Prevent infinite loop
            
            while len(tool_assignments_data) < 40 and attempts < max_attempts:
                tool_id = random.choice(deps['ai_tool_ids']) if deps['ai_tool_ids'] else random.randint(1, 10)
                user_id = random.choice(dashboard_user_ids)
                
                # Skip if this tool-user combination already exists
                if (tool_id, user_id) not in existing_assignments:
                    tool_assignments_data.append({
                        'tool_id': tool_id,  # Use actual AI tool IDs
                        'user_id': user_id,  # Use actual dashboard user IDs
                        'assigned_by': random.choice(dashboard_user_ids),  # Use actual dashboard user IDs
                        'assigned_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                        'status': random.choice(['ACTIVE', 'INACTIVE', 'PENDING', 'SUSPENDED']),
                        'permissions': json.dumps(['read', 'write', 'admin']),
                        'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
                    })
                    # Add to existing set to avoid duplicates in this batch
                    existing_assignments.add((tool_id, user_id))
                attempts += 1
            
            if tool_assignments_data:
                results['tool_assignments'] = insert_data_flexible(session, 'tool_assignments', tool_assignments_data)
                print(f"    ✅ Created {results['tool_assignments']} tool assignments")
            else:
                print("    ⚠️  All tool-user combinations already exist, skipping tool_assignments")
                results['tool_assignments'] = 0
    except Exception as e:
        print(f"    ❌ Error seeding tool_assignments: {e}")
        results['tool_assignments'] = 0
    
    return results

def seed_analytics_planning(session: Session, deps: Dict[str, List[int]]) -> Dict[str, int]:
    """Seed Analytics & Planning (3 tables)."""
    results = {}
    
    print("  Seeding performance_logs...")
    try:
        performance_logs_data = []
        for i in range(150):
            performance_logs_data.append({
                'user_id': random.choice(deps['user_ids']) if deps['user_ids'] else random.randint(1, 32),
                'activity_id': random.randint(1, 50),
                'component': f'Component_{i+1}',  # Required NOT NULL field
                'operation': random.choice(['CREATE', 'READ', 'UPDATE', 'DELETE', 'SEARCH', 'PROCESS']),  # Required NOT NULL field
                'duration': random.randint(100, 5000),  # Required NOT NULL field
                'status': random.choice(['SUCCESS', 'FAILED', 'PENDING', 'CANCELLED']),  # Required NOT NULL field
                'performance_metric': random.choice(['SPEED', 'ACCURACY', 'ENDURANCE', 'FLEXIBILITY']),
                'value': round(random.uniform(0.0, 100.0), 2),
                'unit': random.choice(['SECONDS', 'PERCENTAGE', 'REPS', 'METERS']),
                'recorded_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
            })
        
        results['performance_logs'] = insert_data_flexible(session, 'performance_logs', performance_logs_data)
        print(f"    ✅ Created {results['performance_logs']} performance logs")
    except Exception as e:
        print(f"    ❌ Error seeding performance_logs: {e}")
        results['performance_logs'] = 0
    
    print("  Seeding security_logs...")
    try:
        security_logs_data = []
        for i in range(100):
            security_logs_data.append({
                'user_id': random.choice(deps['user_ids']) if deps['user_ids'] else random.randint(1, 32),
                'event_type': random.choice(['LOGIN', 'LOGOUT', 'ACCESS_DENIED', 'PASSWORD_CHANGE']),  # Required NOT NULL field
                'severity': random.choice(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']),  # Required NOT NULL field
                'description': f'Security event {i+1}: {random.choice(["User login", "Password change", "Access denied", "Logout"])}',  # Required NOT NULL field
                'action': random.choice(['LOGIN', 'LOGOUT', 'ACCESS_DENIED', 'PASSWORD_CHANGE']),
                'ip_address': f'192.168.1.{random.randint(1, 254)}',
                'user_agent': f'Browser_{random.randint(1, 10)}',
                'success': random.choice([True, False]),
                'created_at': datetime.now() - timedelta(hours=random.randint(1, 24))
            })
        
        results['security_logs'] = insert_data_flexible(session, 'security_logs', security_logs_data)
        print(f"    ✅ Created {results['security_logs']} security logs")
    except Exception as e:
        print(f"    ❌ Error seeding security_logs: {e}")
        results['security_logs'] = 0
    
    print("  Seeding webhooks...")
    try:
        webhooks_data = []
        for i in range(20):
            webhooks_data.append({
                'subscription_id': random.randint(1, 30),  # Required NOT NULL field - reference to gpt_subscriptions
                'name': f'Webhook {i+1}',
                'url': f'https://example.com/webhook/{i+1}',
                'event_type': random.choice(['USER_CREATED', 'ACTIVITY_COMPLETED', 'GRADE_UPDATED']),
                'is_active': random.choice([True, False]),
                'secret_key': f'secret_{i+1}_{random.randint(1000, 9999)}',
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
            })
        
        results['webhooks'] = insert_data_flexible(session, 'webhooks', webhooks_data)
        print(f"    ✅ Created {results['webhooks']} webhooks")
    except Exception as e:
        print(f"    ❌ Error seeding webhooks: {e}")
        results['webhooks'] = 0
    
    print("  Seeding planning_history...")
    try:
        # Get actual activity plans IDs
        plan_result = session.execute(text("SELECT id FROM activity_plans_planning LIMIT 20"))
        plan_ids = [row[0] for row in plan_result.fetchall()]
        
        if not plan_ids:
            print("    ⚠️  No activity plans found, skipping planning_history")
            results['planning_history'] = 0
        else:
            planning_history_data = []
            for i in range(60):
                planning_history_data.append({
                    'plan_id': random.choice(plan_ids),  # Use actual plan IDs
                    'plan_name': f'Plan {i+1}',
                    'plan_type': random.choice(['LESSON', 'CURRICULUM', 'ASSESSMENT', 'ACTIVITY']),
                    'action': random.choice(['CREATED', 'UPDATED', 'DELETED', 'ARCHIVED']),
                    'changes': json.dumps({'field': 'description', 'old_value': 'old', 'new_value': 'new'}),
                    'history_date': datetime.now() - timedelta(days=random.randint(1, 30)),  # Required NOT NULL field
                    'history_type': random.choice(['CREATE', 'UPDATE', 'DELETE', 'ARCHIVE']),  # Required NOT NULL field
                    'updated_at': datetime.now() - timedelta(days=random.randint(1, 7)),  # Required NOT NULL field
                    'user_id': random.choice(deps['user_ids']) if deps['user_ids'] else random.randint(1, 32),
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
                })
            
            results['planning_history'] = insert_data_flexible(session, 'planning_history', planning_history_data)
            print(f"    ✅ Created {results['planning_history']} planning history records")
    except Exception as e:
        print(f"    ❌ Error seeding planning_history: {e}")
        results['planning_history'] = 0
    
    print("  Seeding planning_metrics...")
    try:
        # Get actual activity plans IDs
        plan_result = session.execute(text("SELECT id FROM activity_plans_planning LIMIT 20"))
        plan_ids = [row[0] for row in plan_result.fetchall()]
        
        if not plan_ids:
            print("    ⚠️  No activity plans found, skipping planning_metrics")
            results['planning_metrics'] = 0
        else:
            planning_metrics_data = []
            for i in range(40):
                planning_metrics_data.append({
                    'plan_id': random.choice(plan_ids),  # Use actual plan IDs
                    'metric_name': f'Metric {i+1}',
                    'metric_value': round(random.uniform(0.0, 100.0), 2),
                    'metric_type': random.choice(['PERCENTAGE', 'COUNT', 'DURATION', 'SCORE']),
                    'metric_date': datetime.now() - timedelta(days=random.randint(1, 30)),  # Required NOT NULL field
                    'measurement_date': datetime.now() - timedelta(days=random.randint(1, 30)),
                    'updated_at': datetime.now() - timedelta(days=random.randint(1, 7)),  # Required NOT NULL field
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
                })
            
            results['planning_metrics'] = insert_data_flexible(session, 'planning_metrics', planning_metrics_data)
            print(f"    ✅ Created {results['planning_metrics']} planning metrics")
    except Exception as e:
        print(f"    ❌ Error seeding planning_metrics: {e}")
        results['planning_metrics'] = 0
    
    print("  Seeding health_fitness_goal_progress...")
    try:
        # Get actual goals and students IDs
        goal_result = session.execute(text("SELECT id FROM goals LIMIT 50"))
        goal_ids = [row[0] for row in goal_result.fetchall()]
        
        student_result = session.execute(text("SELECT id FROM students LIMIT 50"))
        student_ids = [row[0] for row in student_result.fetchall()]
        
        if not goal_ids or not student_ids:
            print("    ⚠️  No goals or students found, skipping health_fitness_goal_progress")
            results['health_fitness_goal_progress'] = 0
        else:
            health_fitness_goal_progress_data = []
            for i in range(100):
                health_fitness_goal_progress_data.append({
                    'goal_id': random.choice(goal_ids),  # Use actual goal IDs
                    'student_id': random.choice(student_ids),  # Use actual student IDs
                    'progress_value': round(random.uniform(0.0, 100.0), 2),
                    'progress_percentage': round(random.uniform(0.0, 100.0), 2),  # Required NOT NULL field
                    'progress_date': datetime.now() - timedelta(days=random.randint(1, 30)),
                    'status': random.choice(BASE_STATUS_VALUES),  # Required NOT NULL field
                    'notes': f'Progress notes {i+1}',
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
                })
            
            results['health_fitness_goal_progress'] = insert_data_flexible(session, 'health_fitness_goal_progress', health_fitness_goal_progress_data)
            print(f"    ✅ Created {results['health_fitness_goal_progress']} health fitness goal progress records")
    except Exception as e:
        print(f"    ❌ Error seeding health_fitness_goal_progress: {e}")
        results['health_fitness_goal_progress'] = 0
    
    return results

def seed_phase11_advanced_system_features(session: Session, deps: Dict[str, List[int]] = None) -> Dict[str, int]:
    """Main function to seed all Phase 11 advanced system features."""
    print("🚀 PHASE 11: ADVANCED SYSTEM FEATURES")
    print("=" * 80)
    print("📊 Seeding 73 tables for advanced system functionality")
    print("🔧 Performance & Caching, Dashboard UI, Project Management")
    print("💬 Communication, Resource Management, Billing & More")
    print("=" * 80)
    
    # Get dependency IDs
    if deps is None:
        print("🔍 Retrieving dependency IDs...")
        deps = get_dependency_ids(session)
        print(f"✅ Retrieved dependency IDs: {len(deps['user_ids'])} users, {len(deps['student_ids'])} students, {len(deps['org_ids'])} organizations")
    else:
        print(f"✅ Using provided dependency IDs: {len(deps['user_ids'])} users, {len(deps['student_ids'])} students, {len(deps['org_ids'])} organizations")
    
    all_results = {}
    
    # 11.1 Performance & Caching System
    print("\n🔧 11.1 PERFORMANCE & CACHING SYSTEM")
    print("-" * 50)
    caching_results = seed_performance_caching_system(session, deps)
    all_results.update(caching_results)
    
    # 11.2 Dashboard & UI Enhancement
    print("\n🎨 11.2 DASHBOARD & UI ENHANCEMENT")
    print("-" * 50)
    dashboard_results = seed_dashboard_ui_enhancement(session, deps)
    all_results.update(dashboard_results)
    
    # 11.3 Competition & Events System
    print("\n🏆 11.3 COMPETITION & EVENTS SYSTEM")
    print("-" * 50)
    competition_results = seed_competition_events_system(session, deps)
    all_results.update(competition_results)
    
    # 11.4 Project Management System
    print("\n📋 11.4 PROJECT MANAGEMENT SYSTEM")
    print("-" * 50)
    project_results = seed_project_management_system(session, deps)
    all_results.update(project_results)
    
    # 11.5 Resource Management System
    print("\n⚡ 11.5 RESOURCE MANAGEMENT SYSTEM")
    print("-" * 50)
    resource_results = seed_resource_management_system(session, deps)
    all_results.update(resource_results)
    
    # 11.6 Communication & Feedback System
    print("\n💬 11.6 COMMUNICATION & FEEDBACK SYSTEM")
    print("-" * 50)
    communication_results = seed_communication_feedback_system(session, deps)
    all_results.update(communication_results)
    
    # 11.7 Core System Integration
    print("\n🔗 11.7 CORE SYSTEM INTEGRATION")
    print("-" * 50)
    core_results = seed_core_system_integration(session, deps)
    all_results.update(core_results)
    
    # 11.8 Billing & Subscription System
    print("\n💰 11.8 BILLING & SUBSCRIPTION SYSTEM")
    print("-" * 50)
    billing_results = seed_billing_subscription_system(session, deps)
    all_results.update(billing_results)
    
    # 11.9 Additional User Management
    print("\n👨‍🏫 11.9 ADDITIONAL USER MANAGEMENT")
    print("-" * 50)
    user_results = seed_additional_user_management(session, deps)
    all_results.update(user_results)
    
    # 11.10 Analytics & Planning
    print("\n📈 11.10 ANALYTICS & PLANNING")
    print("-" * 50)
    analytics_results = seed_analytics_planning(session, deps)
    all_results.update(analytics_results)
    
    print("\n" + "=" * 80)
    print("🎉 PHASE 11 ADVANCED SYSTEM FEATURES COMPLETE!")
    print("=" * 80)
    print(f"📊 Total records created: {sum(all_results.values()):,}")
    print(f"📋 Tables processed: {len(all_results)}")
    print(f"✅ Successfully populated: {len([k for k, v in all_results.items() if v > 0])} tables")
    print(f"🏆 Phase 11 completion: {len([k for k, v in all_results.items() if v > 0])}/{len(all_results)} tables")
    print("=" * 80)
    
    return all_results

if __name__ == "__main__":
    from app.core.database import SessionLocal
    
    session = SessionLocal()
    try:
        results = seed_phase11_advanced_system_features(session)
        session.commit()
        print(f"\n🎉 Phase 11 completed successfully!")
        print(f"📊 Total records created: {sum(results.values()):,}")
        print(f"📋 Tables processed: {len(results)}")
        print(f"✅ Successfully populated: {len([k for k, v in results.items() if v > 0])} tables")
    except Exception as e:
        print(f"\n❌ Phase 11 failed: {e}")
        session.rollback()
        import traceback
        traceback.print_exc()
    finally:
        session.close()
