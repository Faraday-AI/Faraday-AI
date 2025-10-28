"""Seed comprehensive security system data."""
from datetime import datetime, timedelta
import random
import json
from sqlalchemy.orm import Session
from sqlalchemy import text

def seed_security_system(session: Session) -> None:
    """Seed comprehensive security system data."""
    print("Seeding security system...")
    
    # Reset any failed transaction state
    try:
        session.rollback()
    except:
        pass
    
    # Seed security policies - using the actual schema
    policies = [
        {"name": "Data Access Policy", "description": "Controls access to student and class data", "policy_type": "access_control", "status": "ACTIVE", "rules": {"enforcement": "strict", "audit_required": True}},
        {"name": "API Security Policy", "description": "API authentication and authorization rules", "policy_type": "api_security", "status": "ACTIVE", "rules": {"rate_limiting": True, "authentication_required": True}},
        {"name": "Audit Logging Policy", "description": "Requirements for system audit logging", "policy_type": "audit", "status": "ACTIVE", "rules": {"log_all_access": True, "retention_days": 365}},
        {"name": "Incident Response Policy", "description": "Security incident response procedures", "policy_type": "incident_response", "status": "ACTIVE", "rules": {"response_time": "1_hour", "escalation_required": True}},
        {"name": "Data Privacy Policy", "description": "Student data privacy and protection", "policy_type": "privacy", "status": "ACTIVE", "rules": {"encryption_required": True, "access_logging": True}}
    ]
    
    # First commit policies to get their IDs
    policy_ids = {}
    
    for policy_data in policies:
        try:
            existing = session.execute(
                text("SELECT id FROM security_policies WHERE name = :name"),
                {"name": policy_data["name"]}
            ).first()
            
            if not existing:
                result = session.execute(
                    text("""
                        INSERT INTO security_policies (name, description, policy_type, status, rules, created_at, updated_at)
                        VALUES (:name, :description, :policy_type, :status, :rules, :created_at, :updated_at)
                        RETURNING id
                    """),
                    {
                        **policy_data,
                        "rules": json.dumps(policy_data["rules"]),
                        "created_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                )
                policy_id = result.fetchone()[0]
                policy_ids[policy_data["name"]] = policy_id
            else:
                policy_ids[policy_data["name"]] = existing[0]
        except Exception as e:
            print(f"Warning: Could not seed security policy {policy_data['name']}: {e}")
    
    # Commit policies first
    try:
        session.commit()
        print(f"✅ Created {len(policy_ids)} security policies")
    except Exception as e:
        print(f"Warning: Could not commit policies: {e}")
        return  # Exit early if policies couldn't be committed
    
    # Seed security rules using policy IDs from above
    rules = [
        {"name": "Student Data Access", "description": "Only authorized staff can access student data", "policy_name": "Data Access Policy", "rule_type": "access_control", "severity": "high", "conditions": {"role_required": "staff", "data_type": "student"}},
        {"name": "API Rate Limiting", "description": "API requests are rate limited", "policy_name": "API Security Policy", "rule_type": "rate_limiting", "severity": "medium", "conditions": {"max_requests": 100, "time_window": "1_minute"}},
        {"name": "Audit Trail", "description": "All access must be logged", "policy_name": "Audit Logging Policy", "rule_type": "logging", "severity": "high", "conditions": {"log_level": "all", "retention": "365_days"}},
        {"name": "Incident Reporting", "description": "Security incidents must be reported within 1 hour", "policy_name": "Incident Response Policy", "rule_type": "incident_response", "severity": "critical", "conditions": {"response_time": "1_hour", "escalation": "required"}},
        {"name": "Data Encryption", "description": "All sensitive data must be encrypted", "policy_name": "Data Privacy Policy", "rule_type": "encryption", "severity": "high", "conditions": {"algorithm": "AES256", "key_rotation": "90_days"}}
    ]
    
    for rule_data in rules:
        try:
            # Get policy_id from policy_name
            policy_name = rule_data.pop("policy_name")
            if policy_name not in policy_ids:
                print(f"Warning: Policy '{policy_name}' not found, skipping rule '{rule_data['name']}'")
                continue
            policy_id = policy_ids[policy_name]
            
            existing = session.execute(
                text("SELECT id FROM security_rules WHERE name = :name"),
                {"name": rule_data["name"]}
            ).first()
            
            if not existing:
                session.execute(
                    text("""
                        INSERT INTO security_rules (name, description, policy_id, rule_type, severity, conditions, actions, status, created_at, updated_at)
                        VALUES (:name, :description, :policy_id, :rule_type, :severity, :conditions, :actions, :status, :created_at, :updated_at)
                    """),
                    {
                        **rule_data,
                        "policy_id": policy_id,
                        "conditions": json.dumps(rule_data["conditions"]),
                        "actions": json.dumps({"action": "block", "notify": True, "log": True}),
                        "status": "ACTIVE",
                        "created_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                )
        except Exception as e:
            print(f"Warning: Could not seed security rule {rule_data['name']}: {e}")
    
    # Seed access control roles
    roles = [
        {"name": "Super Admin", "description": "Full system access"},
        {"name": "PE Administrator", "description": "PE department administration"},
        {"name": "Teacher", "description": "Class and student management"},
        {"name": "Safety Officer", "description": "Safety and compliance access"},
        {"name": "Student", "description": "Limited student access"},
        {"name": "Guest", "description": "Read-only public access"}
    ]
    
    for role_data in roles:
        try:
            existing = session.execute(
                text("SELECT id FROM access_control_roles WHERE name = :name"),
                {"name": role_data["name"]}
            ).first()
            
            if not existing:
                session.execute(
                    text("""
                        INSERT INTO access_control_roles (name, description, created_at, updated_at, status)
                        VALUES (:name, :description, :created_at, :updated_at, :status)
                    """),
                    {
                        "name": role_data["name"],
                        "description": role_data["description"],
                        "created_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow(),
                        "status": "ACTIVE"
                    }
                )
        except Exception as e:
            print(f"Warning: Could not seed access control role {role_data['name']}: {e}")
    
    # Seed access control permissions
    permissions = [
        {"name": "read_student_data", "description": "Read student information", "resource_type": "student", "action": "read", "permission_type": "data_access"},
        {"name": "write_student_data", "description": "Modify student information", "resource_type": "student", "action": "write", "permission_type": "data_modification"},
        {"name": "read_class_data", "description": "Read class information", "resource_type": "class", "action": "read", "permission_type": "data_access"},
        {"name": "write_class_data", "description": "Modify class information", "resource_type": "class", "action": "write", "permission_type": "data_modification"},
        {"name": "read_safety_data", "description": "Read safety information", "resource_type": "safety", "action": "read", "permission_type": "data_access"},
        {"name": "write_safety_data", "description": "Modify safety information", "resource_type": "safety", "action": "write", "permission_type": "data_modification"},
        {"name": "admin_system", "description": "Full system administration", "resource_type": "system", "action": "admin", "permission_type": "system_control"},
        {"name": "audit_logs", "description": "Access audit logs", "resource_type": "audit", "action": "read", "permission_type": "data_access"}
    ]
    
    for perm_data in permissions:
        try:
            existing = session.execute(
                text("SELECT id FROM access_control_permissions WHERE name = :name"),
                {"name": perm_data["name"]}
            ).first()
            
            if not existing:
                session.execute(
                    text("""
                        INSERT INTO access_control_permissions (name, description, resource_type, action, permission_type, status, created_at, updated_at)
                        VALUES (:name, :description, :resource_type, :action, :permission_type, :status, :created_at, :updated_at)
                    """),
                    {
                        "name": perm_data["name"],
                        "description": perm_data["description"],
                        "resource_type": perm_data["resource_type"],
                        "action": perm_data["action"],
                        "permission_type": perm_data["permission_type"],
                        "status": "ACTIVE",
                        "created_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                )
        except Exception as e:
            print(f"Warning: Could not seed access control permission {perm_data['name']}: {e}")
    
    # Seed role permissions
    try:
        # Get role and permission IDs
        role_ids = session.execute(text("SELECT id FROM access_control_roles LIMIT 6")).fetchall()
        permission_ids = session.execute(text("SELECT id FROM access_control_permissions LIMIT 8")).fetchall()
        
        # Super Admin gets all permissions
        if role_ids and permission_ids:
            super_admin_id = role_ids[0][0]  # First role should be Super Admin
            
            for perm_id in permission_ids:
                session.execute(
                    text("""
                        INSERT INTO access_control_role_permissions (role_id, permission_id, created_at, updated_at, status)
                        VALUES (:role_id, :permission_id, :created_at, :updated_at, :status)
                    """),
                    {
                        "role_id": super_admin_id,
                        "permission_id": perm_id[0],
                        "created_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow(),
                        "status": "ACTIVE"
                    }
                )
            
            # PE Administrator gets most permissions
            pe_admin_id = role_ids[1][0] if len(role_ids) > 1 else super_admin_id
            for perm_id in permission_ids[:6]:  # All except admin_system and audit_logs
                session.execute(
                    text("""
                        INSERT INTO access_control_role_permissions (role_id, permission_id, created_at, updated_at, status)
                        VALUES (:role_id, :permission_id, :created_at, :updated_at, :status)
                    """),
                    {
                        "role_id": pe_admin_id,
                        "permission_id": perm_id[0],
                        "created_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow(),
                        "status": "ACTIVE"
                    }
                )
            
            # Teacher gets basic permissions
            teacher_id = role_ids[2][0] if len(role_ids) > 2 else super_admin_id
            for perm_id in permission_ids[:4]:  # Read/write student and class data
                session.execute(
                    text("""
                        INSERT INTO access_control_role_permissions (role_id, permission_id, created_at, updated_at, status)
                        VALUES (:role_id, :permission_id, :created_at, :updated_at, :status)
                    """),
                    {
                        "role_id": teacher_id,
                        "permission_id": perm_id[0],
                        "created_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow(),
                        "status": "ACTIVE"
                    }
                )
                
    except Exception as e:
        print(f"Warning: Could not seed role permissions: {e}")
    
    # Seed user roles
    try:
        # Get existing user IDs and role IDs
        user_ids = session.execute(text("SELECT id FROM users LIMIT 3")).fetchall()
        role_ids = session.execute(text("SELECT id FROM access_control_roles LIMIT 3")).fetchall()
        
        for i, user_id in enumerate(user_ids):
            role_id = role_ids[i % len(role_ids)][0] if role_ids else 1
            
            existing = session.execute(
                text("SELECT id FROM access_control_user_roles WHERE user_id = :user_id"),
                {"user_id": user_id[0]}
            ).first()
            
            if not existing:
                session.execute(
                    text("""
                        INSERT INTO access_control_user_roles (user_id, role_id, created_at, updated_at, status)
                        VALUES (:user_id, :role_id, :created_at, :updated_at, :status)
                    """),
                    {
                        "user_id": user_id[0],
                        "role_id": role_id,
                        "created_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow(),
                        "status": "ACTIVE"
                    }
                )
    except Exception as e:
        print(f"Warning: Could not seed user roles: {e}")
    
    # Seed API keys
    api_keys = [
        {"name": "PE System API", "key": "demo_key_1", "permissions": ["read_student_data", "read_class_data"], "description": "API key for PE system access"},
        {"name": "Safety Monitor API", "key": "demo_key_2", "permissions": ["read_safety_data", "write_safety_data"], "description": "API key for safety monitoring"},
        {"name": "Analytics API", "key": "demo_key_3", "permissions": ["read_student_data", "read_class_data"], "description": "API key for analytics access"}
    ]
    
    # Get a user ID for the API keys
    user_ids = session.execute(text("SELECT id FROM users LIMIT 1")).fetchall()
    
    if user_ids:
        user_id = user_ids[0][0]
        
        for key_data in api_keys:
            try:
                existing = session.execute(
                    text("SELECT id FROM api_keys WHERE name = :name"),
                    {"name": key_data["name"]}
                ).first()
                
                if not existing:
                    session.execute(
                        text("""
                            INSERT INTO api_keys (name, key, description, user_id, permissions, is_active, source, created_at)
                            VALUES (:name, :key, :description, :user_id, :permissions, :is_active, :source, :created_at)
                        """),
                        {
                            "name": key_data["name"],
                            "key": key_data["key"],
                            "description": key_data["description"],
                            "user_id": user_id,
                            "permissions": json.dumps(key_data["permissions"]),
                            "is_active": True,
                            "source": "OTHER",
                            "created_at": datetime.utcnow()
                        }
                    )
            except Exception as e:
                print(f"Warning: Could not seed API key {key_data['name']}: {e}")
    else:
        print("Warning: No users found for API key seeding")
    
    # Seed security audit logs
    audit_events = [
        {"action": "user_login", "user_id": 1, "resource_type": "user", "resource_id": 1, "details": {"message": "Successful login", "ip_address": "192.168.1.100"}},
        {"action": "data_access", "user_id": 1, "resource_type": "student", "resource_id": 1, "details": {"message": "Accessed student records", "ip_address": "192.168.1.100"}},
        {"action": "permission_change", "user_id": 1, "resource_type": "user", "resource_id": 1, "details": {"message": "Modified user permissions", "ip_address": "192.168.1.100"}},
        {"action": "api_request", "user_id": 2, "resource_type": "api", "resource_id": 1, "details": {"message": "API call to student endpoint", "ip_address": "192.168.1.101"}},
        {"action": "security_alert", "user_id": 1, "resource_type": "security", "resource_id": 1, "details": {"message": "Failed login attempt", "ip_address": "192.168.1.102"}}
    ]
    
    for event_data in audit_events:
        try:
            session.execute(
                text("""
                    INSERT INTO security_audit_logs (timestamp, action, resource_type, resource_id, user_id, details)
                    VALUES (:timestamp, :action, :resource_type, :resource_id, :user_id, :details)
                """),
                {
                    "timestamp": datetime.utcnow(),
                    "action": event_data["action"],
                    "resource_type": event_data["resource_type"],
                    "resource_id": event_data["resource_id"],
                    "user_id": event_data["user_id"],
                    "details": json.dumps(event_data["details"])
                }
            )
        except Exception as e:
            print(f"Warning: Could not seed security audit log: {e}")
    
    # Seed security incidents
    incidents = [
        {"incident_type": "failed_login", "severity": "low", "description": "Multiple failed login attempts", "status": "COMPLETED"},
        {"incident_type": "data_access", "severity": "medium", "description": "Unauthorized access attempt", "status": "PENDING"},
        {"incident_type": "api_abuse", "severity": "high", "description": "API rate limit exceeded", "status": "COMPLETED"}
    ]
    
    # Get some IDs for required foreign key fields
    policy_ids = session.execute(text("SELECT id FROM security_policies LIMIT 1")).fetchall()
    activity_ids = session.execute(text("SELECT id FROM activities LIMIT 1")).fetchall()
    student_ids = session.execute(text("SELECT id FROM students LIMIT 1")).fetchall()
    
    if policy_ids and activity_ids and student_ids:
        policy_id = policy_ids[0][0]
        activity_id = activity_ids[0][0]
        student_id = student_ids[0][0]
        
        for incident_data in incidents:
            try:
                existing = session.execute(
                    text("SELECT id FROM security_incidents WHERE incident_type = :incident_type AND description = :description"),
                    {"incident_type": incident_data["incident_type"], "description": incident_data["description"]}
                ).first()
                
                if not existing:
                    session.execute(
                        text("""
                            INSERT INTO security_incidents (policy_id, activity_id, student_id, incident_type, severity, description, status, created_at, updated_at)
                            VALUES (:policy_id, :activity_id, :student_id, :incident_type, :severity, :description, :status, :created_at, :updated_at)
                        """),
                        {
                            "policy_id": policy_id,
                            "activity_id": activity_id,
                            "student_id": student_id,
                            "incident_type": incident_data["incident_type"],
                            "severity": incident_data["severity"],
                            "description": incident_data["description"],
                            "status": incident_data["status"],
                            "created_at": datetime.utcnow(),
                            "updated_at": datetime.utcnow()
                        }
                    )
            except Exception as e:
                print(f"Warning: Could not seed security incident: {e}")
    else:
        print("Warning: No required foreign key references found for security incidents seeding")
    
    # Seed IP allowlist/blocklist
    allowlist_entries = [
        {"ip_address": "192.168.1.0/24", "description": "Internal network"},
        {"ip_address": "10.0.0.0/8", "description": "VPN network"}
    ]
    
    for entry in allowlist_entries:
        try:
            existing = session.execute(
                text("SELECT id FROM ip_allowlist WHERE ip_address = :ip_address"),
                {"ip_address": entry["ip_address"]}
            ).first()
            
            if not existing:
                session.execute(
                    text("""
                        INSERT INTO ip_allowlist (ip_address, description, created_at)
                        VALUES (:ip_address, :description, :created_at)
                    """),
                    {
                        **entry,
                        "created_at": datetime.utcnow()
                    }
                )
        except Exception as e:
            print(f"Warning: Could not seed IP allowlist entry: {e}")
    
    blocklist_entries = [
        {"ip_address": "203.0.113.1", "reason": "Suspicious activity"}
    ]
    
    for entry in blocklist_entries:
        try:
            existing = session.execute(
                text("SELECT id FROM ip_blocklist WHERE ip_address = :ip_address"),
                {"ip_address": entry["ip_address"]}
            ).first()
            
            if not existing:
                session.execute(
                    text("""
                        INSERT INTO ip_blocklist (ip_address, reason, created_at)
                        VALUES (:ip_address, :reason, :created_at)
                    """),
                    {
                        **entry,
                        "created_at": datetime.utcnow()
                    }
                )
        except Exception as e:
            print(f"Warning: Could not seed IP blocklist entry: {e}")
    
    # Seed rate limits
    rate_limits = [
        {"endpoint": "/api/v1/*", "method": "GET", "limit": 1000, "period": 3600},
        {"endpoint": "/auth/login", "method": "POST", "limit": 5, "period": 300},
        {"endpoint": "/api/v1/export", "method": "POST", "limit": 10, "period": 86400}
    ]
    
    for limit_data in rate_limits:
        try:
            existing = session.execute(
                text("SELECT id FROM rate_limits WHERE endpoint = :endpoint AND method = :method"),
                {"endpoint": limit_data["endpoint"], "method": limit_data["method"]}
            ).first()
            
            if not existing:
                session.execute(
                    text("""
                        INSERT INTO rate_limits (endpoint, method, "limit", period, is_active, created_at, updated_at)
                        VALUES (:endpoint, :method, :limit, :period, :is_active, :created_at, :updated_at)
                    """),
                    {
                        **limit_data,
                        "is_active": True,
                        "created_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                )
        except Exception as e:
            print(f"Warning: Could not seed rate limit {limit_data['endpoint']}: {e}")
    
    # Seed rate limit related tables
    seed_rate_limit_policies(session)
    seed_rate_limit_metrics(session)
    seed_rate_limit_logs(session)
    
    print("Security system seeded successfully!")

def seed_rate_limit_policies(session):
    """Seed rate limit policies"""
    print("  🔄 Seeding rate limit policies...")
    
    # Check if already has data
    result = session.execute(text("SELECT COUNT(*) FROM rate_limit_policies"))
    if result.scalar() > 0:
        print("    ✅ rate_limit_policies already has data")
        return
    
    # Get rate limit IDs
    rate_limits = session.execute(text("SELECT id FROM rate_limits")).fetchall()
    if not rate_limits:
        print("    ⚠️ No rate limits found, skipping rate_limit_policies")
        return
    
    policies = []
    for rate_limit_id, in rate_limits:
        policies.append({
            'rate_limit_id': rate_limit_id,
            'name': f'Policy for Rate Limit {rate_limit_id}',
            'description': f'Policy configuration for rate limit {rate_limit_id}',
            'trigger': 'THRESHOLD',
            'action': 'BLOCK_REQUEST',
            'parameters': '{"message": "Rate limit exceeded"}',
            'is_active': True,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        })
    
    # Insert rate limit policies
    for policy in policies:
        session.execute(text("""
            INSERT INTO rate_limit_policies (rate_limit_id, name, description, trigger, action, parameters, is_active, created_at, updated_at)
            VALUES (:rate_limit_id, :name, :description, :trigger, :action, :parameters, :is_active, :created_at, :updated_at)
        """), policy)
    
    print(f"    ✅ Created {len(policies)} rate limit policies")

def seed_rate_limit_metrics(session):
    """Seed rate limit metrics"""
    print("  🔄 Seeding rate limit metrics...")
    
    # Check if already has data
    result = session.execute(text("SELECT COUNT(*) FROM rate_limit_metrics"))
    if result.scalar() > 0:
        print("    ✅ rate_limit_metrics already has data")
        return
    
    # Get rate limit IDs
    rate_limits = session.execute(text("SELECT id FROM rate_limits")).fetchall()
    if not rate_limits:
        print("    ⚠️ No rate limits found, skipping rate_limit_metrics")
        return
    
    metrics = []
    for rate_limit_id, in rate_limits:
        for i in range(5):  # Create 5 metrics per rate limit
            metrics.append({
                'rate_limit_id': rate_limit_id,
                'window_start': datetime.utcnow(),
                'request_count': 0,
                'violation_count': 0,
                'average_latency': 150.0,
                'max_latency': 300.0,
                'burst_count': 0,
                'metrics_data': '{"status": "normal"}',
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            })
    
    # Insert rate limit metrics
    for metric in metrics:
        session.execute(text("""
            INSERT INTO rate_limit_metrics (rate_limit_id, window_start, request_count, violation_count, average_latency, max_latency, burst_count, metrics_data, created_at, updated_at)
            VALUES (:rate_limit_id, :window_start, :request_count, :violation_count, :average_latency, :max_latency, :burst_count, :metrics_data, :created_at, :updated_at)
        """), metric)
    
    print(f"    ✅ Created {len(metrics)} rate limit metrics")

def seed_rate_limit_logs(session):
    """Seed rate limit logs"""
    print("  🔄 Seeding rate limit logs...")
    
    # Check if already has data
    result = session.execute(text("SELECT COUNT(*) FROM rate_limit_logs"))
    if result.scalar() > 0:
        print("    ✅ rate_limit_logs already has data")
        return
    
    # Get rate limit IDs and API keys
    rate_limits = session.execute(text("SELECT id FROM rate_limits")).fetchall()
    api_keys = session.execute(text("SELECT id FROM api_keys LIMIT 3")).fetchall()
    
    if not rate_limits or not api_keys:
        print("    ⚠️ No rate limits or API keys found, skipping rate_limit_logs")
        return
    
    logs = []
    for rate_limit_id, in rate_limits:
        for api_key_id, in api_keys:
            for i in range(3):  # Create 3 logs per rate limit + API key combination
                logs.append({
                    'api_key_id': api_key_id,
                    'endpoint': f'/api/v1/test{i}',
                    'method': 'GET',
                    'timestamp': datetime.utcnow(),
                    'ip_address': f'192.168.1.{i+1}',
                    'user_agent': f'TestAgent/{i+1}',
                    'created_at': datetime.utcnow()
                })
    
    # Insert rate limit logs
    for log in logs:
        session.execute(text("""
            INSERT INTO rate_limit_logs (api_key_id, endpoint, method, timestamp, ip_address, user_agent, created_at)
            VALUES (:api_key_id, :endpoint, :method, :timestamp, :ip_address, :user_agent, :created_at)
        """), log)
    
    print(f"    ✅ Created {len(logs)} rate limit logs") 