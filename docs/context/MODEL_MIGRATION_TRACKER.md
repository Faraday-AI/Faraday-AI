# Model Migration Tracker

## Target Structure
- `/app/models/`
  - `activity.py` (combine all activity-related models) ✅
  - `student.py` (combine student and health metrics) ✅
  - `class_.py` (combine class and enrollment) ✅
  - `routine.py` (combine routine and performance)
  - `assessment.py` (combine all assessment types)
  - `safety.py` (combine safety and equipment checks)
  - `exercise.py` (combine exercise and workout)
  - `types.py` (consolidate all enum types)
  - `base.py` (for shared base classes and utilities)

## File Location Map
### Base Directory
- Working Directory: `/Users/joemartucci/Projects/New Faraday Cursor/Faraday-AI`
- All changes must be made within this directory

### Model Paths
- Primary Models Location: `/app/models/`
- Service Models Location: `/app/services/physical_education/models/`
- API Models Location: `/app/api/v1/models/`

### Service Manager Paths
All service managers are located in `/app/services/physical_education/`:
- `activity_visualization_manager.py` ✅
- `activity_export_manager.py` ✅
- `activity_collaboration_manager.py` ✅
- `activity_adaptation_manager.py` ✅
- `activity_assessment_manager.py` ✅
- `activity_tracking_manager.py` ✅
- `activity_planning_manager.py` ✅
- `activity_security_manager.py` ✅
- `activity_cache_manager.py` ✅
- `activity_rate_limit_manager.py` ✅
- `activity_circuit_breaker_manager.py` ✅

### Configuration Files
- Main Config: `/app/core/config.py`
- Database Config: `/app/core/database.py`
- Service Config: `/app/services/physical_education/config/`
- Model Config: `/app/models/config/`

### Test Files Location
- Base Test Directory: `/tests/`
- Physical Education Tests: `/tests/physical_education/`
- Model Tests: `/tests/models/`
- Service Tests: `/tests/services/`

## Current Model Locations
### Activity Models ✅
- [x] `/models/physical_education/activity.py` -> Consolidated
- [x] `/app/services/physical_education/models/activity.py` -> Consolidated
- [x] `/app/services/physical_education/models/activity_categories.py` -> Consolidated
- [x] `/app/services/physical_education/models/activity_category_association.py` -> Consolidated
- [x] `/app/services/physical_education/models/activity_adaptation_models.py` -> Consolidated
- [x] `/app/services/physical_education/models/activity_plan.py` -> Consolidated
- [x] `/app/models/physical_education/activity/activity.py` -> Consolidated
- [x] `/app/models/physical_education/activity/activity_types.py` -> Consolidated

### Student Models ✅
- [x] `/models/physical_education/student.py` -> Consolidated
- [x] `/app/services/physical_education/models/student.py` -> Consolidated
- [x] `/app/models/physical_education/student/student.py` -> Consolidated
- [x] `/app/models/physical_education/student/student_types.py` -> Consolidated
- [x] `/app/models/physical_education/health/health_metrics.py` -> Consolidated
- [x] `/app/models/physical_education/health/fitness_goals.py` -> Consolidated

### Class Models ✅
- [x] `/app/models/physical_education/class_/class_.py` -> Consolidated
- [x] `/app/models/physical_education/class_/class_types.py` -> Consolidated

### Routine Models ✅
- [x] `/models/physical_education/routine.py` -> Consolidated and backed up
- [x] `/app/services/physical_education/models/routine.py` -> Consolidated and backed up
- [x] `/app/services/physical_education/models/routine_performance_models.py` -> Consolidated and backed up
- [x] Backup created in `/models_backup/physical_education/routine/`
- [x] Import paths updated in all dependent services
- [x] Model relationships verified and preserved
- [x] Service functionality tested and confirmed

### Assessment Models ✅
- [x] `/models/physical_education/assessment.py` -> Consolidated
- [x] `/app/services/physical_education/models/skill_assessment/skill_assessment.py` -> Consolidated
- [x] `/app/models/physical_education/assessment/assessment_types.py` -> Consolidated

### Safety Models ✅
- [x] `/models/physical_education/safety.py` -> Consolidated
- [x] `/app/models/physical_education/safety/safety.py` -> Consolidated
- [x] `/app/services/physical_education/models/safety.py` -> Consolidated

### Exercise Models ✅
- [x] `/models/physical_education/exercise.py` -> Consolidated
- [x] `/app/services/physical_education/models/exercise.py` -> Consolidated
- [x] `/app/services/physical_education/models/workout.py` -> Consolidated

### Dashboard Models 🔄 (IN PROGRESS)
- [ ] `/app/dashboard/models/gpt_models.py` -> Needs consolidation
- [ ] `/app/dashboard/models/tool_registry.py` -> Needs consolidation
- [ ] `/app/dashboard/models/user.py` -> Needs consolidation
- [ ] `/app/dashboard/models/context.py` -> Needs consolidation
- [ ] `/app/dashboard/models/security.py` -> Needs consolidation
- [ ] `/app/dashboard/models/resource_models.py` -> Needs consolidation
- [ ] `/app/dashboard/models/notification_models.py` -> Needs consolidation
- [ ] `/app/dashboard/models/dashboard_models.py` -> Needs consolidation
- [ ] `/app/models/feedback/tools/user_tool.py` -> Needs consolidation
- [ ] `/app/models/dashboard/models/tool_registry.py` -> Needs consolidation

### Current Dashboard Model Issues
- [ ] Duplicate Tool class definitions causing table creation conflicts
- [ ] GPT models not properly registered in main metadata registry
- [ ] Foreign key relationship errors between dashboard_users and gpt_subscriptions
- [ ] Import path conflicts between dashboard and feedback tool models
- [ ] Base class inconsistencies (SharedBase vs CoreBase)

### Service Integration ✅
- [x] Activity Visualization Manager
- [x] Activity Export Manager
- [x] Activity Collaboration Manager
- [x] Activity Adaptation Manager
- [x] Activity Assessment Manager
- [x] Activity Tracking Manager
- [x] Activity Planning Manager
- [x] Activity Security Manager
- [x] Activity Cache Manager
- [x] Activity Rate Limit Manager
- [x] Activity Circuit Breaker Manager

## Migration Progress
1. [x] Create new model files in `/app/models/` (activity.py and student.py completed)
2. [ ] Move and consolidate models one category at a time (activity and student models completed)
3. [ ] Update import paths
4. [ ] Test each consolidation
5. [ ] Remove old files
6. [ ] Clean up `__pycache__` directories
7. [x] Implement service managers
8. [x] Set up error handling and logging
9. [x] Implement metrics tracking
10. [x] Set up caching mechanisms
11. [x] Implement rate limiting
12. [x] Add security measures

## Current Status
- Working on: Dashboard Model Consolidation
- Next up: Resolve GPT and Tool Registry conflicts
- Completed: All Physical Education model consolidations (Activity, Student, Class, Routine, Assessment, Safety, Exercise)
- Current Issue: Dashboard models have duplicate definitions and import conflicts
- Priority: Consolidate dashboard models following established patterns

## Dependencies to Update
### Core Dependencies
- SQLAlchemy ORM
- Pydantic schemas
- FastAPI routes
- Redis cache
- PostgreSQL database

### Service Dependencies
- Plotly for visualizations
- NumPy for calculations
- Pandas for data manipulation
- Logging system
- Metrics collection

### Testing Dependencies
- pytest
- pytest-asyncio
- pytest-cov
- pytest-mock
- pytest-env

## Critical Paths to Maintain
1. Database Migrations: `/migrations/`
2. API Routes: `/app/api/v1/`
3. Service Configs: `/app/services/physical_education/config/`
4. Test Fixtures: `/tests/fixtures/`
5. Seed Data: `/app/scripts/seed_data/`

## Notes
- Keep track of all relationships
- Maintain table names and constraints
- Preserve all enums and types
- Update all import paths
- Test after each consolidation
- Implemented comprehensive service layer
- Added performance monitoring
- Set up security measures
- Integrated caching system
- Successfully consolidated routine models
- Created backup of old model files
- Updated all routine-related service files
- Maintained all model relationships
- Preserved database schema compatibility
- All models have been successfully consolidated
- Model relationships preserved across all consolidations
- Import paths updated systematically
- Backup copies created for all old model files

## Recommendations for Further Restructuring
1. Consider implementing a model versioning system
2. Add model migration scripts for future changes
3. Implement automated testing for model relationships
4. Create model documentation generator
5. Add model validation layer
6. Implement model caching strategy
7. Add model performance monitoring
8. Create model dependency graph
9. Implement model change tracking
10. Add model audit logging

## Verification Checklist
1. [ ] All models consolidated in correct locations
2. [ ] All import paths updated
3. [ ] All service managers implemented
4. [ ] All tests passing
5. [ ] All migrations working
6. [ ] All API endpoints functional
7. [ ] All relationships preserved
8. [ ] All enums and types consolidated
9. [ ] All configurations updated
10. [ ] All documentation current
- [x] Routine models consolidated
- [x] Routine import paths updated
- [x] Routine service managers implemented
- [x] Routine tests passing
- [x] Routine migrations working
- [x] Routine API endpoints functional
- [x] Routine relationships preserved
- [x] Routine backup created

### Dashboard Model Verification Checklist
1. [ ] Dashboard models use consistent base classes (SharedBase)
2. [ ] No duplicate Tool class definitions
3. [ ] GPT models properly registered in metadata registry
4. [ ] Foreign key relationships work between dashboard_users and gpt_subscriptions
5. [ ] All dashboard import paths updated
6. [ ] Database seeding works without table creation errors
7. [ ] All dashboard API endpoints functional
8. [ ] All dashboard tests passing
9. [ ] Dashboard documentation updated
10. [ ] No circular import dependencies

## Next Actions
1. Complete comprehensive testing of all consolidated models
2. Implement performance monitoring
3. Set up alerting system
4. Optimize caching mechanisms
5. Update documentation
6. Clean up old model files after thorough testing

## Dashboard Model Consolidation Plan

### Phase 1: Tool Registry Consolidation
1. [ ] Consolidate duplicate Tool class definitions
   - `/app/dashboard/models/tool_registry.py` (SharedBase)
   - `/app/models/dashboard/models/tool_registry.py` (CoreBase -> SharedBase)
   - `/app/models/feedback/tools/tool.py` (REMOVED - duplicate)
2. [ ] Unify base classes to SharedBase
3. [ ] Update all import paths
4. [ ] Test table creation

### Phase 2: GPT Models Consolidation
1. [ ] Ensure GPT models are properly registered in main metadata registry
2. [ ] Fix foreign key relationships between dashboard_users and gpt_subscriptions
3. [ ] Resolve import conflicts
4. [ ] Test all GPT model relationships

### Phase 3: User Model Consolidation
1. [ ] Consolidate DashboardUser with core User model relationships
2. [ ] Resolve cross-system foreign key references
3. [ ] Update all user-related imports
4. [ ] Test user model functionality

### Phase 4: Context and Security Models
1. [ ] Consolidate context models
2. [ ] Consolidate security models
3. [ ] Update all related imports
4. [ ] Test functionality

### Phase 5: Resource and Notification Models
1. [ ] Consolidate resource models
2. [ ] Consolidate notification models
3. [ ] Update all related imports
4. [ ] Test functionality

### Verification Steps for Dashboard Models
1. [ ] All dashboard models use consistent base classes
2. [ ] No duplicate table definitions
3. [ ] All foreign key relationships work correctly
4. [ ] All import paths updated
5. [ ] Database seeding works without errors
6. [ ] All API endpoints functional
7. [ ] All tests passing
8. [ ] Documentation updated 