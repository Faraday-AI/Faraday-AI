# Faraday AI Database Documentation

## Overview

The Faraday AI database is a comprehensive PostgreSQL system designed for K-12 educational data management, featuring student tracking, performance analytics, and educational content management.

## Database Statistics

- **Total Tables**: 459
- **Total Records**: 391,271
- **Database Size**: ~163 MB
- **Students**: 3,714 across 6 schools
- **Performance Records**: 41,104
- **Analytics Events**: 4,960

## Architecture

### Core Tables

#### Student Management
- `students` - Student demographics and basic information
- `schools` - School information and configuration
- `student_school_enrollments` - Student enrollment relationships

#### Academic Data
- `courses` - Course catalog and curriculum
- `course_enrollments` - Student course registrations
- `lesson_plans` - Educational lesson plans
- `progress` - Student academic progress tracking

#### Performance & Analytics
- `student_activity_performances` - Student performance data
- `analytics_events` - User behavior and system events
- `activity_logs` - System activity tracking

#### Physical Education
- `pe_lesson_plans` - PE-specific lesson plans
- `pe_activity_preferences` - Student PE preferences
- `routine_performance_metrics` - PE performance tracking

## Performance Optimization

### Indexes Applied

#### High-Traffic Tables
- `idx_students_grade_level` - Student grade queries
- `idx_enrollments_student_school` - Enrollment lookups
- `idx_performances_student_activity` - Performance queries
- `idx_performances_date` - Performance date filtering

#### Analytics Tables
- `idx_analytics_events_user` - User analytics queries
- `idx_analytics_events_timestamp` - Time-based analytics
- `idx_activity_logs_date` - Activity log date filtering

#### Production Indexes
- `idx_prod_students_school_grade` - Composite school/grade queries
- `idx_prod_enrollments_active` - Active enrollment filtering
- `idx_prod_performances_composite` - Multi-column performance queries

### Query Performance

- **Average Query Time**: < 100ms
- **Index Usage**: 90%+ of queries use indexes
- **Connection Pooling**: Enabled for production
- **Query Caching**: Implemented for frequently accessed data

## Data Distribution

### School Distribution
- **Elementary Schools**: 4 schools (~387 students each)
- **Middle School**: 1 school (800 students)
- **High School**: 1 school (1,422 students)

### Grade Level Distribution
- **Elementary**: K-5 (1,548 students)
- **Middle**: 6-8 (800 students)
- **High**: 9-12 (1,422 students)

## Monitoring & Maintenance

### Daily Monitoring
```bash
# Run daily health check
./production_monitoring.sh

# Check performance metrics
docker-compose exec app python3 /app/app/scripts/monitor_performance.py
```

### Weekly Optimization
```bash
# Run development optimization
docker-compose exec app python3 /app/app/scripts/optimize_development_final.py

# Analyze performance patterns
docker-compose exec app python3 /app/app/scripts/analyze_performance.py
```

### Monthly Archiving
```bash
# Archive old data
./production_archiving.sh
```

## Backup & Recovery

### Azure PostgreSQL Backups
- **Automated Backups**: 7-day retention
- **Point-in-Time Recovery**: Available
- **Geo-Redundant Storage**: Enabled
- **Backup Frequency**: Continuous

### Recovery Procedures
1. **Point-in-Time Recovery**: Use Azure portal
2. **Full Database Restore**: Contact Azure support
3. **Data Export**: Use `pg_dump` for manual backups

## Security

### Access Control
- **Connection Encryption**: SSL/TLS required
- **Authentication**: Azure Active Directory
- **Authorization**: Role-based access control
- **Audit Logging**: All access logged

### Best Practices
- Use connection pooling
- Rotate credentials regularly
- Monitor failed login attempts
- Implement least-privilege access

## Development Workflow

### Seeding Process
```bash
# Full seed (all phases)
./run.sh --restart --no-cache

# Fast seed (CI/development)
./run_fast_seed_validation.sh

# Skip specific phases
SKIP_PHASE_4=true SKIP_PHASE_5=true ./run.sh
```

### Environment Variables
- `SKIP_PHASE_*` - Skip specific seeding phases
- `MAX_TOTAL_STUDENTS` - Limit student count for testing
- `SEED_RNG` - Set random seed for reproducible data
- `SKIP_DB_INIT` - Skip automatic table creation

## Troubleshooting

### Common Issues

#### Slow Queries
1. Check index usage: `EXPLAIN ANALYZE <query>`
2. Run performance analysis: `analyze_performance.py`
3. Add missing indexes based on recommendations

#### Connection Issues
1. Check Azure PostgreSQL status
2. Verify connection string
3. Check firewall rules
4. Monitor connection pool usage

#### Data Issues
1. Run validation: `post_seed_validation.py`
2. Check for orphaned records: `health_check.py`
3. Verify foreign key constraints

### Performance Tuning

#### Query Optimization
1. Use `EXPLAIN ANALYZE` to identify bottlenecks
2. Add indexes for frequently queried columns
3. Consider materialized views for complex aggregations
4. Use connection pooling for high concurrency

#### Database Maintenance
1. Run `VACUUM ANALYZE` regularly
2. Monitor table bloat and dead tuples
3. Archive old data to maintain performance
4. Update statistics after major data changes

## API Integration

### Power BI Connection
```
Server: faraday-ai-db.postgres.database.azure.com
Port: 5432
Database: postgres
SSL Mode: Require
```

### Recommended Settings
- Use DirectQuery for real-time data
- Enable query folding for performance
- Set connection timeout to 30 seconds
- Use connection pooling

### Key Tables for Reporting
- `students` - Demographics and enrollment
- `student_activity_performances` - Performance metrics
- `analytics_events` - User behavior analytics
- `schools` - Organizational structure
- `progress` - Academic progress tracking

## Support

### Documentation
- Database schema: `docs/database/schema.md`
- API documentation: `docs/api/`
- Troubleshooting guide: `docs/troubleshooting.md`

### Monitoring
- Grafana dashboard: http://localhost:3000
- Performance metrics: `monitor_performance.py`
- Health checks: `production_monitoring.sh`

### Contact
- Database issues: Check logs and monitoring
- Performance problems: Run analysis scripts
- Data questions: Review validation reports
