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

def seed_phase1_foundation(session=None):
    """Main function to seed Phase 1 foundation tables"""
    print("\n" + "="*60)
    print("🌱 PHASE 1: FOUNDATION & CORE INFRASTRUCTURE SEEDING")
    print("="*60)
    
    if session is None:
        session = SessionLocal()
        should_close_session = True
    else:
        should_close_session = False
    
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
        
        # Phase 1.2: Complete Avatar System (MOVED BEFORE SYSTEM CONFIGURATION)
        print("\n📋 PHASE 1.2: Complete Avatar System")
        print("-" * 40)
        try:
            seed_avatar_system(session)
            session.commit()
            print("✅ Phase 1.2 completed successfully!")
        except Exception as e:
            session.rollback()
            print(f"❌ Phase 1.2 failed: {e}")
            # Continue to next phase
        
        # Phase 1.3: System Configuration (MOVED AFTER AVATAR SYSTEM)
        print("\n📋 PHASE 1.3: System Configuration")
        print("-" * 40)
        try:
            seed_system_configuration(session)
            session.commit()
            print("✅ Phase 1.3 completed successfully!")
        except Exception as e:
            session.rollback()
            print(f"❌ Phase 1.3 failed: {e}")
            # Continue to next phase
        
        # Phase 1.4: Basic Infrastructure
        print("\n📋 PHASE 1.4: Basic Infrastructure")
        print("-" * 40)
        try:
            seed_basic_infrastructure(session)
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
        if should_close_session:
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
    result = session.execute(text("SELECT id FROM dashboard_users"))
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
    result = session.execute(text("SELECT id, role FROM dashboard_users"))
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
    result = session.execute(text("SELECT id FROM dashboard_users"))
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
    result = session.execute(text("SELECT id FROM dashboard_users"))
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
    result = session.execute(text("SELECT id FROM dashboard_users"))
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
    result = session.execute(text("SELECT id FROM dashboard_users"))
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
    result = session.execute(text("SELECT id FROM dashboard_users"))
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
    result = session.execute(text("SELECT id FROM dashboard_users"))
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
    result = session.execute(text("SELECT id FROM dashboard_users"))
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
    result = session.execute(text("SELECT id FROM dashboard_users"))
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
    else:
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
                INSERT INTO access_control_roles (name, description, status, is_active, created_at, updated_at)
                VALUES (:name, :description, :status, :is_active, :now, :now)
            """), {
                **role_data,
                "status": "ACTIVE",
                "now": datetime.utcnow()
            })
        
        print(f"      ✅ Created {len(roles_data)} access control roles")
    
    # Now seed permissions
    seed_access_control_permissions(session)
    
    # Then seed role-permission mappings
    seed_role_permissions(session)
    
    # Seed permissions table first
    seed_permissions_table(session)
    
    # Seed additional role-permission table
    seed_role_permissions_table(session)
    
    # Seed permission overrides
    seed_permission_overrides(session)
    
    # Seed feedback user tool settings
    seed_feedback_user_tool_settings(session)
    
    # Seed user management voice preferences
    seed_user_management_voice_preferences(session)
    
    # Seed additional user management tables
    seed_user_management_preferences(session)
    seed_user_management_user_organizations(session)
    seed_user_tool_settings(session)
    seed_user_tools(session)
    seed_user_preference_categories(session)
    seed_user_preference_templates(session)
    seed_user_preference_template_assignments(session)
    seed_user_recommendations(session)
    seed_role_hierarchy(session)
    seed_role_templates(session)
    seed_security_preferences(session)
    seed_security_logs(session)
    seed_sessions(session)
    seed_shared_contexts(session)
    seed_tool_assignments(session)
    seed_voice_templates(session)
    seed_voices(session)
    
    # Seed avatar system (HARD tables - need to be in order)
    seed_avatar_templates(session)  # First - no dependencies
    seed_user_avatars(session)      # Second - depends on avatar_templates + users
    seed_user_avatar_customizations(session)  # Third - depends on user_avatars
    seed_avatar_customizations(session)
    seed_student_avatar_customizations(session)
    
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
        {'name': 'USER_CREATE', 'description': 'Create new users', 'resource_type': 'users', 'action': 'create', 'permission_type': 'WRITE'},
        {'name': 'USER_READ', 'description': 'Read user information', 'resource_type': 'users', 'action': 'read', 'permission_type': 'READ'},
        {'name': 'USER_UPDATE', 'description': 'Update user information', 'resource_type': 'users', 'action': 'update', 'permission_type': 'WRITE'},
        {'name': 'USER_DELETE', 'description': 'Delete users', 'resource_type': 'users', 'action': 'delete', 'permission_type': 'DELETE'},
        
        # Educational Content
        {'name': 'LESSON_CREATE', 'description': 'Create lessons', 'resource_type': 'lessons', 'action': 'create', 'permission_type': 'WRITE'},
        {'name': 'LESSON_READ', 'description': 'Read lessons', 'resource_type': 'lessons', 'action': 'read', 'permission_type': 'READ'},
        {'name': 'LESSON_UPDATE', 'description': 'Update lessons', 'resource_type': 'lessons', 'action': 'update', 'permission_type': 'WRITE'},
        {'name': 'LESSON_DELETE', 'description': 'Delete lessons', 'resource_type': 'lessons', 'action': 'delete', 'permission_type': 'DELETE'},
        
        # Physical Education
        {'name': 'EXERCISE_CREATE', 'description': 'Create exercises', 'resource_type': 'exercises', 'action': 'create', 'permission_type': 'WRITE'},
        {'name': 'EXERCISE_READ', 'description': 'Read exercises', 'resource_type': 'exercises', 'action': 'read', 'permission_type': 'READ'},
        {'name': 'EXERCISE_UPDATE', 'description': 'Update exercises', 'resource_type': 'exercises', 'action': 'update', 'permission_type': 'WRITE'},
        {'name': 'EXERCISE_DELETE', 'description': 'Delete exercises', 'resource_type': 'exercises', 'action': 'delete', 'permission_type': 'DELETE'},
        
        # Assessment & Analytics
        {'name': 'ASSESSMENT_CREATE', 'description': 'Create assessments', 'resource_type': 'assessments', 'action': 'create', 'permission_type': 'WRITE'},
        {'name': 'ASSESSMENT_READ', 'description': 'Read assessments', 'resource_type': 'assessments', 'action': 'read', 'permission_type': 'READ'},
        {'name': 'ASSESSMENT_UPDATE', 'description': 'Update assessments', 'resource_type': 'assessments', 'action': 'update', 'permission_type': 'WRITE'},
        {'name': 'ASSESSMENT_DELETE', 'description': 'Delete assessments', 'resource_type': 'assessments', 'action': 'delete', 'permission_type': 'DELETE'},
        
        # System Administration
        {'name': 'SYSTEM_CONFIG', 'description': 'Configure system settings', 'resource_type': 'system', 'action': 'configure', 'permission_type': 'ADMIN'},
        {'name': 'FEATURE_TOGGLE', 'description': 'Toggle feature flags', 'resource_type': 'features', 'action': 'toggle', 'permission_type': 'ADMIN'},
        {'name': 'LOG_ACCESS', 'description': 'Access system logs', 'resource_type': 'logs', 'action': 'read', 'permission_type': 'READ'},
        {'name': 'BACKUP_RESTORE', 'description': 'Backup and restore data', 'resource_type': 'system', 'action': 'backup', 'permission_type': 'ADMIN'}
    ]
    
    # Insert permissions
    for perm_data in permissions_data:
        session.execute(text("""
            INSERT INTO access_control_permissions (name, description, resource_type, action, permission_type, status, is_active, created_at, updated_at)
            VALUES (:name, :description, :resource_type, :action, :permission_type, :status, :is_active, :now, :now)
        """), {
            **perm_data,
            "status": "ACTIVE",
            "is_active": True,
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
            INSERT INTO access_control_role_permissions (role_id, permission_id, status, is_active, created_at, updated_at)
            VALUES (:role_id, :permission_id, :status, :is_active, :now, :now)
        """), {
            **rp,
            "status": "ACTIVE",
            "is_active": True,
            "now": datetime.utcnow()
        })
    
    print(f"        ✅ Created {len(role_permissions)} role-permission mappings")

def seed_permissions_table(session):
    """Seed the permissions table (separate from access_control_permissions)"""
    print("      🔄 Seeding permissions table...")
    
    # Check if already has data
    result = session.execute(text("SELECT COUNT(*) FROM permissions"))
    if result.scalar() > 0:
        print("        ✅ permissions already has data")
        return
    
    # Create basic permissions
    permissions_data = [
        {'name': 'read_users', 'description': 'Read user information', 'resource_type': 'users', 'action': 'read', 'status': 'ACTIVE', 'is_active': True},
        {'name': 'write_users', 'description': 'Create and update users', 'resource_type': 'users', 'action': 'write', 'status': 'ACTIVE', 'is_active': True},
        {'name': 'delete_users', 'description': 'Delete users', 'resource_type': 'users', 'action': 'delete', 'status': 'ACTIVE', 'is_active': True},
        {'name': 'read_roles', 'description': 'Read role information', 'resource_type': 'roles', 'action': 'read', 'status': 'ACTIVE', 'is_active': True},
        {'name': 'write_roles', 'description': 'Create and update roles', 'resource_type': 'roles', 'action': 'write', 'status': 'ACTIVE', 'is_active': True},
        {'name': 'read_permissions', 'description': 'Read permission information', 'resource_type': 'permissions', 'action': 'read', 'status': 'ACTIVE', 'is_active': True},
        {'name': 'write_permissions', 'description': 'Create and update permissions', 'resource_type': 'permissions', 'action': 'write', 'status': 'ACTIVE', 'is_active': True},
        {'name': 'admin_access', 'description': 'Full administrative access', 'resource_type': 'system', 'action': 'admin', 'status': 'ACTIVE', 'is_active': True}
    ]
    
    # Insert permissions
    for perm in permissions_data:
        session.execute(text("""
            INSERT INTO permissions (name, description, resource_type, action, status, is_active)
            VALUES (:name, :description, :resource_type, :action, :status, :is_active)
        """), perm)
    
    print(f"        ✅ Created {len(permissions_data)} permissions")

def seed_role_permissions_table(session):
    """Seed the role_permissions table (separate from access_control_role_permissions)"""
    print("      🔄 Seeding role_permissions table...")
    
    # Check if already has data
    result = session.execute(text("SELECT COUNT(*) FROM role_permissions"))
    if result.scalar() > 0:
        print("        ✅ role_permissions already has data")
        return
    
    # Get role IDs and permission IDs
    roles = session.execute(text("SELECT id FROM roles")).fetchall()
    permissions = session.execute(text("SELECT id FROM permissions")).fetchall()
    
    if not roles or not permissions:
        print("        ⚠️ No roles or permissions found, skipping role_permissions")
        return
    
    # Create role-permission mappings for the role_permissions table
    role_permissions = []
    for role_id, in roles:
        for perm_id, in permissions:
            role_permissions.append({'role_id': role_id, 'permission_id': perm_id})
    
    # Insert role-permission mappings
    for rp in role_permissions:
        session.execute(text("""
            INSERT INTO role_permissions (role_id, permission_id)
            VALUES (:role_id, :permission_id)
        """), rp)
    
    print(f"        ✅ Created {len(role_permissions)} role-permission mappings")

def seed_permission_overrides(session):
    """Seed permission overrides for specific users"""
    print("      🔄 Seeding permission overrides...")
    
    # Check if already has data
    result = session.execute(text("SELECT COUNT(*) FROM permission_overrides"))
    if result.scalar() > 0:
        print("        ✅ permission_overrides already has data")
        return
    
    # Get some users and permissions
    users = session.execute(text("SELECT id FROM users")).fetchall()
    permissions = session.execute(text("SELECT id FROM access_control_permissions LIMIT 3")).fetchall()
    
    if not users or not permissions:
        print("        ⚠️ No users or permissions found, skipping permission_overrides")
        return
    
    overrides = []
    for i, (user_id,) in enumerate(users):
        for j, (perm_id,) in enumerate(permissions):
            overrides.append({
                'user_id': user_id,
                'permission_id': perm_id,
                'is_allowed': True,
                'reason': f'Override for user {user_id}',
                'expires_at': None,
                'status': 'ACTIVE',
                'is_active': True
            })
    
    # Insert permission overrides
    for override in overrides:
        session.execute(text("""
            INSERT INTO permission_overrides (user_id, permission_id, is_allowed, reason, expires_at, status, is_active)
            VALUES (:user_id, :permission_id, :is_allowed, :reason, :expires_at, :status, :is_active)
        """), override)
    
    print(f"        ✅ Created {len(overrides)} permission overrides")

def seed_feedback_user_tool_settings(session):
    """Seed feedback user tool settings"""
    print("      🔄 Seeding feedback user tool settings...")
    
    # Check if already has data
    result = session.execute(text("SELECT COUNT(*) FROM feedback_user_tool_settings"))
    if result.scalar() > 0:
        print("        ✅ feedback_user_tool_settings already has data")
        return
    
    # Get some users
    users = session.execute(text("SELECT id FROM users")).fetchall()
    if not users:
        print("        ⚠️ No users found, skipping feedback_user_tool_settings")
        return
    
    # Get existing tool IDs or create a default one
    tools = session.execute(text("SELECT id FROM dashboard_tools")).fetchall()
    if not tools:
        # Create a default tool if none exist
        result = session.execute(text("""
            INSERT INTO dashboard_tools (name, description, category, created_at, updated_at)
            VALUES ('Default Tool', 'Default tool for feedback settings', 'FEEDBACK', :now, :now)
            RETURNING id
        """), {"now": datetime.utcnow()})
        tool_id = result.scalar()
        tools = [(tool_id,)]  # Use the actual tool ID returned
    
    settings = []
    for user_id, in users:
        tool_id = tools[0][0]  # Use the first available tool ID
        settings.append({
            'user_id': user_id,
            'tool_id': tool_id,
            'is_enabled': True,
            'settings': '{"theme": "dark", "notifications": true}',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        })
    
    # Insert feedback user tool settings
    for setting in settings:
        session.execute(text("""
            INSERT INTO feedback_user_tool_settings (user_id, tool_id, is_enabled, settings, created_at, updated_at)
            VALUES (:user_id, :tool_id, :is_enabled, :settings, :created_at, :updated_at)
        """), setting)
    
    print(f"        ✅ Created {len(settings)} feedback user tool settings")

def seed_user_management_voice_preferences(session):
    """Seed user management voice preferences"""
    print("      🔄 Seeding user management voice preferences...")
    
    # Check if already has data
    result = session.execute(text("SELECT COUNT(*) FROM user_management_voice_preferences"))
    if result.scalar() > 0:
        print("        ✅ user_management_voice_preferences already has data")
        return
    
    # Get some users
    users = session.execute(text("SELECT id FROM users")).fetchall()
    if not users:
        print("        ⚠️ No users found, skipping user_management_voice_preferences")
        return
    
    preferences = []
    for user_id, in users:
        preferences.append({
            'avatar_id': 1,
            'user_id': user_id,
            'voice_id': 1,
            'language': 'en-US',
            'speed': 100,
            'pitch': 50,
            'provider': 'GOOGLE',
            'style': 'conversational',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'metadata': '{"quality": "high", "accent": "american"}'
        })
    
    # Insert user management voice preferences
    for preference in preferences:
        session.execute(text("""
            INSERT INTO user_management_voice_preferences (avatar_id, user_id, voice_id, language, speed, pitch, provider, style, created_at, updated_at, metadata)
            VALUES (:avatar_id, :user_id, :voice_id, :language, :speed, :pitch, :provider, :style, :created_at, :updated_at, :metadata)
        """), preference)
    
    print(f"        ✅ Created {len(preferences)} user management voice preferences")

def seed_user_management_preferences(session):
    """Seed user management preferences"""
    print("      🔄 Seeding user management preferences...")
    
    # Check if already has data
    result = session.execute(text("SELECT COUNT(*) FROM user_management_preferences"))
    if result.scalar() > 0:
        print("        ✅ user_management_preferences already has data")
        return
    
    # Get some users
    users = session.execute(text("SELECT id FROM users")).fetchall()
    if not users:
        print("        ⚠️ No users found, skipping user_management_preferences")
        return
    
    preferences = []
    for user_id, in users:
        preferences.append({
            'user_id': user_id,
            'category_id': None,
            'type': 'THEME',
            'config': '{"theme": "dark", "notifications": true}',
            'is_active': True,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        })
    
    # Insert user management preferences
    for preference in preferences:
        session.execute(text("""
            INSERT INTO user_management_preferences (user_id, category_id, type, config, is_active, created_at, updated_at)
            VALUES (:user_id, :category_id, :type, :config, :is_active, :created_at, :updated_at)
        """), preference)
    
    print(f"        ✅ Created {len(preferences)} user management preferences")

def seed_user_management_user_organizations(session):
    """Seed user management user organizations"""
    print("      🔄 Seeding user management user organizations...")
    
    # Check if already has data
    result = session.execute(text("SELECT COUNT(*) FROM user_management_user_organizations"))
    if result.scalar() > 0:
        print("        ✅ user_management_user_organizations already has data")
        return
    
    # Get some users and organizations
    users = session.execute(text("SELECT id FROM users")).fetchall()
    organizations = session.execute(text("SELECT id FROM organizations")).fetchall()
    
    if not users or not organizations:
        print("        ⚠️ No users or organizations found, skipping user_management_user_organizations")
        return
    
    user_orgs = []
    for user_id, in users:
        for org_id, in organizations:
            user_orgs.append({
                'user_id': user_id,
                'organization_id': org_id,
                'role': 'MEMBER',
                'status': 'ACTIVE',
                'is_active': True
            })
    
    # Insert user management user organizations
    for user_org in user_orgs:
        session.execute(text("""
            INSERT INTO user_management_user_organizations (user_id, organization_id, role, status, is_active)
            VALUES (:user_id, :organization_id, :role, :status, :is_active)
        """), user_org)
    
    print(f"        ✅ Created {len(user_orgs)} user management user organizations")

def seed_user_tool_settings(session):
    """Seed user tool settings"""
    print("      🔄 Seeding user tool settings...")
    
    # Check if already has data
    result = session.execute(text("SELECT COUNT(*) FROM user_tool_settings"))
    if result.scalar() > 0:
        print("        ✅ user_tool_settings already has data")
        return
    
    # Get some users and tools
    users = session.execute(text("SELECT id FROM users")).fetchall()
    tools = session.execute(text("SELECT id FROM dashboard_tools")).fetchall()
    
    if not users or not tools:
        print("        ⚠️ No users or tools found, skipping user_tool_settings")
        return
    
    settings = []
    for user_id, in users:
        for tool_id, in tools:
            settings.append({
                'user_id': user_id,
                'tool_id': tool_id,
                'is_enabled': True,
                'settings': '{"theme": "dark", "notifications": true}',
                'last_used': datetime.utcnow(),
                'usage_count': 0,
                'rate_limit_remaining': 100,
                'rate_limit_reset': datetime.utcnow(),
                'error_count': 0,
                'last_error': None,
                'last_success': datetime.utcnow(),
                'avatar_customization': '{"color": "blue"}',
                'voice_preferences': '{"speed": 1.0, "pitch": 1.0}'
            })
    
    # Insert user tool settings
    for setting in settings:
        session.execute(text("""
            INSERT INTO user_tool_settings (user_id, tool_id, is_enabled, settings, last_used, usage_count, rate_limit_remaining, rate_limit_reset, error_count, last_error, last_success, avatar_customization, voice_preferences)
            VALUES (:user_id, :tool_id, :is_enabled, :settings, :last_used, :usage_count, :rate_limit_remaining, :rate_limit_reset, :error_count, :last_error, :last_success, :avatar_customization, :voice_preferences)
        """), setting)
    
    print(f"        ✅ Created {len(settings)} user tool settings")

def seed_user_tools(session):
    """Seed user tools"""
    print("      🔄 Seeding user tools...")
    
    # Check if already has data
    result = session.execute(text("SELECT COUNT(*) FROM user_tools"))
    if result.scalar() > 0:
        print("        ✅ user_tools already has data")
        return
    
    # Get some users and tools
    users = session.execute(text("SELECT id FROM users")).fetchall()
    tools = session.execute(text("SELECT id FROM dashboard_tools")).fetchall()
    
    if not users or not tools:
        print("        ⚠️ No users or tools found, skipping user_tools")
        return
    
    user_tools = []
    for user_id, in users:
        for tool_id, in tools:
            user_tools.append({
                'user_id': user_id,
                'tool_id': tool_id
            })
    
    # Insert user tools
    for user_tool in user_tools:
        session.execute(text("""
            INSERT INTO user_tools (user_id, tool_id)
            VALUES (:user_id, :tool_id)
        """), user_tool)
    
    print(f"        ✅ Created {len(user_tools)} user tools")

def seed_user_preference_categories(session):
    """Seed user preference categories"""
    print("      🔄 Seeding user preference categories...")
    
    # Check if already has data
    result = session.execute(text("SELECT COUNT(*) FROM user_preference_categories"))
    if result.scalar() > 0:
        print("        ✅ user_preference_categories already has data")
        return
    
    categories = [
        {'name': 'Display', 'description': 'Display preferences', 'category_metadata': '{"type": "ui", "priority": "high"}'},
        {'name': 'Notifications', 'description': 'Notification preferences', 'category_metadata': '{"type": "communication", "priority": "medium"}'},
        {'name': 'Privacy', 'description': 'Privacy preferences', 'category_metadata': '{"type": "security", "priority": "high"}'},
        {'name': 'Accessibility', 'description': 'Accessibility preferences', 'category_metadata': '{"type": "accessibility", "priority": "high"}'},
        {'name': 'Language', 'description': 'Language preferences', 'category_metadata': '{"type": "localization", "priority": "medium"}'}
    ]
    
    # Insert user preference categories
    for category in categories:
        session.execute(text("""
            INSERT INTO user_preference_categories (name, description, category_metadata)
            VALUES (:name, :description, :category_metadata)
        """), category)
    
    print(f"        ✅ Created {len(categories)} user preference categories")

def seed_user_preference_templates(session):
    """Seed user preference templates"""
    print("      🔄 Seeding user preference templates...")
    
    # Check if already has data
    result = session.execute(text("SELECT COUNT(*) FROM user_preference_templates"))
    if result.scalar() > 0:
        print("        ✅ user_preference_templates already has data")
        return
    
    templates = [
        {'name': 'Default', 'description': 'Default user preferences', 'template_data': '{"theme": "light", "notifications": true}', 'template_metadata': '{"version": "1.0", "type": "default"}'},
        {'name': 'Teacher', 'description': 'Teacher-specific preferences', 'template_data': '{"theme": "professional", "notifications": true}', 'template_metadata': '{"version": "1.0", "type": "teacher"}'},
        {'name': 'Student', 'description': 'Student-specific preferences', 'template_data': '{"theme": "bright", "notifications": false}', 'template_metadata': '{"version": "1.0", "type": "student"}'},
        {'name': 'Admin', 'description': 'Admin-specific preferences', 'template_data': '{"theme": "dark", "notifications": true}', 'template_metadata': '{"version": "1.0", "type": "admin"}'}
    ]
    
    # Insert user preference templates
    for template in templates:
        session.execute(text("""
            INSERT INTO user_preference_templates (name, description, template_data, template_metadata)
            VALUES (:name, :description, :template_data, :template_metadata)
        """), template)
    
    print(f"        ✅ Created {len(templates)} user preference templates")

def seed_user_preference_template_assignments(session):
    """Seed user preference template assignments"""
    print("      🔄 Seeding user preference template assignments...")
    
    # Check if already has data
    result = session.execute(text("SELECT COUNT(*) FROM user_preference_template_assignments"))
    if result.scalar() > 0:
        print("        ✅ user_preference_template_assignments already has data")
        return
    
    # Get some users and templates
    users = session.execute(text("SELECT id FROM users")).fetchall()
    templates = session.execute(text("SELECT id FROM user_preference_templates LIMIT 4")).fetchall()
    
    if not users or not templates:
        print("        ⚠️ No users or templates found, skipping user_preference_template_assignments")
        return
    
    assignments = []
    for user_id, in users:
        for template_id, in templates:
            assignments.append({
                'user_id': user_id,
                'template_id': template_id
            })
    
    # Insert user preference template assignments
    for assignment in assignments:
        session.execute(text("""
            INSERT INTO user_preference_template_assignments (user_id, template_id)
            VALUES (:user_id, :template_id)
        """), assignment)
    
    print(f"        ✅ Created {len(assignments)} user preference template assignments")

def seed_user_recommendations(session):
    """Seed user recommendations"""
    print("      🔄 Seeding user recommendations...")
    
    # Check if already has data
    result = session.execute(text("SELECT COUNT(*) FROM user_recommendations"))
    if result.scalar() > 0:
        print("        ✅ user_recommendations already has data")
        return
    
    # Get some users
    users = session.execute(text("SELECT id FROM users")).fetchall()
    if not users:
        print("        ⚠️ No users found, skipping user_recommendations")
        return
    
    recommendations = []
    for user_id, in users:
        recommendations.append({
            'user_id': user_id,
            'recommendation_type': 'FEATURE',
            'recommendation_data': '{"title": "Try new features", "description": "Explore new features available in the system"}',
            'priority_score': 0.7,
            'category': 'SYSTEM',
            'actionable_items': '["Enable notifications", "Update profile"]',
            'timestamp': datetime.utcnow(),
            'is_implemented': False,
            'implementation_date': None
        })
    
    # Insert user recommendations
    for recommendation in recommendations:
        session.execute(text("""
            INSERT INTO user_recommendations (user_id, recommendation_type, recommendation_data, priority_score, category, actionable_items, timestamp, is_implemented, implementation_date)
            VALUES (:user_id, :recommendation_type, :recommendation_data, :priority_score, :category, :actionable_items, :timestamp, :is_implemented, :implementation_date)
        """), recommendation)
    
    print(f"        ✅ Created {len(recommendations)} user recommendations")

def seed_role_hierarchy(session):
    """Seed role hierarchy"""
    print("      🔄 Seeding role hierarchy...")
    
    # Check if already has data
    result = session.execute(text("SELECT COUNT(*) FROM role_hierarchy"))
    if result.scalar() > 0:
        print("        ✅ role_hierarchy already has data")
        return
    
    # Get some roles
    roles = session.execute(text("SELECT id FROM access_control_roles")).fetchall()
    if not roles:
        print("        ⚠️ No roles found, skipping role_hierarchy")
        return
    
    hierarchy = []
    for i, (role_id,) in enumerate(roles):
        if i > 0:  # Skip first role
            hierarchy.append({
                'parent_role_id': roles[i-1][0],
                'child_role_id': role_id,
                'hierarchy_metadata': '{"level": ' + str(i) + ', "inheritance": true}',
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'last_accessed_at': None,
                'archived_at': None,
                'deleted_at': None,
                'scheduled_deletion_at': None,
                'retention_period': 365,
                'status': 'ACTIVE',
                'is_active': True,
                'metadata': '{"type": "hierarchy", "auto_created": true}'
            })
    
    # Insert role hierarchy
    for h in hierarchy:
        session.execute(text("""
            INSERT INTO role_hierarchy (parent_role_id, child_role_id, hierarchy_metadata, created_at, updated_at, last_accessed_at, archived_at, deleted_at, scheduled_deletion_at, retention_period, status, is_active, metadata)
            VALUES (:parent_role_id, :child_role_id, :hierarchy_metadata, :created_at, :updated_at, :last_accessed_at, :archived_at, :deleted_at, :scheduled_deletion_at, :retention_period, :status, :is_active, :metadata)
        """), h)
    
    print(f"        ✅ Created {len(hierarchy)} role hierarchy entries")

def seed_role_templates(session):
    """Seed role templates"""
    print("      🔄 Seeding role templates...")
    
    # Check if already has data
    result = session.execute(text("SELECT COUNT(*) FROM role_templates"))
    if result.scalar() > 0:
        print("        ✅ role_templates already has data")
        return
    
    templates = [
        {'name': 'Teacher Template', 'description': 'Template for teacher roles', 'is_system': False, 'status': 'ACTIVE', 'is_active': True, 'metadata': '{"type": "teacher", "permissions": ["read", "write"]}'},
        {'name': 'Student Template', 'description': 'Template for student roles', 'is_system': False, 'status': 'ACTIVE', 'is_active': True, 'metadata': '{"type": "student", "permissions": ["read"]}'},
        {'name': 'Admin Template', 'description': 'Template for admin roles', 'is_system': True, 'status': 'ACTIVE', 'is_active': True, 'metadata': '{"type": "admin", "permissions": ["read", "write", "delete"]}'}
    ]
    
    # Insert role templates
    for template in templates:
        session.execute(text("""
            INSERT INTO role_templates (name, description, is_system, status, is_active, metadata)
            VALUES (:name, :description, :is_system, :status, :is_active, :metadata)
        """), template)
    
    print(f"        ✅ Created {len(templates)} role templates")

def seed_security_preferences(session):
    """Seed security preferences"""
    print("      🔄 Seeding security preferences...")
    
    # Check if already has data
    result = session.execute(text("SELECT COUNT(*) FROM security_preferences"))
    if result.scalar() > 0:
        print("        ✅ security_preferences already has data")
        return
    
    # Get some users
    users = session.execute(text("SELECT id FROM users")).fetchall()
    if not users:
        print("        ⚠️ No users found, skipping security_preferences")
        return
    
    preferences = []
    for user_id, in users:
        preferences.append({
            'user_id': user_id,
            'theme': 'light',
            'accent_color': 'blue',
            'font_size': 'medium',
            'font_family': 'Arial',
            'dashboard_layout': '{"sidebar": "left", "widgets": ["activity", "progress"]}',
            'sidebar_position': 'left',
            'sidebar_collapsed': False,
            'grid_view': True,
            'email_notifications': True,
            'push_notifications': True,
            'in_app_notifications': True,
            'notification_sound': True,
            'notification_types': '["email", "push", "in_app"]',
            'quiet_hours': '{"start": "22:00", "end": "08:00"}',
            'language': 'en-US',
            'timezone': 'UTC',
            'date_format': 'MM/DD/YYYY',
            'time_format': '12h',
            'data_sharing': False,
            'analytics_opt_in': True,
            'personalized_ads': False,
            'high_contrast': False,
            'reduced_motion': False,
            'screen_reader': False,
            'keyboard_shortcuts': '{"save": "Ctrl+S", "new": "Ctrl+N"}',
            'cache_enabled': True,
            'cache_duration': 3600,
            'auto_refresh': True,
            'refresh_interval': 300,
            'connected_services': '["google", "microsoft"]',
            'webhook_urls': '[]',
            'api_keys': '{}',
            'auto_backup': True,
            'backup_frequency': 'daily',
            'backup_location': 'cloud',
            'custom_settings': '{}',
            'status': 'ACTIVE',
            'is_active': True
        })
    
    # Insert security preferences
    for preference in preferences:
        session.execute(text("""
            INSERT INTO security_preferences (user_id, theme, accent_color, font_size, font_family, dashboard_layout, sidebar_position, sidebar_collapsed, grid_view, email_notifications, push_notifications, in_app_notifications, notification_sound, notification_types, quiet_hours, language, timezone, date_format, time_format, data_sharing, analytics_opt_in, personalized_ads, high_contrast, reduced_motion, screen_reader, keyboard_shortcuts, cache_enabled, cache_duration, auto_refresh, refresh_interval, connected_services, webhook_urls, api_keys, auto_backup, backup_frequency, backup_location, custom_settings, status, is_active)
            VALUES (:user_id, :theme, :accent_color, :font_size, :font_family, :dashboard_layout, :sidebar_position, :sidebar_collapsed, :grid_view, :email_notifications, :push_notifications, :in_app_notifications, :notification_sound, :notification_types, :quiet_hours, :language, :timezone, :date_format, :time_format, :data_sharing, :analytics_opt_in, :personalized_ads, :high_contrast, :reduced_motion, :screen_reader, :keyboard_shortcuts, :cache_enabled, :cache_duration, :auto_refresh, :refresh_interval, :connected_services, :webhook_urls, :api_keys, :auto_backup, :backup_frequency, :backup_location, :custom_settings, :status, :is_active)
        """), preference)
    
    print(f"        ✅ Created {len(preferences)} security preferences")

def seed_sessions(session):
    """Seed sessions"""
    print("      🔄 Seeding sessions...")
    
    # Check if already has data
    result = session.execute(text("SELECT COUNT(*) FROM sessions"))
    if result.scalar() > 0:
        print("        ✅ sessions already has data")
        return
    
    # Get some users
    users = session.execute(text("SELECT id FROM users")).fetchall()
    if not users:
        print("        ⚠️ No users found, skipping sessions")
        return
    
    sessions_data = []
    for user_id, in users:
        sessions_data.append({
            'user_id': user_id,
            'device_info': '{"device": "web", "browser": "chrome"}',
            'ip_address': f'192.168.1.{user_id}',
            'started_at': datetime.utcnow(),
            'ended_at': None,
            'termination_reason': None
        })
    
    # Insert sessions
    for sess in sessions_data:
        session.execute(text("""
            INSERT INTO sessions (user_id, device_info, ip_address, started_at, ended_at, termination_reason)
            VALUES (:user_id, :device_info, :ip_address, :started_at, :ended_at, :termination_reason)
        """), sess)
    
    print(f"        ✅ Created {len(sessions_data)} sessions")

def seed_shared_contexts(session):
    """Seed shared contexts"""
    print("      🔄 Seeding shared contexts...")
    
    # Check if already has data
    result = session.execute(text("SELECT COUNT(*) FROM shared_contexts"))
    if result.scalar() > 0:
        print("        ✅ shared_contexts already has data")
        return
    
    # Get some users
    users = session.execute(text("SELECT id FROM users")).fetchall()
    if not users:
        print("        ⚠️ No users found, skipping shared_contexts")
        return
    
    # Get existing context IDs or create default ones
    contexts_data = session.execute(text("SELECT id FROM gpt_interaction_contexts LIMIT 5")).fetchall()
    if not contexts_data:
        # Get existing GPT IDs or create default ones
        gpt_ids = session.execute(text("SELECT id FROM gpt_definitions LIMIT 5")).fetchall()
        if not gpt_ids:
            # Create default GPT definition if none exist
            result = session.execute(text("""
                INSERT INTO gpt_definitions (name, model_type, version, description, max_tokens, temperature, top_p, frequency_penalty, presence_penalty, context_window, created_at, updated_at)
                VALUES (:name, :model_type, :version, :description, :max_tokens, :temperature, :top_p, :frequency_penalty, :presence_penalty, :context_window, :now, :now)
                RETURNING id
            """), {
                "name": "Default GPT",
                "model_type": "gpt-3.5-turbo",
                "version": "1.0",
                "description": "Default GPT for contexts",
                "max_tokens": 4096,
                "temperature": 0.7,
                "top_p": 1.0,
                "frequency_penalty": 0.0,
                "presence_penalty": 0.0,
                "context_window": 4096,
                "now": datetime.utcnow()
            })
            gpt_id = result.scalar()
            gpt_ids = [(gpt_id,)]
        
        # Create default contexts if none exist
        for user_id, in users:
            gpt_id = gpt_ids[0][0]  # Use the first available GPT ID
            result = session.execute(text("""
                INSERT INTO gpt_interaction_contexts (name, description, context_type, user_id, primary_gpt_id, status, created_at, updated_at)
                VALUES (:name, :description, :context_type, :user_id, :primary_gpt_id, :status, :now, :now)
                RETURNING id
            """), {
                "name": f"Context for User {user_id}",
                "description": f"Default context for user {user_id}",
                "context_type": "CONVERSATION",
                "user_id": user_id,
                "primary_gpt_id": gpt_id,
                "status": "ACTIVE",
                "now": datetime.utcnow()
            })
            context_id = result.scalar()
            contexts_data.append((context_id,))
    
    contexts = []
    for i, (user_id,) in enumerate(users):
        context_id = contexts_data[i % len(contexts_data)][0]  # Use available context IDs
        contexts.append({
            'context_id': context_id,
            'sharing_type': 'USER',
            'sharing_permissions': '{"read": true, "write": false}',
            'sharing_scope': 'PRIVATE',
            'access_count': 0,
            'last_accessed': None,
            'expires_at': None,
            'owner_id': user_id,
            'shared_with_user_id': None,
            'shared_with_project_id': None,
            'shared_with_organization_id': None,
            'status': 'ACTIVE',
            'is_active': True,
            'metadata': '{"created_by": "system"}'
        })
    
    # Insert shared contexts
    for context in contexts:
        session.execute(text("""
            INSERT INTO shared_contexts (context_id, sharing_type, sharing_permissions, sharing_scope, access_count, last_accessed, expires_at, owner_id, shared_with_user_id, shared_with_project_id, shared_with_organization_id, status, is_active, metadata)
            VALUES (:context_id, :sharing_type, :sharing_permissions, :sharing_scope, :access_count, :last_accessed, :expires_at, :owner_id, :shared_with_user_id, :shared_with_project_id, :shared_with_organization_id, :status, :is_active, :metadata)
        """), context)
    
    print(f"        ✅ Created {len(contexts)} shared contexts")

def seed_tool_assignments(session):
    """Seed tool assignments"""
    print("      🔄 Seeding tool assignments...")
    
    # Check if already has data
    result = session.execute(text("SELECT COUNT(*) FROM tool_assignments"))
    if result.scalar() > 0:
        print("        ✅ tool_assignments already has data")
        return
    
    # Get some users and tools
    users = session.execute(text("SELECT id FROM dashboard_users LIMIT 10")).fetchall()
    tools = session.execute(text("SELECT id FROM ai_tools LIMIT 3")).fetchall()
    
    if not users or not tools:
        print("        ⚠️ No users or tools found, skipping tool_assignments")
        return
    
    assignments = []
    for user_id, in users:
        for tool_id, in tools:
            # Randomly select who assigned this tool
            assigned_by = random.choice(users)[0]
            assignments.append({
                'tool_id': tool_id,
                'user_id': user_id,
                'assigned_by': assigned_by,
                'assigned_at': datetime.utcnow() - timedelta(days=random.randint(1, 30)),
                'expires_at': datetime.utcnow() + timedelta(days=random.randint(30, 365)) if random.random() > 0.5 else None
            })
    
    # Insert tool assignments
    for assignment in assignments:
        session.execute(text("""
            INSERT INTO tool_assignments (tool_id, user_id, assigned_by, assigned_at, expires_at)
            VALUES (:tool_id, :user_id, :assigned_by, :assigned_at, :expires_at)
        """), assignment)
    
    print(f"        ✅ Created {len(assignments)} tool assignments")

def seed_voice_templates(session):
    """Seed voice templates"""
    print("      🔄 Seeding voice templates...")
    
    # Check if already has data
    result = session.execute(text("SELECT COUNT(*) FROM voice_templates"))
    if result.scalar() > 0:
        print("        ✅ voice_templates already has data")
        return
    
    templates = [
        {'name': 'Default Voice', 'description': 'Default voice template', 'voice_settings': '{"speed": 1.0, "pitch": 1.0, "volume": 0.8}', 'template_metadata': '{"version": "1.0", "category": "default"}', 'metadata': '{"created_by": "system"}'},
        {'name': 'Teacher Voice', 'description': 'Voice template for teachers', 'voice_settings': '{"speed": 0.9, "pitch": 1.1, "volume": 0.9}', 'template_metadata': '{"version": "1.0", "category": "professional"}', 'metadata': '{"created_by": "system"}'},
        {'name': 'Student Voice', 'description': 'Voice template for students', 'voice_settings': '{"speed": 1.1, "pitch": 0.9, "volume": 0.7}', 'template_metadata': '{"version": "1.0", "category": "student"}', 'metadata': '{"created_by": "system"}'}
    ]
    
    # Insert voice templates
    for template in templates:
        session.execute(text("""
            INSERT INTO voice_templates (name, description, voice_settings, template_metadata, metadata)
            VALUES (:name, :description, :voice_settings, :template_metadata, :metadata)
        """), template)
    
    print(f"        ✅ Created {len(templates)} voice templates")

def seed_voices(session):
    """Seed voices"""
    print("      🔄 Seeding voices...")
    
    # Check if already has data
    result = session.execute(text("SELECT COUNT(*) FROM voices"))
    if result.scalar() > 0:
        print("        ✅ voices already has data")
        return
    
    # Get some users and avatars
    users = session.execute(text("SELECT id FROM users")).fetchall()
    avatars = session.execute(text("SELECT id FROM avatars")).fetchall()
    
    if not users or not avatars:
        print("        ⚠️ No users or avatars found, skipping voices")
        return
    
    voices = []
    for user_id, in users:
        for avatar_id, in avatars:
            voices.append({
                'avatar_id': avatar_id,
                'user_id': user_id,
                'template_id': 1,  # Default template
                'voice_type': 'TTS',
                'voice_settings': '{"speed": 1.0, "pitch": 1.0, "volume": 0.8}',
                'voice_metadata': '{"provider": "system", "quality": "high"}',
                'metadata': '{"created_by": "system"}'
            })
    
    # Insert voices
    for voice in voices:
        session.execute(text("""
            INSERT INTO voices (avatar_id, user_id, template_id, voice_type, voice_settings, voice_metadata, metadata)
            VALUES (:avatar_id, :user_id, :template_id, :voice_type, :voice_settings, :voice_metadata, :metadata)
        """), voice)
    
    print(f"        ✅ Created {len(voices)} voices")

def seed_avatar_templates(session):
    """Seed avatar templates"""
    print("      🔄 Seeding avatar templates...")
    
    # Check if already has data
    result = session.execute(text("SELECT COUNT(*) FROM avatar_templates"))
    if result.scalar() > 0:
        print("        ✅ avatar_templates already has data")
        return
    
    templates = [
        {'name': 'Default Avatar', 'description': 'Default avatar template', 'template_data': '{"base": "human", "gender": "neutral"}', 'template_metadata': '{"version": "1.0", "category": "default"}', 'metadata': '{"created_by": "system"}'},
        {'name': 'Teacher Avatar', 'description': 'Avatar template for teachers', 'template_data': '{"base": "human", "gender": "neutral", "profession": "teacher"}', 'template_metadata': '{"version": "1.0", "category": "professional"}', 'metadata': '{"created_by": "system"}'},
        {'name': 'Student Avatar', 'description': 'Avatar template for students', 'template_data': '{"base": "human", "gender": "neutral", "age_group": "young"}', 'template_metadata': '{"version": "1.0", "category": "student"}', 'metadata': '{"created_by": "system"}'}
    ]
    
    # Insert avatar templates
    for template in templates:
        session.execute(text("""
            INSERT INTO avatar_templates (name, description, template_data, template_metadata, created_at, updated_at, metadata)
            VALUES (:name, :description, :template_data, :template_metadata, :created_at, :updated_at, :metadata)
        """), {
            **template,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        })
    
    print(f"        ✅ Created {len(templates)} avatar templates")

def seed_avatar_customizations(session):
    """Seed avatar customizations"""
    print("      🔄 Seeding avatar customizations...")
    
    # Check if already has data
    result = session.execute(text("SELECT COUNT(*) FROM avatar_customizations"))
    if result.scalar() > 0:
        print("        ✅ avatar_customizations already has data")
        return
    
    # Get some users and avatars
    users = session.execute(text("SELECT id FROM users")).fetchall()
    avatars = session.execute(text("SELECT id FROM avatars")).fetchall()
    
    if not users or not avatars:
        print("        ⚠️ No users or avatars found, skipping avatar_customizations")
        return
    
    customizations = []
    for user_id, in users:
        for avatar_id, in avatars:
            customizations.append({
                'avatar_id': avatar_id,
                'user_id': user_id,
                'scale': 100,
                'position': '{"x": 0, "y": 0, "z": 0}',
                'rotation': '{"x": 0, "y": 0, "z": 0}',
                'color': 'blue',
                'opacity': 100,
                'type': 'APPEARANCE',
                'config': '{"customized": true}',
                'is_active': True
            })
    
    # Insert avatar customizations
    for customization in customizations:
        session.execute(text("""
            INSERT INTO avatar_customizations (avatar_id, user_id, scale, position, rotation, color, opacity, type, config, is_active, created_at, updated_at)
            VALUES (:avatar_id, :user_id, :scale, :position, :rotation, :color, :opacity, :type, :config, :is_active, :created_at, :updated_at)
        """), {
            **customization,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        })
    
    print(f"        ✅ Created {len(customizations)} avatar customizations")

def seed_user_avatars(session):
    """Seed user avatars"""
    print("      🔄 Seeding user avatars...")
    
    # Check if already has data
    result = session.execute(text("SELECT COUNT(*) FROM user_avatars"))
    if result.scalar() > 0:
        print("        ✅ user_avatars already has data")
        return
    
    # Get some users
    users = session.execute(text("SELECT id FROM users")).fetchall()
    if not users:
        print("        ⚠️ No users found, skipping user_avatars")
        return
    
    # Get avatar templates
    templates = session.execute(text("SELECT id FROM avatar_templates")).fetchall()
    if not templates:
        print("        ⚠️ No avatar templates found, skipping user_avatars")
        return
    
    avatars = []
    for user_id, in users:
        template_id = templates[user_id % len(templates)][0]  # Cycle through templates
        avatars.append({
            'user_id': user_id,
            'template_id': template_id,
            'avatar_type': 'STATIC',
            'style': 'REALISTIC',
            'avatar_data': '{"color": "blue", "accessories": "glasses"}',
            'is_active': True,
            'metadata': '{"created_by": "system"}'
        })
    
    # Insert user avatars
    for avatar in avatars:
        session.execute(text("""
            INSERT INTO user_avatars (user_id, template_id, avatar_type, style, avatar_data, is_active, created_at, updated_at, metadata)
            VALUES (:user_id, :template_id, :avatar_type, :style, :avatar_data, :is_active, :created_at, :updated_at, :metadata)
        """), {
            **avatar,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        })
    
    print(f"        ✅ Created {len(avatars)} user avatars")

def seed_user_avatar_customizations(session):
    """Seed user avatar customizations"""
    print("      🔄 Seeding user avatar customizations...")
    
    # Check if already has data
    result = session.execute(text("SELECT COUNT(*) FROM user_avatar_customizations"))
    if result.scalar() > 0:
        print("        ✅ user_avatar_customizations already has data")
        return
    
    # Get some users
    users = session.execute(text("SELECT id FROM users")).fetchall()
    if not users:
        print("        ⚠️ No users found, skipping user_avatar_customizations")
        return
    
    # Get user avatars
    user_avatars = session.execute(text("SELECT id FROM user_avatars")).fetchall()
    if not user_avatars:
        print("        ⚠️ No user avatars found, skipping user_avatar_customizations")
        return
    
    customizations = []
    for avatar_id, in user_avatars:
        customizations.append({
            'avatar_id': avatar_id,
            'customization_type': 'COLOR',
            'customization_value': '{"color": "blue", "shade": "medium"}',
            'customization_metadata': '{"applied_by": "user", "version": "1.0"}',
            'metadata': '{"created_by": "system"}'
        })
    
    # Insert user avatar customizations
    for customization in customizations:
        session.execute(text("""
            INSERT INTO user_avatar_customizations (avatar_id, customization_type, customization_value, customization_metadata, created_at, updated_at, metadata)
            VALUES (:avatar_id, :customization_type, :customization_value, :customization_metadata, :created_at, :updated_at, :metadata)
        """), {
            **customization,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        })
    
    print(f"        ✅ Created {len(customizations)} user avatar customizations")

def seed_student_avatar_customizations(session):
    """Seed student avatar customizations"""
    print("      🔄 Seeding student avatar customizations...")
    
    # Check if already has data
    result = session.execute(text("SELECT COUNT(*) FROM student_avatar_customizations"))
    if result.scalar() > 0:
        print("        ✅ student_avatar_customizations already has data")
        return
    
    # Get some users and avatars (using users as students)
    users = session.execute(text("SELECT id FROM users")).fetchall()
    avatars = session.execute(text("SELECT id FROM avatars")).fetchall()
    
    if not users or not avatars:
        print("        ⚠️ No users or avatars found, skipping student_avatar_customizations")
        return
    
    customizations = []
    for user_id, in users:
        for avatar_id, in avatars:
            customizations.append({
                'avatar_id': avatar_id,
                'user_id': user_id,
                'customization_type': 'COLOR',
                'customization_value': 'blue'
            })
    
    # Insert student avatar customizations
    for customization in customizations:
        session.execute(text("""
            INSERT INTO student_avatar_customizations (avatar_id, user_id, customization_type, customization_value, created_at, updated_at)
            VALUES (:avatar_id, :user_id, :customization_type, :customization_value, :created_at, :updated_at)
        """), {
            **customization,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        })
    
    print(f"        ✅ Created {len(customizations)} student avatar customizations")

def seed_security_logs(session):
    """Seed security logs"""
    print("      🔄 Seeding security logs...")
    
    # Check if already has data
    result = session.execute(text("SELECT COUNT(*) FROM security_logs"))
    if result.scalar() > 0:
        print("        ✅ security_logs already has data")
        return
    
    # Get some users
    users = session.execute(text("SELECT id FROM users")).fetchall()
    if not users:
        print("        ⚠️ No users found, skipping security_logs")
        return
    
    logs = []
    for user_id, in users:
        logs.append({
            'event_type': 'LOGIN',
            'severity': 'INFO',
            'source_ip': f'192.168.1.{user_id}',
            'user_id': user_id,
            'description': 'User login event',
            'security_metadata': '{"browser": "Chrome", "os": "Windows"}',
            'created_at': datetime.utcnow()
        })
    
    # Insert security logs
    for log in logs:
        session.execute(text("""
            INSERT INTO security_logs (event_type, severity, source_ip, user_id, description, security_metadata, created_at)
            VALUES (:event_type, :severity, :source_ip, :user_id, :description, :security_metadata, :created_at)
        """), log)
    
    print(f"        ✅ Created {len(logs)} security logs")

def seed_user_role_assignments(session):
    """Seed user-role assignments in access control system"""
    print("      🔄 Seeding user-role assignments...")
    
    # Check if already has data
    result = session.execute(text("SELECT COUNT(*) FROM access_control_user_roles"))
    if result.scalar() > 0:
        print("        ✅ access_control_user_roles already has data")
        return
    
    # Get users and their dashboard roles
    result = session.execute(text("SELECT id, role FROM dashboard_users"))
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
    try:
        seed_notifications_system(session)
    except Exception as e:
        print(f"    ⚠️  Notifications system seeding failed: {e}")
        # Continue with next phase
    
    # Phase 1.3.2: Logging System
    print("  📋 Phase 1.3.2: Logging System")
    try:
        seed_logging_system(session)
    except Exception as e:
        print(f"    ⚠️  Logging system seeding failed: {e}")
        # Continue with next phase
    
    # Phase 1.3.3: Monitoring & Audit
    print("  📋 Phase 1.3.3: Monitoring & Audit")
    try:
        seed_monitoring_system(session)
    except Exception as e:
        print(f"    ⚠️  Monitoring system seeding failed: {e}")
        # Continue with next phase
    
    # Phase 1.3.4: System Utilities
    print("  📋 Phase 1.3.4: System Utilities")
    try:
        seed_system_utilities(session)
    except Exception as e:
        print(f"    ⚠️  System utilities seeding failed: {e}")
        # Continue with next phase
    
    print("✅ Basic infrastructure seeding complete!")

def seed_notifications_system(session):
    """Seed notifications system tables"""
    print("    🔄 Seeding notifications system...")
    
    # Check if dashboard_notification_channels table exists and seed it
    try:
        result = session.execute(text("SELECT COUNT(*) FROM dashboard_notification_channels"))
        if result.scalar() > 0:
            print("      ✅ dashboard_notification_channels already has data")
            return
        
        # Create some notification models first
        print("      🔄 Creating notification models...")
        notification_models = []
        for i in range(10):  # Create 10 notification models
            notification_models.append({
                'user_id': random.randint(1, 10),  # Required user_id
                'type': random.choice(['SYSTEM', 'ALERT', 'UPDATE', 'REMINDER', 'ACHIEVEMENT']),
                'title': f'Notification Model {i+1}',
                'message': f'This is notification model {i+1}',
                'data': json.dumps({'model_id': i+1, 'category': 'test'}),
                'priority': random.choice(['LOW', 'NORMAL', 'HIGH', 'URGENT']),
                'status': random.choice(['PENDING', 'SENT', 'DELIVERED', 'READ']),
                'created_at': datetime.now() - timedelta(days=random.randint(0, 30)),
                'read_at': datetime.now() - timedelta(days=random.randint(0, 15)) if random.random() > 0.5 else None,
                'expires_at': datetime.now() + timedelta(days=random.randint(1, 30)),
                'is_active': True,
                'metadata': json.dumps({'source': 'phase1_seeding', 'version': '1.0'})
            })
        
        # Insert notification models and get their IDs
        notification_ids = []
        for model in notification_models:
            result = session.execute(text("""
                INSERT INTO dashboard_notification_models (
                    user_id, type, title, message, data, priority, status, created_at, read_at, expires_at, is_active, metadata
                ) VALUES (
                    :user_id, :type, :title, :message, :data, :priority, :status, :created_at, :read_at, :expires_at, :is_active, :metadata
                ) RETURNING id
            """), model)
            notification_ids.append(result.scalar())
        
        print(f"      ✅ Created {len(notification_models)} notification models with IDs: {notification_ids}")
        
        # Get user IDs for notifications
        result = session.execute(text("SELECT id FROM dashboard_users"))
        user_ids = [row[0] for row in result.fetchall()]
        
        if not user_ids:
            print("      ⚠️  No users found for notifications")
            return
        
        # Create sample notification channels
        channels = ['EMAIL', 'PUSH', 'SMS', 'WEBSOCKET', 'IN_APP']
        statuses = ['PENDING', 'SENT', 'FAILED', 'DELIVERED']
        notification_data = []
        
        for user_id in user_ids:
            # Create multiple notification channels per user
            for i in range(random.randint(1, 2)):
                notification_data.append({
                    'notification_id': random.choice(notification_ids),  # Use actual IDs from models we just created
                    'channel': random.choice(channels),
                    'status': random.choice(statuses),
                    'sent_at': datetime.now() - timedelta(days=random.randint(0, 30)) if random.random() > 0.3 else None,
                    'error': None if random.random() > 0.1 else 'Connection timeout',
                    'retry_count': random.randint(0, 3),
                    'last_retry': datetime.now() - timedelta(hours=random.randint(1, 24)) if random.random() > 0.5 else None,
                    'is_active': random.choice([True, False]),
                    'metadata': json.dumps({
                        'user_id': user_id,
                        'priority': random.choice(['LOW', 'MEDIUM', 'HIGH']),
                        'template': f'template_{i+1}'
                    })
                })
        
        # Insert notifications
        for notif in notification_data:
            session.execute(text("""
                INSERT INTO dashboard_notification_channels (
                    notification_id, channel, status, sent_at, error, retry_count, last_retry, is_active, metadata
                ) VALUES (
                    :notification_id, :channel, :status, :sent_at, :error, :retry_count, :last_retry, :is_active, :metadata
                )
            """), notif)
        
        print(f"      ✅ Created {len(notification_data)} notification channels")
        
    except Exception as e:
        print(f"      ⚠️  Notifications table not available: {e}")

def seed_logging_system(session):
    """Seed logging system tables"""
    print("    🔄 Seeding logging system...")
    
    # Check if activity_logs table exists and seed it
    try:
        result = session.execute(text("SELECT COUNT(*) FROM activity_logs"))
        if result.scalar() > 0:
            print("      ✅ activity_logs already has data")
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
                INSERT INTO activity_logs (
                    level, category, message, details, timestamp
                ) VALUES (
                    :level, :category, :message, :details, :timestamp
                )
            """), log)
        
        print(f"      ✅ Created {len(log_data)} activity logs")
        
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
                    'changes': random.choice([
                        {'field': 'status', 'old_value': 'INACTIVE', 'new_value': 'ACTIVE'},
                        {'field': 'name', 'old_value': 'Old Name', 'new_value': 'New Name'},
                        {'field': 'permissions', 'old_value': 'READ', 'new_value': 'READ,WRITE'},
                        None
                    ])
                }),
                'ip_address': f"192.168.1.{random.randint(1, 255)}",
                'user_agent': 'FaradayAI/1.0',
                'created_at': datetime.utcnow() - timedelta(days=random.randint(0, 30)),
                'updated_at': datetime.utcnow() - timedelta(days=random.randint(0, 15))
            })
        
        # Insert audit logs
        for audit in audit_data:
            session.execute(text("""
                INSERT INTO audit_logs (
                    user_id, action, resource_type, resource_id, details, ip_address, user_agent, created_at, updated_at
                ) VALUES (
                    :user_id, :action, :resource_type, :resource_id, :details, :ip_address, :user_agent, :created_at, :updated_at
                )
            """), audit)
        
        print(f"      ✅ Created {len(audit_data)} audit logs")
        
    except Exception as e:
        print(f"      ⚠️  Audit logs table not available: {e}")

def seed_system_utilities(session):
    """Seed other system utility tables"""
    print("    🔄 Seeding system utilities...")
    
    # Check if organization_settings table exists and seed it
    try:
        result = session.execute(text("SELECT COUNT(*) FROM organization_settings"))
        if result.scalar() > 0:
            print("      ✅ organization_settings already has data")
        else:
            # Get organization_id
            result = session.execute(text("SELECT id FROM organizations LIMIT 1"))
            org_id = result.scalar()
            if not org_id:
                print("      ⚠️  No organizations found, skipping organization settings")
                return
            
            # Create sample organization settings
            settings_data = [
                {
                    'organization_id': org_id,
                    'theme': 'modern',
                    'language': 'en',
                    'timezone': 'America/New_York',
                    'features': json.dumps(['ai_assistant', 'analytics', 'collaboration']),
                    'enabled_modules': json.dumps(['lessons', 'assessments', 'reports']),
                    'experimental_features': json.dumps(['ai_grading', 'voice_commands']),
                    'notification_preferences': json.dumps({'email': True, 'push': True, 'sms': False}),
                    'email_settings': json.dumps({'smtp_host': 'smtp.example.com', 'from_email': 'noreply@example.com'}),
                    'security_policies': json.dumps({'password_min_length': 8, 'session_timeout': 3600}),
                    'status': 'ACTIVE',
                    'is_active': True,
                    'created_at': datetime.utcnow(),
                    'updated_at': datetime.utcnow()
                }
            ]
            
            # Insert organization settings
            for setting in settings_data:
                session.execute(text("""
                    INSERT INTO organization_settings (
                        organization_id, theme, language, timezone, features, enabled_modules, experimental_features, notification_preferences, email_settings, security_policies, status, is_active, created_at, updated_at
                    ) VALUES (
                        :organization_id, :theme, :language, :timezone, :features, :enabled_modules, :experimental_features, :notification_preferences, :email_settings, :security_policies, :status, :is_active, :created_at, :updated_at
                    )
                """), setting)
            
            print(f"      ✅ Created {len(settings_data)} organization settings")
        
    except Exception as e:
        print(f"      ⚠️  Organization settings table not available: {e}")
    
    # Feature flags are handled via organization_settings.features JSON column
    print("      ✅ Feature flags handled via organization_settings.features")
    
    # Check if project_settings table exists and seed it
    try:
        result = session.execute(text("SELECT COUNT(*) FROM project_settings"))
        if result.scalar() > 0:
            print("      ✅ project_settings already has data")
        else:
            # Get a project_id from organization_projects
            result = session.execute(text("SELECT id FROM organization_projects LIMIT 1"))
            project_id = result.scalar()
            if not project_id:
                # Create a sample project if none exists
                session.execute(text("""
                    INSERT INTO organization_projects (name, description, status, created_at, updated_at)
                    VALUES ('Sample Project', 'A sample project for testing', 'ACTIVE', :now, :now)
                    RETURNING id
                """), {"now": datetime.utcnow()})
                result = session.execute(text("SELECT id FROM organization_projects ORDER BY id DESC LIMIT 1"))
                project_id = result.scalar()
            
            # Create sample project settings
            project_setting = {
                'project_id': project_id,
                'theme': 'modern',
                'language': 'en',
                'timezone': 'America/New_York',
                'features': json.dumps(['analytics', 'collaboration', 'reporting']),
                'enabled_modules': json.dumps(['dashboard', 'reports', 'settings']),
                'experimental_features': json.dumps(['ai_insights', 'advanced_charts']),
                'notification_preferences': json.dumps({'email': True, 'push': False, 'sms': False}),
                'email_settings': json.dumps({'smtp_host': 'smtp.project.com', 'from_email': 'noreply@project.com'}),
                'security_policies': json.dumps({'password_min_length': 8, 'session_timeout': 7200}),
                'status': 'ACTIVE',
                'is_active': True,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            # Insert project settings
            session.execute(text("""
                INSERT INTO project_settings (
                    project_id, theme, language, timezone, features, enabled_modules, experimental_features, 
                    notification_preferences, email_settings, security_policies, status, is_active, created_at, updated_at
                ) VALUES (
                    :project_id, :theme, :language, :timezone, :features, :enabled_modules, :experimental_features,
                    :notification_preferences, :email_settings, :security_policies, :status, :is_active, :created_at, :updated_at
                )
            """), project_setting)
            
            print("      ✅ Created 1 project settings")
        
    except Exception as e:
        print(f"      ⚠️  Project settings table not available: {e}")

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
            result = session.execute(text("SELECT id, role FROM dashboard_users"))
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