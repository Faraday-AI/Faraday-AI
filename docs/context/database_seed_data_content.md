# Database Seeding Documentation

## Quick Start Guide for AI Agents

### Current State
- All core tables are implemented and seeded ✅
- Performance tracking tables are implemented and seeded ✅
- Safety & Risk tables are fully implemented and seeded ✅
- Exercise tables are implemented and seeded ✅
- Movement Analysis tables are implemented and seeded ✅
- Activity Adaptation tables are implemented and seeded ✅
- Skill Assessment tables are implemented and seeded ✅
- Educational Feature tables are in implementation ⏳
- Dashboard Enhancement tables are implemented and seeded ✅
- Analytics & Monitoring tables are implemented and seeded ✅

### Recent Updates
1. **Enhanced Dashboard Tables**
   - Added real-time analytics tracking
   - Implemented performance monitoring
   - Added widget configuration storage
   - Enhanced user preference tracking
   - Implemented theme management

2. **Educational Features Implementation**
   - Added gradebook system tables
   - Implemented assignment tracking
   - Added parent-teacher communication
   - Implemented message board system
   - Enhanced security permissions

3. **Analytics Enhancement**
   - Added detailed metrics tracking
   - Implemented trend analysis storage
   - Enhanced performance monitoring
   - Added user behavior tracking
   - Implemented resource usage analytics

4. **Security Improvements**
   - Enhanced audit logging
   - Added detailed access tracking
   - Implemented advanced permission system
   - Added security metrics storage
   - Enhanced session management

2. **Table Structure Improvements**
   - Fixed activity category associations table naming
   - Added proper foreign key constraints
   - Implemented proper JSON schema for exercise instructions
   - Added skill assessment tables with proper structure

3. **Data Model Enhancements**
   - Updated Exercise model with complete field set
   - Added proper validation for exercise data
   - Implemented proper relationship mappings
   - Added skill assessment model with complete field set

### Immediate Next Steps
1. **Verify Current Setup**
   ```bash
   # Check current directory
   pwd  # Should be: /Users/joemartucci/Projects/New Faraday Cursor/Faraday-AI
   
   # Check running containers
   docker-compose ps
   ```

2. **Run Migrations**
   ```bash
   docker-compose run migrations
   ```
   - This will create all necessary tables
   - Check for any errors in the output

3. **Build and Start Services**
   ```bash
   ./run.sh
   ```
   - This will:
     - Build all containers
     - Start the services
     - Run the seed script automatically

4. **Verify Seeding**
   - Check console output for success messages
   - Each table should show "seeded successfully"
   - No foreign key constraint errors should appear

### Critical Rules to Follow
1. **Directory Structure**
   - ALL files must be in Faraday-AI directory
   - Never create files in workspace root
   - Never create nested files without permission

2. **Database Operations**
   - Always run migrations before seeding
   - Never remove services for compatibility issues
   - Always check foreign key constraints

3. **File Management**
   - Never create files without asking first
   - Never move files without asking first
   - Never edit files in wrong locations

4. **Dependencies**
   - Never remove packages without asking
   - Never replace large code sections without asking
   - Always verify compatibility

### Current Focus Areas
1. **Safety & Risk Management**
   - Implement remaining safety tables (safety_checks, equipment_checks, environmental_checks)
   - Create migrations for these tables
   - Add seed data

2. **Activity Planning**
   - Implement activity_plans and related tables
   - Create necessary migrations
   - Add seed data

### Common Issues to Watch For
1. **Foreign Key Constraints**
   - Always check table dependencies
   - Ensure parent tables are seeded first
   - Verify ID types match between related tables

2. **Migration Order**
   - Check migration chain in migrations/versions/
   - Ensure proper down_revision links
   - Verify no duplicate table creation

3. **Seeding Order**
   - Follow the order in seed_database.py
   - Ensure all dependencies are seeded first
   - Check for proper transaction commits

### When in Doubt
1. Check the Table Status section below for current implementation status
2. Review the Getting Started section for detailed setup instructions
3. Consult the Troubleshooting section for common issues and solutions

## Overview
This document describes the database seeding process for the Faraday-AI application. The seeding process populates the database with initial data required for the application to function properly.

## Directory Structure
The seeding scripts are located in:
```
Faraday-AI/app/scripts/seed_data/
```

Key files:
- `__main__.py` - Entry point for seeding
- `seed_database.py` - Main seeding orchestration
- `seed_activities.py` - Activity data seeding
- `seed_students.py` - Student data seeding
- `seed_classes.py` - Class data seeding
- `seed_class_students.py` - Class-Student relationship seeding
- `seed_exercises.py` - Exercise data seeding
- `seed_safety_incidents.py` - Safety incident data seeding
- `seed_safety_checks.py` - Safety check data seeding
- `seed_student_activity_data.py` - Student activity data seeding
- `seed_routines.py` - Routine data seeding
- `seed_risk_assessments.py` - Risk assessment data seeding
- `seed_performance_metrics.py` - Performance metric data seeding

## Seeding Order
The seeding process follows a specific order to handle dependencies correctly:

1. Activities (base data)
2. Students
3. Classes
4. Class Students (relationships)
5. Routines and Routine Activities
6. Exercises (depends on activities)
7. Risk Assessments
8. Routine Performances
9. Performance Metrics
10. Student Activity Performances and Preferences
11. Safety Incidents (depends on students and activities)
12. Safety Checks (depends on classes)
13. Student Activity Data (depends on students and activities)

## Data Content

### Activities
- Basic physical education activities
- Each activity has:
  - Name
  - Description
  - Category
  - Equipment needed
  - Safety considerations

### Students
- Sample student data for grades 5 and 6
- Each student has:
  - First name
  - Last name
  - Date of birth
  - Grade level
  - Medical conditions (if any)

### Classes
- Physical education classes for grades 5 and 6
- Each class has:
  - ID (integer)
  - Grade level
  - Section
  - Teacher name
  - Schedule information

### Class Students
- Relationships between classes and students
- Each relationship includes:
  - Class ID
  - Student ID
  - Enrollment date

### Routines
- Exercise routines and sequences
- Each routine includes:
  - Name
  - Description
  - Duration
  - Difficulty level
  - Associated activities

### Routine Activities
- Activities within routines
- Each record includes:
  - Routine ID
  - Activity ID
  - Order
  - Duration
  - Instructions

### Exercises
- Exercise routines based on activities
- Each exercise includes:
  - Activity reference
  - Duration
  - Intensity level
  - Instructions

### Risk Assessments
- Safety evaluations for activities
- Each assessment includes:
  - Activity ID
  - Risk level
  - Mitigation strategies
  - Assessment date

### Routine Performances
- Student performance in routines
- Each record includes:
  - Student ID
  - Routine ID
  - Performance metrics
  - Completion status
  - Date

### Performance Metrics
- Standardized performance measurements
- Each metric includes:
  - Name
  - Description
  - Unit of measurement
  - Target ranges

### Safety Incidents
- Records of safety-related incidents during activities
- Each incident includes:
  - Student ID
  - Activity ID
  - Incident type
  - Severity level
  - Description
  - Action taken
  - Metadata

### Safety Checks
- Regular safety inspections and checks
- Each check includes:
  - Class ID
  - Check type
  - Date
  - Results
  - Status
  - Metadata

### Student Activity Data
- Performance and preference data for students in activities
- Each record includes:
  - Student ID
  - Activity ID
  - Performance data (JSON)
  - Preferences (JSON)

### Environmental Checks
- Regular monitoring of environmental conditions
- Each check includes:
  - Class ID (integer)
  - Check date
  - Temperature (Celsius)
  - Humidity (Percentage)
  - Air Quality (AQI)
  - Surface Conditions (JSON)
  - Lighting (Lux)
  - Equipment Condition (JSON)
  - Environmental Metadata (JSON)
  - Created/Updated timestamps

### Movement Analysis
- ✅ `movement_analysis` - Stores movement analysis data (SEEDED)
  - Student movement data
  - Analysis results
  - Confidence scores
  - Timestamps
  - Movement metrics (smoothness, consistency, speed, range of motion)
  - Key points data
  - Recommendations

- ✅ `movement_patterns` - Records movement patterns (SEEDED)
  - Pattern type (jumping, running, throwing, catching)
  - Confidence score
  - Pattern data (sequence and metrics)
  - Duration (nullable)
  - Repetitions
  - Quality score
  - Notes
  - Created/Updated timestamps

### Activity Adaptation
- ✅ `activity_adaptations` - Stores activity adaptations (SEEDED)
  - Student-specific adaptations
  - Activity modifications
  - Difficulty adjustments
  - Adaptation types (intensity, duration, equipment, technique, progression)
  - Active status tracking
  - Start/End dates
  - Created/Updated timestamps

- ✅ `adaptation_history` - Tracks history of adaptations (SEEDED)
  - Change tracking
  - Previous and new states
  - Effectiveness scoring
  - Change reasons
  - Created timestamps

### Skill Assessment
- ✅ `skill_assessments` - Records skill assessments (SEEDED)
- ✅ `assessment_criteria` - Stores assessment criteria (SEEDED)
- ✅ `assessment_results` - Records assessment results (SEEDED)
- ✅ `assessment_history` - Tracks assessment history (SEEDED)
- ✅ `skill_progress` - Monitors skill progression (SEEDED)

### User & System
- ❌ `users` - Stores user information
- ❌ `user_preferences` - Stores user preferences
- ❌ `lessons` - Stores lesson information
- ❌ `user_memories` - Stores user memories
- ❌ `memory_interactions` - Tracks memory interactions
- ❌ `subject_categories` - Stores subject categories
- ❌ `assistant_profiles` - Stores assistant profiles
- ❌ `assistant_capabilities` - Stores assistant capabilities

### Implementation Notes
- ✅ = Table exists, migration created, and seeding implemented
- ❌ = Table not yet implemented
- All core tables, performance tracking tables, safety & risk tables, activity planning tables, movement analysis tables, and skill assessment tables are now fully functional and seeded with initial data
- Tables marked with ❌ are planned for future implementation 

## Important Notes

1. **ID Types**: 
   - Class IDs must be integers (not strings)
   - Example: `"id": 501` (correct) vs `"id": "501"` (incorrect)
   - Student IDs are integers
   - Activity IDs are integers
   - Routine IDs are integers
   - Risk Assessment IDs are integers

2. **Duplicate Execution**:
   - The seed script may run twice during startup
   - This is normal behavior and doesn't affect functionality
   - First run seeds the data
   - Second run attempts to seed but only prints messages (no duplicate data)

3. **Error Handling**:
   - Each seed file handles its own error cases
   - The main script (`seed_database.py`) provides overall error handling
   - Errors are printed to the console with stack traces

4. **Database Session**:
   - Uses async SQLAlchemy sessions
   - Commits changes after all seeding is complete
   - Rolls back on error

5. **Foreign Key Constraints**:
   - Safety incidents reference both students and activities
   - Safety checks reference classes
   - Student activity data references both students and activities
   - Routine activities reference both routines and activities
   - Risk assessments reference activities
   - Routine performances reference both students and routines
   - All foreign keys use CASCADE delete

## Running the Seeding Process

The seeding process is automatically triggered during application startup through:
1. `run.sh` script execution
2. Docker container initialization

Manual execution:
```bash
docker-compose exec app python -m app.scripts.seed_data.__main__
```

## Verification

To verify successful seeding:
1. Check console output for success messages
2. Verify data in the database
3. Access the application at `localhost:8000`
4. Check API endpoints for seeded data

## Troubleshooting

Common issues and solutions:

1. **Seeding Fails**:
   - Check database connection
   - Verify environment variables
   - Check for data type mismatches
   - Ensure foreign key constraints are satisfied

2. **Duplicate Data**:
   - Each seed file deletes existing records before inserting
   - If duplicates appear, check the delete-then-insert pattern

3. **Missing Data**:
   - Verify seeding order
   - Check foreign key constraints
   - Review error messages in console

4. **Foreign Key Violations**:
   - Ensure parent tables are seeded before child tables
   - Verify ID types match between related tables
   - Check for proper transaction commits

## Dependencies

The seeding process depends on:
- PostgreSQL database
- SQLAlchemy ORM
- Async database session
- Proper environment variables
- Docker container setup

## Related Files

- `docker-compose.yml` - Container configuration
- `Dockerfile` - Application container setup
- `run.sh` - Startup script
- Database models in `app/services/physical_education/models/` 

## Critical File Configurations

### Docker Configuration Files

#### docker-compose.yml
```yaml
services:
  app:
    build: .
    ports:
      - "${PORT:-8000}:${PORT:-8000}"
    environment:
      - DATABASE_URL=postgresql://faraday_admin:CodaMoeLuna31@faraday-ai-db.postgres.database.azure.com:5432/postgres?sslmode=require
      - REDIS_URL=redis://redis:${REDIS_PORT:-6379}/0
      - PYTHONPATH=/app
    volumes:
      - ./app:/app/app:delegated
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

#### Dockerfile
```dockerfile
# Build stage
FROM python:3.10.13-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    # ... other dependencies ...

# Create virtual environment
RUN python -m venv /opt/venv \
    && . /opt/venv/bin/activate \
    && pip install --no-cache-dir --timeout=1000 --retries=5 -r requirements.txt

# Create required directories
RUN mkdir -p /app/data /app/services/physical_education/models/movement_analysis /app/models /app/scripts

# Final stage
FROM python:3.10.13-slim

# Copy virtual environment
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set environment variables
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1

# Start the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Seed Script Files

#### __init__.py
```python
import os
import sys
from sqlalchemy.ext.asyncio import AsyncSession

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Import models and seed functions
from app.core.database import async_session
from app.services.physical_education.models import (
    Activity, Exercise, Student, Class, ClassStudent,
    SafetyIncident, SafetyCheck, StudentActivityData,
    Routine, RoutineActivity, RiskAssessment,
    RoutinePerformance, PerformanceMetric
)

# Import seed functions
from .seed_activities import seed_activities
from .seed_students import seed_students
from .seed_classes import seed_classes
from .seed_class_students import seed_class_students
from .seed_exercises import seed_exercises
from .seed_safety_incidents import seed_safety_incidents
from .seed_safety_checks import seed_safety_checks
from .seed_student_activity_data import seed_student_activity_data
from .seed_routines import seed_routines
from .seed_risk_assessments import seed_risk_assessments
from .seed_performance_metrics import seed_performance_metrics
from .seed_database import seed_database

__all__ = ['seed_database']
```

#### __main__.py
```python
from .seed_database import seed_database

if __name__ == "__main__":
    import asyncio
    asyncio.run(seed_database())
```

#### seed_database.py
```python
async def seed_database():
    """Main function to seed the database with initial data."""
    print("Running seed data script...")
    try:
        async with async_session() as session:
            # Seed activities first since other tables depend on it
            await seed_activities(session)
            
            # Seed students next
            await seed_students(session)
            
            # Seed classes
            await seed_classes(session)
            
            # Seed class_students
            await seed_class_students(session)
            
            # Seed routines and routine activities
            await seed_routines(session)
            
            # Seed exercises
            await seed_exercises(session)
            
            # Seed risk assessments
            await seed_risk_assessments(session)
            
            # Seed routine performances
            await seed_routine_performances(session)
            
            # Seed performance metrics
            await seed_performance_metrics(session)
            
            # Seed student activity performances and preferences
            await seed_student_activity_data(session)
            
            # Seed safety incidents
            await seed_safety_incidents(session)
            
            # Seed safety checks
            await seed_safety_checks(session)
            
            await session.commit()
            print("Database seeding completed successfully!")
    except Exception as e:
        print(f"Error in database session: {str(e)}")
        raise
```

### Critical Settings

1. **Database Connection**:
   ```bash
   # Database URL for all environments
   DATABASE_URL=postgresql://faraday_admin:CodaMoeLuna31@faraday-ai-db.postgres.database.azure.com:5432/postgres?sslmode=require
   ```
   - Must use SSL connection with sslmode=require
   - Azure PostgreSQL compatible
   - Connection pooling enabled

2. **Python Path**:
   - Must include project root: `/app`
   - Set in both Dockerfile and docker-compose.yml

3. **Port Configuration**:
   - App: 8000
   - Redis: 6379
   - MinIO: 9002
   - Prometheus: 9090
   - Grafana: 3000

4. **Volume Mounts**:
   - App code: `./app:/app/app:delegated`
   - Models: `./models:/app/models`
   - Logs: `./logs:/app/logs`
   - Exports: `./exports:/app/exports`

5. **Health Checks**:
   - App: Checks `/health` endpoint
   - Interval: 30s
   - Timeout: 10s
   - Retries: 3

### Backup and Recovery

1. **Project Location**:
   - Primary: SSD storage
   - Path: `/Users/joemartucci/Projects/New Faraday Cursor/Faraday-AI`

2. **Critical Files to Backup**:
   - All Docker configuration files
   - Seed scripts
   - Database models
   - Environment variables

3. **Recovery Steps**:
   - Clone repository to SSD
   - Ensure all environment variables are set
   - Run `./run.sh` to rebuild and start services
   - Verify seeding process completes successfully 

## Getting Started

### Prerequisites
1. Docker and Docker Compose installed
2. Access to the Faraday-AI repository
3. Proper permissions for the database
4. Environment variables set correctly

### Initial Setup Steps
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd Faraday-AI
   ```

2. Verify directory structure:
   ```
   Faraday-AI/
   ├── app/
   │   └── scripts/
   │       └── seed_data/
   ├── migrations/
   │   └── versions/
   └── run.sh
   ```

3. Check current working directory:
   ```bash
   pwd  # Should be: /Users/joemartucci/Projects/New Faraday Cursor/Faraday-AI
   ```

### Database Setup Procedure

1. **Run Migrations First**
   ```bash
   docker-compose run migrations
   ```
   - This creates all necessary tables
   - Check for any errors in the output
   - Verify all migrations complete successfully

2. **Build and Start Services**
   ```bash
   ./run.sh
   ```
   - This will:
     - Build all containers
     - Start the services
     - Run the seed script automatically

3. **Verify Seeding**
   - Check console output for success messages
   - Each table should show "seeded successfully"
   - No foreign key constraint errors should appear

### Common Issues and Solutions

1. **Migration Errors**
   - If migrations fail, check:
     - Database connection string
     - Table existence
     - Foreign key constraints
   - Solution: Drop and recreate the database if needed

2. **Seeding Errors**
   - If seeding fails, check:
     - Migration completion
     - Data types match
     - Foreign key references exist
   - Solution: Run migrations again, then retry seeding

3. **Container Issues**
   - If containers fail to start:
     - Check Docker logs
     - Verify environment variables
     - Ensure ports are available
   - Solution: Stop all containers and rebuild

### Recovery Steps

If something goes wrong:

1. Stop all containers:
   ```bash
   docker-compose down
   ```

2. Clean up orphaned containers:
   ```bash
   docker-compose down --remove-orphans
   ```

3. Rebuild and restart:
   ```bash
   ./run.sh
   ```

### Verification Checklist

After setup, verify:

1. All containers are running:
   ```bash
   docker-compose ps
   ```

2. Database tables exist:
   ```sql
   SELECT table_name 
   FROM information_schema.tables 
   WHERE table_schema = 'public';
   ```

3. Data is seeded:
   ```sql
   SELECT COUNT(*) FROM activities;
   SELECT COUNT(*) FROM students;
   -- etc.
   ```

### Important Reminders

1. **Directory Structure**
   - All files must be in the Faraday-AI directory
   - Never create files in the workspace root
   - Never create nested files without permission

2. **Database Operations**
   - Always run migrations before seeding
   - Never remove services for compatibility issues
   - Always check foreign key constraints

3. **File Management**
   - Never create files without asking first
   - Never move files without asking first
   - Never edit files in wrong locations

4. **Dependencies**
   - Never remove packages without asking
   - Never replace large code sections without asking
   - Always verify compatibility 

## Table Status

### Core Tables
- ✅ `activities` - Stores physical education activities (44 records)
- ✅ `classes` - Stores class information (4 records)
- ✅ `students` - Stores student information (8 records)
- ✅ `users` - Stores user information (3 records)
- ✅ `lessons` - Stores lesson information (3 records)
- ✅ `subject_categories` - Stores subject categories (5 records)

### User & System
- ✅ `users` - Stores user information (3 records)
- ✅ `user_memories` - Stores user memories (6 records)
- ✅ `memory_interactions` - Tracks memory interactions (12 records)
- ✅ `lessons` - Stores lesson information (3 records)
- ✅ `subject_categories` - Stores subject categories (5 records)

### Safety & Risk Management
- ✅ `safety_checks` - Records safety inspections (20 records)

### Activity Categories
- ✅ `Cardio` (10 activities)
  - High-Intensity (3 activities)
  - Jumping (3 activities)
  - Running (4 activities)
- ✅ `Cool-down` (9 activities)
  - Breathing (3 activities)
  - Light Movement (3 activities)
  - Static Stretching (3 activities)
- ✅ `Individual Skills` (6 activities)
  - Agility (3 activities)
  - Balance (3 activities)
  - Coordination (3 activities)
- ✅ `Team Sports` (9 activities)
  - Basketball (3 activities)
  - Soccer (3 activities)
  - Volleyball (3 activities)
- ✅ `Warm-up` (10 activities)
  - Dynamic Stretching (3 activities)
  - Joint Mobility (3 activities)
  - Light Cardio (4 activities)

### Implementation Notes
- ✅ = Table exists, migration created, and seeding implemented
- All core tables, user & system tables, safety tables, and activity categories are now fully functional and seeded with initial data
- Activity categories follow a hierarchical structure with proper parent-child relationships
- Activities are distributed across multiple categories with varying difficulty levels

## Current Activity Distribution (Updated April 2024)

### Activity Categories and Counts
- Total Activities: 44
- Categories: 5 main categories with 15 subcategories

#### Cardio (10 activities)
- High-Intensity: 3 activities
- Jumping: 3 activities
- Running: 4 activities

#### Cool-down (9 activities)
- Breathing: 3 activities
- Light Movement: 3 activities
- Static Stretching: 3 activities

#### Individual Skills (6 activities)
- Agility: 3 activities
- Balance: 3 activities
- Coordination: 3 activities

#### Team Sports (9 activities)
- Basketball: 3 activities
- Soccer: 3 activities
- Volleyball: 3 activities

#### Warm-up (10 activities)
- Dynamic Stretching: 3 activities
- Joint Mobility: 3 activities
- Light Cardio: 4 activities

### Activity Types Distribution
- SKILL_DEVELOPMENT: 18 activities
- WARM_UP: 10 activities
- COOL_DOWN: 9 activities
- FITNESS_TRAINING: 4 activities
- GAME: 3 activities

### Difficulty Level Distribution
- BEGINNER: 24 activities
- INTERMEDIATE: 14 activities
- ADVANCED: 6 activities

## Related Documentation

### Core Documentation
- [Database Documentation](/docs/context/database.md)
  - Database schema
  - Data structures
  - Relationships
  - Implementation details

- [Activity System](/docs/activity_system.md)
  - Activity data models
  - System functionality
  - Data requirements
  - Implementation details

### Implementation Details
- [Dashboard Integration Context](/docs/context/dashboard-ai-integration-context.md)
  - Data integration
  - System architecture
  - Implementation status
  - Success metrics

- [User System Implementation](/docs/handoff/user_system_implementation.md)
  - User data models
  - Security features
  - Data management
  - Implementation details

### Development Resources
- [Educational Features Implementation](/docs/guides/educational-features-implementation.md)
  - Data requirements
  - Implementation details
  - Success metrics
  - Best practices

- [New Features Implementation Guide](/docs/guides/new-features-implementation-guide.md)
  - Data structures
  - Implementation strategy
  - Success criteria
  - Best practices

### Beta Program Documentation
- [Beta Documentation](/docs/beta/beta_documentation.md)
  - Technical details
  - Data structures
  - API references
  - Implementation guides

- [Monitoring Setup](/docs/beta/monitoring_feedback_setup.md)
  - Data collection
  - Performance tracking
  - System monitoring
  - Alert systems

### Additional Resources
- [Activity Visualization Manager](/docs/activity_visualization_manager.md)
  - Data visualization
  - Analysis tools
  - Performance tracking
  - Reporting features

- [Movement Analysis Schema](/docs/context/movement_analysis_schema.md)
  - Data structures
  - Analysis methods
  - Implementation details
  - Performance metrics