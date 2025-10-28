# Database Troubleshooting Guide

## Quick Diagnostics

### 1. Database Health Check
```bash
# Run comprehensive health check
docker-compose exec app python3 /app/app/scripts/monitor_performance.py

# Check specific issues
docker-compose exec app python3 /app/app/scripts/health_check.py
```

### 2. Performance Analysis
```bash
# Analyze query performance
docker-compose exec app python3 /app/app/scripts/analyze_performance.py

# Test application queries
docker-compose exec app python3 /app/app/scripts/test_application_queries.py
```

## Common Issues & Solutions

### Connection Issues

#### Problem: Cannot connect to database
**Symptoms:**
- Connection timeout errors
- "Connection refused" messages
- Application fails to start

**Solutions:**
1. Check Azure PostgreSQL status
2. Verify connection string in environment variables
3. Check firewall rules and IP whitelist
4. Verify SSL certificate

```bash
# Test connection
docker-compose exec app python3 -c "
from app.core.database import SessionLocal
session = SessionLocal()
result = session.execute(text('SELECT 1')).scalar()
print('Connection successful:', result)
session.close()
"
```

#### Problem: Too many connections
**Symptoms:**
- "Too many connections" error
- Application becomes unresponsive
- Database locks up

**Solutions:**
1. Check connection pool settings
2. Monitor active connections
3. Kill idle connections
4. Increase connection limit

```sql
-- Check active connections
SELECT count(*) FROM pg_stat_activity;

-- Kill idle connections
SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity 
WHERE state = 'idle' AND query_start < NOW() - INTERVAL '1 hour';
```

### Performance Issues

#### Problem: Slow queries
**Symptoms:**
- Queries take > 1 second
- Application feels sluggish
- High CPU usage

**Solutions:**
1. Check index usage
2. Analyze query execution plans
3. Add missing indexes
4. Optimize query structure

```sql
-- Check slow queries
SELECT query, mean_exec_time, calls
FROM pg_stat_statements 
WHERE mean_exec_time > 1000
ORDER BY mean_exec_time DESC;

-- Analyze query plan
EXPLAIN ANALYZE SELECT * FROM students WHERE school_id = 1;
```

#### Problem: High database size
**Symptoms:**
- Database size > 1GB
- Slow backup operations
- Storage warnings

**Solutions:**
1. Run data archiving
2. Clean up old data
3. Optimize table storage
4. Consider partitioning

```bash
# Check database size
docker-compose exec app python3 -c "
from app.core.database import SessionLocal
from sqlalchemy import text
session = SessionLocal()
size = session.execute(text('SELECT pg_size_pretty(pg_database_size(current_database()))')).scalar()
print('Database size:', size)
session.close()
"

# Run archiving
docker-compose exec app python3 /app/app/scripts/archive_data.py --live
```

### Data Issues

#### Problem: Missing or corrupted data
**Symptoms:**
- Validation errors
- Missing records
- Inconsistent data

**Solutions:**
1. Run data validation
2. Check for orphaned records
3. Verify foreign key constraints
4. Restore from backup if needed

```bash
# Run validation
docker-compose exec app python3 /app/app/scripts/seed_data/post_seed_validation.py

# Check for orphans
docker-compose exec app python3 /app/app/scripts/health_check.py
```

#### Problem: Duplicate records
**Symptoms:**
- Unique constraint violations
- Duplicate data in reports
- Inconsistent counts

**Solutions:**
1. Identify duplicates
2. Remove duplicates
3. Add unique constraints
4. Fix data entry process

```sql
-- Find duplicate students
SELECT first_name, last_name, school_id, COUNT(*)
FROM students
GROUP BY first_name, last_name, school_id
HAVING COUNT(*) > 1;

-- Remove duplicates (keep latest)
DELETE FROM students 
WHERE id NOT IN (
    SELECT MAX(id) 
    FROM students 
    GROUP BY first_name, last_name, school_id
);
```

### Index Issues

#### Problem: Missing indexes
**Symptoms:**
- Sequential scans on large tables
- Slow queries on indexed columns
- High CPU usage

**Solutions:**
1. Run performance analysis
2. Add recommended indexes
3. Monitor index usage
4. Remove unused indexes

```bash
# Run optimization
docker-compose exec app python3 /app/app/scripts/optimize_development_final.py

# Check index usage
docker-compose exec app python3 -c "
from app.core.database import SessionLocal
from sqlalchemy import text
session = SessionLocal()
result = session.execute(text('SELECT schemaname, relname, indexrelname, idx_scan FROM pg_stat_user_indexes WHERE idx_scan = 0')).fetchall()
for row in result:
    print(f'Unused index: {row.relname}.{row.indexrelname}')
session.close()
"
```

#### Problem: Index bloat
**Symptoms:**
- Large index sizes
- Slow index operations
- High disk usage

**Solutions:**
1. Rebuild indexes
2. Run VACUUM
3. Monitor index growth
4. Consider partial indexes

```sql
-- Rebuild specific index
REINDEX INDEX idx_students_grade_level;

-- Run VACUUM on table
VACUUM ANALYZE students;
```

## Monitoring & Alerts

### Key Metrics to Monitor

#### Database Size
- **Warning**: > 500MB
- **Critical**: > 1GB
- **Action**: Run archiving

#### Query Performance
- **Warning**: > 100ms average
- **Critical**: > 1s average
- **Action**: Add indexes, optimize queries

#### Connection Count
- **Warning**: > 50 connections
- **Critical**: > 80 connections
- **Action**: Check connection pooling

#### Dead Tuples
- **Warning**: > 10% dead tuples
- **Critical**: > 25% dead tuples
- **Action**: Run VACUUM

### Alert Scripts

#### Daily Health Check
```bash
#!/bin/bash
# Add to crontab: 0 9 * * * /path/to/daily_health_check.sh

cd "/Users/joemartucci/Projects/New Faraday Cursor/Faraday-AI"
./production_monitoring.sh

# Check for critical issues
if [ $? -ne 0 ]; then
    echo "Database health check failed" | mail -s "Database Alert" admin@faraday-ai.com
fi
```

#### Weekly Performance Review
```bash
#!/bin/bash
# Add to crontab: 0 10 * * 1 /path/to/weekly_performance.sh

cd "/Users/joemartucci/Projects/New Faraday Cursor/Faraday-AI"
docker-compose exec app python3 /app/app/scripts/analyze_performance.py
docker-compose exec app python3 /app/app/scripts/optimize_development_final.py
```

## Recovery Procedures

### Data Recovery

#### Point-in-Time Recovery
1. Access Azure PostgreSQL portal
2. Navigate to "Backup & Restore"
3. Select recovery point
4. Create new database from backup
5. Update connection string

#### Full Database Restore
1. Stop application
2. Drop existing database
3. Restore from backup
4. Run validation
5. Restart application

#### Partial Data Recovery
1. Identify affected tables
2. Export data from backup
3. Import to current database
4. Verify data integrity
5. Update application

### Performance Recovery

#### Emergency Performance Fix
```bash
# 1. Kill long-running queries
docker-compose exec app python3 -c "
from app.core.database import SessionLocal
from sqlalchemy import text
session = SessionLocal()
session.execute(text('SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = \'active\' AND query_start < NOW() - INTERVAL \'5 minutes\''))
session.close()
"

# 2. Run emergency optimization
docker-compose exec app python3 /app/app/scripts/optimize_development_final.py

# 3. Restart application
docker-compose restart app
```

## Prevention

### Best Practices

#### Regular Maintenance
- Run daily health checks
- Weekly performance analysis
- Monthly archiving
- Quarterly full review

#### Monitoring
- Set up alerts for key metrics
- Monitor query performance
- Track database growth
- Watch for errors

#### Documentation
- Keep troubleshooting logs
- Document solutions
- Update procedures
- Train team members

### Proactive Measures

#### Performance
- Regular index analysis
- Query optimization
- Capacity planning
- Load testing

#### Data Integrity
- Regular validation
- Constraint checking
- Backup verification
- Data quality monitoring

#### Security
- Regular security audits
- Access review
- Credential rotation
- Log monitoring

## Support Contacts

### Internal Support
- Database issues: Check logs and monitoring
- Performance problems: Run analysis scripts
- Data questions: Review validation reports

### External Support
- Azure PostgreSQL: Azure support portal
- Performance tuning: Database consultant
- Emergency recovery: 24/7 support team

### Escalation Procedures
1. **Level 1**: Check logs and run diagnostics
2. **Level 2**: Run troubleshooting scripts
3. **Level 3**: Contact Azure support
4. **Level 4**: Engage database specialist
