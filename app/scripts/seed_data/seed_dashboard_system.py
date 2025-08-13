"""Seed comprehensive dashboard system data."""
from datetime import datetime, timedelta
import random
import json
from sqlalchemy.orm import Session
from sqlalchemy import text

def seed_dashboard_system(session: Session) -> None:
    """Seed comprehensive dashboard system data."""
    print("Seeding dashboard system...")
    
    # Seed organizations first (required for dashboard teams)
    try:
        # Check if default organization exists
        existing_org = session.execute(
            text("SELECT id FROM organizations WHERE name = :name"),
            {"name": "Faraday AI Platform"}
        ).first()
        
        if not existing_org:
            result = session.execute(
                text("""
                    INSERT INTO organizations (name, type, subscription_tier, status, created_at, updated_at, is_active, metadata)
                    VALUES (:name, :type, :subscription_tier, :status, :created_at, :updated_at, :is_active, :metadata)
                    RETURNING id
                """),
                {
                    "name": "Faraday AI Platform",
                    "type": "PLATFORM",
                    "subscription_tier": "BASIC",
                    "status": "ACTIVE",
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                    "is_active": True,
                    "metadata": json.dumps({
                        "description": "Flexible Physical Education and safety platform for individual teachers, students, or any school district",
                        "use_cases": ["Individual Teachers", "Individual Students", "School Districts", "Multi-Organization"],
                        "flexibility": "High",
                        "deployment": "Generic"
                    })
                }
            )
            default_org_id = result.fetchone()[0]
            session.commit()
            print(f"Created flexible platform organization with ID: {default_org_id}")
        else:
            default_org_id = existing_org[0]
            print(f"Using existing flexible platform organization with ID: {default_org_id}")
    except Exception as e:
        print(f"Warning: Could not seed organization: {e}")
        # Use a fallback ID if seeding fails
        default_org_id = 1
    
    # Seed dashboard categories
    categories = [
        {"name": "Physical Education", "description": "PE-specific dashboards and widgets"},
        {"name": "Student Analytics", "description": "Student performance and progress tracking"},
        {"name": "Safety & Compliance", "description": "Safety monitoring and compliance tracking"},
        {"name": "Equipment Management", "description": "Equipment status and maintenance"},
        {"name": "Health & Fitness", "description": "Health metrics and fitness tracking"},
        {"name": "Administrative", "description": "Administrative and operational dashboards"}
    ]
    
    for cat_data in categories:
        try:
            # Check if category exists
            existing = session.execute(
                text("SELECT id FROM dashboard_categories WHERE name = :name"),
                {"name": cat_data["name"]}
            ).first()
            
            if not existing:
                session.execute(
                    text("""
                        INSERT INTO dashboard_categories (name, description, created_at)
                        VALUES (:name, :description, :created_at)
                    """),
                    {
                        "name": cat_data["name"],
                        "description": cat_data["description"],
                        "created_at": datetime.utcnow()
                    }
                )
        except Exception as e:
            print(f"Warning: Could not seed dashboard category {cat_data['name']}: {e}")
    
    # Seed dashboard themes
    themes = [
        {"name": "Default Light", "colors": {"primary": "#007bff", "secondary": "#6c757d", "background": "#ffffff"}, "typography": {"font_family": "Arial", "font_size": "14px"}, "spacing": {"padding": "16px", "margin": "8px"}},
        {"name": "Dark Mode", "colors": {"primary": "#17a2b8", "secondary": "#6c757d", "background": "#343a40"}, "typography": {"font_family": "Arial", "font_size": "14px"}, "spacing": {"padding": "16px", "margin": "8px"}},
        {"name": "PE Theme", "colors": {"primary": "#28a745", "secondary": "#ffc107", "background": "#f8f9fa"}, "typography": {"font_family": "Arial", "font_size": "14px"}, "spacing": {"padding": "16px", "margin": "8px"}},
        {"name": "Safety Theme", "colors": {"primary": "#dc3545", "secondary": "#fd7e14", "background": "#fff5f5"}, "typography": {"font_family": "Arial", "font_size": "14px"}, "spacing": {"padding": "16px", "margin": "8px"}}
    ]
    
    for theme_data in themes:
        try:
            existing = session.execute(
                text("SELECT id FROM dashboard_theme_configs WHERE name = :name"),
                {"name": theme_data["name"]}
            ).first()
            
            if not existing:
                session.execute(
                    text("""
                        INSERT INTO dashboard_theme_configs (name, colors, typography, spacing, status, is_active)
                        VALUES (:name, :colors, :typography, :spacing, :status, :is_active)
                    """),
                    {
                        "name": theme_data["name"],
                        "colors": json.dumps(theme_data["colors"]),
                        "typography": json.dumps(theme_data["typography"]),
                        "spacing": json.dumps(theme_data["spacing"]),
                        "status": "ACTIVE",
                        "is_active": True
                    }
                )
        except Exception as e:
            print(f"Warning: Could not seed dashboard theme {theme_data['name']}: {e}")
    
    # Seed dashboards first
    dashboards = [
        {"name": "PE Main Dashboard", "description": "Main Physical Education dashboard"},
        {"name": "Safety Monitor", "description": "Safety and compliance monitoring"},
        {"name": "Student Analytics", "description": "Student performance analytics"}
    ]
    
    dashboard_ids = []
    for dashboard_data in dashboards:
        try:
            existing = session.execute(
                text("SELECT id FROM dashboards WHERE name = :name"),
                {"name": dashboard_data["name"]}
            ).first()
            
            if not existing:
                result = session.execute(
                    text("""
                        INSERT INTO dashboards (name, description, layout, created_at)
                        VALUES (:name, :description, :layout, :created_at)
                        RETURNING id
                    """),
                    {
                        "name": dashboard_data["name"],
                        "description": dashboard_data["description"],
                        "layout": json.dumps({"type": "GRID", "columns": 3, "rows": 2}),  # Convert to JSON
                        "created_at": datetime.utcnow()
                    }
                )
                dashboard_ids.append(result.fetchone()[0])
                session.commit()
            else:
                dashboard_ids.append(existing[0])
        except Exception as e:
            print(f"Warning: Could not seed dashboard {dashboard_data['name']}: {e}")
            # Use a default ID if seeding fails
            dashboard_ids.append(1)
    
    # Seed dashboard widgets
    widgets = [
        {"name": "Student Attendance", "category": "Physical Education", "config": {"chart_type": "bar", "refresh_interval": 300}},
        {"name": "Safety Incidents", "category": "Safety & Compliance", "config": {"alert_level": "high", "refresh_interval": 60}},
        {"name": "Equipment Status", "category": "Equipment Management", "config": {"status_colors": {"available": "green", "maintenance": "yellow", "broken": "red"}}},
        {"name": "Health Metrics", "category": "Health & Fitness", "config": {"chart_type": "line", "refresh_interval": 600}},
        {"name": "Performance Trends", "category": "Student Analytics", "config": {"chart_type": "line", "refresh_interval": 3600}},
        {"name": "Class Schedule", "category": "Physical Education", "config": {"view": "week", "refresh_interval": 1800}}
    ]
    
    for widget_data in widgets:
        try:
            # Get category ID
            cat_result = session.execute(
                text("SELECT id FROM dashboard_categories WHERE name = :name"),
                {"name": widget_data["category"]}
            ).first()
            
            if cat_result:
                category_id = cat_result[0]
                
                existing = session.execute(
                    text("SELECT id FROM dashboard_widgets WHERE name = :name"),
                    {"name": widget_data["name"]}
                ).first()
                
                if not existing:
                    # Use the first dashboard ID or default to 1
                    dashboard_id = dashboard_ids[0] if dashboard_ids else 1
                    session.execute(
                        text("""
                            INSERT INTO dashboard_widgets (name, widget_type, configuration, dashboard_id, layout_position, size, created_at)
                            VALUES (:name, :widget_type, :configuration, :dashboard_id, :layout_position, :size, :created_at)
                        """),
                        {
                            "name": widget_data["name"],
                            "widget_type": "CHART",
                            "configuration": json.dumps(widget_data["config"]),
                            "dashboard_id": dashboard_id,
                            "layout_position": "TOP_LEFT",
                            "size": json.dumps({"width": 400, "height": 300}),
                            "created_at": datetime.utcnow()
                        }
                    )
        except Exception as e:
            print(f"Warning: Could not seed dashboard widget {widget_data['name']}: {e}")
    
    # Seed dashboard tools - check schema first
    try:
        # Check if dashboard_tools table has a 'type' column
        result = session.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'dashboard_tools' AND column_name = 'type'")).first()
        has_type_column = result is not None
        
        tools = [
            {"name": "Data Exporter", "description": "Export dashboard data to various formats", "type": "utility"},
            {"name": "Report Generator", "description": "Generate automated reports", "type": "reporting"},
            {"name": "Alert Manager", "description": "Manage dashboard alerts and notifications", "type": "monitoring"},
            {"name": "Data Analyzer", "description": "Advanced data analysis tools", "type": "analytics"}
        ]
        
        for tool_data in tools:
            try:
                existing = session.execute(
                    text("SELECT id FROM dashboard_tools WHERE name = :name"),
                    {"name": tool_data["name"]}
                ).first()
                
                if not existing:
                    if has_type_column:
                        session.execute(
                            text("""
                                INSERT INTO dashboard_tools (name, description, type, created_at)
                                VALUES (:name, :description, :type, :created_at)
                            """),
                            {
                                **tool_data,
                                "created_at": datetime.utcnow()
                            }
                        )
                    else:
                        # Fallback without type column
                        session.execute(
                            text("""
                                INSERT INTO dashboard_tools (name, description, created_at)
                                VALUES (:name, :description, :created_at)
                            """),
                            {
                                "name": tool_data["name"],
                                "description": tool_data["description"],
                                "created_at": datetime.utcnow()
                            }
                        )
            except Exception as e:
                print(f"Warning: Could not seed dashboard tool {tool_data['name']}: {e}")
    except Exception as e:
        print(f"Warning: Could not seed dashboard tools: {e}")
    
    # Seed dashboard users
    try:
        # Get existing user IDs with their details
        user_details = session.execute(text("SELECT id, email, password_hash, first_name, last_name, role FROM users LIMIT 3")).fetchall()
        
        for user_detail in user_details:
            existing = session.execute(
                text("SELECT id FROM dashboard_users WHERE core_user_id = :core_user_id"),
                {"core_user_id": user_detail[0]}
            ).first()
            
            if not existing:
                # Concatenate first_name and last_name, handle NULL values
                first_name = user_detail[3] or ""
                last_name = user_detail[4] or ""
                full_name = f"{first_name} {last_name}".strip() if first_name or last_name else "Unknown User"
                
                # Convert role to uppercase to match userrole enum
                user_role = user_detail[5] or "STAFF"
                dashboard_role = user_role.upper()
                
                # Map common roles to valid enum values
                role_mapping = {
                    "TEACHER": "TEACHER",
                    "ADMIN": "ADMIN", 
                    "STUDENT": "STUDENT",
                    "PARENT": "PARENT",
                    "STAFF": "STAFF",
                    "SUPERUSER": "ADMIN",
                    "USER": "STAFF"
                }
                
                dashboard_role = role_mapping.get(dashboard_role, "STAFF")
                
                session.execute(
                    text("""
                        INSERT INTO dashboard_users (core_user_id, email, hashed_password, full_name, role, preferences, created_at)
                        VALUES (:core_user_id, :email, :hashed_password, :full_name, :role, :preferences, :created_at)
                    """),
                    {
                        "core_user_id": user_detail[0],
                        "email": user_detail[1],
                        "hashed_password": user_detail[2],
                        "full_name": full_name,
                        "role": dashboard_role,
                        "preferences": json.dumps({"theme": "Default Light", "refresh_rate": 300}),
                        "created_at": datetime.utcnow()
                    }
                )
    except Exception as e:
        print(f"Warning: Could not seed dashboard users: {e}")
    
    # Seed dashboard teams
    teams = [
        {"name": "PE Department", "description": "Physical Education Department Team", "organization_id": default_org_id},
        {"name": "Safety Committee", "description": "Safety and Compliance Team", "organization_id": default_org_id},
        {"name": "Administrative", "description": "Administrative Support Team", "organization_id": default_org_id}
    ]
    
    for team_data in teams:
        try:
            existing = session.execute(
                text("SELECT id FROM dashboard_teams WHERE name = :name"),
                {"name": team_data["name"]}
            ).first()
            
            if not existing:
                session.execute(
                    text("""
                        INSERT INTO dashboard_teams (name, description, organization_id, created_at, updated_at, is_active, settings)
                        VALUES (:name, :description, :organization_id, :created_at, :updated_at, :is_active, :settings)
                    """),
                    {
                        **team_data,
                        "created_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow(),
                        "is_active": True,
                        "settings": json.dumps({"theme": "default", "notifications": True})
                    }
                )
        except Exception as e:
            print(f"Warning: Could not seed dashboard team {team_data['name']}: {e}")
    
    # Seed dashboard projects
    projects = [
        {"name": "PE Analytics Dashboard", "description": "Comprehensive PE analytics platform", "team_id": 1},
        {"name": "Safety Monitoring System", "description": "Real-time safety monitoring", "team_id": 2},
        {"name": "Equipment Management", "description": "Equipment tracking and maintenance", "team_id": 1}
    ]
    
    for project_data in projects:
        try:
            existing = session.execute(
                text("SELECT id FROM dashboard_projects WHERE name = :name"),
                {"name": project_data["name"]}
            ).first()
            
            if not existing:
                session.execute(
                    text("""
                        INSERT INTO dashboard_projects (name, description, team_id, user_id, status, organization_id, created_at, updated_at, is_template)
                        VALUES (:name, :description, :team_id, :user_id, :status, :organization_id, :created_at, :updated_at, :is_template)
                    """),
                    {
                        **project_data,
                        "user_id": 1,  # Use first user ID
                        "status": "ACTIVE",
                        "organization_id": default_org_id,
                        "created_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow(),
                        "is_template": False
                    }
                )
        except Exception as e:
            print(f"Warning: Could not seed dashboard project {project_data['name']}: {e}")
    
    # Seed dashboard shares
    try:
        # Get some project IDs instead of dashboard IDs
        project_ids = session.execute(text("SELECT id FROM dashboard_projects LIMIT 3")).fetchall()
        
        for project_id in project_ids:
            existing = session.execute(
                text("SELECT id FROM dashboard_shares WHERE project_id = :project_id"),
                {"project_id": project_id[0]}
            ).first()
            
            if not existing:
                session.execute(
                    text("""
                        INSERT INTO dashboard_shares (user_id, share_type, permissions, project_id, organization_id, created_at)
                        VALUES (:user_id, :share_type, :permissions, :project_id, :organization_id, :created_at)
                    """),
                    {
                        "user_id": 1,  # Use first user ID
                        "share_type": "TEAM",
                        "permissions": json.dumps({"read": True, "write": False, "admin": False}),
                        "project_id": project_id[0],
                        "organization_id": default_org_id,
                        "created_at": datetime.utcnow()
                    }
                )
    except Exception as e:
        print(f"Warning: Could not seed dashboard shares: {e}")
    
    # Seed dashboard filters
    filters = [
        {"name": "Date Range", "filter_type": "date", "configuration": {"default": "last_30_days"}},
        {"name": "Student Grade", "filter_type": "select", "configuration": {"options": ["9th", "10th", "11th", "12th"]}},
        {"name": "Activity Type", "filter_type": "multi_select", "configuration": {"options": ["sports", "fitness", "safety", "assessment"]}},
        {"name": "Safety Level", "filter_type": "select", "configuration": {"options": ["low", "medium", "high", "critical"]}}
    ]
    
    for filter_data in filters:
        try:
            existing = session.execute(
                text("SELECT id FROM dashboard_filters WHERE name = :name"),
                {"name": filter_data["name"]}
            ).first()
            
            if not existing:
                session.execute(
                    text("""
                        INSERT INTO dashboard_filters (user_id, filter_type, name, configuration, applied_to, project_id, organization_id, created_at)
                        VALUES (:user_id, :filter_type, :name, :configuration, :applied_to, :project_id, :organization_id, :created_at)
                    """),
                    {
                        "user_id": 1,  # Use first user ID
                        "filter_type": filter_data["filter_type"],
                        "name": filter_data["name"],
                        "configuration": json.dumps(filter_data["configuration"]),
                        "applied_to": json.dumps({"scope": "global", "targets": ["dashboard", "widgets"]}),
                        "project_id": None,  # Global filter
                        "organization_id": default_org_id,
                        "created_at": datetime.utcnow()
                    }
                )
        except Exception as e:
            print(f"Warning: Could not seed dashboard filter {filter_data['name']}: {e}")
    
    # Seed dashboard analytics
    analytics_data = [
        {
            "metrics": {"dashboard_views": random.randint(100, 1000)},
            "timestamp": datetime.utcnow() - timedelta(days=i),
            "period": "daily",
            "gpt_usage": {"tokens": random.randint(1000, 5000), "cost": round(random.uniform(0.01, 0.10), 4)},
            "api_calls": {"total": random.randint(50, 200), "successful": random.randint(45, 190)},
            "error_logs": {"errors": random.randint(0, 5), "warnings": random.randint(1, 10)}
        }
        for i in range(30)
    ]
    
    for analytics in analytics_data:
        try:
            session.execute(
                text("""
                    INSERT INTO dashboard_analytics (user_id, metrics, timestamp, period, gpt_usage, api_calls, error_logs)
                    VALUES (:user_id, :metrics, :timestamp, :period, :gpt_usage, :api_calls, :error_logs)
                """),
                {
                    "user_id": 1,  # Use first user ID
                    "metrics": json.dumps(analytics["metrics"]),
                    "timestamp": analytics["timestamp"],
                    "period": analytics["period"],
                    "gpt_usage": json.dumps(analytics["gpt_usage"]),
                    "api_calls": json.dumps(analytics["api_calls"]),
                    "error_logs": json.dumps(analytics["error_logs"])
                }
            )
        except Exception as e:
            print(f"Warning: Could not seed dashboard analytics: {e}")
    
    print("Dashboard system seeded successfully!") 