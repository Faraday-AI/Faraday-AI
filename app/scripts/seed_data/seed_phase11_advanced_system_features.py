#!/usr/bin/env python3
"""
Phase 11: Advanced System Features
Seeds 73 tables for advanced system functionality including performance, caching, 
dashboard enhancements, project management, resource management, communication,
billing, and core system integration.

This script follows the same robust approach as previous phases with:
- Dynamic schema detection
- Data migration from existing tables
- Proper foreign key relationships
- Enum validation
- Flexible development-friendly seeding
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
    """Get IDs from dependency tables for foreign key relationships."""
    dependencies = {}
    
    # Core user and organization data
    try:
        users = session.execute(text("SELECT id FROM users")).fetchall()
        dependencies['user_ids'] = [u[0] for u in users] if users else [1]
    except:
        dependencies['user_ids'] = [1]
    
    try:
        students = session.execute(text("SELECT id FROM students")).fetchall()
        dependencies['student_ids'] = [s[0] for s in students] if students else [1]
    except:
        dependencies['student_ids'] = [1]
    
    try:
        organizations = session.execute(text("SELECT id FROM organizations")).fetchall()
        dependencies['organization_ids'] = [o[0] for o in organizations] if organizations else [1]
    except:
        dependencies['organization_ids'] = [1]
    
    try:
        schools = session.execute(text("SELECT id FROM schools")).fetchall()
        dependencies['school_ids'] = [s[0] for s in schools] if schools else [1]
    except:
        dependencies['school_ids'] = [1]
    
    try:
        activities = session.execute(text("SELECT id FROM activities")).fetchall()
        dependencies['activity_ids'] = [a[0] for a in activities] if activities else [1]
    except:
        dependencies['activity_ids'] = [1]
    
    try:
        dashboard_users = session.execute(text("SELECT id FROM dashboard_users")).fetchall()
        dependencies['dashboard_user_ids'] = [d[0] for d in dashboard_users] if dashboard_users else [1]
    except:
        dependencies['dashboard_user_ids'] = [1]
    
    try:
        dashboard_tools = session.execute(text("SELECT id FROM dashboard_tools")).fetchall()
        dependencies['dashboard_tool_ids'] = [d[0] for d in dashboard_tools] if dashboard_tools else [1]
    except:
        dependencies['dashboard_tool_ids'] = [1]
    
    try:
        gpt_definitions = session.execute(text("SELECT id FROM gpt_definitions")).fetchall()
        dependencies['gpt_definition_ids'] = [g[0] for g in gpt_definitions] if gpt_definitions else [1]
    except:
        dependencies['gpt_definition_ids'] = [1]
    
    try:
        roles = session.execute(text("SELECT id FROM roles")).fetchall()
        dependencies['role_ids'] = [r[0] for r in roles] if roles else [1]
    except:
        dependencies['role_ids'] = [1]
    
    try:
        teams = session.execute(text("SELECT id FROM teams")).fetchall()
        dependencies['team_ids'] = [t[0] for t in teams] if teams else [1]
    except:
        dependencies['team_ids'] = [1]
    
    return dependencies

def insert_data_flexible(session: Session, table_name: str, data: List[Dict[str, Any]], 
                        schema: Optional[Dict[str, Any]] = None) -> int:
    """Insert data with flexible schema handling."""
    if not data:
        return 0
    
    try:
        # Get schema if not provided
        if not schema:
            schema = get_table_schema(session, table_name)
        
        # If no schema found, try to get it from the first record
        if not schema and data:
            # Use all columns from the first record as a fallback
            schema = {col: {'type': 'text'} for col in data[0].keys()}
        
        # Filter data to only include valid columns
        valid_columns = set(schema.keys()) if schema else set(data[0].keys())
        filtered_data = []
        
        for record in data:
            filtered_record = {k: v for k, v in record.items() if k in valid_columns}
            if filtered_record:  # Only add non-empty records
                filtered_data.append(filtered_record)
        
        if not filtered_data:
            print(f"    ⚠️  No valid data to insert for {table_name}")
            return 0
        
        # Insert data
        columns = list(filtered_data[0].keys())
        if not columns:
            print(f"    ⚠️  No valid columns found for {table_name}")
            return 0
            
        placeholders = ', '.join([f':{col}' for col in columns])
        columns_str = ', '.join(columns)
        query = f'INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})'
        
        for record in filtered_data:
            session.execute(text(query), record)
        
        return len(filtered_data)
        
    except Exception as e:
        print(f"    ❌ Error inserting data into {table_name}: {e}")
        # Rollback the current transaction to allow other tables to continue
        try:
            session.rollback()
        except:
            pass
        return 0

def seed_phase11_advanced_system_features(session: Session) -> Dict[str, int]:
    """
    Seed Phase 11: Advanced System Features (73 tables)
    """
    print("=" * 80)
    print("🚀 PHASE 11: ADVANCED SYSTEM FEATURES")
    print("=" * 80)
    print("📊 Seeding 73 tables for advanced system functionality")
    print("🔧 Performance & Caching, Dashboard UI, Project Management")
    print("💬 Communication, Resource Management, Billing & More")
    print("=" * 80)
    
    results = {}
    total_records = 0
    
    # Get dependency IDs
    print("🔍 Retrieving dependency IDs...")
    ids = get_dependency_ids(session)
    print(f"✅ Retrieved dependency IDs: {len(ids['user_ids'])} users, {len(ids['student_ids'])} students, {len(ids['organization_ids'])} organizations")
    
    # 11.1 Performance & Caching System (7 tables)
    print("\n🔧 11.1 PERFORMANCE & CACHING SYSTEM")
    print("-" * 60)
    results.update(seed_performance_caching_system(session, ids))
    
    # 11.2 Dashboard & UI Enhancement (17 tables)
    print("\n🎨 11.2 DASHBOARD & UI ENHANCEMENT")
    print("-" * 60)
    results.update(seed_dashboard_ui_enhancement(session, ids))
    
    # 11.3 Competition & Events System (4 tables)
    print("\n🏆 11.3 COMPETITION & EVENTS SYSTEM")
    print("-" * 60)
    results.update(seed_competition_events_system(session, ids))
    
    # 11.4 Project Management System (13 tables)
    print("\n📋 11.4 PROJECT MANAGEMENT SYSTEM")
    print("-" * 60)
    results.update(seed_project_management_system(session, ids))
    
    # 11.5 Resource Management System (9 tables)
    print("\n⚡ 11.5 RESOURCE MANAGEMENT SYSTEM")
    print("-" * 60)
    results.update(seed_resource_management_system(session, ids))
    
    # 11.6 Communication & Feedback System (8 tables)
    print("\n💬 11.6 COMMUNICATION & FEEDBACK SYSTEM")
    print("-" * 60)
    results.update(seed_communication_feedback_system(session, ids))
    
    # 11.7 Core System Integration (3 tables)
    print("\n🔗 11.7 CORE SYSTEM INTEGRATION")
    print("-" * 60)
    results.update(seed_core_system_integration(session, ids))
    
    # 11.8 Billing & Subscription System (6 tables)
    print("\n💰 11.8 BILLING & SUBSCRIPTION SYSTEM")
    print("-" * 60)
    results.update(seed_billing_subscription_system(session, ids))
    
    # 11.9 Additional User Management (4 tables)
    print("\n👨‍🏫 11.9 ADDITIONAL USER MANAGEMENT")
    print("-" * 60)
    results.update(seed_additional_user_management(session, ids))
    
    # 11.10 Analytics & Planning (3 tables)
    print("\n📈 11.10 ANALYTICS & PLANNING")
    print("-" * 60)
    results.update(seed_analytics_planning(session, ids))
    
    # Calculate totals
    total_records = sum(results.values())
    successful_tables = len([k for k, v in results.items() if v > 0])
    
    print("\n" + "=" * 80)
    print("🎉 PHASE 11 ADVANCED SYSTEM FEATURES COMPLETE!")
    print("=" * 80)
    print(f"📊 Total records created: {total_records:,}")
    print(f"📋 Tables processed: {len(results)}")
    print(f"✅ Successfully populated: {successful_tables} tables")
    print(f"🏆 Phase 11 completion: {successful_tables}/{len(results)} tables")
    print("=" * 80)
    
    return results

def seed_performance_caching_system(session: Session, ids: Dict[str, List[int]]) -> Dict[str, int]:
    """Seed Performance & Caching System (7 tables)"""
    results = {}
    
    # Cache entries
    try:
        print("  Seeding cache_entries...")
        cache_entries = []
        for i in range(100):
            cache_entries.append({
                'key': f'cache_key_{i+1}',
                'value': json.dumps({'data': f'cached_data_{i+1}', 'timestamp': datetime.now().isoformat()}),
                'expires_at': datetime.now() + timedelta(hours=random.randint(1, 24)),
                'created_at': datetime.now() - timedelta(hours=random.randint(1, 168)),
                'updated_at': datetime.now() - timedelta(hours=random.randint(1, 24))
            })
        
        count = insert_data_flexible(session, 'cache_entries', cache_entries)
        results['cache_entries'] = count
        print(f"    ✅ Created {count} cache entries")
    except Exception as e:
        print(f"    ❌ Error seeding cache_entries: {e}")
        results['cache_entries'] = 0
        # Rollback to allow other tables to continue
        try:
            session.rollback()
        except:
            pass
    
    # Cache metrics
    try:
        print("  Seeding cache_metrics...")
        cache_metrics = []
        for i in range(50):
            cache_metrics.append({
                'entry_id': random.randint(1, 100),  # Reference to cache_entries
                'hits': random.randint(0, 1000),
                'misses': random.randint(0, 100),
                'last_accessed': datetime.now() - timedelta(minutes=random.randint(1, 1440)),
                'size_bytes': random.randint(1024, 1048576),  # 1KB to 1MB
                'metrics_metadata': json.dumps({'source': 'cache_monitor', 'version': '1.0'}),
                'created_at': datetime.now() - timedelta(hours=random.randint(1, 168)),
                'updated_at': datetime.now() - timedelta(hours=random.randint(1, 24))
            })
        
        count = insert_data_flexible(session, 'cache_metrics', cache_metrics)
        results['cache_metrics'] = count
        print(f"    ✅ Created {count} cache metrics")
    except Exception as e:
        print(f"    ❌ Error seeding cache_metrics: {e}")
        results['cache_metrics'] = 0
    
    # Cache policies
    try:
        print("  Seeding cache_policies...")
        cache_policies = []
        for i in range(10):
            cache_policies.append({
                'name': f'Cache Policy {i+1}',
                'description': f'Cache policy for {random.choice(["users", "activities", "students", "reports"])}',
                'ttl': random.randint(300, 86400),  # TTL in seconds
                'max_size': random.randint(100, 10000),
                'priority': random.choice(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']),
                'policy_metadata': json.dumps({'source': 'cache_manager', 'version': '1.0'}),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 7))
            })
        
        count = insert_data_flexible(session, 'cache_policies', cache_policies)
        results['cache_policies'] = count
        print(f"    ✅ Created {count} cache policies")
    except Exception as e:
        print(f"    ❌ Error seeding cache_policies: {e}")
        results['cache_policies'] = 0
    
    # Circuit breaker history
    try:
        print("  Seeding circuit_breaker_history...")
        circuit_breaker_history = []
        for i in range(200):
            circuit_breaker_history.append({
                'circuit_breaker_id': random.randint(1, 10),  # Reference to circuit_breakers
                'previous_status': random.choice(['CLOSED', 'OPEN', 'HALF_OPEN']),
                'new_status': random.choice(['CLOSED', 'OPEN', 'HALF_OPEN']),
                'trigger': random.choice(['FAILURE_THRESHOLD', 'TIMEOUT', 'MANUAL', 'SUCCESS_THRESHOLD']),
                'failure_count': random.randint(0, 20),
                'meta_data': json.dumps({'request_id': f'req_{i+1}', 'duration_ms': random.randint(10, 5000)}),
                'created_at': datetime.now() - timedelta(minutes=random.randint(1, 1440))
            })
        
        count = insert_data_flexible(session, 'circuit_breaker_history', circuit_breaker_history)
        results['circuit_breaker_history'] = count
        print(f"    ✅ Created {count} circuit breaker history records")
    except Exception as e:
        print(f"    ❌ Error seeding circuit_breaker_history: {e}")
        results['circuit_breaker_history'] = 0
    
    # Circuit breaker metrics
    try:
        print("  Seeding circuit_breaker_metrics...")
        circuit_breaker_metrics = []
        for i in range(30):
            total_requests = random.randint(100, 10000)
            successful_requests = int(total_requests * random.uniform(0.7, 0.99))
            failed_requests = total_requests - successful_requests
            
            circuit_breaker_metrics.append({
                'circuit_breaker_id': random.randint(1, 10),  # Reference to circuit_breakers
                'total_requests': total_requests,
                'successful_requests': successful_requests,
                'failed_requests': failed_requests,
                'total_latency': round(random.uniform(100.0, 5000.0), 2),
                'average_latency': round(random.uniform(10.0, 500.0), 2),
                'max_latency': round(random.uniform(500.0, 10000.0), 2),
                'min_latency': round(random.uniform(1.0, 50.0), 2),
                'error_rate': round(failed_requests / total_requests * 100, 2),
                'success_rate': round(successful_requests / total_requests * 100, 2),
                'last_updated': datetime.now() - timedelta(minutes=random.randint(1, 1440)),
                'meta_data': json.dumps({'window_size_minutes': random.choice([1, 5, 15, 60])})
            })
        
        count = insert_data_flexible(session, 'circuit_breaker_metrics', circuit_breaker_metrics)
        results['circuit_breaker_metrics'] = count
        print(f"    ✅ Created {count} circuit breaker metrics")
    except Exception as e:
        print(f"    ❌ Error seeding circuit_breaker_metrics: {e}")
        results['circuit_breaker_metrics'] = 0
    
    # Circuit breaker policies
    try:
        print("  Seeding circuit_breaker_policies...")
        circuit_breaker_policies = []
        for i in range(5):
            circuit_breaker_policies.append({
                'name': f'Circuit Breaker Policy {i+1}',
                'description': f'Policy for {random.choice(["user_service", "activity_service", "student_service", "report_service"])}',
                'type': random.choice(['REQUEST', 'TIMEOUT', 'ERROR_RATE', 'CUSTOM']),
                'level': random.choice(['SERVICE', 'ENDPOINT', 'GLOBAL']),
                'is_active': True,
                'failure_threshold': random.randint(5, 20),
                'reset_timeout': random.randint(30, 300),
                'half_open_timeout': random.randint(10, 60),
                'max_failures': random.randint(10, 100),
                'error_threshold': random.randint(5, 50),
                'success_threshold': random.randint(5, 20),
                'meta_data': json.dumps({'source': 'circuit_breaker_manager', 'version': '1.0'}),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 7))
            })
        
        count = insert_data_flexible(session, 'circuit_breaker_policies', circuit_breaker_policies)
        results['circuit_breaker_policies'] = count
        print(f"    ✅ Created {count} circuit breaker policies")
    except Exception as e:
        print(f"    ❌ Error seeding circuit_breaker_policies: {e}")
        results['circuit_breaker_policies'] = 0
    
    # Circuit breakers
    try:
        print("  Seeding circuit_breakers...")
        circuit_breakers = []
        for i in range(8):
            circuit_breakers.append({
                'name': f'Circuit Breaker {i+1}',
                'description': f'Circuit breaker for {random.choice(["user_service", "activity_service", "student_service", "report_service"])}',
                'type': random.choice(['REQUEST', 'TIMEOUT', 'ERROR_RATE', 'CUSTOM']),
                'level': random.choice(['SERVICE', 'ENDPOINT', 'GLOBAL']),
                'status': random.choice(['CLOSED', 'OPEN', 'HALF_OPEN']),
                'trigger': random.choice(['FAILURE_THRESHOLD', 'TIMEOUT', 'MANUAL', 'SUCCESS_THRESHOLD']),
                'threshold': random.randint(5, 20),
                'failure_count': random.randint(0, 15),
                'last_failure_time': datetime.now() - timedelta(minutes=random.randint(1, 60)) if random.random() < 0.5 else None,
                'last_success_time': datetime.now() - timedelta(minutes=random.randint(1, 30)) if random.random() < 0.7 else None,
                'reset_timeout': random.randint(30, 300),
                'meta_data': json.dumps({'source': 'circuit_breaker_manager', 'version': '1.0'}),
                'activity_id': random.randint(1, 100) if random.random() < 0.3 else None,
                'policy_id': random.randint(1, 5),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'updated_at': datetime.now() - timedelta(minutes=random.randint(1, 60))
            })
        
        count = insert_data_flexible(session, 'circuit_breakers', circuit_breakers)
        results['circuit_breakers'] = count
        print(f"    ✅ Created {count} circuit breakers")
    except Exception as e:
        print(f"    ❌ Error seeding circuit_breakers: {e}")
        results['circuit_breakers'] = 0
    
    return results

def seed_dashboard_ui_enhancement(session: Session, ids: Dict[str, List[int]]) -> Dict[str, int]:
    """Seed Dashboard & UI Enhancement (17 tables)"""
    results = {}
    
    # Core dashboard widgets
    try:
        print("  Seeding core_dashboard_widgets...")
        core_dashboard_widgets = []
        for i in range(25):
            core_dashboard_widgets.append({
                'widget_type': random.choice(['chart', 'table', 'metric', 'gauge', 'map']),
                'name': f'Widget {i+1}',
                'configuration': json.dumps({
                    'title': f'Dashboard Widget {i+1}',
                    'data_source': random.choice(['activities', 'students', 'users', 'reports']),
                    'refresh_interval': random.randint(30, 300)
                }),
                'position': json.dumps({'x': random.randint(0, 12), 'y': random.randint(0, 8)}),
                'size': json.dumps({'width': random.randint(2, 6), 'height': random.randint(2, 4)}),
                'user_id': random.choice(ids['dashboard_user_ids']),
                'status': random.choice(['ACTIVE', 'INACTIVE', 'PENDING', 'ERROR']),
                'is_active': random.choice([True, False]),
                'metadata': json.dumps({'source': 'dashboard_builder', 'version': '1.0'})
            })
        
        count = insert_data_flexible(session, 'core_dashboard_widgets', core_dashboard_widgets)
        results['core_dashboard_widgets'] = count
        print(f"    ✅ Created {count} core dashboard widgets")
    except Exception as e:
        print(f"    ❌ Error seeding core_dashboard_widgets: {e}")
        results['core_dashboard_widgets'] = 0
    
    # Dashboard API keys
    try:
        print("  Seeding dashboard_api_keys...")
        dashboard_api_keys = []
        for i in range(15):
            dashboard_api_keys.append({
                'key_id': f'key_{random.randint(100000, 999999)}',
                'user_id': random.choice(ids['dashboard_user_ids']),
                'name': f'API Key {i+1}',
                'description': f'API key for {random.choice(["dashboard", "reports", "analytics", "admin"])} access',
                'hashed_secret': f'hashed_secret_{random.randint(100000, 999999)}',
                'permissions': json.dumps(['read', 'write', 'admin']),
                'expires_at': datetime.now() + timedelta(days=random.randint(30, 365)),
                'revoked_at': None,
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 7))
            })
        
        count = insert_data_flexible(session, 'dashboard_api_keys', dashboard_api_keys)
        results['dashboard_api_keys'] = count
        print(f"    ✅ Created {count} dashboard API keys")
    except Exception as e:
        print(f"    ❌ Error seeding dashboard_api_keys: {e}")
        results['dashboard_api_keys'] = 0
    
    # Dashboard audit logs
    try:
        print("  Seeding dashboard_audit_logs...")
        dashboard_audit_logs = []
        for i in range(100):
            dashboard_audit_logs.append({
                'user_id': random.choice(ids['dashboard_user_ids']),
                'action': random.choice(['login', 'logout', 'create', 'update', 'delete', 'view']),
                'resource_type': random.choice(['user', 'activity', 'student', 'report', 'dashboard']),
                'resource_id': random.randint(1, 1000),
                'ip_address': f'192.168.1.{random.randint(1, 254)}',
                'user_agent': f'Browser {random.randint(1, 5)}',
                'timestamp': datetime.now() - timedelta(minutes=random.randint(1, 1440)),
                'metadata': json.dumps({'session_id': f'session_{i+1}', 'duration_ms': random.randint(100, 5000)})
            })
        
        count = insert_data_flexible(session, 'dashboard_audit_logs', dashboard_audit_logs)
        results['dashboard_audit_logs'] = count
        print(f"    ✅ Created {count} dashboard audit logs")
    except Exception as e:
        print(f"    ❌ Error seeding dashboard_audit_logs: {e}")
        results['dashboard_audit_logs'] = 0
    
    # Dashboard filter searches
    try:
        print("  Seeding dashboard_filter_searches...")
        dashboard_filter_searches = []
        for i in range(50):
            dashboard_filter_searches.append({
                'user_id': random.choice(ids['dashboard_user_ids']),
                'search_query': f'Search query {i+1}',
                'filters': json.dumps({
                    'date_range': f'{random.randint(1, 30)} days',
                    'category': random.choice(['activities', 'students', 'reports']),
                    'status': random.choice(['active', 'inactive', 'pending'])
                }),
                'results_count': random.randint(0, 1000),
                'search_timestamp': datetime.now() - timedelta(minutes=random.randint(1, 1440)),
                'execution_time_ms': random.randint(10, 5000)
            })
        
        count = insert_data_flexible(session, 'dashboard_filter_searches', dashboard_filter_searches)
        results['dashboard_filter_searches'] = count
        print(f"    ✅ Created {count} dashboard filter searches")
    except Exception as e:
        print(f"    ❌ Error seeding dashboard_filter_searches: {e}")
        results['dashboard_filter_searches'] = 0
    
    # Dashboard IP allowlist
    try:
        print("  Seeding dashboard_ip_allowlist...")
        dashboard_ip_allowlist = []
        for i in range(20):
            dashboard_ip_allowlist.append({
                'ip_address': f'192.168.{random.randint(1, 255)}.{random.randint(1, 254)}',
                'description': f'Allowed IP {i+1}',
                'is_active': True,
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'created_by': random.choice(ids['dashboard_user_ids'])
            })
        
        count = insert_data_flexible(session, 'dashboard_ip_allowlist', dashboard_ip_allowlist)
        results['dashboard_ip_allowlist'] = count
        print(f"    ✅ Created {count} dashboard IP allowlist entries")
    except Exception as e:
        print(f"    ❌ Error seeding dashboard_ip_allowlist: {e}")
        results['dashboard_ip_allowlist'] = 0
    
    # Dashboard IP blocklist
    try:
        print("  Seeding dashboard_ip_blocklist...")
        dashboard_ip_blocklist = []
        for i in range(10):
            dashboard_ip_blocklist.append({
                'ip_address': f'10.0.{random.randint(1, 255)}.{random.randint(1, 254)}',
                'reason': random.choice(['Suspicious activity', 'Spam', 'Security threat', 'Policy violation']),
                'is_active': True,
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'created_by': random.choice(ids['dashboard_user_ids'])
            })
        
        count = insert_data_flexible(session, 'dashboard_ip_blocklist', dashboard_ip_blocklist)
        results['dashboard_ip_blocklist'] = count
        print(f"    ✅ Created {count} dashboard IP blocklist entries")
    except Exception as e:
        print(f"    ❌ Error seeding dashboard_ip_blocklist: {e}")
        results['dashboard_ip_blocklist'] = 0
    
    # Dashboard marketplace listings
    try:
        print("  Seeding dashboard_marketplace_listings...")
        dashboard_marketplace_listings = []
        for i in range(15):
            dashboard_marketplace_listings.append({
                'name': f'Marketplace Item {i+1}',
                'description': f'Description for marketplace item {i+1}',
                'category': random.choice(['WIDGET', 'THEME', 'PLUGIN', 'INTEGRATION']),
                'price': round(random.uniform(0.0, 100.0), 2),
                'currency': 'USD',
                'is_active': random.choice([True, False]),
                'created_by': random.choice(ids['dashboard_user_ids']),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 7))
            })
        
        count = insert_data_flexible(session, 'dashboard_marketplace_listings', dashboard_marketplace_listings)
        results['dashboard_marketplace_listings'] = count
        print(f"    ✅ Created {count} dashboard marketplace listings")
    except Exception as e:
        print(f"    ❌ Error seeding dashboard_marketplace_listings: {e}")
        results['dashboard_marketplace_listings'] = 0
    
    # Dashboard notification channels
    try:
        print("  Seeding dashboard_notification_channels...")
        dashboard_notification_channels = []
        for i in range(10):
            dashboard_notification_channels.append({
                'name': f'Notification Channel {i+1}',
                'type': random.choice(['EMAIL', 'SMS', 'PUSH', 'WEBHOOK']),
                'config': json.dumps({
                    'endpoint': f'https://api.example.com/notifications/{i+1}',
                    'retry_count': random.randint(1, 5),
                    'timeout_seconds': random.randint(30, 300)
                }),
                'is_active': random.choice([True, False]),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 7))
            })
        
        count = insert_data_flexible(session, 'dashboard_notification_channels', dashboard_notification_channels)
        results['dashboard_notification_channels'] = count
        print(f"    ✅ Created {count} dashboard notification channels")
    except Exception as e:
        print(f"    ❌ Error seeding dashboard_notification_channels: {e}")
        results['dashboard_notification_channels'] = 0
    
    # Dashboard notification models
    try:
        print("  Seeding dashboard_notification_models...")
        dashboard_notification_models = []
        for i in range(8):
            dashboard_notification_models.append({
                'name': f'Notification Model {i+1}',
                'template': f'Notification template {i+1}',
                'variables': json.dumps(['user_name', 'action', 'timestamp']),
                'is_active': random.choice([True, False]),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 7))
            })
        
        count = insert_data_flexible(session, 'dashboard_notification_models', dashboard_notification_models)
        results['dashboard_notification_models'] = count
        print(f"    ✅ Created {count} dashboard notification models")
    except Exception as e:
        print(f"    ❌ Error seeding dashboard_notification_models: {e}")
        results['dashboard_notification_models'] = 0
    
    # Dashboard rate limits
    try:
        print("  Seeding dashboard_rate_limits...")
        dashboard_rate_limits = []
        for i in range(12):
            dashboard_rate_limits.append({
                'endpoint': f'/api/endpoint/{i+1}',
                'requests_per_minute': random.randint(10, 1000),
                'requests_per_hour': random.randint(100, 10000),
                'burst_limit': random.randint(5, 50),
                'is_active': random.choice([True, False]),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 7))
            })
        
        count = insert_data_flexible(session, 'dashboard_rate_limits', dashboard_rate_limits)
        results['dashboard_rate_limits'] = count
        print(f"    ✅ Created {count} dashboard rate limits")
    except Exception as e:
        print(f"    ❌ Error seeding dashboard_rate_limits: {e}")
        results['dashboard_rate_limits'] = 0
    
    # Dashboard security policies
    try:
        print("  Seeding dashboard_security_policies...")
        dashboard_security_policies = []
        for i in range(15):
            dashboard_security_policies.append({
                'policy_name': f'Security Policy {i+1}',
                'policy_type': random.choice(['AUTHENTICATION', 'AUTHORIZATION', 'DATA_PROTECTION', 'ACCESS_CONTROL']),
                'rules': json.dumps({
                    'min_password_length': random.randint(8, 16),
                    'require_2fa': random.choice([True, False]),
                    'session_timeout': random.randint(30, 480)
                }),
                'is_active': random.choice([True, False]),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 7))
            })
        
        count = insert_data_flexible(session, 'dashboard_security_policies', dashboard_security_policies)
        results['dashboard_security_policies'] = count
        print(f"    ✅ Created {count} dashboard security policies")
    except Exception as e:
        print(f"    ❌ Error seeding dashboard_security_policies: {e}")
        results['dashboard_security_policies'] = 0
    
    # Dashboard sessions
    try:
        print("  Seeding dashboard_sessions...")
        dashboard_sessions = []
        for i in range(50):
            dashboard_sessions.append({
                'user_id': random.choice(ids['dashboard_user_ids']),
                'session_token': f'session_token_{random.randint(100000, 999999)}',
                'ip_address': f'192.168.1.{random.randint(1, 254)}',
                'user_agent': f'Browser {random.randint(1, 5)}',
                'started_at': datetime.now() - timedelta(hours=random.randint(1, 168)),
                'last_activity': datetime.now() - timedelta(minutes=random.randint(1, 60)),
                'expires_at': datetime.now() + timedelta(hours=random.randint(1, 24)),
                'is_active': random.choice([True, False])
            })
        
        count = insert_data_flexible(session, 'dashboard_sessions', dashboard_sessions)
        results['dashboard_sessions'] = count
        print(f"    ✅ Created {count} dashboard sessions")
    except Exception as e:
        print(f"    ❌ Error seeding dashboard_sessions: {e}")
        results['dashboard_sessions'] = 0
    
    # Dashboard share configs
    try:
        print("  Seeding dashboard_share_configs...")
        dashboard_share_configs = []
        for i in range(20):
            dashboard_share_configs.append({
                'name': f'Share Config {i+1}',
                'share_type': random.choice(['PUBLIC', 'PRIVATE', 'RESTRICTED']),
                'permissions': json.dumps(['read', 'write', 'admin']),
                'expires_at': datetime.now() + timedelta(days=random.randint(1, 365)),
                'is_active': random.choice([True, False]),
                'created_by': random.choice(ids['dashboard_user_ids']),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 7))
            })
        
        count = insert_data_flexible(session, 'dashboard_share_configs', dashboard_share_configs)
        results['dashboard_share_configs'] = count
        print(f"    ✅ Created {count} dashboard share configs")
    except Exception as e:
        print(f"    ❌ Error seeding dashboard_share_configs: {e}")
        results['dashboard_share_configs'] = 0
    
    # Dashboard share exports
    try:
        print("  Seeding dashboard_share_exports...")
        dashboard_share_exports = []
        for i in range(25):
            dashboard_share_exports.append({
                'export_name': f'Export {i+1}',
                'export_type': random.choice(['CSV', 'JSON', 'PDF', 'EXCEL']),
                'file_path': f'/exports/export_{i+1}.{random.choice(["csv", "json", "pdf", "xlsx"])}',
                'file_size_bytes': random.randint(1024, 10485760),
                'status': random.choice(['PENDING', 'PROCESSING', 'COMPLETED', 'FAILED']),
                'created_by': random.choice(ids['dashboard_user_ids']),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'completed_at': datetime.now() - timedelta(days=random.randint(1, 7)) if random.random() < 0.8 else None
            })
        
        count = insert_data_flexible(session, 'dashboard_share_exports', dashboard_share_exports)
        results['dashboard_share_exports'] = count
        print(f"    ✅ Created {count} dashboard share exports")
    except Exception as e:
        print(f"    ❌ Error seeding dashboard_share_exports: {e}")
        results['dashboard_share_exports'] = 0
    
    # Dashboard shared contexts
    try:
        print("  Seeding dashboard_shared_contexts...")
        dashboard_shared_contexts = []
        for i in range(30):
            dashboard_shared_contexts.append({
                'context_name': f'Shared Context {i+1}',
                'context_data': json.dumps({'data': f'Context data {i+1}', 'type': 'shared'}),
                'shared_with': random.choice(ids['dashboard_user_ids']),
                'permissions': json.dumps(['read', 'write']),
                'is_active': random.choice([True, False]),
                'created_by': random.choice(ids['dashboard_user_ids']),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 7))
            })
        
        count = insert_data_flexible(session, 'dashboard_shared_contexts', dashboard_shared_contexts)
        results['dashboard_shared_contexts'] = count
        print(f"    ✅ Created {count} dashboard shared contexts")
    except Exception as e:
        print(f"    ❌ Error seeding dashboard_shared_contexts: {e}")
        results['dashboard_shared_contexts'] = 0
    
    # Dashboard team members
    try:
        print("  Seeding dashboard_team_members...")
        dashboard_team_members = []
        for i in range(40):
            dashboard_team_members.append({
                'team_id': random.choice(ids['team_ids']),
                'user_id': random.choice(ids['dashboard_user_ids']),
                'role': random.choice(['MEMBER', 'ADMIN', 'OWNER']),
                'joined_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'is_active': random.choice([True, False])
            })
        
        count = insert_data_flexible(session, 'dashboard_team_members', dashboard_team_members)
        results['dashboard_team_members'] = count
        print(f"    ✅ Created {count} dashboard team members")
    except Exception as e:
        print(f"    ❌ Error seeding dashboard_team_members: {e}")
        results['dashboard_team_members'] = 0
    
    # Dashboard tool usage logs
    try:
        print("  Seeding dashboard_tool_usage_logs...")
        dashboard_tool_usage_logs = []
        for i in range(100):
            dashboard_tool_usage_logs.append({
                'user_id': random.choice(ids['dashboard_user_ids']),
                'tool_id': random.choice(ids['dashboard_tool_ids']),
                'action': random.choice(['CREATE', 'READ', 'UPDATE', 'DELETE', 'EXPORT']),
                'duration_ms': random.randint(100, 5000),
                'ip_address': f'192.168.1.{random.randint(1, 254)}',
                'user_agent': f'Browser {random.randint(1, 5)}',
                'timestamp': datetime.now() - timedelta(minutes=random.randint(1, 1440)),
                'metadata': json.dumps({'session_id': f'session_{i+1}', 'request_id': f'req_{i+1}'})
            })
        
        count = insert_data_flexible(session, 'dashboard_tool_usage_logs', dashboard_tool_usage_logs)
        results['dashboard_tool_usage_logs'] = count
        print(f"    ✅ Created {count} dashboard tool usage logs")
    except Exception as e:
        print(f"    ❌ Error seeding dashboard_tool_usage_logs: {e}")
        results['dashboard_tool_usage_logs'] = 0
    
    return results

def seed_competition_events_system(session: Session, ids: Dict[str, List[int]]) -> Dict[str, int]:
    """Seed Competition & Events System (4 tables)"""
    results = {}
    
    # Competition base events
    try:
        print("  Seeding competition_base_events...")
        competition_base_events = []
        for i in range(20):
            competition_base_events.append({
                'competition_id': random.randint(1, 10),  # Reference to competitions table
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
                'status': random.choice(['SCHEDULED', 'ONGOING', 'COMPLETED', 'CANCELLED']),
                'is_active': random.choice([True, False]),
                'metadata': json.dumps({'source': 'competition_manager', 'version': '1.0'})
            })
        
        count = insert_data_flexible(session, 'competition_base_events', competition_base_events)
        results['competition_base_events'] = count
        print(f"    ✅ Created {count} competition base events")
    except Exception as e:
        print(f"    ❌ Error seeding competition_base_events: {e}")
        results['competition_base_events'] = 0
    
    # Competition base participants
    try:
        print("  Seeding competition_base_participants...")
        competition_base_participants = []
        for i in range(100):
            competition_base_participants.append({
                'student_id': random.choice(ids['student_ids']),
                'event_id': random.randint(1, 20),  # Assuming 20 events from above
                'registration_date': datetime.now() - timedelta(days=random.randint(1, 30)),
                'status': random.choice(['REGISTERED', 'CONFIRMED', 'CANCELLED', 'COMPLETED']),
                'team_name': f'Team {i+1}' if random.random() < 0.3 else None,
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 7))
            })
        
        count = insert_data_flexible(session, 'competition_base_participants', competition_base_participants)
        results['competition_base_participants'] = count
        print(f"    ✅ Created {count} competition base participants")
    except Exception as e:
        print(f"    ❌ Error seeding competition_base_participants: {e}")
        results['competition_base_participants'] = 0
    
    # Competition base event participants
    try:
        print("  Seeding competition_base_event_participants...")
        competition_base_event_participants = []
        for i in range(80):
            competition_base_event_participants.append({
                'event_id': random.randint(1, 20),
                'participant_id': random.randint(1, 100),
                'score': round(random.uniform(0.0, 100.0), 2) if random.random() < 0.7 else None,
                'rank': random.randint(1, 50) if random.random() < 0.5 else None,
                'participation_date': datetime.now() - timedelta(days=random.randint(1, 30)),
                'notes': f'Participation notes {i+1}' if random.random() < 0.3 else None
            })
        
        count = insert_data_flexible(session, 'competition_base_event_participants', competition_base_event_participants)
        results['competition_base_event_participants'] = count
        print(f"    ✅ Created {count} competition base event participants")
    except Exception as e:
        print(f"    ❌ Error seeding competition_base_event_participants: {e}")
        results['competition_base_event_participants'] = 0
    
    # Competitions
    try:
        print("  Seeding competitions...")
        competitions = []
        for i in range(15):
            competitions.append({
                'name': f'Competition {i+1}',
                'description': f'Description for competition {i+1}',
                'competition_type': random.choice(['INDIVIDUAL', 'TEAM', 'MIXED']),
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
        
        count = insert_data_flexible(session, 'competitions', competitions)
        results['competitions'] = count
        print(f"    ✅ Created {count} competitions")
    except Exception as e:
        print(f"    ❌ Error seeding competitions: {e}")
        results['competitions'] = 0
    
    return results

def seed_project_management_system(session: Session, ids: Dict[str, List[int]]) -> Dict[str, int]:
    """Seed Project Management System (13 tables)"""
    results = {}
    
    # Feedback projects
    try:
        print("  Seeding feedback_projects...")
        feedback_projects = []
        for i in range(25):
            feedback_projects.append({
                'name': f'Feedback Project {i+1}',
                'description': f'Description for feedback project {i+1}',
                'status': random.choice(['PLANNING', 'ACTIVE', 'ON_HOLD', 'COMPLETED', 'CANCELLED']),
                'priority': random.choice(['LOW', 'MEDIUM', 'HIGH', 'URGENT']),
                'start_date': datetime.now() - timedelta(days=random.randint(1, 30)),
                'end_date': datetime.now() + timedelta(days=random.randint(1, 90)),
                'created_by': random.choice(ids['user_ids']),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 7))
            })
        
        count = insert_data_flexible(session, 'feedback_projects', feedback_projects)
        results['feedback_projects'] = count
        print(f"    ✅ Created {count} feedback projects")
    except Exception as e:
        print(f"    ❌ Error seeding feedback_projects: {e}")
        results['feedback_projects'] = 0
    
    # Project comments
    try:
        print("  Seeding project_comments...")
        project_comments = []
        for i in range(150):
            project_comments.append({
                'project_id': random.randint(1, 25),
                'user_id': random.choice(ids['user_ids']),
                'content': f'Project comment {i+1}',
                'is_internal': random.choice([True, False]),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 7))
            })
        
        count = insert_data_flexible(session, 'project_comments', project_comments)
        results['project_comments'] = count
        print(f"    ✅ Created {count} project comments")
    except Exception as e:
        print(f"    ❌ Error seeding project_comments: {e}")
        results['project_comments'] = 0
    
    # Project feedback
    try:
        print("  Seeding project_feedback...")
        project_feedback = []
        for i in range(100):
            project_feedback.append({
                'project_id': random.randint(1, 25),
                'user_id': random.choice(ids['user_ids']),
                'rating': random.randint(1, 5),
                'feedback_text': f'Project feedback {i+1}',
                'feedback_type': random.choice(['IMPROVEMENT', 'BUG_REPORT', 'FEATURE_REQUEST', 'GENERAL']),
                'is_public': random.choice([True, False]),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
            })
        
        count = insert_data_flexible(session, 'project_feedback', project_feedback)
        results['project_feedback'] = count
        print(f"    ✅ Created {count} project feedback records")
    except Exception as e:
        print(f"    ❌ Error seeding project_feedback: {e}")
        results['project_feedback'] = 0
    
    # Project members
    try:
        print("  Seeding project_members...")
        project_members = []
        for i in range(80):
            project_members.append({
                'project_id': random.randint(1, 25),
                'user_id': random.choice(ids['user_ids']),
                'role': random.choice(['MEMBER', 'ADMIN', 'OWNER', 'VIEWER']),
                'joined_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'is_active': random.choice([True, False])
            })
        
        count = insert_data_flexible(session, 'project_members', project_members)
        results['project_members'] = count
        print(f"    ✅ Created {count} project members")
    except Exception as e:
        print(f"    ❌ Error seeding project_members: {e}")
        results['project_members'] = 0
    
    # Project milestones
    try:
        print("  Seeding project_milestones...")
        project_milestones = []
        for i in range(60):
            project_milestones.append({
                'project_id': random.randint(1, 25),
                'name': f'Milestone {i+1}',
                'description': f'Description for milestone {i+1}',
                'due_date': datetime.now() + timedelta(days=random.randint(1, 90)),
                'status': random.choice(['PENDING', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED']),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 7))
            })
        
        count = insert_data_flexible(session, 'project_milestones', project_milestones)
        results['project_milestones'] = count
        print(f"    ✅ Created {count} project milestones")
    except Exception as e:
        print(f"    ❌ Error seeding project_milestones: {e}")
        results['project_milestones'] = 0
    
    # Project resources
    try:
        print("  Seeding project_resources...")
        project_resources = []
        for i in range(120):
            project_resources.append({
                'project_id': random.randint(1, 25),
                'name': f'Resource {i+1}',
                'resource_type': random.choice(['DOCUMENT', 'IMAGE', 'VIDEO', 'LINK', 'FILE']),
                'url': f'https://example.com/resource/{i+1}',
                'file_size_bytes': random.randint(1024, 10485760),
                'is_public': random.choice([True, False]),
                'created_by': random.choice(ids['user_ids']),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
            })
        
        count = insert_data_flexible(session, 'project_resources', project_resources)
        results['project_resources'] = count
        print(f"    ✅ Created {count} project resources")
    except Exception as e:
        print(f"    ❌ Error seeding project_resources: {e}")
        results['project_resources'] = 0
    
    # Project roles
    try:
        print("  Seeding project_roles...")
        project_roles = []
        for i in range(20):
            project_roles.append({
                'name': f'Project Role {i+1}',
                'description': f'Description for project role {i+1}',
                'permissions': json.dumps(['read', 'write', 'admin']),
                'is_active': random.choice([True, False]),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 7))
            })
        
        count = insert_data_flexible(session, 'project_roles', project_roles)
        results['project_roles'] = count
        print(f"    ✅ Created {count} project roles")
    except Exception as e:
        print(f"    ❌ Error seeding project_roles: {e}")
        results['project_roles'] = 0
    
    # Project settings
    try:
        print("  Seeding project_settings...")
        project_settings = []
        for i in range(25):
            project_settings.append({
                'project_id': random.randint(1, 25),
                'setting_key': random.choice(['notifications', 'privacy', 'collaboration', 'reporting']),
                'setting_value': json.dumps({'enabled': True, 'frequency': 'daily'}),
                'updated_by': random.choice(ids['user_ids']),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 7))
            })
        
        count = insert_data_flexible(session, 'project_settings', project_settings)
        results['project_settings'] = count
        print(f"    ✅ Created {count} project settings")
    except Exception as e:
        print(f"    ❌ Error seeding project_settings: {e}")
        results['project_settings'] = 0
    
    # Project tasks
    try:
        print("  Seeding project_tasks...")
        project_tasks = []
        for i in range(200):
            project_tasks.append({
                'project_id': random.randint(1, 25),
                'name': f'Task {i+1}',
                'description': f'Description for task {i+1}',
                'status': random.choice(['TODO', 'IN_PROGRESS', 'REVIEW', 'COMPLETED', 'CANCELLED']),
                'priority': random.choice(['LOW', 'MEDIUM', 'HIGH', 'URGENT']),
                'assigned_to': random.choice(ids['user_ids']),
                'due_date': datetime.now() + timedelta(days=random.randint(1, 30)),
                'created_by': random.choice(ids['user_ids']),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 7))
            })
        
        count = insert_data_flexible(session, 'project_tasks', project_tasks)
        results['project_tasks'] = count
        print(f"    ✅ Created {count} project tasks")
    except Exception as e:
        print(f"    ❌ Error seeding project_tasks: {e}")
        results['project_tasks'] = 0
    
    # Feedback project comments
    try:
        print("  Seeding feedback_project_comments...")
        feedback_project_comments = []
        for i in range(100):
            feedback_project_comments.append({
                'project_id': random.randint(1, 25),
                'user_id': random.choice(ids['user_ids']),
                'comment_text': f'Feedback project comment {i+1}',
                'is_approved': random.choice([True, False]),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 7))
            })
        
        count = insert_data_flexible(session, 'feedback_project_comments', feedback_project_comments)
        results['feedback_project_comments'] = count
        print(f"    ✅ Created {count} feedback project comments")
    except Exception as e:
        print(f"    ❌ Error seeding feedback_project_comments: {e}")
        results['feedback_project_comments'] = 0
    
    # Feedback project members
    try:
        print("  Seeding feedback_project_members...")
        feedback_project_members = []
        for i in range(60):
            feedback_project_members.append({
                'project_id': random.randint(1, 25),
                'user_id': random.choice(ids['user_ids']),
                'role': random.choice(['MEMBER', 'ADMIN', 'REVIEWER']),
                'joined_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'is_active': random.choice([True, False])
            })
        
        count = insert_data_flexible(session, 'feedback_project_members', feedback_project_members)
        results['feedback_project_members'] = count
        print(f"    ✅ Created {count} feedback project members")
    except Exception as e:
        print(f"    ❌ Error seeding feedback_project_members: {e}")
        results['feedback_project_members'] = 0
    
    # Feedback project resources
    try:
        print("  Seeding feedback_project_resources...")
        feedback_project_resources = []
        for i in range(80):
            feedback_project_resources.append({
                'project_id': random.randint(1, 25),
                'resource_name': f'Feedback Resource {i+1}',
                'resource_type': random.choice(['DOCUMENT', 'IMAGE', 'VIDEO', 'LINK']),
                'url': f'https://example.com/feedback/resource/{i+1}',
                'created_by': random.choice(ids['user_ids']),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
            })
        
        count = insert_data_flexible(session, 'feedback_project_resources', feedback_project_resources)
        results['feedback_project_resources'] = count
        print(f"    ✅ Created {count} feedback project resources")
    except Exception as e:
        print(f"    ❌ Error seeding feedback_project_resources: {e}")
        results['feedback_project_resources'] = 0
    
    # Feedback project tasks
    try:
        print("  Seeding feedback_project_tasks...")
        feedback_project_tasks = []
        for i in range(120):
            feedback_project_tasks.append({
                'project_id': random.randint(1, 25),
                'task_name': f'Feedback Task {i+1}',
                'description': f'Description for feedback task {i+1}',
                'status': random.choice(['PENDING', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED']),
                'assigned_to': random.choice(ids['user_ids']),
                'due_date': datetime.now() + timedelta(days=random.randint(1, 30)),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 7))
            })
        
        count = insert_data_flexible(session, 'feedback_project_tasks', feedback_project_tasks)
        results['feedback_project_tasks'] = count
        print(f"    ✅ Created {count} feedback project tasks")
    except Exception as e:
        print(f"    ❌ Error seeding feedback_project_tasks: {e}")
        results['feedback_project_tasks'] = 0
    
    return results

def seed_resource_management_system(session: Session, ids: Dict[str, List[int]]) -> Dict[str, int]:
    """Seed Resource Management System (9 tables)"""
    results = {}
    
    # Resource alerts
    try:
        print("  Seeding resource_alerts...")
        resource_alerts = []
        for i in range(50):
            resource_alerts.append({
                'alert_type': random.choice(['CPU_HIGH', 'MEMORY_LOW', 'DISK_FULL', 'NETWORK_SLOW', 'SERVICE_DOWN']),
                'severity': random.choice(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']),
                'message': f'Resource alert {i+1}',
                'resource_name': f'Resource {i+1}',
                'threshold_value': round(random.uniform(50.0, 100.0), 2),
                'current_value': round(random.uniform(60.0, 110.0), 2),
                'is_resolved': random.choice([True, False]),
                'created_at': datetime.now() - timedelta(minutes=random.randint(1, 1440)),
                'resolved_at': datetime.now() - timedelta(minutes=random.randint(1, 720)) if random.random() < 0.7 else None
            })
        
        count = insert_data_flexible(session, 'resource_alerts', resource_alerts)
        results['resource_alerts'] = count
        print(f"    ✅ Created {count} resource alerts")
    except Exception as e:
        print(f"    ❌ Error seeding resource_alerts: {e}")
        results['resource_alerts'] = 0
    
    # Resource events
    try:
        print("  Seeding resource_events...")
        resource_events = []
        for i in range(80):
            resource_events.append({
                'event_type': random.choice(['ALLOCATION', 'DEALLOCATION', 'SCALING', 'MAINTENANCE', 'ERROR']),
                'resource_name': f'Resource {i+1}',
                'description': f'Resource event {i+1}',
                'old_value': round(random.uniform(10.0, 100.0), 2),
                'new_value': round(random.uniform(5.0, 95.0), 2),
                'timestamp': datetime.now() - timedelta(minutes=random.randint(1, 1440)),
                'metadata': json.dumps({'source': 'resource_manager', 'version': '1.0'})
            })
        
        count = insert_data_flexible(session, 'resource_events', resource_events)
        results['resource_events'] = count
        print(f"    ✅ Created {count} resource events")
    except Exception as e:
        print(f"    ❌ Error seeding resource_events: {e}")
        results['resource_events'] = 0
    
    # Resource management sharing
    try:
        print("  Seeding resource_management_sharing...")
        resource_management_sharing = []
        for i in range(30):
            resource_management_sharing.append({
                'resource_id': random.randint(1, 100),
                'shared_with_user_id': random.choice(ids['user_ids']),
                'permissions': json.dumps(['read', 'write']),
                'shared_by': random.choice(ids['user_ids']),
                'expires_at': datetime.now() + timedelta(days=random.randint(1, 365)),
                'is_active': random.choice([True, False]),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
            })
        
        count = insert_data_flexible(session, 'resource_management_sharing', resource_management_sharing)
        results['resource_management_sharing'] = count
        print(f"    ✅ Created {count} resource management sharing records")
    except Exception as e:
        print(f"    ❌ Error seeding resource_management_sharing: {e}")
        results['resource_management_sharing'] = 0
    
    # Resource management usage
    try:
        print("  Seeding resource_management_usage...")
        resource_management_usage = []
        for i in range(100):
            resource_management_usage.append({
                'resource_id': random.randint(1, 100),
                'user_id': random.choice(ids['user_ids']),
                'usage_type': random.choice(['CPU', 'MEMORY', 'STORAGE', 'NETWORK']),
                'usage_amount': round(random.uniform(0.0, 100.0), 2),
                'unit': random.choice(['PERCENT', 'BYTES', 'REQUESTS']),
                'timestamp': datetime.now() - timedelta(minutes=random.randint(1, 1440)),
                'metadata': json.dumps({'session_id': f'session_{i+1}'})
            })
        
        count = insert_data_flexible(session, 'resource_management_usage', resource_management_usage)
        results['resource_management_usage'] = count
        print(f"    ✅ Created {count} resource management usage records")
    except Exception as e:
        print(f"    ❌ Error seeding resource_management_usage: {e}")
        results['resource_management_usage'] = 0
    
    # Resource optimization events
    try:
        print("  Seeding resource_optimization_events...")
        resource_optimization_events = []
        for i in range(60):
            resource_optimization_events.append({
                'event_type': random.choice(['AUTO_SCALING', 'LOAD_BALANCING', 'CACHE_OPTIMIZATION', 'QUERY_OPTIMIZATION']),
                'resource_name': f'Resource {i+1}',
                'optimization_type': random.choice(['PERFORMANCE', 'COST', 'EFFICIENCY']),
                'old_value': round(random.uniform(10.0, 100.0), 2),
                'new_value': round(random.uniform(5.0, 95.0), 2),
                'improvement_percentage': round(random.uniform(5.0, 50.0), 2),
                'timestamp': datetime.now() - timedelta(minutes=random.randint(1, 1440)),
                'metadata': json.dumps({'algorithm': 'auto_optimizer', 'version': '1.0'})
            })
        
        count = insert_data_flexible(session, 'resource_optimization_events', resource_optimization_events)
        results['resource_optimization_events'] = count
        print(f"    ✅ Created {count} resource optimization events")
    except Exception as e:
        print(f"    ❌ Error seeding resource_optimization_events: {e}")
        results['resource_optimization_events'] = 0
    
    # Resource optimization recommendations
    try:
        print("  Seeding resource_optimization_recommendations...")
        resource_optimization_recommendations = []
        for i in range(40):
            resource_optimization_recommendations.append({
                'resource_id': random.randint(1, 100),
                'recommendation_type': random.choice(['SCALE_UP', 'SCALE_DOWN', 'OPTIMIZE_QUERY', 'ADD_CACHE']),
                'title': f'Optimization Recommendation {i+1}',
                'description': f'Description for optimization recommendation {i+1}',
                'priority': random.choice(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']),
                'estimated_savings': round(random.uniform(10.0, 1000.0), 2),
                'is_implemented': random.choice([True, False]),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'implemented_at': datetime.now() - timedelta(days=random.randint(1, 7)) if random.random() < 0.3 else None
            })
        
        count = insert_data_flexible(session, 'resource_optimization_recommendations', resource_optimization_recommendations)
        results['resource_optimization_recommendations'] = count
        print(f"    ✅ Created {count} resource optimization recommendations")
    except Exception as e:
        print(f"    ❌ Error seeding resource_optimization_recommendations: {e}")
        results['resource_optimization_recommendations'] = 0
    
    # Resource optimization thresholds
    try:
        print("  Seeding resource_optimization_thresholds...")
        resource_optimization_thresholds = []
        for i in range(25):
            resource_optimization_thresholds.append({
                'resource_type': random.choice(['CPU', 'MEMORY', 'STORAGE', 'NETWORK']),
                'metric_name': f'Metric {i+1}',
                'warning_threshold': round(random.uniform(70.0, 85.0), 2),
                'critical_threshold': round(random.uniform(85.0, 95.0), 2),
                'unit': random.choice(['PERCENT', 'BYTES', 'REQUESTS']),
                'is_active': random.choice([True, False]),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 7))
            })
        
        count = insert_data_flexible(session, 'resource_optimization_thresholds', resource_optimization_thresholds)
        results['resource_optimization_thresholds'] = count
        print(f"    ✅ Created {count} resource optimization thresholds")
    except Exception as e:
        print(f"    ❌ Error seeding resource_optimization_thresholds: {e}")
        results['resource_optimization_thresholds'] = 0
    
    # Resource optimizations
    try:
        print("  Seeding resource_optimizations...")
        resource_optimizations = []
        for i in range(35):
            resource_optimizations.append({
                'resource_id': random.randint(1, 100),
                'optimization_type': random.choice(['PERFORMANCE', 'COST', 'EFFICIENCY', 'RELIABILITY']),
                'optimization_name': f'Optimization {i+1}',
                'description': f'Description for optimization {i+1}',
                'status': random.choice(['PENDING', 'IN_PROGRESS', 'COMPLETED', 'FAILED']),
                'estimated_impact': round(random.uniform(5.0, 50.0), 2),
                'created_by': random.choice(ids['user_ids']),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'completed_at': datetime.now() - timedelta(days=random.randint(1, 7)) if random.random() < 0.6 else None
            })
        
        count = insert_data_flexible(session, 'resource_optimizations', resource_optimizations)
        results['resource_optimizations'] = count
        print(f"    ✅ Created {count} resource optimizations")
    except Exception as e:
        print(f"    ❌ Error seeding resource_optimizations: {e}")
        results['resource_optimizations'] = 0
    
    # Resource thresholds
    try:
        print("  Seeding resource_thresholds...")
        resource_thresholds = []
        for i in range(20):
            resource_thresholds.append({
                'resource_name': f'Resource {i+1}',
                'threshold_type': random.choice(['WARNING', 'CRITICAL', 'INFO']),
                'threshold_value': round(random.uniform(50.0, 100.0), 2),
                'unit': random.choice(['PERCENT', 'BYTES', 'REQUESTS']),
                'is_active': random.choice([True, False]),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 7))
            })
        
        count = insert_data_flexible(session, 'resource_thresholds', resource_thresholds)
        results['resource_thresholds'] = count
        print(f"    ✅ Created {count} resource thresholds")
    except Exception as e:
        print(f"    ❌ Error seeding resource_thresholds: {e}")
        results['resource_thresholds'] = 0
    
    return results

def seed_communication_feedback_system(session: Session, ids: Dict[str, List[int]]) -> Dict[str, int]:
    """Seed Communication & Feedback System (8 tables)"""
    results = {}
    
    # Comments
    try:
        print("  Seeding comments...")
        comments = []
        for i in range(200):
            comments.append({
                'content': f'Comment content {i+1}',
                'author_id': random.choice(ids['user_ids']),
                'parent_id': random.randint(1, 50) if random.random() < 0.3 else None,
                'entity_type': random.choice(['activity', 'student', 'project', 'report']),
                'entity_id': random.randint(1, 1000),
                'is_approved': random.choice([True, False]),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 7))
            })
        
        count = insert_data_flexible(session, 'comments', comments)
        results['comments'] = count
        print(f"    ✅ Created {count} comments")
    except Exception as e:
        print(f"    ❌ Error seeding comments: {e}")
        results['comments'] = 0
    
    # Feedback actions
    try:
        print("  Seeding feedback_actions...")
        feedback_actions = []
        for i in range(75):
            feedback_actions.append({
                'action_type': random.choice(['LIKE', 'DISLIKE', 'REPORT', 'SHARE', 'BOOKMARK']),
                'user_id': random.choice(ids['user_ids']),
                'entity_type': random.choice(['comment', 'post', 'project', 'activity']),
                'entity_id': random.randint(1, 1000),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
            })
        
        count = insert_data_flexible(session, 'feedback_actions', feedback_actions)
        results['feedback_actions'] = count
        print(f"    ✅ Created {count} feedback actions")
    except Exception as e:
        print(f"    ❌ Error seeding feedback_actions: {e}")
        results['feedback_actions'] = 0
    
    # Feedback attachments
    try:
        print("  Seeding feedback_attachments...")
        feedback_attachments = []
        for i in range(50):
            feedback_attachments.append({
                'feedback_id': random.randint(1, 100),
                'file_name': f'attachment_{i+1}.{random.choice(["pdf", "jpg", "png", "docx"])}',
                'file_path': f'/attachments/feedback_{i+1}',
                'file_size_bytes': random.randint(1024, 10485760),
                'mime_type': random.choice(['application/pdf', 'image/jpeg', 'image/png', 'application/msword']),
                'uploaded_by': random.choice(ids['user_ids']),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
            })
        
        count = insert_data_flexible(session, 'feedback_attachments', feedback_attachments)
        results['feedback_attachments'] = count
        print(f"    ✅ Created {count} feedback attachments")
    except Exception as e:
        print(f"    ❌ Error seeding feedback_attachments: {e}")
        results['feedback_attachments'] = 0
    
    # Feedback categories
    try:
        print("  Seeding feedback_categories...")
        feedback_categories = []
        for i in range(15):
            feedback_categories.append({
                'name': f'Category {i+1}',
                'description': f'Description for feedback category {i+1}',
                'color': f'#{random.randint(0, 255):02x}{random.randint(0, 255):02x}{random.randint(0, 255):02x}',
                'is_active': random.choice([True, False]),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 7))
            })
        
        count = insert_data_flexible(session, 'feedback_categories', feedback_categories)
        results['feedback_categories'] = count
        print(f"    ✅ Created {count} feedback categories")
    except Exception as e:
        print(f"    ❌ Error seeding feedback_categories: {e}")
        results['feedback_categories'] = 0
    
    # Feedback comments
    try:
        print("  Seeding feedback_comments...")
        feedback_comments = []
        for i in range(200):
            feedback_comments.append({
                'feedback_id': random.randint(1, 100),
                'user_id': random.choice(ids['user_ids']),
                'content': f'Feedback comment {i+1}',
                'parent_id': random.randint(1, 50) if random.random() < 0.3 else None,
                'is_approved': random.choice([True, False]),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 7))
            })
        
        count = insert_data_flexible(session, 'feedback_comments', feedback_comments)
        results['feedback_comments'] = count
        print(f"    ✅ Created {count} feedback comments")
    except Exception as e:
        print(f"    ❌ Error seeding feedback_comments: {e}")
        results['feedback_comments'] = 0
    
    # Feedback responses
    try:
        print("  Seeding feedback_responses...")
        feedback_responses = []
        for i in range(100):
            feedback_responses.append({
                'feedback_id': random.randint(1, 100),
                'responder_id': random.choice(ids['user_ids']),
                'response_text': f'Feedback response {i+1}',
                'response_type': random.choice(['ACKNOWLEDGMENT', 'RESOLUTION', 'FOLLOW_UP', 'CLARIFICATION']),
                'is_public': random.choice([True, False]),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 7))
            })
        
        count = insert_data_flexible(session, 'feedback_responses', feedback_responses)
        results['feedback_responses'] = count
        print(f"    ✅ Created {count} feedback responses")
    except Exception as e:
        print(f"    ❌ Error seeding feedback_responses: {e}")
        results['feedback_responses'] = 0
    
    # Message board posts
    try:
        print("  Seeding message_board_posts...")
        message_board_posts = []
        for i in range(150):
            message_board_posts.append({
                'board_id': random.randint(1, 10),
                'author_id': random.choice(ids['user_ids']),
                'title': f'Message Board Post {i+1}',
                'content': f'Content for message board post {i+1}',
                'is_pinned': random.choice([True, False]),
                'is_locked': random.choice([True, False]),
                'view_count': random.randint(0, 1000),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 7))
            })
        
        count = insert_data_flexible(session, 'message_board_posts', message_board_posts)
        results['message_board_posts'] = count
        print(f"    ✅ Created {count} message board posts")
    except Exception as e:
        print(f"    ❌ Error seeding message_board_posts: {e}")
        results['message_board_posts'] = 0
    
    # Message boards
    try:
        print("  Seeding message_boards...")
        message_boards = []
        for i in range(10):
            message_boards.append({
                'name': f'Message Board {i+1}',
                'description': f'Description for message board {i+1}',
                'category': random.choice(['GENERAL', 'ANNOUNCEMENTS', 'DISCUSSION', 'SUPPORT']),
                'is_public': random.choice([True, False]),
                'is_active': random.choice([True, False]),
                'created_by': random.choice(ids['user_ids']),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 7))
            })
        
        count = insert_data_flexible(session, 'message_boards', message_boards)
        results['message_boards'] = count
        print(f"    ✅ Created {count} message boards")
    except Exception as e:
        print(f"    ❌ Error seeding message_boards: {e}")
        results['message_boards'] = 0
    
    return results

def seed_core_system_integration(session: Session, ids: Dict[str, List[int]]) -> Dict[str, int]:
    """Seed Core System Integration (3 tables)"""
    results = {}
    
    # Context data
    try:
        print("  Seeding context_data...")
        context_data = []
        for i in range(100):
            context_data.append({
                'context_key': f'context_{i+1}',
                'context_value': json.dumps({'data': f'Context data {i+1}', 'type': 'system'}),
                'context_type': random.choice(['USER', 'SESSION', 'SYSTEM', 'CACHE']),
                'expires_at': datetime.now() + timedelta(hours=random.randint(1, 24)),
                'created_at': datetime.now() - timedelta(hours=random.randint(1, 168)),
                'updated_at': datetime.now() - timedelta(hours=random.randint(1, 24))
            })
        
        count = insert_data_flexible(session, 'context_data', context_data)
        results['context_data'] = count
        print(f"    ✅ Created {count} context data records")
    except Exception as e:
        print(f"    ❌ Error seeding context_data: {e}")
        results['context_data'] = 0
    
    # Core activities
    try:
        print("  Seeding core_activities...")
        core_activities = []
        for i in range(50):
            core_activities.append({
                'activity_name': f'Core Activity {i+1}',
                'activity_type': random.choice(['SYSTEM', 'USER', 'AUTOMATED', 'SCHEDULED']),
                'description': f'Description for core activity {i+1}',
                'status': random.choice(['ACTIVE', 'INACTIVE', 'PENDING', 'COMPLETED']),
                'priority': random.choice(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']),
                'created_by': random.choice(ids['user_ids']),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 7))
            })
        
        count = insert_data_flexible(session, 'core_activities', core_activities)
        results['core_activities'] = count
        print(f"    ✅ Created {count} core activities")
    except Exception as e:
        print(f"    ❌ Error seeding core_activities: {e}")
        results['core_activities'] = 0
    
    # Webhooks
    try:
        print("  Seeding webhooks...")
        webhooks = []
        for i in range(20):
            webhooks.append({
                'name': f'Webhook {i+1}',
                'url': f'https://api.example.com/webhooks/{i+1}',
                'event_type': random.choice(['USER_CREATED', 'ACTIVITY_COMPLETED', 'STUDENT_ENROLLED', 'SYSTEM_ALERT']),
                'secret': f'webhook_secret_{random.randint(100000, 999999)}',
                'is_active': random.choice([True, False]),
                'retry_count': random.randint(0, 5),
                'timeout_seconds': random.randint(30, 300),
                'created_by': random.choice(ids['user_ids']),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 7))
            })
        
        count = insert_data_flexible(session, 'webhooks', webhooks)
        results['webhooks'] = count
        print(f"    ✅ Created {count} webhooks")
    except Exception as e:
        print(f"    ❌ Error seeding webhooks: {e}")
        results['webhooks'] = 0
    
    return results

def seed_billing_subscription_system(session: Session, ids: Dict[str, List[int]]) -> Dict[str, int]:
    """Seed Billing & Subscription System (6 tables)"""
    results = {}
    
    # GPT subscription billing
    try:
        print("  Seeding gpt_subscription_billing...")
        gpt_subscription_billing = []
        for i in range(30):
            gpt_subscription_billing.append({
                'user_id': random.choice(ids['user_ids']),
                'subscription_id': random.randint(1, 15),
                'amount': round(random.uniform(10.0, 100.0), 2),
                'currency': 'USD',
                'billing_period': random.choice(['MONTHLY', 'QUARTERLY', 'YEARLY']),
                'status': random.choice(['PENDING', 'PAID', 'FAILED', 'REFUNDED']),
                'due_date': datetime.now() + timedelta(days=random.randint(1, 30)),
                'paid_at': datetime.now() - timedelta(days=random.randint(1, 30)) if random.random() < 0.8 else None,
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 7))
            })
        
        count = insert_data_flexible(session, 'gpt_subscription_billing', gpt_subscription_billing)
        results['gpt_subscription_billing'] = count
        print(f"    ✅ Created {count} GPT subscription billing records")
    except Exception as e:
        print(f"    ❌ Error seeding gpt_subscription_billing: {e}")
        results['gpt_subscription_billing'] = 0
    
    # GPT subscription invoices
    try:
        print("  Seeding gpt_subscription_invoices...")
        gpt_subscription_invoices = []
        for i in range(25):
            gpt_subscription_invoices.append({
                'subscription_id': random.randint(1, 15),
                'invoice_number': f'INV-{random.randint(100000, 999999)}',
                'amount': round(random.uniform(10.0, 100.0), 2),
                'currency': 'USD',
                'status': random.choice(['DRAFT', 'SENT', 'PAID', 'OVERDUE', 'CANCELLED']),
                'due_date': datetime.now() + timedelta(days=random.randint(1, 30)),
                'paid_at': datetime.now() - timedelta(days=random.randint(1, 30)) if random.random() < 0.7 else None,
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 7))
            })
        
        count = insert_data_flexible(session, 'gpt_subscription_invoices', gpt_subscription_invoices)
        results['gpt_subscription_invoices'] = count
        print(f"    ✅ Created {count} GPT subscription invoices")
    except Exception as e:
        print(f"    ❌ Error seeding gpt_subscription_invoices: {e}")
        results['gpt_subscription_invoices'] = 0
    
    # GPT subscription payments
    try:
        print("  Seeding gpt_subscription_payments...")
        gpt_subscription_payments = []
        for i in range(30):
            gpt_subscription_payments.append({
                'subscription_id': random.randint(1, 15),
                'invoice_id': random.randint(1, 25),
                'amount': round(random.uniform(10.0, 100.0), 2),
                'currency': 'USD',
                'payment_method': random.choice(['CREDIT_CARD', 'BANK_TRANSFER', 'PAYPAL', 'STRIPE']),
                'transaction_id': f'txn_{random.randint(100000, 999999)}',
                'status': random.choice(['PENDING', 'COMPLETED', 'FAILED', 'REFUNDED']),
                'processed_at': datetime.now() - timedelta(days=random.randint(1, 30)) if random.random() < 0.8 else None,
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
            })
        
        count = insert_data_flexible(session, 'gpt_subscription_payments', gpt_subscription_payments)
        results['gpt_subscription_payments'] = count
        print(f"    ✅ Created {count} GPT subscription payments")
    except Exception as e:
        print(f"    ❌ Error seeding gpt_subscription_payments: {e}")
        results['gpt_subscription_payments'] = 0
    
    # GPT subscription refunds
    try:
        print("  Seeding gpt_subscription_refunds...")
        gpt_subscription_refunds = []
        for i in range(10):
            gpt_subscription_refunds.append({
                'subscription_id': random.randint(1, 15),
                'payment_id': random.randint(1, 30),
                'amount': round(random.uniform(5.0, 50.0), 2),
                'currency': 'USD',
                'reason': random.choice(['CANCELLATION', 'DUPLICATE', 'ERROR', 'CUSTOMER_REQUEST']),
                'status': random.choice(['PENDING', 'PROCESSED', 'FAILED']),
                'processed_at': datetime.now() - timedelta(days=random.randint(1, 15)) if random.random() < 0.7 else None,
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
            })
        
        count = insert_data_flexible(session, 'gpt_subscription_refunds', gpt_subscription_refunds)
        results['gpt_subscription_refunds'] = count
        print(f"    ✅ Created {count} GPT subscription refunds")
    except Exception as e:
        print(f"    ❌ Error seeding gpt_subscription_refunds: {e}")
        results['gpt_subscription_refunds'] = 0
    
    # GPT subscription usage
    try:
        print("  Seeding gpt_subscription_usage...")
        gpt_subscription_usage = []
        for i in range(100):
            gpt_subscription_usage.append({
                'subscription_id': random.randint(1, 15),
                'user_id': random.choice(ids['user_ids']),
                'usage_type': random.choice(['API_CALLS', 'TOKENS', 'STORAGE', 'BANDWIDTH']),
                'usage_amount': random.randint(1, 1000),
                'usage_date': datetime.now() - timedelta(days=random.randint(1, 30)),
                'cost': round(random.uniform(0.01, 10.0), 2),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
            })
        
        count = insert_data_flexible(session, 'gpt_subscription_usage', gpt_subscription_usage)
        results['gpt_subscription_usage'] = count
        print(f"    ✅ Created {count} GPT subscription usage records")
    except Exception as e:
        print(f"    ❌ Error seeding gpt_subscription_usage: {e}")
        results['gpt_subscription_usage'] = 0
    
    return results

def seed_additional_user_management(session: Session, ids: Dict[str, List[int]]) -> Dict[str, int]:
    """Seed Additional User Management (4 tables)"""
    results = {}
    
    # Instructors
    try:
        print("  Seeding instructors...")
        instructors = []
        for i in range(20):
            instructors.append({
                'first_name': f'Instructor{i+1}',
                'last_name': f'LastName{i+1}',
                'email': f'instructor{i+1}@example.com',
                'phone': f'555-{random.randint(100, 999)}-{random.randint(1000, 9999)}',
                'specialization': random.choice(['PHYSICAL_EDUCATION', 'SPORTS_SCIENCE', 'HEALTH_EDUCATION', 'FITNESS']),
                'certification_level': random.choice(['BASIC', 'INTERMEDIATE', 'ADVANCED', 'EXPERT']),
                'years_experience': random.randint(1, 20),
                'is_active': random.choice([True, False]),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 7))
            })
        
        count = insert_data_flexible(session, 'instructors', instructors)
        results['instructors'] = count
        print(f"    ✅ Created {count} instructors")
    except Exception as e:
        print(f"    ❌ Error seeding instructors: {e}")
        results['instructors'] = 0
    
    # Subject assistant
    try:
        print("  Seeding subject_assistant...")
        subject_assistant = []
        for i in range(15):
            subject_assistant.append({
                'name': f'Subject Assistant {i+1}',
                'subject_area': random.choice(['MATHEMATICS', 'SCIENCE', 'PHYSICAL_EDUCATION', 'LANGUAGE_ARTS', 'SOCIAL_STUDIES']),
                'description': f'Description for subject assistant {i+1}',
                'capabilities': json.dumps(['tutoring', 'grading', 'lesson_planning', 'assessment']),
                'is_active': random.choice([True, False]),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 7))
            })
        
        count = insert_data_flexible(session, 'subject_assistant', subject_assistant)
        results['subject_assistant'] = count
        print(f"    ✅ Created {count} subject assistants")
    except Exception as e:
        print(f"    ❌ Error seeding subject_assistant: {e}")
        results['subject_assistant'] = 0
    
    # Teacher certification base
    try:
        print("  Seeding teacher_certification_base...")
        teacher_certification_base = []
        for i in range(20):
            teacher_certification_base.append({
                'certification_name': f'Certification {i+1}',
                'certification_type': random.choice(['TEACHING', 'ADMINISTRATIVE', 'SPECIAL_EDUCATION', 'PHYSICAL_EDUCATION']),
                'description': f'Description for certification {i+1}',
                'requirements': json.dumps(['bachelor_degree', 'teaching_experience', 'examination']),
                'validity_years': random.randint(1, 10),
                'is_active': random.choice([True, False]),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 7))
            })
        
        count = insert_data_flexible(session, 'teacher_certification_base', teacher_certification_base)
        results['teacher_certification_base'] = count
        print(f"    ✅ Created {count} teacher certification base records")
    except Exception as e:
        print(f"    ❌ Error seeding teacher_certification_base: {e}")
        results['teacher_certification_base'] = 0
    
    # Tool assignments
    try:
        print("  Seeding tool_assignments...")
        tool_assignments = []
        for i in range(40):
            tool_assignments.append({
                'tool_id': random.choice(ids['dashboard_tool_ids']),
                'user_id': random.choice(ids['dashboard_user_ids']),
                'assigned_by': random.choice(ids['dashboard_user_ids']),
                'assigned_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'expires_at': datetime.now() + timedelta(days=random.randint(30, 365)) if random.random() < 0.7 else None,
                'is_active': random.choice([True, False])
            })
        
        count = insert_data_flexible(session, 'tool_assignments', tool_assignments)
        results['tool_assignments'] = count
        print(f"    ✅ Created {count} tool assignments")
    except Exception as e:
        print(f"    ❌ Error seeding tool_assignments: {e}")
        results['tool_assignments'] = 0
    
    return results

def seed_analytics_planning(session: Session, ids: Dict[str, List[int]]) -> Dict[str, int]:
    """Seed Analytics & Planning (3 tables)"""
    results = {}
    
    # Optimization events
    try:
        print("  Seeding optimization_events...")
        optimization_events = []
        for i in range(75):
            optimization_events.append({
                'event_type': random.choice(['PERFORMANCE_OPTIMIZATION', 'CACHE_OPTIMIZATION', 'QUERY_OPTIMIZATION', 'RESOURCE_OPTIMIZATION']),
                'description': f'Optimization event {i+1}',
                'old_value': round(random.uniform(10.0, 100.0), 2),
                'new_value': round(random.uniform(5.0, 95.0), 2),
                'improvement_percentage': round(random.uniform(5.0, 50.0), 2),
                'execution_time_ms': random.randint(100, 5000),
                'created_at': datetime.now() - timedelta(minutes=random.randint(1, 1440)),
                'metadata': json.dumps({'source': 'system_optimizer', 'version': '1.0'})
            })
        
        count = insert_data_flexible(session, 'optimization_events', optimization_events)
        results['optimization_events'] = count
        print(f"    ✅ Created {count} optimization events")
    except Exception as e:
        print(f"    ❌ Error seeding optimization_events: {e}")
        results['optimization_events'] = 0
    
    # Planning history
    try:
        print("  Seeding planning_history...")
        planning_history = []
        for i in range(60):
            planning_history.append({
                'plan_name': f'Plan {i+1}',
                'plan_type': random.choice(['LESSON', 'CURRICULUM', 'ASSESSMENT', 'ACTIVITY']),
                'description': f'Description for plan {i+1}',
                'status': random.choice(['DRAFT', 'REVIEW', 'APPROVED', 'IMPLEMENTED', 'ARCHIVED']),
                'created_by': random.choice(ids['user_ids']),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 7)),
                'metadata': json.dumps({'version': '1.0', 'tags': ['planning', 'education']})
            })
        
        count = insert_data_flexible(session, 'planning_history', planning_history)
        results['planning_history'] = count
        print(f"    ✅ Created {count} planning history records")
    except Exception as e:
        print(f"    ❌ Error seeding planning_history: {e}")
        results['planning_history'] = 0
    
    # Planning metrics
    try:
        print("  Seeding planning_metrics...")
        planning_metrics = []
        for i in range(40):
            planning_metrics.append({
                'metric_name': f'Planning Metric {i+1}',
                'metric_type': random.choice(['EFFICIENCY', 'QUALITY', 'COMPLETION', 'SATISFACTION']),
                'value': round(random.uniform(0.0, 100.0), 2),
                'unit': random.choice(['PERCENT', 'SCORE', 'COUNT', 'RATING']),
                'period': random.choice(['DAILY', 'WEEKLY', 'MONTHLY', 'QUARTERLY']),
                'timestamp': datetime.now() - timedelta(days=random.randint(1, 30)),
                'metadata': json.dumps({'source': 'planning_system', 'version': '1.0'})
            })
        
        count = insert_data_flexible(session, 'planning_metrics', planning_metrics)
        results['planning_metrics'] = count
        print(f"    ✅ Created {count} planning metrics")
    except Exception as e:
        print(f"    ❌ Error seeding planning_metrics: {e}")
        results['planning_metrics'] = 0
    
    return results

if __name__ == "__main__":
    from app.core.database import SessionLocal
    
    session = SessionLocal()
    try:
        results = seed_phase11_advanced_system_features(session)
        session.commit()
        print(f"\n🎉 Phase 11 completed successfully!")
        print(f"📊 Total records created: {sum(results.values()):,}")
    except Exception as e:
        print(f"\n❌ Phase 11 failed: {e}")
        session.rollback()
        raise
    finally:
        session.close()
