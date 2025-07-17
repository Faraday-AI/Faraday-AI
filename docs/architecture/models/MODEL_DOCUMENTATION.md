# Faraday AI Model Documentation

## Table of Contents
1. [Model Architecture](#model-architecture)
2. [Database Schema](#database-schema)
3. [Standardization Status](#standardization-status)
4. [Migration Status](#migration-status)

## Model Architecture

### Base Classes
- Primary: `Base` from `app.db.base_class` (35 files)
- Secondary: `BaseModel` from `.base` (2 files)
- Mixins: `TimestampedMixin`, `BaseModelMixin`, `StatusMixin`, `MetadataMixin`

### Model Categories

#### 1. Core Models ✅
- `core_models.py` - Core model definitions and enums
- `base.py` - Base model classes
- `memory.py` - Memory-related models
- `action_type.py` - Action type definitions
- `api.py` - API-related models
- Status: Fully standardized

#### 2. Feature Models ✅
- curriculum.py
- safety.py
- assessment.py
- progress_tracking.py
- goal_setting.py
- Status: Fully standardized

#### 3. Supporting Models ✅
- health.py
- movement_analysis.py
- environmental.py
- competition.py
- injury_prevention.py
- load_balancer.py
- Status: Fully standardized

#### 4. Additional Categories
- Activity Adaptation Models 🔄
- Context Models 🔄
- Competition Models 🔄
- Movement Analysis Models 🔄
- Utils Models 🔄
- Resource Management Models 🔄
- Organization Models 🔄
- ML Models 🔄
- Health & Fitness Models 🔄
- GPT Models 🔄
- Feedback Models 🔄
- Environmental Models 🔄
- Dashboard Models 🔄
- Security Models 🔄
- Educational Models 🔄
- User Management Models 🔄
- System Models 🔄
- Skill Assessment Models 🔄
- Preference Models ✅

## Database Schema

### Core User System

#### `users`
- **Role**: Core user account management
- **Key Fields**:
  - `id` (UUID, primary key)
  - `email` (unique, indexed)
  - `password_hash`
  - `first_name`, `last_name`
  - `is_teacher`, `is_active`
  - `school`, `department`
  - `subjects`, `grade_levels` (JSONB)
  - Timestamps: `created_at`, `updated_at`, `last_login`
- **Relationships**:
  - → `user_management_preferences` (one-to-one)
  - → `user_memories` (one-to-many)
  - → `memory_interactions` (one-to-many)

### Preference Models

#### `user_management_preferences`
- **Role**: User-specific settings and preferences
- **Key Fields**:
  - `user_id` (UUID FK to users)
  - `theme`
  - `notifications` (JSON)
  - `language`
  - `timezone`
- **Relationships**:
  - → `users` (many-to-one)

#### `pe_activity_preferences`
- **Role**: Physical education activity preferences
- **Key Fields**:
  - `student_id` (FK)
  - `activity_id` (FK)
  - `preference_score` (Float)
  - `preference_level` (Integer)
  - `notes` (Text)
  - `metadata` (JSONB)
- **Relationships**:
  - → `students` (many-to-one)
  - → `activities` (many-to-one)

#### `adaptation_activity_preferences`
- **Role**: Activity adaptation preferences
- **Key Fields**:
  - `student_id` (FK)
  - `activity_type` (Enum)
  - `preference_score` (Float)
- **Relationships**:
  - → `students` (many-to-one)

#### `context_notification_preferences`
- **Role**: Notification settings
- **Key Fields**:
  - `user_id` (FK)
  - `channel` (Enum)
  - `type` (Enum)
  - `priority_threshold` (Enum)
  - `quiet_hours` (Time)
- **Relationships**:
  - → `users` (many-to-one)

#### `user_management_voice_preferences`
- **Role**: Voice settings
- **Key Fields**:
  - `user_id` (FK)
  - `avatar_id` (FK)
  - `voice_id` (String)
  - `language` (String)
  - `speed` (Integer)
  - `pitch` (Integer)
  - `provider` (Enum)
- **Relationships**:
  - → `users` (many-to-one)
  - → `avatars` (many-to-one)

#### `security_preferences`
- **Role**: Security settings
- **Key Fields**:
  - `user_id` (FK)
  - `data_sharing` (Boolean)
  - `analytics_opt_in` (Boolean)
  - `backup_settings` (JSONB)
- **Relationships**:
  - → `users` (many-to-one)

### Physical Education System

#### `activities`
- **Role**: Physical activities definition
- **Key Fields**:
  - `name` (1-100 chars, non-empty)
  - `description` (max 500 chars)
  - `activity_type` (Enum from core_models.py)
  - `difficulty` (Enum from core_models.py)
  - `equipment_required` (Enum from core_models.py)
  - `duration_minutes` (1-240 minutes)
  - `instructions`, `safety_guidelines`
  - `variations`, `benefits`
  - `activity_metadata` (JSON)
- **Relationships**:
  - → `routines` (many-to-many)
  - → `risk_assessments` (one-to-many)
  - → `safety_incidents` (one-to-many)
  - → `activity_performances` (one-to-many)
  - → `progressions` (one-to-many)
  - → `plan_activities` (one-to-many)
  - → `exercises` (one-to-many)
  - → `movement_analyses` (one-to-many)
  - → `skill_assessments` (one-to-many)
  - → `activity_adaptations` (one-to-many)
  - → `skill_progress` (one-to-many)
  - → `categories` (many-to-many)

## Standardization Status

### Completed Tasks ✅
1. Core Models Standardization
   - Consolidated enums in core_models.py
   - Updated import patterns
   - Standardized relationships
2. Feature Models Standardization
   - Updated to use core_models.py
   - Standardized relationships
3. Supporting Models Standardization
   - Updated to use core_models.py
   - Standardized relationships
4. Preference Models Table Naming
   - Standardized all preference model names
   - Updated relationships

### In Progress Tasks 🔄
1. Activity Adaptation Models
   - [ ] Review model inheritance
   - [ ] Update import patterns
   - [ ] Standardize relationships

2. Context Models
   - [ ] Review model inheritance
   - [ ] Update import patterns
   - [ ] Standardize relationships

3. Competition Models
   - [ ] Review model inheritance
   - [ ] Update import patterns
   - [ ] Standardize relationships

4. Movement Analysis Models
   - [ ] Review model inheritance
   - [ ] Update import patterns
   - [ ] Standardize relationships

5. Utils Models
   - [ ] Review model inheritance
   - [ ] Update import patterns
   - [ ] Standardize relationships

6. Resource Management Models
   - [ ] Review model inheritance
   - [ ] Update import patterns
   - [ ] Standardize relationships

7. Organization Models
   - [ ] Review model inheritance
   - [ ] Update import patterns
   - [ ] Standardize relationships

8. ML Models
   - [ ] Review model inheritance
   - [ ] Update import patterns
   - [ ] Standardize relationships

9. Health & Fitness Models
   - [ ] Review model inheritance
   - [ ] Update import patterns
   - [ ] Standardize relationships

10. GPT Models
    - [ ] Review model inheritance
    - [ ] Update import patterns
    - [ ] Standardize relationships

11. Feedback Models
    - [ ] Review model inheritance
    - [ ] Update import patterns
    - [ ] Standardize relationships

12. Environmental Models
    - [ ] Review model inheritance
    - [ ] Update import patterns
    - [ ] Standardize relationships

13. Dashboard Models
    - [ ] Review widget inheritance patterns
    - [ ] Standardize theme model relationships
    - [ ] Update filter model imports
    - [ ] Verify sharing model constraints

14. Security Models
    - [ ] Review access control inheritance
    - [ ] Standardize policy model relationships
    - [ ] Update API key model imports
    - [ ] Verify session model constraints

15. Educational Models
    - [ ] Review base model inheritance
    - [ ] Standardize curriculum relationships
    - [ ] Update classroom model imports
    - [ ] Verify staff model constraints

16. User Management Models
    - [ ] Verify user model constraints

17. System Models
    - [ ] Review model inheritance
    - [ ] Update import patterns
    - [ ] Standardize relationships

18. Skill Assessment Models
    - [ ] Review model inheritance
    - [ ] Update import patterns
    - [ ] Standardize relationships

## Migration Status

### Completed Migrations ✅
1. Core Models Migration
   - Moved enums to core_models.py
   - Updated all imports
   - Verified relationships

2. Preference Models Table Renaming
   - `user_preferences` → `user_management_preferences`
   - `student_activity_preferences` → `pe_activity_preferences`
   - `activity_preferences` → `adaptation_activity_preferences`
   - `notification_preferences` → `context_notification_preferences`
   - `voice_preferences` → `user_management_voice_preferences`

### In Progress Migrations 🔄
1. Activity Adaptation Models
   - Review and standardize table names
   - Update relationships and constraints

2. Context Models
   - Review and standardize table names
   - Update relationships and constraints

3. Competition Models
   - Review and standardize table names
   - Update relationships and constraints

4. Movement Analysis Models
   - Review and standardize table names
   - Update relationships and constraints

5. Utils Models
   - Review and standardize table names
   - Update relationships and constraints

6. Resource Management Models
   - Review and standardize table names
   - Update relationships and constraints

7. Organization Models
   - Review and standardize table names
   - Update relationships and constraints

8. ML Models
   - Review and standardize table names
   - Update relationships and constraints

9. Health & Fitness Models
   - Review and standardize table names
   - Update relationships and constraints

10. GPT Models
    - Review and standardize table names
    - Update relationships and constraints

11. Feedback Models
    - Review and standardize table names
    - Update relationships and constraints

12. Environmental Models
    - Review and standardize table names
    - Update relationships and constraints

13. Dashboard Models
    - Review and standardize table names
    - Update relationships and constraints

14. Security Models
    - Review and standardize table names
    - Update relationships and constraints

15. Educational Models
    - Review and standardize table names
    - Update relationships and constraints

16. User Management Models
    - Review and standardize table names
    - Update relationships and constraints

17. System Models
    - Review and standardize table names
    - Update relationships and constraints

18. Skill Assessment Models
    - Review and standardize table names
    - Update relationships and constraints

### Migration Process
1. Planning Phase
   - Review current table names and relationships
   - Document all required changes
   - Create migration scripts
   - Test migrations in development environment

2. Implementation Phase
   - Execute migrations in order
   - Update model references
   - Update service layer code
   - Update API endpoints

3. Testing Phase
   - Verify data integrity
   - Test all affected functionality
   - Validate relationships
   - Check performance impact

4. Deployment Phase
   - Schedule maintenance window
   - Execute migrations
   - Monitor system health
   - Rollback plan if needed

## Best Practices

### Naming Conventions
1. Table Names
   - Use domain prefix (e.g., `pe_`, `user_management_`)
   - Use plural form
   - Use snake_case

2. Field Names
   - Use snake_case
   - Be descriptive and clear
   - Use consistent patterns

### Relationships
1. Foreign Keys
   - Name: `{table_name}_id`
   - Type: UUID or Integer
   - Include appropriate constraints

2. Many-to-Many
   - Use junction tables
   - Name: `{table1}_{table2}`
   - Include timestamps

### Validation
1. Field Constraints
   - Use appropriate types
   - Set length limits
   - Add check constraints

2. Data Integrity
   - Use foreign key constraints
   - Set cascade behavior
   - Add unique constraints

### Documentation
1. Model Documentation
   - Clear purpose statement
   - Field descriptions
   - Relationship documentation
   - Validation rules

2. Code Documentation
   - Type hints
   - Docstrings
   - Usage examples

## Current Priorities

### Build Status
1. Core Models ✅
   - Fully standardized
   - Ready for build

2. Feature Models ✅
   - Fully standardized
   - Ready for build

3. Supporting Models ✅
   - Fully standardized
   - Ready for build

4. Preference Models ✅
   - Table names standardized
   - Ready for build

### Next Steps
1. Complete remaining model migrations
2. Implement comprehensive testing
3. Set up performance monitoring
4. Update documentation
5. Clean up deprecated files

### Build Process
1. Development Environment
   - Set up local development environment
   - Configure database connections
   - Install dependencies
   - Run initial migrations

2. Testing Environment
   - Set up test database
   - Configure test environment
   - Run test suite
   - Verify model relationships

3. Production Environment
   - Configure production database
   - Set up monitoring
   - Deploy application
   - Verify system health 