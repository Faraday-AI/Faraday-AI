# Migration Guide for Existing Users

## Overview
This guide helps existing users migrate to the new version of the Faraday AI Dashboard, which includes AI Suite management, marketplace functionality, and organization management features.

## Pre-Migration Checklist

### 1. Backup Current Data
```bash
# Backup PostgreSQL database
pg_dump faraday_db > faraday_backup.sql

# Backup Redis cache
redis-cli save

# Backup configuration files
cp config/* config_backup/
```

### 2. Version Compatibility Check
- Python version: 3.8+
- PostgreSQL version: 12+
- Redis version: 6+
- FastAPI version: 0.68+

### 3. System Requirements
- Additional disk space: 1GB minimum
- RAM: 4GB minimum
- CPU: 2 cores minimum

## Migration Steps

### 1. User Data Migration (COMPLETED)

#### Migrate Existing Users to New Schema
```python
async def migrate_user_data():
    """Migrate existing users to new schema."""
    users = await db.execute(select(User))
    for user in users:
        # Add new required fields
        user.user_type = UserType.STUDENT  # Default value
        user.billing_tier = BillingTier.FREE  # Default value
        user.credits_balance = 0.0  # Initial balance
        user.is_active = True
        
        # Create default AI suite
        suite = await setup_user_ai_suite(
            user_id=user.id,
            suite_name=f"{user.email}'s Suite"
        )
        
        # Migrate existing GPT subscriptions to tools
        await migrate_user_gpts(user.id, suite.id)
    
    await db.commit()
```

#### Migrate Existing GPT Subscriptions (COMPLETED)
```python
async def migrate_user_gpts(user_id: str, suite_id: str):
    """Migrate existing GPT subscriptions to AI tools."""
    subscriptions = await db.execute(
        select(GPTSubscription).where(GPTSubscription.user_id == user_id)
    )
    
    for sub in subscriptions:
        # Create new AI tool
        tool = await add_tool_to_suite(
            suite_id=suite_id,
            tool_data=AIToolCreate(
                name=sub.gpt_id,
                tool_type="gpt",
                configuration=sub.preferences,
                pricing_tier=BillingTier.FREE
            )
        )
        
        # Create tool assignment
        await assign_tool(
            tool_id=tool.id,
            user_id=user_id,
            assigned_by="system",
            permissions={"full_access": True}
        )
```

### 2. Project Migration (COMPLETED)

#### Migrate Project Data
```python
async def migrate_project_data():
    """Migrate existing projects to new schema."""
    projects = await db.execute(select(Project))
    for project in projects:
        # Update project with new fields
        project.is_template = False
        
        # Migrate project GPTs to tools
        await migrate_project_gpts(project.id)
    
    await db.commit()
```

#### Handle Project GPT Migration (COMPLETED)
```python
async def migrate_project_gpts(project_id: str):
    """Migrate project GPTs to AI tools."""
    project = await db.get(Project, project_id)
    if project.active_gpt_id:
        # Create tool for active GPT
        tool = await create_project_tool(
            project_id=project_id,
            gpt_id=project.active_gpt_id
        )
        project.active_gpt_id = tool.id
```

### 3. Organization Setup (COMPLETED)

#### Create Default Organization
```python
async def setup_default_organization():
    """Create default organization for existing users."""
    org = await create_organization(
        OrganizationCreate(
            name="Default Organization",
            type="education",
            subscription_tier=BillingTier.FREE,
            settings={}
        )
    )
    
    # Create default department
    dept = await add_department(
        org_id=org.id,
        dept_data=DepartmentCreate(
            name="General",
            description="Default department"
        )
    )
    
    return org, dept
```

#### Assign Users to Organization (COMPLETED)
```python
async def assign_users_to_organization(org_id: str, dept_id: str):
    """Assign existing users to default organization."""
    users = await db.execute(select(User))
    for user in users:
        user.organization_id = org_id
        user.department_id = dept_id
    
    await db.commit()
```

### 4. Data Verification (COMPLETED)

#### Verify Migration Success
```python
async def verify_migration():
    """Verify successful migration of all data."""
    # Check user migration
    users = await db.execute(select(User))
    for user in users:
        assert user.user_type is not None
        assert user.billing_tier is not None
        assert user.credits_balance is not None
        
        # Verify AI suite
        suite = await db.execute(
            select(AISuite).where(AISuite.user_id == user.id)
        )
        assert suite is not None
        
        # Verify tool assignments
        assignments = await db.execute(
            select(ToolAssignment).where(ToolAssignment.user_id == user.id)
        )
        assert len(assignments) > 0
```

### 5. Post-Migration Tasks (COMPLETED)

#### Initialize Credits System
```python
async def initialize_credits():
    """Initialize credits for existing users."""
    users = await db.execute(select(User))
    for user in users:
        # Add initial credits based on user type
        initial_credits = {
            UserType.STUDENT: 100.0,
            UserType.TEACHER: 500.0,
            UserType.ADMIN: 1000.0
        }.get(user.user_type, 100.0)
        
        await manage_credits(user.id, initial_credits, "add")
```

#### Setup Usage Tracking (COMPLETED)
```python
async def setup_usage_tracking():
    """Initialize usage tracking for existing tools."""
    tools = await db.execute(select(AITool))
    for tool in tools:
        # Create initial usage log
        await log_tool_usage(
            tool.user_id,
            tool.id,
            "migration",
            0.0  # No credits charged for migration
        )
```

## Rollback Procedure

### 1. Database Rollback
```bash
# Restore PostgreSQL backup
psql faraday_db < faraday_backup.sql

# Restore Redis backup
redis-cli flushall
redis-cli restore dump.rdb
```

### 2. Code Rollback
```python
async def rollback_changes():
    """Rollback migration changes if needed."""
    # Drop new tables
    await db.execute(text("DROP TABLE IF EXISTS tool_assignments CASCADE"))
    await db.execute(text("DROP TABLE IF EXISTS ai_tools CASCADE"))
    await db.execute(text("DROP TABLE IF EXISTS ai_suites CASCADE"))
    
    # Remove new columns
    await db.execute(text("ALTER TABLE users DROP COLUMN IF EXISTS user_type"))
    await db.execute(text("ALTER TABLE users DROP COLUMN IF EXISTS billing_tier"))
    # ... additional column removals
```

## Troubleshooting

### Common Migration Issues

1. **Missing User Data**
```python
async def fix_missing_user_data(user_id: str):
    """Fix missing user data after migration."""
    user = await db.get(User, user_id)
    if not user.user_type:
        user.user_type = UserType.STUDENT
    if not user.billing_tier:
        user.billing_tier = BillingTier.FREE
    await db.commit()
```

2. **Incomplete Tool Migration**
```python
async def fix_tool_migration(user_id: str):
    """Fix incomplete tool migration."""
    subscriptions = await get_user_subscriptions(user_id)
    suite = await get_user_suite(user_id)
    
    for sub in subscriptions:
        if not await has_tool_for_subscription(sub.id):
            await migrate_subscription_to_tool(sub, suite.id)
```

3. **Credits System Issues**
```python
async def fix_credits_system(user_id: str):
    """Fix credits system issues."""
    user = await db.get(User, user_id)
    logs = await get_credit_logs(user_id)
    
    expected_balance = calculate_expected_balance(logs)
    if user.credits_balance != expected_balance:
        user.credits_balance = expected_balance
        await db.commit()
```

## Post-Migration Verification

### 1. System Health Check
```python
async def verify_system_health():
    """Verify system health after migration."""
    # Check database connections
    assert await db.execute(text("SELECT 1")) is not None
    
    # Check Redis connection
    assert await redis.ping() is True
    
    # Verify API endpoints
    assert await test_api_endpoints() is True
```

### 2. Data Integrity Check
```python
async def verify_data_integrity():
    """Verify data integrity after migration."""
    # Check user data
    users = await db.execute(select(User))
    for user in users:
        assert user.user_type is not None
        assert user.billing_tier is not None
        assert await get_user_suite(user.id) is not None
        
    # Check tool assignments
    tools = await db.execute(select(AITool))
    for tool in tools:
        assert tool.pricing_tier is not None
        assert tool.credits_cost >= 0
```

### 3. Performance Check
```python
async def verify_performance():
    """Verify system performance after migration."""
    # Check response times
    response_times = await measure_api_response_times()
    assert max(response_times) < 1.0  # Max 1 second
    
    # Check database query performance
    query_times = await measure_query_performance()
    assert max(query_times) < 0.1  # Max 100ms
```

## Support and Feedback

For migration support or to report issues:
1. Open a support ticket
2. Join our Discord community
3. Email support@faraday.ai
4. Check our migration FAQ

## Next Steps

After successful migration:
1. Review new features documentation
2. Update API integrations
3. Train team members on new features
4. Monitor system performance
5. Collect user feedback

## Related Documentation

### Core Documentation
- [Database Documentation](/docs/context/database.md)
  - Database schema
  - Data structures
  - Implementation details
  - Migration procedures

- [Activity System](/docs/activity_system.md)
  - System features
  - Implementation details
  - Integration points
  - Migration impact

### Implementation Details
- [Educational Features Implementation](/docs/guides/educational-features-implementation.md)
  - Feature updates
  - Implementation changes
  - Migration considerations
  - Best practices

- [New Features Implementation Guide](/docs/guides/new-features-implementation-guide.md)
  - Feature rollout
  - Implementation steps
  - Migration procedures
  - Best practices

### Development Resources
- [Dashboard Integration Context](/docs/context/dashboard-ai-integration-context.md)
  - System architecture
  - Integration details
  - Migration impact
  - Success metrics

- [Database Seed Data Content](/docs/context/database_seed_data_content.md)
  - Data content
  - Migration procedures
  - Implementation status
  - Table structure

### Beta Program Documentation
- [Beta Documentation](/docs/beta/beta_documentation.md)
  - Technical details
  - Migration guides
  - API references
  - Integration steps

- [Monitoring Setup](/docs/beta/monitoring_feedback_setup.md)
  - System monitoring
  - Performance tracking
  - Migration metrics
  - Alert systems 