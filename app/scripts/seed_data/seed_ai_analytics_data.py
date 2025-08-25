from datetime import datetime, timedelta
import random
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select

def seed_ai_analytics_data(session):
    """Seed AI and analytics data for empty tables."""
    print("  Seeding AI and analytics data...")
    
    total_records = 0
    
    # Seed AI suites (if table exists)
    try:
        from app.dashboard.models.ai_suite import AISuite
        
        # Clear existing data first
        session.execute(AISuite.__table__.delete())
        
        # Create new AI suites
        ai_suites = [
            {
                "name": "PE Performance Analyzer",
                "description": "AI system for analyzing physical education performance",
                "version": "1.0.0",
                "status": "ACTIVE",
                "capabilities": ["performance_analysis", "skill_assessment", "progress_tracking"],
                "created_at": datetime.now() - timedelta(days=30)
            },
            {
                "name": "Movement Pattern Recognition",
                "description": "AI system for recognizing and analyzing movement patterns",
                "version": "2.1.0",
                "status": "ACTIVE",
                "capabilities": ["pattern_recognition", "form_analysis", "injury_prevention"],
                "created_at": datetime.now() - timedelta(days=25)
            },
            {
                "name": "Adaptive Learning Engine",
                "description": "AI system for adaptive physical education learning",
                "version": "1.5.0",
                "status": "ACTIVE",
                "capabilities": ["adaptive_curriculum", "personalized_goals", "skill_progression"],
                "created_at": datetime.now() - timedelta(days=20)
            }
        ]
        
        for suite_data in ai_suites:
            suite = AISuite(**suite_data)
            session.add(suite)
            total_records += 1
        
        print(f"    Created {len(ai_suites)} AI suites")
        
    except Exception as e:
        print(f"    Could not seed AI suites: {e}")
    
    # Seed AI tools (if table exists)
    try:
        from app.dashboard.models.ai_tool import AITool
        
        # Clear existing data first
        session.execute(AITool.__table__.delete())
        
        # Create new AI tools
        ai_tools = [
            {
                "name": "Performance Dashboard",
                "description": "AI-powered performance visualization tool",
                "tool_type": "VISUALIZATION",
                "status": "ACTIVE",
                "capabilities": ["charts", "graphs", "reports"],
                "created_at": datetime.now() - timedelta(days=15)
            },
            {
                "name": "Skill Assessment Bot",
                "description": "AI chatbot for skill assessment",
                "tool_type": "CHATBOT",
                "status": "ACTIVE",
                "capabilities": ["conversation", "assessment", "feedback"],
                "created_at": datetime.now() - timedelta(days=10)
            },
            {
                "name": "Progress Tracker",
                "description": "AI tool for tracking student progress",
                "tool_type": "TRACKING",
                "status": "ACTIVE",
                "capabilities": ["progress_monitoring", "goal_setting", "milestone_tracking"],
                "created_at": datetime.now() - timedelta(days=5)
            }
        ]
        
        for tool_data in ai_tools:
            tool = AITool(**tool_data)
            session.add(tool)
            total_records += 1
        
        print(f"    Created {len(ai_tools)} AI tools")
        
    except Exception as e:
        print(f"    Could not seed AI tools: {e}")
    
    # Seed analytics events (if table exists)
    try:
        from app.models.analytics.user_analytics import AnalyticsEvent
        
        # Clear existing data first
        session.execute(AnalyticsEvent.__table__.delete())
        
        # Create new analytics events
        for i in range(50):
            event = AnalyticsEvent(
                event_type=random.choice(["USER_LOGIN", "ACTIVITY_COMPLETED", "ASSESSMENT_TAKEN", "PROGRESS_UPDATED"]),
                user_id=random.randint(1, 50),  # Random user ID
                event_data={
                    "timestamp": datetime.now().isoformat(),
                    "session_id": f"session_{i}",
                    "page": random.choice(["dashboard", "activities", "assessments", "progress"]),
                    "action": random.choice(["view", "create", "update", "delete"])
                },
                created_at=datetime.now() - timedelta(days=random.randint(1, 30))
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
        session.execute(Feedback.__table__.delete())
        
        # Create new feedback records
        feedback_types = ["SUGGESTION", "BUG_REPORT", "FEATURE_REQUEST", "GENERAL"]
        feedback_statuses = ["OPEN", "IN_PROGRESS", "RESOLVED", "CLOSED"]
        
        for i in range(25):
            feedback = Feedback(
                feedback_type=random.choice(feedback_types),
                title=f"Feedback {i+1}",
                description=f"This is feedback record number {i+1} for testing purposes",
                status=random.choice(feedback_statuses),
                priority=random.choice(["LOW", "MEDIUM", "HIGH", "CRITICAL"]),
                user_id=random.randint(1, 50),
                created_at=datetime.now() - timedelta(days=random.randint(1, 30))
            )
            session.add(feedback)
            total_records += 1
        
        print(f"    Created 25 feedback records")
        
    except Exception as e:
        print(f"    Could not seed feedback data: {e}")
    
    print(f"  Total AI and analytics records created: {total_records}")
    return total_records 