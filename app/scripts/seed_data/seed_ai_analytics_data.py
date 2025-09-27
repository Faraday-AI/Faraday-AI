from datetime import datetime, timedelta
import random
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select, text

def seed_ai_analytics_data(session):
    """Seed AI and analytics data for empty tables."""
    print("  Seeding AI and analytics data...")
    
    total_records = 0
    
    # Seed AI suites (if table exists)
    try:
        from app.dashboard.models.ai_suite import AISuite
        
        # Clear existing data first - delete in correct order to handle foreign keys
        session.execute(text("DELETE FROM ai_tools"))  # Delete dependent table first
        session.execute(text("DELETE FROM ai_suites"))  # Then delete parent table
        session.commit()  # Commit the deletions
        
        # Get user IDs for foreign key references
        user_result = session.execute(text("SELECT id FROM dashboard_users LIMIT 10"))
        user_ids = [row[0] for row in user_result.fetchall()]
        if not user_ids:
            user_ids = [1]  # Fallback
        
        # Create new AI suites
        ai_suites = [
            {
                "name": "PE Performance Analyzer",
                "description": "AI system for analyzing physical education performance",
                "version": "1.0.0",
                "user_id": random.choice(user_ids),
                "configuration": {"capabilities": ["performance_analysis", "skill_assessment", "progress_tracking"]},
                "is_active": True,
                "created_at": datetime.now() - timedelta(days=30)
            },
            {
                "name": "Movement Pattern Recognition",
                "description": "AI system for recognizing and analyzing movement patterns",
                "version": "2.1.0",
                "user_id": random.choice(user_ids),
                "configuration": {"capabilities": ["pattern_recognition", "form_analysis", "injury_prevention"]},
                "is_active": True,
                "created_at": datetime.now() - timedelta(days=25)
            },
            {
                "name": "Adaptive Learning Engine",
                "description": "AI system for adaptive physical education learning",
                "version": "1.5.0",
                "user_id": random.choice(user_ids),
                "configuration": {"capabilities": ["adaptive_curriculum", "personalized_goals", "skill_progression"]},
                "is_active": True,
                "created_at": datetime.now() - timedelta(days=20)
            }
        ]
        
        for suite_data in ai_suites:
            suite = AISuite(**suite_data)
            session.add(suite)
            total_records += 1
        
        session.commit()  # Commit AI suites before creating tools
        print(f"    Created {len(ai_suites)} AI suites")
        
    except Exception as e:
        print(f"    Could not seed AI suites: {e}")
    
    # Seed AI tools (if table exists)
    try:
        from app.dashboard.models.ai_tool import AITool
        
        # Clear existing data first
        session.execute(text("DELETE FROM ai_tools"))
        session.commit()  # Commit the deletion
        
        # Get suite IDs for foreign key references
        suite_result = session.execute(text("SELECT id FROM ai_suites LIMIT 10"))
        suite_ids = [row[0] for row in suite_result.fetchall()]
        if not suite_ids:
            suite_ids = [1]  # Fallback
        
        # Create new AI tools
        ai_tools = [
            {
                "name": "Performance Dashboard",
                "description": "AI-powered performance visualization tool",
                "tool_type": "VISUALIZATION",
                "status": "ACTIVE",
                "suite_id": random.choice(suite_ids),
                "configuration": {"capabilities": ["charts", "graphs", "reports"]},
                "created_at": datetime.now() - timedelta(days=15)
            },
            {
                "name": "Skill Assessment Bot",
                "description": "AI chatbot for skill assessment",
                "tool_type": "CHATBOT",
                "status": "ACTIVE",
                "suite_id": random.choice(suite_ids),
                "configuration": {"capabilities": ["conversation", "assessment", "feedback"]},
                "created_at": datetime.now() - timedelta(days=10)
            },
            {
                "name": "Progress Tracker",
                "description": "AI tool for tracking student progress",
                "tool_type": "TRACKING",
                "status": "ACTIVE",
                "suite_id": random.choice(suite_ids),
                "configuration": {"capabilities": ["progress_monitoring", "goal_setting", "milestone_tracking"]},
                "created_at": datetime.now() - timedelta(days=5)
            }
        ]
        
        for tool_data in ai_tools:
            tool = AITool(**tool_data)
            session.add(tool)
            total_records += 1
        
        session.commit()  # Commit AI tools
        print(f"    Created {len(ai_tools)} AI tools")
        
    except Exception as e:
        print(f"    Could not seed AI tools: {e}")
    
    # Seed analytics events (if table exists)
    try:
        from app.models.analytics.user_analytics import AnalyticsEvent
        
        # Clear existing data first
        session.execute(text("DELETE FROM analytics_events"))
        
        # Get user IDs for foreign key references
        user_result = session.execute(text("SELECT id FROM users LIMIT 50"))
        user_ids = [row[0] for row in user_result.fetchall()]
        if not user_ids:
            user_ids = list(range(1, 51))  # Fallback
        
        # Create new analytics events
        for i in range(50):
            event = AnalyticsEvent(
                event_type=random.choice(["USER_LOGIN", "ACTIVITY_COMPLETED", "ASSESSMENT_TAKEN", "PROGRESS_UPDATED"]),
                user_id=random.choice(user_ids),
                event_data={
                    "timestamp": datetime.now().isoformat(),
                    "session_id": f"session_{i}",
                    "page": random.choice(["dashboard", "activities", "assessments", "progress"]),
                    "action": random.choice(["view", "create", "update", "delete"])
                },
                session_id=f"session_{i}",
                source=random.choice(["web", "mobile", "api"]),
                version="1.0.0",
                event_metadata={"test": True, "iteration": i},
                timestamp=datetime.now() - timedelta(days=random.randint(1, 30))
            )
            session.add(event)
            total_records += 1
        
        print(f"    Created 50 analytics events")
        
    except Exception as e:
        print(f"    Could not seed analytics events: {e}")
    
    # Seed feedback data (if table exists)
    try:
        from app.dashboard.models.feedback import Feedback
        
        # Clear existing data first
        session.execute(text("DELETE FROM dashboard_feedback"))
        
        # Get user IDs for foreign key references
        user_result = session.execute(text("SELECT id FROM dashboard_users LIMIT 50"))
        user_ids = [row[0] for row in user_result.fetchall()]
        if not user_ids:
            user_ids = list(range(1, 51))  # Fallback
        
        # Create new feedback records
        feedback_types = ["SUGGESTION", "BUG_REPORT", "FEATURE_REQUEST", "GENERAL"]
        feedback_statuses = ["open", "in_progress", "resolved", "closed"]
        
        for i in range(25):
            feedback = Feedback(
                user_id=random.choice(user_ids),
                gpt_id=f"gpt_{i+1}",
                title=f"Feedback {i+1}",
                feedback_type=random.choice(feedback_types),
                content={
                    "description": f"This is feedback record number {i+1} for testing purposes",
                    "category": random.choice(["performance", "usability", "feature", "bug"])
                },
                rating=random.randint(1, 5),
                status=random.choice(feedback_statuses),
                priority=random.choice(["LOW", "MEDIUM", "HIGH", "CRITICAL"])
            )
            session.add(feedback)
            total_records += 1
        
        print(f"    Created 25 feedback records")
        
    except Exception as e:
        print(f"    Could not seed feedback data: {e}")
    
    print(f"  Total AI and analytics records created: {total_records}")
    return total_records 