"""Seed comprehensive GPT/AI system data."""
from datetime import datetime, timedelta
import random
import json
from sqlalchemy.orm import Session
from sqlalchemy import text

def seed_gpt_system(session: Session) -> None:
    """Seed comprehensive GPT/AI system data."""
    print("Seeding GPT/AI system...")
    
    # First, we need to create some basic GPT records since the schema is different than expected
    # The gpt_categories table has gpt_id and category_id, not name/description
    
    # Create some basic GPT records first
    gpt_records = [
        {"name": "PE Lesson Planner", "description": "AI-powered lesson planning assistant", "version": "1.0.0"},
        {"name": "Safety Monitor", "description": "AI safety monitoring and alert system", "version": "1.2.0"},
        {"name": "Student Performance Analyzer", "description": "AI student performance analysis", "version": "1.1.0"},
        {"name": "Equipment Tracker", "description": "AI equipment management system", "version": "1.0.0"},
        {"name": "Health Metrics Analyzer", "description": "AI health and fitness analysis", "version": "1.3.0"},
        {"name": "Admin Assistant", "description": "AI administrative support", "version": "1.0.0"}
    ]
    
    # Since the schema is different, let's focus on seeding tables that actually exist
    # and have the expected structure
    
    # Seed GPT subscription plans (if table exists)
    try:
        plans = [
            {"name": "Basic", "description": "Basic AI features", "price": 29.99, "currency": "USD", "billing_cycle": "monthly", "features": ["basic_analysis", "standard_reports"]},
            {"name": "Professional", "description": "Professional AI features", "price": 79.99, "currency": "USD", "billing_cycle": "monthly", "features": ["advanced_analysis", "custom_reports", "priority_support"]},
            {"name": "Enterprise", "description": "Enterprise AI features", "price": 199.99, "currency": "USD", "billing_cycle": "monthly", "features": ["full_ai_suite", "custom_integration", "dedicated_support"]}
        ]
        
        for plan_data in plans:
            try:
                existing = session.execute(
                    text("SELECT id FROM gpt_subscription_plans WHERE name = :name"),
                    {"name": plan_data["name"]}
                ).first()
                
                if not existing:
                    session.execute(
                        text("""
                            INSERT INTO gpt_subscription_plans (name, description, price, currency, billing_cycle, features, is_active, is_public, status)
                            VALUES (:name, :description, :price, :currency, :billing_cycle, :features, :is_active, :is_public, :status)
                        """),
                        {
                            "name": plan_data["name"],
                            "description": plan_data["description"],
                            "price": plan_data["price"],
                            "currency": plan_data["currency"],
                            "billing_cycle": plan_data["billing_cycle"],
                            "features": json.dumps(plan_data["features"]),
                            "is_active": True,
                            "is_public": True,
                            "status": "ACTIVE"
                        }
                    )
            except Exception as e:
                print(f"Warning: Could not seed GPT subscription plan {plan_data['name']}: {e}")
    except Exception as e:
        print(f"Warning: GPT subscription plans table may not exist: {e}")
    
    # Seed GPT subscriptions
    try:
        # Get some user IDs and plan IDs
        user_ids = session.execute(text("SELECT id FROM users LIMIT 3")).fetchall()
        plan_ids = session.execute(text("SELECT id FROM gpt_subscription_plans LIMIT 3")).fetchall()
        
        if user_ids and plan_ids:
            for i, user_id in enumerate(user_ids):
                plan_id = plan_ids[i % len(plan_ids)][0]
                
                existing = session.execute(
                    text("SELECT id FROM gpt_subscriptions WHERE user_id = :user_id AND plan_id = :plan_id"),
                    {"user_id": user_id[0], "plan_id": plan_id}
                ).first()
                
                if not existing:
                    start_date = datetime.utcnow() - timedelta(days=10)
                    end_date = start_date + timedelta(days=365)
                    
                    session.execute(
                        text("""
                            INSERT INTO gpt_subscriptions (user_id, plan_id, subscription_type, status, start_date, end_date, billing_cycle, price, currency, auto_renew, is_active)
                            VALUES (:user_id, :plan_id, :subscription_type, :status, :start_date, :end_date, :billing_cycle, :price, :currency, :auto_renew, :is_active)
                        """),
                        {
                            "user_id": user_id[0],
                            "plan_id": plan_id,
                            "subscription_type": "premium",
                            "status": "ACTIVE",
                            "start_date": start_date,
                            "end_date": end_date,
                            "billing_cycle": "monthly",
                            "price": 29.99,
                            "currency": "USD",
                            "auto_renew": True,
                            "is_active": True
                        }
                    )
    except Exception as e:
        print(f"Warning: Could not seed GPT subscriptions: {e}")
    
    # Seed GPT usage history (if table exists)
    try:
        # Get subscription IDs from dashboard_gpt_subscriptions
        subscription_ids = session.execute(text("SELECT id FROM dashboard_gpt_subscriptions LIMIT 3")).fetchall()
        
        if subscription_ids:
            for subscription_id in subscription_ids:
                # Generate 30 days of usage data
                for i in range(30):
                    session.execute(
                        text("""
                            INSERT INTO gpt_usage_history (subscription_id, interaction_type, details, timestamp, metadata)
                            VALUES (:subscription_id, :interaction_type, :details, :timestamp, :metadata)
                        """),
                        {
                            "subscription_id": subscription_id[0],
                            "interaction_type": random.choice(["analysis", "generation", "training", "inference"]),
                            "details": json.dumps({"tokens_used": random.randint(100, 5000), "cost": round(random.uniform(0.01, 0.50), 2)}),
                            "timestamp": datetime.utcnow() - timedelta(days=i),
                            "metadata": json.dumps({"source": "seeding", "batch": i})
                        }
                    )
    except Exception as e:
        print(f"Warning: Could not seed GPT usage history: {e}")
    
    # Seed GPT performance metrics (if table exists)
    try:
        # Get actual subscription IDs from dashboard_gpt_subscriptions (not gpt_subscriptions)
        subscription_ids = session.execute(text("SELECT id FROM dashboard_gpt_subscriptions LIMIT 3")).fetchall()
        user_ids = session.execute(text("SELECT id FROM dashboard_users LIMIT 3")).fetchall()
        
        if subscription_ids and user_ids:
            subscription_id = subscription_ids[0][0]
            user_id = user_ids[0][0]
            
            session.execute(
                text("""
                    INSERT INTO gpt_performance (subscription_id, model_id, user_id, metrics, timestamp, response_time, error_rate, usage_count)
                    VALUES (:subscription_id, :model_id, :user_id, :metrics, :timestamp, :response_time, :error_rate, :usage_count)
                """),
                {
                    "subscription_id": subscription_id,
                    "model_id": 1,  # Use a default ID for gpt_definitions
                    "user_id": user_id,
                    "metrics": json.dumps({"accuracy": round(random.uniform(0.85, 0.98), 3), "success_rate": round(random.uniform(0.90, 0.99), 3)}),
                    "timestamp": datetime.utcnow(),
                    "response_time": random.randint(100, 2000),
                    "error_rate": round(random.uniform(0.01, 0.15), 3),
                    "usage_count": random.randint(10, 100)
                }
            )
        else:
            print("Warning: No dashboard subscriptions or users found for GPT performance seeding")
    except Exception as e:
        print(f"Warning: Could not seed GPT performance: {e}")
    
    # Seed GPT analytics (if table exists)
    try:
        # Get actual user and subscription IDs from dashboard tables
        user_ids = session.execute(text("SELECT id FROM dashboard_users LIMIT 3")).fetchall()
        subscription_ids = session.execute(text("SELECT id FROM dashboard_gpt_subscriptions LIMIT 3")).fetchall()
        
        if user_ids and subscription_ids:
            analytics_data = [
                {"metric_name": "total_requests", "metric_value": random.randint(1000, 10000), "timestamp": datetime.utcnow() - timedelta(days=i)}
                for i in range(30)
            ]
            
            for analytics in analytics_data:
                try:
                    session.execute(
                        text("""
                            INSERT INTO gpt_analytics (user_id, subscription_id, metric_name, metric_value, timestamp)
                            VALUES (:user_id, :subscription_id, :metric_name, :metric_value, :timestamp)
                        """),
                        {
                            "user_id": user_ids[0][0],
                            "subscription_id": subscription_ids[0][0],
                            "metric_name": analytics["metric_name"],
                            "metric_value": analytics["metric_value"],
                            "timestamp": analytics["timestamp"]
                        }
                    )
                except Exception as e:
                    print(f"Warning: Could not seed GPT analytics: {e}")
        else:
            print("Warning: No dashboard users or subscriptions found for GPT analytics seeding")
    except Exception as e:
        print(f"Warning: Could not seed GPT analytics: {e}")
    
    # Seed GPT feedback (if table exists)
    try:
        # Get user and subscription IDs for feedback
        user_ids = session.execute(text("SELECT id FROM dashboard_users LIMIT 3")).fetchall()
        subscription_ids = session.execute(text("SELECT id FROM dashboard_gpt_subscriptions LIMIT 3")).fetchall()
        
        if user_ids and subscription_ids:
            feedback_data = [
                {"rating": 5, "comment": "Excellent AI assistance for lesson planning"},
                {"rating": 4, "comment": "Good safety monitoring, could be faster"},
                {"rating": 5, "comment": "Great student performance insights"},
                {"rating": 4, "comment": "Helpful equipment tracking"},
                {"rating": 5, "comment": "Accurate health metrics analysis"}
            ]
            
            for i, feedback in enumerate(feedback_data):
                try:
                    user_id = user_ids[i % len(user_ids)][0]
                    subscription_id = subscription_ids[i % len(subscription_ids)][0]
                    
                    session.execute(
                        text("""
                            INSERT INTO gpt_feedback (user_id, subscription_id, rating, comment, created_at)
                            VALUES (:user_id, :subscription_id, :rating, :comment, :created_at)
                        """),
                        {
                            "user_id": user_id,
                            "subscription_id": subscription_id,
                            "rating": feedback["rating"],
                            "comment": feedback["comment"],
                            "created_at": datetime.utcnow()
                        }
                    )
                except Exception as e:
                    print(f"Warning: Could not seed GPT feedback: {e}")
        else:
            print("Warning: No dashboard users or subscriptions found for GPT feedback seeding")
    except Exception as e:
        print(f"Warning: Could not seed GPT feedback: {e}")
    
    # Seed GPT integrations (if table exists)
    try:
        integrations = [
            {"name": "Canvas LMS", "integration_type": "lms", "status": "ACTIVE", "configuration": {"api_key": "demo_key", "endpoint": "https://canvas.example.com"}},
            {"name": "Google Classroom", "integration_type": "lms", "status": "ACTIVE", "configuration": {"oauth_token": "demo_token", "project_id": "demo_project"}},
            {"name": "Microsoft Teams", "integration_type": "communication", "status": "ACTIVE", "configuration": {"webhook_url": "https://teams.example.com/webhook"}},
            {"name": "Slack", "integration_type": "communication", "status": "ACTIVE", "configuration": {"bot_token": "demo_bot_token", "channel": "#pe-notifications"}}
        ]
        
        for integration_data in integrations:
            try:
                existing = session.execute(
                    text("SELECT id FROM gpt_integrations WHERE name = :name"),
                    {"name": integration_data["name"]}
                ).first()
                
                if not existing:
                    # Get a gpt_id for the integration
                    gpt_ids = session.execute(text("SELECT id FROM gpt_definitions LIMIT 1")).fetchall()
                    if gpt_ids:
                        gpt_id = gpt_ids[0][0]
                        
                        session.execute(
                            text("""
                                INSERT INTO gpt_integrations (gpt_id, integration_type, name, configuration, status, is_active, created_at)
                                VALUES (:gpt_id, :integration_type, :name, :configuration, :status, :is_active, :created_at)
                            """),
                            {
                                "gpt_id": gpt_id,
                                "integration_type": integration_data["integration_type"],
                                "name": integration_data["name"],
                                "configuration": json.dumps(integration_data["configuration"]),  # Convert dict to JSON string
                                "status": integration_data["status"],
                                "is_active": True,
                                "created_at": datetime.utcnow()
                            }
                        )
                    else:
                        print(f"Warning: No GPT definitions found for integration {integration_data['name']}")
            except Exception as e:
                print(f"Warning: Could not seed GPT integration {integration_data['name']}: {e}")
    except Exception as e:
        print(f"Warning: Could not seed GPT integrations: {e}")
    
    # Seed GPT context data (if table exists)
    try:
        # Generate context data
        context_data = {
            "example": "context_data", 
            "timestamp": datetime.utcnow().isoformat(),
            "type": "demo",
            "version": "1.0"
        }
        
        # Get some gpt_id values for context data
        gpt_ids = session.execute(text("SELECT id FROM gpt_definitions LIMIT 3")).fetchall()
        
        if gpt_ids:
            gpt_id = gpt_ids[0][0]
            
            session.execute(
                text("""
                    INSERT INTO context_data (context_id, gpt_id, data_type, content, status, created_at, updated_at)
                    VALUES (:context_id, :gpt_id, :data_type, :content, :status, :created_at, :updated_at)
                """),
                {
                    "context_id": 1,  # Use a default context ID
                    "gpt_id": gpt_id,
                    "data_type": random.choice(["lesson_plan", "safety_alert", "performance_analysis", "equipment_status"]),
                    "content": json.dumps(context_data),  # Convert dict to JSON string
                    "status": "ACTIVE",
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            )
        else:
            print("Warning: No GPT definitions found for context data seeding")
    except Exception as e:
        print(f"Warning: Could not seed GPT context data: {e}")
    
    print("GPT/AI system seeded successfully!") 