# Database Schema Documentation

## Table Relationships

### Core Entity Relationships

```
schools (1) ──→ (N) student_school_enrollments (N) ──→ (1) students
    │                                                      │
    │                                                      │
    └──→ (N) courses ──→ (N) course_enrollments ──→ (N) students
    │
    └──→ (N) teachers ──→ (N) teacher_school_assignments
```

### Performance & Analytics

```
students (1) ──→ (N) student_activity_performances (N) ──→ (1) activities
    │                                                           │
    │                                                           │
    └──→ (N) analytics_events                                   └──→ (N) activity_categories
    │
    └──→ (N) progress
    │
    └──→ (N) activity_logs
```

## Table Descriptions

### Student Management

#### `students`
Primary student information table.

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Primary key |
| first_name | VARCHAR(100) | Student first name |
| last_name | VARCHAR(100) | Student last name |
| grade_level | VARCHAR(10) | Grade level (K, 1st, 2nd, etc.) |
| school_id | INTEGER | Foreign key to schools |
| created_at | TIMESTAMP | Record creation time |
| updated_at | TIMESTAMP | Last update time |

**Indexes:**
- `idx_students_grade_level` ON (grade_level)
- `idx_prod_students_school_grade` ON (school_id, grade_level)

#### `schools`
School information and configuration.

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Primary key |
| name | VARCHAR(200) | School name |
| school_type | VARCHAR(50) | Elementary, Middle, High |
| address | TEXT | School address |
| created_at | TIMESTAMP | Record creation time |

#### `student_school_enrollments`
Student enrollment relationships.

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Primary key |
| student_id | INTEGER | Foreign key to students |
| school_id | INTEGER | Foreign key to schools |
| enrollment_date | DATE | Enrollment date |
| active | BOOLEAN | Active enrollment status |
| created_at | TIMESTAMP | Record creation time |

**Indexes:**
- `idx_enrollments_student_school` ON (student_id, school_id)
- `idx_prod_enrollments_active` ON (student_id, school_id) WHERE active = true

### Academic Data

#### `courses`
Course catalog and curriculum information.

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Primary key |
| course_code | VARCHAR(20) | Unique course code |
| title | VARCHAR(200) | Course title |
| description | TEXT | Course description |
| credits | DECIMAL(3,1) | Credit hours |
| school_id | INTEGER | Foreign key to schools |
| created_at | TIMESTAMP | Record creation time |

**Indexes:**
- `ux_courses_course_code` ON (course_code) UNIQUE

#### `course_enrollments`
Student course registrations.

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Primary key |
| student_id | INTEGER | Foreign key to students |
| course_id | INTEGER | Foreign key to courses |
| enrollment_date | DATE | Enrollment date |
| active | BOOLEAN | Active enrollment status |
| created_at | TIMESTAMP | Record creation time |

**Indexes:**
- `idx_course_enrollments_course_id` ON (course_id)
- `idx_course_enrollments_student_id` ON (student_id)
- `ux_course_enrollments_course_student` ON (course_id, student_id) UNIQUE

#### `progress`
Student academic progress tracking.

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Primary key |
| student_id | INTEGER | Foreign key to students |
| subject | VARCHAR(100) | Subject area |
| grade | VARCHAR(10) | Grade received |
| semester | VARCHAR(20) | Academic semester |
| created_at | TIMESTAMP | Record creation time |

**Indexes:**
- `idx_progress_date` ON (created_at)

### Performance & Analytics

#### `student_activity_performances`
Student performance data for activities.

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Primary key |
| student_id | INTEGER | Foreign key to students |
| activity_id | INTEGER | Foreign key to activities |
| score | DECIMAL(5,2) | Performance score |
| completion_time | INTEGER | Time to complete (seconds) |
| created_at | TIMESTAMP | Record creation time |

**Indexes:**
- `idx_performances_student_activity` ON (student_id, activity_id)
- `idx_performances_date` ON (created_at)
- `idx_prod_performances_composite` ON (student_id, activity_id, created_at)

#### `analytics_events`
User behavior and system events.

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Primary key |
| user_id | INTEGER | User identifier |
| event_type | VARCHAR(100) | Type of event |
| event_data | JSONB | Event-specific data |
| session_id | VARCHAR(100) | Session identifier |
| timestamp | TIMESTAMP | Event timestamp |
| source | VARCHAR(50) | Event source |
| version | VARCHAR(20) | Event version |

**Indexes:**
- `idx_analytics_events_user` ON (user_id)
- `idx_analytics_events_timestamp` ON (timestamp)
- `idx_prod_analytics_user_time` ON (user_id, timestamp)

#### `activity_logs`
System activity tracking.

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Primary key |
| action | VARCHAR(100) | Action performed |
| resource_type | VARCHAR(100) | Type of resource |
| resource_id | INTEGER | Resource identifier |
| user_id | INTEGER | User who performed action |
| org_id | INTEGER | Organization identifier |
| timestamp | TIMESTAMP | Action timestamp |
| created_at | TIMESTAMP | Record creation time |

**Indexes:**
- `idx_activity_logs_date` ON (created_at)
- `idx_prod_activity_logs_user_time` ON (user_id, created_at)

### Physical Education

#### `pe_lesson_plans`
PE-specific lesson plans.

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Primary key |
| title | VARCHAR(200) | Lesson plan title |
| description | TEXT | Lesson description |
| grade_level | VARCHAR(10) | Target grade level |
| duration | INTEGER | Duration in minutes |
| created_at | TIMESTAMP | Record creation time |

#### `pe_activity_preferences`
Student PE activity preferences.

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Primary key |
| student_id | INTEGER | Foreign key to students |
| activity_type | VARCHAR(100) | Type of activity |
| preference_score | INTEGER | Preference rating (1-10) |
| created_at | TIMESTAMP | Record creation time |

## Data Constraints

### Primary Keys
All tables have `id` as the primary key (SERIAL).

### Foreign Keys
- `students.school_id` → `schools.id`
- `student_school_enrollments.student_id` → `students.id`
- `student_school_enrollments.school_id` → `schools.id`
- `course_enrollments.student_id` → `students.id`
- `course_enrollments.course_id` → `courses.id`
- `progress.student_id` → `students.id`
- `student_activity_performances.student_id` → `students.id`

### Unique Constraints
- `courses.course_code` - Unique course codes
- `course_enrollments(course_id, student_id)` - One enrollment per student per course

### Check Constraints
- `progress.grade` - Valid grade values
- `student_activity_performances.score` - Score range validation
- `pe_activity_preferences.preference_score` - Rating range (1-10)

## Performance Considerations

### Table Sizes (Approximate)
- `students`: 3,714 rows
- `student_school_enrollments`: 3,714 rows
- `student_activity_performances`: 41,104 rows
- `analytics_events`: 4,960 rows
- `activity_logs`: 5,000 rows

### Index Usage
- **High-traffic tables**: Multiple indexes for common query patterns
- **Composite indexes**: For multi-column queries
- **Partial indexes**: For filtered queries (e.g., active enrollments)
- **Covering indexes**: For SELECT-only queries

### Query Optimization
- Use `EXPLAIN ANALYZE` for query analysis
- Monitor index usage with `pg_stat_user_indexes`
- Regular `VACUUM ANALYZE` for statistics updates
- Consider materialized views for complex aggregations

## Maintenance Procedures

### Daily
- Monitor database size and performance
- Check for long-running queries
- Verify backup status

### Weekly
- Run performance optimization
- Analyze query patterns
- Update statistics

### Monthly
- Archive old data
- Review index usage
- Performance tuning

### Quarterly
- Full database analysis
- Security review
- Capacity planning
