#!/usr/bin/env python3
"""
Seed all empty tables with mock data for development
This ensures comprehensive testing coverage
"""

import sys
import os
import random
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from app.core.database import SessionLocal
from sqlalchemy import text

def seed_empty_tables():
    """Seed all empty tables with mock data for development"""
    session = SessionLocal()
    try:
        print("🌱 SEEDING EMPTY TABLES FOR DEVELOPMENT")
        print("=" * 50)
        
        # Get all empty tables
        result = session.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """))
        all_tables = [row[0] for row in result.fetchall()]
        
        empty_tables = []
        for table in all_tables:
            try:
                count_result = session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = count_result.fetchone()[0]
                if count == 0:
                    empty_tables.append(table)
            except Exception as e:
                print(f"⚠️  Error checking {table}: {e}")
        
        print(f"📊 Found {len(empty_tables)} empty tables to seed")
        
        # Get dependency IDs
        user_ids = get_ids(session, "users", 50)
        student_ids = get_ids(session, "students", 100)
        teacher_ids = get_ids(session, "teachers", 20)
        activity_ids = get_ids(session, "activities", 50)
        lesson_plan_ids = get_ids(session, "pe_lesson_plans", 20)
        assessment_ids = get_ids(session, "skill_assessment_assessments", 20)
        organization_ids = get_ids(session, "organizations", 10)
        dashboard_user_ids = get_ids(session, "dashboard_users", 20)
        
        # Seed each empty table
        seeded_count = 0
        for table in empty_tables:
            try:
                count = seed_table(session, table, user_ids, student_ids, teacher_ids, 
                                 activity_ids, lesson_plan_ids, assessment_ids, 
                                 organization_ids, dashboard_user_ids)
                if count > 0:
                    print(f"  ✅ {table}: {count} records")
                    seeded_count += 1
                else:
                    print(f"  ⚠️  {table}: skipped (no suitable data)")
            except Exception as e:
                print(f"  ❌ {table}: {e}")
        
        session.commit()
        print(f"\n🎉 Seeded {seeded_count} empty tables successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        session.rollback()
        import traceback
        traceback.print_exc()
    finally:
        session.close()

def get_ids(session, table, limit):
    """Get IDs from a table"""
    try:
        result = session.execute(text(f"SELECT id FROM {table} LIMIT {limit}"))
        return [row[0] for row in result.fetchall()]
    except:
        return []

def seed_table(session, table_name, user_ids, student_ids, teacher_ids, 
               activity_ids, lesson_plan_ids, assessment_ids, organization_ids, dashboard_user_ids):
    """Seed a specific table with mock data"""
    
    if not user_ids and not student_ids and not teacher_ids:
        return 0
    
    # Define seeding strategies for each table
    strategies = {
        # AI Assistant Tables
        'ai_assistant_analytics': lambda: seed_ai_assistant_analytics(session, user_ids),
        'ai_assistant_conversations': lambda: seed_ai_assistant_conversations(session, user_ids),
        'ai_assistant_feedback': lambda: seed_ai_assistant_feedback(session, user_ids),
        'ai_assistant_messages': lambda: seed_ai_assistant_messages(session, user_ids),
        'ai_assistant_usage': lambda: seed_ai_assistant_usage(session, user_ids),
        'ai_lesson_suggestions': lambda: seed_ai_lesson_suggestions(session, lesson_plan_ids),
        
        # Assessment Tables
        'assessment_checklists': lambda: seed_assessment_checklists(session, assessment_ids),
        'assessment_criteria': lambda: seed_assessment_criteria(session, assessment_ids),
        'assessment_questions': lambda: seed_assessment_questions(session, assessment_ids),
        'assessment_rubrics': lambda: seed_assessment_rubrics(session, assessment_ids),
        'assessment_standards': lambda: seed_assessment_standards(session),
        'assessment_template_category_associations': lambda: seed_template_associations(session),
        'assessment_template_sharing': lambda: seed_template_sharing(session, user_ids),
        'assessment_template_usage': lambda: seed_template_usage(session, user_ids),
        
        # Beta Testing Tables
        'beta_lesson_plan_activities': lambda: seed_beta_lesson_activities(session, lesson_plan_ids),
        'beta_testing_feature_flags': lambda: seed_feature_flags(session),
        'beta_testing_feedback': lambda: seed_beta_feedback(session, user_ids),
        'beta_testing_notifications': lambda: seed_beta_notifications(session, user_ids),
        'beta_testing_participants': lambda: seed_beta_participants(session, user_ids),
        'beta_testing_reports': lambda: seed_beta_reports(session, user_ids),
        'beta_testing_survey_responses': lambda: seed_survey_responses(session, user_ids),
        'beta_testing_surveys': lambda: seed_beta_surveys(session),
        'beta_testing_usage_analytics': lambda: seed_usage_analytics(session, user_ids),
        
        # Resource Management Tables
        'collection_resource_associations': lambda: seed_collection_associations(session),
        'collection_sharing': lambda: seed_collection_sharing(session, user_ids),
        'resource_category_associations': lambda: seed_resource_category_associations(session),
        'resource_collections': lambda: seed_resource_collections(session, user_ids),
        'resource_downloads': lambda: seed_resource_downloads(session, user_ids),
        'resource_favorites': lambda: seed_resource_favorites(session, user_ids),
        'resource_reviews': lambda: seed_resource_reviews(session, user_ids),
        'resource_sharing': lambda: seed_resource_sharing(session, user_ids),
        'resource_usage': lambda: seed_resource_usage(session, user_ids),
        
        # Curriculum Tables
        'curriculum_units': lambda: seed_curriculum_units(session),
        'drivers_ed_instructor_certifications': lambda: seed_drivers_ed_certifications(session, teacher_ids),
        'drivers_ed_lesson_activities': lambda: seed_drivers_ed_activities(session, lesson_plan_ids),
        'drivers_ed_safety_incidents': lambda: seed_safety_incidents(session, student_ids),
        'drivers_ed_student_progress': lambda: seed_drivers_ed_progress(session, student_ids),
        'health_incidents': lambda: seed_health_incidents(session, student_ids),
        'health_instructor_certifications': lambda: seed_health_certifications(session, teacher_ids),
        'health_lesson_activities': lambda: seed_health_activities(session, lesson_plan_ids),
        'health_student_progress': lambda: seed_health_progress(session, student_ids),
        
        # Communication Tables
        'filters': lambda: seed_filters(session, user_ids),
        'lesson_plan_sharing': lambda: seed_lesson_plan_sharing(session, user_ids, lesson_plan_ids),
        'lesson_plan_usage': lambda: seed_lesson_plan_usage(session, user_ids, lesson_plan_ids),
        'lesson_plans': lambda: seed_lesson_plans(session, teacher_ids),
        'template_category_associations': lambda: seed_template_category_associations(session),
        
        # System Tables
        'job': lambda: seed_jobs(session),
        'job_run_details': lambda: seed_job_details(session),
    }
    
    if table_name in strategies:
        return strategies[table_name]()
    else:
        # Generic seeding for unknown tables
        return seed_generic_table(session, table_name, user_ids, student_ids)

def seed_ai_assistant_analytics(session, user_ids):
    """Seed AI assistant analytics"""
    if not user_ids:
        return 0
    
    data = []
    for i in range(50):
        data.append({
            'user_id': random.choice(user_ids),
            'assistant_id': random.randint(1, 5),
            'interaction_count': random.randint(1, 100),
            'success_rate': random.uniform(0.7, 0.95),
            'avg_response_time': random.uniform(0.5, 3.0),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    return insert_data(session, 'ai_assistant_analytics', data)

def seed_ai_assistant_conversations(session, user_ids):
    """Seed AI assistant conversations"""
    if not user_ids:
        return 0
    
    data = []
    for i in range(100):
        data.append({
            'user_id': random.choice(user_ids),
            'assistant_id': random.randint(1, 5),
            'conversation_id': f"conv_{i+1}_{random.randint(1000, 9999)}",
            'status': random.choice(['ACTIVE', 'COMPLETED', 'ARCHIVED']),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    return insert_data(session, 'ai_assistant_conversations', data)

def seed_ai_assistant_feedback(session, user_ids):
    """Seed AI assistant feedback"""
    if not user_ids:
        return 0
    
    data = []
    for i in range(75):
        data.append({
            'user_id': random.choice(user_ids),
            'assistant_id': random.randint(1, 5),
            'rating': random.randint(1, 5),
            'feedback_text': f"Feedback {i+1}: " + random.choice([
                "Great response!", "Very helpful", "Could be better", "Excellent service"
            ]),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    return insert_data(session, 'ai_assistant_feedback', data)

def seed_ai_assistant_messages(session, user_ids):
    """Seed AI assistant messages"""
    if not user_ids:
        return 0
    
    data = []
    for i in range(200):
        data.append({
            'user_id': random.choice(user_ids),
            'assistant_id': random.randint(1, 5),
            'conversation_id': f"conv_{random.randint(1, 50)}_{random.randint(1000, 9999)}",
            'message_type': random.choice(['USER', 'ASSISTANT']),
            'content': f"Message {i+1}: " + random.choice([
                "How can I help you?", "What would you like to know?", "Here's the information you requested"
            ]),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    return insert_data(session, 'ai_assistant_messages', data)

def seed_ai_assistant_usage(session, user_ids):
    """Seed AI assistant usage"""
    if not user_ids:
        return 0
    
    data = []
    for i in range(100):
        data.append({
            'user_id': random.choice(user_ids),
            'assistant_id': random.randint(1, 5),
            'usage_type': random.choice(['QUERY', 'ANALYSIS', 'RECOMMENDATION']),
            'duration_seconds': random.randint(5, 300),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    return insert_data(session, 'ai_assistant_usage', data)

def seed_ai_lesson_suggestions(session, lesson_plan_ids):
    """Seed AI lesson suggestions"""
    if not lesson_plan_ids:
        return 0
    
    data = []
    for i in range(50):
        data.append({
            'lesson_plan_id': random.choice(lesson_plan_ids),
            'suggestion_type': random.choice(['ACTIVITY', 'ASSESSMENT', 'RESOURCE']),
            'suggestion_text': f"AI Suggestion {i+1}: " + random.choice([
                "Consider adding a group activity", "Include a formative assessment", 
                "Add a visual resource", "Try a different approach"
            ]),
            'confidence_score': random.uniform(0.6, 0.95),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    return insert_data(session, 'ai_lesson_suggestions', data)

def seed_assessment_checklists(session, assessment_ids):
    """Seed assessment checklists"""
    if not assessment_ids:
        return 0
    
    data = []
    for i in range(100):
        data.append({
            'assessment_id': random.choice(assessment_ids),
            'checklist_item': f"Checklist Item {i+1}",
            'is_required': random.choice([True, False]),
            'order_index': i + 1,
            'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    return insert_data(session, 'assessment_checklists', data)

def seed_assessment_criteria(session, assessment_ids):
    """Seed assessment criteria"""
    if not assessment_ids:
        return 0
    
    data = []
    for i in range(150):
        data.append({
            'assessment_id': random.choice(assessment_ids),
            'criteria_name': f"Criteria {i+1}",
            'description': f"Description for criteria {i+1}",
            'max_score': random.randint(1, 10),
            'weight': random.uniform(0.1, 1.0),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    return insert_data(session, 'assessment_criteria', data)

def seed_assessment_questions(session, assessment_ids):
    """Seed assessment questions"""
    if not assessment_ids:
        return 0
    
    data = []
    for i in range(200):
        data.append({
            'assessment_id': random.choice(assessment_ids),
            'question_text': f"Question {i+1}: What is the main objective?",
            'question_type': random.choice(['MULTIPLE_CHOICE', 'SHORT_ANSWER', 'ESSAY']),
            'points': random.randint(1, 10),
            'order_index': i + 1,
            'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    return insert_data(session, 'assessment_questions', data)

def seed_assessment_rubrics(session, assessment_ids):
    """Seed assessment rubrics"""
    if not assessment_ids:
        return 0
    
    data = []
    for i in range(80):
        data.append({
            'assessment_id': random.choice(assessment_ids),
            'rubric_name': f"Rubric {i+1}",
            'description': f"Description for rubric {i+1}",
            'max_score': random.randint(10, 100),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    return insert_data(session, 'assessment_rubrics', data)

def seed_assessment_standards(session):
    """Seed assessment standards"""
    data = []
    standards = [
        "Common Core State Standards",
        "Next Generation Science Standards", 
        "National PE Standards",
        "State Curriculum Standards",
        "District Learning Objectives"
    ]
    
    for i, standard in enumerate(standards):
        data.append({
            'standard_name': standard,
            'description': f"Description for {standard}",
            'grade_level': random.choice(['K-2', '3-5', '6-8', '9-12']),
            'subject': random.choice(['PE', 'Health', 'Science', 'Math']),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    return insert_data(session, 'assessment_standards', data)

def seed_template_associations(session):
    """Seed template associations"""
    data = []
    for i in range(50):
        data.append({
            'template_id': random.randint(1, 10),
            'category_id': random.randint(1, 20),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    return insert_data(session, 'assessment_template_category_associations', data)

def seed_template_sharing(session, user_ids):
    """Seed template sharing"""
    if not user_ids:
        return 0
    
    data = []
    for i in range(75):
        data.append({
            'template_id': random.randint(1, 10),
            'shared_by_user_id': random.choice(user_ids),
            'shared_with_user_id': random.choice(user_ids),
            'permission_level': random.choice(['READ', 'WRITE', 'ADMIN']),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    return insert_data(session, 'assessment_template_sharing', data)

def seed_template_usage(session, user_ids):
    """Seed template usage"""
    if not user_ids:
        return 0
    
    data = []
    for i in range(100):
        data.append({
            'template_id': random.randint(1, 10),
            'user_id': random.choice(user_ids),
            'usage_type': random.choice(['VIEW', 'COPY', 'MODIFY']),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    return insert_data(session, 'assessment_template_usage', data)

def seed_beta_lesson_activities(session, lesson_plan_ids):
    """Seed beta lesson activities"""
    if not lesson_plan_ids:
        return 0
    
    data = []
    for i in range(100):
        data.append({
            'lesson_plan_id': random.choice(lesson_plan_ids),
            'activity_name': f"Beta Activity {i+1}",
            'description': f"Description for beta activity {i+1}",
            'duration_minutes': random.randint(10, 60),
            'order_index': i + 1,
            'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    return insert_data(session, 'beta_lesson_plan_activities', data)

def seed_feature_flags(session):
    """Seed feature flags"""
    data = []
    features = [
        "ai_lesson_planning", "advanced_analytics", "beta_testing", 
        "collaborative_planning", "real_time_feedback", "mobile_app"
    ]
    
    for i, feature in enumerate(features):
        data.append({
            'feature_name': feature,
            'is_enabled': random.choice([True, False]),
            'description': f"Feature flag for {feature}",
            'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    return insert_data(session, 'beta_testing_feature_flags', data)

def seed_beta_feedback(session, user_ids):
    """Seed beta feedback"""
    if not user_ids:
        return 0
    
    data = []
    for i in range(150):
        data.append({
            'user_id': random.choice(user_ids),
            'feature_name': random.choice(['ai_lesson_planning', 'advanced_analytics', 'beta_testing']),
            'feedback_text': f"Beta feedback {i+1}: " + random.choice([
                "Great feature!", "Needs improvement", "Very useful", "Could be better"
            ]),
            'rating': random.randint(1, 5),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    return insert_data(session, 'beta_testing_feedback', data)

def seed_beta_notifications(session, user_ids):
    """Seed beta notifications"""
    if not user_ids:
        return 0
    
    data = []
    for i in range(100):
        data.append({
            'user_id': random.choice(user_ids),
            'notification_type': random.choice(['FEATURE_UPDATE', 'BETA_INVITE', 'FEEDBACK_REQUEST']),
            'title': f"Beta Notification {i+1}",
            'message': f"Message for beta notification {i+1}",
            'is_read': random.choice([True, False]),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    return insert_data(session, 'beta_testing_notifications', data)

def seed_beta_participants(session, user_ids):
    """Seed beta participants"""
    if not user_ids:
        return 0
    
    data = []
    for i in range(50):
        data.append({
            'user_id': random.choice(user_ids),
            'program_id': random.randint(1, 5),
            'status': random.choice(['ACTIVE', 'COMPLETED', 'DROPPED']),
            'enrolled_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    return insert_data(session, 'beta_testing_participants', data)

def seed_beta_reports(session, user_ids):
    """Seed beta reports"""
    if not user_ids:
        return 0
    
    data = []
    for i in range(25):
        data.append({
            'user_id': random.choice(user_ids),
            'report_type': random.choice(['USAGE', 'PERFORMANCE', 'FEEDBACK']),
            'title': f"Beta Report {i+1}",
            'content': f"Content for beta report {i+1}",
            'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    return insert_data(session, 'beta_testing_reports', data)

def seed_survey_responses(session, user_ids):
    """Seed survey responses"""
    if not user_ids:
        return 0
    
    data = []
    for i in range(200):
        data.append({
            'user_id': random.choice(user_ids),
            'survey_id': random.randint(1, 10),
            'question_id': random.randint(1, 50),
            'response_text': f"Survey response {i+1}",
            'rating': random.randint(1, 5),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    return insert_data(session, 'beta_testing_survey_responses', data)

def seed_beta_surveys(session):
    """Seed beta surveys"""
    data = []
    for i in range(10):
        data.append({
            'survey_name': f"Beta Survey {i+1}",
            'description': f"Description for beta survey {i+1}",
            'is_active': random.choice([True, False]),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    return insert_data(session, 'beta_testing_surveys', data)

def seed_usage_analytics(session, user_ids):
    """Seed usage analytics"""
    if not user_ids:
        return 0
    
    data = []
    for i in range(300):
        data.append({
            'user_id': random.choice(user_ids),
            'feature_name': random.choice(['lesson_planning', 'assessments', 'resources', 'analytics']),
            'usage_count': random.randint(1, 100),
            'session_duration': random.randint(60, 3600),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    return insert_data(session, 'beta_testing_usage_analytics', data)

def seed_collection_associations(session):
    """Seed collection associations"""
    data = []
    for i in range(100):
        data.append({
            'collection_id': random.randint(1, 20),
            'resource_id': random.randint(1, 50),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    return insert_data(session, 'collection_resource_associations', data)

def seed_collection_sharing(session, user_ids):
    """Seed collection sharing"""
    if not user_ids:
        return 0
    
    data = []
    for i in range(50):
        data.append({
            'collection_id': random.randint(1, 20),
            'shared_by_user_id': random.choice(user_ids),
            'shared_with_user_id': random.choice(user_ids),
            'permission_level': random.choice(['READ', 'WRITE', 'ADMIN']),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    return insert_data(session, 'collection_sharing', data)

def seed_resource_category_associations(session):
    """Seed resource category associations"""
    data = []
    for i in range(100):
        data.append({
            'resource_id': random.randint(1, 50),
            'category_id': random.randint(1, 20),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    return insert_data(session, 'resource_category_associations', data)

def seed_resource_collections(session, user_ids):
    """Seed resource collections"""
    if not user_ids:
        return 0
    
    data = []
    for i in range(20):
        data.append({
            'name': f"Resource Collection {i+1}",
            'description': f"Description for collection {i+1}",
            'user_id': random.choice(user_ids),
            'is_public': random.choice([True, False]),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    return insert_data(session, 'resource_collections', data)

def seed_resource_downloads(session, user_ids):
    """Seed resource downloads"""
    if not user_ids:
        return 0
    
    data = []
    for i in range(200):
        data.append({
            'resource_id': random.randint(1, 50),
            'user_id': random.choice(user_ids),
            'download_count': random.randint(1, 10),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    return insert_data(session, 'resource_downloads', data)

def seed_resource_favorites(session, user_ids):
    """Seed resource favorites"""
    if not user_ids:
        return 0
    
    data = []
    for i in range(150):
        data.append({
            'resource_id': random.randint(1, 50),
            'user_id': random.choice(user_ids),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    return insert_data(session, 'resource_favorites', data)

def seed_resource_reviews(session, user_ids):
    """Seed resource reviews"""
    if not user_ids:
        return 0
    
    data = []
    for i in range(100):
        data.append({
            'resource_id': random.randint(1, 50),
            'user_id': random.choice(user_ids),
            'rating': random.randint(1, 5),
            'review_text': f"Review {i+1}: " + random.choice([
                "Great resource!", "Very helpful", "Could be better", "Excellent quality"
            ]),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    return insert_data(session, 'resource_reviews', data)

def seed_resource_sharing(session, user_ids):
    """Seed resource sharing"""
    if not user_ids:
        return 0
    
    data = []
    for i in range(75):
        data.append({
            'resource_id': random.randint(1, 50),
            'shared_by_user_id': random.choice(user_ids),
            'shared_with_user_id': random.choice(user_ids),
            'permission_level': random.choice(['READ', 'WRITE', 'ADMIN']),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    return insert_data(session, 'resource_sharing', data)

def seed_resource_usage(session, user_ids):
    """Seed resource usage"""
    if not user_ids:
        return 0
    
    data = []
    for i in range(200):
        data.append({
            'resource_id': random.randint(1, 50),
            'user_id': random.choice(user_ids),
            'usage_type': random.choice(['VIEW', 'DOWNLOAD', 'SHARE']),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    return insert_data(session, 'resource_usage', data)

def seed_curriculum_units(session):
    """Seed curriculum units"""
    data = []
    for i in range(30):
        data.append({
            'unit_name': f"Unit {i+1}",
            'description': f"Description for unit {i+1}",
            'grade_level': random.choice(['K-2', '3-5', '6-8', '9-12']),
            'subject': random.choice(['PE', 'Health', 'Science']),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    return insert_data(session, 'curriculum_units', data)

def seed_drivers_ed_certifications(session, teacher_ids):
    """Seed drivers ed certifications"""
    if not teacher_ids:
        return 0
    
    data = []
    for i in range(25):
        data.append({
            'teacher_id': random.choice(teacher_ids),
            'certification_type': random.choice(['CDL', 'INSTRUCTOR', 'SAFETY']),
            'certification_number': f"DE{i+1:04d}",
            'expiry_date': datetime.now() + timedelta(days=random.randint(30, 365)),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    return insert_data(session, 'drivers_ed_instructor_certifications', data)

def seed_drivers_ed_activities(session, lesson_plan_ids):
    """Seed drivers ed activities"""
    if not lesson_plan_ids:
        return 0
    
    data = []
    for i in range(50):
        data.append({
            'lesson_plan_id': random.choice(lesson_plan_ids),
            'activity_name': f"Drivers Ed Activity {i+1}",
            'description': f"Description for drivers ed activity {i+1}",
            'duration_minutes': random.randint(15, 90),
            'order_index': i + 1,
            'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    return insert_data(session, 'drivers_ed_lesson_activities', data)

def seed_safety_incidents(session, student_ids):
    """Seed safety incidents"""
    if not student_ids:
        return 0
    
    data = []
    for i in range(30):
        data.append({
            'student_id': random.choice(student_ids),
            'incident_type': random.choice(['MINOR', 'MODERATE', 'MAJOR']),
            'description': f"Safety incident {i+1}",
            'severity': random.randint(1, 5),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    return insert_data(session, 'drivers_ed_safety_incidents', data)

def seed_drivers_ed_progress(session, student_ids):
    """Seed drivers ed progress"""
    if not student_ids:
        return 0
    
    data = []
    for i in range(100):
        data.append({
            'student_id': random.choice(student_ids),
            'lesson_id': random.randint(1, 50),
            'completion_percentage': random.randint(0, 100),
            'status': random.choice(['IN_PROGRESS', 'COMPLETED', 'FAILED']),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    return insert_data(session, 'drivers_ed_student_progress', data)

def seed_health_incidents(session, student_ids):
    """Seed health incidents"""
    if not student_ids:
        return 0
    
    data = []
    for i in range(25):
        data.append({
            'student_id': random.choice(student_ids),
            'incident_type': random.choice(['INJURY', 'ILLNESS', 'EMERGENCY']),
            'description': f"Health incident {i+1}",
            'severity': random.randint(1, 5),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    return insert_data(session, 'health_incidents', data)

def seed_health_certifications(session, teacher_ids):
    """Seed health certifications"""
    if not teacher_ids:
        return 0
    
    data = []
    for i in range(20):
        data.append({
            'teacher_id': random.choice(teacher_ids),
            'certification_type': random.choice(['FIRST_AID', 'CPR', 'HEALTH_EDUCATION']),
            'certification_number': f"HE{i+1:04d}",
            'expiry_date': datetime.now() + timedelta(days=random.randint(30, 365)),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    return insert_data(session, 'health_instructor_certifications', data)

def seed_health_activities(session, lesson_plan_ids):
    """Seed health activities"""
    if not lesson_plan_ids:
        return 0
    
    data = []
    for i in range(40):
        data.append({
            'lesson_plan_id': random.choice(lesson_plan_ids),
            'activity_name': f"Health Activity {i+1}",
            'description': f"Description for health activity {i+1}",
            'duration_minutes': random.randint(20, 60),
            'order_index': i + 1,
            'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    return insert_data(session, 'health_lesson_activities', data)

def seed_health_progress(session, student_ids):
    """Seed health progress"""
    if not student_ids:
        return 0
    
    data = []
    for i in range(80):
        data.append({
            'student_id': random.choice(student_ids),
            'lesson_id': random.randint(1, 50),
            'completion_percentage': random.randint(0, 100),
            'status': random.choice(['IN_PROGRESS', 'COMPLETED', 'FAILED']),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    return insert_data(session, 'health_student_progress', data)

def seed_filters(session, user_ids):
    """Seed filters"""
    if not user_ids:
        return 0
    
    data = []
    for i in range(20):
        data.append({
            'user_id': random.choice(user_ids),
            'filter_name': f"Filter {i+1}",
            'filter_config': json.dumps({
                'type': random.choice(['DATE', 'CATEGORY', 'STATUS']),
                'value': f"value_{i+1}"
            }),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    return insert_data(session, 'filters', data)

def seed_lesson_plan_sharing(session, user_ids, lesson_plan_ids):
    """Seed lesson plan sharing"""
    if not user_ids or not lesson_plan_ids:
        return 0
    
    data = []
    for i in range(50):
        data.append({
            'lesson_plan_id': random.choice(lesson_plan_ids),
            'shared_by_user_id': random.choice(user_ids),
            'shared_with_user_id': random.choice(user_ids),
            'permission_level': random.choice(['READ', 'WRITE', 'ADMIN']),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    return insert_data(session, 'lesson_plan_sharing', data)

def seed_lesson_plan_usage(session, user_ids, lesson_plan_ids):
    """Seed lesson plan usage"""
    if not user_ids or not lesson_plan_ids:
        return 0
    
    data = []
    for i in range(100):
        data.append({
            'lesson_plan_id': random.choice(lesson_plan_ids),
            'user_id': random.choice(user_ids),
            'usage_type': random.choice(['VIEW', 'COPY', 'MODIFY']),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    return insert_data(session, 'lesson_plan_usage', data)

def seed_lesson_plans(session, teacher_ids):
    """Seed lesson plans"""
    if not teacher_ids:
        return 0
    
    data = []
    for i in range(50):
        data.append({
            'teacher_id': random.choice(teacher_ids),
            'title': f"Lesson Plan {i+1}",
            'description': f"Description for lesson plan {i+1}",
            'subject': random.choice(['PE', 'Health', 'Science']),
            'grade_level': random.choice(['K-2', '3-5', '6-8', '9-12']),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    return insert_data(session, 'lesson_plans', data)

def seed_template_category_associations(session):
    """Seed template category associations"""
    data = []
    for i in range(50):
        data.append({
            'template_id': random.randint(1, 20),
            'category_id': random.randint(1, 30),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    return insert_data(session, 'template_category_associations', data)

def seed_jobs(session):
    """Seed jobs"""
    data = []
    for i in range(10):
        data.append({
            'job_name': f"Job {i+1}",
            'job_type': random.choice(['BACKUP', 'CLEANUP', 'ANALYTICS', 'REPORT']),
            'status': random.choice(['PENDING', 'RUNNING', 'COMPLETED', 'FAILED']),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    return insert_data(session, 'job', data)

def seed_job_details(session):
    """Seed job details"""
    data = []
    for i in range(50):
        data.append({
            'job_id': random.randint(1, 10),
            'status': random.choice(['STARTED', 'IN_PROGRESS', 'COMPLETED', 'FAILED']),
            'message': f"Job detail message {i+1}",
            'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    return insert_data(session, 'job_run_details', data)

def seed_generic_table(session, table_name, user_ids, student_ids):
    """Generic seeding for unknown tables"""
    # Try to insert basic data based on common patterns
    try:
        # Check if table has common columns
        result = session.execute(text(f"""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = '{table_name}' 
            AND table_schema = 'public'
        """))
        columns = {row[0]: row[1] for row in result.fetchall()}
        
        data = []
        for i in range(10):  # Insert 10 generic records
            record = {}
            
            # Add common fields
            if 'id' in columns:
                record['id'] = i + 1
            if 'name' in columns:
                record['name'] = f"{table_name.title()} {i+1}"
            if 'description' in columns:
                record['description'] = f"Description for {table_name} {i+1}"
            if 'user_id' in columns and user_ids:
                record['user_id'] = random.choice(user_ids)
            if 'student_id' in columns and student_ids:
                record['student_id'] = random.choice(student_ids)
            if 'created_at' in columns:
                record['created_at'] = datetime.now() - timedelta(days=random.randint(1, 30))
            if 'updated_at' in columns:
                record['updated_at'] = datetime.now() - timedelta(days=random.randint(1, 7))
            if 'is_active' in columns:
                record['is_active'] = random.choice([True, False])
            if 'status' in columns:
                record['status'] = random.choice(['ACTIVE', 'INACTIVE', 'PENDING'])
            
            data.append(record)
        
        return insert_data(session, table_name, data)
        
    except Exception as e:
        print(f"    ⚠️  Could not seed {table_name}: {e}")
        return 0

def insert_data(session, table_name, data):
    """Insert data into a table"""
    if not data:
        return 0
    
    try:
        # Get column names from first record
        columns = list(data[0].keys())
        columns_str = ', '.join(columns)
        placeholders = ', '.join([f':{col}' for col in columns])
        
        query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
        
        for record in data:
            session.execute(text(query), record)
        
        return len(data)
    except Exception as e:
        print(f"    ⚠️  Error inserting into {table_name}: {e}")
        return 0

if __name__ == "__main__":
    seed_empty_tables()
