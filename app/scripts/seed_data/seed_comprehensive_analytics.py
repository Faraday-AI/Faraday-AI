from datetime import datetime, timedelta
import random
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select, text
import json

def seed_comprehensive_analytics(session: Session) -> Dict[str, int]:
    """Seed comprehensive analytics and performance data for district-level insights."""
    print("Seeding comprehensive analytics and performance data...")
    
    total_records = {}
    
    # Get existing data for relationships
    students = session.execute(select(text("id")).select_from(text("students")).limit(500)).fetchall()
    activities = session.execute(select(text("id")).select_from(text("activities")).limit(200)).fetchall()
    routines = session.execute(select(text("id")).select_from(text("physical_education_routines")).limit(100)).fetchall()
    users = session.execute(select(text("id")).select_from(text("users")).limit(50)).fetchall()
    
    if not students or not activities:
        print("  No students or activities found, skipping analytics seeding")
        return {"total": 0}
    
    student_ids = [row[0] for row in students]
    activity_ids = [row[0] for row in activities]
    routine_ids = [row[0] for row in routines] if routines else []
    user_ids = [row[0] for row in users] if users else []
    
    print(f"    Found {len(student_ids)} students, {len(activity_ids)} activities, {len(routine_ids)} routines, {len(user_ids)} users")
    
    # 1. Seed Performance Logs (should be 1,000+)
    try:
        from app.models.performance_log import PerformanceLog
        
        # Clear existing data
        session.execute(PerformanceLog.__table__.delete())
        
        performance_logs_created = 0
        components = ["activity_tracker", "routine_manager", "assessment_system", "progress_monitor", "safety_checker"]
        operations = ["start_activity", "complete_activity", "assess_performance", "update_progress", "check_safety", "generate_report"]
        
        for i in range(1200):  # Create 1,200 performance logs
            log = PerformanceLog(
                component=random.choice(components),
                operation=random.choice(operations),
                duration=random.uniform(0.1, 5.0),
                status=random.choice(["SUCCESS", "SUCCESS", "SUCCESS", "WARNING", "ERROR"]),
                error_message=random.choice([None, "Timeout occurred", "Resource limit reached"]) if random.random() < 0.1 else None,
                performance_metadata={
                    "user_id": random.choice(user_ids) if user_ids else None,
                    "request_size": random.randint(100, 10000),
                    "response_size": random.randint(50, 5000),
                    "memory_usage": random.uniform(10, 100),
                    "cpu_usage": random.uniform(5, 50)
                }
            )
            session.add(log)
            performance_logs_created += 1
            
            if performance_logs_created % 100 == 0:
                session.flush()
        
        session.commit()
        total_records["performance_logs"] = performance_logs_created
        print(f"    Created {performance_logs_created} performance logs")
        
    except Exception as e:
        print(f"    Could not seed performance logs: {e}")
        total_records["performance_logs"] = 0
    
    # 2. Seed Analytics Events (should be 10,000+)
    try:
        # Import the correct model
        from app.models.analytics.user_analytics import AnalyticsEvent
        
        analytics_events_created = 0
        
        # Get users for foreign key relationships
        try:
            users = session.execute(text("SELECT id FROM users LIMIT 100")).fetchall()
            user_ids = [u[0] for u in users] if users else [1]
        except:
            user_ids = [1]  # Default fallback
        
        # Note: No need to delete existing data - initial cascade drop cleared everything
        
        # Create analytics events using ORM
        event_types = ["PAGE_VIEW", "BUTTON_CLICK", "FORM_SUBMIT", "API_CALL", "ERROR", "PERFORMANCE", "USER_ACTION", "SYSTEM_EVENT"]
        sources = ["web", "mobile", "api", "dashboard"]
        
        for i in range(10000):  # Create 10,000 analytics events
            event_data = {
                "event_type": random.choice(event_types),
                "user_id": random.choice(user_ids),
                "event_data": {
                    "page": f"/page_{random.randint(1, 50)}",
                    "action": f"action_{random.randint(1, 100)}",
                    "timestamp": (datetime.now() - timedelta(days=random.randint(1, 365))).isoformat(),
                    "session_data": {
                        "session_id": f"session_{random.randint(1000, 9999)}",
                        "duration": random.randint(30, 3600),
                        "interactions": random.randint(1, 50)
                    }
                },
                "session_id": f"session_{random.randint(1000, 9999)}",
                "timestamp": datetime.now() - timedelta(days=random.randint(1, 365)),
                "source": random.choice(sources),
                "version": f"{random.randint(1, 5)}.{random.randint(0, 9)}.{random.randint(0, 9)}",
                "event_metadata": {
                    "browser": random.choice(["Chrome", "Firefox", "Safari", "Edge"]),
                    "device": random.choice(["desktop", "mobile", "tablet"]),
                    "location": random.choice(["US", "CA", "UK", "AU", "DE"]),
                    "performance_score": random.uniform(0.5, 1.0)
                }
            }
            
            event = AnalyticsEvent(
                user_id=event_data["user_id"],
                event_type=event_data["event_type"],
                event_data=event_data["event_data"],
                session_id=event_data["session_id"],
                timestamp=event_data["timestamp"],
                source=event_data["source"],
                version=event_data["version"],
                event_metadata=event_data["event_metadata"]
            )
            
            session.add(event)
            analytics_events_created += 1
            
            if analytics_events_created % 1000 == 0:
                session.flush()
                print(f"      Created {analytics_events_created} analytics events...")
        
        session.commit()
        total_records["analytics_events"] = analytics_events_created
        print(f"    Created {analytics_events_created} analytics events")
        
    except Exception as e:
        print(f"    Could not seed analytics events: {e}")
        total_records["analytics_events"] = 0
    
    # 3. Seed AI Suites and Tools (should be 100+)
    try:
        # Import the correct models
        from app.dashboard.models.ai_suite import AISuite
        from app.dashboard.models.ai_tool import AITool
        from app.dashboard.models.feedback import Feedback
        
        ai_suites_created = 0
        ai_tools_created = 0
        
        # Get dashboard users for foreign key relationships
        try:
            dashboard_users = session.execute(text("SELECT id FROM dashboard_users LIMIT 100")).fetchall()
            dashboard_user_ids = [u[0] for u in dashboard_users] if dashboard_users else [1]
        except:
            dashboard_user_ids = [1]  # Default fallback
        
        # Clear existing data first
        # Note: No need to delete existing data - initial cascade drop cleared everything
        
        # Create AI suites using ORM
        suite_data_list = [
            {"name": "PE Assessment AI", "description": "AI-powered physical education assessment system", "status": "ACTIVE"},
            {"name": "Performance Analytics AI", "description": "Comprehensive performance analysis and insights", "status": "ACTIVE"},
            {"name": "Safety Monitoring AI", "description": "Real-time safety monitoring and alert system", "status": "ACTIVE"},
            {"name": "Progress Tracking AI", "description": "Intelligent progress tracking and recommendations", "status": "ACTIVE"},
            {"name": "Adaptive Learning AI", "description": "Personalized learning path optimization", "status": "ACTIVE"}
        ]
        
        created_suites = []
        for suite_data in suite_data_list:
            suite = AISuite(
                name=suite_data["name"],
                description=suite_data["description"],
                user_id=random.choice(dashboard_user_ids),
                is_active=True,
                created_at=datetime.now() - timedelta(days=random.randint(30, 365))
            )
            session.add(suite)
            created_suites.append(suite)
            ai_suites_created += 1
        
        session.flush()  # Flush to get IDs
        
        # Create AI tools using ORM
        tool_data_list = [
            {"name": "Movement Analyzer", "description": "Analyzes student movement patterns", "suite_id": 1, "status": "ACTIVE"},
            {"name": "Performance Predictor", "description": "Predicts student performance trends", "suite_id": 2, "status": "ACTIVE"},
            {"name": "Safety Alert System", "description": "Monitors and alerts safety concerns", "suite_id": 3, "status": "ACTIVE"},
            {"name": "Progress Optimizer", "description": "Optimizes learning progression paths", "suite_id": 4, "status": "ACTIVE"},
            {"name": "Adaptive Coach", "description": "Provides personalized coaching feedback", "suite_id": 5, "status": "ACTIVE"}
        ]
        
        for tool_data in tool_data_list:
            tool = AITool(
                name=tool_data["name"],
                description=tool_data["description"],
                suite_id=created_suites[tool_data["suite_id"]-1].id if tool_data["suite_id"] <= len(created_suites) else None,
                tool_type="ANALYTICS",  # Default tool type
                created_at=datetime.now() - timedelta(days=random.randint(30, 365))
            )
            session.add(tool)
            ai_tools_created += 1
        
        session.commit()
        total_records["ai_suites"] = ai_suites_created
        total_records["ai_tools"] = ai_tools_created
        print(f"    Created {ai_suites_created} AI suites and {ai_tools_created} AI tools")
        
    except Exception as e:
        print(f"    Could not seed AI suites and tools: {e}")
        total_records["ai_suites"] = 0
        total_records["ai_tools"] = 0
    
    # 4. Seed Feedback Data (should be 500+)
    try:
        # Use ORM for feedback
        feedback_created = 0
        
        # Clear existing data first
        # Note: No need to delete existing data - initial cascade drop cleared everything
        
        feedback_types = ["PERFORMANCE", "SAFETY", "TECHNIQUE", "PROGRESS", "GENERAL"]
        
        for i in range(500):  # Create 500 feedback records
            feedback = Feedback(
                user_id=random.choice(dashboard_user_ids) if 'dashboard_user_ids' in locals() else random.randint(1, 100),
                gpt_id=f"gpt_{random.randint(1000, 9999)}",
                feedback_type=random.choice(feedback_types),
                content={
                    "message": f"Comprehensive feedback entry {i+1} for system improvement and student development",
                    "category": "physical_education",
                    "context": "seeding_data"
                },
                rating=random.randint(1, 5),
                created_at=datetime.now() - timedelta(days=random.randint(1, 180)),
                status=random.choice(["open", "in_progress", "resolved"]),
                priority=random.choice(["low", "medium", "high"])
            )
            
            session.add(feedback)
            feedback_created += 1
            
            if feedback_created % 100 == 0:
                session.flush()
                print(f"      Created {feedback_created} feedback records...")
        
        session.commit()
        total_records["feedback"] = feedback_created
        print(f"    Created {feedback_created} feedback records")
        
    except Exception as e:
        print(f"    Could not seed feedback data: {e}")
        total_records["feedback"] = 0
    
    # 5. Seed Additional Activity Performances (should be 1,000+)
    try:
        from app.models.physical_education.activity.models import StudentActivityPerformance
        
        # Create additional activity performances for better data distribution
        additional_performances_created = 0
        
        for i in range(1000):  # Create 1,000 additional performance records
            from app.models.physical_education.pe_enums.pe_types import PerformanceLevel
            
            # Get random performance level and convert to uppercase string for database compatibility
            performance_level_enum = random.choice([PerformanceLevel.EXCELLENT, PerformanceLevel.GOOD, PerformanceLevel.SATISFACTORY, PerformanceLevel.NEEDS_IMPROVEMENT, PerformanceLevel.POOR])
            performance_level_str = performance_level_enum.value.upper()
            
            performance = StudentActivityPerformance(
                student_id=random.choice(student_ids),
                activity_id=random.choice(activity_ids),
                performance_level=performance_level_str,
                score=random.uniform(60, 100),
                completion_time=random.randint(15, 60),
                attempts=random.randint(1, 5),
                recorded_at=datetime.now() - timedelta(days=random.randint(1, 90)),
                notes=f"Additional comprehensive performance record {i+1} for analytics",
                feedback={"teacher_notes": "Good effort, keep practicing", "peer_feedback": "Great teamwork!"},
                performance_metadata={"location": "gym", "weather": "indoor", "equipment_used": "standard"}
            )
            session.add(performance)
            additional_performances_created += 1
            
            if additional_performances_created % 100 == 0:
                session.flush()
                print(f"      Created {additional_performances_created} additional activity performances...")
        
        session.commit()
        total_records["additional_activity_performances"] = additional_performances_created
        print(f"    Created {additional_performances_created} additional activity performances")
        
    except Exception as e:
        print(f"    Could not seed additional activity performances: {e}")
        total_records["additional_activity_performances"] = 0
    
    # Calculate total records
    total_records["total"] = sum(total_records.values())
    
    print(f"✅ Comprehensive analytics seeding complete! Created {total_records['total']} total records")
    print(f"    Breakdown:")
    for key, value in total_records.items():
        if key != "total":
            print(f"      - {key}: {value}")
    
    return total_records 