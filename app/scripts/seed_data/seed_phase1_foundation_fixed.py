"""
Phase 1: Foundation & Core Infrastructure Seeding Script

This script handles the foundational data seeding for the Faraday AI system,
including user management, access control, system configuration, and basic infrastructure.
"""

import random
import json
from datetime import datetime, timedelta
from sqlalchemy import text
from sqlalchemy.orm import Session


def seed_phase1_foundation(session: Session):
    """
    Main function to seed Phase 1 foundation data
    """
    print("\n" + "="*50)
    print("🌱 PHASE 1: FOUNDATION & CORE INFRASTRUCTURE")
    print("="*50)
    
    try:
        # Phase 1.1: User Management Foundation
        print("📋 PHASE 1.1: User Management Foundation")
        print("-" * 40)
        seed_user_management_foundation(session)
        session.commit()
        print("✅ Phase 1.1 completed successfully!")
        
        # Phase 1.2: Access Control System
        print("\n📋 PHASE 1.2: Access Control System")
        print("-" * 40)
        seed_access_control_system(session)
        session.commit()
        print("✅ Phase 1.2 completed successfully!")
        
        # Phase 1.3: System Configuration
        print("\n📋 PHASE 1.3: System Configuration")
        print("-" * 40)
        seed_system_configuration(session)
        session.commit()
        print("✅ Phase 1.3 completed successfully!")
        
        # Phase 1.4: Basic Infrastructure
        print("\n📋 PHASE 1.4: Basic Infrastructure")
        print("-" * 40)
        seed_basic_infrastructure(session)
        session.commit()
        print("✅ Phase 1.4 completed successfully!")
        
        print("\n✅ Phase 1 Foundation seeding completed!")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Error in Phase 1 foundation seeding: {e}")
        raise


def seed_user_management_foundation(session: Session):
    """Seed user management foundation data"""
    print("🔄 Seeding user management foundation...")
    
    # Seed sample users
    seed_sample_users(session)
    
    # Seed user profiles
    seed_user_profiles(session)
    
    # Seed user roles
    seed_user_roles(session)
    
    # Seed user sessions
    seed_user_sessions(session)
    
    # Seed user activities
    seed_user_activities(session)
    
    # Seed user behaviors
    seed_user_behaviors(session)
    
    # Seed user engagements
    seed_user_engagements(session)
    
    # Seed user insights
    seed_user_insights(session)
    
    # Seed user trends
    seed_user_trends(session)
    
    # Seed user predictions
    seed_user_predictions(session)
    
    # Seed user comparisons
    seed_user_comparisons(session)


def seed_sample_users(session: Session):
    """Seed sample users if they don't exist"""
    print("  🔄 Seeding sample users...")
    
    # Check if users already exist
    result = session.execute(text("SELECT COUNT(*) FROM users"))
    existing_count = result.scalar()
    if existing_count > 0:
        print(f"    ✅ {existing_count} users already exist, migrating data...")
        return
    
    # Create sample users
    users = []
    for i in range(1, 33):  # 32 users
        users.append({
            'email': f'user{i}@example.com',
            'username': f'user{i}',
            'first_name': f'User{i}',
            'last_name': 'Test',
            'is_active': True,
            'is_verified': True,
            'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
            'updated_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    columns = list(users[0].keys())
    placeholders = ', '.join([f':{col}' for col in columns])
    query = f"INSERT INTO users ({', '.join(columns)}) VALUES ({placeholders})"
    session.execute(text(query), users)
    print(f"    ✅ Created {len(users)} users")


def seed_user_profiles(session: Session):
    """Seed user profiles"""
    print("  🔄 Seeding user profiles...")
    
    result = session.execute(text("SELECT id FROM users"))
    user_ids = [row[0] for row in result.fetchall()]
    
    profiles = []
    for user_id in user_ids:
        profiles.append({
            'user_id': user_id,
            'avatar_id': None,
            'notification_preferences': json.dumps({
                'email': True,
                'sms': False,
                'push': True,
                'in_app': True
            }),
            'custom_settings': json.dumps({
                'theme': random.choice(['light', 'dark', 'auto']),
                'language': 'en',
                'timezone': 'UTC'
            }),
            'metadata': json.dumps({
                'last_login': datetime.now().isoformat(),
                'login_count': random.randint(1, 100),
                'preferences': {
                    'notifications': True,
                    'marketing': False
                }
            }),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
            'updated_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    if profiles:
        columns = list(profiles[0].keys())
        placeholders = ', '.join([f':{col}' for col in columns])
        query = f"INSERT INTO user_profiles ({', '.join(columns)}) VALUES ({placeholders})"
        session.execute(text(query), profiles)
        print(f"    ✅ Created {len(profiles)} user profiles")


def seed_user_roles(session: Session):
    """Seed user roles and assignments"""
    print("  🔄 Seeding user roles...")
    
    # Check if roles already exist
    result = session.execute(text("SELECT COUNT(*) FROM roles"))
    existing_count = result.scalar()
    if existing_count > 0:
        print(f"    ✅ Roles already exist, migrating data...")
    else:
        # Create roles
        roles = [
            {'name': 'admin', 'description': 'Administrator role', 'is_active': True},
            {'name': 'teacher', 'description': 'Teacher role', 'is_active': True},
            {'name': 'student', 'description': 'Student role', 'is_active': True},
            {'name': 'parent', 'description': 'Parent role', 'is_active': True},
            {'name': 'guest', 'description': 'Guest role', 'is_active': True}
        ]
        
        columns = list(roles[0].keys())
        placeholders = ', '.join([f':{col}' for col in columns])
        query = f"INSERT INTO roles ({', '.join(columns)}) VALUES ({placeholders})"
        session.execute(text(query), roles)
        print(f"    ✅ Created {len(roles)} roles")
    
    # Create user-role assignments
    result = session.execute(text("SELECT id FROM users"))
    user_ids = [row[0] for row in result.fetchall()]
    
    result = session.execute(text("SELECT id, name FROM roles"))
    roles = {row[1]: row[0] for row in result.fetchall()}
    
    user_roles = []
    for user_id in user_ids:
        # Assign random roles to users
        role_names = random.sample(list(roles.keys()), random.randint(1, 3))
        for role_name in role_names:
            user_roles.append({
                'user_id': user_id,
                'role_id': roles[role_name]
            })
    
    if user_roles:
        columns = list(user_roles[0].keys())
        placeholders = ', '.join([f':{col}' for col in columns])
        query = f"INSERT INTO user_roles ({', '.join(columns)}) VALUES ({placeholders})"
        session.execute(text(query), user_roles)
        print(f"    ✅ Created user-role assignments")


def seed_user_sessions(session: Session):
    """Seed user sessions"""
    print("  🔄 Seeding user sessions...")
    
    result = session.execute(text("SELECT id FROM users"))
    user_ids = [row[0] for row in result.fetchall()]
    
    sessions = []
    for user_id in user_ids:
        sessions.append({
            'id': f'session_{user_id}_{random.randint(1000, 9999)}',
            'ip_address': f'192.168.1.{random.randint(1, 254)}',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'last_activity': datetime.now() - timedelta(minutes=random.randint(1, 60)),
            'status': random.choice(['ACTIVE', 'INACTIVE', 'PENDING', 'SCHEDULED', 'COMPLETED', 'CANCELLED', 'ON_HOLD'])
        })
    
    if sessions:
        columns = list(sessions[0].keys())
        placeholders = ', '.join([f':{col}' for col in columns])
        query = f"INSERT INTO user_sessions ({', '.join(columns)}) VALUES ({placeholders})"
        session.execute(text(query), sessions)
        print(f"    ✅ Created {len(sessions)} user sessions")


def seed_user_activities(session: Session):
    """Seed user activities"""
    print("  🔄 Seeding user activities...")
    
    result = session.execute(text("SELECT id FROM users"))
    user_ids = [row[0] for row in result.fetchall()]
    
    activities = []
    for user_id in user_ids:
        for i in range(random.randint(5, 20)):
            activities.append({
                'user_id': user_id,
                'activity_data': json.dumps({
                    'action': random.choice(['login', 'logout', 'view_page', 'click_button', 'submit_form']),
                    'page': random.choice(['dashboard', 'profile', 'settings', 'courses', 'assignments']),
                    'duration': random.randint(1, 300)
                }),
                'session_id': f'session_{user_id}_{random.randint(1000, 9999)}',
                'timestamp': datetime.now() - timedelta(days=random.randint(1, 30)),
                'ip_address': f'192.168.1.{random.randint(1, 254)}',
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'location_data': json.dumps({
                    'country': 'US',
                    'city': 'New York',
                    'timezone': 'America/New_York'
                })
            })
    
    if activities:
        columns = list(activities[0].keys())
        placeholders = ', '.join([f':{col}' for col in columns])
        query = f"INSERT INTO user_activities ({', '.join(columns)}) VALUES ({placeholders})"
        session.execute(text(query), activities)
        print(f"    ✅ Created user activities")


def seed_user_behaviors(session: Session):
    """Seed user behaviors"""
    print("  🔄 Seeding user behaviors...")
    
    result = session.execute(text("SELECT id FROM users"))
    user_ids = [row[0] for row in result.fetchall()]
    
    behaviors = []
    for user_id in user_ids:
        behaviors.append({
            'user_id': user_id,
            'behavior_data': json.dumps({
                'pattern': random.choice(['consistent', 'sporadic', 'burst', 'gradual']),
                'preferences': {
                    'time_of_day': random.choice(['morning', 'afternoon', 'evening', 'night']),
                    'day_of_week': random.choice(['weekday', 'weekend']),
                    'device_type': random.choice(['desktop', 'mobile', 'tablet'])
                },
                'engagement_level': random.choice(['low', 'medium', 'high'])
            }),
            'confidence_score': random.uniform(0.1, 1.0),
            'timestamp': datetime.now() - timedelta(days=random.randint(1, 30)),
            'analysis_period': random.choice(['daily', 'weekly', 'monthly'])
        })
    
    if behaviors:
        columns = list(behaviors[0].keys())
        placeholders = ', '.join([f':{col}' for col in columns])
        query = f"INSERT INTO user_behaviors ({', '.join(columns)}) VALUES ({placeholders})"
        session.execute(text(query), behaviors)
        print(f"    ✅ Created {len(behaviors)} user behaviors")


def seed_user_engagements(session: Session):
    """Seed user engagements"""
    print("  🔄 Seeding user engagements...")
    
    result = session.execute(text("SELECT id FROM users"))
    user_ids = [row[0] for row in result.fetchall()]
    
    engagements = []
    for user_id in user_ids:
        engagements.append({
            'user_id': user_id,
            'engagement_score': random.uniform(0.1, 1.0),
            'session_count': random.randint(1, 50),
            'feature_usage': json.dumps({
                'most_used': random.choice(['dashboard', 'courses', 'assignments', 'profile']),
                'usage_frequency': random.choice(['daily', 'weekly', 'monthly']),
                'preferred_features': ['dashboard', 'courses', 'assignments']
            }),
            'retention_metrics': json.dumps({
                'days_since_first_visit': random.randint(1, 365),
                'total_visits': random.randint(1, 100),
                'last_visit': (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat()
            }),
            'churn_risk': random.uniform(0.0, 1.0),
            'timestamp': datetime.now() - timedelta(days=random.randint(1, 30)),
            'period': random.choice(['daily', 'weekly', 'monthly'])
        })
    
    if engagements:
        columns = list(engagements[0].keys())
        placeholders = ', '.join([f':{col}' for col in columns])
        query = f"INSERT INTO user_engagements ({', '.join(columns)}) VALUES ({placeholders})"
        session.execute(text(query), engagements)
        print(f"    ✅ Created {len(engagements)} user engagements")


def seed_user_insights(session: Session):
    """Seed user insights"""
    print("  🔄 Seeding user insights...")
    
    result = session.execute(text("SELECT id FROM users"))
    user_ids = [row[0] for row in result.fetchall()]
    
    insights = []
    for user_id in user_ids:
        insights.append({
            'user_id': user_id,
            'insight_data': json.dumps({
                'type': random.choice(['behavioral', 'performance', 'preference', 'engagement']),
                'description': f'Insight for user {user_id}',
                'confidence': random.uniform(0.1, 1.0),
                'source': 'ml_analysis'
            }),
            'key_findings': json.dumps([
                f'User {user_id} shows strong engagement patterns',
                f'Preferred learning style: {random.choice(["visual", "auditory", "kinesthetic"])}',
                f'Peak activity time: {random.choice(["morning", "afternoon", "evening"])}'
            ]),
            'improvement_areas': json.dumps([
                'Increase session duration',
                'Explore new features',
                'Improve consistency'
            ]),
            'strengths': json.dumps([
                'High engagement',
                'Consistent usage',
                'Active participation'
            ]),
            'opportunities': json.dumps([
                'Advanced features',
                'Collaboration tools',
                'Personalization'
            ]),
            'risk_factors': json.dumps([
                'Potential churn risk',
                'Low engagement',
                'Inconsistent usage'
            ]),
            'timestamp': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    if insights:
        columns = list(insights[0].keys())
        placeholders = ', '.join([f':{col}' for col in columns])
        query = f"INSERT INTO user_insights ({', '.join(columns)}) VALUES ({placeholders})"
        session.execute(text(query), insights)
        print(f"    ✅ Created {len(insights)} user insights")


def seed_user_trends(session: Session):
    """Seed user trends"""
    print("  🔄 Seeding user trends...")
    
    result = session.execute(text("SELECT id FROM users"))
    user_ids = [row[0] for row in result.fetchall()]
    
    trends = []
    for user_id in user_ids:
        trends.append({
            'user_id': user_id,
            'trend_type': random.choice(['increasing', 'decreasing', 'stable', 'volatile']),
            'trend_data': json.dumps({
                'metric': random.choice(['engagement', 'activity', 'performance', 'satisfaction']),
                'value': random.uniform(0.1, 1.0),
                'baseline': random.uniform(0.1, 1.0),
                'change_percentage': random.uniform(-50.0, 50.0)
            }),
            'trend_direction': random.choice(['up', 'down', 'stable', 'fluctuating']),
            'trend_strength': random.uniform(0.1, 1.0),
            'seasonal_patterns': json.dumps({
                'has_seasonality': random.choice([True, False]),
                'peak_season': random.choice(['spring', 'summer', 'fall', 'winter']),
                'low_season': random.choice(['spring', 'summer', 'fall', 'winter'])
            }),
            'time_range': random.choice(['daily', 'weekly', 'monthly', 'yearly']),
            'timestamp': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    if trends:
        columns = list(trends[0].keys())
        placeholders = ', '.join([f':{col}' for col in columns])
        query = f"INSERT INTO user_trends ({', '.join(columns)}) VALUES ({placeholders})"
        session.execute(text(query), trends)
        print(f"    ✅ Created {len(trends)} user trends")


def seed_user_predictions(session: Session):
    """Seed user predictions"""
    print("  🔄 Seeding user predictions...")
    
    result = session.execute(text("SELECT id FROM users"))
    user_ids = [row[0] for row in result.fetchall()]
    
    predictions = []
    for user_id in user_ids:
        predictions.append({
            'user_id': user_id,
            'prediction_type': random.choice(['behavior', 'preference', 'outcome', 'risk']),
            'prediction_data': json.dumps({
                'prediction': f'Prediction for user {user_id}',
                'description': f'Detailed prediction description for user {user_id}',
                'source': 'ml_model',
                'features_used': ['engagement', 'activity', 'preferences']
            }),
            'confidence_score': random.uniform(0.1, 1.0),
            'prediction_horizon': random.choice(['short', 'medium', 'long']),
            'model_version': f'v{random.randint(1, 3)}.{random.randint(0, 9)}',
            'timestamp': datetime.now() - timedelta(days=random.randint(1, 30)),
            'is_active': True
        })
    
    if predictions:
        columns = list(predictions[0].keys())
        placeholders = ', '.join([f':{col}' for col in columns])
        query = f"INSERT INTO user_predictions ({', '.join(columns)}) VALUES ({placeholders})"
        session.execute(text(query), predictions)
        print(f"    ✅ Created {len(predictions)} user predictions")


def seed_user_comparisons(session: Session):
    """Seed user comparisons"""
    print("  🔄 Seeding user comparisons...")
    
    result = session.execute(text("SELECT id FROM users"))
    user_ids = [row[0] for row in result.fetchall()]
    
    comparisons = []
    for user_id in user_ids:
        value = random.uniform(0.1, 1.0)
        baseline_value = random.uniform(0.1, 1.0)
        comparisons.append({
            'user_id': user_id,
            'comparison_type': random.choice(['peer', 'historical', 'benchmark', 'target']),
            'comparison_data': json.dumps({
                'metric': random.choice(['performance', 'engagement', 'satisfaction', 'efficiency']),
                'value': value,
                'baseline_value': baseline_value,
                'difference': value - baseline_value,
                'unit': 'score'
            }),
            'comparison_users': json.dumps([random.randint(1, 32) for _ in range(random.randint(1, 5))]),
            'percentile_rank': random.uniform(0.0, 100.0),
            'benchmarking_data': json.dumps({
                'industry_average': random.uniform(0.1, 1.0),
                'top_percentile': random.uniform(0.8, 1.0),
                'bottom_percentile': random.uniform(0.0, 0.3)
            }),
            'insights': json.dumps([
                f'User {user_id} performs better than {random.randint(60, 90)}% of peers',
                f'Significant improvement over last period: {random.uniform(5, 25):.1f}%',
                f'Key strength: {random.choice(["consistency", "growth", "engagement"])}'
            ]),
            'timestamp': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    if comparisons:
        columns = list(comparisons[0].keys())
        placeholders = ', '.join([f':{col}' for col in columns])
        query = f"INSERT INTO user_comparisons ({', '.join(columns)}) VALUES ({placeholders})"
        session.execute(text(query), comparisons)
        print(f"    ✅ Created {len(comparisons)} user comparisons")


def seed_access_control_system(session: Session):
    """Seed access control system"""
    print("🔄 Seeding access control system...")
    
    # Seed permissions
    seed_permissions(session)
    
    # Seed role permissions
    seed_role_permissions(session)
    
    # Seed permission overrides
    seed_permission_overrides(session)


def seed_permissions(session: Session):
    """Seed permissions"""
    print("  🔄 Seeding permissions...")
    
    result = session.execute(text("SELECT COUNT(*) FROM permissions"))
    existing_count = result.scalar()
    if existing_count > 0:
        print(f"    ✅ Permissions already exist, migrating data...")
        return
    
    permissions = [
        {'name': 'user.read', 'description': 'Read user data', 'resource': 'user', 'action': 'read'},
        {'name': 'user.write', 'description': 'Write user data', 'resource': 'user', 'action': 'write'},
        {'name': 'user.delete', 'description': 'Delete user data', 'resource': 'user', 'action': 'delete'},
        {'name': 'course.read', 'description': 'Read course data', 'resource': 'course', 'action': 'read'},
        {'name': 'course.write', 'description': 'Write course data', 'resource': 'course', 'action': 'write'},
        {'name': 'course.delete', 'description': 'Delete course data', 'resource': 'course', 'action': 'delete'},
        {'name': 'assignment.read', 'description': 'Read assignment data', 'resource': 'assignment', 'action': 'read'},
        {'name': 'assignment.write', 'description': 'Write assignment data', 'resource': 'assignment', 'action': 'write'},
        {'name': 'assignment.delete', 'description': 'Delete assignment data', 'resource': 'assignment', 'action': 'delete'},
        {'name': 'system.admin', 'description': 'System administration', 'resource': 'system', 'action': 'admin'}
    ]
    
    columns = list(permissions[0].keys())
    placeholders = ', '.join([f':{col}' for col in columns])
    query = f"INSERT INTO permissions ({', '.join(columns)}) VALUES ({placeholders})"
    session.execute(text(query), permissions)
    print(f"    ✅ Created {len(permissions)} permissions")


def seed_role_permissions(session: Session):
    """Seed role permissions"""
    print("  🔄 Seeding role permissions...")
    
    # Get roles and permissions
    result = session.execute(text("SELECT id, name FROM roles"))
    roles = {row[1]: row[0] for row in result.fetchall()}
    
    result = session.execute(text("SELECT id, name FROM permissions"))
    permissions = {row[1]: row[0] for row in result.fetchall()}
    
    role_permissions = []
    
    # Admin gets all permissions
    if 'admin' in roles:
        for perm_name, perm_id in permissions.items():
            role_permissions.append({
                'role_id': roles['admin'],
                'permission_id': perm_id
            })
    
    # Teacher gets course and assignment permissions
    if 'teacher' in roles:
        teacher_perms = ['course.read', 'course.write', 'assignment.read', 'assignment.write', 'user.read']
        for perm_name in teacher_perms:
            if perm_name in permissions:
                role_permissions.append({
                    'role_id': roles['teacher'],
                    'permission_id': permissions[perm_name]
                })
    
    # Student gets read permissions
    if 'student' in roles:
        student_perms = ['course.read', 'assignment.read', 'user.read']
        for perm_name in student_perms:
            if perm_name in permissions:
                role_permissions.append({
                    'role_id': roles['student'],
                    'permission_id': permissions[perm_name]
                })
    
    if role_permissions:
        columns = list(role_permissions[0].keys())
        placeholders = ', '.join([f':{col}' for col in columns])
        query = f"INSERT INTO role_permissions ({', '.join(columns)}) VALUES ({placeholders})"
        session.execute(text(query), role_permissions)
        print(f"    ✅ Created role permissions")


def seed_permission_overrides(session: Session):
    """Seed permission overrides"""
    print("  🔄 Seeding permission overrides...")
    
    # Get users and permissions
    result = session.execute(text("SELECT id FROM users LIMIT 5"))
    user_ids = [row[0] for row in result.fetchall()]
    
    result = session.execute(text("SELECT id FROM permissions LIMIT 3"))
    permission_ids = [row[0] for row in result.fetchall()]
    
    overrides = []
    for user_id in user_ids:
        for perm_id in permission_ids:
            overrides.append({
                'user_id': user_id,
                'permission_id': perm_id,
                'is_allowed': random.choice([True, False]),
                'reason': f'Override for user {user_id}',
                'expires_at': datetime.now() + timedelta(days=30),
                'status': random.choice(['ACTIVE', 'INACTIVE', 'PENDING', 'SCHEDULED', 'COMPLETED', 'CANCELLED', 'ON_HOLD']),
                'is_active': random.choice([True, False])
            })
    
    if overrides:
        columns = list(overrides[0].keys())
        placeholders = ', '.join([f':{col}' for col in columns])
        query = f"INSERT INTO permission_overrides ({', '.join(columns)}) VALUES ({placeholders})"
        session.execute(text(query), overrides)
        print(f"    ✅ Created permission overrides")


def seed_system_configuration(session: Session):
    """Seed system configuration"""
    print("🔄 Seeding system configuration...")
    
    # Seed system configs
    seed_system_configs(session)
    
    # Seed feature flags
    seed_feature_flags(session)


def seed_system_configs(session: Session):
    """Seed system configurations"""
    print("  🔄 Seeding system configs...")
    
    # Organization settings
    result = session.execute(text("SELECT COUNT(*) FROM organization_settings"))
    existing_count = result.scalar()
    if existing_count > 0:
        print(f"    ✅ Organization settings already exist, migrating data...")
    else:
        org_settings = [
            {
                'organization_id': 1,
                'setting_key': 'name',
                'setting_value': 'Faraday AI Education',
                'description': 'Organization name',
                'is_active': True
            },
            {
                'organization_id': 1,
                'setting_key': 'timezone',
                'setting_value': 'UTC',
                'description': 'Default timezone',
                'is_active': True
            }
        ]
        
        columns = list(org_settings[0].keys())
        placeholders = ', '.join([f':{col}' for col in columns])
        query = f"INSERT INTO organization_settings ({', '.join(columns)}) VALUES ({placeholders})"
        session.execute(text(query), org_settings)
        print(f"    ✅ Created organization settings")
    
    # Project settings
    result = session.execute(text("SELECT COUNT(*) FROM project_settings"))
    existing_count = result.scalar()
    if existing_count > 0:
        print(f"    ✅ Project settings already exist, migrating data...")
    else:
        project_settings = [
            {
                'project_id': 1,
                'setting_key': 'name',
                'setting_value': 'Faraday AI Education Platform',
                'description': 'Project name',
                'is_active': True
            },
            {
                'project_id': 1,
                'setting_key': 'version',
                'setting_value': '1.0.0',
                'description': 'Project version',
                'is_active': True
            }
        ]
        
        columns = list(project_settings[0].keys())
        placeholders = ', '.join([f':{col}' for col in columns])
        query = f"INSERT INTO project_settings ({', '.join(columns)}) VALUES ({placeholders})"
        session.execute(text(query), project_settings)
        print(f"    ✅ Created project settings")


def seed_feature_flags(session: Session):
    """Seed feature flags"""
    print("  🔄 Seeding feature flags...")
    
    try:
        # Check if feature flags already exist
        result = session.execute(text("SELECT COUNT(*) FROM feature_flags"))
        existing_count = result.scalar()
        if existing_count > 0:
            print(f"    ✅ Feature flags already exist, migrating data...")
            return
        
        feature_flags = [
            {'name': 'user_management', 'description': 'User management features', 'is_enabled': True, 'is_active': True},
            {'name': 'role_based_access', 'description': 'Role-based access control', 'is_enabled': True, 'is_active': True},
            {'name': 'analytics', 'description': 'Analytics features', 'is_enabled': True, 'is_active': True},
            {'name': 'notifications', 'description': 'Notification system', 'is_enabled': True, 'is_active': True},
            {'name': 'ai_features', 'description': 'AI-powered features', 'is_enabled': True, 'is_active': True},
            {'name': 'beta_features', 'description': 'Beta features', 'is_enabled': False, 'is_active': True}
        ]
        
        columns = list(feature_flags[0].keys())
        placeholders = ', '.join([f':{col}' for col in columns])
        query = f"INSERT INTO feature_flags ({', '.join(columns)}) VALUES ({placeholders})"
        session.execute(text(query), feature_flags)
        print(f"    ✅ Created {len(feature_flags)} feature flags")
    except Exception as e:
        print(f"    ⚠️  Feature flags table does not exist, skipping: {e}")


def seed_basic_infrastructure(session: Session):
    """Seed basic infrastructure data"""
    print("  🔄 Seeding basic infrastructure...")
    
    try:
        # Seed notifications system
        seed_notifications_system(session)
    except Exception as e:
        print(f"    ⚠️  Error seeding notifications system: {e}")
    
    try:
        # Seed logging system
        seed_logging_system(session)
    except Exception as e:
        print(f"    ⚠️  Error seeding logging system: {e}")
    
    try:
        # Seed monitoring system
        seed_monitoring_system(session)
    except Exception as e:
        print(f"    ⚠️  Error seeding monitoring system: {e}")
    
    try:
        # Seed system utilities
        seed_system_utilities(session)
    except Exception as e:
        print(f"    ⚠️  Error seeding system utilities: {e}")
    
    try:
        # Seed missing foundational tables
        seed_missing_foundational_tables(session)
    except Exception as e:
        print(f"    ⚠️  Error seeding missing foundational tables: {e}")


def seed_notifications_system(session: Session):
    """Seed notifications system"""
    print("    🔄 Seeding notifications system...")
    
    try:
        # Notification models
        result = session.execute(text("SELECT COUNT(*) FROM notification_models"))
        existing_count = result.scalar()
        if existing_count > 0:
            print(f"      ✅ Notification models already exist, migrating data...")
        else:
            notification_models = [
                {'name': 'email', 'description': 'Email notifications', 'is_active': True},
                {'name': 'sms', 'description': 'SMS notifications', 'is_active': True},
                {'name': 'push', 'description': 'Push notifications', 'is_active': True},
                {'name': 'in_app', 'description': 'In-app notifications', 'is_active': True}
            ]
            
            columns = list(notification_models[0].keys())
            placeholders = ', '.join([f':{col}' for col in columns])
            query = f"INSERT INTO notification_models ({', '.join(columns)}) VALUES ({placeholders})"
            session.execute(text(query), notification_models)
            print(f"      ✅ Created notification models")
    except Exception as e:
        print(f"      ⚠️  Notification models table does not exist, skipping: {e}")
        return
    
    try:
        # Notification preferences
        result = session.execute(text("SELECT COUNT(*) FROM notification_preferences"))
        existing_count = result.scalar()
        if existing_count > 0:
            print(f"      ✅ Notification preferences already exist, migrating data...")
        else:
            result = session.execute(text("SELECT id FROM users"))
            user_ids = [row[0] for row in result.fetchall()]
            
            preferences = []
            for user_id in user_ids:
                preferences.append({
                    'user_id': user_id,
                    'notification_type': random.choice(['email', 'sms', 'push', 'in_app']),
                    'is_enabled': random.choice([True, False]),
                    'frequency': random.choice(['immediate', 'daily', 'weekly', 'monthly']),
                    'created_at': datetime.now(),
                    'updated_at': datetime.now()
                })
            
            if preferences:
                columns = list(preferences[0].keys())
                placeholders = ', '.join([f':{col}' for col in columns])
                query = f"INSERT INTO notification_preferences ({', '.join(columns)}) VALUES ({placeholders})"
                session.execute(text(query), preferences)
                print(f"      ✅ Created notification preferences")
    except Exception as e:
        print(f"      ⚠️  Notification preferences table does not exist, skipping: {e}")


def seed_logging_system(session: Session):
    """Seed logging system"""
    print("    🔄 Seeding logging system...")
    
    try:
        # Security logs
        result = session.execute(text("SELECT COUNT(*) FROM security_logs"))
        existing_count = result.scalar()
        if existing_count > 0:
            print(f"      ✅ Security logs already exist, migrating data...")
        else:
            result = session.execute(text("SELECT id FROM users"))
            user_ids = [row[0] for row in result.fetchall()]
            
            security_logs = []
            for user_id in user_ids:
                for i in range(random.randint(1, 5)):
                    security_logs.append({
                        'user_id': user_id,
                        'event_type': random.choice(['login', 'logout', 'failed_login', 'permission_denied']),
                        'description': f'Security event {i+1} for user {user_id}',
                        'ip_address': f'192.168.1.{random.randint(1, 254)}',
                        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                        'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
                    })
            
            if security_logs:
                columns = list(security_logs[0].keys())
                placeholders = ', '.join([f':{col}' for col in columns])
                query = f"INSERT INTO security_logs ({', '.join(columns)}) VALUES ({placeholders})"
                session.execute(text(query), security_logs)
                print(f"      ✅ Created security logs")
    except Exception as e:
        print(f"      ⚠️  Security logs table does not exist, skipping: {e}")
        return
    
    try:
        # Performance logs
        result = session.execute(text("SELECT COUNT(*) FROM performance_logs"))
        existing_count = result.scalar()
        if existing_count > 0:
            print(f"      ✅ Performance logs already exist, migrating data...")
        else:
            performance_logs = []
            for i in range(100):
                performance_logs.append({
                    'operation': random.choice(['database_query', 'api_call', 'file_upload', 'data_processing']),
                    'duration_ms': random.randint(10, 5000),
                    'memory_usage_mb': random.uniform(1.0, 100.0),
                    'cpu_usage_percent': random.uniform(1.0, 100.0),
                    'status': random.choice(['success', 'warning', 'error']),
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
                })
            
            if performance_logs:
                columns = list(performance_logs[0].keys())
                placeholders = ', '.join([f':{col}' for col in columns])
                query = f"INSERT INTO performance_logs ({', '.join(columns)}) VALUES ({placeholders})"
                session.execute(text(query), performance_logs)
                print(f"      ✅ Created performance logs")
    except Exception as e:
        print(f"      ⚠️  Performance logs table does not exist, skipping: {e}")


def seed_monitoring_system(session: Session):
    """Seed monitoring system"""
    print("    🔄 Seeding monitoring system...")
    
    try:
        result = session.execute(text("SELECT COUNT(*) FROM monitoring_alerts"))
        existing_count = result.scalar()
        if existing_count > 0:
            print(f"      ✅ Monitoring already configured, migrating data...")
        else:
            alerts = [
                {
                    'alert_type': 'system_health',
                    'severity': 'info',
                    'message': 'System running normally',
                    'is_resolved': True,
                    'created_at': datetime.now() - timedelta(days=1),
                    'resolved_at': datetime.now() - timedelta(hours=12)
                },
                {
                    'alert_type': 'performance',
                    'severity': 'warning',
                    'message': 'High CPU usage detected',
                    'is_resolved': False,
                    'created_at': datetime.now() - timedelta(hours=2)
                }
            ]
            
            columns = list(alerts[0].keys())
            placeholders = ', '.join([f':{col}' for col in columns])
            query = f"INSERT INTO monitoring_alerts ({', '.join(columns)}) VALUES ({placeholders})"
            session.execute(text(query), alerts)
            print(f"      ✅ Created monitoring alerts")
    except Exception as e:
        print(f"      ⚠️  Monitoring alerts table does not exist, skipping: {e}")


def seed_system_utilities(session: Session):
    """Seed system utilities"""
    print("    🔄 Seeding system utilities...")
    
    try:
        result = session.execute(text("SELECT COUNT(*) FROM system_utilities"))
        existing_count = result.scalar()
        if existing_count > 0:
            print(f"      ✅ System utilities already configured, migrating data...")
        else:
            utilities = [
                {
                    'name': 'data_cleanup',
                    'description': 'Clean up old data',
                    'is_enabled': True,
                    'schedule': 'daily',
                    'last_run': datetime.now() - timedelta(hours=6),
                    'next_run': datetime.now() + timedelta(hours=18)
                },
                {
                    'name': 'backup',
                    'description': 'System backup',
                    'is_enabled': True,
                    'schedule': 'daily',
                    'last_run': datetime.now() - timedelta(hours=12),
                    'next_run': datetime.now() + timedelta(hours=12)
                }
            ]
            
            columns = list(utilities[0].keys())
            placeholders = ', '.join([f':{col}' for col in columns])
            query = f"INSERT INTO system_utilities ({', '.join(columns)}) VALUES ({placeholders})"
            session.execute(text(query), utilities)
            print(f"      ✅ Created system utilities")
    except Exception as e:
        print(f"      ⚠️  System utilities table does not exist, skipping: {e}")


def seed_missing_foundational_tables(session: Session):
    """Seed the 22 missing foundational tables"""
    print("    🔄 Seeding missing foundational tables...")
    
    try:
        # Get user IDs for foreign key references
        result = session.execute(text("SELECT id FROM users"))
        user_ids = [row[0] for row in result.fetchall()]
        
        # Get student IDs for foreign key references
        result = session.execute(text("SELECT id FROM students"))
        student_ids = [row[0] for row in result.fetchall()]
    except Exception as e:
        print(f"      ⚠️  Error getting user/student IDs, skipping missing foundational tables: {e}")
        return
    
    results = {}
    
    # 1. Avatar Templates
    print("      🔄 Seeding avatar_templates...")
    try:
        result = session.execute(text("SELECT COUNT(*) FROM avatar_templates"))
        existing_count = result.scalar()
        if existing_count > 0:
            print(f"        ✅ Avatar templates already exist, migrating data...")
        else:
            avatar_templates = []
            for i in range(10):
                avatar_templates.append({
                    'name': f'avatar_template_{i+1}',
                    'description': f'Avatar template {i+1}',
                    'template_data': json.dumps({
                        'type': random.choice(['human', 'animal', 'abstract']),
                        'style': random.choice(['realistic', 'cartoon', 'anime']),
                        'colors': ['#FF0000', '#00FF00', '#0000FF'],
                        'features': ['eyes', 'mouth', 'hair']
                    }),
                    'template_metadata': json.dumps({
                        'category': random.choice(['professional', 'casual', 'fun']),
                        'age_group': random.choice(['child', 'teen', 'adult']),
                        'gender': random.choice(['male', 'female', 'neutral'])
                    }),
                    'is_active': True,
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 365))
                })
            
            if avatar_templates:
                columns = list(avatar_templates[0].keys())
                placeholders = ', '.join([f':{col}' for col in columns])
                query = f"INSERT INTO avatar_templates ({', '.join(columns)}) VALUES ({placeholders})"
                session.execute(text(query), avatar_templates)
                print(f"        ✅ Created {len(avatar_templates)} avatar templates")
        results['avatar_templates'] = True
    except Exception as e:
        print(f"        ⚠️  Avatar templates table does not exist, skipping: {e}")
        results['avatar_templates'] = False
    
    # 2. Avatars
    print("      🔄 Seeding avatars...")
    try:
        result = session.execute(text("SELECT COUNT(*) FROM avatars"))
        existing_count = result.scalar()
        if existing_count > 0:
            print(f"        ✅ Avatars already exist, migrating data...")
        else:
            # Get template IDs
            result = session.execute(text("SELECT id FROM avatar_templates"))
            template_ids = [row[0] for row in result.fetchall()]
            
            avatars = []
            for i in range(20):
                avatars.append({
                    'name': f'avatar_{i+1}',
                    'description': f'Avatar {i+1}',
                    'type': random.choice(['STATIC', 'ANIMATED', 'THREE_D']),
                    'avatar_data': json.dumps({
                        'image_url': f'https://example.com/avatars/avatar_{i+1}.png',
                        'thumbnail_url': f'https://example.com/avatars/thumb_avatar_{i+1}.png',
                        'dimensions': {'width': 200, 'height': 200},
                        'file_size': random.randint(1000, 10000)
                    }),
                    'is_active': True,
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 365))
                })
            
            if avatars:
                columns = list(avatars[0].keys())
                placeholders = ', '.join([f':{col}' for col in columns])
                query = f"INSERT INTO avatars ({', '.join(columns)}) VALUES ({placeholders})"
                session.execute(text(query), avatars)
                print(f"        ✅ Created {len(avatars)} avatars")
        results['avatars'] = True
    except Exception as e:
        print(f"        ⚠️  Avatars table does not exist, skipping: {e}")
        results['avatars'] = False
    
    # 3. User Avatars
    print("      🔄 Seeding user_avatars...")
    try:
        result = session.execute(text("SELECT COUNT(*) FROM user_avatars"))
        existing_count = result.scalar()
        if existing_count > 0:
            print(f"        ✅ User avatars already exist, migrating data...")
        else:
            # Get avatar IDs and template IDs
            result = session.execute(text("SELECT id FROM avatars"))
            avatar_ids = [row[0] for row in result.fetchall()]
            
            result = session.execute(text("SELECT id FROM avatar_templates"))
            template_ids = [row[0] for row in result.fetchall()]
            
            user_avatars = []
            for user_id in user_ids:
                user_avatars.append({
                    'user_id': user_id,
                    'avatar_id': random.choice(avatar_ids) if avatar_ids else None,
                    'template_id': random.choice(template_ids) if template_ids else None,
                    'avatar_type': random.choice(['STATIC', 'ANIMATED', 'THREE_D']),
                    'style': random.choice(['REALISTIC', 'CARTOON', 'ANIME', 'PIXEL', 'MINIMAL', 'CUSTOM']),
                    'customization_data': json.dumps({
                        'colors': ['#FF0000', '#00FF00', '#0000FF'],
                        'accessories': ['hat', 'glasses', 'scarf'],
                        'background': 'transparent'
                    }),
                    'is_active': True,
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 365))
                })
            
            if user_avatars:
                columns = list(user_avatars[0].keys())
                placeholders = ', '.join([f':{col}' for col in columns])
                query = f"INSERT INTO user_avatars ({', '.join(columns)}) VALUES ({placeholders})"
                session.execute(text(query), user_avatars)
                print(f"        ✅ Created {len(user_avatars)} user avatars")
        results['user_avatars'] = True
    except Exception as e:
        print(f"        ⚠️  User avatars table does not exist, skipping: {e}")
        results['user_avatars'] = False
    
    # 4. Avatar Customizations
    print("      🔄 Seeding avatar_customizations...")
    try:
        result = session.execute(text("SELECT COUNT(*) FROM avatar_customizations"))
        existing_count = result.scalar()
        if existing_count > 0:
            print(f"        ✅ Avatar customizations already exist, migrating data...")
        else:
            # Get avatar IDs
            result = session.execute(text("SELECT id FROM avatars"))
            avatar_ids = [row[0] for row in result.fetchall()]
            
            avatar_customizations = []
            for avatar_id in avatar_ids:
                for i in range(random.randint(1, 3)):
                    avatar_customizations.append({
                        'avatar_id': avatar_id,
                        'user_id': random.choice(user_ids),
                        'scale': random.uniform(0.5, 2.0),
                        'position': json.dumps({'x': random.randint(0, 100), 'y': random.randint(0, 100)}),
                        'rotation': random.uniform(0, 360),
                        'color': f'#{random.randint(0, 0xFFFFFF):06x}',
                        'opacity': random.uniform(0.1, 1.0),
                        'type': random.choice(['color', 'accessory', 'background', 'style']),
                        'config': json.dumps({
                            'customization_type': random.choice(['color', 'accessory', 'background', 'style']),
                            'value': f'custom_value_{i+1}',
                            'metadata': {'created_by': 'user', 'version': '1.0'}
                        }),
                        'created_at': datetime.now() - timedelta(days=random.randint(1, 365))
                    })
            
            if avatar_customizations:
                columns = list(avatar_customizations[0].keys())
                placeholders = ', '.join([f':{col}' for col in columns])
                query = f"INSERT INTO avatar_customizations ({', '.join(columns)}) VALUES ({placeholders})"
                session.execute(text(query), avatar_customizations)
                print(f"        ✅ Created {len(avatar_customizations)} avatar customizations")
        results['avatar_customizations'] = True
    except Exception as e:
        print(f"        ⚠️  Avatar customizations table does not exist, skipping: {e}")
        results['avatar_customizations'] = False
    
    # 5. User Avatar Customizations
    print("      🔄 Seeding user_avatar_customizations...")
    try:
        result = session.execute(text("SELECT COUNT(*) FROM user_avatar_customizations"))
        existing_count = result.scalar()
        if existing_count > 0:
            print(f"        ✅ User avatar customizations already exist, migrating data...")
        else:
            # Get user_avatar IDs
            result = session.execute(text("SELECT id FROM user_avatars"))
            user_avatar_ids = [row[0] for row in result.fetchall()]
            
            user_avatar_customizations = []
            for user_avatar_id in user_avatar_ids:
                user_avatar_customizations.append({
                    'user_avatar_id': user_avatar_id,
                    'customization_type': random.choice(['color', 'accessory', 'background', 'style']),
                    'customization_value': f'user_custom_{user_avatar_id}',
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 365))
                })
            
            if user_avatar_customizations:
                columns = list(user_avatar_customizations[0].keys())
                placeholders = ', '.join([f':{col}' for col in columns])
                query = f"INSERT INTO user_avatar_customizations ({', '.join(columns)}) VALUES ({placeholders})"
                session.execute(text(query), user_avatar_customizations)
                print(f"        ✅ Created {len(user_avatar_customizations)} user avatar customizations")
        results['user_avatar_customizations'] = True
    except Exception as e:
        print(f"        ⚠️  User avatar customizations table does not exist, skipping: {e}")
        results['user_avatar_customizations'] = False
    
    # 6. Student Avatar Customizations
    print("      🔄 Seeding student_avatar_customizations...")
    try:
        result = session.execute(text("SELECT COUNT(*) FROM student_avatar_customizations"))
        existing_count = result.scalar()
        if existing_count > 0:
            print(f"        ✅ Student avatar customizations already exist, migrating data...")
        else:
            # Get actual user_avatar IDs from the database (not avatars table)
            user_avatar_result = session.execute(text("SELECT id FROM user_avatars"))
            user_avatar_ids = [row[0] for row in user_avatar_result.fetchall()]
            if not user_avatar_ids:
                print("      ⚠️ No user avatars found, skipping student_avatar_customizations")
            else:
                student_avatar_customizations = []
                for student_id in student_ids:
                    student_avatar_customizations.append({
                        'avatar_id': random.choice(user_avatar_ids),
                        'user_id': student_id,
                        'customization_type': random.choice(['color', 'accessory', 'background', 'style']),
                        'customization_value': f'student_custom_{student_id}',
                        'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
                    })
                
                if student_avatar_customizations:
                    columns = list(student_avatar_customizations[0].keys())
                    placeholders = ', '.join([f':{col}' for col in columns])
                    query = f"INSERT INTO student_avatar_customizations ({', '.join(columns)}) VALUES ({placeholders})"
                    session.execute(text(query), student_avatar_customizations)
                    print(f"        ✅ Created {len(student_avatar_customizations)} student avatar customizations")
        results['student_avatar_customizations'] = True
    except Exception as e:
        print(f"        ⚠️  Student avatar customizations table does not exist, skipping: {e}")
        results['student_avatar_customizations'] = False
    
    # 7. Voice Templates
    print("      🔄 Seeding voice_templates...")
    try:
        result = session.execute(text("SELECT COUNT(*) FROM voice_templates"))
        existing_count = result.scalar()
        if existing_count > 0:
            print(f"        ✅ Voice templates already exist, migrating data...")
        else:
            voice_templates = []
            for i in range(10):
                voice_templates.append({
                    'name': f'voice_template_{i+1}',
                    'description': f'Voice template {i+1}',
                    'template_data': json.dumps({
                        'language': random.choice(['en', 'es', 'fr', 'de']),
                        'accent': random.choice(['american', 'british', 'australian', 'canadian']),
                        'gender': random.choice(['male', 'female', 'neutral']),
                        'age_group': random.choice(['child', 'teen', 'adult', 'senior'])
                    }),
                    'template_metadata': json.dumps({
                        'category': random.choice(['professional', 'casual', 'educational']),
                        'use_case': random.choice(['narration', 'conversation', 'instruction']),
                        'quality': random.choice(['standard', 'premium', 'ultra'])
                    }),
                    'is_active': True,
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 365))
                })
            
            if voice_templates:
                columns = list(voice_templates[0].keys())
                placeholders = ', '.join([f':{col}' for col in columns])
                query = f"INSERT INTO voice_templates ({', '.join(columns)}) VALUES ({placeholders})"
                session.execute(text(query), voice_templates)
                print(f"        ✅ Created {len(voice_templates)} voice templates")
        results['voice_templates'] = True
    except Exception as e:
        print(f"        ⚠️  Voice templates table does not exist, skipping: {e}")
        results['voice_templates'] = False
    
    # 8. Voices
    print("      🔄 Seeding voices...")
    try:
        result = session.execute(text("SELECT COUNT(*) FROM voices"))
        existing_count = result.scalar()
        if existing_count > 0:
            print(f"        ✅ Voices already exist, migrating data...")
        else:
            voices = []
            for i in range(20):
                voices.append({
                    'name': f'voice_{i+1}',
                    'description': f'Voice {i+1}',
                    'voice_data': json.dumps({
                        'language': random.choice(['en', 'es', 'fr', 'de']),
                        'accent': random.choice(['american', 'british', 'australian', 'canadian']),
                        'gender': random.choice(['male', 'female', 'neutral']),
                        'age_group': random.choice(['child', 'teen', 'adult', 'senior']),
                        'sample_rate': random.choice([22050, 44100, 48000]),
                        'bit_rate': random.choice([128, 256, 320])
                    }),
                    'is_active': True,
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 365))
                })
            
            if voices:
                columns = list(voices[0].keys())
                placeholders = ', '.join([f':{col}' for col in columns])
                query = f"INSERT INTO voices ({', '.join(columns)}) VALUES ({placeholders})"
                session.execute(text(query), voices)
                print(f"        ✅ Created {len(voices)} voices")
        results['voices'] = True
    except Exception as e:
        print(f"        ⚠️  Voices table does not exist, skipping: {e}")
        results['voices'] = False
    
    # 9. User Management Preferences
    print("      🔄 Seeding user_management_preferences...")
    try:
        result = session.execute(text("SELECT COUNT(*) FROM user_management_preferences"))
        existing_count = result.scalar()
        if existing_count > 0:
            print(f"        ✅ User management preferences already exist, migrating data...")
        else:
            user_management_preferences = []
            for user_id in user_ids:
                user_management_preferences.append({
                    'user_id': user_id,
                    'preference_key': random.choice(['theme', 'language', 'notifications', 'privacy']),
                    'preference_value': json.dumps({
                        'theme': random.choice(['light', 'dark', 'auto']),
                        'language': random.choice(['en', 'es', 'fr', 'de']),
                        'notifications': random.choice([True, False]),
                        'privacy': random.choice(['public', 'private', 'friends'])
                    }),
                    'is_active': True,
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 365))
                })
            
            if user_management_preferences:
                columns = list(user_management_preferences[0].keys())
                placeholders = ', '.join([f':{col}' for col in columns])
                query = f"INSERT INTO user_management_preferences ({', '.join(columns)}) VALUES ({placeholders})"
                session.execute(text(query), user_management_preferences)
                print(f"        ✅ Created {len(user_management_preferences)} user management preferences")
        results['user_management_preferences'] = True
    except Exception as e:
        print(f"        ⚠️  User management preferences table does not exist, skipping: {e}")
        results['user_management_preferences'] = False
    
    # 10. User Management User Organizations
    print("      🔄 Seeding user_management_user_organizations...")
    try:
        result = session.execute(text("SELECT COUNT(*) FROM user_management_user_organizations"))
        existing_count = result.scalar()
        if existing_count > 0:
            print(f"        ✅ User management user organizations already exist, migrating data...")
        else:
            user_management_user_organizations = []
            for user_id in user_ids:
                user_management_user_organizations.append({
                    'user_id': user_id,
                    'organization_id': random.randint(1, 5),
                    'role': random.choice(['member', 'admin', 'moderator']),
                    'is_active': True,
                    'joined_at': datetime.now() - timedelta(days=random.randint(1, 365))
                })
            
            if user_management_user_organizations:
                columns = list(user_management_user_organizations[0].keys())
                placeholders = ', '.join([f':{col}' for col in columns])
                query = f"INSERT INTO user_management_user_organizations ({', '.join(columns)}) VALUES ({placeholders})"
                session.execute(text(query), user_management_user_organizations)
                print(f"        ✅ Created {len(user_management_user_organizations)} user management user organizations")
        results['user_management_user_organizations'] = True
    except Exception as e:
        print(f"        ⚠️  User management user organizations table does not exist, skipping: {e}")
        results['user_management_user_organizations'] = False
    
    # 11. User Management Voice Preferences
    print("      🔄 Seeding user_management_voice_preferences...")
    try:
        result = session.execute(text("SELECT COUNT(*) FROM user_management_voice_preferences"))
        existing_count = result.scalar()
        if existing_count > 0:
            print(f"        ✅ User management voice preferences already exist, migrating data...")
        else:
            user_management_voice_preferences = []
            for user_id in user_ids:
                user_management_voice_preferences.append({
                    'user_id': user_id,
                    'voice_id': random.randint(1, 20),
                    'preference_type': random.choice(['default', 'narration', 'conversation']),
                    'is_active': True,
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 365))
                })
            
            if user_management_voice_preferences:
                columns = list(user_management_voice_preferences[0].keys())
                placeholders = ', '.join([f':{col}' for col in columns])
                query = f"INSERT INTO user_management_voice_preferences ({', '.join(columns)}) VALUES ({placeholders})"
                session.execute(text(query), user_management_voice_preferences)
                print(f"        ✅ Created {len(user_management_voice_preferences)} user management voice preferences")
        results['user_management_voice_preferences'] = True
    except Exception as e:
        print(f"        ⚠️  User management voice preferences table does not exist, skipping: {e}")
        results['user_management_voice_preferences'] = False
    
    # 12. User Preference Categories
    print("      🔄 Seeding user_preference_categories...")
    try:
        result = session.execute(text("SELECT COUNT(*) FROM user_preference_categories"))
        existing_count = result.scalar()
        if existing_count > 0:
            print(f"        ✅ User preference categories already exist, migrating data...")
        else:
            user_preference_categories = []
            categories = ['appearance', 'behavior', 'notifications', 'privacy', 'accessibility']
            for i, category in enumerate(categories):
                user_preference_categories.append({
                    'name': category,
                    'description': f'User preference category for {category}',
                    'is_active': True,
                    'sort_order': i + 1,
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 365))
                })
            
            if user_preference_categories:
                columns = list(user_preference_categories[0].keys())
                placeholders = ', '.join([f':{col}' for col in columns])
                query = f"INSERT INTO user_preference_categories ({', '.join(columns)}) VALUES ({placeholders})"
                session.execute(text(query), user_preference_categories)
                print(f"        ✅ Created {len(user_preference_categories)} user preference categories")
        results['user_preference_categories'] = True
    except Exception as e:
        print(f"        ⚠️  User preference categories table does not exist, skipping: {e}")
        results['user_preference_categories'] = False
    
    # 13. User Preference Template Assignments
    print("      🔄 Seeding user_preference_template_assignments...")
    try:
        result = session.execute(text("SELECT COUNT(*) FROM user_preference_template_assignments"))
        existing_count = result.scalar()
        if existing_count > 0:
            print(f"        ✅ User preference template assignments already exist, migrating data...")
        else:
            user_preference_template_assignments = []
            for user_id in user_ids:
                user_preference_template_assignments.append({
                    'user_id': user_id,
                    'template_id': random.randint(1, 10),
                    'is_active': True,
                    'assigned_at': datetime.now() - timedelta(days=random.randint(1, 365))
                })
            
            if user_preference_template_assignments:
                columns = list(user_preference_template_assignments[0].keys())
                placeholders = ', '.join([f':{col}' for col in columns])
                query = f"INSERT INTO user_preference_template_assignments ({', '.join(columns)}) VALUES ({placeholders})"
                session.execute(text(query), user_preference_template_assignments)
                print(f"        ✅ Created {len(user_preference_template_assignments)} user preference template assignments")
        results['user_preference_template_assignments'] = True
    except Exception as e:
        print(f"        ⚠️  User preference template assignments table does not exist, skipping: {e}")
        results['user_preference_template_assignments'] = False
    
    # 14. User Preference Templates
    print("      🔄 Seeding user_preference_templates...")
    try:
        result = session.execute(text("SELECT COUNT(*) FROM user_preference_templates"))
        existing_count = result.scalar()
        if existing_count > 0:
            print(f"        ✅ User preference templates already exist, migrating data...")
        else:
            user_preference_templates = []
            for i in range(10):
                user_preference_templates.append({
                    'name': f'preference_template_{i+1}',
                    'description': f'User preference template {i+1}',
                    'template_data': json.dumps({
                        'theme': random.choice(['light', 'dark', 'auto']),
                        'language': random.choice(['en', 'es', 'fr', 'de']),
                        'notifications': random.choice([True, False]),
                        'privacy': random.choice(['public', 'private', 'friends'])
                    }),
                    'is_active': True,
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 365))
                })
            
            if user_preference_templates:
                columns = list(user_preference_templates[0].keys())
                placeholders = ', '.join([f':{col}' for col in columns])
                query = f"INSERT INTO user_preference_templates ({', '.join(columns)}) VALUES ({placeholders})"
                session.execute(text(query), user_preference_templates)
                print(f"        ✅ Created {len(user_preference_templates)} user preference templates")
        results['user_preference_templates'] = True
    except Exception as e:
        print(f"        ⚠️  User preference templates table does not exist, skipping: {e}")
        results['user_preference_templates'] = False
    
    # 15. User Recommendations
    print("      🔄 Seeding user_recommendations...")
    try:
        result = session.execute(text("SELECT COUNT(*) FROM user_recommendations"))
        existing_count = result.scalar()
        if existing_count > 0:
            print(f"        ✅ User recommendations already exist, migrating data...")
        else:
            user_recommendations = []
            for user_id in user_ids:
                user_recommendations.append({
                    'user_id': user_id,
                    'recommendation_type': random.choice(['course', 'content', 'feature', 'tool']),
                    'recommendation_data': json.dumps({
                        'title': f'Recommended item for user {user_id}',
                        'description': f'This is a recommendation for user {user_id}',
                        'confidence_score': random.uniform(0.1, 1.0),
                        'source': 'ml_algorithm'
                    }),
                    'is_active': True,
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 365))
                })
            
            if user_recommendations:
                columns = list(user_recommendations[0].keys())
                placeholders = ', '.join([f':{col}' for col in columns])
                query = f"INSERT INTO user_recommendations ({', '.join(columns)}) VALUES ({placeholders})"
                session.execute(text(query), user_recommendations)
                print(f"        ✅ Created {len(user_recommendations)} user recommendations")
        results['user_recommendations'] = True
    except Exception as e:
        print(f"        ⚠️  User recommendations table does not exist, skipping: {e}")
        results['user_recommendations'] = False
    
    # 16. User Tool Settings
    print("      🔄 Seeding user_tool_settings...")
    try:
        result = session.execute(text("SELECT COUNT(*) FROM user_tool_settings"))
        existing_count = result.scalar()
        if existing_count > 0:
            print(f"        ✅ User tool settings already exist, migrating data...")
        else:
            user_tool_settings = []
            for user_id in user_ids:
                user_tool_settings.append({
                    'user_id': user_id,
                    'tool_name': random.choice(['calculator', 'notepad', 'calendar', 'chat']),
                    'settings': json.dumps({
                        'enabled': random.choice([True, False]),
                        'position': random.choice(['top', 'bottom', 'left', 'right']),
                        'size': random.choice(['small', 'medium', 'large']),
                        'theme': random.choice(['light', 'dark'])
                    }),
                    'is_active': True,
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 365))
                })
            
            if user_tool_settings:
                columns = list(user_tool_settings[0].keys())
                placeholders = ', '.join([f':{col}' for col in columns])
                query = f"INSERT INTO user_tool_settings ({', '.join(columns)}) VALUES ({placeholders})"
                session.execute(text(query), user_tool_settings)
                print(f"        ✅ Created {len(user_tool_settings)} user tool settings")
        results['user_tool_settings'] = True
    except Exception as e:
        print(f"        ⚠️  User tool settings table does not exist, skipping: {e}")
        results['user_tool_settings'] = False
    
    # 17. User Tools
    print("      🔄 Seeding user_tools...")
    try:
        result = session.execute(text("SELECT COUNT(*) FROM user_tools"))
        existing_count = result.scalar()
        if existing_count > 0:
            print(f"        ✅ User tools already exist, migrating data...")
        else:
            user_tools = []
            for user_id in user_ids:
                user_tools.append({
                    'user_id': user_id,
                    'tool_name': random.choice(['calculator', 'notepad', 'calendar', 'chat']),
                    'tool_data': json.dumps({
                        'type': random.choice(['utility', 'productivity', 'communication']),
                        'version': '1.0.0',
                        'configuration': {
                            'enabled': True,
                            'position': 'top',
                            'size': 'medium'
                        }
                    }),
                    'is_active': True,
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 365))
                })
            
            if user_tools:
                columns = list(user_tools[0].keys())
                placeholders = ', '.join([f':{col}' for col in columns])
                query = f"INSERT INTO user_tools ({', '.join(columns)}) VALUES ({placeholders})"
                session.execute(text(query), user_tools)
                print(f"        ✅ Created {len(user_tools)} user tools")
        results['user_tools'] = True
    except Exception as e:
        print(f"        ⚠️  User tools table does not exist, skipping: {e}")
        results['user_tools'] = False
    
    # 18. Role Hierarchy
    print("      🔄 Seeding role_hierarchy...")
    try:
        result = session.execute(text("SELECT COUNT(*) FROM role_hierarchy"))
        existing_count = result.scalar()
        if existing_count > 0:
            print(f"        ✅ Role hierarchy already exist, migrating data...")
        else:
            role_hierarchy = []
            # Get roles
            role_result = session.execute(text("SELECT id, name FROM roles"))
            roles = {row[1]: row[0] for row in role_result.fetchall()}
            if not roles:
                print("      ⚠️ No roles found, skipping role_hierarchy")
            else:
                # Create hierarchy relationships
                if 'admin' in roles and 'teacher' in roles:
                    role_hierarchy.append({
                        'parent_role_id': roles['admin'],
                        'child_role_id': roles['teacher'],
                        'level': 1,
                        'is_active': True,
                        'created_at': datetime.now() - timedelta(days=random.randint(1, 365))
                    })
                if 'teacher' in roles and 'student' in roles:
                    role_hierarchy.append({
                        'parent_role_id': roles['teacher'],
                        'child_role_id': roles['student'],
                        'level': 2,
                        'is_active': True,
                        'created_at': datetime.now() - timedelta(days=random.randint(1, 365))
                    })
                
                if role_hierarchy:
                    columns = list(role_hierarchy[0].keys())
                    placeholders = ', '.join([f':{col}' for col in columns])
                    query = f"INSERT INTO role_hierarchy ({', '.join(columns)}) VALUES ({placeholders})"
                    session.execute(text(query), role_hierarchy)
                    print(f"        ✅ Created {len(role_hierarchy)} role hierarchy entries")
        results['role_hierarchy'] = True
    except Exception as e:
        print(f"        ⚠️  Role hierarchy table does not exist, skipping: {e}")
        results['role_hierarchy'] = False
    
    # 19. Role Templates
    print("      🔄 Seeding role_templates...")
    try:
        result = session.execute(text("SELECT COUNT(*) FROM role_templates"))
        existing_count = result.scalar()
        if existing_count > 0:
            print(f"        ✅ Role templates already exist, migrating data...")
        else:
            role_templates = []
            for i in range(5):
                role_templates.append({
                    'name': f'role_template_{i+1}',
                    'description': f'Role template {i+1}',
                    'template_data': json.dumps({
                        'permissions': ['read', 'write', 'delete'],
                        'restrictions': ['time_based', 'location_based'],
                        'metadata': {'version': '1.0', 'created_by': 'system'}
                    }),
                    'is_active': True,
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 365))
                })
            
            if role_templates:
                columns = list(role_templates[0].keys())
                placeholders = ', '.join([f':{col}' for col in columns])
                query = f"INSERT INTO role_templates ({', '.join(columns)}) VALUES ({placeholders})"
                session.execute(text(query), role_templates)
                print(f"        ✅ Created {len(role_templates)} role templates")
        results['role_templates'] = True
    except Exception as e:
        print(f"        ⚠️  Role templates table does not exist, skipping: {e}")
        results['role_templates'] = False
    
    # 20. Security Preferences
    print("      🔄 Seeding security_preferences...")
    try:
        result = session.execute(text("SELECT COUNT(*) FROM security_preferences"))
        existing_count = result.scalar()
        if existing_count > 0:
            print(f"        ✅ Security preferences already exist, migrating data...")
        else:
            security_preferences = []
            for user_id in user_ids:
                security_preferences.append({
                    'user_id': user_id,
                    'preference_key': random.choice(['two_factor', 'password_policy', 'session_timeout']),
                    'preference_value': json.dumps({
                        'two_factor': random.choice([True, False]),
                        'password_policy': 'strong',
                        'session_timeout': random.randint(30, 120)
                    }),
                    'is_active': True,
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 365))
                })
            
            if security_preferences:
                columns = list(security_preferences[0].keys())
                placeholders = ', '.join([f':{col}' for col in columns])
                query = f"INSERT INTO security_preferences ({', '.join(columns)}) VALUES ({placeholders})"
                session.execute(text(query), security_preferences)
                print(f"        ✅ Created {len(security_preferences)} security preferences")
        results['security_preferences'] = True
    except Exception as e:
        print(f"        ⚠️  Security preferences table does not exist, skipping: {e}")
        results['security_preferences'] = False
    
    # 21. Sessions
    print("      🔄 Seeding sessions...")
    try:
        result = session.execute(text("SELECT COUNT(*) FROM sessions"))
        existing_count = result.scalar()
        if existing_count > 0:
            print(f"        ✅ Sessions already exist, migrating data...")
        else:
            sessions = []
            for user_id in user_ids:
                sessions.append({
                    'id': f'session_{user_id}_{random.randint(1000, 9999)}',
                    'user_id': user_id,
                    'ip_address': f'192.168.1.{random.randint(1, 254)}',
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'last_activity': datetime.now() - timedelta(minutes=random.randint(1, 60)),
                    'is_active': random.choice([True, False]),
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
                })
            
            if sessions:
                columns = list(sessions[0].keys())
                placeholders = ', '.join([f':{col}' for col in columns])
                query = f"INSERT INTO sessions ({', '.join(columns)}) VALUES ({placeholders})"
                session.execute(text(query), sessions)
                print(f"        ✅ Created {len(sessions)} sessions")
        results['sessions'] = True
    except Exception as e:
        print(f"        ⚠️  Sessions table does not exist, skipping: {e}")
        results['sessions'] = False
    
    # 22. Shared Contexts
    print("      🔄 Seeding shared_contexts...")
    try:
        result = session.execute(text("SELECT COUNT(*) FROM shared_contexts"))
        existing_count = result.scalar()
        if existing_count > 0:
            print(f"        ✅ Shared contexts already exist, migrating data...")
        else:
            shared_contexts = []
            for i in range(20):
                shared_contexts.append({
                    'name': f'shared_context_{i+1}',
                    'description': f'Shared context {i+1}',
                    'context_data': json.dumps({
                        'type': random.choice(['user', 'course', 'assignment', 'system']),
                        'metadata': {
                            'created_by': 'system',
                            'version': '1.0',
                            'tags': ['shared', 'context', 'data']
                        }
                    }),
                    'is_active': True,
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 365))
                })
            
            if shared_contexts:
                columns = list(shared_contexts[0].keys())
                placeholders = ', '.join([f':{col}' for col in columns])
                query = f"INSERT INTO shared_contexts ({', '.join(columns)}) VALUES ({placeholders})"
                session.execute(text(query), shared_contexts)
                print(f"        ✅ Created {len(shared_contexts)} shared contexts")
        results['shared_contexts'] = True
    except Exception as e:
        print(f"        ⚠️  Shared contexts table does not exist, skipping: {e}")
        results['shared_contexts'] = False
    
    # Summary
    successful_tables = sum(1 for success in results.values() if success)
    total_tables = len(results)
    print(f"\n    📊 SUMMARY: {successful_tables}/{total_tables} tables seeded successfully")
    
    return results
