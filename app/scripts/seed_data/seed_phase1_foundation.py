#!/usr/bin/env python3
"""
Phase 1: Foundation & Core Infrastructure Seeding
================================================

This script seeds the foundational tables that other systems depend on.
Focuses on user management, system configuration, and basic infrastructure.

Phase 1.1: User Management Foundation (10 tables)
- user_profiles, user_roles, user_sessions, user_activities
- user_behaviors, user_engagements, user_insights, user_trends
- user_predictions, user_comparisons

Phase 1.2: System Configuration (20 tables)
- access_control_*, system_configs, feature_flags, etc.

Phase 1.3: Basic Infrastructure (15 tables)
- notifications, logs, monitoring, etc.
"""

import os
import sys
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from app.core.database import SessionLocal
from app.dashboard.models.user import DashboardUser
from app.models.user_management.user.user import User
from sqlalchemy import text

def seed_phase1_foundation():
    """Main function to seed Phase 1 foundation tables"""
    print("\n" + "="*60)
    print("🌱 PHASE 1: FOUNDATION & CORE INFRASTRUCTURE SEEDING")
    print("="*60)
    
    session = SessionLocal()
    try:
        # Phase 1.1: User Management Foundation
        print("\n📋 PHASE 1.1: User Management Foundation")
        print("-" * 40)
        try:
            seed_user_management_foundation(session)
            session.commit()
            print("✅ Phase 1.1 completed successfully!")
        except Exception as e:
            session.rollback()
            print(f"❌ Phase 1.1 failed: {e}")
            # Continue to next phase
        
        # Phase 1.2: System Configuration
        print("\n📋 PHASE 1.2: System Configuration")
        print("-" * 40)
        try:
            seed_system_configuration(session)
            session.commit()
            print("✅ Phase 1.2 completed successfully!")
        except Exception as e:
            session.rollback()
            print(f"❌ Phase 1.2 failed: {e}")
            # Continue to next phase
        
        # Phase 1.3: Basic Infrastructure
        print("\n📋 PHASE 1.3: Basic Infrastructure")
        print("-" * 40)
        try:
            seed_basic_infrastructure(session)
            session.commit()
            print("✅ Phase 1.3 completed successfully!")
        except Exception as e:
            session.rollback()
            print(f"❌ Phase 1.3 failed: {e}")
            # Continue to next phase
        
        # Phase 1.4: Complete Avatar System (Complete User Profiles)
        print("\n📋 PHASE 1.4: Complete Avatar System")
        print("-" * 40)
        try:
            seed_avatar_system(session)
            session.commit()
            print("✅ Phase 1.4 completed successfully!")
        except Exception as e:
            session.rollback()
            print(f"❌ Phase 1.4 failed: {e}")
            # Continue to next phase
        
        print("\n✅ Phase 1 Foundation seeding completed!")
        
    except Exception as e:
        print(f"❌ Critical error during Phase 1 seeding: {e}")
        session.rollback()
        raise
    finally:
        session.close()

def seed_user_management_foundation(session):
    """Seed Phase 1.1: User Management Foundation tables"""
    print("🔄 Seeding user management foundation...")
    
    # Get existing users from dashboard_users
    result = session.execute(text("SELECT COUNT(*) FROM dashboard_users"))
    user_count = result.scalar()
    
    if user_count == 0:
        print("⚠️  No users found in dashboard_users. Creating sample users first...")
        seed_sample_users(session)
        result = session.execute(text("SELECT COUNT(*) FROM dashboard_users"))
        user_count = result.scalar()
    
    print(f"📊 Found {user_count} users to work with")
    
    # Seed each table
    seed_user_profiles(session)
    seed_user_roles(session)
    seed_user_sessions(session)
    seed_user_activities(session)
    seed_user_behaviors(session)
    seed_user_engagements(session)
    seed_user_insights(session)
    seed_user_trends(session)
    seed_user_predictions(session)
    seed_user_comparisons(session)
    
    print("✅ User management foundation seeding complete!")

def seed_sample_users(session):
    """Create sample users if none exist"""
    sample_users = [
        {"username": "john_doe", "email": "john@example.com", "role": "STUDENT"},
        {"username": "jane_smith", "email": "jane@example.com", "role": "TEACHER"},
        {"username": "admin_user", "email": "admin@example.com", "role": "ADMIN"},
        {"username": "coach_wilson", "email": "coach@example.com", "role": "COACH"},
        {"username": "parent_jones", "email": "parent@example.com", "role": "PARENT"}
    ]
    
    for user_data in sample_users:
        session.execute(text("""
            INSERT INTO dashboard_users (full_name, email, hashed_password, role, is_active, created_at, updated_at)
            VALUES (:full_name, :email, :hashed_password, :role, true, :now, :now)
        """), {
            "full_name": user_data["username"],  # Map username to full_name
            "email": user_data["email"],
            "hashed_password": "dummy_password_hash",  # Required field
            "role": user_data["role"],
            "now": datetime.utcnow()
        })
    
    session.commit()
    print(f"✅ Created {len(sample_users)} sample users")

def seed_user_profiles(session):
    """Seed user_profiles table"""
    print("  🔄 Seeding user_profiles...")
    
    # Check if already has data
    result = session.execute(text("SELECT COUNT(*) FROM user_profiles"))
    if result.scalar() > 0:
        print("    ✅ user_profiles already has data")
        return
    
    # Get user IDs
    result = session.execute(text("SELECT id FROM dashboard_users LIMIT 10"))
    user_ids = [row[0] for row in result.fetchall()]
    
    if not user_ids:
        print("    ⚠️  No users found for profiles")
        return
    
    # Check if avatars table exists and has data
    try:
        result = session.execute(text("SELECT COUNT(*) FROM avatars"))
        avatar_count = result.scalar()
        has_avatars = avatar_count > 0
        print(f"    📊 Avatars table has {avatar_count} records")
    except:
        has_avatars = False
        print("    📊 Avatars table does not exist or is empty")
    
    profiles_data = []
    for user_id in user_ids:
        # Only set avatar_id if avatars table exists and has data
        avatar_id = None
        if has_avatars:
            avatar_id = random.randint(1, min(avatar_count, 100)) if random.random() > 0.3 else None
        
        profiles_data.append({
            'user_id': user_id,
            'avatar_id': avatar_id,
            'bio': random.choice([
                "Passionate about physical education and student development",
                "Dedicated coach with 10+ years experience",
                "Enthusiastic student athlete",
                "Supportive parent and community member",
                "Experienced PE teacher and curriculum developer"
            ]),
            'timezone': random.choice(['America/New_York', 'America/Chicago', 'America/Denver', 'America/Los_Angeles']),
            'language': random.choice(['en', 'es', 'fr']),
            'notification_preferences': json.dumps({
                'email': random.choice([True, False]),
                'sms': random.choice([True, False]),
                'push': random.choice([True, False]),
                'frequency': random.choice(['daily', 'weekly', 'monthly'])
            }),
            'custom_settings': json.dumps({
                'theme': random.choice(['light', 'dark', 'auto']),
                'accessibility': random.choice([True, False]),
                'privacy_level': random.choice(['public', 'friends', 'private'])
            }),
            'metadata': json.dumps({
                'last_login': datetime.utcnow().isoformat(),
                'preferences_version': '1.0',
                'setup_complete': True
            })
        })
    
    # Insert profiles
    for profile in profiles_data:
        session.execute(text("""
            INSERT INTO user_profiles (
                user_id, avatar_id, bio, timezone, language,
                notification_preferences, custom_settings, metadata
            ) VALUES (
                :user_id, :avatar_id, :bio, :timezone, :language,
                :notification_preferences, :custom_settings, :metadata
            )
        """), profile)
    
    print(f"    ✅ Created {len(profiles_data)} user profiles")

def seed_user_roles(session):
    """Seed user_roles table"""
    print("  🔄 Seeding user_roles...")
    
    # Check if already has data
    result = session.execute(text("SELECT COUNT(*) FROM user_roles"))
    if result.scalar() > 0:
        print("    ✅ user_roles already has data")
        return
    
    # Check if roles table exists and has data
    try:
        result = session.execute(text("SELECT COUNT(*) FROM roles"))
        roles_count = result.scalar()
        has_roles = roles_count > 0
        print(f"    📊 Roles table has {roles_count} records")
    except:
        has_roles = False
        print("    📊 Roles table does not exist or is empty")
    
    # Get user IDs and create role assignments
    result = session.execute(text("SELECT id, role FROM dashboard_users LIMIT 10"))
    users = result.fetchall()
    
    if not users:
        print("    ⚠️  No users found for roles")
        return
    
    # Create role assignments
    for user_id, user_role in users:
        # Only set role_id if roles table exists and has data
        role_id = None
        if has_roles:
            role_id = random.randint(1, min(roles_count, 10)) if random.random() > 0.3 else None
        
        session.execute(text("""
            INSERT INTO user_roles (user_id, role_id)
            VALUES (:user_id, :role_id)
        """), {
            'user_id': user_id,
            'role_id': role_id
        })
    
    print(f"    ✅ Created {len(users)} user role assignments")

def seed_user_sessions(session):
    """Seed user_sessions table"""
    print("  🔄 Seeding user_sessions...")
    
    # Check if already has data
    result = session.execute(text("SELECT COUNT(*) FROM user_sessions"))
    if result.scalar() > 0:
        print("    ✅ user_sessions already has data")
        return
    
    # Get user IDs
    result = session.execute(text("SELECT id FROM dashboard_users LIMIT 10"))
    user_ids = [row[0] for row in result.fetchall()]
    
    if not user_ids:
        print("    ⚠️  No users found for sessions")
        return
    
    # Check what valid status values exist for the enum
    try:
        result = session.execute(text("""
            SELECT unnest(enum_range(NULL::base_status_enum)) as status_value
        """))
        valid_statuses = [row[0] for row in result.fetchall()]
        print(f"    📊 Valid status values: {valid_statuses}")
    except:
        # Fallback to common status values
        valid_statuses = ['ACTIVE', 'INACTIVE', 'EXPIRED']
        print(f"    📊 Using fallback status values: {valid_statuses}")
    
    sessions_data = []
    for user_id in user_ids:
        # Create multiple sessions per user
        for i in range(random.randint(1, 3)):
            session_start = datetime.utcnow() - timedelta(days=random.randint(0, 30))
            session_data = {
                'user_id': user_id,
                'session_token': f"token_{user_id}_{i}_{random.randint(1000, 9999)}",
                'ip_address': f"192.168.1.{random.randint(1, 255)}",
                'user_agent': random.choice([
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
                ]),
                'last_activity': session_start + timedelta(minutes=random.randint(5, 120)),
                'expires_at': session_start + timedelta(hours=random.randint(1, 24)),
                'is_active': random.choice([True, False]),
                'status': random.choice(valid_statuses)
            }
            sessions_data.append(session_data)
    
    # Insert sessions
    for session_data in sessions_data:
        session.execute(text("""
            INSERT INTO user_sessions (
                user_id, session_token, ip_address, user_agent, last_activity,
                expires_at, is_active, status
            ) VALUES (
                :user_id, :session_token, :ip_address, :user_agent, :last_activity,
                :expires_at, :is_active, :status
            )
        """), session_data)
    
    print(f"    ✅ Created {len(sessions_data)} user sessions")

def seed_user_activities(session):
    """Seed user_activities table"""
    print("  🔄 Seeding user_activities...")
    
    # Check if already has data
    result = session.execute(text("SELECT COUNT(*) FROM user_activities"))
    if result.scalar() > 0:
        print("    ✅ user_activities already has data")
        return
    
    # Get user IDs
    result = session.execute(text("SELECT id FROM dashboard_users LIMIT 10"))
    user_ids = [row[0] for row in result.fetchall()]
    
    if not user_ids:
        print("    ⚠️  No users found for activities")
        return
    
    activities_data = []
    activity_types = ['LOGIN', 'LOGOUT', 'PROFILE_UPDATE', 'LESSON_VIEW', 'EXERCISE_COMPLETE', 'ASSESSMENT_TAKE']
    
    for user_id in user_ids:
        # Create multiple activities per user
        for i in range(random.randint(5, 15)):
            activity_data = {
                'user_id': user_id,
                'activity_type': random.choice(activity_types),
                'activity_data': json.dumps({
                    'page': random.choice(['dashboard', 'lessons', 'exercises', 'profile']),
                    'duration': random.randint(30, 300),
                    'success': random.choice([True, False])
                }),
                'session_id': f"session_{user_id}_{i}",
                'timestamp': datetime.utcnow() - timedelta(days=random.randint(0, 30)),
                'ip_address': f"192.168.1.{random.randint(1, 255)}",
                'user_agent': 'Mozilla/5.0 (compatible; FaradayAI/1.0)',
                'location_data': json.dumps({
                    'country': 'US',
                    'state': random.choice(['CA', 'NY', 'TX', 'FL', 'IL']),
                    'city': 'Sample City'
                })
            }
            activities_data.append(activity_data)
    
    # Insert activities
    for activity_data in activities_data:
        session.execute(text("""
            INSERT INTO user_activities (
                user_id, activity_type, activity_data, session_id, timestamp,
                ip_address, user_agent, location_data
            ) VALUES (
                :user_id, :activity_type, :activity_data, :session_id, :timestamp,
                :ip_address, :user_agent, :location_data
            )
        """), activity_data)
    
    print(f"    ✅ Created {len(activities_data)} user activities")

def seed_user_behaviors(session):
    """Seed user_behaviors table"""
    print("  🔄 Seeding user_behaviors...")
    
    # Check if already has data
    result = session.execute(text("SELECT COUNT(*) FROM user_behaviors"))
    if result.scalar() > 0:
        print("    ✅ user_behaviors already has data")
        return
    
    # Get user IDs
    result = session.execute(text("SELECT id FROM dashboard_users LIMIT 10"))
    user_ids = [row[0] for row in result.fetchall()]
    
    if not user_ids:
        print("    ⚠️  No users found for behaviors")
        return
    
    behaviors_data = []
    behavior_types = ['ENGAGEMENT', 'LEARNING_STYLE', 'PREFERENCE', 'PERFORMANCE', 'SOCIAL']
    
    for user_id in user_ids:
        # Create multiple behaviors per user
        for i in range(random.randint(2, 5)):
            behavior_data = {
                'user_id': user_id,
                'behavior_type': random.choice(behavior_types),
                'behavior_data': json.dumps({
                    'pattern': random.choice(['consistent', 'variable', 'improving', 'declining']),
                    'frequency': random.randint(1, 10),
                    'intensity': random.uniform(0.1, 1.0)
                }),
                'confidence_score': random.uniform(0.5, 1.0),
                'timestamp': datetime.utcnow() - timedelta(days=random.randint(0, 30)),
                'analysis_period': random.choice(['daily', 'weekly', 'monthly'])
            }
            behaviors_data.append(behavior_data)
    
    # Insert behaviors
    for behavior_data in behaviors_data:
        session.execute(text("""
            INSERT INTO user_behaviors (
                user_id, behavior_type, behavior_data, confidence_score, timestamp, analysis_period
            ) VALUES (
                :user_id, :behavior_type, :behavior_data, :confidence_score, :timestamp, :analysis_period
            )
        """), behavior_data)
    
    print(f"    ✅ Created {len(behaviors_data)} user behaviors")

def seed_user_engagements(session):
    """Seed user_engagements table"""
    print("  🔄 Seeding user_engagements...")
    
    # Check if already has data
    result = session.execute(text("SELECT COUNT(*) FROM user_engagements"))
    if result.scalar() > 0:
        print("    ✅ user_engagements already has data")
        return
    
    # Get user IDs
    result = session.execute(text("SELECT id FROM dashboard_users LIMIT 10"))
    user_ids = [row[0] for row in result.fetchall()]
    
    if not user_ids:
        print("    ⚠️  No users found for engagements")
        return
    
    engagements_data = []
    for user_id in user_ids:
        # Create engagement data for each user
        engagement_data = {
            'user_id': user_id,
            'engagement_score': random.uniform(0.1, 1.0),
            'session_count': random.randint(1, 50),
            'avg_session_duration': random.uniform(5.0, 120.0),
            'feature_usage': json.dumps({
                'lessons': random.randint(0, 100),
                'exercises': random.randint(0, 200),
                'assessments': random.randint(0, 50),
                'profile': random.randint(0, 20)
            }),
            'retention_metrics': json.dumps({
                'days_active': random.randint(1, 365),
                'return_rate': random.uniform(0.1, 1.0),
                'churn_probability': random.uniform(0.0, 0.3)
            }),
            'churn_risk': random.choice(['LOW', 'MEDIUM', 'HIGH']),
            'timestamp': datetime.utcnow() - timedelta(days=random.randint(0, 30)),
            'period': random.choice(['daily', 'weekly', 'monthly'])
        }
        engagements_data.append(engagement_data)
    
    # Insert engagements
    for engagement_data in engagements_data:
        session.execute(text("""
            INSERT INTO user_engagements (
                user_id, engagement_score, session_count, avg_session_duration,
                feature_usage, retention_metrics, churn_risk, timestamp, period
            ) VALUES (
                :user_id, :engagement_score, :session_count, :avg_session_duration,
                :feature_usage, :retention_metrics, :churn_risk, :timestamp, :period
            )
        """), engagement_data)
    
    print(f"    ✅ Created {len(engagements_data)} user engagements")

def seed_user_insights(session):
    """Seed user_insights table"""
    print("  🔄 Seeding user_insights...")
    
    # Check if already has data
    result = session.execute(text("SELECT COUNT(*) FROM user_insights"))
    if result.scalar() > 0:
        print("    ✅ user_insights already has data")
        return
    
    # Get user IDs
    result = session.execute(text("SELECT id FROM dashboard_users LIMIT 10"))
    user_ids = [row[0] for row in result.fetchall()]
    
    if not user_ids:
        print("    ⚠️  No users found for insights")
        return
    
    insights_data = []
    insight_types = ['PERFORMANCE', 'LEARNING', 'ENGAGEMENT', 'BEHAVIOR', 'RECOMMENDATION']
    
    for user_id in user_ids:
        # Create multiple insights per user
        for i in range(random.randint(1, 3)):
            insight_data = {
                'user_id': user_id,
                'insight_type': random.choice(insight_types),
                'insight_data': json.dumps({
                    'summary': f"User shows {random.choice(['strong', 'moderate', 'improving'])} performance",
                    'details': "Detailed analysis of user patterns and behaviors",
                    'impact_score': random.uniform(0.1, 1.0)
                }),
                'confidence_score': random.uniform(0.6, 1.0),
                'key_findings': json.dumps([
                    "User responds well to visual learning",
                    "Performance improves with regular practice",
                    "Prefers structured lesson formats"
                ]),
                'improvement_areas': json.dumps([
                    "Could benefit from more challenging exercises",
                    "Social interaction opportunities",
                    "Advanced skill development"
                ]),
                'strengths': json.dumps([
                    "Consistent attendance",
                    "Quick skill acquisition",
                    "Positive attitude"
                ]),
                'opportunities': json.dumps([
                    "Leadership roles in group activities",
                    "Mentoring younger students",
                    "Advanced curriculum exploration"
                ]),
                'risk_factors': json.dumps([
                    "Occasional disengagement during complex tasks",
                    "Limited peer interaction",
                    "Performance variability"
                ]),
                'timestamp': datetime.utcnow() - timedelta(days=random.randint(0, 30)),
                'is_actionable': random.choice([True, False])
            }
            insights_data.append(insight_data)
    
    # Insert insights
    for insight_data in insights_data:
        session.execute(text("""
            INSERT INTO user_insights (
                user_id, insight_type, insight_data, confidence_score, key_findings,
                improvement_areas, strengths, opportunities, risk_factors, timestamp, is_actionable
            ) VALUES (
                :user_id, :insight_type, :insight_data, :confidence_score, :key_findings,
                :improvement_areas, :strengths, :opportunities, :risk_factors, :timestamp, :is_actionable
            )
        """), insight_data)
    
    print(f"    ✅ Created {len(insights_data)} user insights")

def seed_user_trends(session):
    """Seed user_trends table"""
    print("  🔄 Seeding user_trends...")
    
    # Check if already has data
    result = session.execute(text("SELECT COUNT(*) FROM user_trends"))
    if result.scalar() > 0:
        print("    ✅ user_trends already has data")
        return
    
    # Get user IDs
    result = session.execute(text("SELECT id FROM dashboard_users LIMIT 10"))
    user_ids = [row[0] for row in result.fetchall()]
    
    if not user_ids:
        print("    ⚠️  No users found for trends")
        return
    
    trends_data = []
    trend_types = ['PERFORMANCE', 'ENGAGEMENT', 'LEARNING', 'BEHAVIOR', 'ACTIVITY']
    
    for user_id in user_ids:
        # Create multiple trends per user
        for i in range(random.randint(1, 3)):
            trend_data = {
                'user_id': user_id,
                'trend_type': random.choice(trend_types),
                'trend_data': json.dumps({
                    'current_value': random.uniform(0.1, 1.0),
                    'previous_value': random.uniform(0.1, 1.0),
                    'change_rate': random.uniform(-0.5, 0.5),
                    'consistency': random.uniform(0.1, 1.0)
                }),
                'trend_direction': random.choice(['INCREASING', 'DECREASING', 'STABLE', 'VARIABLE']),
                'trend_strength': random.uniform(0.1, 1.0),
                'seasonal_patterns': json.dumps({
                    'season': random.choice(['spring', 'summer', 'fall', 'winter']),
                    'pattern_strength': random.uniform(0.1, 1.0),
                    'peak_periods': ["morning", "afternoon"]
                }),
                'time_range': random.choice(['week', 'month', 'quarter', 'year']),
                'timestamp': datetime.utcnow() - timedelta(days=random.randint(0, 30))
            }
            trends_data.append(trend_data)
    
    # Insert trends
    for trend_data in trends_data:
        session.execute(text("""
            INSERT INTO user_trends (
                user_id, trend_type, trend_data, trend_direction, trend_strength,
                seasonal_patterns, time_range, timestamp
            ) VALUES (
                :user_id, :trend_type, :trend_data, :trend_direction, :trend_strength,
                :seasonal_patterns, :time_range, :timestamp
            )
        """), trend_data)
    
    print(f"    ✅ Created {len(trends_data)} user trends")

def seed_user_predictions(session):
    """Seed user_predictions table"""
    print("  🔄 Seeding user_predictions...")
    
    # Check if already has data
    result = session.execute(text("SELECT COUNT(*) FROM user_predictions"))
    if result.scalar() > 0:
        print("    ✅ user_predictions already has data")
        return
    
    # Get user IDs
    result = session.execute(text("SELECT id FROM dashboard_users LIMIT 10"))
    user_ids = [row[0] for row in result.fetchall()]
    
    if not user_ids:
        print("    ⚠️  No users found for predictions")
        return
    
    predictions_data = []
    prediction_types = ['PERFORMANCE', 'ENGAGEMENT', 'COMPLETION', 'ACHIEVEMENT', 'RISK']
    
    for user_id in user_ids:
        # Create multiple predictions per user
        for i in range(random.randint(1, 2)):
            prediction_data = {
                'user_id': user_id,
                'prediction_type': random.choice(prediction_types),
                'prediction_data': json.dumps({
                    'predicted_value': random.uniform(0.1, 1.0),
                    'confidence_interval': [random.uniform(0.0, 0.5), random.uniform(0.5, 1.0)],
                    'factors': ["current performance", "engagement level", "learning style"],
                    'assumptions': ["continued practice", "stable environment", "consistent effort"]
                }),
                'confidence_score': random.uniform(0.5, 1.0),
                'prediction_horizon': random.choice(['1_week', '1_month', '3_months', '6_months']),
                'model_version': f"v{random.randint(1, 3)}.{random.randint(0, 9)}",
                'timestamp': datetime.utcnow() - timedelta(days=random.randint(0, 30)),
                'is_active': random.choice([True, False])
            }
            predictions_data.append(prediction_data)
    
    # Insert predictions
    for prediction_data in predictions_data:
        session.execute(text("""
            INSERT INTO user_predictions (
                user_id, prediction_type, prediction_data, confidence_score, prediction_horizon,
                model_version, timestamp, is_active
            ) VALUES (
                :user_id, :prediction_type, :prediction_data, :confidence_score, :prediction_horizon,
                :model_version, :timestamp, :is_active
            )
        """), prediction_data)
    
    print(f"    ✅ Created {len(predictions_data)} user predictions")

def seed_user_comparisons(session):
    """Seed user_comparisons table"""
    print("  🔄 Seeding user_comparisons...")
    
    # Check if already has data
    result = session.execute(text("SELECT COUNT(*) FROM user_comparisons"))
    if result.scalar() > 0:
        print("    ✅ user_comparisons already has data")
        return
    
    # Get user IDs
    result = session.execute(text("SELECT id FROM dashboard_users LIMIT 10"))
    user_ids = [row[0] for row in result.fetchall()]
    
    if not user_ids:
        print("    ⚠️  No users found for comparisons")
        return
    
    comparisons_data = []
    comparison_types = ['PERFORMANCE', 'ENGAGEMENT', 'PROGRESS', 'SKILLS', 'ACHIEVEMENT']
    
    for user_id in user_ids:
        # Create multiple comparisons per user
        for i in range(random.randint(1, 2)):
            comparison_data = {
                'user_id': user_id,
                'comparison_type': random.choice(comparison_types),
                'comparison_data': json.dumps({
                    'user_score': random.uniform(0.1, 1.0),
                    'peer_average': random.uniform(0.1, 1.0),
                    'percentile': random.randint(1, 100),
                    'ranking': random.randint(1, 50)
                }),
                'comparison_users': json.dumps({
                    'peer_group_size': random.randint(10, 100),
                    'similar_users': random.randint(1, 10),
                    'benchmark_group': "grade_level_peers"
                }),
                'percentile_rank': random.uniform(0.1, 1.0),
                'benchmarking_data': json.dumps({
                    'national_average': random.uniform(0.1, 1.0),
                    'state_average': random.uniform(0.1, 1.0),
                    'school_average': random.uniform(0.1, 1.0)
                }),
                'insights': json.dumps([
                    "User performs above peer average",
                    "Strong in physical skills, improving in cognitive aspects",
                    "Consistent progress over time"
                ]),
                'timestamp': datetime.utcnow() - timedelta(days=random.randint(0, 30))
            }
            comparisons_data.append(comparison_data)
    
    # Insert comparisons
    for comparison_data in comparisons_data:
        session.execute(text("""
            INSERT INTO user_comparisons (
                user_id, comparison_type, comparison_data, comparison_users, percentile_rank,
                benchmarking_data, insights, timestamp
            ) VALUES (
                :user_id, :comparison_type, :comparison_data, :comparison_users, :percentile_rank,
                :benchmarking_data, :insights, :timestamp
            )
        """), comparison_data)
    
    print(f"    ✅ Created {len(comparisons_data)} user comparisons")

def seed_system_configuration(session):
    """Seed Phase 1.2: System Configuration tables"""
    print("🔄 Seeding system configuration...")
    
    # Phase 1.2.1: Access Control System
    print("  📋 Phase 1.2.1: Access Control System")
    seed_access_control_system(session)
    
    # Phase 1.2.2: System Configuration
    print("  📋 Phase 1.2.2: System Configuration")
    seed_system_configs(session)
    
    # Phase 1.2.3: Feature Flags
    print("  📋 Phase 1.2.3: Feature Flags")
    seed_feature_flags(session)
    
    print("✅ System configuration seeding complete!")

def seed_access_control_system(session):
    """Seed access control tables"""
    print("    🔄 Seeding access control system...")
    
    # Check if access_control_roles already has data
    result = session.execute(text("SELECT COUNT(*) FROM access_control_roles"))
    if result.scalar() > 0:
        print("      ✅ access_control_roles already has data")
        return
    
    # Create basic roles
    roles_data = [
        {'name': 'SUPER_ADMIN', 'description': 'Full system access and control', 'is_active': True},
        {'name': 'ADMIN', 'description': 'Administrative access to most features', 'is_active': True},
        {'name': 'TEACHER', 'description': 'Teacher access to educational features', 'is_active': True},
        {'name': 'COACH', 'description': 'Coach access to training features', 'is_active': True},
        {'name': 'STUDENT', 'description': 'Student access to learning features', 'is_active': True},
        {'name': 'PARENT', 'description': 'Parent access to monitoring features', 'is_active': True},
        {'name': 'GUEST', 'description': 'Limited read-only access', 'is_active': True},
        {'name': 'MODERATOR', 'description': 'Content moderation access', 'is_active': True}
    ]
    
    # Insert roles
    for role_data in roles_data:
        session.execute(text("""
            INSERT INTO access_control_roles (name, description, is_active, created_at, updated_at)
            VALUES (:name, :description, :is_active, :now, :now)
        """), {
            **role_data,
            "now": datetime.utcnow()
        })
    
    print(f"      ✅ Created {len(roles_data)} access control roles")
    
    # Now seed permissions
    seed_access_control_permissions(session)
    
    # Then seed role-permission mappings
    seed_role_permissions(session)
    
    # Finally seed user-role assignments
    seed_user_role_assignments(session)

def seed_access_control_permissions(session):
    """Seed access control permissions"""
    print("      🔄 Seeding access control permissions...")
    
    # Check if already has data
    result = session.execute(text("SELECT COUNT(*) FROM access_control_permissions"))
    if result.scalar() > 0:
        print("        ✅ access_control_permissions already has data")
        return
    
    # Create comprehensive permissions
    permissions_data = [
        # User Management
        {'name': 'USER_CREATE', 'description': 'Create new users', 'resource': 'users', 'action': 'create'},
        {'name': 'USER_READ', 'description': 'Read user information', 'resource': 'users', 'action': 'read'},
        {'name': 'USER_UPDATE', 'description': 'Update user information', 'resource': 'users', 'action': 'update'},
        {'name': 'USER_DELETE', 'description': 'Delete users', 'resource': 'users', 'action': 'delete'},
        
        # Educational Content
        {'name': 'LESSON_CREATE', 'description': 'Create lessons', 'resource': 'lessons', 'action': 'create'},
        {'name': 'LESSON_READ', 'description': 'Read lessons', 'resource': 'lessons', 'action': 'read'},
        {'name': 'LESSON_UPDATE', 'description': 'Update lessons', 'resource': 'lessons', 'action': 'update'},
        {'name': 'LESSON_DELETE', 'description': 'Delete lessons', 'resource': 'lessons', 'action': 'delete'},
        
        # Physical Education
        {'name': 'EXERCISE_CREATE', 'description': 'Create exercises', 'resource': 'exercises', 'action': 'create'},
        {'name': 'EXERCISE_READ', 'description': 'Read exercises', 'resource': 'exercises', 'action': 'read'},
        {'name': 'EXERCISE_UPDATE', 'description': 'Update exercises', 'resource': 'exercises', 'action': 'update'},
        {'name': 'EXERCISE_DELETE', 'description': 'Delete exercises', 'resource': 'exercises', 'action': 'delete'},
        
        # Assessment & Analytics
        {'name': 'ASSESSMENT_CREATE', 'description': 'Create assessments', 'resource': 'assessments', 'action': 'create'},
        {'name': 'ASSESSMENT_READ', 'description': 'Read assessments', 'resource': 'assessments', 'action': 'read'},
        {'name': 'ASSESSMENT_UPDATE', 'description': 'Update assessments', 'resource': 'assessments', 'action': 'update'},
        {'name': 'ASSESSMENT_DELETE', 'description': 'Delete assessments', 'resource': 'assessments', 'action': 'delete'},
        
        # System Administration
        {'name': 'SYSTEM_CONFIG', 'description': 'Configure system settings', 'resource': 'system', 'action': 'configure'},
        {'name': 'FEATURE_TOGGLE', 'description': 'Toggle feature flags', 'resource': 'features', 'action': 'toggle'},
        {'name': 'LOG_ACCESS', 'description': 'Access system logs', 'resource': 'logs', 'action': 'read'},
        {'name': 'BACKUP_RESTORE', 'description': 'Backup and restore data', 'resource': 'system', 'action': 'backup'}
    ]
    
    # Insert permissions
    for perm_data in permissions_data:
        session.execute(text("""
            INSERT INTO access_control_permissions (name, description, resource, action, created_at, updated_at)
            VALUES (:name, :description, :resource, :action, :now, :now)
        """), {
            **perm_data,
            "now": datetime.utcnow()
        })
    
    print(f"        ✅ Created {len(permissions_data)} access control permissions")

def seed_role_permissions(session):
    """Seed role-permission mappings"""
    print("      🔄 Seeding role-permission mappings...")
    
    # Check if already has data
    result = session.execute(text("SELECT COUNT(*) FROM access_control_role_permissions"))
    if result.scalar() > 0:
        print("        ✅ access_control_role_permissions already has data")
        return
    
    # Get role IDs
    result = session.execute(text("SELECT id, name FROM access_control_roles"))
    roles = result.fetchall()
    
    # Get permission IDs
    result = session.execute(text("SELECT id, name FROM access_control_permissions"))
    permissions = result.fetchall()
    
    # Create role-permission mappings
    role_permissions = []
    
    for role_id, role_name in roles:
        if role_name == 'SUPER_ADMIN':
            # Super admin gets all permissions
            for perm_id, _ in permissions:
                role_permissions.append({'role_id': role_id, 'permission_id': perm_id})
        
        elif role_name == 'ADMIN':
            # Admin gets most permissions except super admin ones
            for perm_id, perm_name in permissions:
                if not perm_name.startswith('SYSTEM_') and not perm_name.startswith('BACKUP_'):
                    role_permissions.append({'role_id': role_id, 'permission_id': perm_id})
        
        elif role_name == 'TEACHER':
            # Teachers get educational content permissions
            for perm_id, perm_name in permissions:
                if any(keyword in perm_name for keyword in ['LESSON_', 'EXERCISE_', 'ASSESSMENT_READ', 'USER_READ']):
                    role_permissions.append({'role_id': role_id, 'permission_id': perm_id})
        
        elif role_name == 'COACH':
            # Coaches get exercise and assessment permissions
            for perm_id, perm_name in permissions:
                if any(keyword in perm_name for keyword in ['EXERCISE_', 'ASSESSMENT_READ', 'USER_READ']):
                    role_permissions.append({'role_id': role_id, 'permission_id': perm_id})
        
        elif role_name == 'STUDENT':
            # Students get read permissions for content
            for perm_id, perm_name in permissions:
                if perm_name.endswith('_READ'):
                    role_permissions.append({'role_id': role_id, 'permission_id': perm_id})
        
        elif role_name == 'PARENT':
            # Parents get read permissions for monitoring
            for perm_id, perm_name in permissions:
                if perm_name in ['USER_READ', 'ASSESSMENT_READ', 'LESSON_READ']:
                    role_permissions.append({'role_id': role_id, 'permission_id': perm_id})
        
        elif role_name == 'MODERATOR':
            # Moderators get content management permissions
            for perm_id, perm_name in permissions:
                if any(keyword in perm_name for keyword in ['LESSON_', 'EXERCISE_', 'ASSESSMENT_', 'USER_READ']):
                    role_permissions.append({'role_id': role_id, 'permission_id': perm_id})
    
    # Insert role-permission mappings
    for rp in role_permissions:
        session.execute(text("""
            INSERT INTO access_control_role_permissions (role_id, permission_id, created_at, updated_at)
            VALUES (:role_id, :permission_id, :now, :now)
        """), {
            **rp,
            "now": datetime.utcnow()
        })
    
    print(f"        ✅ Created {len(role_permissions)} role-permission mappings")

def seed_user_role_assignments(session):
    """Seed user-role assignments in access control system"""
    print("      🔄 Seeding user-role assignments...")
    
    # Check if already has data
    result = session.execute(text("SELECT COUNT(*) FROM access_control_user_roles"))
    if result.scalar() > 0:
        print("        ✅ access_control_user_roles already has data")
        return
    
    # Get users and their dashboard roles
    result = session.execute(text("SELECT id, role FROM dashboard_users LIMIT 10"))
    users = result.fetchall()
    
    # Get access control roles
    result = session.execute(text("SELECT id, name FROM access_control_roles"))
    ac_roles = {role_name: role_id for role_id, role_name in result.fetchall()}
    
    # Create user-role assignments
    user_roles = []
    for user_id, dashboard_role in users:
        # Map dashboard roles to access control roles
        if dashboard_role == 'ADMIN':
            ac_role_id = ac_roles.get('ADMIN', ac_roles.get('SUPER_ADMIN'))
        elif dashboard_role == 'TEACHER':
            ac_role_id = ac_roles.get('TEACHER')
        elif dashboard_role == 'COACH':
            ac_role_id = ac_roles.get('COACH')
        elif dashboard_role == 'STUDENT':
            ac_role_id = ac_roles.get('STUDENT')
        elif dashboard_role == 'PARENT':
            ac_role_id = ac_roles.get('PARENT')
        else:
            ac_role_id = ac_roles.get('GUEST')
        
        if ac_role_id:
            user_roles.append({
                'user_id': user_id,
                'role_id': ac_role_id
            })
    
    # Insert user-role assignments
    for ur in user_roles:
        session.execute(text("""
            INSERT INTO access_control_user_roles (user_id, role_id, created_at, updated_at)
            VALUES (:user_id, :role_id, :now, :now)
        """), {
            **ur,
            "now": datetime.utcnow()
        })
    
    print(f"        ✅ Created {len(user_roles)} user-role assignments")

def seed_system_configs(session):
    """Seed system configuration tables"""
    print("    🔄 Seeding system configurations...")
    
    # This will be implemented based on what system config tables exist
    print("      ⏳ System configs seeding - coming in next iteration")

def seed_feature_flags(session):
    """Seed feature flags"""
    print("    🔄 Seeding feature flags...")
    
    # This will be implemented based on what feature flag tables exist
    print("      ⏳ Feature flags seeding - coming in next iteration")

def seed_basic_infrastructure(session):
    """Seed Phase 1.3: Basic Infrastructure tables"""
    print("🔄 Seeding basic infrastructure...")
    
    # Phase 1.3.1: Notifications System
    print("  📋 Phase 1.3.1: Notifications System")
    seed_notifications_system(session)
    
    # Phase 1.3.2: Logging System
    print("  📋 Phase 1.3.2: Logging System")
    seed_logging_system(session)
    
    # Phase 1.3.3: Monitoring & Audit
    print("  📋 Phase 1.3.3: Monitoring & Audit")
    seed_monitoring_system(session)
    
    # Phase 1.3.4: System Utilities
    print("  📋 Phase 1.3.4: System Utilities")
    seed_system_utilities(session)
    
    print("✅ Basic infrastructure seeding complete!")

def seed_notifications_system(session):
    """Seed notifications system tables"""
    print("    🔄 Seeding notifications system...")
    
    # Check if notifications table exists and seed it
    try:
        result = session.execute(text("SELECT COUNT(*) FROM notifications"))
        if result.scalar() > 0:
            print("      ✅ notifications already has data")
            return
        
        # Get user IDs for notifications
        result = session.execute(text("SELECT id FROM dashboard_users LIMIT 10"))
        user_ids = [row[0] for row in result.fetchall()]
        
        if not user_ids:
            print("      ⚠️  No users found for notifications")
            return
        
        # Create sample notifications
        notification_types = ['SYSTEM', 'EDUCATIONAL', 'REMINDER', 'ACHIEVEMENT', 'ALERT']
        notification_data = []
        
        for user_id in user_ids:
            # Create multiple notifications per user
            for i in range(random.randint(2, 5)):
                notification_data.append({
                    'user_id': user_id,
                    'type': random.choice(notification_types),
                    'title': random.choice([
                        'Welcome to Faraday AI!',
                        'New lesson available',
                        'Exercise reminder',
                        'Achievement unlocked!',
                        'System maintenance notice',
                        'Weekly progress report',
                        'New feature available',
                        'Safety reminder'
                    ]),
                    'message': random.choice([
                        'Welcome to the platform! We\'re excited to have you here.',
                        'A new lesson has been added to your curriculum.',
                        'Time for your daily exercise routine!',
                        'Congratulations! You\'ve reached a new milestone.',
                        'Scheduled maintenance will occur tonight.',
                        'Here\'s your weekly progress summary.',
                        'Check out our latest feature updates.',
                        'Remember to warm up before exercising.'
                    ]),
                    'is_read': random.choice([True, False]),
                    'priority': random.choice(['LOW', 'MEDIUM', 'HIGH', 'URGENT']),
                    'created_at': datetime.utcnow() - timedelta(days=random.randint(0, 30))
                })
        
        # Insert notifications
        for notif in notification_data:
            session.execute(text("""
                INSERT INTO notifications (
                    user_id, type, title, message, is_read, priority, created_at
                ) VALUES (
                    :user_id, :type, :title, :message, :is_read, :priority, :created_at
                )
            """), notif)
        
        print(f"      ✅ Created {len(notification_data)} notifications")
        
    except Exception as e:
        print(f"      ⚠️  Notifications table not available: {e}")

def seed_logging_system(session):
    """Seed logging system tables"""
    print("    🔄 Seeding logging system...")
    
    # Check if system_logs table exists and seed it
    try:
        result = session.execute(text("SELECT COUNT(*) FROM system_logs"))
        if result.scalar() > 0:
            print("      ✅ system_logs already has data")
            return
        
        # Create sample system logs
        log_levels = ['INFO', 'WARNING', 'ERROR', 'DEBUG']
        log_categories = ['AUTHENTICATION', 'USER_ACTIVITY', 'SYSTEM_OPERATION', 'SECURITY', 'PERFORMANCE']
        
        log_data = []
        for i in range(100):  # Create 100 sample log entries
            log_data.append({
                'level': random.choice(log_levels),
                'category': random.choice(log_categories),
                'message': random.choice([
                    'User login successful',
                    'Database connection established',
                    'Cache refreshed successfully',
                    'API request processed',
                    'User profile updated',
                    'Lesson content loaded',
                    'Exercise completed',
                    'Assessment submitted',
                    'System backup completed',
                    'Performance metrics collected'
                ]),
                'details': json.dumps({
                    'user_id': random.randint(1, 10) if random.random() > 0.3 else None,
                    'ip_address': f"192.168.1.{random.randint(1, 255)}",
                    'user_agent': 'FaradayAI/1.0',
                    'session_id': f"session_{random.randint(1000, 9999)}"
                }),
                'timestamp': datetime.utcnow() - timedelta(days=random.randint(0, 30))
            })
        
        # Insert logs
        for log in log_data:
            session.execute(text("""
                INSERT INTO system_logs (
                    level, category, message, details, timestamp
                ) VALUES (
                    :level, :category, :message, :details, :timestamp
                )
            """), log)
        
        print(f"      ✅ Created {len(log_data)} system logs")
        
    except Exception as e:
        print(f"      ⚠️  System logs table not available: {e}")
    
    # Seed activity_logs table
    try:
        result = session.execute(text("SELECT COUNT(*) FROM activity_logs"))
        if result.scalar() > 0:
            print("      ✅ activity_logs already has data")
        else:
            # Get user and organization IDs
            user_result = session.execute(text("SELECT id FROM users LIMIT 10"))
            user_ids = [row[0] for row in user_result.fetchall()]
            
            org_result = session.execute(text("SELECT id FROM organizations LIMIT 5"))
            org_ids = [row[0] for row in org_result.fetchall()]
            
            if not user_ids:
                user_ids = [1, 2, 3, 4, 5]  # Fallback IDs
            if not org_ids:
                org_ids = [1, 2, 3]  # Fallback IDs
            
            # Create sample activity logs
            actions = ['CREATE', 'UPDATE', 'DELETE', 'VIEW', 'EXPORT', 'IMPORT', 'LOGIN', 'LOGOUT']
            resource_types = ['USER', 'STUDENT', 'LESSON', 'EXERCISE', 'ACTIVITY', 'ASSESSMENT', 'CURRICULUM']
            
            activity_logs_data = []
            for i in range(200):  # Create 200 sample activity log entries
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
            
            # Insert activity logs
            for log in activity_logs_data:
                session.execute(text("""
                    INSERT INTO activity_logs (
                        action, resource_type, resource_id, details, user_id, org_id, timestamp, created_at, updated_at
                    ) VALUES (
                        :action, :resource_type, :resource_id, :details, :user_id, :org_id, :timestamp, :created_at, :updated_at
                    )
                """), log)
            
            print(f"      ✅ Created {len(activity_logs_data)} activity logs")
        
    except Exception as e:
        print(f"      ⚠️  Activity logs table not available: {e}")

def seed_monitoring_system(session):
    """Seed monitoring and audit tables"""
    print("    🔄 Seeding monitoring system...")
    
    # Check if audit_logs table exists and seed it
    try:
        result = session.execute(text("SELECT COUNT(*) FROM audit_logs"))
        if result.scalar() > 0:
            print("      ✅ audit_logs already has data")
            return
        
        # Create sample audit logs
        audit_actions = ['CREATE', 'READ', 'UPDATE', 'DELETE', 'LOGIN', 'LOGOUT', 'EXPORT', 'IMPORT']
        audit_resources = ['USER', 'LESSON', 'EXERCISE', 'ASSESSMENT', 'CURRICULUM', 'SYSTEM']
        
        audit_data = []
        for i in range(50):  # Create 50 sample audit entries
            audit_data.append({
                'user_id': random.randint(1, 10) if random.random() > 0.2 else None,
                'action': random.choice(audit_actions),
                'resource_type': random.choice(audit_resources),
                'resource_id': random.randint(1, 100),
                'details': json.dumps({
                    'ip_address': f"192.168.1.{random.randint(1, 255)}",
                    'user_agent': 'FaradayAI/1.0',
                    'changes': random.choice([
                        {'field': 'status', 'old_value': 'INACTIVE', 'new_value': 'ACTIVE'},
                        {'field': 'name', 'old_value': 'Old Name', 'new_value': 'New Name'},
                        {'field': 'permissions', 'old_value': 'READ', 'new_value': 'READ,WRITE'},
                        None
                    ])
                }),
                'timestamp': datetime.utcnow() - timedelta(days=random.randint(0, 30))
            })
        
        # Insert audit logs
        for audit in audit_data:
            session.execute(text("""
                INSERT INTO audit_logs (
                    user_id, action, resource_type, resource_id, details, timestamp
                ) VALUES (
                    :user_id, :action, :resource_type, :resource_id, :details, :timestamp
                )
            """), audit)
        
        print(f"      ✅ Created {len(audit_data)} audit logs")
        
    except Exception as e:
        print(f"      ⚠️  Audit logs table not available: {e}")

def seed_system_utilities(session):
    """Seed other system utility tables"""
    print("    🔄 Seeding system utilities...")
    
    # Check if system_settings table exists and seed it
    try:
        result = session.execute(text("SELECT COUNT(*) FROM system_settings"))
        if result.scalar() > 0:
            print("      ✅ system_settings already has data")
            return
        
        # Create sample system settings
        settings_data = [
            {
                'key': 'maintenance_mode',
                'value': 'false',
                'description': 'System maintenance mode flag',
                'category': 'SYSTEM'
            },
            {
                'key': 'max_file_size',
                'value': '10485760',
                'description': 'Maximum file upload size in bytes',
                'category': 'UPLOAD'
            },
            {
                'key': 'session_timeout',
                'value': '3600',
                'description': 'User session timeout in seconds',
                'category': 'SECURITY'
            },
            {
                'key': 'email_notifications',
                'value': 'true',
                'description': 'Enable email notifications',
                'category': 'NOTIFICATIONS'
            },
            {
                'key': 'debug_mode',
                'value': 'false',
                'description': 'Enable debug mode for development',
                'category': 'DEVELOPMENT'
            },
            {
                'key': 'backup_frequency',
                'value': 'daily',
                'description': 'System backup frequency',
                'category': 'BACKUP'
            },
            {
                'key': 'max_concurrent_users',
                'value': '1000',
                'description': 'Maximum concurrent users allowed',
                'category': 'PERFORMANCE'
            },
            {
                'key': 'content_moderation',
                'value': 'true',
                'description': 'Enable content moderation',
                'category': 'CONTENT'
            }
        ]
        
        # Insert system settings
        for setting in settings_data:
            session.execute(text("""
                INSERT INTO system_settings (
                    key, value, description, category, created_at, updated_at
                ) VALUES (
                    :key, :value, :description, :category, :now, :now
                )
            """), {
                **setting,
                "now": datetime.utcnow()
            })
        
        print(f"      ✅ Created {len(settings_data)} system settings")
        
    except Exception as e:
        print(f"      ⚠️  System settings table not available: {e}")
    
    # Check if feature_flags table exists and seed it
    try:
        result = session.execute(text("SELECT COUNT(*) FROM feature_flags"))
        if result.scalar() > 0:
            print("      ✅ feature_flags already has data")
            return
        
        # Create sample feature flags
        feature_data = [
            {
                'name': 'ai_assistant',
                'is_enabled': True,
                'description': 'AI-powered teaching assistant',
                'category': 'AI_FEATURES'
            },
            {
                'name': 'real_time_analytics',
                'is_enabled': True,
                'description': 'Real-time performance analytics',
                'category': 'ANALYTICS'
            },
            {
                'name': 'mobile_app',
                'is_enabled': False,
                'description': 'Mobile application access',
                'category': 'PLATFORM'
            },
            {
                'name': 'advanced_reporting',
                'is_enabled': True,
                'description': 'Advanced reporting and insights',
                'category': 'REPORTING'
            },
            {
                'name': 'social_features',
                'is_enabled': False,
                'description': 'Social learning features',
                'category': 'SOCIAL'
            },
            {
                'name': 'gamification',
                'is_enabled': True,
                'description': 'Gamification elements',
                'category': 'ENGAGEMENT'
            }
        ]
        
        # Insert feature flags
        for feature in feature_data:
            session.execute(text("""
                INSERT INTO feature_flags (
                    name, is_enabled, description, category, created_at, updated_at
                ) VALUES (
                    :name, :is_enabled, :description, :category, :now, :now
                )
            """), {
                **feature,
                "now": datetime.utcnow()
            })
        
        print(f"      ✅ Created {len(feature_data)} feature flags")
        
    except Exception as e:
        print(f"      ⚠️  Feature flags table not available: {e}")

def seed_avatar_system(session):
    """Seed avatar system to complete user profiles"""
    print("🔄 Seeding avatar system...")
    
    # First, seed the roles table
    print("  🔄 Seeding roles table...")
    try:
        result = session.execute(text("SELECT COUNT(*) FROM roles"))
        roles_count = result.scalar()
        
        if roles_count > 0:
            print("    ✅ Roles table already has data")
        else:
            print("    📊 Roles table has 0 records - creating basic roles...")
            
            # Create basic roles
            basic_roles = [
                {'name': 'STUDENT', 'description': 'Student role with learning access', 'is_custom': False, 'status': 'ACTIVE', 'is_active': True},
                {'name': 'TEACHER', 'description': 'Teacher role with educational access', 'is_custom': False, 'status': 'ACTIVE', 'is_active': True},
                {'name': 'COACH', 'description': 'Coach role with training access', 'is_custom': False, 'status': 'ACTIVE', 'is_active': True},
                {'name': 'PARENT', 'description': 'Parent role with monitoring access', 'is_custom': False, 'status': 'ACTIVE', 'is_active': True},
                {'name': 'ADMIN', 'description': 'Administrator role with system access', 'is_custom': False, 'status': 'ACTIVE', 'is_active': True},
                {'name': 'MODERATOR', 'description': 'Moderator role with content access', 'is_custom': False, 'status': 'ACTIVE', 'is_active': True},
                {'name': 'GUEST', 'description': 'Limited read-only access', 'is_custom': False, 'status': 'ACTIVE', 'is_active': True}
            ]
            
            # Insert roles
            for role_data in basic_roles:
                session.execute(text("""
                    INSERT INTO roles (name, description, is_custom, status, is_active)
                    VALUES (:name, :description, :is_custom, :status, :is_active)
                """), role_data)
            
            print(f"    ✅ Created {len(basic_roles)} basic roles")
            
            # Now update user_roles to use proper role IDs
            print("    🔄 Updating user_roles with proper role assignments...")
            
            # Get the roles we just created
            result = session.execute(text("SELECT id, name FROM roles"))
            role_mapping = {role_name: role_id for role_id, role_name in result.fetchall()}
            
            # Get users and their dashboard roles
            result = session.execute(text("SELECT id, role FROM dashboard_users LIMIT 10"))
            users = result.fetchall()
            
            # Update user_roles table
            for user_id, dashboard_role in users:
                # Map dashboard role to roles table role
                if dashboard_role in role_mapping:
                    role_id = role_mapping[dashboard_role]
                    
                    # Check if user_roles entry exists
                    result = session.execute(text("SELECT COUNT(*) FROM user_roles WHERE user_id = :user_id"), {'user_id': user_id})
                    if result.scalar() > 0:
                        # Update existing entry
                        session.execute(text("""
                            UPDATE user_roles 
                            SET role_id = :role_id 
                            WHERE user_id = :user_id
                        """), {'role_id': role_id, 'user_id': user_id})
                    else:
                        # Create new entry
                        session.execute(text("""
                            INSERT INTO user_roles (user_id, role_id)
                            VALUES (:user_id, :role_id)
                        """), {'user_id': user_id, 'role_id': role_id})
            
            print(f"    ✅ Updated user_roles for {len(users)} users")
    
    except Exception as e:
        print(f"    ⚠️  Roles table seeding failed: {e}")
    
    # Now seed the avatars table
    print("  🔄 Seeding avatars table...")
    try:
        result = session.execute(text("SELECT COUNT(*) FROM avatars"))
        avatar_count = result.scalar()
        
        if avatar_count > 0:
            print("    ✅ Avatars table already has data")
        else:
            print("    📊 Avatars table has 0 records - creating AI avatars...")
            
            # Create AI-powered avatars
            avatar_data = []
            
            # AI avatar types using correct enum values
            avatar_types = [
                {'type': 'STATIC', 'url': '/static/avatars/static_01.png'},
                {'type': 'ANIMATED', 'url': '/static/avatars/animated_01.png'},
                {'type': 'THREE_D', 'url': '/static/avatars/3d_01.png'},
                {'type': 'STATIC', 'url': '/static/avatars/static_02.png'},
                {'type': 'ANIMATED', 'url': '/static/avatars/animated_02.png'},
                {'type': 'THREE_D', 'url': '/static/avatars/3d_02.png'},
                {'type': 'STATIC', 'url': '/static/avatars/static_03.png'},
                {'type': 'ANIMATED', 'url': '/static/avatars/animated_03.png'},
                {'type': 'THREE_D', 'url': '/static/avatars/3d_03.png'},
                {'type': 'STATIC', 'url': '/static/avatars/static_04.png'}
            ]
            
            for i, avatar_info in enumerate(avatar_types, 1):
                avatar_data.append({
                    'id': i,
                    'type': avatar_info['type'],
                    'url': avatar_info['url'],
                    'config': json.dumps({
                        'personality': random.choice(['friendly', 'energetic', 'calm', 'enthusiastic', 'professional', 'encouraging']),
                        'specialties': random.choice(['sports', 'dance', 'fitness', 'education', 'wellness', 'leadership']),
                        'accessibility': random.choice([True, False]),
                        'interaction_style': random.choice(['formal', 'casual', 'playful', 'serious', 'motivational'])
                    }),
                    'voice_enabled': random.choice([True, False]),
                    'voice_config': json.dumps({
                        'voice_type': random.choice(['male', 'female', 'neutral']),
                        'speed': random.choice(['slow', 'normal', 'fast']),
                        'pitch': random.uniform(0.8, 1.2),
                        'language': random.choice(['en', 'es', 'fr'])
                    }) if random.choice([True, False]) else None,
                    'expression_config': json.dumps({
                        'expressions': ['happy', 'encouraging', 'focused', 'celebratory'],
                        'intensity': random.uniform(0.5, 1.0),
                        'response_time': random.randint(100, 500)
                    }),
                    'gesture_config': json.dumps({
                        'gestures': ['pointing', 'clapping', 'thumbs_up', 'wave'],
                        'animation_speed': random.uniform(0.8, 1.2),
                        'synchronization': random.choice([True, False])
                    }),
                    'created_at': datetime.utcnow() - timedelta(days=random.randint(0, 30)),
                    'updated_at': datetime.utcnow()
                })
            
            # Insert avatars
            for avatar in avatar_data:
                session.execute(text("""
                    INSERT INTO avatars (
                        id, type, url, config, voice_enabled, voice_config, expression_config, gesture_config, created_at, updated_at
                    ) VALUES (
                        :id, :type, :url, :config, :voice_enabled, :voice_config, :expression_config, :gesture_config, :created_at, :updated_at
                    )
                """), avatar)
            
            print(f"    ✅ Created {len(avatar_data)} AI-powered avatars")
            
            # Now update user profiles to assign avatars
            print("    🔄 Updating user profiles with avatar assignments...")
            
            # Get user profiles without avatars
            result = session.execute(text("""
                SELECT up.id, up.user_id 
                FROM user_profiles up 
                WHERE up.avatar_id IS NULL
            """))
            profiles_without_avatars = result.fetchall()
            
            if profiles_without_avatars:
                # Get available avatar IDs
                result = session.execute(text("SELECT id FROM avatars"))
                available_avatar_ids = [row[0] for row in result.fetchall()]
                
                # Assign avatars to profiles
                for profile_id, user_id in profiles_without_avatars:
                    avatar_id = random.choice(available_avatar_ids)
                    session.execute(text("""
                        UPDATE user_profiles 
                        SET avatar_id = :avatar_id
                        WHERE id = :profile_id
                    """), {
                        'avatar_id': avatar_id,
                        'profile_id': profile_id
                    })
                
                print(f"    ✅ Assigned avatars to {len(profiles_without_avatars)} user profiles")
            else:
                print("    ✅ All user profiles already have avatars")
    
    except Exception as e:
        print(f"    ⚠️  Avatar system not available: {e}")
        print("    📝 Note: User profiles will continue without avatars")
    
    print("  ✅ Avatar and roles system seeding complete!")
    
    # Seed activity_logs table
    try:
        result = session.execute(text("SELECT COUNT(*) FROM activity_logs"))
        if result.scalar() > 0:
            print("      ✅ activity_logs already has data")
        else:
            # Get user and organization IDs
            user_result = session.execute(text("SELECT id FROM users LIMIT 10"))
            user_ids = [row[0] for row in user_result.fetchall()]
            
            org_result = session.execute(text("SELECT id FROM organizations LIMIT 5"))
            org_ids = [row[0] for row in org_result.fetchall()]
            
            if not user_ids:
                user_ids = [1, 2, 3, 4, 5]  # Fallback IDs
            if not org_ids:
                org_ids = [1, 2, 3]  # Fallback IDs
            
            # Create sample activity logs
            actions = ['CREATE', 'UPDATE', 'DELETE', 'VIEW', 'EXPORT', 'IMPORT', 'LOGIN', 'LOGOUT']
            resource_types = ['USER', 'STUDENT', 'LESSON', 'EXERCISE', 'ACTIVITY', 'ASSESSMENT', 'CURRICULUM']
            
            activity_logs_data = []
            for i in range(200):  # Create 200 sample activity log entries
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
            
            # Insert activity logs
            for log in activity_logs_data:
                session.execute(text("""
                    INSERT INTO activity_logs (
                        action, resource_type, resource_id, details, user_id, org_id, timestamp, created_at, updated_at
                    ) VALUES (
                        :action, :resource_type, :resource_id, :details, :user_id, :org_id, :timestamp, :created_at, :updated_at
                    )
                """), log)
            
            print(f"      ✅ Created {len(activity_logs_data)} activity logs")
        
    except Exception as e:
        print(f"      ⚠️  Activity logs table not available: {e}")

if __name__ == "__main__":
    seed_phase1_foundation() 